"""
Phase 4 Week 9 Tests - Vectors & Embeddings
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_pgvector_config():
    try:
        from core.embeddings import configure_pgvector
        ok = configure_pgvector()
        print(f"✅ pgvector extension available: {ok}")
        return ok is True
    except Exception as e:
        print(f"❌ pgvector config failed: {e}")
        return False

def test_embedding_pipeline():
    try:
        from core.embeddings import embedding_generation_pipeline
        vecs = embedding_generation_pipeline(["test text"])
        assert isinstance(vecs, list) and len(vecs) == 1 and isinstance(vecs[0], list)
        print("✅ Embedding pipeline generated vectors")
        return True
    except Exception as e:
        print(f"❌ Embedding pipeline failed: {e}")
        return False

def test_vector_search_wrapper():
    try:
        from core.database import SessionLocal
        from core.embeddings import vector_similarity_search
        db = SessionLocal()
        res = vector_similarity_search(db, "passport", limit=1)
        assert isinstance(res, dict) and "results" in res
        print("✅ Vector search wrapper works")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Vector search wrapper failed: {e}")
        return False

def test_index_optimization():
    try:
        from core.embeddings import optimize_vector_indexing
        ok = optimize_vector_indexing()
        print(f"✅ Vector index optimization: {ok}")
        return ok is True
    except Exception as e:
        print(f"❌ Index optimization failed: {e}")
        return False

def test_multilingual_model_support():
    try:
        from core.embeddings import ensure_multilingual_model
        name = ensure_multilingual_model()
        assert isinstance(name, str) and len(name) > 0
        print(f"✅ Multilingual model configured: {name}")
        return True
    except Exception as e:
        print(f"❌ Multilingual model support failed: {e}")
        return False

def main():
    print("🧪 Testing Week 9 Vectors & Embeddings...")
    tests = [
        ("pgvector Config", test_pgvector_config),
        ("Embedding Pipeline", test_embedding_pipeline),
        ("Vector Search Wrapper", test_vector_search_wrapper),
        ("Index Optimization", test_index_optimization),
        ("Multilingual Model Support", test_multilingual_model_support),
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