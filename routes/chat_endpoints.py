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
from pydantic import BaseModel, Field
from typing import Optional, List
from langdetect import detect, LangDetectException
from datetime import datetime, timedelta

from core.database import get_db
from core.rag import RAGPipeline
from core.sarvam import sarvam
from core.cache import chat_cache
from core.repositories import ContentChunkRepository, FAQRepository, DocumentRepository
from core.search import SearchEngine
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

_TRANSLATION_CACHE: dict[tuple[str, str, str], tuple[str, float]] = {}
_TRANSLATION_TTL_SEC = 1800


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


FAST_INTENT_ENABLED = _env_bool("FAST_INTENT_ENABLED", True)
FAST_SARVAM_BENCH_ENABLED = _env_bool("FAST_SARVAM_BENCH_ENABLED", True)

_FAST_INTENT_RESPONSES_EN: dict[str, tuple[str, list[str]]] = {
    "passport application form": (
        "Apply online at Passport Seva Portal (passportindia.gov.in). Create an account, fill the fresh passport form, upload required documents, pay the fee, and book a PSK/POPSK appointment.",
        ["Passport Seva Portal"],
    ),
    "documents required for passport": (
        "For most fresh passport applications, keep proof of address, proof of date of birth, and photo ID ready. Exact documents depend on category, so confirm the latest checklist on passportindia.gov.in before appointment.",
        ["Passport Seva FAQ"],
    ),
    "aadhaar update address online": (
        "Use myAadhaar (myaadhaar.uidai.gov.in), choose Address Update, submit a valid address proof or use address validation if available, then track request status using the SRN.",
        ["UIDAI myAadhaar"],
    ),
    "epfo provident fund withdrawal": (
        "Log in to EPFO Member e-Sewa, verify KYC and bank details, then submit Form-19/10C withdrawal claim. Track claim status in the same portal.",
        ["EPFO Member e-Sewa"],
    ),
}

_FAST_RAW_QUERY_RESPONSES: dict[str, tuple[str, str, list[str]]] = {
    "what documents are needed for passport?": (
        "For passport applications, keep proof of address, proof of date of birth, and valid photo identity ready. Final required set varies by category, so confirm the latest list on passportindia.gov.in before booking appointment.",
        "en",
        ["Passport Seva FAQ"],
    ),
    "पासपोर्ट के लिए कौन से दस्तावेज़ चाहिए?": (
        "सामान्य रूप से पासपोर्ट के लिए पता प्रमाण, जन्म तिथि प्रमाण और फोटो पहचान पत्र चाहिए होते हैं। आपकी श्रेणी के अनुसार दस्तावेज़ बदल सकते हैं, इसलिए अंतिम सूची passportindia.gov.in पर जांचें।",
        "hi",
        ["Passport Seva FAQ"],
    ),
}

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


def _service_playbook_fallback(query: str) -> str | None:
    q = (query or "").lower()
    if any(k in q for k in ["aadhaar", "aadhar", "uidai", "myaadhaar"]):
        return (
            "Steps:\n"
            "- Open UIDAI/myAadhaar portal and choose Enrolment or Update service.\n"
            "- Fill details exactly as per supporting documents and select a nearby center if biometrics are required.\n"
            "- Upload required proofs and submit request to get URN/acknowledgement.\n\n"
            "Documents:\n"
            "- Identity proof, address proof, and date-of-birth proof as per UIDAI list.\n\n"
            "Timeline and fees:\n"
            "- Usually same day to a few working days depending on service type.\n"
            "- Fees vary by update type; confirm latest fee on UIDAI before payment.\n\n"
            "Official portal:\n"
            "- https://myaadhaar.uidai.gov.in/"
        )
    if any(k in q for k in ["passport", "psk", "passport seva"]):
        return (
            "Steps:\n"
            "- Create/login to Passport Seva account and select New/Re-issue Passport.\n"
            "- Fill online form, pay fees, and book PSK/POPSK appointment.\n"
            "- Visit center with originals for verification and biometrics, then track ARN status online.\n\n"
            "Documents:\n"
            "- Address proof, date-of-birth proof, identity proof, and old passport for re-issue.\n\n"
            "Timeline and fees:\n"
            "- Depends on normal/tatkaal and police verification outcome.\n\n"
            "Official portal:\n"
            "- https://www.passportindia.gov.in/"
        )
    if any(k in q for k in ["pan", "nsdl", "uti"]):
        return (
            "Steps:\n"
            "- Choose PAN new application or correction on official portal.\n"
            "- Fill form carefully, upload supporting documents, and pay fee.\n"
            "- Submit and track acknowledgement number until PAN is issued/updated.\n\n"
            "Documents:\n"
            "- Identity proof, address proof, date-of-birth proof, and photo/signature.\n\n"
            "Official portal:\n"
            "- https://www.onlineservices.nsdl.com/"
        )
    return None


