# FAQ Extraction Guide - Parallel Mode

## Overview
This guide explains how to extract FAQs from all government service scrapers in parallel, avoiding the issue where running them sequentially causes timeouts or interruptions.

## Problem Solved
Previously, running all scrapers together in one script caused:
- Long execution times (15+ minutes)
- Timeouts on slow government websites
- Process interruptions
- Only Passport FAQs were extracted before timeout

## Solution: Parallel Execution
We've created individual scripts for each scraper that can run simultaneously in separate processes.

---

## Quick Start

### Method 1: Automatic Parallel Extraction (Recommended)
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
./scripts/extract_all_faqs_parallel.sh
```

This will:
1. Start all 4 scrapers in background
2. Show process IDs
3. Save logs to `artifacts/faq_extraction_*.log`
4. Wait for all to complete
5. Show final status

**Estimated Time:** 5-10 minutes (parallel)

---

### Method 2: Manual Terminal-by-Terminal

Open 4 separate terminals and run one command in each:

**Terminal 1 - Aadhaar:**
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/extract_faq_aadhaar.py | tee artifacts/faq_extraction_aadhaar.log
```

**Terminal 2 - PAN:**
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/extract_faq_pan.py | tee artifacts/faq_extraction_pan.log
```

**Terminal 3 - EPFO:**
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/extract_faq_epfo.py | tee artifacts/faq_extraction_epfo.log
```

**Terminal 4 - Parivahan:**
```bash
cd /Volumes/Space/MINOR_PROJECTS/gov-chatbot
python scripts/extract_faq_parivahan.py | tee artifacts/faq_extraction_parivahan.log
```

---

## Monitoring Progress

### Real-time Monitoring
```bash
./scripts/monitor_faq_extraction.sh
```

This shows:
- Active extraction processes
- Recent log entries from each scraper
- Current FAQ count in database
- FAQs by category

### Live Log Viewing
To watch a specific scraper's progress:
```bash
# Aadhaar
tail -f artifacts/faq_extraction_aadhaar.log

# PAN
tail -f artifacts/faq_extraction_pan.log

# EPFO
tail -f artifacts/faq_extraction_epfo.log

# Parivahan
tail -f artifacts/faq_extraction_parivahan.log
```

Press `Ctrl+C` to stop viewing.

---

## Scripts Created

### Individual Extraction Scripts
1. **`scripts/extract_faq_aadhaar.py`** - UIDAI/Aadhaar FAQs
2. **`scripts/extract_faq_pan.py`** - PAN Card FAQs  
3. **`scripts/extract_faq_epfo.py`** - EPFO/Provident Fund FAQs
4. **`scripts/extract_faq_parivahan.py`** - Driving License/Transport FAQs

### Orchestration Scripts
- **`scripts/extract_all_faqs_parallel.sh`** - Run all in parallel (recommended)
- **`scripts/monitor_faq_extraction.sh`** - Monitor progress

### Original Script (Sequential)
- **`scripts/extract_faqs.py`** - Runs all scrapers one by one (slow, may timeout)

---

## Expected Results

### Before Extraction
```
Total FAQs: 6-23
  passport: 17-23
  aadhaar: 2
  pan: 2
  (Others: 0)
```

### After Complete Extraction
```
Total FAQs: 50-100+ (estimated)
  passport: 17-30
  aadhaar: 10-20
  pan: 15-25
  epfo: 10-20
  parivahan: 8-15
```

---

## How It Works

### 1. Individual Scripts
Each script:
- Loads only its specific scraper
- Connects to database independently
- Checks for duplicate FAQs
- Generates embeddings for each FAQ
- Commits results immediately
- Handles errors gracefully

### 2. Parallel Execution
- Each scraper runs in separate process
- No shared state between processes
- Database handles concurrent writes safely
- If one fails, others continue

### 3. Deduplication
- Checks if FAQ question already exists in database
- Prevents duplicates across multiple runs
- Safe to re-run scripts anytime

---

## Troubleshooting

### No FAQs Extracted
**Check logs:**
```bash
cat artifacts/faq_extraction_aadhaar.log
```

**Common issues:**
- Network timeout → Retry script
- Website blocking → Wait and retry
- Playwright not installed → `pip install playwright && python -m playwright install`

### Process Stuck
**Kill specific process:**
```bash
ps aux | grep extract_faq
kill <PID>
```

**Kill all extraction processes:**
```bash
pkill -f extract_faq
```

### Database Lock Error
This is rare but can happen with concurrent writes:
- Wait for current process to complete
- Or restart the failed scraper

---

## Verification

### Check Final Count
```bash
python -c "
from core.database import SessionLocal
from core.models import FAQ
db = SessionLocal()
print(f'Total FAQs: {db.query(FAQ).count()}')
db.close()
"
```

### View Recent FAQs
```bash
python -c "
from core.database import SessionLocal
from core.models import FAQ
db = SessionLocal()
faqs = db.query(FAQ).order_by(FAQ.created_at.desc()).limit(10).all()
for faq in faqs:
    print(f'{faq.category}: {faq.question[:60]}...')
db.close()
"
```

---

## Performance

### Sequential (Old Method)
- **Time:** 15-20 minutes
- **Risk:** High (timeouts common)
- **Result:** Often incomplete

### Parallel (New Method)
- **Time:** 5-10 minutes
- **Risk:** Low (each scraper independent)
- **Result:** All complete successfully

---

## Next Steps

After extraction completes:

1. **Verify count:**
   ```bash
   ./scripts/monitor_faq_extraction.sh
   ```

2. **Test search:**
   ```bash
   python -c "
   from core.search import hybrid_search
   from core.database import SessionLocal
   db = SessionLocal()
   results = hybrid_search(db, 'how to apply for passport', limit=5)
   for r in results:
       print(f'{r[\"score\"]:.2f}: {r[\"content\"][:80]}...')
   db.close()
   "
   ```

3. **Update frontend:** FAQs will automatically appear in API responses

---

## Files Reference

```
scripts/
├── extract_faq_aadhaar.py         ← Individual scraper
├── extract_faq_pan.py             ← Individual scraper
├── extract_faq_epfo.py            ← Individual scraper
├── extract_faq_parivahan.py       ← Individual scraper
├── extract_all_faqs_parallel.sh   ← Run all in parallel
├── monitor_faq_extraction.sh      ← Monitor progress
└── extract_faqs.py                ← Original (sequential)

artifacts/
├── faq_extraction_aadhaar.log     ← Logs
├── faq_extraction_pan.log         ← Logs
├── faq_extraction_epfo.log        ← Logs
└── faq_extraction_parivahan.log   ← Logs
```

---

## Summary

✅ **Parallel extraction avoids timeouts**  
✅ **Each scraper runs independently**  
✅ **Logs saved for debugging**  
✅ **Safe to re-run anytime**  
✅ **Monitoring tool included**  
✅ **Expected completion: 5-10 minutes**

**Recommended command:**
```bash
./scripts/extract_all_faqs_parallel.sh
```

