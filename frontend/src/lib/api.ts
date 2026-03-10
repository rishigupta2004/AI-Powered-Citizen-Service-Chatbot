function resolveApiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_URL?.trim()
  if (configured) {
    return configured.replace(/\/$/, '')
  }

  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host.includes('vercel.app') || host.includes('seva-sindu-portal')) {
      return 'https://gov-chatbot.fly.dev'
    }
  }

  return 'http://localhost:8000'
}

export const API_BASE_URL = resolveApiBaseUrl()

const DEFAULT_TIMEOUT_MS = 12000

export class ApiError extends Error {
  status?: number
  payload?: unknown

  constructor(message: string, status?: number, payload?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

async function fetchWithTimeout(
  input: RequestInfo | URL,
  init: RequestInit = {},
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)
  try {
    return await fetch(input, { ...init, signal: controller.signal })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError(`Request timed out after ${timeoutMs}ms`)
    }
    throw error
  } finally {
    clearTimeout(timeout)
  }
}

async function readJsonResponse<T>(response: Response): Promise<T> {
  let body: unknown = null
  try {
    body = await response.json()
  } catch {
    body = null
  }

  if (!response.ok) {
    const message =
      (typeof body === 'object' && body && 'detail' in body && String((body as { detail: unknown }).detail)) ||
      (typeof body === 'object' && body && 'error' in body && String((body as { error: unknown }).error)) ||
      `HTTP ${response.status}`
    throw new ApiError(message, response.status, body)
  }
  return body as T
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export type ResponseMode = 'auto' | 'rag_only' | 'sarvam'

export interface ChatResponse {
  response: string
  language: string
  sources?: string[]
  session_id?: string | null
}

export interface VoiceChatResponse {
  transcript: string
  response: string
  audio_base64?: string
  language?: string
  error?: string
}

export interface SpeechToTextResponse {
  transcript: string
  language_code?: string
  error?: string
}

export async function sendChat(
  message: string,
  history: ChatMessage[] = [],
  language = 'auto',
  service_context?: string,
  response_mode: ResponseMode = 'auto',
  session_id?: string,
): Promise<ChatResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      language,
      history,
      service_context,
      response_mode,
      session_id,
    }),
  })
  return readJsonResponse<ChatResponse>(response)
}

export const sendChatMessage = sendChat

export async function sendVoice(audio: Blob, language = 'auto'): Promise<VoiceChatResponse> {
  const form = new FormData()
  form.append('audio', audio, 'recording.webm')
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/voice-chat?language=${language}&fast_mode=true&max_voice_chars=110`,
    {
      method: 'POST',
      body: form,
    },
    20000,
  )
  return readJsonResponse<VoiceChatResponse>(response)
}

export async function speechToText(audio: Blob, language = 'auto'): Promise<SpeechToTextResponse> {
  const form = new FormData()
  form.append('audio', audio, 'recording.webm')
  form.append('language', language)
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/speech-to-text`, {
    method: 'POST',
    body: form,
  }, 20000)
  return readJsonResponse<SpeechToTextResponse>(response)
}

export async function textToSpeech(text: string, language = 'hi') {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/text-to-speech`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language }),
  })

  if (!response.ok) {
    return readJsonResponse<never>(response)
  }

  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('audio/')) {
    const fallbackBody = await response.text()
    throw new ApiError('TTS endpoint did not return audio', response.status, fallbackBody)
  }

  return response.arrayBuffer()
}

export function playAudioBlob(audioData: ArrayBuffer) {
  const blob = new Blob([audioData], { type: 'audio/wav' })
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  return audio
}

export function playBase64Audio(base64Audio: string, mimeType = 'audio/wav') {
  const audio = new Audio(`data:${mimeType};base64,${base64Audio}`)
  return audio
}

export async function getHealth() {
  const response = await fetchWithTimeout(`${API_BASE_URL}/health`, {}, 8000)
  return readJsonResponse<Record<string, unknown>>(response)
}