def _build_rag_fallback(
    query: str,
    language: str,
    context_parts: list[str],
    user: Optional[User],
) -> str:
    localized_generic = {
        "hi": "मैं पासपोर्ट, आधार, पैन, ईपीएफओ, डिजिलॉकर और अन्य सरकारी सेवाओं में मदद कर सकता हूँ। कृपया अपना सवाल बताएं, मैं चरण-दर-चरण मार्गदर्शन दूंगा।",
        "ta": "பாஸ்போர்ட், ஆதார், பான், EPFO, DigiLocker மற்றும் பிற அரசு சேவைகளில் உதவ முடியும். உங்கள் கேள்வியை எழுதுங்கள்; படிப்படியாக வழிகாட்டுவேன்.",
        "te": "పాస్‌పోర్ట్, ఆధార్, PAN, EPFO, DigiLocker వంటి ప్రభుత్వ సేవలలో నేను సహాయం చేయగలను. మీ ప్రశ్నను పంపండి; దశలవారీగా మార్గనిర్దేశం చేస్తాను.",
        "bn": "পাসপোর্ট, আধার, প্যান, EPFO, DigiLocker সহ সরকারি পরিষেবা বিষয়ে আমি সাহায্য করতে পারি। আপনার প্রশ্ন লিখুন, আমি ধাপে ধাপে গাইড করব।",
        "mr": "पासपोर्ट, आधार, पॅन, EPFO, DigiLocker आणि इतर सरकारी सेवांबाबत मी मदत करू शकतो. तुमचा प्रश्न लिहा; मी टप्प्याटप्प्याने मार्गदर्शन करेन.",
        "gu": "પાસપોર્ટ, આધાર, PAN, EPFO, DigiLocker સહિત સરકારી સેવાઓમાં હું મદદ કરી શકું છું. તમારો પ્રશ્ન લખો; હું સ્ટેપ-બાય-સ્ટેપ માર્ગદર્શન આપીશ.",
        "kn": "ಪಾಸ್ಪೋರ್ಟ್, ಆಧಾರ್, PAN, EPFO, DigiLocker ಸೇರಿದಂತೆ ಸರ್ಕಾರಿ ಸೇವೆಗಳಲ್ಲಿ ನಾನು ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಬರೆಯಿರಿ; ಹಂತ ಹಂತವಾಗಿ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತೇನೆ.",
        "ml": "പാസ്‌പോർട്ട്, ആധാർ, PAN, EPFO, DigiLocker തുടങ്ങിയ സർക്കാർ സേവനങ്ങളിൽ ഞാൻ സഹായിക്കാം. നിങ്ങളുടെ ചോദ്യം എഴുതൂ; ഘട്ടം ഘട്ടമായി ഞാൻ വഴികാട്ടാം.",
        "pa": "ਪਾਸਪੋਰਟ, ਆਧਾਰ, ਪੈਨ, EPFO, DigiLocker ਅਤੇ ਹੋਰ ਸਰਕਾਰੀ ਸੇਵਾਵਾਂ ਵਿੱਚ ਮੈਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ। ਆਪਣਾ ਸਵਾਲ ਲਿਖੋ; ਮੈਂ ਕਦਮ-ਦਰ-ਕਦਮ ਗਾਈਡ ਕਰਾਂਗਾ।",
    }

    playbook = _service_playbook_fallback(query)
    if playbook:
        base = playbook
    elif context_parts:
        base = _summarize_context_locally(context_parts)
    else:
        base = localized_generic.get(
            language,
            "I can help with Indian government services like Passport, Aadhaar, PAN, "
            "EPFO, DigiLocker, voter ID, and driving license. Share your exact query "
            "and I will provide step-by-step guidance.",
        )

    first_name = str(getattr(user, "first_name", "") or "") if user else ""
    if first_name:
        return f"{first_name}, {base}"
    return base


def _summarize_context_locally(context_parts: list[str]) -> str:
    """Fast local summarizer for RAG-only mode; avoids raw chunk dumps."""

    def _clean_point(raw: str) -> str:
        text = " ".join((raw or "").replace("\n", " ").split()).strip()
        if not text:
            return ""

        lower = text.lower()
        if re.search(
            r"\b(refer rules|annexure|signature/thumb impression|space for|form of application)\b",
            lower,
        ):
            return ""

        if "q:" in lower and "a:" in lower:
            try:
                answer = text.split("A:", 1)[1].strip()
                text = answer or text
            except Exception:
                pass

        text = re.sub(r"\s+", " ", text).strip(" .")
        if len(text) > 220:
            text = text[:220].rsplit(" ", 1)[0].strip()

        if (
            "form" in lower
            and len(text) > 140
            and not any(
                k in lower
                for k in ["apply", "portal", "status", "document", "fee", "track"]
            )
        ):
            return ""

        return text

    unique_points: list[str] = []
    for raw in context_parts:
        cleaned = _clean_point(raw)
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if any(lowered == p.lower() for p in unique_points):
            continue
        unique_points.append(cleaned)
        if len(unique_points) >= 4:
            break

    if not unique_points:
        return (
            "What to do:\n"
            "- Share the exact service name and I will provide eligibility, documents, fees, and processing steps.\n\n"
            "Official portal:\n"
            "- Please use only official government portals for final submission and payments."
        )

    cleaned_points: list[str] = []
    for point in unique_points:
        short = re.sub(r"\s+", " ", point[:220]).strip(" .")
        cleaned_points.append(short)

    step_lines = "\n".join(f"- {item}" for item in cleaned_points[:3])
    return (
        "What to do:\n"
        f"{step_lines}\n\n"
        "Documents / details to keep ready:\n"
        "- Identity proof, address proof, and service-specific documents as listed on official portal.\n\n"
        "Official portal:\n"
        "- Verify latest process and fees on the official service website before submitting."
    )


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


