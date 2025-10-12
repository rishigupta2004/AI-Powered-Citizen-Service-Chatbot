#!/bin/bash
# Monitor FAQ extraction progress

cd "$(dirname "$0")/.."

echo "╔════════════════════════════════════════════════════════╗"
echo "║     FAQ EXTRACTION MONITOR                            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if extraction processes are running
RUNNING=$(ps aux | grep "extract_faq_" | grep -v grep | wc -l)

if [ $RUNNING -eq 0 ]; then
    echo "⚠️  No extraction processes running"
    echo ""
    echo "To start extraction:"
    echo "  ./scripts/extract_all_faqs_parallel.sh"
    echo ""
else
    echo "✅ $RUNNING extraction process(es) running"
    echo ""
    echo "Active processes:"
    ps aux | grep "extract_faq_" | grep -v grep | awk '{print "  PID " $2 ": " $11}'
    echo ""
fi

# Show latest log entries
echo "Recent activity:"
echo "────────────────────────────────────────────────────────"
for log in artifacts/faq_extraction_*.log; do
    if [ -f "$log" ]; then
        SERVICE=$(basename "$log" .log | sed 's/faq_extraction_//')
        echo ""
        echo "📋 $SERVICE:"
        tail -3 "$log" 2>/dev/null | sed 's/^/  /'
    fi
done

echo ""
echo "────────────────────────────────────────────────────────"
echo ""

# Check current FAQ count
echo "Current database status:"
python -c "
from core.database import SessionLocal
from core.models import FAQ
db = SessionLocal()
try:
    total = db.query(FAQ).count()
    print(f'  Total FAQs in database: {total}')
    
    # Count by category
    from sqlalchemy import func
    by_category = db.query(FAQ.category, func.count(FAQ.faq_id)).group_by(FAQ.category).all()
    print('\n  By category:')
    for cat, count in by_category:
        print(f'    {cat or \"unknown\"}: {count}')
finally:
    db.close()
" 2>/dev/null || echo "  ⚠️  Database connection failed"

echo ""
echo "To view live logs:"
echo "  tail -f artifacts/faq_extraction_aadhaar.log"
echo "  tail -f artifacts/faq_extraction_pan.log"
echo "  tail -f artifacts/faq_extraction_epfo.log"
echo "  tail -f artifacts/faq_extraction_parivahan.log"
echo ""

