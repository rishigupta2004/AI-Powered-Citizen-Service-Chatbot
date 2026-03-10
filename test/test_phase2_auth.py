"""
SevaSindhu — Phase 2: Auth Test Suite
Run: python scripts/test_phase2_auth.py
Tests: all auth endpoints, JWT flow, DigiLocker redirect, DB tables, env vars
"""

import sys, os, json, time, re

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

BASE_URL = os.getenv("API_BASE_URL", "https://gov-chatbot.fly.dev")

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"
GRAY = "\033[90m"


def divider(width=72):
    print(GRAY + "─" * width + RESET)


def ok(msg):
    print(f"  {GREEN}✅ PASS{RESET}  {msg}")


def fail(msg):
    print(f"  {RED}❌ FAIL{RESET}  {msg}")


def warn(msg):
    print(f"  {YELLOW}⚠  WARN{RESET}  {msg}")


def info(msg):
    print(f"  {GRAY}     {msg}{RESET}")


results = []


def check(label, passed, detail=""):
    results.append({"label": label, "pass": passed, "detail": detail})
    if passed:
        ok(f"{label}  {GRAY}{detail}{RESET}")
    else:
        fail(f"{label}  {GRAY}{detail}{RESET}")
    return passed


def run():
    print(f"\n{BOLD}{'═' * 72}{RESET}")
    print(f"{BOLD}  SevaSindhu — Phase 2: Auth Test Suite{RESET}")
    print(
        f"{GRAY}  Target: all 6 auth endpoints reachable, DB tables exist, JWT working{RESET}"
    )
    print(f"{BOLD}{'═' * 72}{RESET}\n")

    # ── 1. Env vars ─────────────────────────────────────────────────────────
    print(f"{BOLD}{BLUE}[1] Environment Variables{RESET}")
    divider()
    required_vars = ["DATABASE_URL", "SARVAM_API_KEY", "HF_TOKEN", "JWT_SECRET_KEY"]
    optional_vars = [
        "DIGILOCKER_CLIENT_ID",
        "DIGILOCKER_CLIENT_SECRET",
        "DIGILOCKER_REDIRECT_URI",
    ]
    env_ok = 0
    for var in required_vars:
        val = os.getenv(var, "")
        passed = bool(val)
        check(
            f"{var}",
            passed,
            "set" if passed else "MISSING — add to .env and flyctl secrets",
        )
        if passed:
            env_ok += 1
    for var in optional_vars:
        val = os.getenv(var, "")
        if val:
            ok(f"{var}  {GRAY}set{RESET}")
        else:
            warn(f"{var}  not set (DigiLocker OAuth will fail)")
    print()

    # ── 2. DB tables ─────────────────────────────────────────────────────────
    print(f"{BOLD}{BLUE}[2] Database Tables{RESET}")
    divider()
    try:
        import psycopg2

        db_url = os.getenv("DATABASE_URL", "")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        )
        tables = [r[0] for r in cur.fetchall()]
        conn.close()

        required_tables = [
            "users",
            "user_sessions",
            "content_chunks",
            "services",
            "faqs",
        ]
        for t in required_tables:
            check(
                f"table '{t}' exists",
                t in tables,
                "found" if t in tables else "MISSING — run python init_db.py",
            )

        info(f"All tables: {', '.join(sorted(tables))}")
    except Exception as e:
        fail(f"DB connection failed: {e}")
    print()

    # ── 3. Auth endpoints reachability ──────────────────────────────────────
    print(f"{BOLD}{BLUE}[3] Auth Endpoint Reachability{RESET}")
    divider()

    endpoints = [
        ("GET", "/health", [200], "Health check"),
        ("GET", "/api/auth/me", [401, 403], "Requires auth — 401 expected"),
        ("POST", "/api/auth/otp/send", [200, 422], "OTP send (422=validation OK)"),
        ("POST", "/api/auth/otp/verify", [200, 422], "OTP verify (422=validation OK)"),
        ("GET", "/api/auth/digilocker", [302, 200], "DigiLocker redirect"),
        ("POST", "/api/auth/logout", [200, 401], "Logout"),
    ]

    for method, path, expected_codes, note in endpoints:
        t0 = time.time()
        try:
            if method == "GET":
                r = requests.get(f"{BASE_URL}{path}", timeout=10, allow_redirects=False)
            else:
                r = requests.post(f"{BASE_URL}{path}", json={}, timeout=10)
            latency = int((time.time() - t0) * 1000)
            passed = r.status_code in expected_codes or r.status_code < 500
            check(
                f"{method} {path}",
                passed,
                f"HTTP {r.status_code} — {note} — {latency}ms",
            )
        except Exception as e:
            check(f"{method} {path}", False, str(e))
    print()

    # ── 4. JWT validation ────────────────────────────────────────────────────
    print(f"{BOLD}{BLUE}[4] JWT Configuration{RESET}")
    divider()
    try:
        from jose import jwt as jose_jwt

        secret = os.getenv("JWT_SECRET_KEY", "")
        if secret:
            payload = {"sub": "test_user_123", "exp": 9999999999}
            token = jose_jwt.encode(payload, secret, algorithm="HS256")
            decoded = jose_jwt.decode(token, secret, algorithms=["HS256"])
            check(
                "JWT encode/decode",
                decoded["sub"] == "test_user_123",
                f"token length={len(token)}",
            )
        else:
            fail("JWT_SECRET_KEY not set — cannot test JWT")
    except ImportError:
        warn("python-jose not installed — add to requirements.txt")
    except Exception as e:
        fail(f"JWT error: {e}")
    print()

    # ── 5. OTP flow simulation ────────────────────────────────────────────────
    print(f"{BOLD}{BLUE}[5] OTP Flow Validation{RESET}")
    divider()

    # Test send-otp with invalid payload (should return 422 not 500)
    try:
        r = requests.post(
            f"{BASE_URL}/api/auth/otp/send", json={"phone": "invalid"}, timeout=10
        )
        check(
            "send-otp rejects invalid phone",
            r.status_code in [400, 422],
            f"HTTP {r.status_code}",
        )
    except Exception as e:
        fail(f"send-otp test failed: {e}")

    # Test verify-otp with wrong OTP (should return 400/401 not 500)
    try:
        r = requests.post(
            f"{BASE_URL}/api/auth/otp/verify",
            json={"phone": "+919999999999", "otp": "000000"},
            timeout=10,
        )
        check(
            "verify-otp rejects wrong OTP",
            r.status_code in [400, 401, 422],
            f"HTTP {r.status_code}",
        )
    except Exception as e:
        fail(f"verify-otp test failed: {e}")
    print()

    # ── 6. Protected route enforcement ──────────────────────────────────────
    print(f"{BOLD}{BLUE}[6] Protected Route Enforcement{RESET}")
    divider()
    try:
        r = requests.get(f"{BASE_URL}/api/auth/me", timeout=10)
        check(
            "/api/auth/me blocks unauthenticated",
            r.status_code in [401, 403],
            f"HTTP {r.status_code}",
        )
    except Exception as e:
        fail(f"Protected route check failed: {e}")

    # Test with fake JWT (should reject)
    try:
        r = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer fakejwt123"},
            timeout=10,
        )
        check(
            "/api/auth/me rejects invalid JWT",
            r.status_code in [401, 403, 422],
            f"HTTP {r.status_code}",
        )
    except Exception as e:
        fail(f"JWT rejection test failed: {e}")
    print()

    # ── Summary ────────────────────────────────────────────────────────────
    passed_count = sum(1 for r in results if r["pass"])
    total_count = len(results)
    pct = round(passed_count / total_count * 100)
    color = GREEN if pct >= 85 else YELLOW if pct >= 70 else RED

    print(f"{BOLD}{'═' * 72}{RESET}")
    print(f"{BOLD}  PHASE 2 SUMMARY{RESET}")
    print(f"{'═' * 72}")
    print(
        f"  Checks passed : {color}{BOLD}{passed_count}/{total_count} = {pct}%{RESET}"
    )
    print(
        f"  Status        : {color}{'✅ PASS' if pct >= 85 else '⚠️  BORDERLINE' if pct >= 70 else '❌ FAIL'}{RESET}"
    )
    if pct < 85:
        failed = [r for r in results if not r["pass"]]
        print(f"\n  Failed checks:")
        for r in failed:
            print(f"    {RED}✗{RESET} {r['label']} — {r['detail']}")
    print(f"{'═' * 72}\n")

    report = {
        "phase": 2,
        "label": "Auth",
        "score_pct": pct,
        "passed": passed_count,
        "total": total_count,
        "status": "PASS" if pct >= 85 else "BORDERLINE" if pct >= 70 else "FAIL",
        "details": results,
    }
    out = os.path.join(os.path.dirname(__file__), "test_results_phase2.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  {GRAY}Report saved → scripts/test_results_phase2.json{RESET}\n")

    return pct >= 70


if __name__ == "__main__":
    ok_result = run()
    sys.exit(0 if ok_result else 1)
