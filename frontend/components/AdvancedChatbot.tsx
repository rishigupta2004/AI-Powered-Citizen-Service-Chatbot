import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  MessageCircle,
  X,
  Send,
  Loader2,
  Paperclip,
  Mic,
  MicOff,
  Sparkles,
  FileText,
  Calendar,
  CreditCard,
  Bot,
  User as UserIcon,
  Home,
  AlertCircle,
  Phone,
  Mail,
  ChevronRight,
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Volume2,
  VolumeX,
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { cn } from "./ui/utils";
import { toast } from "sonner";
import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";
import {
  sendChatMessage,
  speechToText,
  textToSpeech,
  playAudioBlob,
  ChatMessage as APIChatMessage,
  ChatAction as APIChatAction,
  ApiError,
  warmUpBackend,
} from "../src/lib/api";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  type?: "text" | "service-card" | "quick-actions" | "form";
  data?: any;
  isTyping?: boolean;
  language?: string;
}

interface GuidedAction extends APIChatAction {}

interface QuickAction {
  id: string;
  icon: any;
  label: string;
  description: string;
  action: string;
}

interface AdvancedChatbotProps {
  onNavigate?: (page: string, serviceId?: string) => void;
  currentPage?: string;
  currentService?: string;
}

// Language options
const LANGUAGES = [
  { code: "auto", label: "Auto Detect" },
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी" },
  { code: "ta", label: "தமிழ்" },
  { code: "te", label: "తెలుగు" },
  { code: "bn", label: "বাংলা" },
  { code: "mr", label: "मराठी" },
  { code: "gu", label: "ગુજરાતી" },
  { code: "kn", label: "ಕನ್ನಡ" },
  { code: "ml", label: "മലയാളം" },
  { code: "pa", label: "ਪੰਜਾਬੀ" },
];