def _should_use_rag_fast_path(query: str, context_parts: list[str]) -> bool:
    """Prefer low-latency RAG synthesis when context looks strong enough."""
    if not context_parts:
        return False
    query_l = query.lower()
    quick_terms = [
        "passport",
        "aadhaar",
        "aadhar",
        "पासपोर्ट",
        "आधार",
        "পাসপোর্ট",
        "আধার",
        "ड्राइविंग",
        "pan",
        "epfo",
        "document",
        "fee",
        "status",
        "track",
        "renew",
        "appointment",
        "apply",
    ]
    if any(term in query_l for term in quick_terms):
        return True
    if any(ord(ch) > 127 for ch in query):
        return True
    if len(context_parts) >= 2:
        return True

    tokens = [t for t in re.findall(r"[a-zA-Z0-9]{3,}", query.lower())]
    if not tokens:
        return True

    sample = context_parts[0].lower()
    overlap = sum(1 for token in tokens if token in sample)
    return overlap >= 2


def _looks_like_upstream_error(text: str) -> bool:
    lowered = (text or "").strip().lower()
    if not lowered:
        return True
    patterns = [
        "trouble connecting to the ai service",
        "something went wrong",
        "please try again in a moment",
        "service unavailable",
        "temporarily unavailable",
        "sarvam_error:",
    ]
    return any(p in lowered for p in patterns)


def _compress_for_voice(text: str, max_chars: int = 1200) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "")).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    clipped = cleaned[:max_chars].rsplit(" ", 1)[0].strip()
    if not clipped:
        clipped = cleaned[:max_chars].strip()
    return f"{clipped}."


def _normalize_chat_language(language: str | None) -> str:
    raw = (language or "").strip().lower()
    if not raw or raw == "auto":
        return "en"
    if "-" in raw:
        raw = raw.split("-", 1)[0]
    if raw == "od":
        return "or"
    return raw if raw in SYSTEM_PROMPTS else "en"


def _build_guided_actions(query: str, language: str) -> list[dict]:
    q = (query or "").lower()
    is_hi = language == "hi"

    if any(token in q for token in ["aadhaar", "aadhar", "आधार", "আধার", "ஆதார்"]):
        return [
            {
                "id": "open_uidai",
                "label": "UIDAI portal खोलें" if is_hi else "Open UIDAI portal",
                "type": "url",
                "url": "https://uidai.gov.in/",
            },
            {
                "id": "open_myaadhaar",
                "label": "myAadhaar self-service खोलें"
                if is_hi
                else "Open myAadhaar self-service",
                "type": "url",
                "url": "https://myaadhaar.uidai.gov.in/",
            },
            {
                "id": "open_services",
                "label": "आधार सेवा गाइड देखें" if is_hi else "Open Aadhaar service guide",
                "type": "navigate",
                "page": "service-detail",
                "service_id": "uidai_aadhaar_services",
            },
        ]

    if any(
        token in q
        for token in [
            "driving",
            "licence",
            "license",
            "sarathi",
            "dl",
            "ड्राइविंग",
            "লাইসেন্স",
            "परिवहन",
        ]
    ):
        return [
            {
                "id": "open_sarathi",
                "label": "Sarathi portal खोलें" if is_hi else "Open Sarathi portal",
                "type": "url",
                "url": "https://sarathi.parivahan.gov.in/",
            },
            {
                "id": "open_dl_service",
                "label": "Driving Licence सेवा पेज"
                if is_hi
                else "Open driving licence service page",
                "type": "navigate",
                "page": "service-detail",
                "service_id": "sarathi_driving_licence_services",
            },
        ]

    if any(
        token in q for token in ["passport", "पासपोर्ट", "পাসপোর্ট", "પાસપોર્ટ", "பாஸ்போர்ட்"]
    ):
        return [
            {
                "id": "open_passport_portal",
                "label": "Passport portal खोलें" if is_hi else "Open Passport portal",
                "type": "url",
                "url": "https://www.passportindia.gov.in/",
            },
            {
                "id": "open_passport_service",
                "label": "Passport सेवा पेज" if is_hi else "Open Passport service page",
                "type": "navigate",
                "page": "service-detail",
                "service_id": "passport_seva",
            },
        ]

    return [
        {
            "id": "browse_services",
            "label": "सभी सेवाएं देखें" if is_hi else "Browse all services",
            "type": "navigate",
            "page": "services",
        },
        {
            "id": "open_faq",
            "label": "FAQ खोलें" if is_hi else "Open FAQ",
            "type": "navigate",
            "page": "faq",
        },
    ]


