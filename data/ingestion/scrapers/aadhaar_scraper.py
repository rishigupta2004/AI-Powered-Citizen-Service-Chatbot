# data/ingestion/scrapers/aadhaar_scraper.py
from data.ingestion.scrapers.base_scraper import Scraper
import logging

logger = logging.getLogger(__name__)

class AadhaarScraper(Scraper):
    def __init__(self):
        super().__init__("https://uidai.gov.in")

    def get_faqs(self, headless: bool = True):
        path = "/en/contact-support/have-any-question/281-english-uk/faqs/your-aadhaar/use-aadhaar-freely.html"
        faqs = []
        # try lightweight requests first (this page often renders server-side)
        try:
            soup = self.scrape_requests(path)
        except Exception:
            try:
                soup = self.scrape_playwright(path, headless=headless, wait_for_selector="div.accordion_head")
            except Exception:
                return faqs

        # typical UIDAI structure: accordion_head / accordion_body or headings + p
        for head in soup.select("div.accordion_head, .accordion_head, .tjbase-accordion .accordion_head, h4, h3"):
            qtxt = head.get_text(strip=True)
            # answer often in next div with class accordion_body or next <p>
            a_div = head.find_next("div", class_="accordion_body") or head.find_next("div", class_="accordionBody")
            a_tag = head.find_next("p")
            atxt = ""
            if a_div:
                atxt = a_div.get_text(strip=True)
            elif a_tag and a_tag.get_text(strip=True):
                atxt = a_tag.get_text(strip=True)
            if qtxt and atxt and not atxt.strip().startswith("collaborate"):
                faqs.append({"question": qtxt, "answer": atxt})

        # dedupe
        seen=set(); out=[]
        for f in faqs:
            if f["question"] in seen:
                continue
            seen.add(f["question"])
            out.append(f)
        return out
