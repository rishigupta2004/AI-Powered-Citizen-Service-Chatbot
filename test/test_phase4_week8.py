"""
Phase 4 Week 8 Tests - NLP Pipeline
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_language_detection():
    try:
        from core.nlp import NLPToolkit
        lang = NLPToolkit().language_detection("पासपोर्ट आवेदन की जानकारी")
        print(f"✅ Language detection: {lang}")
        return True
    except Exception as e:
        print(f"❌ Language detection failed: {e}")
        return False

def test_entity_extraction():
    try:
        from core.nlp import NLPToolkit
        entities = NLPToolkit().entity_extraction("Passport application requires Aadhaar and PAN details")
        assert "passport" in entities
        print(f"✅ Entity extraction: {entities}")
        return True
    except Exception as e:
        print(f"❌ Entity extraction failed: {e}")
        return False

def test_content_classification():
    try:
        from core.nlp import NLPToolkit
        label = NLPToolkit().content_classification("Passport application procedure and documents")
        print(f"✅ Content classification: {label}")
        return True
    except Exception as e:
        print(f"❌ Content classification failed: {e}")
        return False

def test_relationship_extraction():
    try:
        from core.nlp import NLPToolkit
        rels = NLPToolkit().relationship_extraction("Passport services are under Ministry of External Affairs")
        assert any(r.get("from") == "passport" for r in rels)
        print(f"✅ Relationship extraction: {rels}")
        return True
    except Exception as e:
        print(f"❌ Relationship extraction failed: {e}")
        return False

def test_summarization():
    try:
        from core.nlp import NLPToolkit
        summary = NLPToolkit().summarization("Passport applications are processed online. Applicants must provide Aadhaar.")
        print(f"✅ Summarization: {summary}")
        return True
    except Exception as e:
        print(f"❌ Summarization failed: {e}")
        return False

def main():
    print("🧪 Testing Week 8 NLP pipeline...")
    tests = [
        ("Language Detection", test_language_detection),
        ("Entity Extraction", test_entity_extraction),
        ("Content Classification", test_content_classification),
        ("Relationship Extraction", test_relationship_extraction),
        ("Summarization", test_summarization),
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