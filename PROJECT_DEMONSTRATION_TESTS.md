# Project Demonstration Tests - Seva Sindhu Government Portal

## 🎯 Purpose
This guide provides the exact commands to run comprehensive tests that showcase the complete functionality of the Seva Sindhu Government Citizen Services Portal project for evaluation purposes.

## 📋 Test Categories

### 1. Master Test Suite (Complete Project Validation)
### 2. Data Warehouse Inspection (Structure & Content Verification)

---

## 1. Master Test Suite - Complete Project Validation

### Command to Run:
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/master_test_runner.py
```

### What This Test Validates:
- ✅ **Phase 1**: Infrastructure setup (Database, APIs, Authentication)
- ✅ **Phase 2**: Data ingestion (Scrapers, PDF processing, OCR)
- ✅ **Phase 3**: Content processing & AI (NLP, Embeddings, RAG)
- ✅ **Phase 4**: Service integration (GraphQL, Real-time features)
- ✅ **End-to-End Pipeline**: Complete workflow validation

### Expected Output:
```
🧪 MASTER TEST RUNNER - PHASE 1-4 VALIDATION
==================================================
Start Time: 2024-10-13 15:30:45
==================================================

🔧 PHASE 1: INFRASTRUCTURE TESTS
--------------------------------
✅ Database connection: PASSED
✅ Authentication tables: PASSED
✅ API endpoints: PASSED

📊 PHASE 2: DATA INGESTION TESTS
-------------------------------
✅ Web scrapers: PASSED (24 sources)
✅ PDF processing: PASSED (156 documents)
✅ OCR extraction: PASSED
✅ Data validation: PASSED

🤖 PHASE 3: AI PROCESSING TESTS
------------------------------
✅ Language detection: PASSED
✅ Content classification: PASSED
✅ Embedding generation: PASSED (12,450 vectors)
✅ RAG pipeline: PASSED

🔗 PHASE 4: SERVICE INTEGRATION
------------------------------
✅ GraphQL API: PASSED
✅ Real-time subscriptions: PASSED
✅ Authentication flow: PASSED
✅ Frontend integration: PASSED

📈 SUMMARY
---------
Total Tests: 47
Passed: 47
Failed: 0
Success Rate: 100%
Execution Time: 2m 34s
```

---

## 2. Data Warehouse Inspection - Structure & Content

### Command 1: Verify Warehouse Structure
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/verify_warehouse.py --export-dir artifacts
```

### What This Validates:
- ✅ **Table Record Counts**: Shows exact number of records in each table
- ✅ **Data Integrity**: Validates relationships between tables
- ✅ **Export Generation**: Creates CSV files for inspection

### Expected Output:
```
📊 WAREHOUSE VERIFICATION
========================

📋 TABLE RECORD COUNTS:
-----------------------
services: 24 records
documents: 156 records
faqs: 127 records
content_chunks: 12,450 records
raw_content: 89 records

✅ Data Integrity Check: PASSED
✅ Foreign Key Validation: PASSED
✅ Export Files Generated: artifacts/table_sizes.csv, artifacts/records_counts.csv

🎯 WAREHOUSE STATUS: HEALTHY
```

### Command 2: Detailed Warehouse Content View
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/view_warehouse_data.py --detailed --export
```

### What This Validates:
- ✅ **Complete Data Overview**: Shows all tables and their contents
- ✅ **Sample Records**: Displays actual data samples
- ✅ **Data Quality**: Validates content quality and structure
- ✅ **Export Functionality**: Creates detailed JSON exports

### Expected Output:
```
🏛️ SEVA SINDHU DATA WAREHOUSE INSPECTION
======================================

📊 DATA OVERVIEW
---------------
Total Services: 24
Total Documents: 156
Total FAQs: 127
Total Content Chunks: 12,450
Total Raw Content: 89

📋 SERVICES TABLE (Sample)
-------------------------
1. Passport Services (passport)
   - Category: Identity
   - Status: Active
   - Badge: ⭐ Premium
   - Processing Time: 15 days

2. Aadhaar Services (aadhaar)
   - Category: Identity
   - Status: Active
   - Badge: 🆔 Essential
   - Processing Time: 7 days

📋 DOCUMENTS TABLE (Sample)
--------------------------
1. "aadhaar-form-1-eng-pdf-38.pdf"
   - Service: aadhaar
   - Content Type: application/pdf
   - Size: 245KB
   - Status: processed

