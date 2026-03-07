# Complete Implementation Guide
## AI-Powered Citizen Service Chatbot — Sarvam-M Integration

**Stack:** Supabase (DB) · Fly.io (FastAPI) · Vercel (React) · Sarvam API (LLM + STT + TTS)  
**Do these steps in order. Each step builds on the previous one.**

---

## Before You Start — Get Your Keys

```
1. Sarvam API key    → sarvam.ai → Sign up → Dashboard → API Keys
2. HF Token          → huggingface.co/settings/tokens → New token (Read)
                       Then accept Sarvam-M license at huggingface.co/sarvamai/sarvam-m
3. Supabase          → supabase.com → New project → Settings → Database
                       Copy "Connection string" (URI format)
4. Fly.io            → fly.io → Sign up (free) → install CLI:
                       brew install flyctl
                       flyctl auth login
```

---

## STEP 1 — Supabase Database Setup

### 1.1 Enable pgvector on Supabase

Go to your Supabase project → **SQL Editor** → run this once:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify it worked
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 1.2 Update your DATABASE_URL

Your `core/database.py` already reads from env. Just update your `.env`:

```bash
# .env  (never commit this file)

# Replace this with your Supabase connection string
# Get it from: Supabase Dashboard → Settings → Database → Connection string → URI
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Sarvam API — handles LLM + STT + TTS (one key for everything)
SARVAM_API_KEY=your_sarvam_api_key_here

# HuggingFace — needed for multilingual embeddings model download
HF_TOKEN=hf_your_token_here

# Switch on the new model features
EMBEDDING_MODEL=intfloat/multilingual-e5-small
EMBEDDING_ENABLED=true
GENERATIVE_ENABLED=true
LLM_PROVIDER=SARVAM

# Keep these
RATE_LIMIT_RPS=10
RATE_LIMIT_BURST=20
```

### 1.3 Migrate your local data to Supabase

Run this once to push your existing local PostgreSQL data to Supabase:

```bash
# Export from local PostgreSQL
pg_dump -h localhost -U postgres gov_chatbot_db > local_backup.sql

# Import into Supabase
# Get the connection string from Supabase Dashboard → Settings → Database → Connection string
psql "postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres" < local_backup.sql
```

---

## STEP 2 — Swap Embedding Model

**Why:** `all-MiniLM-L6-v2` is English-only. Hindi/Tamil queries will return garbage vector
search results. `multilingual-e5-small` supports 100+ languages including all Indic scripts,
and is the same 384 dimensions — so your pgvector schema needs zero changes.

### 2.1 Update `core/embeddings.py`

Find the model initialization in your existing `core/embeddings.py` and change:

```python
# BEFORE (find this line)
DEFAULT_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# AFTER (change the default)
DEFAULT_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
```

Also update the `embed_text` function to use the correct prefix format that
`multilingual-e5` requires:

```python
# In core/embeddings.py — update the embed function
def embed_text(self, text: str, is_query: bool = False) -> list[float]:
    """
    multilingual-e5-small requires prefix strings for best performance:
    - Queries:   "query: <text>"
    - Documents: "passage: <text>"
    """
    if isinstance(self.model, SentenceTransformer):
        # Add e5 prefix for query vs passage
        prefix = "query: " if is_query else "passage: "
        prefixed = prefix + text.strip()
        embedding = self.model.encode(prefixed, normalize_embeddings=True)
        return embedding.tolist()
    return []

def embed_batch(self, texts: list[str], is_query: bool = False) -> list[list[float]]:
    """Batch embed with e5 prefix."""
    if isinstance(self.model, SentenceTransformer):
        prefix = "query: " if is_query else "passage: "
        prefixed = [prefix + t.strip() for t in texts]
        embeddings = self.model.encode(prefixed, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()
    return []
```

### 2.2 Update `core/search.py` — pass is_query=True for searches

Find where search queries are embedded in `core/search.py` and add `is_query=True`:

```python
# In core/search.py — find the vector search section and update like this:

def vector_search(self, query: str, limit: int = 10, service_id: int = None):
    """Semantic vector search with multilingual support."""
    try:
        embedder = EmbeddingEngine()
        # Pass is_query=True so e5 uses "query: " prefix
        query_vector = embedder.embed_text(query, is_query=True)
        # ... rest of your existing vector search code stays the same
    except Exception as e:
        logger.error(f"Vector search error: {e}")
        return []
```

### 2.3 Re-embed all existing content chunks

After updating the model, your existing embeddings are stale. Re-generate them:

```bash
# This re-embeds all content_chunks rows with the new multilingual model
# Your existing script already handles this
python scripts/backfill_embeddings.py

# Expected output: "Processed X chunks, updated Y embeddings"
# Takes 5-15 minutes depending on how many chunks you have
```

---

## STEP 3 — Sarvam API Integration (LLM + STT + TTS)

### 3.1 Create `core/sarvam.py` — NEW FILE

This is the single client that handles all Sarvam API calls.

