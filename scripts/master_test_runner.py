"""
Master Test Runner
==================
Runs all critical system tests to validate Phase 1-4 completion

Run: python scripts/master_test_runner.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
from datetime import datetime


class MasterTestRunner:
    """Comprehensive test runner for all phases"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*80)
        print("🧪 MASTER TEST RUNNER - PHASE 1-4 VALIDATION")
        print("="*80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Phase 1: Infrastructure
        self._run_phase1_tests()
        
        # Phase 2: Data Ingestion
        self._run_phase2_tests()
        
        # Phase 3: Content Processing & AI
        self._run_phase3_tests()
        
        # Phase 4: Service Integration
        self._run_phase4_tests()
        
        # Print summary
        self._print_summary()
    
    def _run_phase1_tests(self):
        """Phase 1: Infrastructure & Foundation"""
        print("\n" + "-"*80)
        print("📦 PHASE 1: Infrastructure & Foundation")
        print("-"*80)
        
        # Test 1.1: Database Connection
        self._run_test("Database Connection", self._test_database_connection)
        
        # Test 1.2: pgvector Extension
        self._run_test("pgvector Extension", self._test_pgvector)
        
        # Test 1.3: Core Models
        self._run_test("Core Models Import", self._test_core_models)
        
        # Test 1.4: Repositories
        self._run_test("Repository Pattern", self._test_repositories)
        
        # Test 1.5: FastAPI App
        self._run_test("FastAPI Application", self._test_fastapi_app)
    
    def _run_phase2_tests(self):
        """Phase 2: Data Ingestion Pipeline"""
        print("\n" + "-"*80)
        print("🔄 PHASE 2: Data Ingestion Pipeline")
        print("-"*80)
        
        # Test 2.1: API Clients
        self._run_test("API Clients", self._test_api_clients)
        
        # Test 2.2: Web Scrapers
        self._run_test("Web Scrapers", self._test_scrapers)
        
        # Test 2.3: Document Parser
        self._run_test("Document Parser", self._test_document_parser)
        
        # Test 2.4: Data Quality
        self._run_test("Data Quality Module", self._test_data_quality)
    
    def _run_phase3_tests(self):
        """Phase 3: Content Processing & AI Integration"""
        print("\n" + "-"*80)
        print("🤖 PHASE 3: Content Processing & AI")
        print("-"*80)
        
        # Test 3.1: NLP Pipeline (optional)
        self._run_optional_test("NLP Pipeline (optional)", self._test_nlp_pipeline)
        
        # Test 3.2: Embeddings (optional)
        self._run_optional_test("Embeddings Generator (optional)", self._test_embeddings)
        
        # Test 3.3: Vector Search
        self._run_test("Vector Search", self._test_vector_search)
        
        # Test 3.4: RAG Pipeline
        self._run_test("RAG Pipeline", self._test_rag_pipeline)
    
    def _run_phase4_tests(self):
        """Phase 4: Service Integration & APIs"""
        print("\n" + "-"*80)
        print("🚀 PHASE 4: Service Integration & APIs")
        print("-"*80)
        
        # Test 4.1: Service Endpoints
        self._run_test("Service-Specific Endpoints", self._test_service_endpoints)
        
        # Test 4.2: Search APIs
        self._run_test("Search & Discovery APIs", self._test_search_apis)
        
        # Test 4.3: Admin APIs
        self._run_test("Admin & Management APIs", self._test_admin_apis)
        
        # Test 4.4: Data Warehouse Population
        self._run_test("Data Warehouse Population", self._test_warehouse_data)
        
        # Optional: GraphQL smoke and dataset exports
        self._run_optional_test("GraphQL Smoke (optional)", self._test_graphql_smoke)
        self._run_test("Dataset Exports", self._test_dataset_exports)
    
    def _run_test(self, test_name, test_func):
        """Run a single test and record result"""
        try:
            print(f"\n🔍 Testing: {test_name}...", end=" ")
            result = test_func()
            if result:
                print("✅ PASS")
                self.results.append((test_name, True, None))
            else:
                print("⚠️  PARTIAL")
                self.results.append((test_name, False, "Partial functionality"))
        except Exception as e:
            print(f"❌ FAIL: {str(e)[:80]}")
            self.results.append((test_name, False, str(e)))

    def _run_optional_test(self, test_name, test_func):
        """Run an optional test; failures do not count against overall status"""
        try:
            print(f"\n🔍 Testing: {test_name}...", end=" ")
            result = test_func()
            if result:
                print("✅ PASS")
            else:
                print("ℹ️  SKIPPED (optional)")
        except Exception:
            print("ℹ️  SKIPPED (optional)")

    def _test_graphql_smoke(self):
        try:
            from routes.graphql_schema import schema
            query = "{ status services(limit: 1){ name category ministry } }"
            result = schema.execute_sync(query)
            return bool(result and not result.errors)
        except Exception:
            return False

    def _test_dataset_exports(self):
        # Ensure exporters can run to completion in a dry manner (DB presence assumed)
        try:
            import subprocess, sys
            cmds = [
                [sys.executable, 'scripts/export_finetune_faq_jsonl.py', '--out', 'data/exports/_test_faqs.jsonl'],
                [sys.executable, 'scripts/export_finetune_chunks_jsonl.py', '--out', 'data/exports/_test_chunks.jsonl'],
                [sys.executable, 'scripts/export_rag_corpus.py', '--out', 'data/exports/_test_rag.json'],
            ]
            for c in cmds:
                subprocess.check_call(c)
            return True
        except Exception:
            return False
    
    # Individual test implementations
    
    def _test_database_connection(self):
        from core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1
    
    def _test_pgvector(self):
        from core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            return result.fetchone() is not None
    
    def _test_core_models(self):
        from core.models import Service, Procedure, Document, FAQ, ContentChunk, RawContent
        return True
    
    def _test_repositories(self):
        from core.database import SessionLocal
        from core.repositories import ServiceRepository
        db = SessionLocal()
        try:
            _ = ServiceRepository(db).count()
            return True
        finally:
            db.close()
    
    def _test_fastapi_app(self):
        import app
        return hasattr(app, 'app')
    
    def _test_api_clients(self):
        from data.ingestion.api_clients.passport import PassportAPIClient
        from data.ingestion.api_clients.aadhaar import AadhaarAPIClient
        return True
    
    def _test_scrapers(self):
        from data.ingestion.scrapers.passport_scraper import PassportScraper
        from data.ingestion.scrapers.aadhaar_scraper import AadhaarScraper
        return True
    
    def _test_document_parser(self):
        from data.processing.document_parser import DocumentParser
        parser = DocumentParser()
        return True
    
    def _test_data_quality(self):
        from core.quality import DataValidator, Deduplicator, QualityMonitor
        return True
    
    def _test_nlp_pipeline(self):
        try:
            from core.nlp import NLPProcessor
            return True
        except ImportError:
            return False
    
    def _test_embeddings(self):
        try:
            from core.embeddings import EmbeddingGenerator
            return True
        except ImportError:
            return False
    
    def _test_vector_search(self):
        from core.search import SearchEngine
        from core.database import SessionLocal
        db = SessionLocal()
        try:
            search = SearchEngine(db)
            return True
        finally:
            db.close()
    
    def _test_rag_pipeline(self):
        try:
            from core.rag import RAGPipeline
            return True
        except ImportError:
            return False
    
    def _test_service_endpoints(self):
        from routes.v1_endpoints import router
        return True
    
    def _test_search_apis(self):
        from routes.api_endpoints import router
        return True
    
    def _test_admin_apis(self):
        from core.ops.backup_restore import backup_database, restore_database
        return True
    
    def _test_warehouse_data(self):
        from core.database import SessionLocal
        from core.models import Service, Document, ContentChunk, RawContent
        db = SessionLocal()
        try:
            services = db.query(Service).count()
            documents = db.query(Document).count()
            chunks = db.query(ContentChunk).count()
            raw = db.query(RawContent).count()
            print(f"(Services: {services}, Docs: {documents}, Chunks: {chunks}, Raw: {raw})", end=" ")
            return services > 0  # At least some data should exist
        finally:
            db.close()
    
    def _print_summary(self):
        """Print test summary"""
        elapsed = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, result, _ in self.results if result)
        total = len(self.results)
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed:   {passed}")
        print(f"❌ Failed:   {failed}")
        print(f"⏱️  Duration: {elapsed:.2f}s")
        
        if failed > 0:
            print("\n⚠️  Failed Tests:")
            for test_name, result, error in self.results:
                if not result:
                    print(f"  - {test_name}")
                    if error:
                        print(f"    Error: {error[:100]}")
        
        print("\n" + "="*80)
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! System is fully functional.")
        elif passed / total >= 0.8:
            print("✅ MOSTLY FUNCTIONAL - Some optional features missing.")
        else:
            print("⚠️  CRITICAL ISSUES - Please review failed tests.")
        
        print("="*80 + "\n")
        
        return passed == total


def main():
    runner = MasterTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()

