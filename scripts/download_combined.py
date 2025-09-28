from __future__ import annotations
import argparse
import asyncio
import csv
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse, unquote, urljoin

import aiofiles
import httpx
from slugify import slugify
from playwright.async_api import async_playwright

# --------- Departments ---------
DEPARTMENTS = {
    "passport": ["passportindia.gov.in", "mea.gov.in"],
    "aadhaar": ["uidai.gov.in"],
    "epfo": ["epfindia.gov.in"],
    "pan": ["incometax.gov.in", "tinpan.proteantech.in"],
    "parivahan": ["parivahan.gov.in"],
    "railways": ["indianrailways.gov.in", "railways.gov.in"],
    "rbi": ["rbi.org.in"],
    "education": ["cbse.gov.in", "du.ac.in"],
}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GovDocBot/1.0; +https://your.domain)",
    "Accept": "*/*",
}

def extract_department_from_url(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    for dept, domains in DEPARTMENTS.items():
        for d in domains:
            if d in domain:
                return dept
    return "other"

def filename_from_url(url: str, dept: str, index: int, ext: str | None = None) -> str:
    parsed = urlparse(url)
    path = unquote(Path(parsed.path).name)
    if not path:
        path = parsed.netloc
    name = slugify(path)[:160] or slugify(parsed.netloc)
    suffix = ext or Path(parsed.path).suffix or ".pdf"
    return f"{dept}__{name}__{index}{suffix}"

# --------- Async HTTP downloader ---------
async def download_one(client: httpx.AsyncClient, url: str, out_dir: Path, index: int,
                       timeout: int = 30, max_retries: int = 3) -> Dict[str, Any]:
    dept = extract_department_from_url(url)
    folder = out_dir / dept
    folder.mkdir(parents=True, exist_ok=True)
    result = {"url": url, "department": dept, "filepath": "", "status": "failed",
              "reason": "", "size": 0, "sha256": ""}

    for attempt in range(1, max_retries + 1):
        try:
            r = await client.get(url, timeout=timeout)
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "").lower()
            ext = ".pdf" if "pdf" in ct or url.lower().endswith(".pdf") else (Path(urlparse(url).path).suffix or ".pdf")
            fname = filename_from_url(url, dept, index, ext)
            dest = folder / fname

            if dest.exists() and dest.stat().st_size > 0:
                result.update({"status": "skipped", "filepath": str(dest)})
                return result

            body = await r.aread()
            async with aiofiles.open(dest, "wb") as f:
                await f.write(body)

            h = hashlib.sha256(body).hexdigest()
            result.update({"status": "ok", "filepath": str(dest), "size": len(body), "sha256": h})
            return result
        except Exception as exc:
            result["reason"] = str(exc)
            await asyncio.sleep(1.5 * attempt)
            continue
    return result

async def run_http_bulk(urls_file: Path, out_dir: Path, concurrency: int = 6) -> List[Dict[str, Any]]:
    urls = [line.strip() for line in urls_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "download_manifest_initial.csv"

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, follow_redirects=True) as client:
        sem = asyncio.Semaphore(concurrency)
        async def worker(url, idx):
            async with sem:
                return await download_one(client, url, out_dir, idx)
        tasks = [worker(url, i + 1) for i, url in enumerate(urls)]
        results = await asyncio.gather(*tasks)

    with manifest_path.open("w", encoding="utf-8", newline="") as csvf:
        writer = csv.DictWriter(csvf,
                                fieldnames=["url", "department", "filepath", "status", "reason", "size", "sha256"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"[HTTP] Download finished. Manifest: {manifest_path}")
    return results

# --------- Playwright retry (async) ---------
async def run_playwright_for_failures_async(failed_rows, out_dir: Path, timeout_ms: int = 60000, headless: bool = True):
    results = []
    if not failed_rows:
        return results

    out_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        for i, row in enumerate(failed_rows, start=1):
            url = row["url"]
            dept = row.get("department") or extract_department_from_url(url)
            folder = out_dir / dept
            folder.mkdir(parents=True, exist_ok=True)
            dest_base = folder / filename_from_url(url, dept, i, ext=".pdf")

            result = {**row}
            result.update({"pw_status": "failed", "pw_reason": "", "pw_filepath": ""})

            try:
                response = await page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                if response and "application/pdf" in (response.headers.get("content-type") or ""):
                    body = await response.body()
                    dest_base.write_bytes(body)
                    result.update({"pw_status": "ok", "pw_filepath": str(dest_base)})
                    results.append(result)
                    continue

                anchors = await page.query_selector_all("a")
                found_ok = False
                for a in anchors:
                    href = await a.get_attribute("href")
                    if href and href.lower().endswith(".pdf"):
                        pdf_url = urljoin(page.url, href)
                        resp = await page.request.get(pdf_url)
                        if resp.ok:
                            dest_base.write_bytes(await resp.body())
                            result.update({"pw_status": "ok", "pw_filepath": str(dest_base)})
                            found_ok = True
                            break
                if found_ok:
                    results.append(result)
                    continue

                html_path = dest_base.with_suffix(".html")
                html_path.write_text(await page.content(), encoding="utf-8")
                try:
                    await page.pdf(path=str(dest_base))
                    if dest_base.exists() and dest_base.stat().st_size > 0:
                        result.update({"pw_status": "ok", "pw_filepath": str(dest_base)})
                except Exception as e:
                    result.update({"pw_reason": f"render-failed:{e}"})
            except Exception as e:
                result.update({"pw_reason": str(e)})
            results.append(result)

        await page.close()
        await context.close()
        await browser.close()

    pw_manifest = out_dir / "download_manifest_playwright.csv"
    with pw_manifest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"[Playwright] Finished. Manifest: {pw_manifest}")
    return results

# --------- main orchestration ---------
async def main_async(urls_file: Path, out_dir: Path, concurrency: int = 6, playwright_headless: bool = True):
    initial = await run_http_bulk(urls_file, out_dir, concurrency=concurrency)
    failed = [r for r in initial if r.get("status") != "ok"]
    failed_urls_file = out_dir / "failed_initial.txt"
    failed_urls_file.write_text("\n".join([r["url"] for r in failed]), encoding="utf-8")
    print(f"[INFO] {len(failed)} failures recorded -> {failed_urls_file}")

    # async playwright retry
    pw_results = await run_playwright_for_failures_async(failed, out_dir, headless=playwright_headless)

    # TODO: heuristic fixes can be added here (same as before)
    return pw_results

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--urls", required=True, help="path to newline-separated urls.txt")
    p.add_argument("--dest", default="data/docs", help="download destination root")
    p.add_argument("--concurrency", type=int, default=6)
    p.add_argument("--headless", action="store_true", help="run playwright headless")
    return p.parse_args()

def main():
    args = parse_args()
    urls_file = Path(args.urls)
    out_dir = Path(args.dest)
    asyncio.run(main_async(urls_file, out_dir, concurrency=args.concurrency, playwright_headless=args.headless))

if __name__ == "__main__":
    main()
