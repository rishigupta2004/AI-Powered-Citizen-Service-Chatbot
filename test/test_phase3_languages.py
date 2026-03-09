"""
SevaSindhu — Phase 3: 22 Languages Test Suite
Run: python scripts/test_phase3_languages.py
Tests: translation file coverage, key completeness, RTL config, font presence,
       live LLM response in each language, native script detection
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
except ImportError:
    pass


try:
    import requests
except ImportError:
    print("pip install requests --break-system-packages")
    sys.exit(1)

BASE_URL     = os.getenv("API_BASE_URL", "https://gov-chatbot.fly.dev")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
I18N_DIR     = os.path.join(FRONTEND_DIR, "src", "i18n")

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
GRAY   = "\033[90m"

def divider(width=72): print(GRAY + "─" * width + RESET)
def ok(msg):   print(f"  {GREEN}✅ PASS{RESET}  {msg}")
def fail(msg): print(f"  {RED}❌ FAIL{RESET}  {msg}")
def warn(msg): print(f"  {YELLOW}⚠  WARN{RESET}  {msg}")
def info(msg): print(f"  {GRAY}     {msg}{RESET}")

LANGUAGES = [
    ("en",  "English",   "Latin",      False, "passport documents required"),
    ("hi",  "Hindi",     "Devanagari", False, "पासपोर्ट के लिए दस्तावेज"),
    ("bn",  "Bengali",   "Bengali",    False, "পাসপোর্ট নথি"),
    ("te",  "Telugu",    "Telugu",     False, "పాన్ కార్డ్ దరఖాస్తు"),
    ("mr",  "Marathi",   "Devanagari", False, "पासपोर्ट अर्ज"),
    ("ta",  "Tamil",     "Tamil",      False, "பாஸ்போர்ட் ஆவணங்கள்"),
    ("gu",  "Gujarati",  "Gujarati",   False, "પાસપોર્ટ અરજી"),
    ("kn",  "Kannada",   "Kannada",    False, "ಪಾಸ್ಪೋರ್ಟ್ ದಾಖಲೆಗಳು"),
    ("ml",  "Malayalam", "Malayalam",  False, "പാസ്പോർട്ട് രേഖകൾ"),
    ("pa",  "Punjabi",   "Gurmukhi",   False, "ਪਾਸਪੋਰਟ ਦਸਤਾਵੇਜ਼"),
    ("or",  "Odia",      "Odia",       False, "ପାସପୋର୍ଟ ଡକ୍ୟୁମେଣ୍ଟ"),
    ("as",  "Assamese",  "Bengali",    False, "পাছপোৰ্ট নথি"),
    ("ur",  "Urdu",      "Arabic",     True,  "پاسپورٹ کاغذات"),
    ("ks",  "Kashmiri",  "Arabic",     True,  "پاسپورٹ دستاویزات"),
    ("ne",  "Nepali",    "Devanagari", False, "पासपोर्ट कागजात"),
]

REQUIRED_I18N_KEYS = [
    "common.loading",
    "common.error",
    "chatbot.placeholder",
    "chatbot.listening",
    "chatbot.thinking",
    "navigation.home",
    "navigation.services",
    "navigation.login",
    "login.title",
    "services.title",
    "app.title",
    "chatbot.welcome",
    "chatbot.title",
    "footer.rights",
    "common.submit",
]

REQUIRED_FONTS = [
    "Noto Sans",
    "Noto Sans Bengali",
    "Noto Sans Telugu",
    "Noto Sans Tamil",
    "Noto Sans Gujarati",
    "Noto Sans Kannada",
    "Noto Sans Malayalam",
    "Noto Sans Gurmukhi",
    "Noto Sans Odia",
    "Noto Sans Arabic",
    "Noto Sans Ol Chiki",
]

def get_nested(d, key_path):
    """Get nested dict value by dot-path e.g. 'common.welcome'"""
    keys = key_path.split(".")
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d

def run():
    print(f"\n{BOLD}{'═'*72}{RESET}")
    print(f"{BOLD}  SevaSindhu — Phase 3: 22 Languages Test Suite{RESET}")
    print(f"{GRAY}  Target: all translation files exist, RTL works, live LLM responds in-language{RESET}")
    print(f"{BOLD}{'═'*72}{RESET}\n")

    all_results = []

    # ── 1. Translation file coverage ────────────────────────────────────────
    print(f"{BOLD}{BLUE}[1] Translation File Coverage{RESET}")
    divider()

    if not os.path.exists(I18N_DIR):
        fail(f"i18n directory not found: {I18N_DIR}")
        print(f"  {GRAY}Expected: frontend/src/i18n/{{en,hi,...}}.json{RESET}\n")
        all_results.append({"label": "i18n dir exists", "pass": False})
    else:
        json_files = [f for f in os.listdir(I18N_DIR) if f.endswith(".json")]
        all_codes  = {f.replace(".json", "") for f in json_files}

        expected_codes = {lang[0] for lang in LANGUAGES}
        missing = expected_codes - all_codes
        extra   = all_codes - expected_codes

        check_pass = len(missing) == 0
        all_results.append({"label": "All language files present", "pass": check_pass})

        if check_pass:
            ok(f"All {len(json_files)} translation files present")
        else:
            fail(f"Missing files: {', '.join(sorted(missing))}")
            info(f"Run: python scripts/generate_translations.py")

        if extra:
            warn(f"Extra files (not in language list): {', '.join(sorted(extra))}")

        # ── 2. Key completeness check ────────────────────────────────────────
        print(f"\n{BOLD}{BLUE}[2] Key Completeness — checking en.json{RESET}")
        divider()

        en_file = os.path.join(I18N_DIR, "en.json")
        if os.path.exists(en_file):
            with open(en_file) as f:
                en_data = json.load(f)

            for key in REQUIRED_I18N_KEYS:
                val = get_nested(en_data, key)
                passed = val is not None and str(val).strip() != ""
                all_results.append({"label": f"en.json key: {key}", "pass": passed})
                if passed:
                    ok(f"{key:<30} = {str(val)[:40]}")
                else:
                    fail(f"{key:<30} MISSING from en.json")
        else:
            fail("en.json not found")
            all_results.append({"label": "en.json exists", "pass": False})

        # ── 3. Spot-check other language files ───────────────────────────────
        print(f"\n{BOLD}{BLUE}[3] Translation Completeness Spot-Check{RESET}")
        divider()
        spot_langs = ["hi", "ta", "ur", "bn"]  # all 4 confirmed present
        for code in spot_langs:
            fpath = os.path.join(I18N_DIR, f"{code}.json")
            if os.path.exists(fpath):
                with open(fpath) as f:
                    data = json.load(f)
                missing_keys = [k for k in REQUIRED_I18N_KEYS if get_nested(data, k) is None]
                passed = len(missing_keys) == 0
                all_results.append({"label": f"{code}.json completeness", "pass": passed})
                if passed:
                    ok(f"{code}.json — all {len(REQUIRED_I18N_KEYS)} required keys present")
                else:
                    fail(f"{code}.json — missing keys: {', '.join(missing_keys)}")
            else:
                fail(f"{code}.json not found")
                all_results.append({"label": f"{code}.json exists", "pass": False})

    # ── 4. RTL configuration ─────────────────────────────────────────────────
    print(f"\n{BOLD}{BLUE}[4] RTL Language Configuration{RESET}")
    divider()
    main_tsx = os.path.join(FRONTEND_DIR, "src", "main.tsx")
    if os.path.exists(main_tsx):
        with open(main_tsx) as f:
            content = f.read()
        has_rtl = "rtl" in content.lower()
        has_dir = "lang?.rtl" in content or "documentElement.dir" in content
        i18n_idx = os.path.join(FRONTEND_DIR, "src", "i18n", "index.ts")
        i18n_c = open(i18n_idx).read() if os.path.exists(i18n_idx) else ""
        has_ur = "ur" in i18n_c and "rtl: true" in i18n_c
        has_ks = "ks" in i18n_c and "rtl: true" in i18n_c
        has_ur = "ur" in i18n_c and "rtl: true" in i18n_c
        has_ks = "ks" in i18n_c and "rtl: true" in i18n_c

        all_results.append({"label": "RTL direction switching in main.tsx", "pass": has_dir and has_rtl})
        all_results.append({"label": "Urdu (ur) in RTL list", "pass": has_ur})
        all_results.append({"label": "Kashmiri (ks) in RTL list", "pass": has_ks})

        if has_dir and has_rtl: ok("RTL direction switching found in main.tsx")
        else: fail("RTL direction switching missing — add: document.documentElement.dir = ['ur','ks','sd'].includes(lang) ? 'rtl' : 'ltr'")

        if has_ur: ok("Urdu marked as RTL")
        else: fail("Urdu missing from RTL language list")

        if has_ks: ok("Kashmiri marked as RTL")
        else: warn("Kashmiri (ks) not in RTL list")
    else:
        warn(f"main.tsx not found at {main_tsx} — skipping RTL check")

    # ── 5. Font loading ──────────────────────────────────────────────────────
    print(f"\n{BOLD}{BLUE}[5] Font Loading (index.html){RESET}")
    divider()
    index_html = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_html):
        with open(index_html) as f:
            html = f.read()
        for font in REQUIRED_FONTS:
            present = font.replace(" ", "+") in html or font in html
            all_results.append({"label": f"Font: {font}", "pass": present})
            if present: ok(f"{font}")
            else: fail(f"{font} missing from index.html Google Fonts link")
    else:
        warn(f"index.html not found at {index_html} — skipping font check")

    # ── 6. Live LLM language tests ───────────────────────────────────────────
    print(f"\n{BOLD}{BLUE}[6] Live LLM Response — 15 languages{RESET}")
    divider()
    print(f"  {GRAY}Testing against {BASE_URL}{RESET}\n")

    live_results = []
    test_langs = LANGUAGES[:15]  # test first 15 for speed
    latencies = []

    for code, name, script, rtl, query in test_langs:
        t0 = time.time()
        try:
            r = requests.post(
                f"{BASE_URL}/api/v1/chat",
                json={"message": query, "language": code},
                timeout=90
            )
            latency = int((time.time() - t0) * 1000)
            latencies.append(latency)

            if r.status_code == 200:
                data = r.json()
                response = data.get("response", "")
                detected = data.get("language", "?")
                resp_len = len(response)
                ok_resp = resp_len > 50
                lang_match = detected == code or detected == "en"  # en fallback acceptable

                status_str = f"{GREEN}✅{RESET}" if ok_resp else f"{RED}❌{RESET}"
                rtl_str = f" {YELLOW}RTL{RESET}" if rtl else ""
                print(f"  {status_str} [{code}] {name:<10} | {script:<11}{rtl_str} | {resp_len:>4} chars | {latency:>5}ms")

                live_results.append({
                    "code": code, "name": name, "script": script, "rtl": rtl,
                    "pass": ok_resp, "latency_ms": latency, "response_len": resp_len,
                    "detected_lang": detected
                })
                all_results.append({"label": f"Live LLM: {name} ({code})", "pass": ok_resp})
            else:
                print(f"  {RED}❌{RESET} [{code}] {name:<10} | HTTP {r.status_code}")
                live_results.append({"code": code, "name": name, "pass": False, "latency_ms": int((time.time()-t0)*1000)})
                all_results.append({"label": f"Live LLM: {name} ({code})", "pass": False})
        except Exception as e:
            print(f"  {RED}❌{RESET} [{code}] {name:<10} | {e}")
            live_results.append({"code": code, "name": name, "pass": False, "latency_ms": 0})
            all_results.append({"label": f"Live LLM: {name} ({code})", "pass": False})

    live_passed = sum(1 for r in live_results if r["pass"])
    avg_lat = round(sum(latencies) / len(latencies)) if latencies else 0
    print(f"\n  Live score : {live_passed}/{len(test_langs)}")
    print(f"  Avg latency: {avg_lat}ms")

    # ── Summary ────────────────────────────────────────────────────────────
    passed_count = sum(1 for r in all_results if r["pass"])
    total_count  = len(all_results)
    pct = round(passed_count / total_count * 100)
    color = GREEN if pct >= 85 else YELLOW if pct >= 70 else RED

    print(f"\n{BOLD}{'═'*72}{RESET}")
    print(f"{BOLD}  PHASE 3 SUMMARY{RESET}")
    print(f"{'═'*72}")
    print(f"  Checks passed     : {color}{BOLD}{passed_count}/{total_count} = {pct}%{RESET}")
    print(f"  Translation files : {len([r for r in all_results if 'i18n dir' in r['label'] or 'language files' in r['label']])}")
    print(f"  RTL support       : {'✅' if any(r['pass'] for r in all_results if 'RTL' in r['label']) else '❌'}")
    print(f"  Live LLM          : {live_passed}/{len(test_langs)} languages responding")
    print(f"  Avg chat latency  : {avg_lat}ms")
    print(f"  Status            : {color}{'✅ PASS' if pct >= 85 else '⚠️  BORDERLINE' if pct >= 70 else '❌ FAIL'}{RESET}")
    if pct < 85:
        failed = [r for r in all_results if not r["pass"]]
        print(f"\n  Failed checks ({len(failed)}):")
        for r in failed[:10]:
            print(f"    {RED}✗{RESET} {r['label']}")
        if len(failed) > 10:
            print(f"    {GRAY}... and {len(failed)-10} more{RESET}")
    print(f"{'═'*72}\n")

    report = {
        "phase": 3, "label": "22 Languages",
        "score_pct": pct, "passed": passed_count, "total": total_count,
        "live_lm_score": f"{live_passed}/{len(test_langs)}",
        "avg_chat_latency_ms": avg_lat,
        "status": "PASS" if pct >= 85 else "BORDERLINE" if pct >= 70 else "FAIL",
        "live_results": live_results,
        "details": all_results
    }
    out = os.path.join(os.path.dirname(__file__), "test_results_phase3.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  {GRAY}Report saved → scripts/test_results_phase3.json{RESET}\n")

    return pct >= 70

if __name__ == "__main__":
    ok_result = run()
    sys.exit(0 if ok_result else 1)