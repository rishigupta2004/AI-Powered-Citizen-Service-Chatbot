"""
RAG Evaluation Suite — 15 test questions across 5 service categories.
Target: 85%+ retrieval accuracy (at least 1 relevant result in top-3).
Run: python scripts/eval_rag.py
"""

import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.database import SessionLocal
from core.search import SearchEngine

TEST_CASES = [
    # (query, expected_keyword_in_result)
    ("passport application form", "passport"),
    ("documents required for passport", "passport"),
    ("tatkal passport processing time", "tatkal"),
    ("pan card apply online", "pan"),
    ("pan card lost reissue", "pan"),
    ("aadhaar update address", "aadhaar"),
    ("driving license renewal", "driving"),
    ("voter id registration", "voter"),
    ("ration card apply", "ration"),
    ("birth certificate municipal", "birth"),
    ("income certificate state government", "income"),
    ("caste certificate obc sc st", "caste"),
    ("epfo pf withdrawal", "provident"),
    ("gst registration business", "gst"),
    ("property registration stamp duty", "property"),
]


def run_eval():
    db = SessionLocal()
    engine = SearchEngine(db)
    passed = 0
    for query, keyword in TEST_CASES:
        results = engine.search(query, limit=3)
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
    db.close()


if __name__ == "__main__":
    run_eval()
