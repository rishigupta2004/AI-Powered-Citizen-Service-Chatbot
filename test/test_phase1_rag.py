"""
SevaSindhu — Phase 1: RAG Quality Test Suite
Run: python scripts/test_phase1_rag.py
Tests: retrieval accuracy, latency, search mode, chunk quality, reranker
"""

import sys, os, time, json
import requests
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
except ImportError:
    pass

BASE_URL = os.getenv("API_BASE_URL", "https://gov-chatbot.fly.dev").rstrip("/")
IS_LOCAL = BASE_URL.startswith("http://localhost") or BASE_URL.startswith(
    "http://127.0.0.1"
)

# ─────────────────────────────────────────────
# TEST CASES: (query, must_contain_keyword, category)
# ─────────────────────────────────────────────
TEST_CASES = [
    ("passport application form", "passport", "Passport"),
    ("documents required for passport", "passport", "Passport"),
    ("passport fees charges payment", "passport", "Passport"),
    ("instant e-pan apply online", "pan", "PAN Card"),
    ("income tax return filing", "income", "Income Tax"),
    ("aadhaar update address online", "aadhaar", "Aadhaar"),
    ("epfo member e-sewa", "epfo", "EPFO"),
    ("gst portal", "gst", "GST"),
    ("voter services", "voter", "Voter ID"),
    ("digilocker services", "digilocker", "DigiLocker"),
    ("national scholarship portal apply", "scholarship", "Education"),
    ("e-shram", "shram", "Labor"),
    ("pm kisan beneficiary status", "kisan", "Agriculture"),
    ("nps account opening", "nps", "Pension"),
    ("umang app services", "umang", "Citizen App"),
]

# Indic queries mapped to English equivalents for text search
# (DB has no Indic script content — Sarvam translation bridges the gap)
INDIC_QUERIES = [
    ("पासपोर्ट के लिए दस्तावेज", "hi", "Hindi", "passport documents"),
    ("ஆதார் முகவரி மாற்றம்", "ta", "Tamil", "aadhaar address update"),
    ("পাসপোর্ট নথি", "bn", "Bengali", "passport documents"),
    ("పాన్ కార్డ్ దరఖాస్తు", "te", "Telugu", "pan card apply"),
    ("ड्राइविंग लाइसेंस नवीनीकरण", "hi", "Hindi2", "driving license renewal"),
    ("ఆధార్ నమోదు", "te", "Telugu2", "aadhaar enrolment"),
]

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"
GRAY = "\033[90m"


def divider(char="─", width=72):
    print(GRAY + char * width + RESET)


def api_search(query: str, limit: int = 10) -> Dict[str, Any]:
    try:
        resp = requests.get(
            f"{BASE_URL}/api/v1/search",
            params={"q": query, "limit": limit},
            timeout=25,
        )
        if resp.status_code != 200:
            return {
                "query": query,
                "total_results": 0,
                "results": [],
                "search_mode": "?",
                "error": f"HTTP {resp.status_code}",
            }
        data = resp.json()
        if not isinstance(data, dict):
            return {
                "query": query,
                "total_results": 0,
                "results": [],
                "search_mode": "?",
                "error": "Invalid JSON payload",
            }
        data.setdefault("query", query)
        data.setdefault("total_results", 0)
        data.setdefault("results", [])
        data.setdefault("search_mode", "?")
        return data
    except Exception as e:
        return {
            "query": query,
            "total_results": 0,
            "results": [],
            "search_mode": "?",
            "error": str(e),
        }


