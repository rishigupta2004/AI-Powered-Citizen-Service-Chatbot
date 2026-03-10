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

    if context_parts:
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
    unique_points: list[str] = []
    for raw in context_parts:
        cleaned = " ".join((raw or "").replace("\n", " ").split())
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if re.search(r"\b(refer rules|annexure|signature/thumb impression)\b", lowered):
            continue
        if "form" in lowered and len(cleaned) > 140:
            continue
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
    ]
    return any(p in lowered for p in patterns)


def _instant_service_template(query: str, language: str) -> Optional[str]:
    q = (query or "").lower()
    is_hi = language == "hi"
    is_bn = language == "bn"
    is_as = language == "as"
    if any(
        token in q
        for token in ["passport", "पासपोर्ट", "পাসপোর্ট", "પાસપોર્ટ", "பாஸ்போர்ட்", "పాస్పోర్ట్"]
    ):
        if is_hi:
            return (
                "पासपोर्ट सेवा के लिए यह त्वरित चेकलिस्ट अपनाएं:\n"
                "1. Passport Seva पोर्टल पर रजिस्टर/लॉगिन करें।\n"
                "2. Fresh/Renewal फॉर्म भरकर सबमिट करें।\n"
                "3. शुल्क भुगतान करें और PSK/POPSK अपॉइंटमेंट बुक करें।\n"
                "4. अपॉइंटमेंट पर पहचान, पता और DOB दस्तावेज़ साथ रखें।\n"
                "5. पुलिस वेरिफिकेशन और डिस्पैच के लिए फाइल नंबर ट्रैक करें।"
            )
        if is_bn:
            return (
                "পাসপোর্ট পরিষেবার জন্য দ্রুত চেকলিস্ট:\n"
                "1. Passport Seva পোর্টালে রেজিস্টার/লগইন করুন।\n"
                "2. নতুন/রিনিউয়াল ফর্ম পূরণ করে জমা দিন।\n"
                "3. ফি প্রদান করে PSK/POPSK অ্যাপয়েন্টমেন্ট বুক করুন।\n"
                "4. অ্যাপয়েন্টমেন্টে পরিচয়, ঠিকানা ও DOB প্রমাণ নিয়ে যান।\n"
                "5. পুলিশ ভেরিফিকেশন ও ডিসপ্যাচের জন্য ফাইল নম্বর ট্র্যাক করুন।"
            )
        if is_as:
            return (
                "পাছপ’ৰ্ট সেৱাৰ বাবে দ্ৰুত চেকলিষ্ট:\n"
                "1. Passport Seva প’ৰ্টেলত ৰেজিষ্টাৰ/লগইন কৰক।\n"
                "2. নতুন/নৱীকৰণ ফৰ্ম পূৰণ কৰি দাখিল কৰক।\n"
                "3. ফী পৰিশোধ কৰি PSK/POPSK অ্যাপইণ্টমেণ্ট বুক কৰক।\n"
                "4. অ্যাপইণ্টমেণ্টত পৰিচয়, ঠিকনা আৰু জন্ম তাৰিখৰ প্ৰমাণ লৈ যাওক।\n"
                "5. পুলিচ ভেৰিফিকেচন আৰু ডিচপেচৰ বাবে ফাইল নম্বৰ ট্ৰেক কৰক।"
            )
        return (
            "For Passport service, follow this fast checklist:\n"
            "1. Register/login on Passport Seva portal.\n"
            "2. Fill fresh/renewal form and submit.\n"
            "3. Pay fee and book PSK/POPSK appointment.\n"
            "4. Carry identity, address, and DOB proofs to appointment.\n"
            "5. Track file number for police verification and dispatch."
        )
    if any(
        token in q
        for token in ["aadhaar", "aadhar", "आधार", "আধার", "আধার", "ಆಧಾರ್", "ஆதார்"]
    ):
        if is_hi:
            return (
                "आधार अपडेट के लिए UIDAI आधिकारिक पोर्टल का उपयोग करें:\n"
                "1. अपडेट प्रकार चुनें (पता/नाम/DOB/मोबाइल)।\n"
                "2. UIDAI सूची के अनुसार सपोर्टिंग डॉक्यूमेंट अपलोड करें।\n"
                "3. शुल्क भुगतान कर अनुरोध सबमिट करें।\n"
                "4. URN सेव करें और स्टेटस ट्रैक करें।"
            )
        return (
            "For Aadhaar update, use UIDAI official portal:\n"
            "1. Choose update type (address/name/DOB/mobile).\n"
            "2. Upload supporting document from UIDAI list.\n"
            "3. Pay update fee and submit.\n"
            "4. Save URN and track status online."
        )
    if any(token in q for token in ["pan", "पैन", "প্যান", "પાન"]):
        if is_hi:
            return (
                "PAN सेवाओं के लिए:\n"
                "1. NSDL/UTI आधिकारिक PAN पोर्टल खोलें।\n"
                "2. नया PAN या करेक्शन विकल्प चुनें।\n"
                "3. फॉर्म भरें, दस्तावेज़ अपलोड करें, शुल्क दें।\n"
                "4. स्टेटस के लिए acknowledgement नंबर ट्रैक करें।"
            )
        return (
            "For PAN services:\n"
            "1. Use NSDL/UTI official PAN service page.\n"
            "2. Select new PAN or correction.\n"
            "3. Fill form, upload proof, and pay fee.\n"
            "4. Track acknowledgement number for status."
        )
    if any(token in q for token in ["epfo", "pf", "ईपीएफओ", "पीएफ", "ইপিএফও"]):
        if is_hi:
            return (
                "EPFO सेवाओं के लिए:\n"
                "1. UAN से EPFO Member e-Sewa में लॉगिन करें।\n"
                "2. KYC और बैंक डिटेल approved होनी चाहिए।\n"
                "3. Online Services से claim/transfer/passbook कार्य करें।\n"
                "4. सबमिशन के बाद पोर्टल में claim status ट्रैक करें।"
            )
        return (
            "For EPFO services:\n"
            "1. Login to EPFO Member e-Sewa using UAN.\n"
            "2. Verify KYC and bank details are approved.\n"
            "3. Use Online Services for claim/transfer/passbook actions.\n"
            "4. Track claim status in portal after submission."
        )
    return None


