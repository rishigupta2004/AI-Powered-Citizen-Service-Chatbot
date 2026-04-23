# core/sarvam.py
import base64
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

try:
    from sarvamai import SarvamAI
except ImportError:  # pragma: no cover - optional dependency in some environments
    SarvamAI = None

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local", override=True)

# ── Model configuration (migrate from deprecated sarvam-m / mayura:v1) ───────
DEFAULT_CHAT_MODEL = "sarvam-30b"
DEFAULT_STT_MODEL = "saaras:v3"
DEFAULT_TTS_MODEL = "bulbul:v3"
DEFAULT_TRANSLATE_MODEL = "sarvam-translate:v1"

LANG_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "mr": "mr-IN",
    "pa": "pa-IN",
    "od": "od-IN",
    "or": "od-IN",
    "as": "as-IN",
    "ur": "ur-IN",
    "ne": "ne-IN",
    "kok": "kok-IN",
    "ks": "ks-IN",
    "sd": "sd-IN",
    "sa": "sa-IN",
    "sat": "sat-IN",
    "mni": "mni-IN",
    "doi": "doi-IN",
    "mai": "mai-IN",
}


def _pick_attr(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _normalize_language_code(language: str | None) -> str | None:
    if not language:
        return None
    normalized = language.strip().lower()
    if not normalized or normalized == "auto":
        return None
    if "-" in normalized:
        return normalized
    return LANG_CODES.get(normalized)


class SarvamClient:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY", "")
        self.chat_model = os.getenv("SARVAM_CHAT_MODEL", DEFAULT_CHAT_MODEL)
        self.stt_model = os.getenv("SARVAM_STT_MODEL", DEFAULT_STT_MODEL)
        self.stt_fallback_model = os.getenv("SARVAM_STT_FALLBACK_MODEL", "").strip()
        self.tts_model = os.getenv("SARVAM_TTS_MODEL", DEFAULT_TTS_MODEL)
        self.tts_speaker = os.getenv("SARVAM_TTS_SPEAKER", "").strip()
        self.translate_model = os.getenv("SARVAM_TRANSLATE_MODEL", DEFAULT_TRANSLATE_MODEL)

        if not self.api_key:
            logger.warning("SARVAM_API_KEY not set.")
            self.client = None
        elif SarvamAI is None:
            logger.warning("sarvamai package not installed. Sarvam features will be disabled.")
            self.client = None
        else:
            self.client = SarvamAI(api_subscription_key=self.api_key)
            logger.info(
                "SarvamClient initialised chat_model=%s stt_model=%s tts_model=%s translate_model=%s",
                self.chat_model,
                self.stt_model,
                self.tts_model,
                self.translate_model,
            )

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

    async def chat(
        self,
        messages: list,
        system_prompt: str = None,
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> str:
        if not self.is_available():
            return "Sarvam API key not configured."
        try:
            all_messages = []
            if system_prompt:
                all_messages.append({"role": "system", "content": system_prompt})
            all_messages.extend(messages)

            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions(
                    model=self.chat_model,
                    messages=all_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Sarvam chat error: %s", e)
            return "I'm having trouble connecting to the AI service. Please try again."

    async def _transcribe_with_model(
        self,
        *,
        audio_bytes: bytes,
        audio_format: str,
        model_name: str,
        language_code: str | None,
    ) -> dict:
        import asyncio
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        def _call_stt():
            try:
                with open(tmp_path, "rb") as audio_file:
                    kwargs: dict[str, Any] = {
                        "file": audio_file,
                        "model": model_name,
                    }
                    if model_name.startswith("saaras:"):
                        kwargs["mode"] = "transcribe"
                    if language_code:
                        kwargs["language_code"] = language_code
                    return self.client.speech_to_text.transcribe(**kwargs)
            finally:
                try:
                    os.unlink(tmp_path)
                except FileNotFoundError:
                    pass

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call_stt)
        return {
            "transcript": _pick_attr(response, "transcript", "") or "",
            "language_code": _pick_attr(response, "language_code", None) or language_code,
            "confidence": _pick_attr(response, "language_probability", 1.0) or 1.0,
        }

    async def speech_to_text(
        self,
        audio_bytes: bytes,
        language: str = "hi",
        audio_format: str = "webm",
    ) -> dict:
        if not self.is_available():
            return {"error": "Sarvam API not configured", "transcript": ""}

        language_code = _normalize_language_code(language)
        try:
            return await self._transcribe_with_model(
                audio_bytes=audio_bytes,
                audio_format=audio_format,
                model_name=self.stt_model,
                language_code=language_code,
            )
        except Exception as e:
            if self.stt_fallback_model and self.stt_fallback_model != self.stt_model:
                logger.warning(
                    "Sarvam STT primary model failed; retrying fallback model=%s error=%s",
                    self.stt_fallback_model,
                    e,
                )
                try:
                    return await self._transcribe_with_model(
                        audio_bytes=audio_bytes,
                        audio_format=audio_format,
                        model_name=self.stt_fallback_model,
                        language_code=language_code,
                    )
                except Exception as fallback_error:
                    logger.error("Sarvam STT fallback error: %s", fallback_error)
                    return {"error": str(fallback_error), "transcript": ""}

            logger.error("Sarvam STT error: %s", e)
            return {"error": str(e), "transcript": ""}

    async def text_to_speech(
        self,
        text: str,
        language: str = "hi",
        speaker: str = None,
        speed: float = 1.0,
    ) -> dict:
        if not self.is_available():
            return {"error": "Sarvam API not configured"}

        lang_code = _normalize_language_code(language) or "hi-IN"
        default_speakers = {
            "hi-IN": "meera",
            "ta-IN": "pavithra",
            "te-IN": "arvind",
            "bn-IN": "isha",
            "en-IN": "arjun",
            "mr-IN": "maitreyi",
        }
        voice = speaker or self.tts_speaker or default_speakers.get(lang_code, "meera")

        try:
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.text_to_speech.convert(
                    text=text[:2500],
                    model=self.tts_model,
                    target_language_code=lang_code,
                    speaker=voice,
                    pace=speed,
                ),
            )
            audios = _pick_attr(response, "audios", []) or []
            if not audios:
                raise ValueError("Sarvam TTS response did not include audio data")
            audio_b64 = audios[0]
            return {
                "audio_base64": audio_b64,
                "audio_bytes": base64.b64decode(audio_b64),
                "format": "wav",
            }
        except Exception as e:
            logger.error("Sarvam TTS error: %s", e)
            return {"error": str(e)}

    async def translate(
        self,
        text: str,
        source_language: str = "en",
        target_language: str = "hi",
    ) -> str:
        if not self.is_available():
            return text
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.text.translate(
                    input=text,
                    source_language_code=_normalize_language_code(source_language) or "en-IN",
                    target_language_code=_normalize_language_code(target_language) or "hi-IN",
                    model=self.translate_model,
                    speaker_gender="Female",
                ),
            )
            return _pick_attr(response, "translated_text", text)
        except Exception as e:
            logger.error("Sarvam translate error: %s", e)
            return text


sarvam = SarvamClient()
