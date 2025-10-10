# data/ingestion/scrapers/base_scraper.py
import logging
import random
import time
import ssl
import os
import json
import hashlib
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin
from datetime import datetime, timedelta
from pathlib import Path

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

# Default proxies - can be overridden by environment variables
# Format: "http://user:pass@host:port" or "http://host:port"
DEFAULT_PROXIES = []

# Get proxies from environment variable if set (comma-separated list)
PROXY_LIST = os.environ.get("SCRAPER_PROXIES", "")
if PROXY_LIST:
    DEFAULT_PROXIES = [p.strip() for p in PROXY_LIST.split(",") if p.strip()]

# Enable/disable proxy rotation via environment variable
USE_PROXIES = os.environ.get("USE_PROXY_ROTATION", "false").lower() in ("true", "1", "yes")

# Enable/disable incremental change detection
USE_INCREMENTAL = os.environ.get("USE_INCREMENTAL_SCRAPING", "true").lower() in ("true", "1", "yes")

# Cache directory for storing ETags, Last-Modified headers and content hashes
CACHE_DIR = Path(os.environ.get("SCRAPER_CACHE_DIR", "data/cache/scrapers"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def random_user_agent():
    return random.choice(USER_AGENTS)

def random_viewport():
    return random.choice(VIEWPORTS)

def random_proxy():
    """Return a random proxy from the list or None if empty"""
    if not DEFAULT_PROXIES or not USE_PROXIES:
        return None
    return random.choice(DEFAULT_PROXIES)

def get_cache_key(url: str) -> str:
    """Generate a safe filename from URL for caching"""
    return hashlib.md5(url.encode()).hexdigest()

def save_response_metadata(url: str, etag: str = None, last_modified: str = None, 
                          content_hash: str = None) -> None:
    """Save response metadata for incremental change detection"""
    if not USE_INCREMENTAL:
        return
    
    cache_key = get_cache_key(url)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    metadata = {
        "url": url,
        "etag": etag,
        "last_modified": last_modified,
        "content_hash": content_hash,
        "last_checked": datetime.now().isoformat()
    }
    
    with open(cache_file, "w") as f:
        json.dump(metadata, f)

def get_response_metadata(url: str) -> Dict[str, Any]:
    """Get cached response metadata if available"""
    if not USE_INCREMENTAL:
        return {}

def apply_conditional_headers(headers: Dict[str, str], metadata: Dict[str, Any]) -> Dict[str, str]:
    """Apply ETag/Last-Modified headers if present in metadata."""
    if not metadata:
        return headers
    etag = metadata.get("etag")
    last_modified = metadata.get("last_modified")
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    return headers

def build_playwright_proxy_config(proxy: Optional[str]) -> Optional[Dict[str, str]]:
    """Return Playwright proxy config from a proxy URL string."""
    if not proxy:
        return None
    p = proxy
    if p.startswith("http://"):
        p = p[7:]
    elif p.startswith("https://"):
        p = p[8:]
    if "@" in p:
        auth, address = p.split("@", 1)
        user, password = auth.split(":", 1)
        return {"server": f"http://{address}", "username": user, "password": password}
    return {"server": f"http://{p}"}
    
    cache_key = get_cache_key(url)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if not cache_file.exists():
        return {}
    
    try:
        with open(cache_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load cache for {url}: {e}")
        return {}

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
    def __init__(self, base_url: str, default_headers: Optional[dict] = None, 
                 use_proxies: bool = None, use_incremental: bool = None):
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {
            "User-Agent": random_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": self.base_url,
        }
        self.logger = logger
        # Allow instance-level override of global settings
        self.use_proxies = USE_PROXIES if use_proxies is None else use_proxies
        self.use_incremental = USE_INCREMENTAL if use_incremental is None else use_incremental

    def _build_url(self, path: str = "") -> str:
        if not path:
            return self.base_url
        if path.startswith("http://") or path.startswith("https://"):
            return path
        # join cleanly
        return urljoin(self.base_url + "/", path.lstrip("/"))
    
    def _should_fetch(self, url: str) -> bool:
        """
        Determine if we should fetch the URL based on cached metadata
        Returns True if we should fetch, False if content hasn't changed
        """
        if not self.use_incremental:
            return True
            
        metadata = get_response_metadata(url)
        if not metadata:
            return True
            
        # Check if we've fetched this recently (within last hour)
        if "last_checked" in metadata:
            try:
                last_checked = datetime.fromisoformat(metadata["last_checked"])
                if datetime.now() - last_checked < timedelta(hours=1):
                    self.logger.info(f"Skipping recent fetch for {url} (checked {last_checked})")
                    return False
            except Exception:
                pass
                
        return True
        
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate a hash of the content for change detection"""
        return hashlib.md5(content.encode()).hexdigest()

    # ---------- Requests fetch ----------
    def scrape_requests(self, path: str = "", params: dict = None, timeout: int = 30,
                        force_fetch: bool = False) -> BeautifulSoup:
        url = self._build_url(path)
        
        # Check if we should fetch based on cached metadata
        if not force_fetch and not self._should_fetch(url):
            self.logger.info(f"Using cached content for {url} (no changes detected)")
            # Return empty soup - caller should handle this appropriately
            return None
            
        session = requests_session_with_retries(timeout=timeout)
        headers = apply_conditional_headers({
            **self.default_headers,
            "User-Agent": random_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
        }, get_response_metadata(url) if self.use_incremental else {})
        
        # Set up proxies if enabled
        proxies = None
        if self.use_proxies:
            proxy = random_proxy()
            if proxy:
                proxies = {"http": proxy, "https": proxy}
                self.logger.info(f"Using proxy: {proxy} for {url}")
        
        self.logger.info("Requests fetching %s", url)
        try:
            resp = session.get(url, headers=headers, params=params or {}, 
                              timeout=timeout, proxies=proxies)
            
            # Handle 304 Not Modified
            if resp.status_code == 304:
                self.logger.info(f"Content not modified for {url}")
                return None
                
            resp.raise_for_status()
            
            # Save response metadata for future incremental fetches
            if self.use_incremental:
                etag = resp.headers.get("ETag")
                last_modified = resp.headers.get("Last-Modified")
                content_hash = self._calculate_content_hash(resp.text)
                save_response_metadata(url, etag, last_modified, content_hash)
                
            return BeautifulSoup(resp.text, "lxml")
            
        except requests.exceptions.RequestException as e:
            if proxies and "ProxyError" in str(e):
                self.logger.warning(f"Proxy error for {url}: {e}. Retrying without proxy.")
                # Retry without proxy
                resp = session.get(url, headers=headers, params=params or {}, timeout=timeout)
                resp.raise_for_status()
                return BeautifulSoup(resp.text, "lxml")
            raise

    # ---------- Playwright fetch (JS rendering) ----------
    def scrape_playwright(self, path: str = "", headless: bool = True, wait_for_selector: Optional[str] = None,
                          wait_until: str = "networkidle", timeout: int = 30000, 
                          force_fetch: bool = False) -> BeautifulSoup:
        """
        Render the page using Playwright and return a BeautifulSoup object.
        - path may be relative (joined to base_url) or absolute.
        - wait_for_selector: CSS selector to wait for (optional).
        - timeout: in ms.
        - force_fetch: bypass incremental change detection
        """
        url = self._build_url(path)
        
        # Check if we should fetch based on cached metadata
        if not force_fetch and not self._should_fetch(url):
            self.logger.info(f"Using cached content for {url} (no changes detected)")
            return None
            
        ua = random_user_agent()
        vp = random_viewport()
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            self.logger.error("playwright not installed or import failed: %s", e)
            raise

        # Set up proxy if enabled
        proxy_config = build_playwright_proxy_config(random_proxy() if self.use_proxies else None)
        if proxy_config:
            self.logger.info(f"Using proxy for Playwright: {proxy_config['server']}")

        self.logger.info("Playwright navigating to %s (headless=%s, ua=%s)", url, headless, ua)
        try:
            with sync_playwright() as p:
                browser_args = ["--no-sandbox", "--disable-dev-shm-usage"]
                
                # Launch browser with proxy if configured
                browser = p.chromium.launch(
                    headless=headless, 
                    args=browser_args,
                    proxy=proxy_config if proxy_config else None
                )
                
                context = browser.new_context(
                    user_agent=ua, 
                    viewport=vp, 
                    locale="en-US",
                    extra_http_headers={"accept-language": "en-US,en;q=0.9"}
                )
                
                # inject stealth
                try:
                    context.add_init_script(STEALTH_JS)
                except Exception:
                    pass
                    
                page = context.new_page()
                
                # Add conditional headers if we have cached metadata
                metadata = get_response_metadata(url) if self.use_incremental else {}
                if metadata:
                    extra = {}
                    if metadata.get("etag"):
                        extra["If-None-Match"] = metadata["etag"]
                    if metadata.get("last_modified"):
                        extra["If-Modified-Since"] = metadata["last_modified"]
                    if extra:
                        page.set_extra_http_headers(extra)
                
                response = page.goto(url, wait_until=wait_until, timeout=timeout)
                
                # Handle 304 Not Modified (though Playwright usually handles this internally)
                if response and response.status == 304:
                    self.logger.info(f"Content not modified for {url}")
                    browser.close()
                    return None
                
                if wait_for_selector:
                    try:
                        page.wait_for_selector(wait_for_selector, timeout=timeout)
                    except Exception as e:
                        self.logger.debug("wait_for_selector (%s) failed: %s", wait_for_selector, e)
                
                time.sleep(random.uniform(0.15, 0.8))
                html = page.content()
                
                # Save response metadata for future incremental fetches
                if self.use_incremental:
                    etag = response.headers.get("etag") if response else None
                    last_modified = response.headers.get("last-modified") if response else None
                    content_hash = self._calculate_content_hash(html)
                    save_response_metadata(url, etag, last_modified, content_hash)
                
                try:
                    browser.close()
                except Exception:
                    pass
                return BeautifulSoup(html, "lxml")
                
        except Exception as e:
            self.logger.warning("Playwright fetch failed for %s: %s", url, e)
            # If proxy error, retry without proxy
            if proxy_config and ("proxy" in str(e).lower() or "timeout" in str(e).lower()):
                self.logger.info("Retrying without proxy due to possible proxy error")
                try:
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=headless, args=["--no-sandbox", "--disable-dev-shm-usage"])
                        context = browser.new_context(user_agent=ua, viewport=vp, locale="en-US",
                                                    extra_http_headers={"accept-language": "en-US,en;q=0.9"})
                        try:
                            context.add_init_script(STEALTH_JS)
                        except Exception:
                            pass
                        page = context.new_page()
                        page.goto(url, wait_until=wait_until, timeout=timeout)
                        if wait_for_selector:
                            try:
                                page.wait_for_selector(wait_for_selector, timeout=timeout)
                            except Exception as e2:
                                self.logger.debug("wait_for_selector (%s) failed: %s", wait_for_selector, e2)
                        time.sleep(random.uniform(0.15, 0.8))
                        html = page.content()
                        browser.close()
                        return BeautifulSoup(html, "lxml")
                except Exception as e2:
                    self.logger.error("Retry without proxy also failed: %s", e2)
                    raise
            raise

    # ---------- Hybrid convenience wrapper ----------
    def scrape(self, path: str = "", prefer: str = "auto", headless: bool = True,
               wait_for_selector: Optional[str] = None, timeout: int = 30,
               force_fetch: bool = False) -> BeautifulSoup:
        """
        prefer: "auto" (requests first, then playwright if empty/fails),
                "requests" (only requests),
                "playwright" (only playwright).
        timeout: seconds for requests; ms for playwright (if playwright path used).
        force_fetch: bypass incremental change detection
        """
        if prefer == "playwright":
            return self.scrape_playwright(path, headless=headless, wait_for_selector=wait_for_selector,
                                          timeout=timeout if timeout > 1000 else int(timeout*1000),
                                          force_fetch=force_fetch)
        if prefer == "requests":
            return self.scrape_requests(path, timeout=timeout, force_fetch=force_fetch)

        # auto: try requests first, then playwright
        try:
            soup = self.scrape_requests(path, timeout=timeout, force_fetch=force_fetch)
            
            # If None is returned, it means content hasn't changed (304)
            if soup is None:
                return None
                
            # if page is basically empty (single noscript/react root), fallback
            body_text = (soup.body.get_text(strip=True) if soup.body else "")
            if len(body_text) < 20:
                self.logger.info("Requests returned near-empty content for %s, falling back to Playwright", path)
                playwright_soup = self.scrape_playwright(path, headless=headless, wait_for_selector=wait_for_selector,
                                              timeout=int(timeout*1000), force_fetch=True)  # Force fetch since we already checked
                return playwright_soup if playwright_soup is not None else soup
            return soup
        except Exception as e:
            self.logger.warning("Requests fetch failed (%s) — falling back to Playwright: %s", path, e)
            return self.scrape_playwright(path, headless=headless, wait_for_selector=wait_for_selector,
                                          timeout=int(timeout*1000), force_fetch=force_fetch)
