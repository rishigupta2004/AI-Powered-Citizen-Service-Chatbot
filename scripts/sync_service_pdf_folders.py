from __future__ import annotations

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = ROOT / "data" / "docs"
PROFILES_DIR = DOCS_ROOT / "national_profiles"
SERVICES_DIR = DOCS_ROOT / "services"


def candidate_folders(service_slug: str) -> list[str]:
    slug = service_slug.lower()
    mapping: list[tuple[str, str]] = [
        ("aadhaar", "aadhaar"),
        ("myaadhaar", "aadhaar"),
        ("passport", "passport"),
        ("pan", "pan"),
        ("income_tax", "pan"),
        ("gst", "pan"),
        ("epfo", "epfo"),
        ("parivahan", "parivahan"),
        ("sarathi", "parivahan"),
        ("vahan", "parivahan"),
        ("rail", "railways"),
        ("rbi", "rbi"),
        ("scholar", "education"),
        ("swayam", "education"),
        ("diksha", "education"),
        ("education", "education"),
    ]
    matched: list[str] = []
    for token, folder in mapping:
        if token in slug and folder not in matched:
            matched.append(folder)
    if "other" not in matched:
        matched.append("other")
    return matched


def link_or_copy(src: Path, dst: Path) -> None:
    if dst.exists() and not dst.is_symlink():
        return
    if dst.exists() and dst.is_symlink():
        dst.unlink(missing_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    SERVICES_DIR.mkdir(parents=True, exist_ok=True)
    profile_files = sorted(PROFILES_DIR.glob("*.md"))
    if not profile_files:
        raise SystemExit("No service profiles found in data/docs/national_profiles")

    created = 0
    linked = 0
    for profile in profile_files:
        service_slug = profile.stem
        out_dir = SERVICES_DIR / service_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        created += 1

        for folder in candidate_folders(service_slug):
            folder_path = DOCS_ROOT / folder
            if not folder_path.exists() or not folder_path.is_dir():
                continue
            for pdf in sorted(folder_path.glob("*.pdf")):
                dst = out_dir / pdf.name
                if dst.exists():
                    continue
                link_or_copy(pdf, dst)
                linked += 1

    print(f"Prepared {created} service folders")
    print(f"Linked/copied {linked} PDF files")


if __name__ == "__main__":
    main()
