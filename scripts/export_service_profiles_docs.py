"""Export seeded national service profiles to data/docs for traceability."""

from __future__ import annotations

from pathlib import Path

from scripts.seed_national_services import LAST_VERIFIED, SEEDS


OUTPUT_DIR = Path("data/docs/national_profiles")


def sanitize(name: str) -> str:
    return (
        name.lower()
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
        .replace("/", "-")
        .replace(" ", "-")
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for seed in SEEDS:
        slug = sanitize(seed.slug)
        path = OUTPUT_DIR / f"{slug}.md"
        body = (
            f"# {seed.name}\n\n"
            f"- Category: {seed.category}\n"
            f"- Mode: {seed.mode}\n"
            f"- Official Authority: {seed.authority}\n"
            f"- Official URL: {seed.url}\n"
            f"- Last Verified: {LAST_VERIFIED}\n\n"
            f"## Overview\n{seed.summary}\n"
        )
        path.write_text(body, encoding="utf-8")
    print(f"Exported {len(SEEDS)} service profiles to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
