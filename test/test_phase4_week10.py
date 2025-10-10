"""
Phase 4 Week 10 Tests - RAG Pipeline
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_rag_architecture():
    try:
        from core.rag import RAGPipeline
        rag = RAGPipeline()
        assert rag.search and rag.nlp
        print("✅ RAG architecture initialized")
        return True
    except Exception as e:
        print(f"❌ RAG architecture failed: {e}")
        return False

def test_context_retrieval():
    try:
        from core.rag import RAGPipeline
        rag = RAGPipeline()
        ctx = rag.retrieve_context("passport application", top_k=2)
        assert isinstance(ctx, list)
        print("✅ Context retrieval works")
        return True
    except Exception as e:
        print(f"❌ Context retrieval failed: {e}")
        return False

def test_response_generation():
    try:
        from core.rag import RAGPipeline
        rag = RAGPipeline()
        resp = rag.generate_response("passport application", [])
        assert isinstance(resp, dict) and "answer" in resp
        print("✅ Response generation works")
        return True
    except Exception as e:
        print(f"❌ Response generation failed: {e}")
        return False

def test_citations_tracking():
    try:
        from core.rag import RAGPipeline
        rag = RAGPipeline()
        resp = rag.generate_response("passport application", [{"source": "document", "service_id": 1}])
        assert len(resp.get("citations", [])) >= 1
        print("✅ Citation tracking works")
        return True
    except Exception as e:
        print(f"❌ Citation tracking failed: {e}")
        return False

def test_answer_quality_scoring():
    try:
        from core.rag import RAGPipeline
        rag = RAGPipeline()
        resp = rag.ask("passport application")
        assert 0.0 <= resp.get("score", 0) <= 1.0
        print("✅ Answer quality scoring works")
        return True
    except Exception as e:
        print(f"❌ Answer quality scoring failed: {e}")
        return False

def main():
    print("🧪 Testing Week 10 RAG pipeline...")
    tests = [
        ("RAG Architecture", test_rag_architecture),
        ("Context Retrieval", test_context_retrieval),
        ("Response Generation", test_response_generation),
        ("Citation Tracking", test_citations_tracking),
        ("Answer Quality Scoring", test_answer_quality_scoring),
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