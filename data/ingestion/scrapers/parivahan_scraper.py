from .base_scraper import Scraper

class ParivahanScraper(Scraper):
    def __init__(self):
        super().__init__("https://parivahan.gov.in")

    def get_faqs(self, headless=True):
        faqs = []

        # --- 1. Try Playwright ---
        soup = self.scrape_playwright(
            "/en/content/faq",
            headless=headless,
            wait_for_selector="div.faq-title-first-child",
            timeout=60000  # 60s, parivahan can be slow
        )

        # --- 2. Fallback to Requests if Playwright fails ---
        if not soup:
            soup = self.scrape("/en/content/faq")

        if not soup:
            return faqs

        # --- Extract Q&A ---
        faq_blocks = soup.select("div.faq-title-first-child")
        for block in faq_blocks:
            q_tag = block.select_one("a")
            a_tag = block.select_one(".views-field-view")
            if not q_tag:
                continue

            question = q_tag.get_text(strip=True)
            answer = a_tag.get_text(" ", strip=True) if a_tag else ""

            if question and answer:
                faqs.append({"question": question, "answer": answer})

        return faqs
