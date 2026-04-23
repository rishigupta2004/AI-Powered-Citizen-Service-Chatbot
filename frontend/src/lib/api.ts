function resolveApiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_URL?.trim()
  if (configured) {
    return configured.replace(/\/$/, '')
  }

  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host.includes('vercel.app') || host.includes('seva-sindu-portal')) {
      // Primary: Modal serverless backend (fast, $30/mo free tier)
      return 'https://rishigupta-rg007--seva-sindhu-backend-fastapi-entrypoint.modal.run'
    }
  }

  return 'http://localhost:8000'
}

export const API_BASE_URL = resolveApiBaseUrl()

const DEFAULT_TIMEOUT_MS = 30000

// HF Spaces can take 60+ seconds to cold-start; give chat requests generous room
const CHAT_TIMEOUT_MS = 90000

export class ApiError extends Error {
  status?: number
  payload?: any

  constructor(message: string, status?: number, payload?: any) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
    
    // Set prototype explicitly for built-in class extension
    Object.setPrototypeOf(this, ApiError.prototype)
  }

  // Helper to get a human-friendly string even if the message is weird
  toString(): string {
    return this.message || `Error ${this.status || 'unknown'}`
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
  let body: any = null
  try {
    body = await response.json()
  } catch {
    body = null
  }

  if (!response.ok) {
    let message = `HTTP ${response.status}`
    
    if (typeof body === 'object' && body !== null) {
      // Handle standard FastAPI error detail
      if (body.detail && typeof body.detail === 'string') {
        message = body.detail
      } 
      // Handle nested error object (e.g. {"error": {"detail": "..."}})
      else if (body.error && typeof body.error === 'object' && body.error.detail) {
        message = String(body.error.detail)
      }
      // Handle other common error fields
      else if (body.error && typeof body.error === 'string') {
        message = body.error
      }
      else if (body.message && typeof body.message === 'string') {
        message = body.message
      }
    }
    
    console.error(`[API Error] ${response.status} ${response.url}:`, body || message);
    throw new ApiError(message, response.status, body)
  }
  return body as T
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export type ResponseMode = 'auto' | 'rag_only' | 'sarvam'

export interface ChatAction {
  id: string
  label: string
  type: 'url' | 'navigate'
  url?: string
  page?: string
  service_id?: string
}

export interface ChatResponse {
  response: string
  language: string
  speak_text?: string
  actions?: ChatAction[]
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
  const payload = {
    message,
    language,
    history,
    service_context,
    response_mode,
    session_id,
  }

  const attempt = async (mode: ResponseMode): Promise<ChatResponse> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...payload, response_mode: mode }),
    }, CHAT_TIMEOUT_MS)
    return readJsonResponse<ChatResponse>(response)
  }

  return attempt(response_mode)
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
    45000,
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
  }, 45000)
  return readJsonResponse<SpeechToTextResponse>(response)
}

async function textToSpeechRequest(text: string, language: string) {
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

export async function textToSpeech(text: string, language = 'hi') {
  return textToSpeechRequest(text, language)
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
  const response = await fetchWithTimeout(`${API_BASE_URL}/health`, {}, 15000)
  return readJsonResponse<Record<string, unknown>>(response)
}

/**
 * Fire-and-forget ping to wake the HF Space backend.
 * Call this when the chat widget opens so the Space starts booting
 * before the user actually sends a message.
 */
let _warmUpPromise: Promise<void> | null = null
export function warmUpBackend(): void {
  if (_warmUpPromise) return
  _warmUpPromise = fetch(`${API_BASE_URL}/health`, { method: 'GET' })
    .then(() => { /* Space is awake */ })
    .catch(() => { /* ignore – best effort */ })
    .finally(() => { _warmUpPromise = null })
}

// ── Form Help API ──────────────────────────────────────────────────────────────
// Powers the ?/HELP button in ServiceDetail. Independent from the chat API.

export interface FormHelpRequest {
  service_id: string
  service_name: string
  document_name: string
  language?: string
}

export interface FormHelpResponse {
  help_text: string
  language: string
  sources?: string[]
}

export async function getFormHelp(req: FormHelpRequest): Promise<FormHelpResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/form-help`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    },
    30000,
  )
  return readJsonResponse<FormHelpResponse>(response)
}
