"""
Chat, STT, and TTS endpoints.
These integrate with the existing FastAPI app.
"""

import os
import logging
import json
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
    """Main chat endpoint. Runs RAG → Sarvam-M pipeline."""
    query = request.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    lang = request.language
    if lang == "auto" or not lang:
        lang = detect_language(query)

    from core.search import SearchEngine
    search_engine = SearchEngine(db=db)
    search_results = search_engine.search(query, limit=5)
    context_results = search_results.get("results", [])
    print(f"DEBUG keys={list(context_results[0].keys()) if context_results else []}", flush=True)

    context_parts = []
    sources = []
    for chunk in context_results:
        content = chunk.get("content", "").strip()
        source_name = chunk.get("source_name", chunk.get("source", ""))
        if content:
            context_parts.append(content[:400])
        if source_name and source_name not in sources:
            sources.append(source_name)

    context_text = "\n\n".join(context_parts) if context_parts else ""

    system_prompt = SYSTEM_PROMPTS.get(lang, DEFAULT_SYSTEM_PROMPT)

    is_first_message = not request.history

    if user and is_first_message:
        greeting = f"Hello {user.first_name}! "
        if lang == "hi":
            greeting = f"नमस्ते {user.first_name}! "
        elif lang == "ta":
            greeting = f"வணக்கம் {user.first_name}! "
        elif lang == "te":
            greeting = f"హలో {user.first_name}! "
        elif lang == "bn":
            greeting = f"নমস্কার {user.first_name}! "
        system_prompt = greeting + system_prompt

    if context_text:
        system_prompt += (
            f"\n\nRelevant government information:\n{context_text}\n\n"
            "Use the above information to answer accurately. "
            "Cite the service name when relevant."
        )

    if request.service_context:
        system_prompt += f"\n\nThe user is asking about: {request.service_context}"

    messages = []
    for msg in (request.history or [])[-6:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": query})

    response_text = await sarvam.chat(
        messages=messages,
        system_prompt=system_prompt,
        temperature=0.3,
        max_tokens=512,
    )

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
        raise HTTPException(status_code=500, detail=result["error"])

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
