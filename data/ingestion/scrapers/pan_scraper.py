# data/ingestion/scrapers/pan_scraper.py
from data.ingestion.scrapers.base_scraper import Scraper
import logging

logger = logging.getLogger(__name__)

class PanScraper(Scraper):
    def __init__(self):
        super().__init__("https://tinpan.proteantech.in")

    def get_faqs(self, headless: bool = True):
        path = "/services/pan/faqs.html"
        faqs = []
        # tinpan is a JS app — use Playwright rendering
        try:
            soup = self.scrape_playwright(path, headless=headless, wait_for_selector="div.flex.flex-col")
        except Exception:
            # fallback to requests
            try:
                soup = self.scrape_requests(path)
            except Exception:
                return faqs

        # Based on DOM from your screenshots: question in button, answer in div with classes
        for block in soup.select("div.flex.flex-col, .faq-item, .accordion-item"):
            q_el = block.select_one("button, .faq-head, h3, h4")
            a_el = block.select_one("div.p-2.text-white.bg-black.whitespace-pre-line, .answer, .faq-body")
            if q_el and a_el:
                qtxt = q_el.get_text(strip=True)
                atxt = a_el.get_text(strip=True)
                if qtxt and atxt:
                    faqs.append({"question": qtxt, "answer": atxt})

        # fallback: pair buttons and following divs
        if not faqs:
            for btn in soup.select("button"):
                ans = btn.find_next("div", class_="p-2 text-white bg-black whitespace-pre-line")
                if ans:
                    faqs.append({"question": btn.get_text(strip=True), "answer": ans.get_text(strip=True)})

        # dedupe
        seen=set(); out=[]
        for f in faqs:
            if f["question"] in seen:
                continue
            seen.add(f["question"])
            out.append(f)
        return out

# Alias to satisfy tests expecting this class name
class PANScraper(PanScraper):
    pass
