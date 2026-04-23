from .passport_scraper import PassportScraper
from .aadhaar_scraper import AadhaarScraper
from .epfo_scraper import EPFOScraper
from .pan_scraper import PanScraper
from .parivahan_scraper import ParivahanScraper

SCRAPERS = {
    "passport": PassportScraper,
    "aadhaar": AadhaarScraper,
    "epfo": EPFOScraper,
    "pan": PanScraper,
    "parivahan": ParivahanScraper,
}

def get_all_scrapers():
    """Return dictionary of all registered scrapers."""
    return SCRAPERS

def crawl_all(seeds: list[str] | None = None, allowlists: dict | None = None, headless: bool = True) -> dict:
    """Run all registered scrapers and return counts per scraper.
    This is a thin orchestrator; individual scrapers implement pagination/JS rendering.
    """
    out = {}
    for name, cls in SCRAPERS.items():
        try:
            s = cls()
            faqs = getattr(s, "get_faqs", lambda **kw: [])(headless=headless)
            out[name] = {"faqs": len(faqs)}
        except Exception as e:
            out[name] = {"error": str(e)}
    return out