```python
# core/sarvam.py
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

# Language code mapping — Sarvam uses BCP-47 codes
LANG_CODES = {
    "hi": "hi-IN",   # Hindi
    "en": "en-IN",   # Indian English
    "ta": "ta-IN",   # Tamil
    "te": "te-IN",   # Telugu
    "bn": "bn-IN",   # Bengali
    "mr": "mr-IN",   # Marathi
    "gu": "gu-IN",   # Gujarati
    "kn": "kn-IN",   # Kannada
    "ml": "ml-IN",   # Malayalam
    "pa": "pa-IN",   # Punjabi
    "or": "or-IN",   # Odia
    "as": "as-IN",   # Assamese
    "ur": "ur-IN",   # Urdu
    "auto": "hi-IN", # Default to Hindi for auto-detect
}


class SarvamClient:
    """
    Async client for Sarvam AI API.
    Handles: Text generation (LLM), Speech-to-Text, Text-to-Speech.
    """

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

    # ─────────────────────────────────────────────────────────────────────
    # LLM — Text Generation
    # ─────────────────────────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = None,
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> str:
        """
        Call Sarvam-M for text generation.

        Args:
            messages: list of {"role": "user"/"assistant", "content": "..."}
            system_prompt: Optional system context
            temperature: 0.1-0.9, lower = more factual (use 0.3 for gov QA)
            max_tokens: Max response length

        Returns:
            Generated text string
        """
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
                    f"{SARVAM_API_BASE}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            logger.error(f"Sarvam LLM error {e.response.status_code}: {e.response.text}")
            return "I'm having trouble connecting to the AI service. Please try again."
        except Exception as e:
            logger.error(f"Sarvam LLM unexpected error: {e}")
            return "Something went wrong. Please try again in a moment."

    # ─────────────────────────────────────────────────────────────────────
    # STT — Speech to Text
    # ─────────────────────────────────────────────────────────────────────

    async def speech_to_text(
        self,
        audio_bytes: bytes,
        language: str = "hi",
        audio_format: str = "webm",
    ) -> dict:
        """
        Transcribe audio to text using Sarvam STT.

        Args:
            audio_bytes: Raw audio bytes (from browser MediaRecorder)
            language: Language code (hi, ta, te, bn, etc.) or "auto"
            audio_format: "webm", "wav", "mp3", "ogg"

        Returns:
            {
                "transcript": "transcribed text",
                "language_code": "hi-IN",
                "confidence": 0.95
            }
        """
        if not self.is_available():
            return {"error": "Sarvam API key not configured", "transcript": ""}

        lang_code = LANG_CODES.get(language, "hi-IN")

        # Sarvam STT expects multipart form data
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {
                    "file": (f"audio.{audio_format}", audio_bytes, f"audio/{audio_format}"),
                }
                data = {
                    "language_code": lang_code,
                    "model": "saarika:v2",       # Sarvam's STT model
                    "with_timestamps": "false",
                }
                headers = {"api-subscription-key": self.api_key}
                # Remove Content-Type — httpx sets it automatically for multipart

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
            logger.error(f"Sarvam STT error {e.response.status_code}: {e.response.text}")
            return {"error": "Speech recognition failed", "transcript": ""}
        except Exception as e:
            logger.error(f"Sarvam STT unexpected error: {e}")
            return {"error": str(e), "transcript": ""}

    # ─────────────────────────────────────────────────────────────────────
    # TTS — Text to Speech
    # ─────────────────────────────────────────────────────────────────────

    async def text_to_speech(
        self,
        text: str,
        language: str = "hi",
        speaker: str = None,
        speed: float = 1.0,
    ) -> dict:
        """
        Convert text to speech using Sarvam TTS.

        Args:
            text: Text to speak (max ~500 chars per call)
            language: Language code (hi, ta, te, bn, etc.)
            speaker: Voice name (optional, Sarvam picks default if None)
            speed: Playback speed (0.5 - 1.5)

        Returns:
            {
                "audio_base64": "base64 encoded WAV audio",
                "audio_bytes": bytes,
            }
        """
        if not self.is_available():
            return {"error": "Sarvam API key not configured"}

        lang_code = LANG_CODES.get(language, "hi-IN")

        # Default speakers per language (Sarvam's built-in voices)
        default_speakers = {
            "hi-IN": "meera",    "ta-IN": "pavithra",
            "te-IN": "arvind",   "bn-IN": "isha",
            "mr-IN": "maitreyi", "gu-IN": "diya",
            "kn-IN": "neel",     "ml-IN": "lekha",
            "pa-IN": "amol",     "en-IN": "arjun",
        }
        voice = speaker or default_speakers.get(lang_code, "meera")

        payload = {
            "inputs": [text[:500]],   # Sarvam TTS limit per request
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
            logger.error(f"Sarvam TTS error {e.response.status_code}: {e.response.text}")
            return {"error": "Text-to-speech failed"}
        except Exception as e:
            logger.error(f"Sarvam TTS unexpected error: {e}")
            return {"error": str(e)}

    # ─────────────────────────────────────────────────────────────────────
    # TRANSLATE — Bonus utility
    # ─────────────────────────────────────────────────────────────────────

    async def translate(
        self,
        text: str,
        source_language: str = "en",
        target_language: str = "hi",
    ) -> str:
        """
        Translate text between Indian languages using Sarvam IndicTrans2.
        Useful for translating UI strings or government documents.
        """
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
            return text  # Fallback to original text


# Module-level singleton — import this everywhere
sarvam = SarvamClient()
```

### 3.2 Create `routes/chat_endpoints.py` — NEW FILE

This replaces `core/chatbot.py` as the main chat entry point, now integrated
directly into `app.py` instead of running as a separate server.

