const API_BASE = "https://gov-chatbot.fly.dev";

export async function sendChat(message: string, language: string, history: any[]) {
  const r = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language, history }),
  });
  return r.json();
}

export const sendChatMessage = sendChat;

export async function sendVoice(audio: Blob, language: string) {
  const form = new FormData();
  form.append("audio", audio, "recording.webm");
  const r = await fetch(`${API_BASE}/api/v1/voice-chat?language=${language}`, {
    method: "POST",
    body: form,
  });
  return r.json();
}

export async function speechToText(audio: Blob, language: string = "hi") {
  const form = new FormData();
  form.append("audio", audio, "recording.webm");
  form.append("language", language);
  const r = await fetch(`${API_BASE}/api/v1/speech-to-text`, {
    method: "POST",
    body: form,
  });
  return r.json();
}

export async function textToSpeech(text: string, language: string = "hi") {
  const r = await fetch(`${API_BASE}/api/v1/text-to-speech`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language }),
  });
  return r.arrayBuffer();
}

export async function playAudioBlob(audioData: ArrayBuffer) {
  const blob = new Blob([audioData], { type: "audio/wav" });
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.play();
  return audio;
}

export async function getHealth() {
  const r = await fetch(`${API_BASE}/api/v1/health`);
  return r.json();
}
