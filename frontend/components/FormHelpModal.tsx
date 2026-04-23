/**
 * FormHelpModal
 * ─────────────────────────────────────────────────────────────────────────────
 * A fully self-contained slide-over modal that appears when the user clicks
 * the "?" button next to a form/PDF download in ServiceDetail.
 *
 * Features:
 *  - AI-generated WHY / HOW content (via /api/v1/form-help → sarvam-30b)
 *  - 🔊 Read Aloud (TTS via existing /api/v1/text-to-speech)
 *  - 🎤 Voice Question (STT via existing /api/v1/speech-to-text + follow-up)
 *  - Language selector (synced with app's i18n)
 *  - Markdown-ish bold rendering
 *  - Retry on error
 *
 * ISOLATION GUARANTEE:
 *  This component has zero coupling to AdvancedChatbot.tsx or any main-chat
 *  state. It uses its own local useState and the separate /form-help endpoint.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  RefreshCw,
  HelpCircle,
  ChevronDown,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { Button } from './ui/button';
import {
  getFormHelp,
  textToSpeech,
  playAudioBlob,
  speechToText,
} from '../src/lib/api';
import { useTranslation } from 'react-i18next';

// ── Supported languages ───────────────────────────────────────────────────────
const LANG_OPTIONS = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी' },
  { code: 'ta', label: 'தமிழ்' },
  { code: 'te', label: 'తెలుగు' },
  { code: 'bn', label: 'বাংলা' },
  { code: 'mr', label: 'मराठी' },
  { code: 'gu', label: 'ગુજરાતી' },
  { code: 'kn', label: 'ಕನ್ನಡ' },
  { code: 'ml', label: 'മലയാളം' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ' },
];

// ── Props ─────────────────────────────────────────────────────────────────────
interface FormHelpModalProps {
  isOpen: boolean;
  onClose: () => void;
  serviceId: string;
  serviceName: string;
  documentName: string;
  /** Initial language code, synced from i18n (default: 'en') */
  initialLanguage?: string;
}

