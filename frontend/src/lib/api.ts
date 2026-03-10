const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatResponse {
  response: string
  language: string
  sources?: string[]
  session_id?: string | null
}

export async function sendChat(
  message: string,
  history: ChatMessage[] = [],
  language = 'auto',
  service_context?: string,
): Promise<ChatResponse> {
  const r = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language, history, service_context }),
  })
  return r.json()
}

export const sendChatMessage = sendChat

export async function sendVoice(audio: Blob, language = 'hi') {
  const form = new FormData()
  form.append('audio', audio, 'recording.webm')
  const r = await fetch(`${API_BASE_URL}/api/v1/voice-chat?language=${language}`, {
    method: 'POST',
    body: form,
  })
  return r.json()
}

export async function speechToText(audio: Blob, language = 'hi') {
  const form = new FormData()
  form.append('audio', audio, 'recording.webm')
  form.append('language', language)
  const r = await fetch(`${API_BASE_URL}/api/v1/speech-to-text`, {
    method: 'POST',
    body: form,
  })
  return r.json()
}

export async function textToSpeech(text: string, language = 'hi') {
  const r = await fetch(`${API_BASE_URL}/api/v1/text-to-speech`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language }),
  })
  return r.arrayBuffer()
}

export function playAudioBlob(audioData: ArrayBuffer) {
  const blob = new Blob([audioData], { type: 'audio/wav' })
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  void audio.play()
  return audio
}

export async function getHealth() {
  const r = await fetch(`${API_BASE_URL}/health`)
  return r.json()
}
