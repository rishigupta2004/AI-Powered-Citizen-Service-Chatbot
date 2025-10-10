"""
Phase 4 Week 11 Tests - Search & Query Processing
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_hybrid_search():
    try:
        from core.database import SessionLocal
        from core.query import hybrid_search
        db = SessionLocal()
        res = hybrid_search(db, "passport renewal", limit=5)
        assert isinstance(res, dict) and "results" in res
        print("✅ Hybrid search works")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")
        return False

def test_query_understanding():
    try:
        from core.query import query_understanding
        meta = query_understanding("Aadhaar update procedure")
        assert isinstance(meta, dict) and "intent" in meta and "entities" in meta
        print("✅ Query understanding works")
        return True
    except Exception as e:
        print(f"❌ Query understanding failed: {e}")
        return False

def test_multilingual_query_processing():
    try:
        from core.query import multilingual_query_processing
        info = multilingual_query_processing("पासपोर्ट आवेदन")
        assert isinstance(info, dict) and "language" in info
        print("✅ Multilingual query processing works")
        return True
    except Exception as e:
        print(f"❌ Multilingual query processing failed: {e}")
        return False

def test_result_ranking_and_filtering():
    try:
        from core.query import rank_and_filter
        ranked = rank_and_filter([
            {"similarity": 0.2, "source": "document"},
            {"similarity": 0.9, "source": "faq"}
        ])
        assert ranked[0]["similarity"] >= ranked[-1]["similarity"]
        filtered = rank_and_filter(ranked, category="faq")
        assert all(r["source"] == "faq" for r in filtered)
        print("✅ Result ranking and filtering works")
        return True
    except Exception as e:
        print(f"❌ Ranking and filtering failed: {e}")
        return False

def test_search_analytics():
    try:
        from core.query import log_query, get_query_logs
        log_query("passport status", {"user": "test"})
        logs = get_query_logs()
        assert isinstance(logs, list) and len(logs) >= 1
        print("✅ Search analytics logging works")
        return True
    except Exception as e:
        print(f"❌ Search analytics failed: {e}")
        return False

def main():
    print("🧪 Testing Week 11 Search & Query Processing...")
    tests = [
        ("Hybrid Search", test_hybrid_search),
        ("Query Understanding", test_query_understanding),
        ("Multilingual Query Processing", test_multilingual_query_processing),
        ("Result Ranking & Filtering", test_result_ranking_and_filtering),
        ("Search Analytics", test_search_analytics),
    ]
    passed = 0
    for name, fn in tests:
        print(f"\n🔍 Running {name}...")
        if fn():
            passed += 1
        else:
            print(f"❌ {name} failed")
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)