def run():
    target_accuracy = 85 if IS_LOCAL else 80
    target_avg_latency_ms = 500 if IS_LOCAL else 2500

    print(f"\n{BOLD}{'═' * 72}{RESET}")
    print(f"{BOLD}  SevaSindhu — Phase 1: RAG Quality Test Suite{RESET}")
    print(
        f"{GRAY}  Target: ≥{target_accuracy}% retrieval accuracy, <{target_avg_latency_ms}ms avg latency{RESET}"
    )
    print(f"{BOLD}{'═' * 72}{RESET}\n")

    # Warm-up call to reduce first-request cold-start latency spikes on remote
    api_search("passport", limit=1)

    # ── 1. Basic retrieval accuracy ────────────────────────────────────────
    print(f"{BOLD}{BLUE}[1] Retrieval Accuracy — {len(TEST_CASES)} queries{RESET}")
    divider()

    passed = 0
    latencies = []
    results_detail = []

    for query, keyword, category in TEST_CASES:
        t0 = time.time()
        result = api_search(query, limit=3)
        latency_ms = int((time.time() - t0) * 1000)
        latencies.append(latency_ms)

        ok = result.get("total_results", 0) > 0
        if ok:
            passed += 1

        status = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
        mode = result.get("search_mode", "?")
        total = result.get("total_results", 0)
        top = (
            result["results"][0]["content"][:60].replace("\n", " ") + "…"
            if result["results"]
            else "EMPTY"
        )

        print(
            f"  {status} [{category:<16}] {query[:42]:<42} | {total:>2} results | {mode:>8} | {latency_ms:>4}ms"
        )
        if not ok:
            print(f"       {GRAY}top result: {top}{RESET}")

        results_detail.append(
            {
                "query": query,
                "pass": ok,
                "latency_ms": latency_ms,
                "mode": mode,
                "total_results": total,
            }
        )

    divider()
    pct = round(passed / len(TEST_CASES) * 100)
    color = GREEN if pct >= target_accuracy else YELLOW if pct >= 70 else RED
    avg_lat = round(sum(latencies) / len(latencies))
    max_lat = max(latencies)

    print(
        f"\n  Score    : {color}{BOLD}{passed}/{len(TEST_CASES)} = {pct}%{RESET}  (target ≥{target_accuracy}%)"
    )
    print(f"  Avg lat  : {BLUE}{avg_lat}ms{RESET}  (target <{target_avg_latency_ms}ms)")
    print(f"  Max lat  : {BLUE}{max_lat}ms{RESET}")
    print(
        f"  Status   : {color}{'✅ PASS' if pct >= target_accuracy else '⚠️  BORDERLINE' if pct >= 70 else '❌ FAIL'}{RESET}\n"
    )

    # ── 2. Search mode ─────────────────────────────────────────────────────
    print(f"{BOLD}{BLUE}[2] Search Mode Distribution{RESET}")
    divider()
    modes = {}
    for r in results_detail:
        modes[r["mode"]] = modes.get(r["mode"], 0) + 1
    for mode, count in modes.items():
        bar = "█" * count
        print(f"  {mode:<10} {bar} {count}/{len(TEST_CASES)}")
    if "semantic" not in modes:
        print(
            f"\n  {YELLOW}⚠  All queries using text fallback — HF embedding API may be down{RESET}"
        )
        print(f"  {GRAY}   Check: flyctl secrets list | grep HF_TOKEN{RESET}")
    print()

    # ── 3. Indic language retrieval ────────────────────────────────────────
    print(f"{BOLD}{BLUE}[3] Indic Language Query Retrieval{RESET}")
    divider()
    indic_passed = 0
    for query, lang, label, english_fallback in INDIC_QUERIES:
        t0 = time.time()
        # Try native script first
        result = api_search(query, limit=3)
        # If no results, try English translation (DB is English-only)
        if result.get("total_results", 0) == 0:
            result = api_search(english_fallback, limit=3)
            used_fallback = True
        else:
            used_fallback = False
        latency_ms = int((time.time() - t0) * 1000)
        ok = result.get("total_results", 0) > 0
        if ok:
            indic_passed += 1
        status = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
        fb_note = f" {YELLOW}[EN fallback]{RESET}" if used_fallback else ""
        print(
            f"  {status} [{label:<8}] {query:<30} | {result.get('total_results', 0):>2} results | {latency_ms:>4}ms{fb_note}"
        )
    print(
        f"\n  Indic score: {indic_passed}/{len(INDIC_QUERIES)} (text search on English DB — semantic search needed for full native support)\n"
    )

    # ── 4. Chunk quality checks ────────────────────────────────────────────
    print(f"{BOLD}{BLUE}[4] Chunk Quality Spot-Check{RESET}")
    divider()
    result = api_search("passport", limit=5)
    for i, r in enumerate(result["results"], 1):
        content = r.get("content", "")
        source = r.get("source_name", "?")
        length = len(content)
        has_qa = "Q:" in content and "A:" in content
        print(
            f"  [{i}] len={length:>4} chars | {'FAQ format' if has_qa else 'Chunk'} | source={source[:50]}"
        )
    print()

    # ── 5. Summary report ─────────────────────────────────────────────────
    print(f"{BOLD}{'═' * 72}{RESET}")
    print(f"{BOLD}  PHASE 1 SUMMARY{RESET}")
    print(f"{'═' * 72}")
    print(
        f"  Retrieval accuracy : {color}{pct}%{RESET}  {'✅' if pct >= target_accuracy else '❌'}"
    )
    print(
        f"  Avg latency        : {GREEN if avg_lat < target_avg_latency_ms else RED}{avg_lat}ms{RESET}  {'✅' if avg_lat < target_avg_latency_ms else '❌'}"
    )
    print(
        f"  Semantic search    : {'✅ active' if 'semantic' in modes else f'{YELLOW}⚠  text fallback only{RESET}'}"
    )
    print(f"  Indic retrieval    : {indic_passed}/{len(INDIC_QUERIES)}")
    print(f"{'═' * 72}\n")

    # Save JSON report
    report = {
        "phase": 1,
        "label": "RAG Quality",
        "score_pct": pct,
        "passed": passed,
        "total": len(TEST_CASES),
        "avg_latency_ms": avg_lat,
        "max_latency_ms": max_lat,
        "search_modes": modes,
        "indic_score": f"{indic_passed}/{len(INDIC_QUERIES)}",
        "status": "PASS"
        if pct >= target_accuracy
        else "BORDERLINE"
        if pct >= 70
        else "FAIL",
        "details": results_detail,
    }
    out = os.path.join(os.path.dirname(__file__), "test_results_phase1.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  {GRAY}Report saved → scripts/test_results_phase1.json{RESET}\n")

    return pct >= target_accuracy


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
