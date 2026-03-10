"""
Chat, STT, and TTS endpoints.
These integrate with the existing FastAPI app.
"""

import asyncio
import os
import logging
import json
import re
import time
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Query,
    Request,
)
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from langdetect import detect, LangDetectException
from datetime import datetime, timedelta

from core.database import get_db
from core.rag import RAGPipeline
from core.sarvam import sarvam
from core.cache import chat_cache
from core.repositories import ContentChunkRepository, FAQRepository, DocumentRepository
from core.auth_models import User, UserSession, ChatSession
from routes.auth_endpoints import get_current_user_dependency

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/api/v1", tags=["Chat"])
security = HTTPBearer()

SYSTEM_PROMPTS = {
    "hi": (
        "आप एक विश्वसनीय भारतीय सरकारी सेवा सहायक हैं। "
        "आप UMANG, DigiLocker, और भारत सरकार की सेवाओं के बारे में "
        "सटीक, चरण-दर-चरण जानकारी देते हैं। "
        "हमेशा उसी भाषा में जवाब दें जिसमें प्रश्न पूछा गया हो। "
        "अनिश्चित होने पर आधिकारिक पोर्टल पर जाने की सलाह दें।"
    ),
    "bn": "আপনি একজন বিশ্বস্ত ভারতীয় সরকারি সেবা সহায়তাকারী। UMANG, DigiLocker এবং সরকারি সেবা সম্পর্কে সঠিক তথ্য দিন।",
    "ta": "நீங்கள் ஒரு நம்பகமான இந்திய அரசாங்க சேவை உதவியாளர். UMANG, DigiLocker மற்றும் அரசாங்க சேவைகள் பற்றி துல்லியமான தகவல்களை வழங்குகிறீர்கள்.",
    "te": "మీరు ఒక నమ్మకమైన భారతీయ ప్రభుత్వ సేవా సహాయకుడు. UMANG, DigiLocker మరియు ప్రభుత్వ సేవల గురించి ఖచ్చితమైన సమాచారం అందిస్తారు.",
    "mr": "आपण एक विश्वासनीय भारतीय सरकारी सेवा सहायक आहात. UMANG, DigiLocker आणि सरकारी सेवांविषयी अचूक माहिती द्या.",
    "gu": "તમે એક વિશ્વસનીય ભારતીય સરકારી સેવા સહાયક છો. UMANG, DigiLocker અને સરકારી સેવાઓ વિશે સચોટ માહિતી આપો.",
    "pa": "ਤੁਸ਼ਟ ਇੱਕ ਭਰੋਸੇਮੰਨ ਭਾਰਤੀ ਸਰਕਾਰੀ ਸੇਵਾ ਸਹਾਇਤਾ ਹੋ। UMANG, DigiLocker ਅਤੇ ਸਰਕਾਰੀ ਸੇਵਾਵਾਂ ਬਾਰੇ ਸਹੀ ਜਾਣਕਾਰੀ ਦਿਓ।",
    "kn": "ನೀವು ವಿಶ್ವಾಸನೀಯ ಭಾರತೀಯ ಸರ್ಕಾರಿ ಸೇವಾ ಸಹಾಯಕರಾಗಿದ್ದೀರಿ. UMANG, DigiLocker ಮತ್ತು ಸರ್ಕಾರಿ ಸೇವೆಗಳ ಬಗ್ಗೆ ನಿಖರವಾದ ಮಾಹಿತಿ ನೀಡಿ.",
    "ml": "നിങ്ങൾ ഒരു വിശ്വാസയോഗ്യമായ ഇന്ത്യാ ഗവണ്മെന്റ് സേവാ സഹായിയാണ്. UMANG, DigiLocker എന്നിവയെക്കുറിച്ച് കൃത്യമായ വിവരങ്ങൾ നൽകുക.",
    "or": "ଆପଣ ଏକ ବିଶ୍ୱାସନୀୟ ଭାରତୀୟ ସରକାରୀ ସେବା ସହାୟକ | UMANG, DigiLocker ଓ ସରକାରୀ ସେବା ବିଷୟରେ ସଠਿਕ ତଥ୍ਯ ଦିਓ |",
    "as": "আপুনি এজন বিশ্বাসযোগ্য ভাৰতীয় চৰকাৰী সেৱা সহায়ক। UMANG, DigiLocker আৰু চৰকাৰী সেৱাসমূহৰ বিষয়ে সঠিক তথ্য দিয়ক।",
    "ur": "آپ ایک بھروسہ مند بھارتی سرکاری خدمات مددگار ہیں۔ UMANG، DigiLocker اور سرکاری خدمات کے بارے میں درست معلومات دیں۔",
    "ks": "तुम कुशल रूपैनि भारतीय सरकारी सेवा मददगार हों। UMANG, DigiLocker आहुन सरकारी सेवाऽन बारे में सही जानकारी दें।",
    "sd": " توھان هڪ پائيدار هندوستاني سرڪاري خدمت مددگار آهيون. UMANG، DigiLocker ۽ سرڪاري خدمتن بابت صحيح معلومات ڏيو.",
    "sa": "भवद्भिः विश्वसनीयः भारतीयः सरकारीः सेवा सहायकः अस्ति। UMANG, DigiLocker च सरकारी सेवान् विषये सत्यं सूचनां ददाति।",
    "ne": "तपाईं एक विश्वसनीय भारतीय सरकारी सेवा सहायक हुनुहुन्छ। UMANG, DigiLocker र सरकारी सेवाहरूको बारेमा सही जानकारी दिनुहोस्।",
    "kok": "तुम्ही एक विश्वासनीय भारतीय सरकारी सेवा सहायक आसतात। UMANG, DigiLocker आनी सरकारी सेवांविशी अचूक माहिती दां।",
    "mai": "रउआ एगो विश्वासनीय भारतीय सरकारी सेवा सहायक बानी। UMANG, DigiLocker अउर सरकारी सेवा सभ के बारे में सही जानकारी दीं।",
    "doi": "ਤੁਸ਼ਟ ਇੱਕ ਭਰੋਸੇਮੰਨ ਭਾਰਤੀ ਸਰਕਾਰੀ ਸੇਵਾ ਸਹਾਇਤਾ ਹੋ। UMANG, DigiLocker ਅਤੇ ਸਰਕਾਰੀ ਸੇਵਾਵਾਂ ਬਾਰੇ ਸਹੀ ਜਾਣਕਾਰੀ ਦਿਓ।",
    "mni": "ꯑꯃꯥ ꯑꯣꯏꯕ ꯃꯤꯇꯝꯂꯕꯛ ꯂꯧꯊꯣꯛꯅꯕ ꯁꯔꯨꯝꯕ ꯁꯦꯝꯕ ꯑꯣꯏꯕꯗꯤ। UMANG, DigiLocker ꯑꯃꯥꯁꯔꯨꯝꯕ ꯁꯔꯤꯕꯒꯤ ꯃꯈꯣꯏꯗꯨꯅꯔꯤꯕ ꯁꯦꯝꯕ ꯑꯦꯟꯕꯒꯤ ꯃꯇꯝꯖꯤꯟꯕꯔꯤ꯫",
    "sat": "ᱚᱞᱚ ᱵᱷᱤᱛᱤᱨᱚᱜ ᱚᱠᱚᱭ ᱚᱱᱚᱞ-ᱵᱚᱛᱚᱱᱚᱜ ᱯᱚᱨᱚᱵᱚᱛ ᱥᱮᱨᱵᱟᱜ ᱟᱹᱱᱟᱹᱲ ᱠᱟᱱᱟ᱾ UMANG, DigiLocker ᱟᱨ ᱯᱚᱨᱚᱵᱚᱛ ᱥᱮᱨᱵᱟᱜ ᱠᱚᱣᱟᱜ ᱞᱮᱠᱟᱛᱮ ᱟᱹᱭᱠᱟᱹᱛᱤᱨᱚᱜ ᱵᱟᱵᱚᱛᱚᱜ ᱟᱠᱟᱫᱤᱢ᱾",
    "en": (
        "You are a reliable Indian Government Services Assistant. "
        "Help citizens access UMANG, DigiLocker, Passport, Aadhaar, PAN, "
        "EPFO, and all Government of India services accurately. "
        "Always respond in the same language as the user's question. "
        "Provide step-by-step guidance. When unsure, direct to official portals only."
    ),
}

