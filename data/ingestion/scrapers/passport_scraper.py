# data/ingestion/scrapers/passport_scraper.py
from data.ingestion.scrapers.base_scraper import Scraper
import logging

logger = logging.getLogger(__name__)

class PassportScraper(Scraper):
    def __init__(self):
        super().__init__("https://www.passportindia.gov.in")

    def get_faqs(self, headless: bool = True):
        urls = [
            "/psp/FaqServicesAvailable#ServiceAvail",
            "/psp/SplCaseOfMinorsReqPassport",
            "/psp/FaqWhereToApply",
            "/psp/FaqApplicationForm",
            "/psp/FaqFeePayment",
            "/psp/FaqResetPassword",
            "/psp/FaqEPassport",
            "/psp/FaqPoliceVerification",
            "/psp/FaqPostalDispatchTracking",
            "/psp/FaqCallCentre",
            "/psp/FaqLostDamagedPassports",
            "/psp/FaqTatkaalPassports",
            "/psp/FaqIdentityCertificate",
            "/psp/FaqAliasName",
            "/psp/FaqAppeal",
            "/psp/FaqSurrender",
            "/psp/FaqMiscellaneous",
            "/psp/FaqLocPermits",
            "/psp/FaqCamp",
        ]
        faqs = []
        for path in urls:
            # Passport site is JS-driven — prefer Playwright rendering for reliable results
            try:
                soup = self.scrape_playwright(path, headless=headless, wait_for_selector="div.faqDiv")
            except Exception:
                # fallback to requests (some pages may render server-side)
                try:
                    soup = self.scrape_requests(path)
                except Exception:
                    continue

            # Try multiple patterns based on observed DOM
            for block in soup.select("div.faqDiv, div.faq-section, article, div.main-content"):
                q = block.select_one("div.faqQuestion, a, h3, h4, strong")
                a = block.select_one("div.faqAnswer, p, div.answer, .faqAns")
                # sometimes <a> holds question and answer is sibling <p>
                if not a and q:
                    a = q.find_next("p")
                if q and a:
                    qtxt = q.get_text(strip=True)
                    atxt = a.get_text(strip=True)
                    if qtxt and atxt and "©" not in atxt:
                        faqs.append({"question": qtxt, "answer": atxt})

        # dedupe
        seen = set(); out=[]
        for f in faqs:
            q = f["question"]
            if q in seen:
                continue
            seen.add(q)
            out.append(f)
        return out
