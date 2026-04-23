"""
RAG Evaluation Suite — 15 test questions across 5 service categories.
Target: 85%+ retrieval accuracy (at least 1 relevant result in top-3).
Run: python scripts/eval_rag.py
"""

import os
import requests

TEST_CASES = [
    # (query, expected_keyword_in_result)
    ("passport application form", "passport"),
    ("documents required for passport", "passport"),
    ("tatkal passport processing time", "passport"),
    ("instant e-pan apply online", "pan"),
    ("income tax return filing", "income"),
    ("aadhaar update address", "aadhaar"),
    ("epfo member e-sewa", "epfo"),
    ("gst portal", "gst"),
    ("voter services", "voter"),
    ("digilocker services", "digilocker"),
    ("national scholarship portal apply", "scholarship"),
    ("e-shram", "shram"),
    ("pm kisan beneficiary status", "kisan"),
    ("nps account opening", "nps"),
    ("umang app services", "umang"),
]


API_BASE_URL = os.getenv("API_BASE_URL", "https://gov-chatbot.fly.dev").rstrip("/")


def api_search(query: str, limit: int = 3) -> dict:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/search",
        params={"q": query, "limit": limit},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        return {"total_results": 0, "results": []}
    payload.setdefault("total_results", 0)
    payload.setdefault("results", [])
    return payload


def run_eval():
    passed = 0
    for query, keyword in TEST_CASES:
        results = api_search(query, limit=3)
        hits = [
            r
            for r in results["results"]
            if keyword.lower() in r.get("content", "").lower()
        ]
        status = "PASS" if hits else "FAIL"
        if hits:
            passed += 1
        top = results["results"][0]["content"][:50] if results["results"] else "EMPTY"
        print(f"{status} | {query:<40} | {top}")
    print(
        f"\nScore: {passed}/{len(TEST_CASES)} = {passed / len(TEST_CASES) * 100:.0f}%"
    )


if __name__ == "__main__":
    run_eval()
