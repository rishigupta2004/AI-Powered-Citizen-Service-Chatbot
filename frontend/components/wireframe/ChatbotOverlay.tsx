import React, { useState, useRef, useEffect } from "react";

const API = "https://gov-chatbot.fly.dev"\;

interface Message { type: "user" | "bot"; text: string; }

export default function ChatbotOverlay() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { type: "bot", text: "नमस्ते! Welcome to Seva Sindhu AI Assistant 🇮🇳\n\nI'm here to help you with government services. How can I assist you today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState("en");
  const [recording, setRecording] = useState(false);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function sendMessage(text: string) {
    if (!text.trim()) return;
    setMessages(m => [...m, { type: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, language: lang, history: [] }),
      });
      const d = await r.json();
      const reply = d.response || d.text || d.detail || "Sorry, I could not get a response.";
      setMessages(m => [...m, { type: "bot", text: reply }]);
    } catch {
      setMessages(m => [...m, { type: "bot", text: "Connection error. Please try again." }]);
    }
    setLoading(false);
  }

  async function speak(text: string) {
    try {
      const r = await fetch(`${API}/api/v1/text-to-speech`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language: lang }),
      });
      const buf = await r.arrayBuffer();
      const audio = new Audio(URL.createObjectURL(new Blob([buf], { type: "audio/wav" })));
      audio.play();
    } catch { console.error("TTS failed"); }
  }

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mr = new MediaRecorder(stream);
    chunksRef.current = [];
    mr.ondataavailable = e => chunksRef.current.push(e.data);
    mr.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const form = new FormData();
      form.append("audio", blob, "recording.webm");
      form.append("language", lang);
      setLoading(true);
      try {
        const r = await fetch(`${API}/api/v1/speech-to-text`, { method: "POST", body: form });
        const d = await r.json();
        if (d.transcript) await sendMessage(d.transcript);
      } catch { console.error("STT failed"); }
      setLoading(false);
    };
    mr.start();
    mediaRef.current = mr;
    setRecording(true);
  }

  function stopRecording() {
    mediaRef.current?.stop();
    setRecording(false);
  }

  const quickActions = ["Check Application Status", "How to apply for Passport?", "Aadhaar update process", "PAN card apply online"];

  return (
    <>
      {/* FAB */}
      <button onClick={() => setOpen(o => !o)}
        style={{ position: "fixed", bottom: 24, right: 24, width: 56, height: 56, borderRadius: "50%", background: "#1e3a8a", color: "white", border: "none", cursor: "pointer", fontSize: 24, zIndex: 9999, boxShadow: "0 4px 20px rgba(0,0,0,0.3)" }}>
        {open ? "✕" : "🤖"}
      </button>

      {open && (
        <div style={{ position: "fixed", bottom: 90, right: 24, width: 380, height: 600, background: "#0f172a", borderRadius: 16, display: "flex", flexDirection: "column", zIndex: 9998, boxShadow: "0 8px 40px rgba(0,0,0,0.5)", border: "1px solid #1e3a8a" }}>
          {/* Header */}
          <div style={{ background: "#1e3a8a", padding: "12px 16px", borderRadius: "16px 16px 0 0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ color: "white", fontWeight: 700 }}>🇮🇳 Seva Sindhu AI</div>
            <select value={lang} onChange={e => setLang(e.target.value)}
              style={{ background: "#2563eb", color: "white", border: "none", borderRadius: 6, padding: "2px 6px", fontSize: 12 }}>
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="ta">தமிழ்</option>
              <option value="te">తెలుగు</option>
              <option value="bn">বাংলা</option>
              <option value="mr">मराठी</option>
              <option value="gu">ગુજરાતી</option>
              <option value="kn">ಕನ್ನಡ</option>
              <option value="ml">മലയാളം</option>
              <option value="pa">ਪੰਜਾਬੀ</option>
            </select>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
            {messages.map((m, i) => (
              <div key={i} style={{ display: "flex", justifyContent: m.type === "user" ? "flex-end" : "flex-start", gap: 8, alignItems: "flex-end" }}>
                {m.type === "bot" && <div style={{ width: 32, height: 32, borderRadius: "50%", background: "#1e3a8a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, flexShrink: 0 }}>🤖</div>}
                <div style={{ maxWidth: "75%", background: m.type === "user" ? "#1e3a8a" : "#1e293b", color: "white", borderRadius: m.type === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px", padding: "10px 14px", fontSize: 14, lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
                  {m.text}
                  {m.type === "bot" && (
                    <button onClick={() => speak(m.text)} style={{ background: "none", border: "none", color: "#94a3b8", cursor: "pointer", fontSize: 12, marginLeft: 8 }}>🔊</button>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <div style={{ width: 32, height: 32, borderRadius: "50%", background: "#1e3a8a", display: "flex", alignItems: "center", justifyContent: "center" }}>🤖</div>
                <div style={{ background: "#1e293b", borderRadius: 16, padding: "10px 14px", color: "#94a3b8", fontSize: 14 }}>⏳ Thinking...</div>
              </div>
            )}
            {messages.length === 1 && !loading && (
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 8 }}>
                {quickActions.map((a, i) => (
                  <button key={i} onClick={() => sendMessage(a)}
                    style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 10, padding: "10px 14px", color: "white", cursor: "pointer", textAlign: "left", fontSize: 13, display: "flex", justifyContent: "space-between" }}>
                    {a} <span>›</span>
                  </button>
                ))}
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div style={{ padding: "12px 16px", borderTop: "1px solid #1e293b", display: "flex", gap: 8, alignItems: "center" }}>
            <input value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage(input)}
              placeholder="Ask about government services..."
              style={{ flex: 1, background: "#1e293b", border: "1px solid #334155", borderRadius: 10, padding: "10px 14px", color: "white", fontSize: 14, outline: "none" }} />
            <button onClick={() => sendMessage(input)} disabled={loading || !input.trim()}
              style={{ background: "#1e3a8a", border: "none", borderRadius: 10, padding: "10px 14px", color: "white", cursor: "pointer", fontSize: 16 }}>➤</button>
            <button onMouseDown={startRecording} onMouseUp={stopRecording} onTouchStart={startRecording} onTouchEnd={stopRecording}
              style={{ background: recording ? "#dc2626" : "#1e293b", border: "1px solid #334155", borderRadius: 10, padding: "10px 12px", color: "white", cursor: "pointer", fontSize: 16 }}>
              {recording ? "⏹" : "🎤"}
            </button>
          </div>
          <div style={{ textAlign: "center", fontSize: 11, color: "#475569", padding: "4px 0 8px" }}>✨ Powered by Sarvam AI • Speech enabled • 24/7</div>
        </div>
      )}
    </>
  );
}