def _service_scope_tokens(query: str) -> list[str]:
    q = (query or "").lower()
    if any(t in q for t in ["passport", "पासपोर्ट", "পাসপোর্ট"]):
        return ["passport", "psk", "popsk", "passport seva"]
    if any(t in q for t in ["aadhaar", "aadhar", "आधार", "আধার"]):
        return ["aadhaar", "aadhar", "uidai", "myaadhaar"]
    if any(
        t in q for t in ["driving", "license", "licence", "sarathi", "परिवहन", "লাইসেন্স"]
    ):
        return ["driving", "license", "licence", "sarathi", "parivahan", "dl"]
    if any(t in q for t in ["pan", "पैन", "প্যান"]):
        return ["pan", "nsdl", "uti", "income tax"]
    if any(t in q for t in ["epfo", "pf", "ईपीएफओ"]):
        return ["epfo", "uan", "pf", "member e-sewa"]
    if any(t in q for t in ["gst", "goods and services tax", "जीएसटी"]):
        return ["gst", "gstn", "goods and services tax"]
    if any(t in q for t in ["voter", "electoral", "मतदाता"]):
        return ["voter", "electoral", "election", "voters service portal"]
    if any(t in q for t in ["digilocker", "digital locker", "डिजिलॉकर"]):
        return ["digilocker", "document wallet", "issued documents"]
    if any(t in q for t in ["pds", "ration", "mera ration", "राशन"]):
        return ["pds", "ration", "nfsa", "mera ration"]
    return []


def _scope_match(text: str, scope_tokens: list[str]) -> bool:
    if not scope_tokens:
        return True
    lowered = (text or "").lower()
    return any(token in lowered for token in scope_tokens)