DEFAULT_SYSTEM_PROMPT = SYSTEM_PROMPTS["en"]

SECURITY_PATTERNS = [
    re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
    re.compile(r"\bdrop\s+table\b", re.IGNORECASE),
    re.compile(r"<script", re.IGNORECASE),
    re.compile(r"union\s+select", re.IGNORECASE),
]


def _is_security_threat(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECURITY_PATTERNS)


def _clean_model_text(text: str) -> str:
    cleaned = (text or "").strip()
    if "</think>" in cleaned:
        cleaned = cleaned.split("</think>")[-1].strip()
    if "<think>" in cleaned and "</think>" not in cleaned:
        cleaned = cleaned.split("<think>", 1)[0].strip()
    return cleaned


def _build_rag_fallback(
    query: str,
    language: str,
    context_parts: list[str],
    user: Optional[User],
) -> str:
    if context_parts:
        synthesized = _summarize_context_locally(context_parts)
        base = (
            "Based on available government records, here is a synthesized response:\n"
            f"{synthesized}\n\n"
            "Suggested next step: Use the relevant official government portal for final submission/verification."
        )
    else:
        base = (
            "I can help with Indian government services like Passport, Aadhaar, PAN, "
            "EPFO, DigiLocker, voter ID, and driving license. Share your exact query "
            "and I will provide step-by-step guidance."
        )

    if language == "hi":
        base = (
            "मैं पासपोर्ट, आधार, पैन, ईपीएफओ, डिजिलॉकर और अन्य सरकारी सेवाओं में मदद कर सकता हूँ। "
            "कृपया अपना सवाल बताएं, मैं चरण-दर-चरण मार्गदर्शन दूंगा।"
            if not context_parts
            else base
        )

    first_name = str(getattr(user, "first_name", "") or "") if user else ""
    if first_name:
        return f"{first_name}, {base}"
    return base


