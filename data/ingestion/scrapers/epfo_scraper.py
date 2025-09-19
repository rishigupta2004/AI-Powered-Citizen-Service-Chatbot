# data/ingestion/scrapers/epfo_scraper.py
from data.ingestion.scrapers.base_scraper import Scraper
import re
import logging

logger = logging.getLogger(__name__)

class EPFOScraper(Scraper):
    def __init__(self):
        super().__init__("https://www.epfindia.gov.in")

    def get_faqs(self, headless: bool = True):
        try:
            soup = self.scrape_requests("/site_en/FAQ.php")
        except Exception:
            return []

        faqs = []
        for row in soup.select("table tr"):
            cells = row.select("td")
            if len(cells) >= 2:
                q = cells[0].get_text(" ", strip=True)
                a = cells[1].get_text(" ", strip=True)
                # skip junk rows (number-only Qs or answers without letters)
                if not q or not a:
                    continue
                if re.fullmatch(r"^\d+\.?$", q.strip()):
                    # skip bare numeric question like "1." etc
                    continue
                if not re.search(r"[A-Za-z]", a):
                    continue
                if "Owned and Developed" in a or "Visitor Count" in a:
                    continue
                faqs.append({"question": q, "answer": a})

        # optionally further cleaning could be done here
        return faqs
