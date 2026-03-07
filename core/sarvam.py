"""
Sarvam AI API client — handles LLM, STT, and TTS in one place.
Docs: https://docs.sarvam.ai
"""

import os
import httpx
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SARVAM_API_BASE = "https://api.sarvam.ai"
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")

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
    "or": "or-IN",
    "as": "as-IN",
    "ur": "ur-IN",
    "auto": "hi-IN",
}


class SarvamClient:
    """Async client for Sarvam AI API. Handles: Text generation (LLM), Speech-to-Text, Text-to-Speech."""

    def __init__(self):
        self.api_key = SARVAM_API_KEY
        if not self.api_key:
            logger.warning("SARVAM_API_KEY not set. Sarvam features will be disabled.")
        self.headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = None,
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
                    headers=self.headers,
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
        language: str = "hi",
        audio_format: str = "webm",
    ) -> dict:
        """Transcribe audio to text using Sarvam STT."""
        if not self.is_available():
            return {"error": "Sarvam API key not configured", "transcript": ""}

        lang_code = LANG_CODES.get(language, "hi-IN")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {
                    "file": (
                        f"audio.{audio_format}",
                        audio_bytes,
                        f"audio/{audio_format}",
                    ),
                }
                data = {
                    "language_code": lang_code,
                    "model": "saarika:v2",
                    "with_timestamps": "false",
                }
                headers = {"api-subscription-key": self.api_key}

                response = await client.post(
                    f"{SARVAM_API_BASE}/speech-to-text",
                    headers=headers,
                    files=files,
                    data=data,
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "transcript": result.get("transcript", ""),
                    "language_code": result.get("language_code", lang_code),
                    "confidence": result.get("confidence", 1.0),
                }

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Sarvam STT error {e.response.status_code}: {e.response.text}"
            )
            return {"error": "Speech recognition failed", "transcript": ""}
        except Exception as e:
            logger.error(f"Sarvam STT unexpected error: {e}")
            return {"error": str(e), "transcript": ""}

    async def text_to_speech(
        self,
        text: str,
        language: str = "hi",
        speaker: str = None,
        speed: float = 1.0,
    ) -> dict:
        """Convert text to speech using Sarvam TTS."""
        if not self.is_available():
            return {"error": "Sarvam API key not configured"}

        lang_code = LANG_CODES.get(language, "hi-IN")

        default_speakers = {
            "hi-IN": "meera",
            "ta-IN": "pavithra",
            "te-IN": "arvind",
            "bn-IN": "isha",
            "mr-IN": "maitreyi",
            "gu-IN": "diya",
            "kn-IN": "neel",
            "ml-IN": "lekha",
            "pa-IN": "amol",
            "en-IN": "arjun",
        }
        voice = speaker or default_speakers.get(lang_code, "meera")

        payload = {
            "inputs": [text[:500]],
            "target_language_code": lang_code,
            "speaker": voice,
            "pace": speed,
            "enable_preprocessing": True,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SARVAM_API_BASE}/text-to-speech",
                    headers=self.headers,
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
            "source_language_code": LANG_CODES.get(source_language, "en-IN"),
            "target_language_code": LANG_CODES.get(target_language, "hi-IN"),
            "speaker_gender": "Female",
            "mode": "formal",
            "model": "mayura:v1",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{SARVAM_API_BASE}/translate",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json().get("translated_text", text)
        except Exception as e:
            logger.error(f"Sarvam translate error: {e}")
            return text


sarvam = SarvamClient()