```python
# routes/chat_endpoints.py
"""
Chat, STT, and TTS endpoints.
These replace the standalone core/chatbot.py server.
Wired into app.py via: app.include_router(chat_router)
"""

import os
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from langdetect import detect, LangDetectException

from core.database import get_db
from core.rag import RAGPipeline
from core.sarvam import sarvam

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/api/v1", tags=["Chat"])

# ─────────────────────────────────────────────────────────────────────────────
# System prompts per language
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "hi": (
        "आप एक विश्वसनीय भारतीय सरकारी सेवा सहायक हैं। "
        "आप UMANG, DigiLocker, और भारत सरकार की सेवाओं के बारे में "
        "सटीक, चरण-दर-चरण जानकारी देते हैं। "
        "हमेशा उसी भाषा में जवाब दें जिसमें प्रश्न पूछा गया हो। "
        "अनिश्चित होने पर आधिकारिक पोर्टल पर जाने की सलाह दें।"
    ),
    "ta": (
        "நீங்கள் ஒரு நம்பகமான இந்திய அரசாங்க சேவை உதவியாளர். "
        "UMANG, DigiLocker மற்றும் அரசாங்க சேவைகள் பற்றி "
        "துல்லியமான தகவல்களை வழங்குகிறீர்கள்."
    ),
    "te": (
        "మీరు ఒక నమ్మకమైన భారతీయ ప్రభుత్వ సేవా సహాయకుడు. "
        "UMANG, DigiLocker మరియు ప్రభుత్వ సేవల గురించి "
        "ఖచ్చితమైన సమాచారం అందిస్తారు."
    ),
    "bn": (
        "আপনি একজন বিশ্বস্ত ভারতীয় সরকারি সেবা সহায়তাকারী। "
        "UMANG, DigiLocker এবং সরকারি সেবা সম্পর্কে সঠিক তথ্য দিন।"
    ),
    "en": (
        "You are a reliable Indian Government Services Assistant. "
        "Help citizens access UMANG, DigiLocker, Passport, Aadhaar, PAN, "
        "EPFO, and all Government of India services accurately. "
        "Always respond in the same language as the user's question. "
        "Provide step-by-step guidance. When unsure, direct to official portals only."
    ),
}

DEFAULT_SYSTEM_PROMPT = SYSTEM_PROMPTS["en"]


def detect_language(text: str) -> str:
    """Detect language code from text. Falls back to 'hi' for short texts."""
    try:
        detected = detect(text)
        # langdetect uses ISO 639-1 codes which match our LANG_CODES keys
        return detected if detected in SYSTEM_PROMPTS else "hi"
    except LangDetectException:
        return "hi"


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str           # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "auto"    # "auto" = detect from message
    history: Optional[list[ChatMessage]] = []
    service_context: Optional[str] = None  # "passport", "aadhaar", etc.
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    language: str
    sources: list[str] = []
    session_id: Optional[str] = None


class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "hi"
    speed: Optional[float] = 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@chat_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint. Runs RAG → Sarvam-M pipeline.

    Flow:
      1. Detect language
      2. Retrieve relevant context from pgvector (RAG)
      3. Build prompt with context + conversation history
      4. Call Sarvam-M for generation
      5. Return response with source citations
    """
    query = request.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # 1. Detect language
    lang = request.language
    if lang == "auto" or not lang:
        lang = detect_language(query)

    # 2. RAG — retrieve relevant context chunks from your pgvector DB
    rag = RAGPipeline(db=db)
    context_results = rag.retrieve_context(query, top_k=5)

    # Build context string from retrieved chunks
    context_parts = []
    sources = []
    for chunk in context_results:
        content = chunk.get("content", "").strip()
        source = chunk.get("source", "")
        if content:
            context_parts.append(content[:400])  # Limit each chunk
        if source and source not in sources:
            sources.append(source)

    context_text = "\n\n".join(context_parts) if context_parts else ""

    # 3. Build messages for Sarvam-M
    system_prompt = SYSTEM_PROMPTS.get(lang, DEFAULT_SYSTEM_PROMPT)

    # Add context to system prompt if we have it
    if context_text:
        system_prompt += (
            f"\n\nRelevant government information:\n{context_text}\n\n"
            "Use the above information to answer accurately. "
            "Cite the service name when relevant."
        )

    # Add service context if provided
    if request.service_context:
        system_prompt += f"\n\nThe user is asking about: {request.service_context}"

    # Build message history
    messages = []
    for msg in (request.history or [])[-6:]:  # Last 6 turns for context
        messages.append({"role": msg.role, "content": msg.content})

    # Add current message
    messages.append({"role": "user", "content": query})

    # 4. Call Sarvam-M
    response_text = await sarvam.chat(
        messages=messages,
        system_prompt=system_prompt,
        temperature=0.3,    # Low temp for factual government Q&A
        max_tokens=512,
    )

    return ChatResponse(
        response=response_text,
        language=lang,
        sources=sources,
        session_id=request.session_id,
    )


@chat_router.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form(default="auto"),
):
    """
    Transcribe audio to text using Sarvam STT.

    Accepts: webm, wav, mp3, ogg (from browser MediaRecorder)
    Returns: { transcript, language_code, confidence }
    """
    if not sarvam.is_available():
        raise HTTPException(status_code=503, detail="Sarvam API not configured")

    # Read uploaded audio bytes
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # Determine audio format from content type or filename
    content_type = audio.content_type or ""
    if "webm" in content_type:
        fmt = "webm"
    elif "wav" in content_type:
        fmt = "wav"
    elif "mp3" in content_type or "mpeg" in content_type:
        fmt = "mp3"
    else:
        fmt = "webm"  # Browser MediaRecorder default

    # Handle auto language
    lang = language if language != "auto" else "hi"

    result = await sarvam.speech_to_text(
        audio_bytes=audio_bytes,
        language=lang,
        audio_format=fmt,
    )

    if "error" in result and not result.get("transcript"):
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@chat_router.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Sarvam TTS.

    Returns: WAV audio file as binary response
    The frontend can play this directly:
      const audio = new Audio(URL.createObjectURL(new Blob([response])))
      audio.play()
    """
    if not sarvam.is_available():
        raise HTTPException(status_code=503, detail="Sarvam API not configured")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = await sarvam.text_to_speech(
        text=request.text,
        language=request.language or "hi",
        speed=request.speed or 1.0,
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Return raw WAV bytes — frontend plays directly
    return Response(
        content=result["audio_bytes"],
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=response.wav"},
    )


@chat_router.get("/chat/health")
async def chat_health():
    """Check if Sarvam API is configured and reachable."""
    return {
        "sarvam_configured": sarvam.is_available(),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small"),
        "generative_enabled": os.getenv("GENERATIVE_ENABLED", "false"),
    }
```

### 3.3 Update `app.py` — add the chat router

Add these two lines to your existing `app.py`:

```python
# app.py — add these imports at the top with your existing imports
from routes.chat_endpoints import chat_router

# app.py — add this line after your existing app.include_router() calls
app.include_router(chat_router)
```

Your `app.py` router section should now look like:

```python
app.include_router(api_router)
app.include_router(v1_router)
app.include_router(auth_router)
app.include_router(chat_router)   # ← ADD THIS LINE
```

### 3.4 Update `requirements.txt` — add new dependencies

```txt
# Add these lines to your existing requirements.txt
httpx>=0.27.0
langdetect>=1.0.9
```

---

## STEP 4 — Deploy to Fly.io

### 4.1 Verify your Dockerfile works locally first

```bash
# Test locally before deploying
uvicorn app:app --reload --port 8000

# Hit the new endpoint to verify
curl http://localhost:8000/api/v1/chat/health
# Expected: {"sarvam_configured": true, "embedding_model": "intfloat/multilingual-e5-small", ...}
```

