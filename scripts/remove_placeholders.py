#!/usr/bin/env python3
"""
Remove placeholder services/FAQs and write a changed_items.csv report.
Placeholders are detected heuristically (names like 'Test Service', FAQs with generic text).
"""
import os
import sys
import csv
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.append(ROOT)

from core.database import SessionLocal
from core.models import Service, FAQ

ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def is_placeholder_service(s: Service) -> bool:
    name = (s.name or "").lower()
    return name.startswith("test service") or name.startswith("test passport service")


def is_placeholder_faq(f: FAQ) -> bool:
    q = (f.question or "").lower()
    a = (f.answer or "").lower()
    return (
        q.startswith("how to apply") and "passport" in q and a.startswith("fill out the form")
    ) or (
        q.startswith("how long") and ("passport" in q or "aadhaar" in q or "pan" in q)
    )


def main():
    db = SessionLocal()
    changed = []
    try:
        # Remove placeholder services
        services = db.query(Service).all()
        for s in services:
            if is_placeholder_service(s):
                changed.append(["service", s.service_id, s.name, "removed"])
                db.delete(s)

        # Remove placeholder FAQs
        faqs = db.query(FAQ).all()
        for f in faqs:
            if is_placeholder_faq(f):
                changed.append(["faq", f.faq_id, (f.question or "")[:80], "removed"])
                db.delete(f)

        db.commit()

        # Write report
        with open(ARTIFACTS / "changed_items.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["type", "id", "name_or_question", "action"])
            for row in changed:
                w.writerow(row)
        print(f"Removed {len(changed)} placeholder items; report at artifacts/changed_items.csv")
    finally:
        db.close()


if __name__ == "__main__":
    main()


