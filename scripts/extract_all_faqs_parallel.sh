#!/bin/bash
# Extract FAQs from all scrapers in parallel

cd "$(dirname "$0")/.."

echo "╔════════════════════════════════════════════════════════╗"
echo "║     FAQ EXTRACTION - PARALLEL MODE                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Starting FAQ extraction from all scrapers in parallel..."
echo "Logs will be saved to artifacts/faq_extraction_*.log"
echo ""

# Create artifacts directory if it doesn't exist
mkdir -p artifacts

# Run each scraper in background and save logs
echo "→ Aadhaar (background)..."
python scripts/extract_faq_aadhaar.py > artifacts/faq_extraction_aadhaar.log 2>&1 &
PID_AADHAAR=$!

echo "→ PAN (background)..."
python scripts/extract_faq_pan.py > artifacts/faq_extraction_pan.log 2>&1 &
PID_PAN=$!

echo "→ EPFO (background)..."
python scripts/extract_faq_epfo.py > artifacts/faq_extraction_epfo.log 2>&1 &
PID_EPFO=$!

echo "→ Parivahan (background)..."
python scripts/extract_faq_parivahan.py > artifacts/faq_extraction_parivahan.log 2>&1 &
PID_PARIVAHAN=$!

echo ""
echo "All scrapers started! PIDs:"
echo "  Aadhaar:    $PID_AADHAAR"
echo "  PAN:        $PID_PAN"
echo "  EPFO:       $PID_EPFO"
echo "  Parivahan:  $PID_PARIVAHAN"
echo ""
echo "Waiting for all scrapers to complete..."
echo "(This may take 5-10 minutes depending on network speed)"
echo ""

# Wait for all background jobs
wait $PID_AADHAAR
STATUS_AADHAAR=$?

wait $PID_PAN
STATUS_PAN=$?

wait $PID_EPFO
STATUS_EPFO=$?

wait $PID_PARIVAHAN
STATUS_PARIVAHAN=$?

# Display results
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║     EXTRACTION COMPLETE                                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

echo "Status:"
[ $STATUS_AADHAAR -eq 0 ] && echo "  ✅ Aadhaar:   SUCCESS" || echo "  ❌ Aadhaar:   FAILED (code: $STATUS_AADHAAR)"
[ $STATUS_PAN -eq 0 ] && echo "  ✅ PAN:       SUCCESS" || echo "  ❌ PAN:       FAILED (code: $STATUS_PAN)"
[ $STATUS_EPFO -eq 0 ] && echo "  ✅ EPFO:      SUCCESS" || echo "  ❌ EPFO:      FAILED (code: $STATUS_EPFO)"
[ $STATUS_PARIVAHAN -eq 0 ] && echo "  ✅ Parivahan: SUCCESS" || echo "  ❌ Parivahan: FAILED (code: $STATUS_PARIVAHAN)"

echo ""
echo "View logs:"
echo "  tail -f artifacts/faq_extraction_aadhaar.log"
echo "  tail -f artifacts/faq_extraction_pan.log"
echo "  tail -f artifacts/faq_extraction_epfo.log"
echo "  tail -f artifacts/faq_extraction_parivahan.log"

echo ""
echo "Check final FAQ count:"
echo "  python -c 'from core.database import SessionLocal; from core.models import FAQ; db = SessionLocal(); print(f\"Total FAQs: {db.query(FAQ).count()}\"); db.close()'"
echo ""