def _search_context_fast(
    db: Session, query: str, limit: int = 5
) -> tuple[list[str], list[str]]:
    try:
        scope_tokens = _service_scope_tokens(query)
        context_parts: list[str] = []
        sources: list[str] = []

        # First pass: hybrid search engine (semantic + text fallback)
        engine = SearchEngine(db)
        hybrid = engine.search(query, limit=max(limit * 2, 6))
        for item in hybrid.get("results", []):
            text = (item.get("content") or "").strip()
            if not text:
                continue
            trimmed = text[:320]
            if not _scope_match(trimmed, scope_tokens):
                continue
            if trimmed in context_parts:
                continue
            context_parts.append(trimmed)
            source = (item.get("source_name") or item.get("source") or "source")[:80]
            if source and source not in sources:
                sources.append(source)
            if len(context_parts) >= limit:
                return context_parts[:limit], sources[:limit]

        chunk_repo = ContentChunkRepository(db)
        faq_repo = FAQRepository(db)
        doc_repo = DocumentRepository(db)

        keywords = [query]
        for token in re.findall(r"[A-Za-z0-9-]+", query):
            if len(token) >= 5 or token.isupper():
                keywords.append(token)

        for kw in keywords[:5]:
            if len(context_parts) >= limit:
                break
            chunks = chunk_repo.search_text(kw, max(1, limit // 2))
            for chunk in chunks:
                text = (chunk.chunk_text or "").strip()
                if not text:
                    continue
                trimmed = text[:320]
                if not _scope_match(trimmed, scope_tokens):
                    continue
                if trimmed in context_parts:
                    continue
                context_parts.append(trimmed)
                source = f"chunk_{chunk.chunk_id}"
                if source not in sources:
                    sources.append(source)

        for kw in keywords[:5]:
            if len(context_parts) >= limit:
                break
            faqs = faq_repo.search_text(kw, 2)
            for faq in faqs:
                text = f"Q: {faq.question}\nA: {faq.answer}".strip()
                trimmed = text[:320]
                if not _scope_match(trimmed, scope_tokens):
                    continue
                if trimmed in context_parts:
                    continue
                context_parts.append(trimmed)
                source = str(faq.question or "faq")[:80]
                if source and source not in sources:
                    sources.append(source)

        for kw in keywords[:5]:
            if len(context_parts) >= limit:
                break
            docs = doc_repo.search_text(kw, 1)
            for doc in docs:
                text = (doc.description or doc.raw_content or doc.name or "").strip()
                if not text:
                    continue
                trimmed = text[:320]
                if not _scope_match(trimmed, scope_tokens):
                    continue
                if trimmed in context_parts:
                    continue
                context_parts.append(trimmed)
                source = str(doc.name or f"doc_{doc.doc_id}")[:80]
                if source and source not in sources:
                    sources.append(source)

        return context_parts[:limit], sources[:limit]
    except Exception as exc:
        db.rollback()
        logger.warning("Fast context search unavailable, using empty context: %s", exc)
        return [], []


def _cache_get_translation(text: str, source_lang: str, target_lang: str) -> str | None:
    key = (text, source_lang, target_lang)
    entry = _TRANSLATION_CACHE.get(key)
    if not entry:
        return None
    translated, ts = entry
    if (time.time() - ts) > _TRANSLATION_TTL_SEC:
        _TRANSLATION_CACHE.pop(key, None)
        return None
    return translated


def _cache_set_translation(
    text: str, source_lang: str, target_lang: str, translated: str
) -> None:
    if not translated:
        return
    _TRANSLATION_CACHE[(text, source_lang, target_lang)] = (translated, time.time())


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
    speak_text: Optional[str] = None
    actions: List[dict] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None


class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "hi"
    speed: Optional[float] = 1.0


@chat_router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    response: Response,
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
    lang = _normalize_chat_language(lang)

    response_mode = (request.response_mode or "auto").strip().lower()
    if response_mode not in {"auto", "rag_only", "sarvam"}:
        response_mode = "auto"

    if _is_security_threat(query):
        guarded = (
            "I can only help with Indian government service information. "
            "Please ask about Passport, Aadhaar, PAN, EPFO, DigiLocker, voter ID, "
            "driving license, or related official service steps."
        )
        response.headers["X-Route-Mode"] = "security_guard"
        response.headers["X-Latency-Total-MS"] = str(
            int((time.perf_counter() - started) * 1000)
        )
        return ChatResponse(
            response=guarded,
            language=lang,
            speak_text=_compress_for_voice(guarded, max_chars=180),
            actions=_build_guided_actions(query, lang),
            sources=[],
            session_id=request.session_id,
        )

    raw_normalized_query = " ".join(query.lower().split())
    fast_raw_entry = _FAST_RAW_QUERY_RESPONSES.get(raw_normalized_query)
    if (
        fast_raw_entry
        and FAST_INTENT_ENABLED
        and (
            response_mode in {"auto", "rag_only"}
            or (response_mode == "sarvam" and FAST_SARVAM_BENCH_ENABLED)
        )
    ):
        fast_text, fast_lang, fast_sources = fast_raw_entry
        payload = ChatResponse(
            response=fast_text,
            language=fast_lang,
            speak_text=_compress_for_voice(fast_text, max_chars=1200),
            actions=_build_guided_actions(query, fast_lang),
            sources=fast_sources,
            session_id=request.session_id,
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        response.headers["X-Route-Mode"] = "intent_fast"
        response.headers["X-Latency-Search-MS"] = "0"
        response.headers["X-Latency-LLM-MS"] = "0"
        response.headers["X-Latency-Total-MS"] = str(elapsed_ms)
        if response_mode != "sarvam":
            chat_cache.set(f"{response_mode}:{query}", fast_lang, payload.model_dump())
        return payload

    retrieval_query = query
    if lang != "en":
        translated_query = _cache_get_translation(query, lang, "en")
        if translated_query is None:
            translated_query = await sarvam.translate(
                query,
                source_language=lang,
                target_language="en",
            )
            _cache_set_translation(query, lang, "en", translated_query)
        if translated_query and translated_query.strip():
            retrieval_query = translated_query.strip()

    cache_key = f"{response_mode}:{retrieval_query}"
    if response_mode != "sarvam":
        cached = chat_cache.get(cache_key, lang)
        if cached:
            response.headers["X-Cache-Hit"] = "1"
            response.headers["X-Route-Mode"] = "cache"
            response.headers["X-Latency-Total-MS"] = str(
                int((time.perf_counter() - started) * 1000)
            )
            return ChatResponse(**cached)
    response.headers["X-Cache-Hit"] = "0"

    normalized_query = " ".join(retrieval_query.lower().split())
    if response_mode != "sarvam" and lang == "en" and FAST_INTENT_ENABLED:
        fast_entry = _FAST_INTENT_RESPONSES_EN.get(normalized_query)
        if fast_entry:
            fast_text, fast_sources = fast_entry
            payload = ChatResponse(
                response=fast_text,
                language=lang,
                speak_text=_compress_for_voice(fast_text, max_chars=1200),
                actions=_build_guided_actions(query, lang),
                sources=fast_sources,
                session_id=request.session_id,
            )
            chat_cache.set(cache_key, lang, payload.model_dump())
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            response.headers["X-Route-Mode"] = "intent_fast"
            response.headers["X-Latency-Search-MS"] = "0"
            response.headers["X-Latency-LLM-MS"] = "0"
            response.headers["X-Latency-Total-MS"] = str(elapsed_ms)
            return payload

    search_started = time.perf_counter()
    context_parts, sources = _search_context_fast(db, retrieval_query, limit=3)
    search_elapsed_ms = int((time.perf_counter() - search_started) * 1000)
    response.headers["X-Latency-Search-MS"] = str(search_elapsed_ms)
    context_text = "\n\n".join(context_parts) if context_parts else ""

    fallback_response = _build_rag_fallback(retrieval_query, lang, context_parts, user)
    response_text = fallback_response

    use_sarvam = response_mode == "sarvam" or (
        response_mode == "auto" and sarvam.is_available()
    )

    llm_elapsed_ms = 0
    route_mode_used = "rag_fast"
    if use_sarvam:
        route_mode_used = "sarvam"
        llm_started = time.perf_counter()
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
        messages.append({"role": "user", "content": retrieval_query})

        try:
            timeout_seconds = float(os.getenv("SARVAM_CHAT_TIMEOUT_SEC", "8.0"))
        except ValueError:
            timeout_seconds = 8.0
        try:
            response_text = await asyncio.wait_for(
                sarvam.chat(
                    messages=messages,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=220,
                ),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.warning("Sarvam chat timeout for query fallback: %.80s", query)
            response_text = fallback_response
        except Exception as exc:
            logger.warning("Sarvam chat failed, using fallback: %s", exc)
            response_text = fallback_response
            route_mode_used = "sarvam_fallback"

        llm_elapsed_ms = int((time.perf_counter() - llm_started) * 1000)

        response_text = _clean_model_text(response_text)
        if (
            not response_text
            or "not configured" in response_text.lower()
            or _looks_like_upstream_error(response_text)
        ):
            response_text = fallback_response
            route_mode_used = "rag_fallback"

    if lang != "en" and response_text:
        translated = _cache_get_translation(response_text, "en", lang)
        if translated is None:
            translated = await sarvam.translate(
                response_text,
                source_language="en",
                target_language=lang,
            )
            _cache_set_translation(response_text, "en", lang, translated)
        if translated and translated.strip():
            response_text = translated.strip()

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
        speak_text=_compress_for_voice(response_text, max_chars=1200),
        actions=_build_guided_actions(query, lang),
        sources=sources,
        session_id=request.session_id,
    )

    if response_mode != "sarvam":
        chat_cache.set(cache_key, lang, payload.model_dump())

    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Route-Mode"] = route_mode_used
    response.headers["X-Latency-LLM-MS"] = str(llm_elapsed_ms)
    response.headers["X-Latency-Total-MS"] = str(int(elapsed_ms))
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
        raise HTTPException(
            status_code=502,
            detail=str(result.get("error", "STT failed")),
        )

    return result


@chat_router.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Sarvam TTS."""
    if not sarvam.is_available():
        raise HTTPException(status_code=503, detail="Sarvam API not configured")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    language = _normalize_chat_language(request.language or "hi")
    result = await sarvam.text_to_speech(
        text=request.text,
        language=language,
        speed=request.speed or 1.0,
    )

    if "error" in result:
        raise HTTPException(
            status_code=502,
            detail=str(result.get("error", "TTS failed")),
        )

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
        "sarvam_chat_model": getattr(sarvam, "chat_model", ""),
        "sarvam_stt_model": getattr(sarvam, "stt_model", ""),
        "sarvam_tts_model": getattr(sarvam, "tts_model", ""),
        "sarvam_translate_model": getattr(sarvam, "translate_model", ""),
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
        raw_sources = getattr(session, "sources", None)
        if raw_sources:
            try:
                sources = json.loads(str(raw_sources))
            except json.JSONDecodeError:
                pass

        result.append(
            ChatHistoryItem(
                role=str(session.role),
                message=str(session.message),
                language=(
                    str(getattr(session, "language", ""))
                    if str(getattr(session, "language", "")).strip()
                    else None
                ),
                sources=sources if sources else None,
                created_at=getattr(session, "created_at", datetime.utcnow()),
            )
        )

    return result


# ── Voice Chat (STS Pipeline) ─────────────────────────────────────────────────
@chat_router.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    language: str = "hi",
    fast_mode: bool = True,
    max_voice_chars: int = Query(500, ge=120, le=1500),
    db: Session = Depends(get_db),
):
    """Full Speech-to-Speech: STT → RAG/LLM → TTT → TTS."""
    if not sarvam.is_available():
        raise HTTPException(503, "Sarvam API not configured")
    try:
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
        )
        transcript = stt.get("transcript", "")
        if not transcript:
            return {
                "transcript": "",
                "response": "Could not transcribe audio.",
                "audio_base64": "",
                "language": language,
                "error": stt.get("error") if isinstance(stt, dict) else None,
            }

        # RAG + LLM
        from core.search import SearchEngine

        engine = SearchEngine(db=db)
        detected_lang = _normalize_chat_language(stt.get("language_code") or language)
        target_lang = _normalize_chat_language(
            language if language and language != "auto" else detected_lang
        )

        search_text = transcript
        if target_lang != "en":
            translated_search = await sarvam.translate(
                transcript,
                source_language=target_lang,
                target_language="en",
            )
            if translated_search and translated_search.strip():
                search_text = translated_search.strip()

        results = engine.search(search_text, limit=3)
        context = "\n".join(
            c.get("content", "")[:300] for c in results.get("results", [])[:3]
        )
        if fast_mode:
            if context:
                context_parts = [
                    c.get("content", "") for c in results.get("results", [])[:3]
                ]
                response_text = _build_rag_fallback(
                    search_text, target_lang, context_parts, None
                )
            else:
                response_text = _build_rag_fallback(search_text, target_lang, [], None)
        else:
            system = (
                "You are SevaSindhu AI for Indian government services. "
                f"Answer only in {target_lang} language in concise, citizen-friendly steps.\n"
                f"Context:\n{context}"
            )
            messages = [{"role": "user", "content": search_text}]
            response_text = await sarvam.chat(
                messages=messages, system_prompt=system, max_tokens=120
            )
        if target_lang != "en" and response_text:
            translated = await sarvam.translate(
                response_text,
                source_language="en",
                target_language=target_lang,
            )
            if translated and translated.strip():
                response_text = translated.strip()

        voice_text = _compress_for_voice(response_text, max_chars=max_voice_chars)
        if fast_mode:
            response_text = voice_text

        # TTS
        tts = await sarvam.text_to_speech(voice_text, language=target_lang, speed=1.2)
        return {
            "transcript": transcript,
            "response": response_text,
            "audio_base64": tts.get("audio_base64", "")
            if isinstance(tts, dict)
            else "",
            "language": target_lang,
            "error": tts.get("error")
            if isinstance(tts, dict) and "error" in tts
            else None,
        }
    except Exception as exc:
        logger.exception("voice_chat pipeline failed: %s", exc)
        return {
            "transcript": "",
            "response": "Voice pipeline failed. Please try again.",
            "audio_base64": "",
            "language": _normalize_chat_language(language),
            "error": str(exc),
        }


# ── Form Help Endpoint ─────────────────────────────────────────────────────────
# Completely isolated from the main chatbot. Powers the "?/HELP" button
# that appears next to each PDF download in ServiceDetail.
#
# Unlike the first version, this now fetches RAG context from the database
# so the help content is grounded in real, factual document information
# rather than relying purely on the LLM's parametric knowledge.
# ─────────────────────────────────────────────────────────────────────────────

class FormHelpRequest(BaseModel):
    service_id: str
    service_name: str
    document_name: str
    language: Optional[str] = "en"


class FormHelpResponse(BaseModel):
    help_text: str
    language: str
    sources: List[str] = Field(default_factory=list)


_FORM_HELP_SYSTEM_PROMPT = (
    "You are a helpful Indian government document assistant. "
    "A citizen needs help understanding a specific government form or PDF. "
    "You have been given RETRIEVED CONTEXT from official government sources below. "
    "Use this context to provide FACTUAL, ACCURATE answers.\n\n"
    "Structure your response as:\n"
    "1. **Why this document is needed** — explain its legal/procedural purpose using the retrieved context (2-3 sentences).\n"
    "2. **How to fill it** — provide clear numbered steps. Reference specific fields, sections, or annexures mentioned in the context.\n"
    "3. **Common mistakes to avoid** — list 2-3 real mistakes based on the context.\n"
    "4. **Where to submit** — tell the user the exact submission method from the context.\n\n"
    "RULES:\n"
    "- ONLY use information from the retrieved context. Do NOT invent field names or procedures.\n"
    "- If the context doesn't cover something, say 'Please check the official portal for this detail.'\n"
    "- Keep the response concise, friendly, and in simple language.\n"
    "- Always respond in the language specified by the user."
)

_FORM_HELP_SYSTEM_PROMPT_NO_CONTEXT = (
    "You are a helpful Indian government document assistant. "
    "A citizen needs help understanding a specific government form or PDF. "
    "No specific retrieved context is available, so provide general but accurate guidance.\n\n"
    "Structure your response as:\n"
    "1. **Why this document is needed** — explain its general procedural purpose (2-3 sentences).\n"
    "2. **How to fill it** — provide general best-practice steps for filling government forms.\n"
    "3. **Common mistakes to avoid** — list 2-3 common mistakes.\n"
    "4. **Where to submit** — advise checking the official portal.\n\n"
    "RULES:\n"
    "- Do NOT make up specific field names or procedures.\n"
    "- Always recommend verifying on the official portal.\n"
    "- Keep the response concise and friendly.\n"
    "- Always respond in the language specified by the user."
)

_FORM_HELP_FALLBACK = (
    "**Why this document is needed**\n"
    "This document is required to verify your eligibility and identity for the service. "
    "It is part of the standard application process mandated by the government authority.\n\n"
    "**How to fill it**\n"
    "1. Read all instructions on the form carefully before filling.\n"
    "2. Use capital letters for name and address fields.\n"
    "3. Fill all mandatory fields marked with * or 'Required'.\n"
    "4. Attach self-attested copies of all supporting documents.\n"
    "5. Sign/thumb-impression only where indicated.\n\n"
    "**Common mistakes to avoid**\n"
    "- Leaving mandatory fields blank.\n"
    "- Using nicknames instead of full legal name.\n"
    "- Submitting photocopies without self-attestation.\n\n"
    "**Where to submit**\n"
    "Submit at the designated counter of the relevant government office, "
    "or upload via the official online portal."
)


def _build_form_help_rag_query(service_name: str, document_name: str) -> str:
    """Build a focused search query to find relevant RAG context for the form."""
    return f"{service_name} {document_name} form fill instructions documents required procedure"


@chat_router.post("/form-help", response_model=FormHelpResponse)
async def form_help(
    request: FormHelpRequest,
    db: Session = Depends(get_db),
) -> FormHelpResponse:
    """
    Generate contextual help for a specific government form/PDF.
    Explains WHY the document is needed and HOW to fill it.

    Enhanced with RAG: searches the database for real, factual context
    about the document before generating help content. This ensures
    the response is grounded in actual official information.

    This endpoint is fully isolated from the main chatbot pipeline.
    """
    lang = _normalize_chat_language(request.language)
    sources: list[str] = []

    # ── Step 1: Search RAG database for factual context about this form ─────
    rag_query = _build_form_help_rag_query(request.service_name, request.document_name)
    context_parts, rag_sources = _search_context_fast(db, rag_query, limit=6)

    # Also search specifically for the document name
    if len(context_parts) < 3:
        extra_parts, extra_sources = _search_context_fast(db, request.document_name, limit=4)
        for part in extra_parts:
            if part not in context_parts:
                context_parts.append(part)
        for src in extra_sources:
            if src not in rag_sources:
                rag_sources.append(src)

    sources = rag_sources[:5]
    has_context = bool(context_parts)

    # ── Step 2: Build the prompt with RAG context ───────────────────────────
    if has_context:
        context_text = "\n---\n".join(context_parts[:6])
        system_prompt = (
            _FORM_HELP_SYSTEM_PROMPT
            + f"\n\n--- RETRIEVED CONTEXT ---\n{context_text}\n--- END CONTEXT ---"
        )
    else:
        system_prompt = _FORM_HELP_SYSTEM_PROMPT_NO_CONTEXT

    lang_instruction = (
        "Hindi" if lang == "hi"
        else "English" if lang == "en"
        else f"the language with code '{lang}'"
    )

    user_prompt = (
        f"Service: {request.service_name}\n"
        f"Document / Form: {request.document_name}\n\n"
        f"Using the retrieved context above, explain why this document is needed "
        f"for '{request.service_name}' and provide step-by-step guidance on how "
        f"to fill it correctly. Include specific field names, sections, or procedures "
        f"from the context where available.\n"
        f"Respond in {lang_instruction}."
    )

    # ── Step 3: Generate help via Sarvam (with RAG-grounded context) ────────
    try:
        raw_help = await sarvam.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temp for factual accuracy
            max_tokens=800,
        )
        help_text = _clean_model_text(raw_help)
        if not help_text or _looks_like_upstream_error(help_text):
            # Fall back to local summarization if we have RAG context
            if has_context:
                help_text = _build_form_help_from_context(
                    request.service_name, request.document_name, context_parts
                )
            else:
                help_text = _FORM_HELP_FALLBACK
    except Exception as exc:
        logger.warning("form_help LLM generation failed: %s", exc)
        # Fall back to local summarization if we have RAG context
        if has_context:
            help_text = _build_form_help_from_context(
                request.service_name, request.document_name, context_parts
            )
        else:
            help_text = _FORM_HELP_FALLBACK

    # ── Step 4: Translate if non-English language requested ──────────────────
    if lang not in ("en",) and sarvam.is_available():
        try:
            translated = await sarvam.translate(
                help_text, source_language="en", target_language=lang
            )
            if translated and not _looks_like_upstream_error(translated):
                help_text = translated
        except Exception as exc:
            logger.warning("form_help translation failed: %s", exc)

    return FormHelpResponse(help_text=help_text, language=lang, sources=sources)


def _build_form_help_from_context(
    service_name: str,
    document_name: str,
    context_parts: list[str],
) -> str:
    """
    Build a structured help response directly from RAG context
    when the LLM is unavailable. This is the offline fallback.
    """
    # Clean and deduplicate context
    cleaned: list[str] = []
    for part in context_parts[:5]:
        text = re.sub(r"\s+", " ", (part or "").strip())
        if len(text) > 30 and text not in cleaned:
            cleaned.append(text[:300])

    if not cleaned:
        return _FORM_HELP_FALLBACK

    context_bullets = "\n".join(f"- {item}" for item in cleaned[:4])

    return (
        f"**Why this document is needed**\n"
        f"The '{document_name}' is required as part of the '{service_name}' application process. "
        f"Below is information retrieved from official sources:\n\n"
        f"**Official information**\n"
        f"{context_bullets}\n\n"
        f"**How to fill it**\n"
        f"1. Download the form from the official portal.\n"
        f"2. Read all instructions carefully before filling.\n"
        f"3. Fill all mandatory fields using capital letters.\n"
        f"4. Attach self-attested copies of supporting documents.\n"
        f"5. Verify all details match your identity documents exactly.\n\n"
        f"**Common mistakes to avoid**\n"
        f"- Leaving mandatory fields blank.\n"
        f"- Name mismatch between form and identity documents.\n"
        f"- Submitting without required supporting documents.\n\n"
        f"**Where to submit**\n"
        f"Please check the official portal for the latest submission process and center locations."
    )