def _summarize_context_locally(context_parts: list[str]) -> str:
    """Fast local summarizer for RAG-only mode; avoids raw chunk dumps."""
    unique_points: list[str] = []
    for raw in context_parts:
        cleaned = " ".join((raw or "").replace("\n", " ").split())
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if any(lowered == p.lower() for p in unique_points):
            continue
        unique_points.append(cleaned)
        if len(unique_points) >= 4:
            break

    if not unique_points:
        return "1. Share the exact service name and I will provide eligibility, documents, fees, and processing steps."

    bullets: list[str] = []
    for idx, point in enumerate(unique_points):
        short = point[:220]
        short = re.sub(r"\s+", " ", short).strip(" .")
        bullets.append(f"{idx + 1}. Key point: {short}.")

    bullets.append(
        f"{len(bullets) + 1}. Recommended action: verify latest details on the official service portal before submission."
    )
    return "\n".join(bullets)


def _build_context_synthesis_instructions(context_text: str) -> str:
    return (
        "You are answering citizens about Indian government services. "
        "Synthesize the retrieved context into a clean answer. "
        "Never paste chunk text verbatim. "
        "Provide short sections in this order: Steps, Documents, Timelines/Fees (if available), and Official Portal guidance. "
        "If something is missing in context, say 'Not specified in source'.\n\n"
        "Retrieved snippets:\n"
        f"{context_text}\n\n"
        "Now provide the final citizen-friendly answer."
    )


