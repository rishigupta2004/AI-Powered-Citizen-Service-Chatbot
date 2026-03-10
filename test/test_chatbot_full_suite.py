"""
Comprehensive chatbot validation suite for real endpoint testing.

Covers:
1) 15 multilingual/service prompts
2) 15 non-straightforward prompts (stutter/repetition/code-mix)
3) TTT, TTS, STT, STS (15 prompts each where applicable)

Usage:
  API_BASE_URL=https://gov-chatbot.fly.dev python test/test_chatbot_full_suite.py

Note:
- Default API_BASE_URL remains localhost to preserve local-first behavior.
- For deployed testing (Fly + Supabase), set API_BASE_URL explicitly.
"""

from __future__ import annotations

import base64
import json
import math
import os
import time
from datetime import datetime
from typing import Any

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
REPORT_PATH = os.path.join(
    os.path.dirname(__file__), "scripts", "test_results_chatbot_full.json"
)

PASS, FAIL, WARN = "✅", "❌", "⚠️"


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    arr = sorted(values)
    idx = max(0, min(len(arr) - 1, math.ceil(0.95 * len(arr)) - 1))
    return arr[idx]


def call_chat(
    message: str,
    language: str = "auto",
    response_mode: str = "auto",
    timeout: int = 20,
) -> tuple[dict[str, Any], float, int]:
    t0 = time.time()
    resp = requests.post(
        f"{API_BASE_URL}/api/v1/chat",
        json={
            "message": message,
            "language": language,
            "response_mode": response_mode,
            "history": [],
        },
        timeout=timeout,
    )
    latency = (time.time() - t0) * 1000
    body = {}
    try:
        body = resp.json()
    except Exception:
        body = {}
    return body, latency, resp.status_code


def call_tts(
    text: str, language: str = "hi", timeout: int = 30
) -> tuple[bytes, str, float, int]:
    t0 = time.time()
    resp = requests.post(
        f"{API_BASE_URL}/api/v1/text-to-speech",
        json={"text": text, "language": language, "speed": 1.0},
        timeout=timeout,
    )
    latency = (time.time() - t0) * 1000
    return resp.content, resp.headers.get("content-type", ""), latency, resp.status_code


def call_stt(
    audio_bytes: bytes, language: str = "auto", timeout: int = 40
) -> tuple[dict[str, Any], float, int]:
    t0 = time.time()
    files = {"audio": ("sample.wav", audio_bytes, "audio/wav")}
    data = {"language": language}
    resp = requests.post(
        f"{API_BASE_URL}/api/v1/speech-to-text",
        files=files,
        data=data,
        timeout=timeout,
    )
    latency = (time.time() - t0) * 1000
    body = {}
    try:
        body = resp.json()
    except Exception:
        body = {}
    return body, latency, resp.status_code


def call_sts(
    audio_bytes: bytes, language: str = "auto", timeout: int = 45
) -> tuple[dict[str, Any], float, int]:
    t0 = time.time()
    files = {"audio": ("sample.wav", audio_bytes, "audio/wav")}
    resp = requests.post(
        f"{API_BASE_URL}/api/v1/voice-chat",
        params={"language": language},
        files=files,
        timeout=timeout,
    )
    latency = (time.time() - t0) * 1000
    body = {}
    try:
        body = resp.json()
    except Exception:
        body = {}
    return body, latency, resp.status_code