def _compress_for_voice(text: str, max_chars: int = 140) -> str:
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


def _search_context_fast(
    db: Session, query: str, limit: int = 5
) -> tuple[list[str], list[str]]:
    try:
        context_parts: list[str] = []
        sources: list[str] = []
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
                if trimmed in context_parts:
                    continue
                context_parts.append(trimmed)
                source = (faq.question or "faq")[:80]
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
                if trimmed in context_parts:
                    continue
                context_parts.append(trimmed)
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

    cache_key = f"{response_mode}:{query}"
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

    search_started = time.perf_counter()
    context_parts, sources = _search_context_fast(db, query, limit=3)
    search_elapsed_ms = int((time.perf_counter() - search_started) * 1000)
    response.headers["X-Latency-Search-MS"] = str(search_elapsed_ms)
    context_text = "\n\n".join(context_parts) if context_parts else ""

    fallback_response = _build_rag_fallback(query, lang, context_parts, user)
    response_text = fallback_response

    prefer_rag_fast_path = _should_use_rag_fast_path(query, context_parts)
    use_sarvam = response_mode == "sarvam" or (
        response_mode == "auto" and not prefer_rag_fast_path
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
        messages.append({"role": "user", "content": query})

        timeout_seconds = float(os.getenv("SARVAM_CHAT_TIMEOUT_SEC", "2.0"))
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
        speak_text=_compress_for_voice(response_text, max_chars=180),
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
        return {"transcript": "", "error": str(result.get("error", "STT failed"))}

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
        if language != "en":
            fallback = await sarvam.text_to_speech(
                text=request.text,
                language="en",
                speed=request.speed or 1.0,
            )
            if "error" not in fallback:
                return Response(
                    content=fallback["audio_bytes"],
                    media_type="audio/wav",
                    headers={"Content-Disposition": "inline; filename=response.wav"},
                )
        return {"transcript": "", "error": str(result.get("error", "TTS failed"))}

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
    fast_mode: bool = True,
    max_voice_chars: int = Query(140, ge=80, le=220),
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
    detected_lang = _normalize_chat_language(stt.get("language_code") or language)
    target_lang = _normalize_chat_language(
        language if language and language != "auto" else detected_lang
    )
    if fast_mode:
        if context:
            context_parts = [
                c.get("content", "") for c in results.get("results", [])[:3]
            ]
            response_text = _build_rag_fallback(
                transcript, target_lang, context_parts, None
            )
        else:
            response_text = _build_rag_fallback(transcript, target_lang, [], None)
    else:
        system = (
            "You are SevaSindhu AI for Indian government services. "
            f"Answer only in {target_lang} language in concise, citizen-friendly steps.\n"
            f"Context:\n{context}"
        )
        messages = [{"role": "user", "content": transcript}]
        response_text = await sarvam.chat(
            messages=messages, system_prompt=system, max_tokens=120
        )
    voice_text = _compress_for_voice(response_text, max_chars=max_voice_chars)
    if fast_mode:
        response_text = voice_text
    # TTS
    tts = await sarvam.text_to_speech(voice_text, language=target_lang, speed=1.2)
    if "error" in tts and target_lang != "en":
        tts = await sarvam.text_to_speech(voice_text, language="en", speed=1.2)
    return {
        "transcript": transcript,
        "response": response_text,
        "audio_base64": tts.get("audio_base64", "") if isinstance(tts, dict) else "",
        "language": target_lang,
        "error": tts.get("error") if isinstance(tts, dict) and "error" in tts else None,
    }
