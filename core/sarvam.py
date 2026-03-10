"""
Sarvam AI API client — handles LLM, STT, and TTS in one place.
Docs: https://docs.sarvam.ai
"""

import os
from pathlib import Path

from dotenv import load_dotenv
import httpx
import base64
import logging

# Load .env relative to project root (robust to any CWD).
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=False)

logger = logging.getLogger(__name__)

SARVAM_API_BASE = "https://api.sarvam.ai"
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")

if not SARVAM_API_KEY:
    logger.warning(
        "SARVAM_API_KEY not set. Indian language features (Sarvam AI) are disabled. "
        "Set SARVAM_API_KEY in .env - get your key at https://dashboard.sarvam.ai"
    )

LANG_CODES = {
    "hi": "hi-IN",
    "en": "en-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "pa": "pa-IN",
    "or": "od-IN",
    "od": "od-IN",
    "as": "as-IN",
    "ur": "ur-IN",
    "unknown": "unknown",
    "auto": "unknown",
}


def _normalize_lang_code(language: str | None, default: str = "hi-IN") -> str:
    if not language:
        return default
    cleaned = language.strip()
    if not cleaned:
        return default
    return LANG_CODES.get(cleaned.lower(), cleaned)


class SarvamClient:
    """Async client for Sarvam AI API. Handles: Text generation (LLM), Speech-to-Text, Text-to-Speech."""

    def __init__(self):
        self.api_key = SARVAM_API_KEY
        if not self.api_key:
            logger.warning("SARVAM_API_KEY not set. Sarvam features will be disabled.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "api-subscription-key": self.api_key,
        }

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> str:
        """Call Sarvam-M for text generation."""
        if not self.is_available():
            return "Sarvam API key not configured. Please set SARVAM_API_KEY."

        payload = {
            "model": "sarvam-m",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_prompt:
            payload["messages"] = [
                {"role": "system", "content": system_prompt}
            ] + messages

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SARVAM_API_BASE}/v1/chat/completions",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Sarvam LLM error {e.response.status_code}: {e.response.text}"
            )
            return "I'm having trouble connecting to the AI service. Please try again."
        except Exception as e:
            logger.error(f"Sarvam LLM unexpected error: {e}")
            return "Something went wrong. Please try again in a moment."

    async def speech_to_text(
        self,
        audio_bytes: bytes,
        language: str = "auto",
        audio_format: str = "webm",
        mode: str = "transcribe",
    ) -> dict:
        """Transcribe audio to text using Sarvam STT."""
        if not self.is_available():
            return {"error": "Sarvam API key not configured", "transcript": ""}

        lang_code = _normalize_lang_code(language, default="unknown")
        stt_model = os.getenv("SARVAM_STT_MODEL", "saaras:v3")

        async def _stt_call(model: str, call_mode: str | None) -> dict:
            files = {
                "file": (
                    f"audio.{audio_format}",
                    audio_bytes,
                    f"audio/{audio_format}",
                ),
            }
            data: dict[str, str] = {
                "language_code": lang_code,
                "model": model,
            }
            if call_mode:
                data["mode"] = call_mode

            # STT docs require api-subscription-key header.
            headers = {"api-subscription-key": self.api_key}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SARVAM_API_BASE}/speech-to-text",
                    headers=headers,
                    files=files,
                    data=data,
                )
                response.raise_for_status()
                return response.json()

        try:
            result = await _stt_call(stt_model, mode)
            transcript = result.get("transcript", "")
            if transcript:
                return {
                    "transcript": transcript,
                    "language_code": result.get("language_code", lang_code),
                    "confidence": result.get("language_probability", 1.0),
                    "request_id": result.get("request_id"),
                }

            if stt_model != "saarika:v2.5":
                fallback_result = await _stt_call("saarika:v2.5", None)
                return {
                    "transcript": fallback_result.get("transcript", ""),
                    "language_code": fallback_result.get("language_code", lang_code),
                    "confidence": fallback_result.get("language_probability", 1.0),
                    "request_id": fallback_result.get("request_id"),
                }

            return {
                "transcript": "",
                "language_code": result.get("language_code", lang_code),
                "confidence": result.get("language_probability", 0.0),
                "request_id": result.get("request_id"),
            }

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Sarvam STT error {e.response.status_code}: {e.response.text}"
            )
            err = "Speech recognition failed"
            try:
                parsed = e.response.json()
                if isinstance(parsed, dict):
                    inner = parsed.get("error")
                    if isinstance(inner, dict):
                        err = str(inner.get("message") or inner.get("code") or err)
                    elif isinstance(inner, str):
                        err = inner
            except Exception:
                pass
            return {"error": err, "transcript": ""}
        except Exception as e:
            logger.error(f"Sarvam STT unexpected error: {e}")
            return {"error": str(e), "transcript": ""}

    async def text_to_speech(
        self,
        text: str,
        language: str = "hi",
        speaker: str = "",
        speed: float = 1.0,
    ) -> dict:
        """Convert text to speech using Sarvam TTS."""
        if not self.is_available():
            return {"error": "Sarvam API key not configured"}

        lang_code = _normalize_lang_code(language, default="hi-IN")

        voice = speaker or "shubh"

        payload = {
            "text": text[:2500],
            "target_language_code": lang_code,
            "speaker": voice,
            "pace": speed,
            "model": "bulbul:v3",
            "output_audio_codec": "wav",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SARVAM_API_BASE}/text-to-speech",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                audio_b64 = result["audios"][0]
                audio_bytes = base64.b64decode(audio_b64)
                return {
                    "audio_base64": audio_b64,
                    "audio_bytes": audio_bytes,
                    "format": "wav",
                }

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Sarvam TTS error {e.response.status_code}: {e.response.text}"
            )
            return {"error": "Text-to-speech failed"}
        except Exception as e:
            logger.error(f"Sarvam TTS unexpected error: {e}")
            return {"error": str(e)}

    async def translate(
        self,
        text: str,
        source_language: str = "en",
        target_language: str = "hi",
    ) -> str:
        """Translate text between Indian languages using Sarvam IndicTrans2."""
        if not self.is_available():
            return text

        payload = {
            "input": text,
            "source_language_code": _normalize_lang_code(
                source_language, default="auto"
            ),
            "target_language_code": _normalize_lang_code(
                target_language, default="hi-IN"
            ),
            "speaker_gender": "Female",
            "mode": "formal",
            "model": "mayura:v1",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{SARVAM_API_BASE}/translate",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                return response.json().get("translated_text", text)
        except Exception as e:
            logger.error(f"Sarvam translate error: {e}")
            return text


sarvam = SarvamClient()