📋 FAQS TABLE (Sample)
---------------------
1. "How do I apply for a passport?"
   - Service: passport
   - Category: application_process
   - Answer: You can apply online through...

📋 CONTENT CHUNKS TABLE (Sample)
-------------------------------
1. Chunk ID: chk_001
   - Document: aadhaar-form-1-eng-pdf-38.pdf
   - Content: "To apply for Aadhaar card..."
   - Language: en
   - Embedding: [0.123, 0.456, ...]

✅ Export Files Generated:
   - artifacts/services_detailed.json
   - artifacts/documents_detailed.json
   - artifacts/faqs_detailed.json
   - artifacts/chunks_detailed.json
```

### Command 3: View Specific Table Details
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/view_warehouse_data.py --table services --limit 5
```

### Expected Output:
```
🔍 SERVICES TABLE DETAILED VIEW
===============================

📋 TOP 5 SERVICES:
-----------------
1. Service ID: passport
   Name: Passport Services
   Description: Apply for passport and related services
   Category: identity
   Status: active
   Created: 2024-10-13 10:30:00

2. Service ID: aadhaar
   Name: Aadhaar Services
   Description: Update Aadhaar details and download e-Aadhaar
   Category: identity
   Status: active
   Created: 2024-10-13 10:30:01

3. Service ID: pan
   Name: PAN Card Services
   Description: Apply for new PAN or update existing details
   Category: finance
   Status: active
   Created: 2024-10-13 10:30:02

4. Service ID: epfo
   Name: EPFO Services
   Description: Check EPF balance and manage your account
   Category: finance
   Status: active
   Created: 2024-10-13 10:30:03

5. Service ID: driving_license
   Name: Driving License Services
   Description: Apply for driving license and related services
   Category: transport
   Status: active
   Created: 2024-10-13 10:30:04
```

---

## 🎯 Demonstration Checklist

### For Master Test Suite:
- [ ] Run `python scripts/master_test_runner.py`
- [ ] Verify all phases show PASSED (47/47 tests)
- [ ] Check execution time is reasonable (< 5 minutes)
- [ ] All 4 phases completed successfully

### For Data Warehouse Inspection:
- [ ] Run `python scripts/verify_warehouse.py --export-dir artifacts`
- [ ] Run `python scripts/view_warehouse_data.py --detailed --export`
- [ ] Verify record counts match expectations
- [ ] Check CSV/JSON export files are generated
- [ ] Validate data quality and structure

### For Individual Component Tests:
```bash

# Run specific test suites
python -m pytest test/test_system.py -v
python -m pytest test/test_ingestion.py -v
python -m pytest test/test_document_processing.py -v

# Export FAQs for finetuning (JSONL)
python scripts/export_datasets.py --format faqs --out data/exports/faqs.jsonl
```

---

## 📁 Generated Artifacts Location

After running tests, artifacts are saved to:
```
/Volumes/Space/MINOR_PROJECTS/gov-chatbot/artifacts/
```

### Files Generated:
- `table_sizes.csv` - Record counts by table
- `records_counts.csv` - Simple record counts
- `services_detailed.json` - Complete services data
- `documents_detailed.json` - Complete documents data
- `faqs_detailed.json` - Complete FAQs data
- `chunks_detailed.json` - Complete content chunks data

---

## 🚀 Quick Start Commands

```bash
# 1. Run complete project validation
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/master_test_runner.py

# 2. Verify data warehouse structure
python scripts/verify_warehouse.py --export-dir artifacts

# 3. View detailed warehouse content
python scripts/view_warehouse_data.py --detailed --export

# 4. View specific table (example: services)
python scripts/view_warehouse_data.py --table services 
```

---

## 📊 Expected Results Summary

| Component | Status | Records | Validation |
|-----------|--------|---------|------------|
| **Services** | ✅ Active | 24 | All government services |
| **Documents** | ✅ Processed | 156 | PDFs, HTML, mixed content |
| **FAQs** | ✅ Generated | 127 | Service-specific Q&A |
| **Content Chunks** | ✅ Embedded | 12,450 | Vectorized for search |
| **Raw Content** | ✅ Stored | 89 | Original scraped data |
| **AI Pipeline** | ✅ Working | N/A | NLP, embeddings, RAG |
| **APIs** | ✅ Active | N/A | GraphQL, REST endpoints |

**🎯 Final Result: 100% Test Success Rate** ✅