### 4.2 Launch on Fly.io

```bash
# From your project root (where app.py lives)
flyctl launch

# Fly will ask you:
# App name: seva-sindhu-api (or whatever you want)
# Region: sin (Singapore — closest to India) or bom (Mumbai if available)
# Would you like to set up a Postgresql database? → NO (using Supabase)
# Would you like to deploy now? → NO (set env vars first)
```

This creates a `fly.toml` file. Open it and make sure it looks like:

```toml
# fly.toml
app = "seva-sindhu-api"
primary_region = "sin"

[build]
  # Uses your existing Dockerfile

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false    # IMPORTANT: never sleep
  auto_start_machines = true
  min_machines_running = 1      # Always keep 1 alive

[env]
  PORT = "8000"

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

### 4.3 Set environment variables on Fly.io

```bash
# Set your secrets (never go into fly.toml or git)
flyctl secrets set SARVAM_API_KEY="your_sarvam_key_here"
flyctl secrets set HF_TOKEN="hf_your_token_here"
flyctl secrets set DATABASE_URL="postgresql://postgres:PASSWORD@db.REF.supabase.co:5432/postgres"
flyctl secrets set EMBEDDING_MODEL="intfloat/multilingual-e5-small"
flyctl secrets set EMBEDDING_ENABLED="true"
flyctl secrets set GENERATIVE_ENABLED="true"
flyctl secrets set LLM_PROVIDER="SARVAM"

# Verify they're set
flyctl secrets list
```

### 4.4 Deploy

```bash
flyctl deploy

# Watch the logs
flyctl logs

# Get your live URL
flyctl status
# Your API is now live at: https://seva-sindhu-api.fly.dev
```

### 4.5 Test your live API

```bash
# Health check
curl https://seva-sindhu-api.fly.dev/health

# Chat test
curl -X POST https://seva-sindhu-api.fly.dev/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "पासपोर्ट के लिए आवेदन कैसे करें?", "language": "hi"}'

# Expected response in Hindi with step-by-step passport guidance
```

---

## STEP 5 — Connect Frontend to Backend

### 5.1 Add env var to Vercel

Go to Vercel Dashboard → Your Project → Settings → Environment Variables:

```
Name:   VITE_API_URL
Value:  https://seva-sindhu-api.fly.dev
Environment: Production, Preview, Development
```

### 5.2 Create `frontend/src/lib/api.ts` — NEW FILE

Centralized API client for the frontend. Import this everywhere instead of
writing fetch() calls directly in components.

```typescript
// frontend/src/lib/api.ts

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  response: string;
  language: string;
  sources: string[];
  session_id?: string;
}

export interface STTResponse {
  transcript: string;
  language_code: string;
  confidence: number;
  error?: string;
}

// ── Text Chat ──────────────────────────────────────────────────────────────