// ── Simple markdown bold/bullet renderer ─────────────────────────────────────
function RenderHelpText({ text }: { text: string }) {
  if (!text) return null;
  const lines = text.split('\n');
  return (
    <div className="space-y-1 text-[var(--foreground)] text-sm leading-relaxed">
      {lines.map((line, i) => {
        // Bold headers **text**
        const boldParts = line.split(/\*\*(.+?)\*\*/g);
        const rendered = boldParts.map((part, j) =>
          j % 2 === 1 ? (
            <strong key={j} className="font-semibold text-[var(--color-navy)]">
              {part}
            </strong>
          ) : (
            <span key={j}>{part}</span>
          ),
        );
        // Bullet lines
        const isBullet = line.trimStart().startsWith('- ') || line.trimStart().startsWith('• ');
        const isNumbered = /^\d+\./.test(line.trimStart());
        if (!line.trim()) return <div key={i} className="h-2" />;
        return (
          <div key={i} className={`flex gap-2 ${isBullet || isNumbered ? 'ml-2' : ''}`}>
            {isBullet && <span className="text-[var(--accent)] mt-0.5 flex-shrink-0">•</span>}
            <span>{rendered}</span>
          </div>
        );
      })}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export function FormHelpModal({
  isOpen,
  onClose,
  serviceId,
  serviceName,
  documentName,
  initialLanguage = 'en',
}: FormHelpModalProps) {
  const { i18n } = useTranslation();
  const [language, setLanguage] = useState<string>(initialLanguage);
  const [showLangPicker, setShowLangPicker] = useState(false);
  const [helpText, setHelpText] = useState<string>('');
  const [sources, setSources] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // TTS state
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isTtsLoading, setIsTtsLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // STT / voice-question state
  const [isRecording, setIsRecording] = useState(false);
  const [voiceAnswer, setVoiceAnswer] = useState<string>('');
  const [isVoiceLoading, setIsVoiceLoading] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // ── Fetch help text ─────────────────────────────────────────────────────────
  const fetchHelp = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setHelpText('');
    setSources([]);
    setVoiceAnswer('');
    try {
      const result = await getFormHelp({
        service_id: serviceId,
        service_name: serviceName,
        document_name: documentName,
        language,
      });
      setHelpText(result.help_text);
      setSources(result.sources ?? []);
    } catch (err) {
      setError('Could not load help content. Please check your connection and retry.');
    } finally {
      setIsLoading(false);
    }
  }, [serviceId, serviceName, documentName, language]);

  // Fetch when modal opens or language changes
  useEffect(() => {
    if (isOpen) {
      fetchHelp();
    }
  }, [isOpen, fetchHelp]);

  // Sync language with app i18n on open
  useEffect(() => {
    if (isOpen) {
      const appLang = i18n.language?.split('-')[0] || 'en';
      const supported = LANG_OPTIONS.find((l) => l.code === appLang);
      if (supported) setLanguage(supported.code);
    }
  }, [isOpen, i18n.language]);

  // Escape key to close
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    if (isOpen) document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  // ── TTS: Read Aloud ────────────────────────────────────────────────────────
  const handleReadAloud = async () => {
    if (isSpeaking) {
      audioRef.current?.pause();
      setIsSpeaking(false);
      return;
    }
    if (!helpText) return;
    setIsTtsLoading(true);
    try {
      const audioData = await textToSpeech(helpText.slice(0, 1200), language);
      if (audioData instanceof ArrayBuffer) {
        const audio = playAudioBlob(audioData);
        audioRef.current = audio;
        audio.onended = () => setIsSpeaking(false);
        audio.onerror = () => setIsSpeaking(false);
        await audio.play();
        setIsSpeaking(true);
      }
    } catch {
      // TTS failed — silently ignore, button just does nothing
    } finally {
      setIsTtsLoading(false);
    }
  };

  // ── STT: Voice Question ────────────────────────────────────────────────────
  const handleVoiceQuestion = async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        setIsVoiceLoading(true);
        try {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          const sttResult = await speechToText(blob, language);
          const transcript = sttResult.transcript?.trim();
          if (!transcript) { setIsVoiceLoading(false); return; }
          // Ask a follow-up via form-help with the voiced question as the document name
          const followUp = await getFormHelp({
            service_id: serviceId,
            service_name: serviceName,
            document_name: `${documentName} — User question: ${transcript}`,
            language,
          });
          setVoiceAnswer(followUp.help_text);
        } catch {
          setVoiceAnswer('Sorry, could not process your voice question. Please type your question or try again.');
        } finally {
          setIsVoiceLoading(false);
        }
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    } catch {
      setVoiceAnswer('Microphone access denied. Please allow microphone permission and retry.');
    }
  };

  const selectedLang = LANG_OPTIONS.find((l) => l.code === language) || LANG_OPTIONS[0];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-[9000] bg-black/40 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Slide-over panel */}
          <motion.div
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0 }}
            transition={{ type: 'spring', stiffness: 340, damping: 36, mass: 0.85 }}
            className="fixed right-0 top-0 bottom-0 z-[9001] w-full max-w-md flex flex-col
                       bg-[var(--card)] border-l-2 border-[var(--card-border)]
                       shadow-[var(--shadow-24)] overflow-hidden"
            role="dialog"
            aria-modal="true"
            aria-label={`Help for ${documentName}`}
          >
            {/* ── Header ───────────────────────────────────────────────────── */}
            <div className="flex items-start justify-between gap-3 p-5 border-b border-[var(--border)]
                            bg-gradient-to-r from-[var(--primary)] to-[#1a3a9f]">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-9 h-9 bg-white/15 rounded-[var(--radius-lg)] flex items-center justify-center flex-shrink-0">
                  <HelpCircle className="w-5 h-5 text-white" />
                </div>
                <div className="min-w-0">
                  <div className="text-xs text-white/70 font-medium uppercase tracking-wide">Form Guidance</div>
                  <div className="text-white font-semibold text-sm leading-tight truncate">{documentName}</div>
                  <div className="text-white/60 text-xs truncate">{serviceName}</div>
                </div>
              </div>
              <button
                onClick={onClose}
                className="mt-0.5 w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors flex-shrink-0"
                aria-label="Close help"
              >
                <X className="w-4 h-4 text-white" />
              </button>
            </div>

            {/* ── Toolbar ──────────────────────────────────────────────────── */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border)] bg-[var(--surface-1)]">
              {/* Language picker */}
              <div className="relative">
                <button
                  onClick={() => setShowLangPicker((p) => !p)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-full)]
                             bg-[var(--surface-2)] border border-[var(--border)] text-sm
                             text-[var(--foreground)] hover:bg-[var(--muted)] transition-colors"
                >
                  <span>{selectedLang.label}</span>
                  <ChevronDown className="w-3 h-3 text-[var(--muted-foreground)]" />
                </button>
                <AnimatePresence>
                  {showLangPicker && (
                    <motion.div
                      initial={{ opacity: 0, y: -6 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -6 }}
                      transition={{ duration: 0.12 }}
                      className="absolute top-full left-0 mt-1 z-10 w-40 bg-[var(--card)]
                                 border border-[var(--border)] rounded-[var(--radius-lg)]
                                 shadow-[var(--shadow-8)] py-1 max-h-56 overflow-y-auto"
                    >
                      {LANG_OPTIONS.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => { setLanguage(lang.code); setShowLangPicker(false); }}
                          className={`w-full text-left px-3 py-2 text-sm hover:bg-[var(--surface-2)] transition-colors ${
                            language === lang.code ? 'font-semibold text-[var(--primary)]' : 'text-[var(--foreground)]'
                          }`}
                        >
                          {lang.label}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <div className="flex-1" />

              {/* Read Aloud */}
              <Button
                size="sm"
                variant="outline"
                onClick={handleReadAloud}
                disabled={!helpText || isLoading || isTtsLoading}
                className="gap-1.5 text-xs border-[var(--border)]"
                title={isSpeaking ? 'Stop reading' : 'Read aloud'}
              >
                {isTtsLoading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : isSpeaking ? (
                  <VolumeX className="w-3.5 h-3.5" />
                ) : (
                  <Volume2 className="w-3.5 h-3.5" />
                )}
                {isSpeaking ? 'Stop' : 'Read'}
              </Button>

              {/* Voice Question */}
              <Button
                size="sm"
                variant={isRecording ? 'destructive' : 'outline'}
                onClick={handleVoiceQuestion}
                disabled={isLoading || isVoiceLoading}
                className="gap-1.5 text-xs"
                title={isRecording ? 'Stop recording' : 'Ask a question by voice'}
              >
                {isVoiceLoading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : isRecording ? (
                  <MicOff className="w-3.5 h-3.5" />
                ) : (
                  <Mic className="w-3.5 h-3.5" />
                )}
                {isRecording ? 'Stop' : 'Ask'}
              </Button>

              {/* Retry */}
              <Button
                size="sm"
                variant="ghost"
                onClick={fetchHelp}
                disabled={isLoading}
                className="text-xs gap-1.5"
                title="Reload help"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            </div>

            {/* ── Content ──────────────────────────────────────────────────── */}
            <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5">

              {/* Loading skeleton */}
              {isLoading && (
                <div className="space-y-3 animate-pulse">
                  {[80, 60, 90, 50, 70, 40].map((w, i) => (
                    <div
                      key={i}
                      className="h-3 bg-[var(--muted)] rounded-full"
                      style={{ width: `${w}%` }}
                    />
                  ))}
                </div>
              )}

              {/* Error state */}
              {error && !isLoading && (
                <div className="flex flex-col items-center gap-3 py-8 text-center">
                  <AlertCircle className="w-10 h-10 text-[var(--destructive)]" />
                  <p className="text-sm text-[var(--muted-foreground)]">{error}</p>
                  <Button size="sm" onClick={fetchHelp}>
                    <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
                    Retry
                  </Button>
                </div>
              )}

              {/* Main help text */}
              {helpText && !isLoading && !error && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  <RenderHelpText text={helpText} />

                  {/* RAG Sources — shows where the factual info came from */}
                  {sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-[var(--border)]">
                      <div className="text-xs font-medium text-[var(--muted-foreground)] mb-2 uppercase tracking-wide">
                        Sources
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {sources.map((src, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px]
                                       bg-[var(--primary)]/10 text-[var(--primary)] border border-[var(--primary)]/20"
                          >
                            {src}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}

              {/* Recording indicator */}
              {isRecording && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center gap-2 p-3 rounded-[var(--radius-lg)]
                             bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800"
                >
                  <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-sm text-red-700 dark:text-red-400">Recording… tap Stop when done.</span>
                </motion.div>
              )}

              {/* Voice answer */}
              {voiceAnswer && !isVoiceLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-[var(--radius-xl)] border-2 border-[var(--accent)]/30
                             bg-[var(--accent)]/5"
                >
                  <div className="flex items-center gap-1.5 mb-2 text-[var(--accent)] text-xs font-semibold uppercase tracking-wide">
                    <Mic className="w-3 h-3" />
                    Voice answer
                  </div>
                  <RenderHelpText text={voiceAnswer} />
                </motion.div>
              )}

              {isVoiceLoading && (
                <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing your question…
                </div>
              )}
            </div>

            {/* ── Footer ───────────────────────────────────────────────────── */}
            <div className="px-5 py-4 border-t border-[var(--border)] bg-[var(--surface-1)]">
              <p className="text-xs text-[var(--muted-foreground)] text-center">
                Powered by Sarvam AI · Content is guidance only · Always verify on the official portal
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
