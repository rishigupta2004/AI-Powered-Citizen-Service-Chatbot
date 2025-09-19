from __future__ import annotations
import argparse
import asyncio
import csv
import hashlib
import re
import time
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse, unquote, urljoin
import aiofiles
import httpx
from slugify import slugify
from playwright.sync_api import sync_playwright  # typing: ignore


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

            # skip if exists
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
        results = []
        for fut in asyncio.as_completed(tasks):
            res = await fut
            results.append(res)

    with manifest_path.open("w", encoding="utf-8", newline="") as csvf:
        writer = csv.DictWriter(csvf,
                                fieldnames=["url", "department", "filepath", "status", "reason", "size", "sha256"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"[HTTP] Download finished. Manifest: {manifest_path}")
    return results

def run_playwright_for_failures(failed_rows: List[Dict[str, Any]], out_dir: Path,
                                timeout_ms: int = 60000, headless: bool = True) -> List[Dict[str, Any]]:
    results = []
    if not failed_rows:
        return results

    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        for i, row in enumerate(failed_rows, start=1):
            url = row["url"]
            dept = row.get("department") or extract_department_from_url(url)
            folder = out_dir / dept
            folder.mkdir(parents=True, exist_ok=True)
            dest_base = folder / filename_from_url(url, dept, i, ext=".pdf")
            result = {**row}
            result.update({"attempt_playwright": True, "pw_filepath": "", "pw_status": "failed", "pw_reason": ""})
            try:
                response = page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                # If response itself is a PDF:
                if response and "application/pdf" in (response.headers.get("content-type") or ""):
                    body = response.body()
                    dest_base.write_bytes(body)
                    result.update({"pw_status": "ok", "pw_filepath": str(dest_base)})
                    results.append(result)
                    continue

                # look for pdf anchors
                anchors = page.query_selector_all("a")
                found_ok = False
                for a in anchors:
                    href = a.get_attribute("href") or ""
                    if re.search(r"\.pdf(\?|$)", href, re.I):
                        pdf_url = urljoin(page.url, href)
                        resp = page.request.get(pdf_url)
                        if resp.status == 200:
                            dest_base.write_bytes(resp.body())
                            result.update({"pw_status": "ok", "pw_filepath": str(dest_base)})
                            found_ok = True
                            break
                if found_ok:
                    results.append(result)
                    continue

                # try fetching via page.request.get(url)
                try:
                    resp = page.request.get(url)
                    if resp.status == 200 and "pdf" in (resp.headers.get("content-type") or ""):
                        dest_base.write_bytes(resp.body())
                        result.update({"pw_status": "ok", "pw_filepath": str(dest_base)})
                        results.append(result)
                        continue
                except Exception:
                    pass

                # fallback: save HTML and attempt page.pdf()
                html_path = dest_base.with_suffix(".html")
                html_path.write_text(page.content(), encoding="utf-8")
                # attempt to generate a PDF of the rendered page (Chromium)
                try:
                    pdf_path = dest_base.with_suffix(".pdf")
                    page.pdf(path=str(pdf_path))
                    if pdf_path.exists() and pdf_path.stat().st_size > 0:
                        result.update({"pw_status": "ok", "pw_filepath": str(pdf_path)})
                    else:
                        result.update({"pw_status": "failed", "pw_reason": "rendered-pdf-empty"})
                except Exception as e:
                    result.update({"pw_status": "failed", "pw_reason": f"no-pdf-render:{e}"})
            except Exception as e:
                result.update({"pw_status": "failed", "pw_reason": str(e)})
            results.append(result)
        try:
            page.close()
        except Exception:
            pass
        context.close()
        browser.close()
    # write playwright manifest
    pw_manifest = out_dir / "download_manifest_playwright.csv"
    with pw_manifest.open("w", encoding="utf-8", newline="") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=list(results[0].keys()) if results else ["url", "pw_status", "pw_reason"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"[Playwright] Finished. Manifest: {pw_manifest}")
    return results

# --------- Heuristic fixes for stubborn failures (async retry) ---------
async def try_fix_url_candidates(url: str, client: httpx.AsyncClient) -> tuple[str | None, str]:
    """
    Try simple heuristics and return (fixed_url, reason) or (None, reason).
    Heuristics: add https/http, add/remove www, strip query, swap http<->https.
    """
    tried = set()
    parsed = urlparse(url)
    base = url
    if not parsed.scheme:
        candidates = [f"https://{url}", f"http://{url}"]
    else:
        candidates = [url]

    # add variants
    if parsed.netloc and not parsed.netloc.startswith("www."):
        candidates += [re.sub(r"^([^:]+://)", r"\1www.", candidates[0], count=1)] if candidates else []
    # strip query
    if "?" in url:
        candidates.append(url.split("?", 1)[0])
    # switch scheme
    if parsed.scheme == "http":
        candidates.append(url.replace("http://", "https://", 1))
    elif parsed.scheme == "https":
        candidates.append(url.replace("https://", "http://", 1))

    # de-duplicate preserve order
    seen = set()
    final = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            final.append(c)

    for c in final:
        try:
            if c in tried:
                continue
            tried.add(c)
            r = await client.get(c, timeout=20)
            if r.status_code == 200:
                ct = r.headers.get("Content-Type", "").lower()
                if "pdf" in ct or c.lower().endswith(".pdf"):
                    return c, f"fixed_candidate:{c}"
                # if it's HTML and contains .pdf links, quick scan
                if "html" in ct:
                    text = r.text
                    found = re.search(r"https?://[^\s\"']+\.pdf", text, re.I)
                    if found:
                        return found.group(0), f"found_pdf_in_html:{c}"
                    # still, returning c may help Playwright render the page
                    return c, f"ok_html_candidate:{c}"
        except Exception:
            continue
    return None, "no_candidate_worked"

# --------- main orchestration ---------
async def main_async(urls_file: Path, out_dir: Path, concurrency: int = 6, playwright_headless: bool = True):
    # 1) HTTP bulk
    initial = await run_http_bulk(urls_file, out_dir, concurrency=concurrency)

    # 2) collect failures
    failed = [r for r in initial if r.get("status") != "ok"]
    failed_urls_file = out_dir / "failed_initial.txt"
    failed_urls_file.write_text("\n".join([r["url"] for r in failed]), encoding="utf-8")
    print(f"[INFO] {len(failed)} failures recorded -> {failed_urls_file}")

    # 3) Playwright retry (synchronous)
    pw_results = run_playwright_for_failures(failed, out_dir, headless=playwright_headless)

    # 4) Merge/update statuses and find still-failed
    pw_ok_urls = {r["url"] for r in pw_results if r.get("pw_status") == "ok"}
    still_failed = [r for r in failed if r["url"] not in pw_ok_urls]

    # 5) Try heuristics for the still-failed
    final_results = []
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, follow_redirects=True) as client:
        for r in still_failed:
            url = r["url"]
            candidate, reason = await try_fix_url_candidates(url, client)
            updated = {**r, "final_status": "failed", "final_reason": reason, "final_filepath": ""}
            if candidate:
                # try direct download of candidate
                try:
                    resp = await client.get(candidate, timeout=30)
                    resp.raise_for_status()
                    ct = resp.headers.get("Content-Type", "").lower()
                    dept = extract_department_from_url(candidate)
                    folder = out_dir / dept
                    folder.mkdir(parents=True, exist_ok=True)
                    ext = ".pdf" if "pdf" in ct or candidate.lower().endswith(".pdf") else ".pdf"
                    idx = int(hashlib.sha256(candidate.encode()).hexdigest(), 16) % 1000000
                    fname = filename_from_url(candidate, dept, idx, ext)
                    dest = folder / fname
                    async with aiofiles.open(dest, "wb") as f:
                        await f.write(await resp.aread())
                    updated.update({"final_status": "fixed_by_heuristic", "final_reason": reason, "final_filepath": str(dest)})
                except Exception as e:
                    updated.update({"final_status": "failed_after_heuristic", "final_reason": f"{reason}|{e}"})
            final_results.append(updated)

    # 6) write final manifest (combine initial, pw, and final)
    final_manifest = out_dir / "download_manifest_final.csv"
    # build map for quick lookups
    initial_map = {r["url"]: r for r in initial}
    pw_map = {r["url"]: r for r in pw_results}
    with final_manifest.open("w", encoding="utf-8", newline="") as csvf:
        fieldnames = [
            "url", "department", "initial_status", "initial_reason", "initial_filepath",
            "pw_status", "pw_reason", "pw_filepath",
            "final_status", "final_reason", "final_filepath"
        ]
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        # iterate all URLs from initial list so ordering is preserved
        for url in [r["url"] for r in initial]:
            row = {"url": url}
            i = initial_map.get(url, {})
            row.update({
                "department": i.get("department", ""),
                "initial_status": i.get("status", ""),
                "initial_reason": i.get("reason", ""),
                "initial_filepath": i.get("filepath", "")
            })
            pw = pw_map.get(url, {})
            row.update({
                "pw_status": pw.get("pw_status", ""),
                "pw_reason": pw.get("pw_reason", ""),
                "pw_filepath": pw.get("pw_filepath", "")
            })
            fin = next((f for f in final_results if f["url"] == url), {})
            row.update({
                "final_status": fin.get("final_status", "") or ( "ok" if i.get("status") == "ok" or pw.get("pw_status") == "ok" else ""),
                "final_reason": fin.get("final_reason", ""),
                "final_filepath": fin.get("final_filepath", "")
            })
            writer.writerow(row)
    print(f"[FINAL] Manifest: {final_manifest}")

    # 7) write small failed list for manual review
    failed_after_all = out_dir / "failed_after_all.txt"
    with failed_after_all.open("w", encoding="utf-8") as f:
        # define failure as final_status empty or contains 'failed'
        for row in final_results:
            if row.get("final_status", "").startswith("failed") or not row.get("final_status"):
                f.write(row["url"] + "\n")
    print(f"[FINAL] Remaining failures (for manual inspection): {failed_after_all}")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--urls", required=True, help="path to newline-separated urls.txt (from extract_urls_from_pdf)")
    p.add_argument("--dest", default="data/docs", help="download destination root")
    p.add_argument("--concurrency", type=int, default=6)
    p.add_argument("--no-playwright", action="store_true", help="skip playwright step (only http downloads)")
    p.add_argument("--headless", action="store_true", help="run playwright headless (default False for debugging).")
    return p.parse_args()

def main():
    args = parse_args()
    urls_file = Path(args.urls)
    out_dir = Path(args.dest)
    headless = bool(args.headless)
    if args.no_playwright:
        # only run HTTP bulk and exit
        asyncio.run(run_http_bulk(urls_file, out_dir, concurrency=args.concurrency))
        return

    # Full pipeline (HTTP -> Playwright -> heuristics)
    asyncio.run(main_async(urls_file, out_dir, concurrency=args.concurrency, playwright_headless=headless))

if __name__ == "__main__":
    main()