export async function sendChatMessage(
  message: string,
  history: ChatMessage[] = [],
  language: string = "auto",
  serviceContext?: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      language,
      history,
      service_context: serviceContext,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Chat API error: ${response.status} — ${error}`);
  }

  return response.json();
}

// ── Speech to Text ─────────────────────────────────────────────────────────

export async function speechToText(
  audioBlob: Blob,
  language: string = "auto"
): Promise<STTResponse> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  formData.append("language", language);

  const response = await fetch(`${API_URL}/api/v1/speech-to-text`, {
    method: "POST",
    body: formData,
    // Do NOT set Content-Type — browser sets it automatically with boundary
  });

  if (!response.ok) {
    throw new Error(`STT API error: ${response.status}`);
  }

  return response.json();
}

// ── Text to Speech ─────────────────────────────────────────────────────────

export async function textToSpeech(
  text: string,
  language: string = "hi",
  speed: number = 1.0
): Promise<Blob> {
  const response = await fetch(`${API_URL}/api/v1/text-to-speech`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language, speed }),
  });

  if (!response.ok) {
    throw new Error(`TTS API error: ${response.status}`);
  }

  // Returns raw WAV audio blob
  return response.blob();
}

// ── Utility ────────────────────────────────────────────────────────────────

export function playAudioBlob(blob: Blob): HTMLAudioElement {
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.play();
  audio.onended = () => URL.revokeObjectURL(url); // Clean up memory
  return audio;
}
```

### 5.3 Replace `frontend/src/components/Chatbot.tsx`

This is the complete updated chatbot component with real API, mic button (STT),
and speaker button (TTS) wired in. Drop this file in as a full replacement:

```tsx
// frontend/src/components/Chatbot.tsx
import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  MessageCircle, X, Send, Loader2, AlertCircle,
  CheckCircle2, WifiOff, Mic, MicOff, Volume2, VolumeX,
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "./ui/utils";
import { toast } from "sonner";
import {
  sendChatMessage,
  speechToText,
  textToSpeech,
  playAudioBlob,
  ChatMessage as APIChatMessage,
} from "../lib/api";

// ── Types ──────────────────────────────────────────────────────────────────

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  status?: "sending" | "sent" | "error";
  language?: string;
}

// ── Language options shown in the dropdown ─────────────────────────────────

const LANGUAGES = [
  { code: "auto", label: "Auto Detect" },
  { code: "hi",   label: "हिन्दी" },
  { code: "en",   label: "English" },
  { code: "ta",   label: "தமிழ்" },
  { code: "te",   label: "తెలుగు" },
  { code: "bn",   label: "বাংলা" },
  { code: "mr",   label: "मराठी" },
  { code: "gu",   label: "ગુજરાતી" },
  { code: "kn",   label: "ಕನ್ನಡ" },
  { code: "ml",   label: "മലയാളം" },
  { code: "pa",   label: "ਪੰਜਾਬੀ" },
];

const SUGGESTED_QUERIES = [
  "How to apply for passport?",
  "Aadhaar update process",
  "EPFO claim status",
  "PAN card correction",
  "Track application",
];

// ── Component ──────────────────────────────────────────────────────────────

export function Chatbot() {
  const [isOpen, setIsOpen]         = useState(false);
  const [isOnline, setIsOnline]     = useState(navigator.onLine);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping]     = useState(false);
  const [language, setLanguage]     = useState("auto");
  const [isRecording, setIsRecording]   = useState(false);
  const [isSpeaking, setIsSpeaking]     = useState(false);
  const [ttsEnabled, setTtsEnabled]     = useState(false);
  const [messages, setMessages]         = useState<Message[]>([
    {
      id: "1",
      text: "Hello! Welcome to Government Citizen Services. How can I assist you today? आप हिन्दी में भी पूछ सकते हैं।",
      sender: "bot",
      timestamp: new Date(),
      status: "sent",
    },
  ]);

  const scrollAreaRef     = useRef<HTMLDivElement>(null);
  const inputRef          = useRef<HTMLInputElement>(null);
  const mediaRecorderRef  = useRef<MediaRecorder | null>(null);
  const audioChunksRef    = useRef<Blob[]>([]);
  const currentAudioRef   = useRef<HTMLAudioElement | null>(null);

  // Build message history for the API (last 6 turns)
  const getHistory = useCallback((): APIChatMessage[] => {
    return messages
      .filter((m) => m.status !== "error")
      .slice(-12)
      .map((m) => ({
        role: m.sender === "user" ? "user" : "assistant",
        content: m.text,
      }));
  }, [messages]);

  // ── Online/offline detection ─────────────────────────────────────────────

  useEffect(() => {
    const onOnline  = () => { setIsOnline(true);  toast.success("Connection restored"); };
    const onOffline = () => { setIsOnline(false); toast.error("Connection lost"); };
    window.addEventListener("online",  onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online",  onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  // ── Auto-scroll to latest message ────────────────────────────────────────

  useEffect(() => {
    if (scrollAreaRef.current) {
      const el = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]");
      if (el) el.scrollTop = el.scrollHeight;
    }
  }, [messages, isTyping]);

  // ── Focus input when chat opens ──────────────────────────────────────────

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 100);
  }, [isOpen]);

  // ── Add a message to state ───────────────────────────────────────────────

  const addMessage = useCallback(
    (text: string, sender: "user" | "bot", extra: Partial<Message> = {}) => {
      const msg: Message = {
        id: Date.now().toString() + Math.random(),
        text,
        sender,
        timestamp: new Date(),
        status: "sent",
        ...extra,
      };
      setMessages((prev) => [...prev, msg]);
      return msg.id;
    },
    []
  );

  // ── Update a message's status ────────────────────────────────────────────

  const updateMessageStatus = useCallback(
    (id: string, status: Message["status"], text?: string) => {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === id ? { ...m, status, ...(text ? { text } : {}) } : m
        )
      );
    },
    []
  );

  // ── TEXT CHAT ────────────────────────────────────────────────────────────

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || !isOnline) return;

      const msgId = addMessage(text, "user", { status: "sending" });
      setInputValue("");
      setIsTyping(true);

      try {
        const result = await sendChatMessage(
          text,
          getHistory(),
          language,
        );

        updateMessageStatus(msgId, "sent");
        const botId = addMessage(result.response, "bot", {
          language: result.language,
        });

        // Auto-speak response if TTS is enabled
        if (ttsEnabled && result.response) {
          const responseLang = result.language || language || "hi";
          if (responseLang !== "auto") {
            speakText(result.response, responseLang);
          }
        }
      } catch (err) {
        updateMessageStatus(msgId, "error");
        addMessage(
          "Sorry, I couldn't connect to the service. Please try again.",
          "bot"
        );
        toast.error("Failed to get response");
      } finally {
        setIsTyping(false);
      }
    },
    [isOnline, language, ttsEnabled, addMessage, updateMessageStatus, getHistory]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handleSuggestedQuery = (query: string) => {
    sendMessage(query);
  };

  // ── SPEECH TO TEXT (Mic button) ──────────────────────────────────────────

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

        // Show "transcribing..." indicator
        setIsTyping(true);
        try {
          const result = await speechToText(audioBlob, language);
          if (result.transcript) {
            setInputValue(result.transcript);
            inputRef.current?.focus();
            toast.success(`Detected: ${result.language_code || language}`);
          } else {
            toast.error("Could not transcribe audio. Please try again.");
          }
        } catch (err) {
          toast.error("Speech recognition failed");
        } finally {
          setIsTyping(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      toast.info("Recording... tap mic again to stop");
    } catch (err) {
      toast.error("Microphone access denied. Please allow mic permissions.");
    }
  }, [language]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const toggleRecording = () => {
    if (isRecording) stopRecording();
    else startRecording();
  };

  // ── TEXT TO SPEECH (Speaker button per message) ──────────────────────────

  const speakText = useCallback(
    async (text: string, lang: string = "hi") => {
      // Stop any currently playing audio
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
        setIsSpeaking(false);
      }

      setIsSpeaking(true);
      try {
        const audioBlob = await textToSpeech(text, lang);
        const audio = playAudioBlob(audioBlob);
        currentAudioRef.current = audio;
        audio.onended = () => {
          setIsSpeaking(false);
          currentAudioRef.current = null;
        };
      } catch (err) {
        toast.error("Text-to-speech failed");
        setIsSpeaking(false);
      }
    },
    []
  );

  const stopSpeaking = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
      setIsSpeaking(false);
    }
  };

  // ── RENDER ───────────────────────────────────────────────────────────────

  return (
    <>
      {/* Floating Bubble */}
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
              className="w-14 h-14 rounded-full bg-[var(--primary)] hover:bg-[var(--primary-hover)] shadow-lg"
              aria-label="Open chat"
            >
              <MessageCircle className="w-6 h-6 text-white" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed bottom-6 right-6 w-full max-w-md z-50"
            role="dialog"
            aria-labelledby="chat-title"
            aria-modal="true"
          >
            <div className="glass-effect rounded-[var(--radius-2xl)] shadow-[var(--shadow-24)] overflow-hidden border-2 border-[var(--card-border)]">

              {/* Header */}
              <div className="bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)] px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 glass-effect rounded-full flex items-center justify-center">
                    <MessageCircle className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div id="chat-title" className="text-white font-semibold text-sm">
                      GovBot Assistant
                    </div>
                    <div className="flex items-center gap-1">
                      <span className={cn(
                        "w-2 h-2 rounded-full",
                        isOnline ? "bg-green-400" : "bg-red-400"
                      )} />
                      <span className="text-white/70 text-xs">
                        {isOnline ? "Online" : "Offline"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {/* Language selector */}
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="text-xs bg-white/20 text-white border-0 rounded px-2 py-1 cursor-pointer"
                    aria-label="Select language"
                  >
                    {LANGUAGES.map((l) => (
                      <option key={l.code} value={l.code} className="text-black">
                        {l.label}
                      </option>
                    ))}
                  </select>

                  {/* TTS toggle */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-white hover:bg-white/20 w-8 h-8"
                    onClick={() => setTtsEnabled((v) => !v)}
                    title={ttsEnabled ? "Disable auto-speak" : "Enable auto-speak"}
                  >
                    {ttsEnabled
                      ? <Volume2 className="w-4 h-4" />
                      : <VolumeX className="w-4 h-4 opacity-50" />
                    }
                  </Button>

                  {/* Close */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-white hover:bg-white/20 w-8 h-8"
                    onClick={() => setIsOpen(false)}
                    aria-label="Close chat"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Messages */}
              <ScrollArea ref={scrollAreaRef} className="h-80 p-4 bg-[var(--background)]">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        "flex gap-2",
                        message.sender === "user" ? "justify-end" : "justify-start"
                      )}
                    >
                      {message.sender === "bot" && (
                        <div className="w-7 h-7 rounded-full bg-[var(--primary)] flex items-center justify-center flex-shrink-0 mt-1">
                          <MessageCircle className="w-3.5 h-3.5 text-white" />
                        </div>
                      )}
                      <div
                        className={cn(
                          "max-w-[78%] rounded-2xl px-4 py-2.5 text-sm",
                          message.sender === "user"
                            ? "bg-[var(--primary)] text-white rounded-br-sm"
                            : "bg-[var(--card)] text-[var(--foreground)] rounded-bl-sm border border-[var(--border)]"
                        )}
                      >
                        <p className="leading-relaxed whitespace-pre-wrap">
                          {message.text}
                        </p>
                        <div className="flex items-center justify-between mt-1 gap-2">
                          <time className={cn(
                            "text-xs",
                            message.sender === "user"
                              ? "text-white/60"
                              : "text-[var(--muted-foreground)]"
                          )}>
                            {message.timestamp.toLocaleTimeString([], {
                              hour: "2-digit", minute: "2-digit"
                            })}
                          </time>

                          {/* Speak this message button */}
                          {message.sender === "bot" && (
                            <button
                              onClick={() => speakText(
                                message.text,
                                message.language || language || "hi"
                              )}
                              className="text-[var(--muted-foreground)] hover:text-[var(--primary)] transition-colors"
                              title="Listen to this response"
                            >
                              <Volume2 className="w-3 h-3" />
                            </button>
                          )}

                          {message.sender === "user" && message.status === "sending" && (
                            <Loader2 className="w-3 h-3 animate-spin text-white/60" />
                          )}
                          {message.sender === "user" && message.status === "sent" && (
                            <CheckCircle2 className="w-3 h-3 text-white/60" />
                          )}
                          {message.sender === "user" && message.status === "error" && (
                            <AlertCircle className="w-3 h-3 text-red-300" />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Typing indicator */}
                  {isTyping && (
                    <div className="flex gap-2 justify-start">
                      <div className="w-7 h-7 rounded-full bg-[var(--primary)] flex items-center justify-center flex-shrink-0">
                        <MessageCircle className="w-3.5 h-3.5 text-white" />
                      </div>
                      <div className="bg-[var(--card)] rounded-2xl rounded-bl-sm border border-[var(--border)] px-4 py-3">
                        <div className="flex gap-1 items-center">
                          {[0, 1, 2].map((i) => (
                            <span
                              key={i}
                              className="w-1.5 h-1.5 bg-[var(--muted-foreground)] rounded-full animate-bounce"
                              style={{ animationDelay: `${i * 0.15}s` }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              {/* Suggested queries (shown only at start) */}
              {messages.length === 1 && (
                <div className="px-4 py-2 bg-[var(--card)] border-t border-[var(--border)]">
                  <p className="text-xs text-[var(--muted-foreground)] mb-2">
                    Quick questions:
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {SUGGESTED_QUERIES.slice(0, 3).map((q, i) => (
                      <button
                        key={i}
                        onClick={() => handleSuggestedQuery(q)}
                        className="text-xs px-2.5 py-1 bg-[var(--muted)] hover:bg-[var(--muted)]/70 text-[var(--foreground)] rounded-full transition-colors"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Offline warning */}
              {!isOnline && (
                <div className="px-4 py-2 bg-red-50 border-t border-red-200 flex items-center gap-2 text-xs text-red-600">
                  <WifiOff className="w-3 h-3" />
                  You are offline. Messages will send when connection restores.
                </div>
              )}

              {/* Input area */}
              <div className="p-3 bg-[var(--card)] border-t border-[var(--border)]">
                <form onSubmit={handleSubmit} className="flex gap-2">

                  {/* Mic button */}
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className={cn(
                      "flex-shrink-0 w-10 h-10 transition-colors",
                      isRecording
                        ? "text-red-500 bg-red-50 hover:bg-red-100 animate-pulse"
                        : "text-[var(--muted-foreground)] hover:text-[var(--primary)]"
                    )}
                    onClick={toggleRecording}
                    disabled={!isOnline}
                    aria-label={isRecording ? "Stop recording" : "Start voice input"}
                    title={isRecording ? "Tap to stop recording" : "Tap to speak"}
                  >
                    {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </Button>

                  <Input
                    ref={inputRef}
                    type="text"
                    placeholder={
                      isRecording
                        ? "Listening..."
                        : isOnline
                        ? "Type your message..."
                        : "Waiting for connection..."
                    }
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    className="flex-1 h-10 text-sm"
                    disabled={!isOnline || isRecording}
                    aria-label="Chat message input"
                  />

                  <Button
                    type="submit"
                    size="icon"
                    className="bg-[var(--primary)] hover:bg-[var(--primary-hover)] flex-shrink-0 w-10 h-10"
                    disabled={!inputValue.trim() || !isOnline}
                    aria-label="Send message"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </form>

                {/* Stop speaking button */}
                {isSpeaking && (
                  <button
                    onClick={stopSpeaking}
                    className="mt-2 text-xs text-[var(--muted-foreground)] hover:text-red-500 flex items-center gap-1 transition-colors"
                  >
                    <VolumeX className="w-3 h-3" />
                    Stop speaking
                  </button>
                )}

                <p className="text-xs text-[var(--muted-foreground)] mt-1.5 text-center">
                  Powered by Sarvam AI · 22 Indian Languages · Secure
                </p>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
```

### 5.4 Redeploy Vercel

```bash
# From your frontend directory
git add .
git commit -m "feat: wire chatbot to FastAPI + Sarvam AI (STT + TTS)"
git push

# Vercel auto-deploys on push
# Check: https://vercel.com/dashboard → your project → Deployments
```

---

## STEP 6 — Multilingual UI (react-i18next)

### 6.1 Install dependencies

```bash
cd frontend
npm install react-i18next i18next i18next-browser-languagedetector i18next-http-backend
```

### 6.2 Create `frontend/src/i18n/index.ts` — NEW FILE

```typescript
// frontend/src/i18n/index.ts
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// Import translation files directly (better for Vite bundling)
import enCommon from "./locales/en/common.json";
import hiCommon from "./locales/hi/common.json";
import taCommon from "./locales/ta/common.json";
import teCommon from "./locales/te/common.json";
import bnCommon from "./locales/bn/common.json";
import mrCommon from "./locales/mr/common.json";

// Font families per script — loaded via Google Fonts in index.html
export const SCRIPT_FONTS: Record<string, string> = {
  en: "'Plus Jakarta Sans', sans-serif",
  hi: "'Noto Sans Devanagari', sans-serif",
  mr: "'Noto Sans Devanagari', sans-serif",
  ta: "'Noto Sans Tamil', sans-serif",
  te: "'Noto Sans Telugu', sans-serif",
  bn: "'Noto Sans Bengali', sans-serif",
  gu: "'Noto Sans Gujarati', sans-serif",
  kn: "'Noto Sans Kannada', sans-serif",
  ml: "'Noto Sans Malayalam', sans-serif",
  pa: "'Noto Sans Gurmukhi', sans-serif",
  ur: "'Noto Nastaliq Urdu', serif",
};

// RTL languages
export const RTL_LANGUAGES = ["ur", "ar"];

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { common: enCommon },
      hi: { common: hiCommon },
      ta: { common: taCommon },
      te: { common: teCommon },
      bn: { common: bnCommon },
      mr: { common: mrCommon },
    },
    fallbackLng: "en",
    defaultNS: "common",
    interpolation: {
      escapeValue: false, // React already escapes
    },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
    },
  });

// Apply font + direction whenever language changes
i18n.on("languageChanged", (lng) => {
  const font = SCRIPT_FONTS[lng] || SCRIPT_FONTS["en"];
  document.documentElement.style.setProperty("--font-sans", font);
  document.documentElement.setAttribute(
    "dir",
    RTL_LANGUAGES.includes(lng) ? "rtl" : "ltr"
  );
  document.documentElement.setAttribute("lang", lng);
});

export default i18n;
```

### 6.3 Create translation files

**`frontend/src/i18n/locales/en/common.json`**

```json
{
  "nav": {
    "home": "Home",
    "services": "Services",
    "faq": "FAQ",
    "dashboard": "Dashboard",
    "admin": "Admin",
    "track": "Track Application"
  },
  "home": {
    "hero_title": "Your Gateway to Government Services",
    "hero_subtitle": "Access 1200+ government services instantly with AI assistance",
    "get_started": "Get Started",
    "learn_more": "Learn More",
    "chatbot_title": "Meet Your Personal AI Assistant",
    "chatbot_subtitle": "Get instant help in your language, 24/7"
  },
  "chatbot": {
    "title": "GovBot Assistant",
    "online": "Online",
    "offline": "Offline",
    "placeholder": "Type your message...",
    "powered_by": "Powered by Sarvam AI · 22 Indian Languages",
    "suggested": "Quick questions:"
  },
  "services": {
    "title": "Government Services",
    "search_placeholder": "Search services...",
    "apply_now": "Apply Now",
    "learn_more": "Learn More",
    "documents_required": "Documents Required",
    "processing_time": "Processing Time",
    "fee": "Fee"
  },
  "common": {
    "loading": "Loading...",
    "error": "Something went wrong",
    "retry": "Try again",
    "back": "Back",
    "next": "Next",
    "submit": "Submit",
    "cancel": "Cancel",
    "save": "Save",
    "close": "Close"
  }
}
```

**`frontend/src/i18n/locales/hi/common.json`**

```json
{
  "nav": {
    "home": "होम",
    "services": "सेवाएं",
    "faq": "अक्सर पूछे जाने वाले प्रश्न",
    "dashboard": "डैशबोर्ड",
    "admin": "प्रशासन",
    "track": "आवेदन ट्रैक करें"
  },
  "home": {
    "hero_title": "सरकारी सेवाओं का आपका प्रवेश द्वार",
    "hero_subtitle": "AI सहायता के साथ 1200+ सरकारी सेवाओं तक तुरंत पहुंचें",
    "get_started": "शुरू करें",
    "learn_more": "और जानें",
    "chatbot_title": "अपने AI सहायक से मिलें",
    "chatbot_subtitle": "अपनी भाषा में 24/7 तत्काल सहायता पाएं"
  },
  "chatbot": {
    "title": "GovBot सहायक",
    "online": "ऑनलाइन",
    "offline": "ऑफलाइन",
    "placeholder": "अपना संदेश टाइप करें...",
    "powered_by": "Sarvam AI द्वारा संचालित · 22 भारतीय भाषाएं",
    "suggested": "त्वरित प्रश्न:"
  },
  "services": {
    "title": "सरकारी सेवाएं",
    "search_placeholder": "सेवाएं खोजें...",
    "apply_now": "अभी आवेदन करें",
    "learn_more": "और जानें",
    "documents_required": "आवश्यक दस्तावेज़",
    "processing_time": "प्रक्रिया समय",
    "fee": "शुल्क"
  },
  "common": {
    "loading": "लोड हो रहा है...",
    "error": "कुछ गलत हुआ",
    "retry": "पुनः प्रयास करें",
    "back": "वापस",
    "next": "अगला",
    "submit": "जमा करें",
    "cancel": "रद्द करें",
    "save": "सहेजें",
    "close": "बंद करें"
  }
}
```

*Create similar files for `ta`, `te`, `bn`, `mr` with the same keys translated.*

### 6.4 Create `frontend/src/components/LanguageSwitcher.tsx` — NEW FILE

```tsx
// frontend/src/components/LanguageSwitcher.tsx
import React from "react";
import { useTranslation } from "react-i18next";
import { Globe } from "lucide-react";

const LANGUAGES = [
  { code: "en", label: "English",    native: "English"    },
  { code: "hi", label: "Hindi",      native: "हिन्दी"     },
  { code: "ta", label: "Tamil",      native: "தமிழ்"     },
  { code: "te", label: "Telugu",     native: "తెలుగు"    },
  { code: "bn", label: "Bengali",    native: "বাংলা"     },
  { code: "mr", label: "Marathi",    native: "मराठी"     },
  { code: "gu", label: "Gujarati",   native: "ગુજરાતી"   },
  { code: "kn", label: "Kannada",    native: "ಕನ್ನಡ"     },
  { code: "ml", label: "Malayalam",  native: "മലയാളം"   },
  { code: "pa", label: "Punjabi",    native: "ਪੰਜਾਬੀ"    },
];

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    i18n.changeLanguage(e.target.value);
  };

  const currentLang = LANGUAGES.find((l) => l.code === i18n.language)
    || LANGUAGES[0];

  return (
    <div className="flex items-center gap-1.5 text-sm">
      <Globe className="w-4 h-4 text-[var(--muted-foreground)]" />
      <select
        value={i18n.language}
        onChange={handleChange}
        className="bg-transparent border-0 text-[var(--foreground)] cursor-pointer 
                   focus:outline-none focus:ring-0 py-0 text-sm"
        aria-label="Select language"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.native}
          </option>
        ))}
      </select>
    </div>
  );
}
```

### 6.5 Add Google Fonts for Indian scripts

In `frontend/index.html`, add inside `<head>`:

```html
<!-- Indian script fonts — loaded on demand by i18n module -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Noto+Sans+Tamil:wght@400;500;600;700&family=Noto+Sans+Telugu:wght@400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&family=Noto+Sans+Gujarati:wght@400;500;600;700&family=Noto+Sans+Kannada:wght@400;500;600;700&family=Noto+Sans+Malayalam:wght@400;500;600;700&family=Noto+Sans+Gurmukhi:wght@400;500;600;700&family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet" />
```

### 6.6 Wire it all up in `frontend/src/main.tsx`

```tsx
// frontend/src/main.tsx — add this import at the top
import "./i18n";  // Must be imported before App
```

### 6.7 Add LanguageSwitcher to your navbar

In your existing navbar component, add:

```tsx
import { LanguageSwitcher } from "./LanguageSwitcher";

// Inside your navbar JSX, wherever the right side controls are:
<LanguageSwitcher />
```

### 6.8 Use translations in any component

```tsx
// Example: in EnhancedHome.tsx
import { useTranslation } from "react-i18next";

function EnhancedHome() {
  const { t } = useTranslation("common");

  return (
    <h1>{t("home.hero_title")}</h1>  // Automatically in selected language
  );
}
```

---

## Final Checklist

```
Backend
  ☐ Supabase project created, pgvector enabled
  ☐ Local DB exported and imported to Supabase
  ☐ .env updated with all keys
  ☐ core/embeddings.py updated to multilingual-e5-small
  ☐ core/sarvam.py created
  ☐ routes/chat_endpoints.py created
  ☐ app.py updated to include chat_router
  ☐ requirements.txt updated (httpx, langdetect)
  ☐ backfill_embeddings.py re-run against Supabase
  ☐ Tested locally: curl localhost:8000/api/v1/chat/health

Fly.io Deployment
  ☐ flyctl installed (brew install flyctl)
  ☐ fly launch run (created fly.toml)
  ☐ fly.toml: auto_stop_machines = false
  ☐ All secrets set via flyctl secrets set
  ☐ flyctl deploy successful
  ☐ Live URL tested: https://your-app.fly.dev/api/v1/chat/health

Frontend
  ☐ VITE_API_URL set in Vercel env vars
  ☐ frontend/src/lib/api.ts created
  ☐ Chatbot.tsx replaced (STT + TTS wired)
  ☐ i18n/index.ts created
  ☐ Translation JSON files created (en + hi minimum)
  ☐ LanguageSwitcher.tsx created
  ☐ Google Fonts added to index.html
  ☐ i18n imported in main.tsx
  ☐ LanguageSwitcher added to navbar
  ☐ Vercel redeployed (git push)

Smoke Tests
  ☐ Chat works in English
  ☐ Chat works in Hindi (पासपोर्ट के बारे में बताएं)
  ☐ Mic button records and transcribes
  ☐ Speaker button plays bot response
  ☐ Language switcher changes UI to Hindi
  ☐ Font changes from Latin to Devanagari on switch
  ☐ No CORS errors in browser console
```

---

## Sarvam API Rate Limits (Free Tier)

```
LLM (sarvam-m):      ~100 requests/day on free tier
STT (saarika:v2):    ~100 requests/day
TTS:                 ~100 requests/day
Translation:         ~100 requests/day
```

For development and demo purposes this is more than enough.
For production, upgrade to Sarvam's paid tier (~₹499/month for 10K requests).

---

*Guide version 1.0 — covers Steps 1-6 for full Sarvam-M integration*
