# core/sarvam.py
import os
import base64
import logging
from sarvamai import SarvamAI

logger = logging.getLogger(__name__)

# ── Model configuration (migrate from deprecated sarvam-m / mayura:v1) ───────
DEFAULT_CHAT_MODEL = "sarvam-30b"          # was: sarvam-m (deprecated)
DEFAULT_TRANSLATE_MODEL = "sarvam-translate:v1"  # was: mayura:v1

LANG_CODES = {
    "hi": "hi-IN", "en": "en-IN", "ta": "ta-IN",
    "te": "te-IN", "bn": "bn-IN", "mr": "mr-IN",
    "gu": "gu-IN", "kn": "kn-IN", "ml": "ml-IN",
    "pa": "pa-IN", "or": "or-IN", "ur": "ur-IN",
    "auto": "hi-IN",
}

class SarvamClient:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY", "")
        self.chat_model = os.getenv("SARVAM_CHAT_MODEL", DEFAULT_CHAT_MODEL)
        self.translate_model = os.getenv("SARVAM_TRANSLATE_MODEL", DEFAULT_TRANSLATE_MODEL)
        self.tts_model = os.getenv("SARVAM_TTS_MODEL", "bulbul:v2")
        self.tts_speaker = os.getenv("SARVAM_TTS_SPEAKER", "")
        if not self.api_key:
            logger.warning("SARVAM_API_KEY not set.")
            self.client = None
        else:
            self.client = SarvamAI(api_subscription_key=self.api_key)
            logger.info("SarvamClient initialised  chat_model=%s  tts_model=%s  translate_model=%s",
                        self.chat_model, self.tts_model, self.translate_model)

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

    async def chat(self, messages: list, system_prompt: str = None,
                   temperature: float = 0.3, max_tokens: int = 512) -> str:
        if not self.is_available():
            return "Sarvam API key not configured."
        try:
            all_messages = []
            if system_prompt:
                all_messages.append({"role": "system", "content": system_prompt})
            all_messages.extend(messages)

            # SDK is synchronous — run in thread to not block async
            import asyncio
            loop = asyncio.get_event_loop()
            _model = self.chat_model
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions(
                    model=_model,
                    messages=all_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Sarvam chat error: {e}")
            return "I'm having trouble connecting to the AI service. Please try again."

    async def speech_to_text(self, audio_bytes: bytes,
                              language: str = "hi", audio_format: str = "webm") -> dict:
        if not self.is_available():
            return {"error": "Sarvam API not configured", "transcript": ""}
        try:
            import asyncio
            import tempfile

            # Write to temp file — SDK needs file object
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as f:
                f.write(audio_bytes)
                tmp_path = f.name

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.speech_to_text.transcribe(
                    file=open(tmp_path, "rb"),
                    model="saarika:v1",
                    language_code=LANG_CODES.get(language, "hi-IN"),
                )
            )
            return {
                "transcript": response.transcript,
                "language_code": LANG_CODES.get(language, "hi-IN"),
                "confidence": 1.0,
            }
        except Exception as e:
            logger.error(f"Sarvam STT error: {e}")
            return {"error": str(e), "transcript": ""}

    async def text_to_speech(self, text: str, language: str = "hi",
                              speaker: str = None, speed: float = 1.0) -> dict:
        if not self.is_available():
            return {"error": "Sarvam API not configured"}
        
        lang_code = LANG_CODES.get(language, "hi-IN")
        is_v3 = "v3" in self.tts_model

        # Speaker lists differ between bulbul:v2 and v3
        if is_v3:
            default_speakers = {
                "hi-IN": "shubh", "ta-IN": "kavitha", "te-IN": "ratan",
                "bn-IN": "ishita", "en-IN": "aditya", "mr-IN": "manisha",
                "gu-IN": "priya", "kn-IN": "shreya", "ml-IN": "vidya",
                "pa-IN": "neha",
            }
            fallback = "shubh"
        else:
            default_speakers = {
                "hi-IN": "anushka", "ta-IN": "anushka", "te-IN": "anushka",
                "bn-IN": "anushka", "en-IN": "anushka", "mr-IN": "manisha",
            }
            fallback = "anushka"

        voice = speaker or self.tts_speaker or default_speakers.get(lang_code, fallback)
        max_chars = 2500 if is_v3 else 1500

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            tts_kwargs = {
                "text": text[:max_chars],
                "target_language_code": lang_code,
                "model": self.tts_model,
                "speaker": voice,
                "pace": speed,
            }
            # enable_preprocessing is only supported on bulbul:v2
            if not is_v3:
                tts_kwargs["enable_preprocessing"] = True

            response = await loop.run_in_executor(
                None,
                lambda: self.client.text_to_speech.convert(**tts_kwargs)
            )
            audio_b64 = response.audios[0]
            return {
                "audio_base64": audio_b64,
                "audio_bytes": base64.b64decode(audio_b64),
                "format": "wav",
            }
        except Exception as e:
            logger.error(f"Sarvam TTS error: {e}")
            return {"error": str(e)}

    async def translate(self, text: str, source_language: str = "en",
                        target_language: str = "hi") -> str:
        if not self.is_available():
            return text
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            _translate_model = self.translate_model
            response = await loop.run_in_executor(
                None,
                lambda: self.client.text.translate(
                    input=text,
                    source_language_code=LANG_CODES.get(source_language, "en-IN"),
                    target_language_code=LANG_CODES.get(target_language, "hi-IN"),
                    model=_translate_model,
                    speaker_gender="Female",
                )
            )
            return response.translated_text
        except Exception as e:
            logger.error(f"Sarvam translate error: {e}")
            return text

sarvam = SarvamClient()
