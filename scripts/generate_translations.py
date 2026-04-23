#!/usr/bin/env python3
import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend" / "src" / "i18n" / "locales"
SOURCE_FILE = FRONTEND_DIR / "en" / "translation.json"

SARVAM_API_URL = "https://api.sarvam.ai/translate"
SARVAM_MODEL = "sarvam-translate:v1"

LANG_CODE_MAP = {
    "hi": "hi-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "pa": "pa-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "or": "od-IN",
    "as": "as-IN",
    "ur": "ur-IN",
    "ks": "ks-IN",
    "sd": "sd-IN",
    "sa": "sa-IN",
    "ne": "ne-IN",
    "kok": "kok-IN",
    "mai": "mai-IN",
    "doi": "doi-IN",
    "mni": "mni-IN",
    "sat": "sat-IN",
}

TARGET_LANGUAGES = {
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu",
    "ks": "Kashmiri",
    "sd": "Sindhi",
    "sa": "Sanskrit",
    "ne": "Nepali",
    "kok": "Konkani",
    "mai": "Maithili",
    "doi": "Dogri",
    "mni": "Manipuri",
    "sat": "Santali",
}

LANGUAGE_SKIP_LIST = ["en"]

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY")

if not SARVAM_API_KEY:
    logger.warning("SARVAM_API_KEY environment variable not set")
    SARVAM_API_KEY = input("Enter Sarvam API Key: ").strip()

API_DELAY = 0.5


def load_json(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path: Path, data: Dict[str, Any]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, str]:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v)))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def translate_text(text: str, target_lang: str) -> Tuple[str, bool]:
    bcp47_code = LANG_CODE_MAP.get(target_lang, f"{target_lang}-IN")
    try:
        response = requests.post(
            SARVAM_API_URL,
            headers={
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "input": text,
                "source_language_code": "en-IN",
                "target_language_code": bcp47_code,
                "model": SARVAM_MODEL,
            },
            timeout=30,
        )

        if response.status_code == 429:
            logger.warning(f"Rate limited, waiting 5 seconds...")
            time.sleep(5)
            return translate_text(text, target_lang)

        if response.status_code != 200:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return text, False

        data = response.json()
        translated_text = data.get("translated_text", text)

        if not translated_text:
            logger.error(f"Empty response for language {target_lang}")
            return text, False

        return translated_text, True

    except requests.exceptions.Timeout:
        logger.error(f"Request timeout for {target_lang}")
        return text, False
    except Exception as e:
        logger.error(f"Error translating to {target_lang}: {e}")
        return text, False


def translate_flat_dict(flat_dict: Dict[str, str], target_lang: str) -> Dict[str, str]:
    translated = {}
    total = len(flat_dict)

    for idx, (key, value) in enumerate(flat_dict.items(), 1):
        translated_value, success = translate_text(value, target_lang)
        translated[key] = translated_value

        if success:
            logger.debug(f"Translated [{idx}/{total}]: {key}")
        else:
            logger.warning(f"Failed [{idx}/{total}]: {key}")

        if idx < total:
            time.sleep(API_DELAY)

    return translated


def get_existing_languages() -> List[str]:
    existing = []
    if FRONTEND_DIR.exists():
        for item in FRONTEND_DIR.iterdir():
            if item.is_dir() and (item / "translation.json").exists():
                existing.append(item.name)
    return existing


def count_characters(data: Dict[str, Any]) -> int:
    flat = flatten_dict(data)
    return sum(len(v) for v in flat.values())


def estimate_cost(char_count: int, num_langs: int) -> float:
    per_char_rate = 0.0001
    return char_count * num_langs * per_char_rate


def main():
    logger.info("=" * 60)
    logger.info("Sarvam AI Translation Generator")
    logger.info("=" * 60)

    if not SOURCE_FILE.exists():
        logger.error(f"Source file not found: {SOURCE_FILE}")
        return

    logger.info(f"Reading source file: {SOURCE_FILE}")
    source_data = load_json(SOURCE_FILE)

    source_char_count = count_characters(source_data)
    logger.info(f"Source character count: {source_char_count}")

    existing_languages = get_existing_languages()
    logger.info(
        f"Existing languages: {', '.join(existing_languages) if existing_languages else 'None'}"
    )

    languages_to_translate = [
        (code, name)
        for code, name in TARGET_LANGUAGES.items()
        if code not in LANGUAGE_SKIP_LIST and code not in existing_languages
    ]

    if not languages_to_translate:
        logger.info("All languages already translated!")
        return

    total_langs = len(languages_to_translate)
    logger.info(f"Languages to translate: {total_langs}")
    logger.info(
        f"Estimated cost: ~${estimate_cost(source_char_count, total_langs):.2f}"
    )

    flat_source = flatten_dict(source_data)

    successful = []
    failed = []

    for idx, (lang_code, lang_name) in enumerate(languages_to_translate, 1):
        logger.info(
            f"\n[{idx}/{total_langs}] Translating to {lang_name} ({lang_code})..."
        )

        output_file = FRONTEND_DIR / lang_code / "translation.json"

        try:
            translated_flat = translate_flat_dict(flat_source, lang_code)
            translated_data = unflatten_dict(translated_flat)

            save_json(output_file, translated_data)

            logger.info(f"✓ Saved: {output_file}")
            successful.append(lang_code)

        except Exception as e:
            logger.error(f"✗ Failed to save {lang_code}: {e}")
            failed.append(lang_code)

    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total languages: {total_langs}")
    logger.info(
        f"Successful: {len(successful)} - {', '.join(successful) if successful else 'None'}"
    )
    logger.info(f"Failed: {len(failed)} - {', '.join(failed) if failed else 'None'}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
