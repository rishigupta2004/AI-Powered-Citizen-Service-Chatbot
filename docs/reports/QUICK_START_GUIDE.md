# 🚀 Quick Start Guide

## Prerequisites
- Python 3.10+
- PostgreSQL 15+ with pgvector extension
- DBeaver (optional, for database management)

## Step-by-Step Setup

### 1. Database Setup

```bash
# Create database (if not exists)
createdb gov_chatbot_db

# Enable pgvector extension via psql
psql -d gov_chatbot_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d gov_chatbot_db -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

### 2. Environment Setup

```bash
# Navigate to project
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export DATABASE_URL="postgresql://yourusername:password@localhost/gov_chatbot_db"
export API_KEY="your-secret-api-key"  # Optional
```

### 3. Initialize Database

```bash
# Create tables and seed initial services
python init_db.py
```

Expected output:
```
🚀 Initializing database...
✅ Tables created successfully
✅ Created service: Passport Services
✅ Created service: Aadhaar Services
...
✅ Database initialized successfully
```

### 4. Ingest All Data

```bash
# Load scraped data and PDFs into warehouse
python scripts/comprehensive_data_ingestion.py
```

This will:
- Create 8 base government service categories
- Ingest 19 scraped JSON files from `data/cache/scrapers/`
- Process 60+ PDF documents from `data/docs/`
- Create content chunks for search
- Store everything in the data warehouse

Expected output:
```
🚀 Starting comprehensive data ingestion...
📋 Ensuring base services exist...
✅ Created service: Driving License Services
...
🕷️  Ingesting scraped web content...
✅ Ingested 19 scraped files
📄 Ingesting PDF documents...
Processing: passport-annexurea-pdf-17.pdf
...
✅ Ingested 60+ PDF files
📊 DATA INGESTION SUMMARY
Services created:       4
Scraped files:          19
PDF files processed:    60+
Documents created:      60+
Content chunks created: 500+
Raw content entries:    80+
```

### 5. Validate Data

```bash
# View warehouse contents
python scripts/view_warehouse_data.py

# For detailed output with samples
python scripts/view_warehouse_data.py --detailed

# To export data to JSON
python scripts/view_warehouse_data.py --export
```

### 6. Run Tests

```bash
# Master test runner (validates all Phase 1-4)
python scripts/master_test_runner.py

# Individual test suites
python test/test_system.py
python test/system_pipeline_tests.py
python test/test_document_processing.py
```

Expected: All or most tests should pass (95%+)

### 7. Start API Server

```bash
# Development mode with auto-reload
uvicorn app:app --reload

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

### 8. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List services
curl http://localhost:8000/api/v1/discovery/services

# Search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "passport application", "limit": 5}'

# Get passport procedures
curl http://localhost:8000/api/v1/passport/procedures

# System health (admin)
curl http://localhost:8000/api/v1/admin/system-health
```

---

## Database Validation (Using DBeaver or psql)

### Using DBeaver

1. Open DBeaver
2. Connect to `gov_chatbot_db`
3. Run these queries:

```sql
-- View all services
SELECT * FROM services;

-- Count records in each table
SELECT 'services' as table_name, COUNT(*) as count FROM services
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'content_chunks', COUNT(*) FROM content_chunks
UNION ALL
SELECT 'raw_content', COUNT(*) FROM raw_content;

-- View raw content by source type
SELECT source_type, COUNT(*) as count
FROM raw_content
GROUP BY source_type;
```

### Using psql

```bash
# Run comprehensive SQL validation
psql -d gov_chatbot_db -f scripts/validate_warehouse.sql
```

---

## Troubleshooting

### Issue: Database connection fails
**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL
echo $DATABASE_URL

# Try direct connection
psql -d gov_chatbot_db
```

### Issue: pgvector extension not found
**Solution:**
```bash
# Install pgvector
brew install pgvector  # macOS
# or
sudo apt-get install postgresql-15-pgvector  # Linux

# Enable in database
psql -d gov_chatbot_db -c "CREATE EXTENSION vector;"
```

### Issue: PDF parsing fails
**Solution:**
```bash
# Install OCR dependencies
brew install tesseract  # macOS
# or
sudo apt-get install tesseract-ocr  # Linux

# Verify installation
tesseract --version
```

### Issue: Import errors
**Solution:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

---

## Next Steps

1. **Explore the API**
   - Visit `http://localhost:8000/docs` for interactive API documentation
   - Try different search queries
   - Test service-specific endpoints

2. **Add More Data**
   - Place new PDFs in `data/docs/{service_category}/`
   - Run ingestion script again
   - Data will be automatically processed

3. **Monitor System**
   - Check `/api/v1/admin/system-health` for system status
   - Use `/api/v1/admin/quality` for data quality metrics
   - View `/api/v1/admin/analytics` for usage analytics

4. **Backup Data**
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/backup
   ```

5. **Production Deployment**
   - Review `PHASE_4_COMPLETION_REPORT.md` for deployment checklist
   - Configure environment variables for production
   - Set up monitoring and logging

---

## Quick Reference

| Task | Command |
|------|---------|
| Initialize DB | `python init_db.py` |
| Ingest Data | `python scripts/comprehensive_data_ingestion.py` |
| View Data | `python scripts/view_warehouse_data.py` |
| Run Tests | `python scripts/master_test_runner.py` |
| Start Server | `uvicorn app:app --reload` |
| Validate DB | `psql -d gov_chatbot_db -f scripts/validate_warehouse.sql` |

---

## Support

For issues or questions:
1. Check `PHASE_4_COMPLETION_REPORT.md` for detailed system documentation
2. Review test output for specific error messages
3. Check database logs for connection issues
4. Verify all dependencies are installed correctly

**Happy Building! 🚀**