def print_header() -> None:
    print("\n" + "=" * 96)
    print("Chatbot Full Validation Suite")
    print(f"Target: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 96)


def log(
    status: str, area: str, label: str, detail: str = "", latency: float = 0.0
) -> None:
    suffix = f" {latency:.0f}ms" if latency else ""
    print(f"  {status} [{area:<10}] {label:<52}{suffix}")
    if detail and status in {FAIL, WARN}:
        print(f"       -> {detail[:180]}")


def evaluate_chat_response(body: dict[str, Any]) -> tuple[bool, str]:
    response = str(body.get("response", "")).strip()
    if not response:
        return False, "empty response"
    if len(response) < 25:
        return False, "response too short"
    lower = response.lower()
    if "having trouble connecting" in lower or "try again later" in lower:
        return False, "fallback error response"
    return True, "ok"


def main() -> int:
    print_header()

    results: list[dict[str, Any]] = []
    hard_failures: list[str] = []

    # Category 1: 15 multilingual/service prompts
    category_1 = [
        ("en", "How to apply for a passport renewal in India with timeline and fees?"),
        ("hi", "आधार कार्ड में पता अपडेट करने के लिए कौन-कौन से दस्तावेज़ चाहिए?"),
        ("ta", "பாஸ்போர்ட் விண்ணப்பத்திற்கு தேவையான ஆவணங்கள் என்ன?"),
        ("te", "డ్రైవింగ్ లైసెన్స్ రీన్యువల్ ప్రక్రియ ఏమిటి?"),
        ("bn", "প্যান কার্ড সংশোধনের জন্য কী কী ডকুমেন্ট লাগে?"),
        ("mr", "ईपीएफओ मधून पैसे काढण्यासाठी प्रक्रिया काय आहे?"),
        ("gu", "દિગિલોકરમાં દસ્તાવેજ કેવી રીતે ડાઉનલોડ કરું?"),
        ("kn", "ವೋಟರ್ ಐಡಿ ತಿದ್ದುಪಡಿ ಮಾಡಲು ಏನು ಕ್ರಮ?"),
        ("ml", "റേഷൻ കാർഡ് പുതുക്കാൻ എന്തെല്ലാം വേണം?"),
        ("pa", "ਜਨਮ ਪ੍ਰਮਾਣ ਪੱਤਰ ਲਈ ਅਰਜ਼ੀ ਕਿਵੇਂ ਦੇਈਏ?"),
        ("en", "What are eligibility rules for PM Kisan registration?"),
        ("hi", "ड्राइविंग लाइसेंस टेस्ट स्लॉट बुक कैसे करें?"),
        ("en", "How to check status of an application using ARN?"),
        ("hi", "पासपोर्ट सेवा केंद्र में अपॉइंटमेंट रीशेड्यूल कैसे करें?"),
        ("auto", "Need steps for caste certificate application in Karnataka."),
    ]

    print("\n[1] Multilingual + Services (15 prompts)")
    print("-" * 96)
    c1_latencies: list[float] = []
    for idx, (lang, prompt) in enumerate(category_1, start=1):
        body, ms, status = call_chat(prompt, language=lang, response_mode="auto")
        ok = status == 200
        if ok:
            ok, detail = evaluate_chat_response(body)
        else:
            detail = f"HTTP {status}"

        c1_latencies.append(ms)
        results.append(
            {
                "category": "multilingual_services",
                "index": idx,
                "language": lang,
                "prompt": prompt,
                "status": status,
                "latency_ms": round(ms),
                "ok": ok,
                "detail": detail,
            }
        )
        if ok:
            log(PASS, "C1", f"Prompt #{idx}", latency=ms)
        else:
            hard_failures.append(f"C1:{idx}")
            log(FAIL, "C1", f"Prompt #{idx}", detail, ms)

    # Category 2: 15 non-straightforward real-user prompts
    category_2 = [
        (
            "auto",
            "uhh passport... passport renew karna hai, matlab old one expire ho gaya, what now?",
        ),
        (
            "auto",
            "aadhaar address change... same city but new flat no... how to do, online maybe?",
        ),
        ("auto", "i i i forgot ARN, can i still track application somehow?"),
        (
            "auto",
            "driving licence ka slot slot slot kaise book hota, site pe confuse ho gaya",
        ),
        (
            "auto",
            "PAN correction name spelling wrong... do i need gazette or just proof?",
        ),
        ("auto", "epfo withdrawal, like partial only, not full, any conditions?"),
        ("auto", "voter id transfer city changed, same state maybe, steps plz short"),
        ("auto", "birth certificate old record not found then what what should i do"),
        ("auto", "digilocker login OTP not coming again and again, workaround?"),
        ("auto", "income certificate urgently चाहिए, tatkal type kuch hai kya?"),
        ("auto", "r- ration card add newborn baby ka process?"),
        (
            "auto",
            "scholarship form filled but pending pending at institute level means?",
        ),
        ("auto", "can you tell checklist only no long para for caste cert"),
        ("auto", "sir DL lost ho gaya duplicate chahiye what docs and fee"),
        ("auto", "hello... confused... passport police verification kab hota exactly"),
    ]

    print("\n[2] Ambiguous + Stuttered Real-user Style (15 prompts)")
    print("-" * 96)
    c2_latencies: list[float] = []
    for idx, (lang, prompt) in enumerate(category_2, start=1):
        body, ms, status = call_chat(prompt, language=lang, response_mode="auto")
        ok = status == 200
        if ok:
            ok, detail = evaluate_chat_response(body)
        else:
            detail = f"HTTP {status}"

        c2_latencies.append(ms)
        results.append(
            {
                "category": "messy_real_user",
                "index": idx,
                "language": lang,
                "prompt": prompt,
                "status": status,
                "latency_ms": round(ms),
                "ok": ok,
                "detail": detail,
            }
        )
        if ok:
            log(PASS, "C2", f"Prompt #{idx}", latency=ms)
        else:
            hard_failures.append(f"C2:{idx}")
            log(FAIL, "C2", f"Prompt #{idx}", detail, ms)

    # Category 3: modality checks, 15 prompts each
    modality_prompts = [
        "Passport renewal steps in short.",
        "Aadhaar address update documents list.",
        "How to track application by ARN?",
        "Driving license duplicate process.",
        "PAN card correction fees and steps.",
        "EPFO partial withdrawal conditions.",
        "Voter ID correction online flow.",
        "Birth certificate re-issue procedure.",
        "DigiLocker document download steps.",
        "Income certificate application timeline.",
        "Ration card member addition process.",
        "Scholarship status meaning at institute level.",
        "Caste certificate required documents.",
        "Police verification for passport timeline.",
        "How to reschedule service appointment?",
    ]

    print("\n[3A] TTT (15 prompts)")
    print("-" * 96)
    ttt_latencies: list[float] = []
    for idx, prompt in enumerate(modality_prompts, start=1):
        body, ms, status = call_chat(prompt, language="auto", response_mode="auto")
        ok = status == 200
        if ok:
            ok, detail = evaluate_chat_response(body)
        else:
            detail = f"HTTP {status}"
        ttt_latencies.append(ms)
        results.append(
            {
                "category": "ttt",
                "index": idx,
                "prompt": prompt,
                "status": status,
                "latency_ms": round(ms),
                "ok": ok,
                "detail": detail,
            }
        )
        if ok:
            log(PASS, "TTT", f"Prompt #{idx}", latency=ms)
        else:
            hard_failures.append(f"TTT:{idx}")
            log(FAIL, "TTT", f"Prompt #{idx}", detail, ms)

    print("\n[3B] TTS (15 prompts)")
    print("-" * 96)
    tts_audio_samples: list[bytes] = []
    tts_latencies: list[float] = []
    for idx, prompt in enumerate(modality_prompts, start=1):
        audio, content_type, ms, status = call_tts(prompt, language="en")
        ok = status == 200 and "audio/" in content_type and len(audio) > 1000
        detail = (
            "ok"
            if ok
            else f"HTTP {status}, content-type={content_type}, bytes={len(audio)}"
        )
        tts_latencies.append(ms)
        results.append(
            {
                "category": "tts",
                "index": idx,
                "text": prompt,
                "status": status,
                "latency_ms": round(ms),
                "ok": ok,
                "detail": detail,
                "audio_bytes": len(audio),
            }
        )
        if ok:
            tts_audio_samples.append(audio)
            log(PASS, "TTS", f"Prompt #{idx}", latency=ms)
        else:
            hard_failures.append(f"TTS:{idx}")
            log(FAIL, "TTS", f"Prompt #{idx}", detail, ms)

    print("\n[3C] STT (15 prompts via TTS loopback audio)")
    print("-" * 96)
    stt_latencies: list[float] = []
    stt_pass_count = 0
    for idx, audio in enumerate(tts_audio_samples[:15], start=1):
        body, ms, status = call_stt(audio, language="auto")
        transcript = str(body.get("transcript", "")).strip()
        ok = status == 200 and len(transcript) >= 5
        detail = "ok" if ok else f"HTTP {status}, transcript='{transcript[:80]}'"
        stt_latencies.append(ms)
        results.append(
            {
                "category": "stt",
                "index": idx,
                "status": status,
                "latency_ms": round(ms),
                "ok": ok,
                "detail": detail,
                "transcript": transcript,
            }
        )
        if ok:
            stt_pass_count += 1
            log(PASS, "STT", f"Audio #{idx}", latency=ms)
        else:
            log(WARN, "STT", f"Audio #{idx}", detail, ms)

    if len(tts_audio_samples) < 15:
        hard_failures.append("STT:insufficient_audio")
        log(
            FAIL,
            "STT",
            "Insufficient TTS audio generated",
            f"got {len(tts_audio_samples)} samples",
        )
    elif stt_pass_count < 10:
        hard_failures.append("STT:low_pass_rate")
        log(FAIL, "STT", "Pass rate below threshold", f"pass={stt_pass_count}/15")

    print("\n[3D] STS (15 prompts via TTS loopback audio)")
    print("-" * 96)
    sts_latencies: list[float] = []
    sts_pass_count = 0
    for idx, audio in enumerate(tts_audio_samples[:15], start=1):
        body, ms, status = call_sts(audio, language="auto")
        transcript = str(body.get("transcript", "")).strip()
        response = str(body.get("response", "")).strip()
        audio_b64 = str(body.get("audio_base64", "")).strip()
        ok = (
            status == 200
            and len(transcript) >= 3
            and len(response) >= 20
            and len(audio_b64) >= 20
        )
        detail = (
            "ok"
            if ok
            else f"HTTP {status}, transcript_len={len(transcript)}, response_len={len(response)}, audio_b64_len={len(audio_b64)}"
        )
        sts_latencies.append(ms)
        results.append(
            {
                "category": "sts",
                "index": idx,
                "status": status,
                "latency_ms": round(ms),
                "ok": ok,
                "detail": detail,
                "transcript": transcript,
            }
        )
        if ok:
            sts_pass_count += 1
            log(PASS, "STS", f"Audio #{idx}", latency=ms)
        else:
            log(WARN, "STS", f"Audio #{idx}", detail, ms)

    if len(tts_audio_samples) < 15:
        hard_failures.append("STS:insufficient_audio")
        log(
            FAIL,
            "STS",
            "Insufficient TTS audio generated",
            f"got {len(tts_audio_samples)} samples",
        )
    elif sts_pass_count < 10:
        hard_failures.append("STS:low_pass_rate")
        log(FAIL, "STS", "Pass rate below threshold", f"pass={sts_pass_count}/15")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["ok"])
    failed = total - passed
    overall_p95 = p95([float(r["latency_ms"]) for r in results if r.get("latency_ms")])

    print("\n" + "=" * 96)
    print(f"TOTAL CHECKS: {total}")
    print(f"PASSED      : {passed}")
    print(f"FAILED      : {failed}")
    print(f"OVERALL P95 : {overall_p95:.0f}ms")
    print("=" * 96)

    report = {
        "suite": "chatbot_full",
        "api_base_url": API_BASE_URL,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "overall_p95_ms": round(overall_p95),
            "category_p95_ms": {
                "c1_multilingual_services": round(p95(c1_latencies)),
                "c2_messy_real_user": round(p95(c2_latencies)),
                "ttt": round(p95(ttt_latencies)),
                "tts": round(p95(tts_latencies)),
                "stt": round(p95(stt_latencies)),
                "sts": round(p95(sts_latencies)),
            },
            "stt_pass_rate": f"{stt_pass_count}/15",
            "sts_pass_rate": f"{sts_pass_count}/15",
            "hard_failures": hard_failures,
        },
        "results": results,
    }

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Report saved -> {REPORT_PATH}")
    return 1 if hard_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
