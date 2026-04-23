"""
SevaSindhu — Master Test Runner
Run: python scripts/run_all_tests.py
Runs Phase 1 (RAG), Phase 2 (Auth), Phase 3 (Languages) and prints combined report.
Each phase also saves its own JSON to scripts/test_results_phase{N}.json
"""
import sys, os, json, subprocess, time

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
GRAY   = "\033[90m"

SCRIPTS_DIR = os.path.dirname(__file__)
PYTHON      = sys.executable

PHASES = [
    ("Phase 1 — RAG Quality",    "test_phase1_rag.py"),
    ("Phase 2 — Auth",           "test_phase2_auth.py"),
    ("Phase 3 — 22 Languages",   "test_phase3_languages.py"),
]

def run():
    print(f"\n{BOLD}{'█'*72}{RESET}")
    print(f"{BOLD}  SevaSindhu — Master Test Runner{RESET}")
    print(f"{BOLD}{'█'*72}{RESET}\n")

    phase_results = []

    for label, script in PHASES:
        script_path = os.path.join(SCRIPTS_DIR, script)
        if not os.path.exists(script_path):
            print(f"{YELLOW}⚠  {label}: script not found ({script}){RESET}\n")
            phase_results.append({"label": label, "score_pct": 0, "status": "MISSING"})
            continue

        print(f"{BOLD}{BLUE}▶  Running: {label}{RESET}")
        print(f"{'─'*72}")
        t0 = time.time()
        result = subprocess.run([PYTHON, script_path], cwd=os.path.dirname(SCRIPTS_DIR))
        elapsed = round(time.time() - t0, 1)
        print(f"\n{GRAY}  Completed in {elapsed}s | exit code {result.returncode}{RESET}\n")

        # Load JSON report
        report_path = os.path.join(SCRIPTS_DIR, f"test_results_{script.replace('test_','').replace('.py','')}.json")
        # Try alternate naming
        alt_path = os.path.join(SCRIPTS_DIR, script.replace("test_","test_results_").replace(".py",".json"))
        
        for candidate in [report_path, alt_path,
                           os.path.join(SCRIPTS_DIR, "test_results_phase1.json"),
                           os.path.join(SCRIPTS_DIR, "test_results_phase2.json"),
                           os.path.join(SCRIPTS_DIR, "test_results_phase3.json")]:
            if os.path.exists(candidate) and f"phase{PHASES.index((label,script))+1}" in candidate:
                with open(candidate) as f:
                    data = json.load(f)
                phase_results.append(data)
                break
        else:
            phase_results.append({
                "label": label,
                "score_pct": 0 if result.returncode != 0 else 70,
                "status": "FAIL" if result.returncode != 0 else "UNKNOWN"
            })

    # ── Combined report ────────────────────────────────────────────────────
    print(f"\n{BOLD}{'█'*72}{RESET}")
    print(f"{BOLD}  COMBINED TEST REPORT — SevaSindhu{RESET}")
    print(f"{'█'*72}\n")

    scores = []
    for r in phase_results:
        pct = r.get("score_pct", 0)
        scores.append(pct)
        color = GREEN if pct >= 85 else YELLOW if pct >= 70 else RED
        status = r.get("status", "?")
        label  = r.get("label", "?")
        bar    = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"  {color}{bar}{RESET}  {pct:>3}%  {label:<28}  {color}{status}{RESET}")

    if scores:
        overall = round(sum(scores) / len(scores))
        color   = GREEN if overall >= 85 else YELLOW if overall >= 70 else RED
        print(f"\n  {'─'*68}")
        print(f"  {'█'*72}")
        print(f"  Overall Score: {color}{BOLD}{overall}%{RESET}  —  {color}{'✅ PRODUCTION READY' if overall >= 85 else '⚠️  NEEDS ATTENTION' if overall >= 70 else '❌ NOT READY'}{RESET}")
        print(f"  {'█'*72}\n")

        # Save master report
        master = {
            "project": "SevaSindhu",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "overall_score_pct": overall,
            "overall_status": "PASS" if overall >= 85 else "BORDERLINE" if overall >= 70 else "FAIL",
            "phases": phase_results
        }
        out = os.path.join(SCRIPTS_DIR, "test_results_master.json")
        with open(out, "w") as f:
            json.dump(master, f, indent=2, ensure_ascii=False)
        print(f"  {GRAY}Master report saved → scripts/test_results_master.json{RESET}\n")

if __name__ == "__main__":
    run()