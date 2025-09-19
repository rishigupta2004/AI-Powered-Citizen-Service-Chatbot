# scripts/inspect_dom.py
import sys
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from data.ingestion.scrapers.base_scraper import Scraper

def inspect(url, depth=2, preview_len=80, export_json=False):
    s = Scraper(url)
    soup = s.scrape_requests("")  # fetch root
    print(f"\nInspecting {url}\n{'='*100}")

    def walk(node, level=0):
        if level > depth:
            return None
        if not getattr(node, "name", None):
            return None
        classes = " ".join(node.get("class", []))
        ident = node.get("id", "")
        txt = node.get_text(strip=True)[:preview_len].replace("\n", " ")
        indent = "  " * level
        print(f"{indent}<{node.name} id='{ident}' class='{classes}'> text='{txt}'")
        for child in node.find_all(recursive=False):
            walk(child, level+1)

    body = soup.find("body")
    if not body:
        print("⚠️ No <body> found. Page might be JS-driven.")
    else:
        for child in body.find_all(recursive=False):
            walk(child)

    # collect same-site links
    base = url
    seen=set(); links=[]
    print("\n🔗 Extracted links:")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href: continue
        full = urljoin(base, href)
        if urlparse(full).netloc == urlparse(base).netloc and full not in seen:
            seen.add(full)
            links.append(full)
            print(f"- {full}   (text='{a.get_text(strip=True)[:60]}')")

    if export_json:
        fname="dom_inspection.json"
        with open(fname,"w") as f:
            json.dump({"url": url, "links": links}, f, indent=2)
        print(f"\n✅ Exported links to {fname}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.inspect_dom <url> [--json]")
        sys.exit(1)
    url = sys.argv[1]
    export = "--json" in sys.argv
    inspect(url, depth=3, export_json=export)
