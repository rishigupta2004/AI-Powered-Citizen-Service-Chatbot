# scripts/test_scrapers.py
import logging
from data.ingestion.scrapers.passport_scraper import PassportScraper
from data.ingestion.scrapers.aadhaar_scraper import AadhaarScraper
from data.ingestion.scrapers.pan_scraper import PanScraper
from data.ingestion.scrapers.parivahan_scraper import ParivahanScraper
from data.ingestion.scrapers.epfo_scraper import EPFOScraper

logging.basicConfig(level=logging.INFO)
sites = [
    ("Passport", PassportScraper()),
    ("Aadhaar", AadhaarScraper()),
    ("PAN", PanScraper()),
    ("Parivahan", ParivahanScraper()),
    ("EPFO", EPFOScraper()),
]

def show_sample(name, faqs):
    if not faqs:
        print(f"⚠️  {name} returned no FAQs.")
        return
    print(f"✅ Found {len(faqs)} FAQs. Showing up to 3 samples:")
    for i, f in enumerate(faqs[:3], 1):
        q = f.get("question","").replace("\n"," ")
        a = f.get("answer","").replace("\n"," ")
        print(f"  {i}. Q: {q}\n     A: {a}\n")

if __name__ == "__main__":
    for name, scraper in sites:
        print(f"\n🔎 Testing {name}Scraper...")
        try:
            faqs = scraper.get_faqs(headless=True)
            show_sample(name, faqs)
        except Exception as e:
            print(f"❌ {name}Scraper error: {e}")