def _search_context_fast(
    db: Session, query: str, limit: int = 5
) -> tuple[list[str], list[str]]:
    try:
        chunk_repo = ContentChunkRepository(db)
        faq_repo = FAQRepository(db)
        doc_repo = DocumentRepository(db)

        sources: list[str] = []
        context_parts: list[str] = []

        chunks = chunk_repo.search_text(query, limit)
        for chunk in chunks[:limit]:
            text = (chunk.chunk_text or "").strip()
            if not text:
                continue
            context_parts.append(text[:320])
            source = f"chunk_{chunk.chunk_id}"
            if source not in sources:
                sources.append(source)

        if len(context_parts) < limit:
            faqs = faq_repo.search_text(query, max(1, limit // 2))
            for faq in faqs:
                text = f"Q: {faq.question}\nA: {faq.answer}".strip()
                context_parts.append(text[:320])
                source = (faq.question or "faq")[:80]
                if source and source not in sources:
                    sources.append(source)

        if len(context_parts) < limit:
            docs = doc_repo.search_text(query, max(1, limit // 2))
            for doc in docs:
                text = (doc.raw_content or doc.name or "").strip()
                if not text:
                    continue
                context_parts.append(text[:320])
                source = (doc.name or f"doc_{doc.doc_id}")[:80]
                if source and source not in sources:
                    sources.append(source)

        return context_parts[:limit], sources[:limit]
    except Exception as exc:
        db.rollback()
        logger.warning("Fast context search unavailable, using empty context: %s", exc)
        return [], []


def detect_language(text: str) -> str:
    """Detect language code from text. Falls back to 'hi' for short texts."""
    try:
        detected = detect(text)
        return detected if detected in SYSTEM_PROMPTS else "hi"
    except LangDetectException:
        return "hi"


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optional authentication dependency - returns user or None"""
    if not credentials:
        return None

    try:
        session = (
            db.query(UserSession)
            .filter(
                UserSession.session_token == credentials.credentials,
                UserSession.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if not session:
            return None

        user = db.query(User).filter(User.id == session.user_id).first()
        return user
    except Exception:
        return None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "auto"
    history: Optional[List[ChatMessage]] = []
    service_context: Optional[str] = None
    response_mode: Optional[str] = "auto"  # auto | rag_only | sarvam
    session_id: Optional[str] = None
    user_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    language: str
    sources: List[str] = []
    session_id: Optional[str] = None


class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "hi"
    speed: Optional[float] = 1.0


@chat_router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Main chat endpoint with fast RAG fallback and latency-aware modes."""
    started = time.perf_counter()
    query = request.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    lang = request.language
    if lang == "auto" or not lang:
        lang = detect_language(query)

    response_mode = (request.response_mode or "auto").strip().lower()
    if response_mode not in {"auto", "rag_only", "sarvam"}:
        response_mode = "auto"

    if _is_security_threat(query):
        guarded = (
            "I can only help with Indian government service information. "
            "Please ask about Passport, Aadhaar, PAN, EPFO, DigiLocker, voter ID, "
            "driving license, or related official service steps."
        )
        return ChatResponse(
            response=guarded,
            language=lang,
            sources=[],
            session_id=request.session_id,
        )

    cache_key = f"{response_mode}:{query}"
    if response_mode != "sarvam":
        cached = chat_cache.get(cache_key, lang)
        if cached:
            return ChatResponse(**cached)

    context_parts, sources = _search_context_fast(db, query, limit=5)
    context_text = "\n\n".join(context_parts) if context_parts else ""

    fallback_response = _build_rag_fallback(query, lang, context_parts, user)
    response_text = fallback_response

    if response_mode != "rag_only":
        system_prompt = SYSTEM_PROMPTS.get(lang, DEFAULT_SYSTEM_PROMPT)
        system_prompt += (
            "\n\nWhen using retrieved context, synthesize and summarize it in clean citizen-friendly steps. "
            "Do not copy raw chunk text verbatim."
        )
        if context_text:
            system_prompt += "\n\n" + _build_context_synthesis_instructions(
                context_text
            )
        if request.service_context:
            system_prompt += f"\n\nThe user is asking about: {request.service_context}"

        messages = []
        for msg in (request.history or [])[-6:]:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": query})

        timeout_seconds = float(os.getenv("SARVAM_CHAT_TIMEOUT_SEC", "2.0"))
        try:
            response_text = await asyncio.wait_for(
                sarvam.chat(
                    messages=messages,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=400,
                ),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.warning("Sarvam chat timeout for query fallback: %.80s", query)
            response_text = fallback_response
        except Exception as exc:
            logger.warning("Sarvam chat failed, using fallback: %s", exc)
            response_text = fallback_response

        response_text = _clean_model_text(response_text)
        if not response_text or "not configured" in response_text.lower():
            response_text = fallback_response

    if user or request.session_id:
        user_msg = ChatSession(
            user_id=user.id if user else None,
            session_id=request.session_id,
            role="user",
            message=query,
            language=lang,
        )
        assistant_msg = ChatSession(
            user_id=user.id if user else None,
            session_id=request.session_id,
            role="assistant",
            message=response_text,
            language=lang,
            sources=json.dumps(sources) if sources else None,
        )
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()

    payload = ChatResponse(
        response=response_text,
        language=lang,
        sources=sources,
        session_id=request.session_id,
    )

    if response_mode != "sarvam":
        chat_cache.set(cache_key, lang, payload.model_dump())

    elapsed_ms = (time.perf_counter() - started) * 1000
    if elapsed_ms > 1000:
        logger.info(
            "Chat latency %.0fms mode=%s query=%.80s",
            elapsed_ms,
            response_mode,
            query,
        )

    return payload


@chat_router.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form(default="auto"),
):
    """Transcribe audio to text using Sarvam STT."""
    if not sarvam.is_available():
        raise HTTPException(status_code=503, detail="Sarvam API not configured")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    content_type = audio.content_type or ""
    if "webm" in content_type:
        fmt = "webm"
    elif "wav" in content_type:
        fmt = "wav"
    elif "mp3" in content_type or "mpeg" in content_type:
        fmt = "mp3"
    else:
        fmt = "webm"

    lang = language if language != "auto" else "auto"

    result = await sarvam.speech_to_text(
        audio_bytes=audio_bytes,
        language=lang,
        audio_format=fmt,
    )

    if "error" in result and not result.get("transcript"):
        return {"transcript": "", "error": str(result.get("error", "STT failed"))}

    return result


@chat_router.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Sarvam TTS."""
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
        return {"transcript": "", "error": str(result.get("error", "STT failed"))}

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
        "embedding_model": os.getenv(
            "EMBEDDING_MODEL", "intfloat/multilingual-e5-small"
        ),
        "generative_enabled": os.getenv("GENERATIVE_ENABLED", "false"),
    }


class ChatHistoryItem(BaseModel):
    role: str
    message: str
    language: Optional[str] = None
    sources: Optional[List[str]] = None
    created_at: datetime


@chat_router.get("/chat/history", response_model=List[ChatHistoryItem])
async def get_chat_history(
    limit: int = Query(50, ge=1, le=100),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    """Get user's chat history"""
    query = db.query(ChatSession).filter(ChatSession.user_id == user.id)

    if session_id:
        query = query.filter(ChatSession.session_id == session_id)

    chat_sessions = query.order_by(ChatSession.created_at.desc()).limit(limit).all()

    result = []
    for session in chat_sessions:
        sources = []
        if session.sources:
            try:
                sources = json.loads(session.sources)
            except json.JSONDecodeError:
                pass

        result.append(
            ChatHistoryItem(
                role=session.role,
                message=session.message,
                language=session.language,
                sources=sources if sources else None,
                created_at=session.created_at,
            )
        )

    return result


# ── Voice Chat (STS Pipeline) ─────────────────────────────────────────────────
@chat_router.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    language: str = "hi",
    db: Session = Depends(get_db),
):
    """Full Speech-to-Speech: STT → RAG/LLM → TTT → TTS."""
    if not sarvam.is_available():
        raise HTTPException(503, "Sarvam API not configured")
    # STT
    audio_bytes = await audio.read()
    content_type = (audio.content_type or "").lower()
    if "wav" in content_type:
        audio_format = "wav"
    elif "mp3" in content_type or "mpeg" in content_type:
        audio_format = "mp3"
    else:
        audio_format = "webm"

    stt = await sarvam.speech_to_text(
        audio_bytes,
        language=language or "auto",
        audio_format=audio_format,
        mode="transcribe",
    )
    transcript = stt.get("transcript", "")
    if not transcript:
        return {
            "transcript": "",
            "response": "Could not transcribe audio.",
            "audio_base64": "",
            "language": language,
        }
    # RAG + LLM
    from core.search import SearchEngine

    engine = SearchEngine(db=db)
    results = engine.search(transcript, limit=3)
    context = "\n".join(
        c.get("content", "")[:300] for c in results.get("results", [])[:3]
    )
    target_lang = language if language and language != "auto" else "hi"
    system = (
        "You are SevaSindhu AI for Indian government services. "
        f"Answer only in {target_lang} language in concise, citizen-friendly steps.\n"
        f"Context:\n{context}"
    )
    messages = [{"role": "user", "content": transcript}]
    response_text = await sarvam.chat(
        messages=messages, system_prompt=system, max_tokens=200
    )
    # TTS
    tts = await sarvam.text_to_speech(response_text, language=target_lang)
    return {
        "transcript": transcript,
        "response": response_text,
        "audio_base64": tts.get("audio_base64", ""),
        "language": target_lang,
    }
