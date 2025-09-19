# data/ingestion/scrapers/base_scraper.py
import logging
import random
import time
import ssl
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

# requests parts
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# module logger
logger = logging.getLogger("data.ingestion.scrapers.base_scraper")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# --- Helpers / constants ---
USER_AGENTS = [
    # small realistic pool; extend if desired
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
]

VIEWPORTS = [
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
]

def random_user_agent():
    return random.choice(USER_AGENTS)

def random_viewport():
    return random.choice(VIEWPORTS)

# --- Optional adapter to allow legacy SSL renegotiation for problematic servers ---
class LegacyHttpAdapter(HTTPAdapter):
    """Requests adapter which attempts to set an SSLContext allowing legacy renegotiation where available."""
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        # try setting legacy server connect flag if available on platform
        try:
            ctx.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0)
        except Exception:
            # fallback: try numeric value for older glibc/openssl combos (best-effort)
            try:
                ctx.options |= 0x4
            except Exception:
                pass
        pool_kwargs["ssl_context"] = ctx
        return super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)

def requests_session_with_retries(timeout=30, max_retries=3):
    s = requests.Session()
    retry = Retry(total=max_retries, backoff_factor=1,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(["GET","POST"]))
    s.mount("https://", LegacyHttpAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

# Minimal manual stealth JS — best-effort
STEALTH_JS = r"""
Object.defineProperty(navigator, 'webdriver', {get: () => false});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
try {
  const getParameter = WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return "Intel Inc.";
    if (parameter === 37446) return "Intel Iris OpenGL Engine";
    return getParameter.call(this, parameter);
  };
} catch(e){}
"""

class Scraper:
    def __init__(self, base_url: str, default_headers: Optional[dict] = None):
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {
            "User-Agent": random_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": self.base_url,
        }
        self.logger = logger

    def _build_url(self, path: str = "") -> str:
        if not path:
            return self.base_url
        if path.startswith("http://") or path.startswith("https://"):
            return path
        # join cleanly
        return urljoin(self.base_url + "/", path.lstrip("/"))

    # ---------- Requests fetch ----------
    def scrape_requests(self, path: str = "", params: dict = None, timeout: int = 30) -> BeautifulSoup:
        url = self._build_url(path)
        session = requests_session_with_retries(timeout=timeout)
        headers = dict(self.default_headers)
        headers["User-Agent"] = random_user_agent()
        headers["Accept-Language"] = "en-US,en;q=0.9"
        self.logger.info("Requests fetching %s", url)
        resp = session.get(url, headers=headers, params=params or {}, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")

    # ---------- Playwright fetch (JS rendering) ----------
    def scrape_playwright(self, path: str = "", headless: bool = True, wait_for_selector: Optional[str] = None,
                          wait_until: str = "networkidle", timeout: int = 30000) -> BeautifulSoup:
        """
        Render the page using Playwright and return a BeautifulSoup object.
        - path may be relative (joined to base_url) or absolute.
        - wait_for_selector: CSS selector to wait for (optional).
        - timeout: in ms.
        """
        url = self._build_url(path)
        ua = random_user_agent()
        vp = random_viewport()
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            self.logger.error("playwright not installed or import failed: %s", e)
            raise

        self.logger.info("Playwright navigating to %s (headless=%s, ua=%s)", url, headless, ua)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless, args=["--no-sandbox", "--disable-dev-shm-usage"])
                context = browser.new_context(user_agent=ua, viewport=vp, locale="en-US",
                                              extra_http_headers={"accept-language": "en-US,en;q=0.9"})
                # inject stealth
                try:
                    context.add_init_script(STEALTH_JS)
                except Exception:
                    pass
                page = context.new_page()
                page.goto(url, wait_until=wait_until, timeout=timeout)
                if wait_for_selector:
                    try:
                        page.wait_for_selector(wait_for_selector, timeout=timeout)
                    except Exception as e:
                        self.logger.debug("wait_for_selector (%s) failed: %s", wait_for_selector, e)
                time.sleep(random.uniform(0.15, 0.8))
                html = page.content()
                try:
                    browser.close()
                except Exception:
                    pass
                return BeautifulSoup(html, "lxml")
        except Exception as e:
            self.logger.warning("Playwright fetch failed for %s: %s", url, e)
            raise

    # ---------- Hybrid convenience wrapper ----------
    def scrape(self, path: str = "", prefer: str = "auto", headless: bool = True,
               wait_for_selector: Optional[str] = None, timeout: int = 30) -> BeautifulSoup:
        """
        prefer: "auto" (requests first, then playwright if empty/fails),
                "requests" (only requests),
                "playwright" (only playwright).
        timeout: seconds for requests; ms for playwright (if playwright path used).
        """
        if prefer == "playwright":
            return self.scrape_playwright(path, headless=headless, wait_for_selector=wait_for_selector,
                                          timeout=timeout if timeout > 1000 else int(timeout*1000))
        if prefer == "requests":
            return self.scrape_requests(path, timeout=timeout)

        # auto: try requests first, then playwright
        try:
            soup = self.scrape_requests(path, timeout=timeout)
            # if page is basically empty (single noscript/react root), fallback
            body_text = (soup.body.get_text(strip=True) if soup.body else "")
            if len(body_text) < 20:
                self.logger.info("Requests returned near-empty content for %s, falling back to Playwright", path)
                return self.scrape_playwright(path, headless=headless, wait_for_selector=wait_for_selector,
                                              timeout=int(timeout*1000))
            return soup
        except Exception as e:
            self.logger.warning("Requests fetch failed (%s) — falling back to Playwright: %s", path, e)
            return self.scrape_playwright(path, headless=headless, wait_for_selector=wait_for_selector,
                                          timeout=int(timeout*1000))