export function AdvancedChatbot({
  onNavigate,
  currentPage = "home",
  currentService,
}: AdvancedChatbotProps) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isSlowResponse, setIsSlowResponse] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputElement, setInputElement] = useState<HTMLInputElement | null>(null);

  // New state for Sarvam integration
  const [language, setLanguage] = useState("auto");
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState<"idle" | "recording" | "transcribing" | "speaking">("idle");
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [voiceChatEnabled, setVoiceChatEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);

  // Build message history for API
  const getHistory = useCallback((): APIChatMessage[] => {
    return messages
      .slice(-12)
      .map((m) => ({
        role: m.sender === "user" ? "user" : "assistant",
        content: m.text,
      }));
  }, [messages]);

  // Welcome message with quick actions - context aware
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Wake up HF Space backend early so it's ready when user types
      warmUpBackend();
      setTimeout(() => {
        let welcomeMessage = `${t("chatbot.welcome", "Namaste! Welcome to Seva Sindhu AI Assistant 🇮🇳")}\n\n`;

        if (currentPage === "dashboard") {
          welcomeMessage += t(
            "chatbot.context.dashboard",
            "I can see you're on your dashboard. I can help you track applications, check status, or start a new service.",
          );
        } else if (currentPage === "services") {
          welcomeMessage += t(
            "chatbot.context.services",
            "Looking for a specific service? I can help you find and apply for the right government service.",
          );
        } else if (currentPage === "service-detail" && currentService) {
          welcomeMessage += t(
            "chatbot.context.serviceDetail",
            "I can help you with {{service}}. Would you like to know about requirements, process, or start the application?",
            { service: currentService },
          );
        } else if (currentPage === "tracker") {
          welcomeMessage += t(
            "chatbot.context.tracker",
            "I can help you track your applications. Just provide your Application Reference Number (ARN).",
          );
        } else {
          welcomeMessage += t(
            "chatbot.context.default",
            "I'm here to help you with government services. How can I assist you today?",
          );
        }

        addBotMessage(welcomeMessage, "text");

        setTimeout(() => {
          addBotMessage("", "quick-actions", {
            actions: quickActions,
          });
        }, 800);
      }, 300);
    }
  }, [isOpen, currentPage, currentService, messages.length]);

  // Auto-scroll to latest message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isTyping]);

  // Show waiting indicator only if response exceeds 2 seconds
  useEffect(() => {
    if (!isTyping) {
      setIsSlowResponse(false);
      return;
    }

    const timer = window.setTimeout(() => {
      setIsSlowResponse(true);
    }, 2000);

    return () => {
      clearTimeout(timer);
      setIsSlowResponse(false);
    };
  }, [isTyping]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputElement) {
      inputElement.focus();
    }
  }, [isOpen, inputElement]);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
      }
    };
  }, []);

  const addBotMessage = (
    text: string,
    type: Message["type"] = "text",
    data?: any,
    language?: string
  ) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: "bot",
      timestamp: new Date(),
      type,
      data,
      language,
    };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage.id;
  };

  const addUserMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: "user",
      timestamp: new Date(),
      type: "text",
    };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage.id;
  };

  const requestAssistantReply = async (userText: string, preferredLanguage?: string, _isRetry = false) => {
    setIsTyping(true);
    try {
      const response = await sendChatMessage(
        userText,
        getHistory(),
        preferredLanguage || language,
        currentService,
        "auto"
      );

      addBotMessage(response.response, "text", undefined, response.language);

      if (response.actions && response.actions.length) {
        addBotMessage("", "form", { actions: response.actions });
      }

      if (ttsEnabled && response.response) {
        const responseLang = response.language || language || "en";
        await speakText(response.speak_text || response.response, responseLang);
      }
    } catch (error: any) {
      console.error("Chat error:", error);
      if (error?.message?.includes("timed out")) {
        if (!_isRetry) {
          // First timeout: likely HF Space cold start. Retry once automatically.
          toast.info(
            t("chatbot.errors.backendWaking", "Backend is waking up… retrying automatically.")
          );
          await requestAssistantReply(userText, preferredLanguage, true);
          return;
        }
        toast.error(
          t("chatbot.errors.slowTimeout", "The server is still starting up. Please wait a moment and try again.")
        );
      } else {
        const errorMsg = error?.message || t("chatbot.errors.responseFailed", "Failed to get response. Please try again.");
        toast.error(String(errorMsg));
      }
    } finally {
      setIsTyping(false);
    }
  };

  // TEXT CHAT - Updated to use real API
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userText = inputValue.trim();
    addUserMessage(userText);
    setInputValue("");
    await requestAssistantReply(userText);
  };

  // SPEECH TO TEXT
  const normalizeLang = (value?: string): string => {
    const v = (value || "").toLowerCase();
    if (!v) return "en";
    if (v.includes("-")) return v.split("-")[0];
    return v;
  };

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
        stream.getTracks().forEach((t) => t.stop()); // Release mic

        setIsTyping(true);
        setVoiceStatus("transcribing");
        try {
          if (voiceChatEnabled) {
            const sttResult = await speechToText(audioBlob, language);
            const transcript = sttResult.transcript?.trim() || "";
            const detectedLang = normalizeLang(sttResult.language_code || language);
            if (!transcript) {
              toast.error(t("chatbot.errors.transcriptionFailed", "Could not transcribe audio. Please try again."));
              setVoiceStatus("idle");
              return;
            }

            addUserMessage(transcript);
            if (language === "auto" && detectedLang) {
              setLanguage(detectedLang);
            }

            const chatResult = await sendChatMessage(
              transcript,
              getHistory(),
              detectedLang,
              currentService,
              "auto"
            );
            const assistantText = chatResult.response || "";
            addBotMessage(assistantText, "text", undefined, chatResult.language || detectedLang);
            if (chatResult.actions && chatResult.actions.length) {
              addBotMessage("", "form", { actions: chatResult.actions });
            }

            if (assistantText) {
              setVoiceStatus("speaking");
              const audioBlobResponse = await textToSpeech(chatResult.speak_text || assistantText, chatResult.language || detectedLang || "en");
              const audio = playAudioBlob(audioBlobResponse);
              currentAudioRef.current = audio;
                try {
                  await audio.play();
                } catch {
                  toast.error(
                    t("chatbot.errors.audioBlockedRetry", "Audio playback blocked by browser. Tap speaker again.")
                  );
                }
                audio.onended = () => {
                  setVoiceStatus("idle");
                };
              }
            } else {
              const result = await speechToText(audioBlob, language);
              const transcript = result.transcript?.trim() || "";
              if (transcript) {
                addUserMessage(transcript);
                toast.success(
                  t("chatbot.voice.detectedLanguage", "Detected: {{language}}", {
                    language: result.language_code || language,
                  })
                );
                const detectedLang = normalizeLang(result.language_code || language);
                if (language === "auto" && detectedLang) {
                  setLanguage(detectedLang);
                }
                await requestAssistantReply(transcript, detectedLang);
              } else {
                toast.error(t("chatbot.errors.transcriptionFailed", "Could not transcribe audio. Please try again."));
              }
              setVoiceStatus("idle");
            }
          } catch (err: any) {
            console.error("Speech error:", err);
            const errorMsg = err?.message || t("chatbot.errors.speechWorkflowFailed", "Speech workflow failed");
            toast.error(String(errorMsg));
            setVoiceStatus("idle");
          } finally {
            setIsTyping(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setVoiceStatus("recording");
        toast.info(t("chatbot.voice.recording", "Recording... tap mic again to stop"));
    } catch (err) {
      toast.error(t("chatbot.voice.micDenied", "Microphone access denied. Please allow mic permissions."));
      setVoiceStatus("idle");
    }
  }, [language, voiceChatEnabled, t, currentService, getHistory]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setVoiceStatus("transcribing");
    }
  }, [isRecording]);

  const toggleRecording = () => {
    if (isRecording) stopRecording();
    else startRecording();
  };

  // TEXT TO SPEECH
  const speakText = useCallback(
    async (text: string, lang: string = "hi") => {
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
        setIsSpeaking(false);
      }

      setIsSpeaking(true);
      setVoiceStatus("speaking");
      try {
        const audioBlob = await textToSpeech(text, lang);
        const audio = playAudioBlob(audioBlob);
        currentAudioRef.current = audio;
        try {
          await audio.play();
        } catch {
          toast.error(
            t("chatbot.errors.audioBlockedTapAgain", "Audio playback blocked by browser. Please tap again.")
          );
          setIsSpeaking(false);
          return;
        }
        audio.onended = () => {
          setIsSpeaking(false);
          setVoiceStatus("idle");
          currentAudioRef.current = null;
        };
      } catch (err: any) {
        console.error("TTS error:", err);
        const errorMsg = err?.message || t("chatbot.errors.ttsFailed", "Text-to-speech failed");
        toast.error(String(errorMsg));
        setIsSpeaking(false);
        setVoiceStatus("idle");
      }
    },
    [t]
  );

  const stopSpeaking = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
      setIsSpeaking(false);
    }
  };

  const quickActions: QuickAction[] = [
    {
      id: "1",
      icon: FileText,
      label: t("chatbot.quick.checkStatus", "Check Application Status"),
      description: t("chatbot.quick.checkStatusDesc", "Track your application progress"),
      action: "check_status",
    },
    {
      id: "2",
      icon: Calendar,
      label: t("chatbot.quick.bookAppointment", "Book Appointment"),
      description: t("chatbot.quick.bookAppointmentDesc", "Schedule a visit to service center"),
      action: "book_appointment",
    },
    {
      id: "3",
      icon: CreditCard,
      label: t("chatbot.quick.payFees", "Pay Fees"),
      description: t("chatbot.quick.payFeesDesc", "Make online payments"),
      action: "pay_fees",
    },
    {
      id: "4",
      icon: Home,
      label: t("chatbot.quick.exploreServices", "Explore Services"),
      description: t("chatbot.quick.exploreServicesDesc", "Browse available government services"),
      action: "explore_services",
    },
  ];

  const handleQuickAction = async (action: QuickAction) => {
    addUserMessage(action.label);

    if (action.action === "explore_services" && onNavigate) {
      onNavigate("services");
    }

    if (action.action === "check_status" && onNavigate) {
      onNavigate("tracker");
    }

    if (action.action === "book_appointment" && onNavigate) {
      onNavigate("dashboard");
    }

    if (action.action === "pay_fees" && onNavigate) {
      onNavigate("dashboard");
    }

    const mappedPrompt: Record<string, string> = {
      check_status: "How can I check my application status using ARN? Share exact steps and official portal path.",
      book_appointment: "How do I book an appointment for government service applications?",
      pay_fees: "How can I pay government service fees online safely?",
      explore_services: "List major Indian government citizen services and how to choose the right one.",
    };

    const backendPrompt = mappedPrompt[action.action] || action.label;
    await requestAssistantReply(backendPrompt);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const handleGuidedAction = (action: GuidedAction) => {
    if (action.type === "url" && action.url) {
      window.open(action.url, "_blank", "noopener,noreferrer");
      return;
    }
    if (action.type === "navigate" && action.page && onNavigate) {
      onNavigate(action.page, action.service_id);
    }
  };

  useEffect(() => {
    const onOpenChat = (evt: Event) => {
      const custom = evt as CustomEvent<{ message?: string }>;
      setIsOpen(true);
      if (custom.detail?.message) {
        setInputValue(custom.detail.message);
      }
    };
    window.addEventListener("seva:open-chat", onOpenChat as EventListener);
    return () => {
      window.removeEventListener("seva:open-chat", onOpenChat as EventListener);
    };
  }, []);

  return (
    <>
      {/* Chat Bubble */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <Button
              onClick={() => setIsOpen(true)}
              size="icon"
              className="w-14 h-14 rounded-full bg-gradient-to-br from-[#000080] to-[#000066] hover:from-[#000066] hover:to-[#000050] shadow-lg shadow-blue-900/20"
              aria-label={t("chatbot.openChat", "Open chat")}
            >
              <MessageCircle className="w-6 h-6 text-white" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed bottom-4 right-4 z-50 w-[calc(100vw-2rem)] max-w-xl md:bottom-6 md:right-6"
          >
            <div className="flex h-[min(82vh,760px)] flex-col overflow-hidden rounded-[var(--radius-2xl)] border-2 border-[var(--card-border)] bg-[var(--card)] shadow-[var(--shadow-24)]">
              {/* Header */}
              <div className="bg-gradient-to-r from-[#000080] to-[#000066] px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div className="text-white font-semibold text-sm">
                      {t("chatbot.title", "Seva Sindhu AI")}
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-green-400" />
                      <span className="text-white/70 text-xs">{t("chatbot.online", "Online")}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {/* Language Selector */}
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="text-xs bg-white/20 text-white border-0 rounded px-2 py-1 cursor-pointer"
                    aria-label={t("chatbot.selectLanguage", "Select language")}
                  >
                    {LANGUAGES.map((l) => (
                      <option key={l.code} value={l.code} className="text-black">
                        {l.label}
                      </option>
                    ))}
                  </select>

                  {/* TTS Toggle */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-white hover:bg-white/20 w-8 h-8"
                    onClick={() => setTtsEnabled((v) => !v)}
                    title={
                      ttsEnabled
                        ? t("chatbot.disableAutoSpeak", "Disable auto-speak")
                        : t("chatbot.enableAutoSpeak", "Enable auto-speak")
                    }
                  >
                    {ttsEnabled ? (
                      <Volume2 className="w-4 h-4" />
                    ) : (
                      <VolumeX className="w-4 h-4 opacity-50" />
                    )}
                  </Button>

                  {/* Voice Conversation Toggle */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-white hover:bg-white/20 w-8 h-8"
                    onClick={() => setVoiceChatEnabled((v) => !v)}
                    title={
                      voiceChatEnabled
                        ? t("chatbot.voiceModeOn", "Voice conversation ON")
                        : t("chatbot.voiceModeOff", "Voice conversation OFF")
                    }
                  >
                    <Phone className={cn("w-4 h-4", voiceChatEnabled ? "text-green-300" : "opacity-70")} />
                  </Button>

                  {/* Close */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-white hover:bg-white/20 w-8 h-8"
                    onClick={() => setIsOpen(false)}
                    aria-label={t("chatbot.closeChat", "Close chat")}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Messages */}
              <ScrollArea className="min-h-0 flex-1 bg-[var(--background)]">
                <div className="p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        "flex gap-2",
                        message.sender === "user"
                          ? "justify-end"
                          : "justify-start"
                      )}
                    >
                      {message.sender === "bot" && (
                        <div className="w-7 h-7 rounded-full bg-[#000080] flex items-center justify-center flex-shrink-0 mt-1">
                          <Bot className="w-3.5 h-3.5 text-white" />
                        </div>
                      )}
                      <div
                        className={cn(
                          "max-w-[78%] rounded-2xl px-4 py-2.5 text-sm",
                          message.sender === "user"
                            ? "bg-[#000080] text-white rounded-br-sm"
                            : "bg-[var(--card)] text-[var(--foreground)] rounded-bl-sm border border-[var(--border)]"
                        )}
                      >
                        {message.type === "quick-actions" && message.data ? (
                          <div className="space-y-2">
                            <p className="font-medium mb-2">{message.text}</p>
                            <div className="grid grid-cols-1 gap-2">
                              {message.data.actions.map((action: QuickAction) => (
                                <button
                                  key={action.id}
                                  onClick={() => handleQuickAction(action)}
                                  className="flex items-start gap-3 p-2.5 rounded-lg bg-[var(--background)] hover:bg-[var(--muted)] transition-colors text-left"
                                >
                                  <div className="w-8 h-8 rounded-lg bg-[#000080]/10 flex items-center justify-center flex-shrink-0">
                                    <action.icon className="w-4 h-4 text-[#000080]" />
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="font-medium text-sm">
                                      {action.label}
                                    </div>
                                    <div className="text-xs text-[var(--muted-foreground)] truncate">
                                      {action.description}
                                    </div>
                                  </div>
                                  <ChevronRight className="w-4 h-4 text-[var(--muted-foreground)] flex-shrink-0" />
                                </button>
                              ))}
                            </div>
                          </div>
                        ) : message.type === "form" && message.data?.actions ? (
                          <div className="space-y-2">
                            {message.data.actions.map((action: GuidedAction) => (
                              <Button
                                key={action.id}
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => handleGuidedAction(action)}
                              >
                                <ExternalLink className="mr-2 h-4 w-4" />
                                {action.label}
                              </Button>
                            ))}
                          </div>
                        ) : (
                          <div>
                            <p className="leading-relaxed whitespace-pre-wrap">
                              {message.text}
                            </p>
                            <div className="flex items-center justify-between mt-1 gap-2">
                              <time
                                className={cn(
                                  "text-xs",
                                  message.sender === "user"
                                    ? "text-white/60"
                                    : "text-[var(--muted-foreground)]"
                                )}
                              >
                                {formatTime(message.timestamp)}
                              </time>

                              {/* Speak button for bot messages */}
                              {message.sender === "bot" && (
                                <button
                                  onClick={() =>
                                     speakText(_compressForSpeak(message.text), message.language || language || "en")
                                   }
                                  className="p-1 rounded hover:bg-white/10"
                                  title={t("chatbot.listen", "Listen")}
                                >
                                  <Volume2 className="w-3 h-3 text-[var(--muted-foreground)]" />
                                </button>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Typing Indicator */}
                  {isTyping && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex gap-2 justify-start"
                    >
                      <div className="w-7 h-7 rounded-full bg-[#000080] flex items-center justify-center flex-shrink-0">
                        <Bot className="w-3.5 h-3.5 text-white" />
                      </div>
                      <div className="bg-[var(--card)] rounded-2xl rounded-bl-sm px-4 py-3 border border-[var(--border)]">
                        <div className="flex gap-1">
                          {[0, 1, 2].map((i) => (
                            <motion.div
                              key={i}
                              animate={{
                                y: [0, -6, 0],
                                opacity: [0.4, 1, 0.4],
                              }}
                              transition={{
                                duration: 0.6,
                                repeat: Infinity,
                                delay: i * 0.15,
                              }}
                              className="w-2 h-2 bg-[#000080] rounded-full"
                            />
                          ))}
                        </div>
                        {isSlowResponse && (
                          <p className="mt-2 text-xs text-[var(--muted-foreground)]">
                            {t("chatbot.slowResponse", "Still working... fetching verified service details.")}
                          </p>
                        )}
                      </div>
                    </motion.div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
                </div>
              </ScrollArea>

              {/* Input Area */}
              <div className="relative z-10 shrink-0 border-t-2 border-[var(--border)] bg-[var(--card)] p-4">
                {voiceStatus !== "idle" && (
                  <div className="mb-2 rounded-md border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2 text-xs text-[var(--muted-foreground)]">
                    {voiceStatus === "recording"
                      ? t("chatbot.voice.recording", "Recording... tap mic again to stop")
                      : voiceStatus === "transcribing"
                        ? t("chatbot.listening", "Listening...")
                        : t("chatbot.thinking", "Thinking...")}
                  </div>
                )}
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex gap-2"
                >
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="flex-shrink-0 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                    aria-label={t("chatbot.attach", "Attach file")}
                    onClick={() => toast.info(t("chatbot.fileSoon", "File upload coming soon"))}
                  >
                    <Paperclip className="w-5 h-5" />
                  </Button>
                  <Input
                    type="text"
                    placeholder={t("chatbot.placeholder", "Ask anything about government services...")}
                    value={inputValue}
                    onChange={(e) => {
                      setInputValue(e.target.value);
                      if (
                        !inputElement &&
                        e.target instanceof HTMLInputElement
                      ) {
                        setInputElement(e.target);
                      }
                    }}
                    className="flex-1 h-12 bg-[var(--input-background)] border-[var(--border)] text-[var(--foreground)]"
                    aria-label={t("chatbot.inputAria", "Chat message input")}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className={cn(
                      "flex-shrink-0",
                      isRecording
                        ? "text-red-500 animate-pulse"
                        : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                    )}
                    aria-label={t("chatbot.voiceInput", "Voice input")}
                    onClick={toggleRecording}
                  >
                    {isRecording ? (
                      <MicOff className="w-5 h-5" />
                    ) : (
                      <Mic className="w-5 h-5" />
                    )}
                  </Button>
                  <Button
                    type="submit"
                    size="icon"
                    className="bg-gradient-to-br from-[#000080] to-[#000066] hover:from-[#000066] hover:to-[#000050] flex-shrink-0 h-12 w-12"
                    disabled={!inputValue.trim() || isTyping}
                    aria-label={t("chatbot.send", "Send message")}
                  >
                    <Send className="w-5 h-5" />
                  </Button>
                </form>
                <div className="text-xs text-[var(--muted-foreground)] mt-3 text-center flex items-center justify-center gap-2">
                  <Sparkles className="w-3 h-3" />
                  <span>
                    {t("chatbot.poweredBy", "Powered by Sarvam AI")} • {t("chatbot.sttTts", "STT/TTS enabled")} • {voiceChatEnabled ? t("chatbot.stsOn", "STS on") : t("chatbot.stsOff", "STS off")}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function _compressForSpeak(text: string, maxChars = 1800): string {
  const cleaned = (text || "").replace(/\s+/g, " ").trim();
  if (cleaned.length <= maxChars) {
    return cleaned;
  }
  const clipped = cleaned.slice(0, maxChars).replace(/\s+\S*$/, "").trim();
  return `${clipped}.`;
}
