"""
Bloat Report - identifies large files and long functions to target refactors.

Run: python scripts/bloat_report.py
"""
import os
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def list_py_files(base: Path):
    for p in base.rglob('*.py'):
        if any(seg in {'.venv','node_modules','__pycache__'} for seg in p.parts):
            continue
        yield p

def line_count(p: Path) -> int:
    try:
        return sum(1 for _ in p.open('r', encoding='utf-8', errors='ignore'))
    except Exception:
        return 0

def top_n_files(n=20):
    files = [(line_count(p), p) for p in list_py_files(ROOT)]
    files.sort(reverse=True)
    return files[:n]

def long_functions(p: Path, min_lines=60):
    try:
        src = p.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(src)
        lines = src.splitlines()
        out = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                length = (node.end_lineno or node.lineno) - node.lineno + 1
                if length >= min_lines:
                    out.append((node.name, length))
        return sorted(out, key=lambda x: x[1], reverse=True)
    except Exception:
        return []

def main():
    print("=== Bloat Report ===")
    print("Top large files (by LOC):")
    for cnt, p in top_n_files():
        print(f"{cnt:5d}  {p.relative_to(ROOT)}")
    print("\nFunctions >= 60 lines:")
    for _, p in top_n_files(50):  # scan more for functions
        funcs = long_functions(p)
        if funcs:
            print(f"\n{p.relative_to(ROOT)}")
            for name, length in funcs[:10]:
                print(f"  - {name} ({length} lines)")
    print("\nTip: target large files/functions first; prefer early returns and helpers.")

if __name__ == '__main__':
    main()

