"""

FastAPI Backend - Mạt Thế Sinh Hoá Nguy Cơ

Cung cấp API metadata chương. Nội dung chương được fetch từ Cloudflare R2.

"""

import asyncio
import io
import hashlib
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
# Force re-deploy to Vercel and Render (Trigger: 2026-03-25 23:14)
from time import monotonic
from typing import Optional, List, Callable, TypeVar, Any
from urllib.parse import quote

import boto3

from botocore.client import Config

import httpx

from fastapi import FastAPI, HTTPException, Query, Header, status, UploadFile, File

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse, PlainTextResponse

from pydantic import BaseModel

from supabase import create_client, Client

from dotenv import load_dotenv

import sys

# Add both current and parent directory to sys.path for maximum compatibility

current_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:

    sys.path.insert(0, current_dir)

if parent_dir not in sys.path:

    sys.path.insert(0, parent_dir)

# Consolidated imports with intelligent fallback

try:

    # Try importing as top-level modules first (when running from within backend/)

    from security_utils import sanitize_html, sanitize_plaintext, extract_bearer_token
    from prompts.translation_prompts import (
        build_chapter_multilocale_system_instruction,
        build_chapter_multilocale_user_prompt,
        build_chapter_refine_system_instruction,
        build_chapter_refine_user_prompt,
        build_guide_multilocale_system_instruction,
        build_guide_multilocale_user_prompt,
        build_homepage_multilocale_system_instruction,
        build_homepage_multilocale_user_prompt,
        build_homepage_translation_prompt,
        build_wiki_multilocale_system_instruction,
        build_wiki_multilocale_user_prompt,
        build_wiki_translation_prompt,
    )

    from routes.engagement import create_engagement_router

    from routes.hq_dashboard import router as hq_router

    from routes.ai_oracle import router as oracle_router

    from routes.wiki_search import router as wiki_router
    from routes.reader_learning import router as reader_learning_router
    from routes.reader_grammar import router as reader_grammar_router

except (ImportError, ModuleNotFoundError):

    # Fallback to absolute imports (when running from project root)

    from backend.security_utils import sanitize_html, sanitize_plaintext, extract_bearer_token
    from backend.prompts.translation_prompts import (
        build_chapter_multilocale_system_instruction,
        build_chapter_multilocale_user_prompt,
        build_chapter_refine_system_instruction,
        build_chapter_refine_user_prompt,
        build_guide_multilocale_system_instruction,
        build_guide_multilocale_user_prompt,
        build_homepage_multilocale_system_instruction,
        build_homepage_multilocale_user_prompt,
        build_homepage_translation_prompt,
        build_wiki_multilocale_system_instruction,
        build_wiki_multilocale_user_prompt,
        build_wiki_translation_prompt,
    )

    from backend.routes.engagement import create_engagement_router

    from backend.routes.hq_dashboard import router as hq_router

    from backend.routes.ai_oracle import router as oracle_router

    from backend.routes.wiki_search import router as wiki_router
    from backend.routes.reader_learning import router as reader_learning_router
    from backend.routes.reader_grammar import router as reader_grammar_router

load_dotenv(override=True)

# === SUPABASE CLIENT ===

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:

    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be configured in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === CLOUDFLARE R2 CLIENT ===

R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID")

R2_SECRET_KEY = os.getenv("R2_SECRET_ACCESS_KEY")

# Support both R2_ENDPOINT_URL (old) and R2_ENDPOINT (new on Render)

R2_ENDPOINT = os.getenv("R2_ENDPOINT_URL") or os.getenv("R2_ENDPOINT")

R2_BUCKET = os.getenv("R2_BUCKET_NAME", "mat-the")

# Support both R2_PUBLIC_URL and R2_PUBLIC_BASE_URL

R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL") or os.getenv("R2_PUBLIC_BASE_URL") or ""

r2_client = None

if R2_ACCESS_KEY and R2_SECRET_KEY and R2_ENDPOINT:

    r2_client = boto3.client(

        's3',

        endpoint_url=R2_ENDPOINT,

        aws_access_key_id=R2_ACCESS_KEY,

        aws_secret_access_key=R2_SECRET_KEY,

        config=Config(signature_version='s3v4'),

        region_name='auto',

    )

def slugify(text: str) -> str:
    """Convert Vietnamese text to ASCII slug for use as R2 object key."""
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

SUPPORTED_LOCALES = ("vi", "en", "zh-CN", "ja")
DEFAULT_LOCALE = "vi"
TRANSLATION_TARGET_LOCALES = ("en", "zh-CN", "ja")
TRANSLATION_LOCALE_LABELS = {
    "en": "English",
    "zh-CN": "Simplified Chinese",
    "ja": "Japanese",
}
TRANSLATION_GLOSSARY_PATH = os.path.join(current_dir, "translation_glossary.json")
DEFAULT_TRANSLATION_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemma-3n-1b-it",
    "gemma-3n-e2b-it",
    "gemma-3-4b-it",
    "gemma-3-12b-it",
    "gemma-3-27b-it",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
]
BULK_TRANSLATION_MODEL_FALLBACK = "gemini-2.5-flash-lite"
QUALITY_TRANSLATION_MODEL_FALLBACK = "gemini-2.5-flash"
TRANSLATION_MODEL_FALLBACK = BULK_TRANSLATION_MODEL_FALLBACK
MODEL_PRIORITY = {model: index for index, model in enumerate(DEFAULT_TRANSLATION_MODELS)}
MODEL_MIN_INTERVAL_SECONDS = {
    "gemini-3-flash-preview": 12.5,
    "gemini-2.5-flash": 12.5,
    "gemini-2.5-flash-lite": 6.5,
    "gemini-3.1-flash-lite-preview": 4.5,
    "gemini-robotics-er-1.5-preview": 6.5,
    "gemma-3-27b-it": 2.5,
    "gemma-3-12b-it": 2.5,
    "gemma-3-4b-it": 2.5,
    "gemma-3n-e2b-it": 2.5,
    "gemma-3n-1b-it": 2.5,
}
TRANSLATION_MAX_OUTPUT_TOKENS = 65536
TRANSLATION_MULTI_LOCALE_MAX_SOURCE_CHARS = 4000
TRANSLATION_ALIGNMENT_MAX_SENTENCE_CHARS = 360
TRANSLATION_ALIGNMENT_VERSION = 2
TRANSLATION_PUBLISH_MIN_SENTENCE_RATIO = 0.67
TRANSLATION_PUBLISH_MAX_SENTENCE_RATIO = 1.5
TRANSLATION_PUBLISH_MAX_BLOCK_DELTA = 8
TRANSLATION_PUBLISH_MIN_ALIGNMENT_ENTRIES = 1
VIETNAMESE_TEXT_HINTS = set("ăâêôơưđàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵĂÂÊÔƠƯĐÀÁẢÃẠẰẮẲẴẶẦẤẨẪẬÈÉẺẼẸỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌỒỐỔỖỘỜỚỞỠỢÙÚỦŨỤỪỨỬỮỰỲÝỶỸỴ")
TRANSLATION_RATE_LIMIT_STATE: dict[str, float] = {}
TRANSLATION_RATE_LIMIT_LOCK = asyncio.Lock()
CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED: Optional[bool] = None
T = TypeVar("T")

def normalize_locale(value: Optional[str]) -> str:
    if not value:
        return DEFAULT_LOCALE
    if value in SUPPORTED_LOCALES:
        return value
    lowered = value.lower()
    if lowered.startswith("vi"):
        return "vi"
    if lowered.startswith("en"):
        return "en"
    if lowered.startswith("zh"):
        return "zh-CN"
    if lowered.startswith("ja"):
        return "ja"
    return DEFAULT_LOCALE

def safe_select(table_name: str, select_fields: str = "*"):
    try:
        return supabase.table(table_name).select(select_fields)
    except Exception:
        return None

def build_content_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def chapter_translation_alignment_supported() -> bool:
    global CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED
    if CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED is not None:
        return CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED
    try:
        supabase.table("chapter_translations").select("sentence_alignment").limit(1).execute()
        CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED = True
    except Exception:
        CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED = False
    return CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED

def load_translation_glossary() -> list[dict]:
    try:
        with open(TRANSLATION_GLOSSARY_PATH, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
            if isinstance(payload, list):
                return payload
    except Exception:
        pass
    return []

def build_glossary_prompt() -> str:
    glossary = load_translation_glossary()
    if not glossary:
        return "Không có glossary bổ sung."

    lines = []
    for item in glossary:
        source = item.get("source", "").strip()
        if not source:
            continue
        translations = item.get("translations", {})
        if not isinstance(translations, dict):
            continue
        mapped = ", ".join(f"{k}={v}" for k, v in translations.items() if v)
        if mapped:
            lines.append(f"- {source}: {mapped}")
    return "\n".join(lines) if lines else "Không có glossary bổ sung."

def build_target_translation_locales(locales: Optional[List[str]] = None) -> list[str]:
    if not locales:
        return list(TRANSLATION_TARGET_LOCALES)

    normalized: list[str] = []
    for item in locales:
        locale = normalize_locale(item)
        if locale == DEFAULT_LOCALE or locale not in TRANSLATION_TARGET_LOCALES:
            continue
        if locale not in normalized:
            normalized.append(locale)
    return normalized

def build_target_locale_prompt(locales: list[str]) -> str:
    lines = []
    for locale in locales:
        locale_name = TRANSLATION_LOCALE_LABELS.get(locale, locale)
        lines.append(f'- "{locale}": {locale_name}')
    return "\n".join(lines)

def build_multilocale_object_schema(target_locales: list[str], field_schemas: dict[str, dict[str, Any]]) -> dict:
    ordered_fields = list(field_schemas.keys())
    locale_properties = {
        locale: {
            "type": "object",
            "properties": field_schemas,
            "required": ordered_fields,
            "additionalProperties": False,
        }
        for locale in target_locales
    }
    return {
        "type": "object",
        "properties": {
            "translations": {
                "type": "object",
                "properties": locale_properties,
                "required": target_locales,
                "additionalProperties": False,
            }
        },
        "required": ["translations"],
        "additionalProperties": False,
    }

def extract_gemini_text_response(data: dict) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        raise ValueError("Missing Gemini candidates")

    parts = candidates[0].get("content", {}).get("parts") or []
    text_parts = [str(part.get("text") or "").strip() for part in parts if part.get("text")]
    text = "\n".join(item for item in text_parts if item).strip()
    if not text:
        raise ValueError("Missing Gemini text response")
    return text

def chunk_translation_source_text(source_text: str, max_chars: int = TRANSLATION_MULTI_LOCALE_MAX_SOURCE_CHARS) -> list[str]:
    normalized = (source_text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return [""]
    if len(normalized) <= max_chars:
        return [normalized]

    chunks: list[str] = []
    remaining = normalized
    min_boundary = max(int(max_chars * 0.5), 1)

    while len(remaining) > max_chars:
        cut = remaining.rfind("\n\n", 0, max_chars + 1)
        if cut < min_boundary:
            cut = remaining.rfind("\n", 0, max_chars + 1)
        if cut < min_boundary:
            cut = remaining.rfind(" ", 0, max_chars + 1)
        if cut < min_boundary:
            cut = max_chars

        chunk = remaining[:cut].strip()
        if not chunk:
            chunk = remaining[:max_chars].strip()
            cut = len(chunk)

        chunks.append(chunk)
        remaining = remaining[cut:].strip()

    if remaining:
        chunks.append(remaining)
    return chunks

def split_text_into_chunk_count(source_text: str, chunk_count: int) -> list[str]:
    normalized = (source_text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if chunk_count <= 1:
        return [normalized]
    if not normalized:
        return [""] * chunk_count

    paragraphs = [item.strip() for item in normalized.split("\n\n") if item.strip()]
    if not paragraphs:
        paragraphs = [normalized]

    chunk_count = max(1, chunk_count)
    total_chars = sum(len(paragraph) for paragraph in paragraphs)
    target_chars = max(int(total_chars / chunk_count), 1)
    groups: list[list[str]] = []
    current_group: list[str] = []
    current_length = 0
    remaining_paragraphs = len(paragraphs)
    remaining_chunks = chunk_count

    for paragraph in paragraphs:
        current_group.append(paragraph)
        current_length += len(paragraph)
        remaining_paragraphs -= 1
        if remaining_chunks <= 1:
            continue
        if current_length >= target_chars and remaining_paragraphs >= (remaining_chunks - 1):
            groups.append(current_group)
            current_group = []
            current_length = 0
            remaining_chunks -= 1

    if current_group:
        groups.append(current_group)

    while len(groups) < chunk_count:
        groups.append([])

    return ["\n\n".join(group).strip() for group in groups[:chunk_count]]


def _strip_html_for_alignment(text: Optional[str]) -> str:
    if not text:
        return ""
    normalized = re.sub(r"(?i)<br\s*/?>", "\n", text)
    normalized = re.sub(r"(?i)</p\s*>", "\n\n", normalized)
    normalized = re.sub(r"(?i)</div\s*>", "\n\n", normalized)
    normalized = re.sub(r"<[^>]+>", "", normalized)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.strip()


def _split_sentences_for_alignment(text: Optional[str]) -> list[str]:
    plain = _strip_html_for_alignment(text)
    if not plain:
        return []
    parts = re.split(r"(?<=[。！？])|(?<=[.!?])\s+|\n+", plain)
    sentences = [" ".join(part.strip().split()) for part in parts if part and part.strip()]
    return sentences if sentences else [plain]


def _cap_alignment_sentence(text: str, max_chars: int = TRANSLATION_ALIGNMENT_MAX_SENTENCE_CHARS) -> str:
    cleaned = " ".join((text or "").strip().split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rstrip()


def _join_sentence_window_for_alignment(sentences: list[str], start_index: int, end_index: int) -> str:
    if not sentences:
        return ""
    safe_start = max(0, min(start_index, len(sentences) - 1))
    safe_end = max(safe_start, min(end_index, len(sentences) - 1))
    return " ".join(item for item in sentences[safe_start : safe_end + 1] if item).strip()


def build_chapter_sentence_alignment(
    source_text: str,
    translated_text: str,
    *,
    source_chunks: Optional[list[str]] = None,
    translated_chunks: Optional[list[str]] = None,
) -> dict[str, Any]:
    safe_source_chunks = source_chunks or chunk_translation_source_text(source_text)
    if translated_chunks is not None:
        safe_translated_chunks = translated_chunks
    else:
        safe_translated_chunks = split_text_into_chunk_count(translated_text, len(safe_source_chunks))

    chunk_count = max(len(safe_source_chunks), len(safe_translated_chunks))
    entries: list[dict[str, Any]] = []
    source_sentence_total = 0
    translated_sentence_total = 0

    for chunk_index in range(chunk_count):
        source_chunk = safe_source_chunks[chunk_index] if chunk_index < len(safe_source_chunks) else ""
        translated_chunk = safe_translated_chunks[chunk_index] if chunk_index < len(safe_translated_chunks) else ""
        source_sentences = _split_sentences_for_alignment(source_chunk)
        translated_sentences = _split_sentences_for_alignment(translated_chunk)

        source_count = len(source_sentences)
        translated_count = len(translated_sentences)
        if source_count == 0 or translated_count == 0:
            source_sentence_total += source_count
            translated_sentence_total += translated_count
            continue

        source_offset = source_sentence_total
        translated_offset = translated_sentence_total

        for translated_local_index, translated_sentence in enumerate(translated_sentences):
            source_start_local = int((translated_local_index * source_count) / translated_count)
            source_end_local = int(((translated_local_index + 1) * source_count) / translated_count) - 1
            source_end_local = min(source_count - 1, max(source_start_local, source_end_local))
            source_excerpt = _join_sentence_window_for_alignment(
                source_sentences,
                source_start_local,
                source_end_local,
            )
            if not source_excerpt:
                continue
            entries.append(
                {
                    "translated_index": translated_offset + translated_local_index,
                    "source_start": source_offset + source_start_local,
                    "source_end": source_offset + source_end_local,
                    "translated_excerpt": _cap_alignment_sentence(translated_sentence),
                    "source_excerpt": _cap_alignment_sentence(source_excerpt),
                    "chunk_index": chunk_index,
                }
            )

        source_sentence_total += source_count
        translated_sentence_total += translated_count

    return {
        "version": TRANSLATION_ALIGNMENT_VERSION,
        "strategy": "chunk_proportional_sentence_map",
        "source_locale": DEFAULT_LOCALE,
        "source_content_hash": build_content_hash(_strip_html_for_alignment(source_text)),
        "translated_content_hash": build_content_hash(_strip_html_for_alignment(translated_text)),
        "chunk_count": chunk_count,
        "source_sentence_count": source_sentence_total,
        "translated_sentence_count": translated_sentence_total,
        "entries": entries,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _normalize_translation_quality_text(text: Optional[str]) -> str:
    normalized = _strip_html_for_alignment(text).lower()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[^\w\s\u00C0-\u024F\u3040-\u30ff\u3400-\u9fff]", "", normalized)
    return normalized.strip()


def _filtered_sentence_count_for_translation_quality(text: Optional[str]) -> int:
    return len(
        [
            sentence
            for sentence in _split_sentences_for_alignment(text)
            if len(_normalize_translation_quality_text(sentence)) >= 6
        ]
    )


def _split_text_blocks_for_translation_quality(text: Optional[str]) -> list[str]:
    plain_text = _strip_html_for_alignment(text)
    if not plain_text:
        return []
    blocks = [block.strip() for block in re.split(r"\n\s*\n+", plain_text) if block.strip()]
    if blocks:
        return blocks
    return [line.strip() for line in plain_text.split("\n") if line.strip()]


def _count_vietnamese_hint_chars(text: Optional[str]) -> int:
    return sum(1 for ch in _strip_html_for_alignment(text) if ch in VIETNAMESE_TEXT_HINTS)


def _count_cjk_chars(text: Optional[str]) -> int:
    return sum(1 for ch in _strip_html_for_alignment(text) if "\u4e00" <= ch <= "\u9fff")


def _count_kana_chars(text: Optional[str]) -> int:
    return sum(
        1
        for ch in _strip_html_for_alignment(text)
        if ("\u3040" <= ch <= "\u309f") or ("\u30a0" <= ch <= "\u30ff")
    )


def _translation_locale_mismatch_score(text: Optional[str], locale: str) -> int:
    cleaned = _strip_html_for_alignment(text)
    if not cleaned or locale == DEFAULT_LOCALE:
        return 0

    vi_count = _count_vietnamese_hint_chars(cleaned)
    cjk_count = _count_cjk_chars(cleaned)
    kana_count = _count_kana_chars(cleaned)

    if locale == "en":
        if vi_count >= 8:
            return vi_count
        if cjk_count >= 12:
            return cjk_count
        return 0

    if locale == "zh-CN":
        if vi_count >= 8 and cjk_count < 40:
            return vi_count + 20
        return 0

    if locale == "ja":
        if vi_count >= 8 and (cjk_count + kana_count) < 40:
            return vi_count + 20
        return 0

    return 0


def _extract_alignment_entry_count(raw_alignment: Any) -> int:
    if not isinstance(raw_alignment, dict):
        return 0
    raw_entries = raw_alignment.get("entries")
    if not isinstance(raw_entries, list):
        return 0

    return sum(
        1
        for item in raw_entries
        if isinstance(item, dict)
        and str(item.get("translated_excerpt") or "").strip()
        and str(item.get("source_excerpt") or "").strip()
    )


def _build_translation_publish_gate_report(
    *,
    source_text: str,
    translated_text: str,
    target_locale: str,
    sentence_alignment: Any,
) -> dict[str, Any]:
    source_sentence_count = _filtered_sentence_count_for_translation_quality(source_text)
    translated_sentence_count = _filtered_sentence_count_for_translation_quality(translated_text)
    sentence_ratio = (
        translated_sentence_count / max(source_sentence_count, 1)
        if source_sentence_count > 0
        else 0.0
    )
    source_block_count = len(_split_text_blocks_for_translation_quality(source_text))
    translated_block_count = len(_split_text_blocks_for_translation_quality(translated_text))
    block_delta = abs(translated_block_count - source_block_count)
    alignment_entry_count = _extract_alignment_entry_count(sentence_alignment)
    locale_mismatch_score = _translation_locale_mismatch_score(translated_text, target_locale)
    reasons: list[str] = []

    if source_sentence_count == 0 or translated_sentence_count == 0:
        reasons.append("missing_sentence_structure")
    elif not (TRANSLATION_PUBLISH_MIN_SENTENCE_RATIO <= sentence_ratio <= TRANSLATION_PUBLISH_MAX_SENTENCE_RATIO):
        reasons.append("sentence_ratio_out_of_range")

    if block_delta > TRANSLATION_PUBLISH_MAX_BLOCK_DELTA:
        reasons.append("block_delta_too_high")

    if alignment_entry_count < TRANSLATION_PUBLISH_MIN_ALIGNMENT_ENTRIES:
        reasons.append("missing_alignment")

    if locale_mismatch_score > 0:
        reasons.append("wrong_locale_content")

    return {
        "passed": len(reasons) == 0,
        "reasons": reasons,
        "source_sentence_count": source_sentence_count,
        "translated_sentence_count": translated_sentence_count,
        "sentence_ratio": round(sentence_ratio, 3),
        "source_block_count": source_block_count,
        "translated_block_count": translated_block_count,
        "block_delta": block_delta,
        "alignment_entry_count": alignment_entry_count,
        "locale_mismatch_score": locale_mismatch_score,
    }


def _format_translation_publish_gate_error(locale: str, report: dict[str, Any]) -> str:
    reasons = ",".join(report.get("reasons") or []) or "unknown"
    return (
        f"Quality gate blocked publish for {normalize_locale(locale)}: "
        f"reasons={reasons}; "
        f"sentence_ratio={report.get('sentence_ratio')}; "
        f"source_sentences={report.get('source_sentence_count')}; "
        f"translated_sentences={report.get('translated_sentence_count')}; "
        f"block_delta={report.get('block_delta')}; "
        f"alignment_entries={report.get('alignment_entry_count')}; "
        f"locale_mismatch_score={report.get('locale_mismatch_score')}. "
        "Bản dịch này có nguy cơ làm đối chiếu Gốc VI không ổn định nên chưa được publish."
    )

def parse_multilocale_translation_payload(
    raw_text: str,
    target_locales: list[str],
    required_fields: list[str],
) -> dict[str, dict[str, Any]]:
    parsed = parse_json_like_payload(raw_text)
    translations = parsed.get("translations") if isinstance(parsed, dict) else None
    if not isinstance(translations, dict):
        translations = parsed if isinstance(parsed, dict) else {}

    payload: dict[str, dict[str, Any]] = {}
    for locale in target_locales:
        locale_payload = translations.get(locale)
        if not isinstance(locale_payload, dict):
            raise ValueError(f"Missing locale payload for {locale}")

        parsed_locale_payload: dict[str, Any] = {}
        for field_name in required_fields:
            if field_name not in locale_payload:
                raise ValueError(f"Missing field '{field_name}' for locale {locale}")
            parsed_locale_payload[field_name] = locale_payload.get(field_name)
        payload[locale] = parsed_locale_payload
    return payload

def extract_r2_object_key(content_url: str) -> Optional[str]:
    if not content_url or not R2_PUBLIC_URL:
        return None
    clean_url = re.sub(r'^https?://', '', content_url)
    clean_base = re.sub(r'^https?://', '', R2_PUBLIC_URL)
    return clean_url.replace(clean_base, "").lstrip("/")

def fetch_r2_content(content_url: str) -> str:
    object_key = extract_r2_object_key(content_url)
    if object_key and r2_client:
        response = r2_client.get_object(Bucket=R2_BUCKET, Key=object_key)
        return response["Body"].read().decode("utf-8")

    response = httpx.get(content_url, timeout=20.0)
    response.raise_for_status()
    return response.text

def resolve_chapter_translation(chapter_id: int, locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None
    try:
        result = (
            supabase.table("chapter_translations")
            .select("*")
            .eq("chapter_id", chapter_id)
            .eq("locale", locale)
            .eq("translation_status", "published")
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None

def resolve_novel_translation(locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None
    try:
        result = (
            supabase.table("novel_settings_translations")
            .select("*")
            .eq("novel_settings_id", 1)
            .eq("locale", locale)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None

def normalize_model_catalog(raw_catalog, fallback_model: str) -> list[str]:
    if isinstance(raw_catalog, list):
        catalog = [f"{item}".strip() for item in raw_catalog if f"{item}".strip()]
    else:
        catalog = []
    if fallback_model and fallback_model not in catalog:
        catalog.insert(0, fallback_model)
    if not catalog:
        catalog = DEFAULT_TRANSLATION_MODELS.copy()
    else:
        catalog.extend(DEFAULT_TRANSLATION_MODELS)
    return list(dict.fromkeys(catalog))

def prioritize_model_catalog(catalog: list[str], preferred_model: str) -> list[str]:
    normalized = [item for item in catalog if item]
    if preferred_model and preferred_model in normalized:
        normalized = [preferred_model, *[item for item in normalized if item != preferred_model]]
    elif preferred_model:
        normalized = [preferred_model, *normalized]
    return list(dict.fromkeys(normalized))

def normalize_api_key_catalog(raw_keys, fallback_key: str) -> list[str]:
    keys = []
    if isinstance(raw_keys, list):
        keys.extend(f"{item}".strip() for item in raw_keys if f"{item}".strip())
    if fallback_key and fallback_key.strip():
        keys.insert(0, fallback_key.strip())
    return list(dict.fromkeys([item for item in keys if item]))

def is_translation_retryable(exc: HTTPException) -> bool:
    detail = str(exc.detail).lower()
    return (
        exc.status_code == 429
        or "resource exhausted" in detail
        or "rate limit" in detail
        or "quota" in detail
        or exc.status_code in (400, 404, 401, 403)
    )

def build_translation_failure_detail(
    attempts: list[dict],
    total_keys: int,
    total_models: int,
    final_detail: str,
) -> str:
    summary = f"Đã thử {total_keys} key, {total_models} model, tổng {len(attempts)} lượt."
    if not attempts:
        return f"{summary}\nLỗi cuối cùng: {final_detail}"

    lines = [summary, "Các lượt lỗi:"]
    for item in attempts:
        lines.append(
            f"- key #{item['key_index']} | {item['model']} | HTTP {item['status_code']} | {item['message']}"
        )
    lines.append(f"Lỗi cuối cùng: {final_detail}")
    return "\n".join(lines)

def get_model_min_interval_seconds(model_name: str) -> float:
    return MODEL_MIN_INTERVAL_SECONDS.get(model_name, 6.5)

def get_key_model_bucket(model_name: str, api_key: str) -> str:
    key_hash = hashlib.sha1(api_key.encode("utf-8")).hexdigest()[:8] if api_key else "nokey"
    return f"{model_name}|{key_hash}"

def clean_json_like_response(raw_text: str) -> str:
    cleaned = (raw_text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace:last_brace + 1]
    return cleaned.strip()

def escape_json_string_control_chars(raw_text: str) -> str:
    result: list[str] = []
    in_string = False
    escaped = False

    for char in raw_text:
        if escaped:
            result.append(char)
            escaped = False
            continue

        if char == "\\":
            result.append(char)
            escaped = True
            continue

        if char == '"':
            result.append(char)
            in_string = not in_string
            continue

        if in_string and char == "\n":
            result.append("\\n")
            continue
        if in_string and char == "\r":
            result.append("\\r")
            continue
        if in_string and char == "\t":
            result.append("\\t")
            continue

        result.append(char)

    return "".join(result)

def parse_json_like_payload(raw_text: str) -> dict:
    """
    Phân tích chuỗi JSON từ phản hồi của AI, bao gồm việc làm sạch và sửa lỗi ký tự điều khiển.
    """
    cleaned = clean_json_like_response(raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        repaired = escape_json_string_control_chars(cleaned)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError as exc:
            snippet = repaired[:240].replace("\n", "\\n")
            raise ValueError(f"Could not parse JSON payload: {exc}. Snippet: {snippet}")

async def generate_structured_translation_payload(
    system_instruction: str,
    user_prompt: str,
    response_json_schema: dict,
    parser: Callable[[str], T],
    timeout_seconds: float = 300.0,
    translation_mode: str = "bulk",
) -> T:
    _active_model, model_catalog, api_keys = await resolve_ai_settings_for_translation(translation_mode)
    if not api_keys:
        raise HTTPException(status_code=503, detail="AI translation is not configured")
    temperature = 0.05 if translation_mode == "quality" else 0.1

    payload = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": TRANSLATION_MAX_OUTPUT_TOKENS,
            "temperature": temperature,
            "responseMimeType": "application/json",
            "responseJsonSchema": response_json_schema,
        },
    }

    last_error: Optional[HTTPException] = None
    attempts: list[dict] = []
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        for key_index, api_key in enumerate(api_keys, start=1):
            for model_name in model_catalog:
                await throttle_translation_request(model_name, api_key)
                gemini_url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model_name}:generateContent?key={api_key}"
                )
                response = await client.post(gemini_url, json=payload)
                if response.is_success:
                    data = response.json()
                    try:
                        raw_text = extract_gemini_text_response(data)
                        return parser(raw_text)
                    except Exception as exc:
                        last_error = HTTPException(
                            status_code=502,
                            detail=f"Model {model_name}: invalid translation payload: {exc}",
                        )
                        attempts.append(
                            {
                                "key_index": key_index,
                                "model": model_name,
                                "status_code": 502,
                                "message": f"invalid translation payload: {exc}",
                            }
                        )
                        continue

                last_error = HTTPException(
                    status_code=response.status_code,
                    detail=f"Model {model_name}: Translation API error: {response.text}",
                )
                attempts.append(
                    {
                        "key_index": key_index,
                        "model": model_name,
                        "status_code": response.status_code,
                        "message": response.text,
                    }
                )
                if not is_translation_retryable(last_error):
                    raise HTTPException(
                        status_code=last_error.status_code,
                        detail=build_translation_failure_detail(
                            attempts,
                            len(api_keys),
                            len(model_catalog),
                            str(last_error.detail),
                        ),
                    )

    if last_error:
        raise HTTPException(
            status_code=last_error.status_code,
            detail=build_translation_failure_detail(
                attempts,
                len(api_keys),
                len(model_catalog),
                str(last_error.detail),
            ),
        )
    raise HTTPException(status_code=502, detail="Không có mô hình dịch AI khả dụng")

async def throttle_translation_request(model_name: str, api_key: str):
    bucket = get_key_model_bucket(model_name, api_key)
    min_interval = get_model_min_interval_seconds(model_name)

    async with TRANSLATION_RATE_LIMIT_LOCK:
        now = monotonic()
        last_sent = TRANSLATION_RATE_LIMIT_STATE.get(bucket, 0.0)
        wait_seconds = max(0.0, min_interval - (now - last_sent))
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
        TRANSLATION_RATE_LIMIT_STATE[bucket] = monotonic()

def resolve_homepage_translation(locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None
    try:
        result = (
            supabase.table("homepage_settings_translations")
            .select("*")
            .eq("homepage_settings_id", 1)
            .eq("locale", locale)
            .eq("translation_status", "published")
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None

def resolve_wiki_translation(entry_id: str, locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None
    try:
        result = (
            supabase.table("wiki_entry_translations")
            .select("*")
            .eq("wiki_entry_id", entry_id)
            .eq("locale", locale)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None

def apply_wiki_translation(entry: dict, locale: str) -> dict:
    translation = resolve_wiki_translation(entry.get("id"), locale)
    resolved_locale = DEFAULT_LOCALE
    is_fallback = False
    if translation:
        if translation.get("title"):
            entry["title"] = translation["title"]
        if translation.get("summary"):
            entry["summary"] = translation["summary"]
        if translation.get("content"):
            entry["content"] = translation["content"]
        resolved_locale = normalize_locale(locale)
    elif normalize_locale(locale) != DEFAULT_LOCALE:
        is_fallback = True

    entry["requested_locale"] = normalize_locale(locale)
    entry["resolved_locale"] = resolved_locale
    entry["is_fallback"] = is_fallback
    return entry

def sanitize_homepage_features(features) -> list[dict]:
    cleaned = []
    if not isinstance(features, list):
        return cleaned

    for item in features:
        if not isinstance(item, dict):
            continue
        cleaned.append(
            {
                "icon": str(item.get("icon") or "").strip(),
                "title": sanitize_plaintext(str(item.get("title") or "")),
                "desc": sanitize_plaintext(str(item.get("desc") or "")),
            }
        )
    return cleaned

def prepare_homepage_settings_payload(payload: Optional[dict]) -> dict:
    raw = dict(payload or {})
    return {
        "warning_title": sanitize_plaintext(raw.get("warning_title")) if raw.get("warning_title") is not None else None,
        "warning_subtitle": sanitize_plaintext(raw.get("warning_subtitle")) if raw.get("warning_subtitle") is not None else None,
        "warning_headline": sanitize_plaintext(raw.get("warning_headline")) if raw.get("warning_headline") is not None else None,
        "warning_description": sanitize_html(raw.get("warning_description")) if raw.get("warning_description") is not None else "",
        "features_title": sanitize_plaintext(raw.get("features_title")) if raw.get("features_title") is not None else None,
        "features_json": sanitize_homepage_features(raw.get("features_json")),
    }

def apply_homepage_translation(payload: dict, locale: str) -> dict:
    requested_locale = normalize_locale(locale)
    resolved_locale = DEFAULT_LOCALE
    is_fallback = False

    translation = resolve_homepage_translation(requested_locale)
    if translation:
        for key in (
            "warning_title",
            "warning_subtitle",
            "warning_headline",
            "warning_description",
            "features_title",
            "features_json",
        ):
            if translation.get(key) is not None:
                payload[key] = translation.get(key)
        payload = prepare_homepage_settings_payload(payload)
        resolved_locale = requested_locale
    elif requested_locale != DEFAULT_LOCALE:
        is_fallback = True

    payload["requested_locale"] = requested_locale
    payload["resolved_locale"] = resolved_locale
    payload["is_fallback"] = is_fallback
    return payload

async def resolve_ai_settings_for_translation(translation_mode: str = "bulk") -> tuple[str, list[str], list[str]]:
    try:
        settings = (
            supabase.table("novel_settings")
            .select("*")
            .eq("id", 1)
            .single()
            .execute()
        )
        if settings.data:
            bulk_model_name = settings.data.get("ai_model_name") or BULK_TRANSLATION_MODEL_FALLBACK
            quality_model_name = settings.data.get("ai_quality_model_name") or QUALITY_TRANSLATION_MODEL_FALLBACK
            model_name = quality_model_name if translation_mode == "quality" else bulk_model_name
            api_key = settings.data.get("ai_api_key") or os.getenv("GEMINI_API_KEY", "")
            model_catalog = normalize_model_catalog(settings.data.get("ai_model_catalog"), model_name)
            return (
                model_name,
                prioritize_model_catalog(model_catalog, model_name),
                normalize_api_key_catalog(settings.data.get("ai_api_keys"), api_key),
            )
    except Exception:
        pass
    fallback_key = os.getenv("GEMINI_API_KEY", "")
    fallback_model = QUALITY_TRANSLATION_MODEL_FALLBACK if translation_mode == "quality" else BULK_TRANSLATION_MODEL_FALLBACK
    return (
        fallback_model,
        prioritize_model_catalog(DEFAULT_TRANSLATION_MODELS.copy(), fallback_model),
        normalize_api_key_catalog([], fallback_key),
    )

async def translate_text_with_ai(source_text: str, source_locale: str, target_locale: str, context_label: str) -> str:
    _active_model, model_catalog, api_keys = await resolve_ai_settings_for_translation()
    if not api_keys:
        raise HTTPException(status_code=503, detail="AI translation is not configured")

    glossary_prompt = build_glossary_prompt()
    prompt = f"""
Bạn là biên dịch viên chuyên nghiệp cho tiểu thuyết sinh tồn hậu tận thế.
Hãy dịch nội dung sau từ {source_locale} sang {target_locale}.

YÊU CẦU:
1. Giữ nguyên tên riêng theo glossary nếu có.
2. Không được rút gọn, không thêm giải thích, không thêm markdown.
3. Giữ nguyên ngắt đoạn và thứ tự nội dung.
4. Nếu gặp ký hiệu hoặc tên kỹ năng, ưu tiên nhất quán hơn viết đẹp.
5. Chỉ trả về bản dịch sau cùng.

CONTEXT: {context_label}

GLOSSARY:
{glossary_prompt}

SOURCE:
{source_text}
""".strip()

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3},
    }

    last_error: Optional[HTTPException] = None
    attempts: list[dict] = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for key_index, api_key in enumerate(api_keys, start=1):
            for model_name in model_catalog:
                await throttle_translation_request(model_name, api_key)
                gemini_url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model_name}:generateContent?key={api_key}"
                )
                response = await client.post(gemini_url, json=payload)
                if response.is_success:
                    data = response.json()
                    try:
                        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    except Exception as exc:
                        raise HTTPException(status_code=502, detail=f"Model {model_name}: invalid translation response: {exc}")

                last_error = HTTPException(
                    status_code=response.status_code,
                    detail=f"Model {model_name}: Translation API error: {response.text}",
                )
                attempts.append(
                    {
                        "key_index": key_index,
                        "model": model_name,
                        "status_code": response.status_code,
                        "message": response.text,
                    }
                )
                if not is_translation_retryable(last_error):
                    raise HTTPException(
                        status_code=last_error.status_code,
                        detail=build_translation_failure_detail(
                            attempts,
                            len(api_keys),
                            len(model_catalog),
                            str(last_error.detail),
                        ),
                    )

    if last_error:
        raise HTTPException(
            status_code=last_error.status_code,
            detail=build_translation_failure_detail(
                attempts,
                len(api_keys),
                len(model_catalog),
                str(last_error.detail),
            ),
        )
    raise HTTPException(status_code=502, detail="Không có mô hình dịch khả dụng")

async def translate_chapter_payload_with_ai(
    title: str,
    content: str,
    source_locale: str,
    target_locale: str,
    context_label: str,
) -> dict:
    translated_payloads = await translate_chapter_payloads_with_ai(
        title=title,
        content=content,
        source_locale=source_locale,
        target_locales=[target_locale],
        context_label=context_label,
    )
    locale_payload = translated_payloads.get(normalize_locale(target_locale)) or {}
    translated_title = str(locale_payload.get("title") or "").strip()
    translated_content = str(locale_payload.get("content") or "").strip()
    if not translated_title or not translated_content:
        raise HTTPException(
            status_code=502,
            detail=f"Missing structured chapter translation payload for locale {normalize_locale(target_locale)}",
        )
    return {
        "title": translated_title,
        "content": translated_content,
    }

async def translate_chapter_payloads_with_ai(
    title: str,
    content: str,
    source_locale: str,
    target_locales: list[str],
    context_label: str,
    translation_mode: str = "bulk",
) -> dict[str, dict[str, Any]]:
    target_locales = build_target_translation_locales(target_locales)
    if not target_locales:
        return {}

    glossary_prompt = build_glossary_prompt()
    locale_prompt = build_target_locale_prompt(target_locales)
    schema = build_multilocale_object_schema(
        target_locales,
        {
            "title": {"type": "string"},
            "content": {"type": "string"},
        },
    )
    system_instruction = build_chapter_multilocale_system_instruction()

    translated_payloads = {
        locale: {"title": "", "content_parts": []}
        for locale in target_locales
    }
    content_chunks = chunk_translation_source_text(content)

    for chunk_index, content_chunk in enumerate(content_chunks, start=1):
        user_prompt = build_chapter_multilocale_user_prompt(
            title=title,
            content_chunk=content_chunk,
            source_locale=source_locale,
            locale_prompt=locale_prompt,
            glossary_prompt=glossary_prompt,
            context_label=context_label,
            chunk_index=chunk_index,
            chunk_count=len(content_chunks),
        )

        chunk_payload = await generate_structured_translation_payload(
            system_instruction=system_instruction,
            user_prompt=user_prompt,
            response_json_schema=schema,
            parser=lambda raw_text: parse_multilocale_translation_payload(raw_text, target_locales, ["title", "content"]),
            translation_mode=translation_mode,
        )

        for locale in target_locales:
            locale_payload = chunk_payload[locale]
            translated_title = str(locale_payload.get("title") or "").strip()
            translated_content = str(locale_payload.get("content") or "").strip()
            if not translated_title or not translated_content:
                raise ValueError(f"Missing chapter title/content for locale {locale}")
            if not translated_payloads[locale]["title"]:
                translated_payloads[locale]["title"] = translated_title
            translated_payloads[locale]["content_parts"].append(translated_content)

    return {
        locale: {
            "title": translated_payloads[locale]["title"] or title,
            "content": "\n\n".join(
                part for part in translated_payloads[locale]["content_parts"] if part
            ).strip(),
            "sentence_alignment": build_chapter_sentence_alignment(
                source_text=content,
                translated_text="\n\n".join(
                    part for part in translated_payloads[locale]["content_parts"] if part
                ).strip(),
                source_chunks=content_chunks,
                translated_chunks=translated_payloads[locale]["content_parts"],
            ),
        }
        for locale in target_locales
    }

async def refine_chapter_translation_with_ai(
    source_title: str,
    source_content: str,
    source_locale: str,
    target_locale: str,
    current_title: str,
    current_content: str,
    context_label: str,
) -> dict[str, Any]:
    glossary_prompt = build_glossary_prompt()
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["title", "content"],
        "additionalProperties": False,
    }
    system_instruction = build_chapter_refine_system_instruction()
    source_chunks = chunk_translation_source_text(source_content)
    current_chunks = split_text_into_chunk_count(current_content, len(source_chunks))

    def parse_refined_payload(raw_text: str) -> dict[str, str]:
        parsed = parse_json_like_payload(raw_text)
        title_value = str(parsed.get("title") or "").strip()
        content_value = str(parsed.get("content") or "").strip()
        if not title_value or not content_value:
            raise ValueError("Missing refined title/content")
        return {
            "title": title_value,
            "content": content_value,
        }

    refined_title = ""
    refined_content_parts: list[str] = []
    for chunk_index, source_chunk in enumerate(source_chunks, start=1):
        current_chunk = current_chunks[chunk_index - 1] if chunk_index - 1 < len(current_chunks) else ""
        chunk_payload = await generate_structured_translation_payload(
            system_instruction=system_instruction,
            user_prompt=build_chapter_refine_user_prompt(
                source_title=source_title,
                source_content_chunk=source_chunk,
                current_title=current_title,
                current_content_chunk=current_chunk,
                source_locale=source_locale,
                target_locale=target_locale,
                glossary_prompt=glossary_prompt,
                context_label=context_label,
                chunk_index=chunk_index,
                chunk_count=len(source_chunks),
            ),
            response_json_schema=schema,
            parser=parse_refined_payload,
            translation_mode="quality",
        )
        if not refined_title:
            refined_title = chunk_payload["title"]
        refined_content_parts.append(chunk_payload["content"])

    if not refined_title or not refined_content_parts:
        raise HTTPException(
            status_code=502,
            detail=f"Missing refined chapter payload for locale {normalize_locale(target_locale)}",
        )
    refined_content = "\n\n".join(part for part in refined_content_parts if part).strip()
    return {
        "title": refined_title.strip(),
        "content": refined_content,
        "sentence_alignment": build_chapter_sentence_alignment(
            source_text=source_content,
            translated_text=refined_content,
            source_chunks=source_chunks,
            translated_chunks=refined_content_parts,
        ),
    }

async def upsert_chapter_translations(
    chapter_row: dict,
    title: str,
    content: str,
    locales: list[str],
    translation_mode: str = "bulk",
) -> dict:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {"translated_locales": [], "failed_translations": []}
    supports_alignment = chapter_translation_alignment_supported()

    def build_failed_translation_row(
        locale: str,
        existing_row: Optional[dict],
        *,
        error_detail: str,
        failure_time: str,
        translation_source: str = "ai",
        candidate_title: Optional[str] = None,
        candidate_content: Optional[str] = None,
        candidate_alignment: Optional[dict[str, Any]] = None,
    ) -> dict:
        current_row = existing_row or {}
        resolved_title = candidate_title if candidate_title is not None else (current_row.get("title") or "")
        resolved_content = candidate_content if candidate_content is not None else (current_row.get("content") or "")
        payload = {
            "chapter_id": chapter_row["id"],
            "locale": locale,
            # Postgres checks NOT NULL on the INSERT half of upsert before conflict handling.
            "title": resolved_title,
            "content": resolved_content,
            "summary": (resolved_content[:280] if resolved_content else current_row.get("summary")),
            "translation_status": "failed",
            "translation_source": translation_source,
            "content_hash": content_hash,
            "updated_at": failure_time,
            "last_error": error_detail,
            "attempt_count": attempt_counts[locale],
        }
        if supports_alignment:
            payload["sentence_alignment"] = candidate_alignment if candidate_alignment is not None else current_row.get("sentence_alignment")
        return payload

    content_hash = build_content_hash(content)
    now_iso = datetime.now(timezone.utc).isoformat()
    existing_select_fields = "locale, attempt_count, title, content, summary, translated_at"
    if supports_alignment:
        existing_select_fields += ", sentence_alignment"
    existing_resp = (
        supabase.table("chapter_translations")
        .select(existing_select_fields)
        .eq("chapter_id", chapter_row["id"])
        .in_("locale", target_locales)
        .execute()
    )
    existing_rows = {
        row.get("locale"): row
        for row in (existing_resp.data or [])
        if row.get("locale")
    }
    attempt_counts = {
        locale: int((existing_rows.get(locale) or {}).get("attempt_count") or 0) + 1
        for locale in target_locales
    }

    for locale in target_locales:
        existing_row = existing_rows.get(locale) or {}
        payload = {
            "chapter_id": chapter_row["id"],
            "locale": locale,
            "title": existing_row.get("title") or "",
            "content": existing_row.get("content") or "",
            "summary": existing_row.get("summary"),
            "translation_status": "in_progress",
            "translation_source": "ai",
            "translated_at": existing_row.get("translated_at"),
            "content_hash": content_hash,
            "last_error": None,
            "attempt_count": attempt_counts[locale],
            "updated_at": now_iso,
        }
        if supports_alignment:
            payload["sentence_alignment"] = existing_row.get("sentence_alignment")
        supabase.table("chapter_translations").upsert(
            payload,
            on_conflict="chapter_id,locale",
        ).execute()

    try:
        translated_payloads = await translate_chapter_payloads_with_ai(
            title=title,
            content=content,
            source_locale=DEFAULT_LOCALE,
            target_locales=target_locales,
            context_label=f"chapter-{chapter_row['chapter_number']}",
            translation_mode=translation_mode,
        )
    except HTTPException as exc:
        failure_time = datetime.now(timezone.utc).isoformat()
        for locale in target_locales:
            supabase.table("chapter_translations").upsert(
                build_failed_translation_row(
                    locale,
                    existing_rows.get(locale),
                    error_detail=str(exc.detail),
                    failure_time=failure_time,
                ),
                on_conflict="chapter_id,locale",
            ).execute()
        raise
    except Exception as exc:
        failure_time = datetime.now(timezone.utc).isoformat()
        for locale in target_locales:
            supabase.table("chapter_translations").upsert(
                build_failed_translation_row(
                    locale,
                    existing_rows.get(locale),
                    error_detail=str(exc),
                    failure_time=failure_time,
                ),
                on_conflict="chapter_id,locale",
            ).execute()
        raise

    translated_locales = []
    failed_translations = []
    translated_at = datetime.now(timezone.utc).isoformat()
    for locale in target_locales:
        locale_payload = translated_payloads.get(locale) or {}
        translated_title = str(locale_payload.get("title") or "").strip()
        translated_content = str(locale_payload.get("content") or "").strip()
        sentence_alignment = locale_payload.get("sentence_alignment")
        if not translated_title or not translated_content:
            detail = f"Missing translated chapter payload for locale {locale}"
            supabase.table("chapter_translations").upsert(
                build_failed_translation_row(
                    locale,
                    existing_rows.get(locale),
                    error_detail=detail,
                    failure_time=translated_at,
                ),
                on_conflict="chapter_id,locale",
            ).execute()
            failed_translations.append({"locale": locale, "status_code": 502, "detail": detail})
            continue

        gate_report = _build_translation_publish_gate_report(
            source_text=content,
            translated_text=translated_content,
            target_locale=locale,
            sentence_alignment=sentence_alignment,
        )
        if not gate_report["passed"]:
            detail = _format_translation_publish_gate_error(locale, gate_report)
            supabase.table("chapter_translations").upsert(
                build_failed_translation_row(
                    locale,
                    existing_rows.get(locale),
                    error_detail=detail,
                    failure_time=translated_at,
                    translation_source="ai",
                    candidate_title=translated_title,
                    candidate_content=translated_content,
                    candidate_alignment=sentence_alignment if supports_alignment else None,
                ),
                on_conflict="chapter_id,locale",
            ).execute()
            failed_translations.append({"locale": locale, "status_code": 422, "detail": detail})
            continue

        payload = {
            "chapter_id": chapter_row["id"],
            "locale": locale,
            "title": translated_title,
            "content": translated_content,
            "summary": translated_content[:280],
            "translation_status": "published",
            "translation_source": "ai",
            "translated_at": translated_at,
            "content_hash": content_hash,
            "last_error": None,
            "attempt_count": attempt_counts[locale],
            "updated_at": translated_at,
        }
        if supports_alignment:
            payload["sentence_alignment"] = sentence_alignment
        supabase.table("chapter_translations").upsert(
            payload,
            on_conflict="chapter_id,locale",
        ).execute()
        translated_locales.append(locale)

    return {
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

async def improve_chapter_translations(chapter_row: dict, title: str, content: str, locales: list[str]) -> dict:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {"translated_locales": [], "failed_translations": []}
    supports_alignment = chapter_translation_alignment_supported()

    existing_select_fields = "locale, attempt_count, title, content, summary, translated_at"
    if supports_alignment:
        existing_select_fields += ", sentence_alignment"
    existing_resp = (
        supabase.table("chapter_translations")
        .select(existing_select_fields)
        .eq("chapter_id", chapter_row["id"])
        .in_("locale", target_locales)
        .execute()
    )
    existing_rows = {
        row.get("locale"): row
        for row in (existing_resp.data or [])
        if row.get("locale")
    }
    translated_at = datetime.now(timezone.utc).isoformat()
    content_hash = build_content_hash(content)
    translated_locales: list[str] = []
    failed_translations: list[dict] = []

    for locale in target_locales:
        existing_row = existing_rows.get(locale) or {}
        current_title = str(existing_row.get("title") or "").strip()
        current_content = str(existing_row.get("content") or "").strip()
        attempt_count = int(existing_row.get("attempt_count") or 0) + 1

        if not current_title or not current_content:
            failed_translations.append(
                {
                    "locale": locale,
                    "status_code": 409,
                    "detail": "No existing translation found to improve",
                }
            )
            continue

        in_progress_payload = {
            "chapter_id": chapter_row["id"],
            "locale": locale,
            "title": current_title,
            "content": current_content,
            "summary": existing_row.get("summary"),
            "translation_status": "in_progress",
            "translation_source": "ai_refine",
            "translated_at": existing_row.get("translated_at"),
            "content_hash": content_hash,
            "last_error": None,
            "attempt_count": attempt_count,
            "updated_at": translated_at,
        }
        if supports_alignment:
            in_progress_payload["sentence_alignment"] = existing_row.get("sentence_alignment")
        supabase.table("chapter_translations").upsert(
            in_progress_payload,
            on_conflict="chapter_id,locale",
        ).execute()

        try:
            improved_payload = await refine_chapter_translation_with_ai(
                source_title=title,
                source_content=content,
                source_locale=DEFAULT_LOCALE,
                target_locale=locale,
                current_title=current_title,
                current_content=current_content,
                context_label=f"chapter-quality-{chapter_row['chapter_number']}-{locale}",
            )
            improved_title = str(improved_payload.get("title") or "").strip()
            improved_content = str(improved_payload.get("content") or "").strip()
            if not improved_title or not improved_content:
                raise ValueError(f"Missing refined chapter payload for locale {locale}")

            gate_report = _build_translation_publish_gate_report(
                source_text=content,
                translated_text=improved_content,
                target_locale=locale,
                sentence_alignment=improved_payload.get("sentence_alignment"),
            )
            if not gate_report["passed"]:
                detail = _format_translation_publish_gate_error(locale, gate_report)
                failed_payload = {
                    "chapter_id": chapter_row["id"],
                    "locale": locale,
                    "title": improved_title,
                    "content": improved_content,
                    "summary": improved_content[:280],
                    "translation_status": "failed",
                    "translation_source": "ai_refine",
                    "content_hash": content_hash,
                    "updated_at": translated_at,
                    "last_error": detail,
                    "attempt_count": attempt_count,
                }
                if supports_alignment:
                    failed_payload["sentence_alignment"] = improved_payload.get("sentence_alignment")
                supabase.table("chapter_translations").upsert(
                    failed_payload,
                    on_conflict="chapter_id,locale",
                ).execute()
                failed_translations.append(
                    {
                        "locale": locale,
                        "status_code": 422,
                        "detail": detail,
                    }
                )
                continue

            success_payload = {
                "chapter_id": chapter_row["id"],
                "locale": locale,
                "title": improved_title,
                "content": improved_content,
                "summary": improved_content[:280],
                "translation_status": "published",
                "translation_source": "ai_refine",
                "translated_at": translated_at,
                "content_hash": content_hash,
                "last_error": None,
                "attempt_count": attempt_count,
                "updated_at": translated_at,
            }
            if supports_alignment:
                success_payload["sentence_alignment"] = improved_payload.get("sentence_alignment")
            supabase.table("chapter_translations").upsert(
                success_payload,
                on_conflict="chapter_id,locale",
            ).execute()
            translated_locales.append(locale)
        except HTTPException as exc:
            failed_payload = {
                "chapter_id": chapter_row["id"],
                "locale": locale,
                "title": current_title,
                "content": current_content,
                "summary": existing_row.get("summary"),
                "translation_status": "failed",
                "translation_source": "ai_refine",
                "content_hash": content_hash,
                "updated_at": translated_at,
                "last_error": str(exc.detail),
                "attempt_count": attempt_count,
            }
            if supports_alignment:
                failed_payload["sentence_alignment"] = existing_row.get("sentence_alignment")
            supabase.table("chapter_translations").upsert(
                failed_payload,
                on_conflict="chapter_id,locale",
            ).execute()
            failed_translations.append(
                {
                    "locale": locale,
                    "status_code": exc.status_code,
                    "detail": str(exc.detail),
                }
            )
        except Exception as exc:
            failed_payload = {
                "chapter_id": chapter_row["id"],
                "locale": locale,
                "title": current_title,
                "content": current_content,
                "summary": existing_row.get("summary"),
                "translation_status": "failed",
                "translation_source": "ai_refine",
                "content_hash": content_hash,
                "updated_at": translated_at,
                "last_error": str(exc),
                "attempt_count": attempt_count,
            }
            if supports_alignment:
                failed_payload["sentence_alignment"] = existing_row.get("sentence_alignment")
            supabase.table("chapter_translations").upsert(
                failed_payload,
                on_conflict="chapter_id,locale",
            ).execute()
            failed_translations.append(
                {
                    "locale": locale,
                    "status_code": 500,
                    "detail": str(exc),
                }
            )

    return {
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

async def translate_homepage_payload_with_ai(settings_payload: dict, target_locale: str) -> dict:
    _active_model, model_catalog, api_keys = await resolve_ai_settings_for_translation()
    if not api_keys:
        raise HTTPException(status_code=503, detail="AI translation is not configured")

    base_payload = prepare_homepage_settings_payload(settings_payload)
    glossary_prompt = build_glossary_prompt()
    source_payload = {
        "warning_title": base_payload.get("warning_title") or "",
        "warning_subtitle": base_payload.get("warning_subtitle") or "",
        "warning_headline": base_payload.get("warning_headline") or "",
        "warning_description": base_payload.get("warning_description") or "",
        "features_title": base_payload.get("features_title") or "",
        "features_json": [
            {
                "icon": feature.get("icon", ""),
                "title": feature.get("title", ""),
                "desc": feature.get("desc", ""),
            }
            for feature in (base_payload.get("features_json") or [])
        ],
    }
    prompt = build_homepage_translation_prompt(
        source_payload=source_payload,
        target_locale=target_locale,
        glossary_prompt=glossary_prompt,
        source_locale=DEFAULT_LOCALE,
    )

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3},
    }

    def parse_homepage_translation_payload(raw_text: str) -> dict:
        parsed = parse_json_like_payload(raw_text)
        translated = prepare_homepage_settings_payload(parsed)
        translated["features_json"] = sanitize_homepage_features(parsed.get("features_json"))
        return translated

    last_error: Optional[HTTPException] = None
    attempts: list[dict] = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for key_index, api_key in enumerate(api_keys, start=1):
            for model_name in model_catalog:
                await throttle_translation_request(model_name, api_key)
                gemini_url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model_name}:generateContent?key={api_key}"
                )
                response = await client.post(gemini_url, json=payload)
                if response.is_success:
                    data = response.json()
                    try:
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        return parse_homepage_translation_payload(raw_text)
                    except Exception as exc:
                        last_error = HTTPException(
                            status_code=502,
                            detail=f"Model {model_name}: invalid homepage translation payload: {exc}",
                        )
                        attempts.append(
                            {
                                "key_index": key_index,
                                "model": model_name,
                                "status_code": 502,
                                "message": f"invalid homepage translation payload: {exc}",
                            }
                        )
                        continue

                last_error = HTTPException(
                    status_code=response.status_code,
                    detail=f"Model {model_name}: Translation API error: {response.text}",
                )
                attempts.append(
                    {
                        "key_index": key_index,
                        "model": model_name,
                        "status_code": response.status_code,
                        "message": response.text,
                    }
                )
                if not is_translation_retryable(last_error):
                    raise HTTPException(
                        status_code=last_error.status_code,
                        detail=build_translation_failure_detail(
                            attempts,
                            len(api_keys),
                            len(model_catalog),
                            str(last_error.detail),
                        ),
                    )

    if last_error:
        raise HTTPException(
            status_code=last_error.status_code,
            detail=build_translation_failure_detail(
                attempts,
                len(api_keys),
                len(model_catalog),
                str(last_error.detail),
            ),
        )
    raise HTTPException(status_code=502, detail="Không có mô hình dịch homepage khả dụng")

async def translate_homepage_payloads_with_ai(settings_payload: dict, locales: list[str]) -> dict[str, dict]:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {}

    base_payload = prepare_homepage_settings_payload(settings_payload)
    glossary_prompt = build_glossary_prompt()
    locale_prompt = build_target_locale_prompt(target_locales)
    source_payload = {
        "warning_title": base_payload.get("warning_title") or "",
        "warning_subtitle": base_payload.get("warning_subtitle") or "",
        "warning_headline": base_payload.get("warning_headline") or "",
        "warning_description": base_payload.get("warning_description") or "",
        "features_title": base_payload.get("features_title") or "",
        "features_json": [
            {
                "icon": feature.get("icon", ""),
                "title": feature.get("title", ""),
                "desc": feature.get("desc", ""),
            }
            for feature in (base_payload.get("features_json") or [])
        ],
    }
    schema = build_multilocale_object_schema(
        target_locales,
        {
            "warning_title": {"type": "string"},
            "warning_subtitle": {"type": "string"},
            "warning_headline": {"type": "string"},
            "warning_description": {"type": "string"},
            "features_title": {"type": "string"},
            "features_json": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "icon": {"type": "string"},
                        "title": {"type": "string"},
                        "desc": {"type": "string"},
                    },
                    "required": ["icon", "title", "desc"],
                    "additionalProperties": False,
                },
            },
        },
    )
    system_instruction = build_homepage_multilocale_system_instruction()
    translated_payloads = await generate_structured_translation_payload(
        system_instruction=system_instruction,
        user_prompt=build_homepage_multilocale_user_prompt(
            source_payload=source_payload,
            locale_prompt=locale_prompt,
            glossary_prompt=glossary_prompt,
            source_locale=DEFAULT_LOCALE,
        ),
        response_json_schema=schema,
        parser=lambda raw_text: parse_multilocale_translation_payload(
            raw_text,
            target_locales,
            [
                "warning_title",
                "warning_subtitle",
                "warning_headline",
                "warning_description",
                "features_title",
                "features_json",
            ],
        ),
    )

    sanitized_payloads: dict[str, dict] = {}
    feature_count = len(source_payload["features_json"])
    for locale in target_locales:
        locale_payload = translated_payloads.get(locale) or {}
        translated = prepare_homepage_settings_payload(locale_payload)
        translated_features = sanitize_homepage_features(locale_payload.get("features_json"))
        if len(translated_features) != feature_count:
            raise ValueError(f"Invalid homepage features_json length for locale {locale}")
        translated["features_json"] = translated_features
        sanitized_payloads[locale] = translated
    return sanitized_payloads

async def upsert_homepage_translations(settings_payload: dict, locales: list[str]) -> dict:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {"translated_locales": [], "failed_translations": []}

    base_payload = prepare_homepage_settings_payload(settings_payload)
    source_hash = build_content_hash(json.dumps(base_payload, ensure_ascii=False, sort_keys=True))
    translated_payloads = await translate_homepage_payloads_with_ai(base_payload, target_locales)

    translated_locales = []
    failed_translations = []
    translated_at = datetime.now(timezone.utc).isoformat()
    for locale in target_locales:
        translated_payload = translated_payloads.get(locale)
        if not translated_payload:
            failed_translations.append({"locale": locale, "status_code": 502, "detail": "Missing homepage translation payload"})
            continue

        payload = {
            "homepage_settings_id": 1,
            "locale": locale,
            "warning_title": translated_payload.get("warning_title", ""),
            "warning_subtitle": translated_payload.get("warning_subtitle", ""),
            "warning_headline": translated_payload.get("warning_headline", ""),
            "warning_description": translated_payload.get("warning_description", ""),
            "features_title": translated_payload.get("features_title", ""),
            "features_json": translated_payload.get("features_json", []),
            "translation_status": "published",
            "translation_source": "ai",
            "translated_at": translated_at,
            "content_hash": source_hash,
            "updated_at": translated_at,
        }
        supabase.table("homepage_settings_translations").upsert(payload, on_conflict="homepage_settings_id,locale").execute()
        translated_locales.append(locale)

    return {
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

async def translate_novel_payloads_with_ai(novel_payload: dict, locales: list[str]) -> dict[str, dict]:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {}

    glossary_prompt = build_glossary_prompt()
    locale_prompt = build_target_locale_prompt(target_locales)
    source_payload = {
        "title": novel_payload.get("title") or "",
        "description": novel_payload.get("description") or "",
    }
    schema = build_multilocale_object_schema(
        target_locales,
        {
            "title": {"type": "string"},
            "description": {"type": "string"},
        },
    )
    system_instruction = "Bạn là chuyên gia dịch thuật văn học. Hãy dịch tiêu đề truyện và mô tả truyện sang các ngôn ngữ yêu cầu. Giữ nguyên phong cách hậu tận thế, kinh dị sinh hóa."
    translated_payloads = await generate_structured_translation_payload(
        system_instruction=system_instruction,
        user_prompt=build_novel_multilocale_user_prompt(
            source_payload=source_payload,
            locale_prompt=locale_prompt,
            glossary_prompt=glossary_prompt,
        ),
        response_json_schema=schema,
        parser=lambda raw_text: parse_multilocale_translation_payload(
            raw_text,
            target_locales,
            ["title", "description"],
        ),
    )
    return translated_payloads

async def upsert_novel_translations(novel_payload: dict, locales: list[str]) -> dict:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {"translated_locales": [], "failed_translations": []}

    translated_payloads = await translate_novel_payloads_with_ai(novel_payload, target_locales)
    translated_at = datetime.now(timezone.utc).isoformat()
    translated_locales = []
    failed_translations = []

    for locale in target_locales:
        translated_payload = translated_payloads.get(locale)
        if not translated_payload:
            failed_translations.append({"locale": locale, "status_code": 502, "detail": "Missing novel translation payload"})
            continue

        payload = {
            "novel_settings_id": 1,
            "locale": locale,
            "title": translated_payload.get("title"),
            "description": translated_payload.get("description"),
            "seo_title": translated_payload.get("seo_title") or translated_payload.get("title"),
            "seo_description": translated_payload.get("seo_description") or translated_payload.get("description"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        supabase.table("novel_settings_translations").upsert(payload, on_conflict="novel_settings_id,locale").execute()
        translated_locales.append(locale)

    return {
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

def build_novel_multilocale_user_prompt(source_payload: dict, locale_prompt: str, glossary_prompt: str) -> str:
    return f"""
Translate the following novel metadata from Vietnamese to multiple locales.
{locale_prompt}
{glossary_prompt}

Source Metadata:
Title: {source_payload['title']}
Description: {source_payload['description']}

Return the result strictly as a JSON object where keys are the locale codes.
"""

async def upsert_homepage_translation(settings_payload: dict, locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None

    base_payload = prepare_homepage_settings_payload(settings_payload)
    translated_payload = await translate_homepage_payload_with_ai(base_payload, locale)

    source_hash = build_content_hash(json.dumps(base_payload, ensure_ascii=False, sort_keys=True))
    payload = {
        "homepage_settings_id": 1,
        "locale": locale,
        "warning_title": translated_payload.get("warning_title", ""),
        "warning_subtitle": translated_payload.get("warning_subtitle", ""),
        "warning_headline": translated_payload.get("warning_headline", ""),
        "warning_description": translated_payload.get("warning_description", ""),
        "features_title": translated_payload.get("features_title", ""),
        "features_json": translated_payload.get("features_json", []),
        "translation_status": "published",
        "translation_source": "ai",
        "translated_at": datetime.now(timezone.utc).isoformat(),
        "content_hash": source_hash,
    }

    try:
        return (
            supabase.table("homepage_settings_translations")
            .upsert(payload, on_conflict="homepage_settings_id,locale")
            .execute()
        )
    except Exception:
        return None

async def translate_wiki_payload_with_ai(entry_payload: dict, target_locale: str) -> dict:
    _active_model, model_catalog, api_keys = await resolve_ai_settings_for_translation()
    if not api_keys:
        raise HTTPException(status_code=503, detail="AI translation is not configured")

    glossary_prompt = build_glossary_prompt()
    source_payload = {
        "title": entry_payload.get("title") or "",
        "summary": entry_payload.get("summary") or "",
        "content": entry_payload.get("content") or "",
    }
    prompt = build_wiki_translation_prompt(
        source_payload=source_payload,
        target_locale=target_locale,
        glossary_prompt=glossary_prompt,
        source_locale=DEFAULT_LOCALE,
    )

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3},
    }

    def parse_wiki_translation_payload(raw_text: str) -> dict:
        parsed = parse_json_like_payload(raw_text)
        translated_title = sanitize_plaintext(str(parsed.get("title") or "").strip())
        translated_summary = sanitize_html(parsed.get("summary")) if parsed.get("summary") is not None else ""
        translated_content = sanitize_html(parsed.get("content")) if parsed.get("content") is not None else ""
        if not translated_title:
            raise ValueError("Missing title in JSON payload")
        return {
            "title": translated_title,
            "summary": translated_summary,
            "content": translated_content,
        }

    last_error: Optional[HTTPException] = None
    attempts: list[dict] = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for key_index, api_key in enumerate(api_keys, start=1):
            for model_name in model_catalog:
                await throttle_translation_request(model_name, api_key)
                gemini_url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model_name}:generateContent?key={api_key}"
                )
                response = await client.post(gemini_url, json=payload)
                if response.is_success:
                    data = response.json()
                    try:
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        return parse_wiki_translation_payload(raw_text)
                    except Exception as exc:
                        last_error = HTTPException(
                            status_code=502,
                            detail=f"Model {model_name}: invalid wiki translation payload: {exc}",
                        )
                        attempts.append(
                            {
                                "key_index": key_index,
                                "model": model_name,
                                "status_code": 502,
                                "message": f"invalid wiki translation payload: {exc}",
                            }
                        )
                        continue

                last_error = HTTPException(
                    status_code=response.status_code,
                    detail=f"Model {model_name}: Translation API error: {response.text}",
                )
                attempts.append(
                    {
                        "key_index": key_index,
                        "model": model_name,
                        "status_code": response.status_code,
                        "message": response.text,
                    }
                )
                if not is_translation_retryable(last_error):
                    raise HTTPException(
                        status_code=last_error.status_code,
                        detail=build_translation_failure_detail(
                            attempts,
                            len(api_keys),
                            len(model_catalog),
                            str(last_error.detail),
                        ),
                    )

    if last_error:
        raise HTTPException(
            status_code=last_error.status_code,
            detail=build_translation_failure_detail(
                attempts,
                len(api_keys),
                len(model_catalog),
                str(last_error.detail),
            ),
        )
    raise HTTPException(status_code=502, detail="Không có mô hình dịch wiki khả dụng")

async def translate_wiki_payloads_with_ai(entry_payload: dict, locales: list[str]) -> dict[str, dict]:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {}

    glossary_prompt = build_glossary_prompt()
    locale_prompt = build_target_locale_prompt(target_locales)
    source_payload = {
        "title": entry_payload.get("title") or "",
        "summary": entry_payload.get("summary") or "",
        "content": entry_payload.get("content") or "",
    }
    schema = build_multilocale_object_schema(
        target_locales,
        {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "content": {"type": "string"},
        },
    )
    system_instruction = build_wiki_multilocale_system_instruction()
    translated_payloads = await generate_structured_translation_payload(
        system_instruction=system_instruction,
        user_prompt=build_wiki_multilocale_user_prompt(
            source_payload=source_payload,
            locale_prompt=locale_prompt,
            glossary_prompt=glossary_prompt,
            source_locale=DEFAULT_LOCALE,
        ),
        response_json_schema=schema,
        parser=lambda raw_text: parse_multilocale_translation_payload(raw_text, target_locales, ["title", "summary", "content"]),
    )

    sanitized_payloads: dict[str, dict] = {}
    for locale in target_locales:
        locale_payload = translated_payloads.get(locale) or {}
        translated_title = sanitize_plaintext(str(locale_payload.get("title") or "").strip())
        translated_summary = sanitize_html(locale_payload.get("summary")) if locale_payload.get("summary") is not None else ""
        translated_content = sanitize_html(locale_payload.get("content")) if locale_payload.get("content") is not None else ""
        if not translated_title:
            raise ValueError(f"Missing wiki title for locale {locale}")
        sanitized_payloads[locale] = {
            "title": translated_title,
            "summary": translated_summary,
            "content": translated_content,
        }
    return sanitized_payloads

async def upsert_wiki_translations(entry_row: dict, locales: list[str]) -> dict:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {"translated_locales": [], "failed_translations": []}

    translated_payloads = await translate_wiki_payloads_with_ai(entry_row, target_locales)
    translated_at = datetime.now(timezone.utc).isoformat()
    translated_locales = []
    failed_translations = []
    for locale in target_locales:
        translated_payload = translated_payloads.get(locale)
        if not translated_payload:
            failed_translations.append({"locale": locale, "status_code": 502, "detail": "Missing wiki translation payload"})
            continue

        supabase.table("wiki_entry_translations").upsert(
            {
                "wiki_entry_id": entry_row["id"],
                "locale": locale,
                "title": translated_payload["title"],
                "summary": translated_payload.get("summary"),
                "content": translated_payload.get("content"),
                "updated_at": translated_at,
            },
            on_conflict="wiki_entry_id,locale",
        ).execute()
        translated_locales.append(locale)

    return {
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

async def upsert_wiki_translation(entry_row: dict, locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None

    translated_payload = await translate_wiki_payload_with_ai(entry_row, locale)
    payload = {
        "wiki_entry_id": entry_row["id"],
        "locale": locale,
        "title": translated_payload["title"],
        "summary": translated_payload.get("summary"),
        "content": translated_payload.get("content"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    return (
        supabase.table("wiki_entry_translations")
        .upsert(payload, on_conflict="wiki_entry_id,locale")
        .execute()
    )

# === ADMIN AUTH ===

async def verify_admin(authorization: Optional[str]) -> dict:

    """

    Xác thực token Admin từ Header Authorization (Bearer <token>).

    """

    token = extract_bearer_token(authorization)

    if not token:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED, 

            detail="Thiếu token xác thực. Hãy đăng nhập lại."

        )

    try:

        # Verify Supabase JWT only

        user_resp = supabase.auth.get_user(token)

        if not user_resp or not user_resp.user:

            raise HTTPException(

                status_code=status.HTTP_401_UNAUTHORIZED, 

                detail="Token không hợp lệ hoặc đã hết hạn."

            )

        

        # Truy vấn profile đểlấy role (editor/superadmin)

        profile_resp = supabase.table("profiles").select("role").eq("id", user_resp.user.id).execute()

        

        user_role = "editor" # Mặc định

        if profile_resp.data:

            user_role = profile_resp.data[0].get("role", "editor").lower()

            

        return {

            "id": user_resp.user.id,

            "email": user_resp.user.email,

            "role": user_role

        }

    except HTTPException:

        raise

    except Exception as e:

        print(f"Auth Error: {str(e)}")

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED, 

            detail="Token không hợp lệ hoặc đã hết hạn."

        )

# === FASTAPI APP ===

app = FastAPI(

    title="Mạt Thế API",

    description="API backend cho website đọc truyện Mạt Thế - Sinh Hoá Nguy Cơ",

    version="1.0.0",

    docs_url="/docs",

    redoc_url=None,  # disable redoc đểgiảm memory trên Render free tier

)

# === CORS MIDDLEWARE ===

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(

    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],

    allow_credentials=ALLOWED_ORIGINS != ["*"],

    allow_methods=["*"],

    allow_headers=["*"],

    expose_headers=["*"],

)

app.include_router(create_engagement_router(supabase))

app.include_router(hq_router)

app.include_router(oracle_router)

app.include_router(wiki_router)

app.include_router(reader_learning_router)

app.include_router(reader_grammar_router)

@app.middleware("http")

async def log_requests(request, call_next):

    # Log incoming request for better debugging on Render/Vercel

    print(f"DEBUG: {request.method} {request.url}")

    try:

        response = await call_next(request)

        return response

    except Exception as e:

        import traceback

        print(f"ERROR: Crash in {request.method} {request.url}: {str(e)}")

        print(traceback.format_exc())

        from fastapi.responses import JSONResponse

        return JSONResponse(

            status_code=500,

            content={"detail": "Internal Server Error"}

        )

# === DATA MODELS ===

class Chapter(BaseModel):
    id: int
    chapter_number: int
    title: str
    content_url: str  # Cloudflare R2 public URL
    created_at: str

    word_count: Optional[int] = None
    view_count: int = 0
    is_side_story: bool = False
    bgm_url: Optional[str] = None
    bgm_title: Optional[str] = None
    requested_locale: str = DEFAULT_LOCALE
    resolved_locale: str = DEFAULT_LOCALE
    is_fallback: bool = False
    translated_title: Optional[str] = None
    translated_content: Optional[str] = None

class ChaptersResponse(BaseModel):

    chapters: list[Chapter]

    total: int

    page: int

    limit: int

    total_pages: int

    max_chapter: int


CHAPTERS_HAS_BGM_COLUMNS: Optional[bool] = None


def _is_missing_bgm_schema_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "bgm_url" in message
        or "bgm_title" in message
        or "column" in message and ("does not exist" in message or "schema cache" in message)
    )


def chapters_support_bgm() -> bool:
    global CHAPTERS_HAS_BGM_COLUMNS
    if CHAPTERS_HAS_BGM_COLUMNS is not None:
        return CHAPTERS_HAS_BGM_COLUMNS

    try:
        supabase.table("chapters").select("bgm_url, bgm_title").limit(1).execute()
        CHAPTERS_HAS_BGM_COLUMNS = True
    except Exception as exc:
        if _is_missing_bgm_schema_error(exc):
            CHAPTERS_HAS_BGM_COLUMNS = False
        else:
            raise

    return bool(CHAPTERS_HAS_BGM_COLUMNS)


def build_chapter_select_fields() -> str:
    fields = "id, chapter_number, title, content_url, created_at, word_count, is_side_story"
    if chapters_support_bgm():
        fields += ", bgm_url, bgm_title"
    return fields


def normalize_bgm_payload(bgm_url: Optional[str], bgm_title: Optional[str]) -> dict[str, Optional[str]]:
    normalized_url = str(bgm_url or "").strip() or None
    normalized_title = str(bgm_title or "").strip() or None

    if not normalized_url:
        return {"bgm_url": None, "bgm_title": None}

    return {
        "bgm_url": normalized_url,
        "bgm_title": normalized_title,
    }

# ============================================================

# ROUTES

# ============================================================

@app.get("/api/health")

async def health_check():

    """Health check endpoint cho Render monitoring"""

    return {"status": "ok", "service": "mat-the-api"}

@app.get("/api/chapters", response_model=ChaptersResponse)

async def get_chapters(

    page: int = Query(1, ge=1, description="Số trang"),

    limit: int = Query(50, ge=1, le=100, description="Số chương mỗi trang"),

    sort: str = Query("asc", pattern="^(asc|desc)$", description="Thứ tự sắp xếp: asc hoặc desc"),

    search: Optional[str] = Query(None, description="Tìm kiếm theo tiêu đề hoặc số chương"),

    is_side_story: Optional[bool] = Query(None, description="Lọc ngoại truyện (true) hoặc mạch chính (false)"),

    locale: str = Query(DEFAULT_LOCALE, description="Requested locale"),
):
    """

    Lấy danh sách chương có phân trang.

    

    - **page**: Trang hiện tại (bắt đầu từ 1)

    - **limit**: Số chương mỗi trang (tối đa 100)

    - **sort**: Sắp xếp theo thứ tự chương (asc/desc)

    """

    try:

        offset = (page - 1) * limit

        # Build base query

        query = supabase.table("chapters").select(build_chapter_select_fields(), count="exact")

        

        # Apply filters

        if is_side_story is not None:

            query = query.eq("is_side_story", is_side_story)

        # Apply search if provided

        if search:

            if search.isdigit():

                query = query.eq("chapter_number", int(search))

            else:

                query = query.ilike("title", f"%{search}%")

        # Fetch page

        ascending = sort == "asc"

        resp = (

            query.order("chapter_number", desc=not ascending)

            .range(offset, offset + limit - 1)

            .execute()

        )

        total = resp.count or 0

        # Fetch max chapter number for realistic pagination bounding

        max_chapter_resp = (

            supabase.table("chapters")

            .select("chapter_number")

            .order("chapter_number", desc=True)

            .limit(1)

            .execute()

        )

        max_chapter = max_chapter_resp.data[0]["chapter_number"] if max_chapter_resp.data else total

        requested_locale = normalize_locale(locale)
        chapters = []
        for row in resp.data:
            chapter_payload = dict(row)
            translation = resolve_chapter_translation(chapter_payload["id"], requested_locale)
            chapter_payload["requested_locale"] = requested_locale
            chapter_payload["resolved_locale"] = requested_locale if translation else DEFAULT_LOCALE
            chapter_payload["is_fallback"] = requested_locale != DEFAULT_LOCALE and translation is None
            if translation:
                chapter_payload["title"] = translation.get("title") or chapter_payload["title"]
                chapter_payload["translated_title"] = translation.get("title")
            chapters.append(Chapter(**chapter_payload))
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        return ChaptersResponse(

            chapters=chapters,

            total=total,

            page=page,

            limit=limit,

            total_pages=total_pages,

            max_chapter=max_chapter,

        )

    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/chapters/{chapter_number}", response_model=Chapter)

async def get_chapter(
    chapter_number: int,
    locale: str = Query(DEFAULT_LOCALE, description="Requested locale"),
):
    """

    Lấy thông tin metadata của một chương bao gồm URL file R2 chứa nội dung.

    Frontend sẽ dùng content_url này để fetch nội dung thẳng từ Cloudflare CDN.

    

    - **chapter_number**: Số chương thực tế trong truyện

    """

    try:

        resp = (

            supabase.table("chapters")

            .select(build_chapter_select_fields())

            .eq("chapter_number", chapter_number)

            .single()

            .execute()

        )

        if not resp.data:

            raise HTTPException(status_code=404, detail=f"Chương {chapter_number} không tìm thấy")

        requested_locale = normalize_locale(locale)
        chapter_payload = dict(resp.data)
        chapter_payload["requested_locale"] = requested_locale
        chapter_payload["resolved_locale"] = DEFAULT_LOCALE
        chapter_payload["translated_title"] = chapter_payload["title"]

        translation = resolve_chapter_translation(chapter_payload["id"], requested_locale)
        if translation:
            chapter_payload["translated_title"] = translation.get("title") or chapter_payload["title"]
            chapter_payload["translated_content"] = translation.get("content")
            chapter_payload["title"] = chapter_payload["translated_title"]
            chapter_payload["resolved_locale"] = requested_locale
            chapter_payload["is_fallback"] = False
        else:
            try:
                chapter_payload["translated_content"] = fetch_r2_content(chapter_payload["content_url"])
            except Exception:
                chapter_payload["translated_content"] = None
            chapter_payload["is_fallback"] = requested_locale != DEFAULT_LOCALE

        return Chapter(**chapter_payload)

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# === TTS PROXY ===

@app.get("/api/tts", summary="Google Translate TTS Proxy")

async def tts_proxy(
    text: str = Query(..., max_length=200, description="Văn bản cần đọc (tối đa 200 ký tự)"),

    lang: str = Query("vi", description="Ngôn ngữ (vi, en, ...)"),

    speed: float = Query(1.0, ge=0.5, le=2.0, description="Tốc độ đọc"),

):

    """

    Proxy Google Translate TTS để tránh bị chặn khi gọi trực tiếp từ browser.

    Trả về audio MP3 stream.

    """

    url = (

        f"https://translate.google.com/translate_tts"

        f"?ie=UTF-8&client=tw-ob&tl={lang}&ttsspeed={speed}"

        f"&q={quote(text)}"

    )

    headers = {

        "User-Agent": (

            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "

            "AppleWebKit/537.36 (KHTML, like Gecko) "

            "Chrome/120.0.0.0 Safari/537.36"

        ),

        "Referer": "https://translate.google.com/",

        "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,*/*;q=0.5",

    }

    try:

        async with httpx.AsyncClient(timeout=15.0) as client:

            resp = await client.get(url, headers=headers, follow_redirects=True)

        if resp.status_code != 200:

            raise HTTPException(

                status_code=502,

                detail=f"Google TTS trả về {resp.status_code}"

            )

        return StreamingResponse(

            io.BytesIO(resp.content),

            media_type="audio/mpeg",

            headers={

                "Cache-Control": "public, max-age=3600",

                "Access-Control-Allow-Origin": "*",

            },

        )

    except httpx.TimeoutException:

        raise HTTPException(status_code=504, detail="Google TTS timeout")

    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChapterTtsRequest(BaseModel):
    chapter_id: int
    locale: str = DEFAULT_LOCALE
    voice: Optional[str] = None

@app.post("/api/tts/chapter", summary="Prepare chapter TTS metadata")
async def prepare_chapter_tts(body: ChapterTtsRequest):
    locale = normalize_locale(body.locale)
    chapter_resp = (
        supabase.table("chapters")
        .select("id, chapter_number, title, content_url")
        .eq("id", body.chapter_id)
        .single()
        .execute()
    )
    if not chapter_resp.data:
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter_row = chapter_resp.data
    translation = resolve_chapter_translation(chapter_row["id"], locale)
    resolved_locale = locale if translation else DEFAULT_LOCALE
    content_text = translation.get("content") if translation else fetch_r2_content(chapter_row["content_url"])
    content_hash = build_content_hash(content_text)
    audio_url = f"/api/tts?lang={resolved_locale}&text={quote((content_text or '')[:200])}"
    cached = False

    try:
        existing = (
            supabase.table("tts_audio_cache")
            .select("audio_url")
            .eq("entity_type", "chapter")
            .eq("entity_id", body.chapter_id)
            .eq("locale", resolved_locale)
            .eq("voice", body.voice or "default")
            .eq("content_hash", content_hash)
            .limit(1)
            .execute()
        )
        if existing.data:
            cached = True
            audio_url = existing.data[0].get("audio_url") or audio_url
        else:
            supabase.table("tts_audio_cache").upsert(
                {
                    "entity_type": "chapter",
                    "entity_id": body.chapter_id,
                    "locale": resolved_locale,
                    "voice": body.voice or "default",
                    "provider": "google-translate-tts",
                    "content_hash": content_hash,
                    "audio_url": audio_url,
                },
                on_conflict="entity_type,entity_id,locale,voice,content_hash",
            ).execute()
    except Exception:
        pass

    return {
        "chapter_id": body.chapter_id,
        "requested_locale": locale,
        "resolved_locale": resolved_locale,
        "cached": cached,
        "audio_url": audio_url,
        "content_hash": content_hash,
    }

# ============================================================

# ADMIN ROUTES (JWT Protected)

# ============================================================

class AdminChapterCreate(BaseModel):

    chapter_number: int

    title: str

    content: str  # Raw text content of the chapter

    is_side_story: bool = False

    bgm_url: Optional[str] = None

    bgm_title: Optional[str] = None

class AdminChapterUpdate(BaseModel):

    title: Optional[str] = None

    content: Optional[str] = None

    is_side_story: Optional[bool] = None

    bgm_url: Optional[str] = None

    bgm_title: Optional[str] = None

@app.post("/api/admin/chapters", summary="[Admin] Thêm chương mới")

async def admin_create_chapter(

    body: AdminChapterCreate,

    authorization: Optional[str] = Header(None),

):

    """Thêm chương mới: Upload nội dung lên R2, lưu metadata vào Supabase."""

    user = await verify_admin(authorization)

    if not r2_client:

        raise HTTPException(status_code=500, detail="R2 chưa được cấu hình trên server")

    # Check chapter number uniqueness

    existing = supabase.table("chapters").select("id").eq("chapter_number", body.chapter_number).execute()

    if existing.data:

        raise HTTPException(status_code=409, detail=f"Chương {body.chapter_number} đã tồn tại")

    sanitized_content = sanitize_html(body.content) or ""

    # Upload content to R2

    slug = slugify(f"chuong-{body.chapter_number}-{body.title}")

    object_key = f"chapters/{body.chapter_number:04d}-{slug}.txt"

    content_bytes = sanitized_content.encode("utf-8")

    r2_client.put_object(

        Bucket=R2_BUCKET,

        Key=object_key,

        Body=content_bytes,

        ContentType="text/plain; charset=utf-8",

    )

    content_url = f"{R2_PUBLIC_URL}/{object_key}"

    word_count = len(sanitized_content.split())

    bgm_payload = normalize_bgm_payload(body.bgm_url, body.bgm_title)
    if bgm_payload["bgm_url"] and not chapters_support_bgm():
        raise HTTPException(
            status_code=503,
            detail="Supabase chưa cài schema BGM cho chapters. Hãy chạy scripts/supabase_chapter_bgm.sql trước.",
        )

    # Insert metadata into Supabase

    insert_payload = {

        "chapter_number": body.chapter_number,

        "title": body.title,

        "content_url": content_url,

        "word_count": word_count,

        "is_side_story": body.is_side_story,

    }
    if chapters_support_bgm():
        insert_payload.update(bgm_payload)

    result = supabase.table("chapters").insert(insert_payload).execute()

    return {"message": "Thêm chương thành công", "chapter": result.data[0]}

@app.put("/api/admin/chapters/{chapter_number}", summary="[Admin] Sửa chương")

async def admin_update_chapter(

    chapter_number: int,

    body: AdminChapterUpdate,

    authorization: Optional[str] = Header(None),

):

    """Sửa tiêu đề và/hoặc nội dung chương."""

    await verify_admin(authorization)

    # Fetch existing chapter

    existing = supabase.table("chapters").select("*").eq("chapter_number", chapter_number).single().execute()

    if not existing.data:

        raise HTTPException(status_code=404, detail=f"Chương {chapter_number} không tìm thấy")

    chapter = existing.data

    update_data = {}
    bgm_payload = normalize_bgm_payload(body.bgm_url, body.bgm_title)

    # Update content on R2 if provided

    if body.content is not None:

        if not r2_client:

            raise HTTPException(status_code=500, detail="R2 chưa được cấu hình trên server")

        sanitized_content = sanitize_html(body.content) or ""

        # Derive key from content_url

        content_url = chapter["content_url"]

        object_key = content_url.replace(f"{R2_PUBLIC_URL}/", "")

        r2_client.put_object(

            Bucket=R2_BUCKET,

            Key=object_key,

            Body=sanitized_content.encode("utf-8"),

            ContentType="text/plain; charset=utf-8",

        )

        update_data["word_count"] = len(sanitized_content.split())

    if body.title is not None:

        update_data["title"] = body.title

    if body.is_side_story is not None:

        update_data["is_side_story"] = body.is_side_story

    if body.bgm_url is not None or body.bgm_title is not None:
        if bgm_payload["bgm_url"] and not chapters_support_bgm():
            raise HTTPException(
                status_code=503,
                detail="Supabase chưa cài schema BGM cho chapters. Hãy chạy scripts/supabase_chapter_bgm.sql trước.",
            )
        if chapters_support_bgm():
            update_data.update(bgm_payload)

    if update_data:

        result = supabase.table("chapters").update(update_data).eq("chapter_number", chapter_number).execute()

        return {"message": "Cập nhật thành công", "chapter": result.data[0]}

    return {"message": "Không có gì thay đổi"}

@app.post("/api/admin/chapters/{chapter_number}/translate", summary="[Admin] Translate chapter to EN/ZH-CN/JA")
async def admin_translate_chapter(
    chapter_number: int,
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    chapter_resp = (
        supabase.table("chapters")
        .select("*")
        .eq("chapter_number", chapter_number)
        .single()
        .execute()
    )
    if not chapter_resp.data:
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter_row = chapter_resp.data
    content_text = fetch_r2_content(chapter_row["content_url"])
    try:
        translation_result = await upsert_chapter_translations(
            chapter_row,
            chapter_row["title"],
            content_text,
            list(TRANSLATION_TARGET_LOCALES),
        )
        translated_locales = translation_result["translated_locales"]
        failed_translations = translation_result["failed_translations"]
    except HTTPException as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(TRANSLATION_TARGET_LOCALES),
                "status_code": exc.status_code,
                "detail": str(exc.detail),
            }
        ]
    except Exception as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(TRANSLATION_TARGET_LOCALES),
                "status_code": 500,
                "detail": str(exc),
            }
        ]

    return {
        "message": "Chapter translated",
        "chapter_number": chapter_number,
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

@app.post("/api/admin/chapters/{chapter_number}/improve-quality", summary="[Admin] Improve chapter translation quality")
async def admin_improve_chapter_translation_quality(
    chapter_number: int,
    force: bool = Query(False, description="Force quality refinement even if the chapter was already refined"),
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    chapter_resp = (
        supabase.table("chapters")
        .select("*")
        .eq("chapter_number", chapter_number)
        .single()
        .execute()
    )
    if not chapter_resp.data:
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter_row = chapter_resp.data
    content_text = fetch_r2_content(chapter_row["content_url"])
    existing_translation_resp = (
        supabase.table("chapter_translations")
        .select("locale, translation_status, translation_source")
        .eq("chapter_id", chapter_row["id"])
        .in_("locale", list(TRANSLATION_TARGET_LOCALES))
        .execute()
    )
    published_locales: list[str] = []
    needed_locales: list[str] = []
    skipped_locales: list[str] = []
    for row in (existing_translation_resp.data or []):
        locale = row.get("locale")
        if not locale or row.get("translation_status") != "published":
            continue
        published_locales.append(locale)
        if force or row.get("translation_source") != "ai_refine":
            needed_locales.append(locale)
        else:
            skipped_locales.append(locale)

    if not published_locales:
        return {
            "message": "No existing published translation found to improve",
            "chapter_number": chapter_number,
            "translated_locales": [],
            "failed_translations": [],
            "skipped_locales": [],
        }

    if not needed_locales:
        return {
            "message": "Chapter translation quality already up to date",
            "chapter_number": chapter_number,
            "translated_locales": [],
            "failed_translations": [],
            "skipped_locales": sorted(set(skipped_locales)),
        }

    try:
        improvement_result = await improve_chapter_translations(
            chapter_row,
            chapter_row["title"],
            content_text,
            needed_locales,
        )
        translated_locales = improvement_result["translated_locales"]
        failed_translations = improvement_result["failed_translations"]
    except HTTPException as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(TRANSLATION_TARGET_LOCALES),
                "status_code": exc.status_code,
                "detail": str(exc.detail),
            }
        ]
    except Exception as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(TRANSLATION_TARGET_LOCALES),
                "status_code": 500,
                "detail": str(exc),
            }
        ]

    return {
        "message": "Chapter translation quality improved",
        "chapter_number": chapter_number,
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
        "skipped_locales": sorted(set(skipped_locales)),
    }

class AdminBatchTranslateRequest(BaseModel):
    start_chapter: int = 1
    end_chapter: int
    only_missing: bool = True

class AdminBatchImproveQualityRequest(BaseModel):
    start_chapter: int = 1
    end_chapter: int
    only_unrefined: bool = True
    force: bool = False

class AdminChapterStatusRequest(BaseModel):
    chapter_numbers: list[int]

@app.post("/api/admin/chapters/translate-batch", summary="[Admin] Batch translate chapters to EN/ZH-CN/JA")
async def admin_translate_chapters_batch(
    body: AdminBatchTranslateRequest,
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    start_chapter = max(1, body.start_chapter)
    end_chapter = max(start_chapter, body.end_chapter)

    chapters_resp = (
        supabase.table("chapters")
        .select("*")
        .gte("chapter_number", start_chapter)
        .lte("chapter_number", end_chapter)
        .order("chapter_number")
        .execute()
    )
    chapter_rows = chapters_resp.data or []
    if not chapter_rows:
        raise HTTPException(status_code=404, detail="No chapters found in selected range")

    translation_map: dict[int, set[str]] = {}
    if body.only_missing:
        translation_resp = (
            supabase.table("chapter_translations")
            .select("chapter_id, locale, translation_status")
            .eq("translation_status", "published")
            .in_("chapter_id", [row["id"] for row in chapter_rows])
            .execute()
        )
        for row in (translation_resp.data or []):
            translation_map.setdefault(row["chapter_id"], set()).add(row["locale"])

    translated_chapters = []
    skipped_chapters = []
    failed_chapters = []

    for chapter_row in chapter_rows:
        needed_locales = list(TRANSLATION_TARGET_LOCALES)
        if body.only_missing:
            existing_locales = translation_map.get(chapter_row["id"], set())
            needed_locales = [locale_code for locale_code in needed_locales if locale_code not in existing_locales]
            if not needed_locales:
                skipped_chapters.append(chapter_row["chapter_number"])
                continue

        try:
            content_text = fetch_r2_content(chapter_row["content_url"])
            translation_result = await upsert_chapter_translations(
                chapter_row,
                chapter_row["title"],
                content_text,
                needed_locales,
            )
            completed_locales = translation_result["translated_locales"]
            chapter_locale_errors = [
                f"{item['locale']}: {item.get('detail') or 'Translation failed'}"
                for item in (translation_result.get("failed_translations") or [])
            ]

            if completed_locales:
                translated_chapters.append(
                    {
                        "chapter_number": chapter_row["chapter_number"],
                        "translated_locales": completed_locales,
                    }
                )
            if chapter_locale_errors:
                failed_chapters.append(
                    {
                        "chapter_number": chapter_row["chapter_number"],
                        "status_code": 500,
                        "detail": "\n".join(chapter_locale_errors),
                    }
                )
        except HTTPException as exc:
            failed_chapters.append(
                {
                    "chapter_number": chapter_row["chapter_number"],
                    "status_code": exc.status_code,
                    "detail": str(exc.detail),
                }
            )
        except Exception as exc:
            failed_chapters.append(
                {
                    "chapter_number": chapter_row["chapter_number"],
                    "status_code": 500,
                    "detail": str(exc),
                }
            )

    return {
        "message": "Batch chapter translation completed",
        "range": {"start_chapter": start_chapter, "end_chapter": end_chapter},
        "only_missing": body.only_missing,
        "translated_count": len(translated_chapters),
        "skipped_count": len(skipped_chapters),
        "failed_count": len(failed_chapters),
        "translated_chapters": translated_chapters,
        "skipped_chapters": skipped_chapters,
        "failed_chapters": failed_chapters,
    }

@app.post("/api/admin/chapters/improve-quality-batch", summary="[Admin] Batch improve chapter translation quality")
async def admin_improve_chapters_quality_batch(
    body: AdminBatchImproveQualityRequest,
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    start_chapter = max(1, body.start_chapter)
    end_chapter = max(start_chapter, body.end_chapter)

    chapters_resp = (
        supabase.table("chapters")
        .select("*")
        .gte("chapter_number", start_chapter)
        .lte("chapter_number", end_chapter)
        .order("chapter_number")
        .execute()
    )
    chapter_rows = chapters_resp.data or []
    if not chapter_rows:
        raise HTTPException(status_code=404, detail="No chapters found in selected range")

    translation_rows_resp = (
        supabase.table("chapter_translations")
        .select("chapter_id, locale, translation_status, translation_source")
        .in_("chapter_id", [row["id"] for row in chapter_rows])
        .execute()
    )
    published_map: dict[int, dict[str, str]] = {}
    for row in (translation_rows_resp.data or []):
        chapter_id = row.get("chapter_id")
        locale = row.get("locale")
        if not chapter_id or not locale or row.get("translation_status") != "published":
            continue
        published_map.setdefault(chapter_id, {})[locale] = str(row.get("translation_source") or "")

    translated_chapters = []
    skipped_chapters = []
    failed_chapters = []

    for chapter_row in chapter_rows:
        chapter_sources = published_map.get(chapter_row["id"], {})
        published_locales = [locale for locale in TRANSLATION_TARGET_LOCALES if locale in chapter_sources]
        if not published_locales:
            skipped_chapters.append(chapter_row["chapter_number"])
            continue

        if body.force:
            needed_locales = published_locales
        elif body.only_unrefined:
            needed_locales = [locale for locale in published_locales if chapter_sources.get(locale) != "ai_refine"]
        else:
            needed_locales = published_locales

        if not needed_locales:
            skipped_chapters.append(chapter_row["chapter_number"])
            continue

        try:
            content_text = fetch_r2_content(chapter_row["content_url"])
            improvement_result = await improve_chapter_translations(
                chapter_row,
                chapter_row["title"],
                content_text,
                needed_locales,
            )
            completed_locales = improvement_result["translated_locales"]
            chapter_locale_errors = [
                f"{item['locale']}: {item.get('detail') or 'Quality refinement failed'}"
                for item in (improvement_result.get("failed_translations") or [])
            ]

            if completed_locales:
                translated_chapters.append(
                    {
                        "chapter_number": chapter_row["chapter_number"],
                        "translated_locales": completed_locales,
                    }
                )
            if chapter_locale_errors:
                failed_chapters.append(
                    {
                        "chapter_number": chapter_row["chapter_number"],
                        "status_code": 500,
                        "detail": "\n".join(chapter_locale_errors),
                    }
                )
        except HTTPException as exc:
            failed_chapters.append(
                {
                    "chapter_number": chapter_row["chapter_number"],
                    "status_code": exc.status_code,
                    "detail": str(exc.detail),
                }
            )
        except Exception as exc:
            failed_chapters.append(
                {
                    "chapter_number": chapter_row["chapter_number"],
                    "status_code": 500,
                    "detail": str(exc),
                }
            )

    return {
        "message": "Batch chapter quality improvement completed",
        "range": {"start_chapter": start_chapter, "end_chapter": end_chapter},
        "only_unrefined": body.only_unrefined,
        "force": body.force,
        "translated_count": len(translated_chapters),
        "skipped_count": len(skipped_chapters),
        "failed_count": len(failed_chapters),
        "translated_chapters": translated_chapters,
        "skipped_chapters": skipped_chapters,
        "failed_chapters": failed_chapters,
    }

@app.post("/api/admin/chapters/translation-statuses", summary="[Admin] Get chapter translation statuses")
async def admin_get_chapter_translation_statuses(
    body: AdminChapterStatusRequest,
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    requested_numbers = sorted({int(number) for number in body.chapter_numbers if int(number) > 0})
    if not requested_numbers:
        return {"statuses": []}

    chapter_rows_resp = (
        supabase.table("chapters")
        .select("id, chapter_number")
        .in_("chapter_number", requested_numbers)
        .execute()
    )
    chapter_rows = chapter_rows_resp.data or []
    if not chapter_rows:
        return {"statuses": []}

    chapter_id_to_number = {row["id"]: row["chapter_number"] for row in chapter_rows}
    translation_rows_resp = (
        supabase.table("chapter_translations")
        .select("chapter_id, locale, translation_status, translation_source, attempt_count, last_error, updated_at")
        .in_("chapter_id", list(chapter_id_to_number.keys()))
        .execute()
    )
    translation_rows = translation_rows_resp.data or []

    status_map: dict[int, dict] = {}
    for chapter_number in requested_numbers:
        status_map[chapter_number] = {
            "chapter_number": chapter_number,
            "published_locales": [],
            "refined_locales": [],
            "failed_locales": [],
            "in_progress_locales": [],
            "published_count": 0,
            "refined_count": 0,
            "can_improve": False,
            "failed_count": 0,
            "in_progress_count": 0,
            "attempt_count": 0,
            "last_error": None,
            "last_error_locale": None,
            "last_error_updated_at": None,
        }

    for row in translation_rows:
        chapter_number = chapter_id_to_number.get(row["chapter_id"])
        if not chapter_number:
            continue

        target = status_map.setdefault(
            chapter_number,
            {
                "chapter_number": chapter_number,
                "published_locales": [],
                "refined_locales": [],
                "failed_locales": [],
                "in_progress_locales": [],
                "published_count": 0,
                "refined_count": 0,
                "can_improve": False,
                "failed_count": 0,
                "in_progress_count": 0,
                "attempt_count": 0,
                "last_error": None,
                "last_error_locale": None,
                "last_error_updated_at": None,
            },
        )
        locale = row.get("locale")
        row_status = row.get("translation_status")
        row_source = str(row.get("translation_source") or "")
        row_attempt = int(row.get("attempt_count") or 0)
        row_updated_at = row.get("updated_at")
        row_error = row.get("last_error")

        if row_status == "published" and locale:
            target["published_locales"].append(locale)
            if row_source == "ai_refine":
                target["refined_locales"].append(locale)
        elif row_status == "failed" and locale:
            target["failed_locales"].append(locale)
        elif row_status == "in_progress" and locale:
            target["in_progress_locales"].append(locale)

        target["attempt_count"] = max(target["attempt_count"], row_attempt)
        if row_error and (target["last_error_updated_at"] is None or (row_updated_at or "") >= (target["last_error_updated_at"] or "")):
            target["last_error"] = row_error
            target["last_error_locale"] = locale
            target["last_error_updated_at"] = row_updated_at

    for chapter_number, payload in status_map.items():
        payload["published_locales"] = sorted(set(payload["published_locales"]))
        payload["refined_locales"] = sorted(set(payload["refined_locales"]))
        payload["failed_locales"] = sorted(set(payload["failed_locales"]))
        payload["in_progress_locales"] = sorted(set(payload["in_progress_locales"]))
        payload["published_count"] = len(payload["published_locales"])
        payload["refined_count"] = len(payload["refined_locales"])
        payload["failed_count"] = len(payload["failed_locales"])
        payload["in_progress_count"] = len(payload["in_progress_locales"])
        payload["can_improve"] = any(locale not in payload["refined_locales"] for locale in payload["published_locales"])
        payload["status_label"] = (
            "Đang dịch"
            if payload["in_progress_count"] > 0
            else f"Đã hoàn thành {payload['published_count']}/3"
            if payload["published_count"] == 3
            else f"Đã lỗi {payload['attempt_count']} lần"
            if payload["failed_count"] > 0
            else f"Đã hoàn thành {payload['published_count']}/3"
            if payload["published_count"] > 0
            else "Chưa dịch"
        )

    for payload in status_map.values():
        payload["quality_status_label"] = (
            f"Đã nâng chất lượng {payload['refined_count']}/{payload['published_count']}"
            if payload["refined_count"] > 0
            else "Chưa nâng chất lượng"
        )

    return {"statuses": [status_map[number] for number in requested_numbers]}

class NovelSettings(BaseModel):
    title: str

    author: str

    description: str

    cover_url: str

    status: str

    genres: list[str]

    donate_qr_url: str = ""

    total_chapters: int = 0

    max_chapter: int = 0

    total_views: int = 0
    total_likes: int = 0
    ai_model_name: str = BULK_TRANSLATION_MODEL_FALLBACK
    ai_quality_model_name: str = QUALITY_TRANSLATION_MODEL_FALLBACK
    ai_model_catalog: list[str] = DEFAULT_TRANSLATION_MODELS.copy()
    ai_api_keys_count: int = 0
    has_ai_key: bool = False  # Frontend diagnostic
    requested_locale: str = DEFAULT_LOCALE
    resolved_locale: str = DEFAULT_LOCALE
    is_fallback: bool = False

class AdminNovelUpdate(BaseModel):
    title: Optional[str] = None

    author: Optional[str] = None

    description: Optional[str] = None

    cover_url: Optional[str] = None

    status: Optional[str] = None

    genres: Optional[list[str]] = None

    donate_qr_url: Optional[str] = None
    ai_model_name: Optional[str] = None
    ai_quality_model_name: Optional[str] = None
    ai_model_catalog: Optional[list[str]] = None
    ai_api_key: Optional[str] = None
    ai_api_keys: Optional[list[str]] = None
    append_ai_api_keys: Optional[list[str]] = None
    remove_ai_key_indexes: Optional[list[int]] = None

@app.get("/api/novel", response_model=NovelSettings)

async def get_novel_settings(locale: str = Query(DEFAULT_LOCALE, description="Requested locale")):
    """Lấy thông tin chung của truyện (Tên, tác giả, mô tả...)"""

    try:

        # 1. Fetch current stats (Total chapters, Max chapter, and aggregated View/Like counts)

        # We fetch all at once to minimize Supabase calls

        stats_resp = supabase.table("chapters").select("chapter_number, view_count, likes_count", count="exact").order("chapter_number", desc=True).execute()

        

        total_chapters = stats_resp.count or 0

        max_chapter = stats_resp.data[0]["chapter_number"] if stats_resp.data else 0

        total_views = sum(row.get("view_count", 0) for row in stats_resp.data) if stats_resp.data else 0

        total_likes = sum(row.get("likes_count", 0) for row in stats_resp.data) if stats_resp.data else 0

        # 2. Fetch novel settings

        resp = supabase.table("novel_settings").select("*").eq("id", 1).single().execute()

        

        default_settings = {

            "title": "Mạt Thế - Sinh Hoá Nguy Cơ",

            "author": "Hàn Nhược Tuyết",

            "description": "Truyện lấy bối cảnh tận thế đột nhiên phủ xuống, thây ma lan tràn, quái vật dị biến nổi lên khắp nơi, loài người bị đẩy vào một trò chơi tàn khốc kinh hoàng nhưng cũng ẩn chứa cơ hội lớn lao...",

            "cover_url": "https://pub-28de8065099f4ffea76bd6dc28a9bcf3.r2.dev/matthe-hero.jpg",

            "status": "Đang cập nhật",

            "genres": ["Mạt Thế", "Sinh Tồn", "Hệ Thống", "Dị Năng"],

            "donate_qr_url": "",

            "total_chapters": total_chapters,

            "max_chapter": max_chapter,

            "total_views": total_views,
            "total_likes": total_likes,
            "ai_model_name": BULK_TRANSLATION_MODEL_FALLBACK,
            "ai_quality_model_name": QUALITY_TRANSLATION_MODEL_FALLBACK,
            "ai_model_catalog": DEFAULT_TRANSLATION_MODELS.copy(),
            "ai_api_keys_count": 0,
        }

        requested_locale = normalize_locale(locale)

        if not resp.data:
            default_settings["requested_locale"] = requested_locale
            default_settings["resolved_locale"] = DEFAULT_LOCALE
            default_settings["is_fallback"] = requested_locale != DEFAULT_LOCALE
            return NovelSettings(**default_settings)
        

        # Merge data

        model_fields = NovelSettings.__fields__.keys()

        final_data = {k: v for k, v in resp.data.items() if k in model_fields}

        final_data["description"] = sanitize_html(final_data.get("description")) or ""

        final_data["total_chapters"] = total_chapters

        final_data["max_chapter"] = max_chapter

        final_data["total_views"] = total_views
        final_data["total_likes"] = total_likes
        final_data["ai_model_name"] = resp.data.get("ai_model_name", BULK_TRANSLATION_MODEL_FALLBACK)
        final_data["ai_quality_model_name"] = resp.data.get("ai_quality_model_name", QUALITY_TRANSLATION_MODEL_FALLBACK)
        final_data["ai_model_catalog"] = normalize_model_catalog(resp.data.get("ai_model_catalog"), final_data["ai_model_name"])
        key_catalog = normalize_api_key_catalog(resp.data.get("ai_api_keys"), resp.data.get("ai_api_key") or "")
        final_data["ai_api_keys_count"] = len(key_catalog)
        final_data["requested_locale"] = requested_locale
        final_data["resolved_locale"] = DEFAULT_LOCALE
        final_data["is_fallback"] = False

        translation = resolve_novel_translation(requested_locale)
        if translation:
            if translation.get("title"):
                final_data["title"] = translation["title"]
            if translation.get("description"):
                final_data["description"] = translation["description"]
            final_data["resolved_locale"] = requested_locale
        elif requested_locale != DEFAULT_LOCALE:
            final_data["is_fallback"] = True
        

        # Security: Never return the actual API key to the frontend

        db_key = resp.data.get("ai_api_key")
        final_data["has_ai_key"] = bool(key_catalog or (db_key and len(db_key) > 5))
        if "ai_api_key" in final_data:
            del final_data["ai_api_key"]
        if "ai_api_keys" in final_data:
            del final_data["ai_api_keys"]
        

        return NovelSettings(**final_data)

    except Exception as e:

        print(f"DEBUG: get_novel_settings error: {str(e)}")

        # Fallback dữ liệu mặc định nếu lỗi DB (tránh sập trang chủ)

        return NovelSettings(

            title="Mạt Thế - Sinh Hoá Nguy Cơ",

            author="Hàn Nhược Tuyết",

            description="Lỗi tải dữ liệu. Hãy thử lại sau.",

            cover_url="/hero-bg.png",

            status="Đang cập nhật",

            genres=["Mạt Thế"],

            total_chapters=0,

            max_chapter=0,

            total_views=0,
            total_likes=0,
            ai_model_name=BULK_TRANSLATION_MODEL_FALLBACK,
            ai_quality_model_name=QUALITY_TRANSLATION_MODEL_FALLBACK,
            ai_model_catalog=DEFAULT_TRANSLATION_MODELS.copy(),
            ai_api_keys_count=0,
            requested_locale=normalize_locale(locale),
            resolved_locale=DEFAULT_LOCALE,
            is_fallback=normalize_locale(locale) != DEFAULT_LOCALE,
        )

@app.put("/api/admin/novel", summary="[Admin] Cập nhật thông tin truyện & cấu hình hệ thống")

async def admin_update_novel(

    body: AdminNovelUpdate,

    authorization: Optional[str] = Header(None),

):

    """Cập nhật các thông tin chung của truyện và cấu hình AI."""

    user = await verify_admin(authorization)

    

    data = body.model_dump(exclude_none=True)

    if not data:

        return {"message": "Không có gì thay đổi"}

    

    if "description" in data:

        data["description"] = sanitize_html(data.get("description")) or ""

    ai_fields = {
        "ai_model_name",
        "ai_quality_model_name",
        "ai_model_catalog",
        "ai_api_key",
        "ai_api_keys",
        "append_ai_api_keys",
        "remove_ai_key_indexes",
    }
    if any(field in data for field in ai_fields) and user.get("role") != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Only superadmin can update AI model or API key.",
        )

    if "ai_model_catalog" in data:
        data["ai_model_catalog"] = normalize_model_catalog(
            data.get("ai_model_catalog"),
            data.get("ai_model_name") or BULK_TRANSLATION_MODEL_FALLBACK,
        )

    if "ai_api_keys" in data:
        normalized_keys = normalize_api_key_catalog(data.get("ai_api_keys"), data.get("ai_api_key") or "")
        data["ai_api_keys"] = normalized_keys
        if normalized_keys:
            data["ai_api_key"] = normalized_keys[0]
        else:
            data["ai_api_key"] = None

    if "append_ai_api_keys" in data or "remove_ai_key_indexes" in data:
        existing_settings_resp = (
            supabase.table("novel_settings")
            .select("ai_api_key, ai_api_keys")
            .eq("id", 1)
            .single()
            .execute()
        )
        existing_settings = existing_settings_resp.data or {}
        current_keys = normalize_api_key_catalog(
            existing_settings.get("ai_api_keys"),
            existing_settings.get("ai_api_key") or "",
        )
        remove_indexes = sorted(
            {
                int(index)
                for index in (data.get("remove_ai_key_indexes") or [])
                if isinstance(index, int) or (isinstance(index, str) and str(index).isdigit())
            }
        )
        remaining_keys = [
            item for index, item in enumerate(current_keys) if index not in remove_indexes
        ]
        appended_keys = normalize_api_key_catalog(data.get("append_ai_api_keys"), "")
        merged_keys = list(dict.fromkeys([*remaining_keys, *appended_keys]))
        data["ai_api_keys"] = merged_keys
        data["ai_api_key"] = merged_keys[0] if merged_keys else None
        data.pop("append_ai_api_keys", None)
        data.pop("remove_ai_key_indexes", None)

    # Update novel settings (ID 1)
    # Do not return raw API keys to the admin frontend.
    schema_warning = None
    try:
        result = supabase.table("novel_settings").upsert({**data, "id": 1}).execute()
    except Exception as exc:
        if "ai_quality_model_name" in data and "ai_quality_model_name" in str(exc):
            fallback_data = dict(data)
            fallback_data.pop("ai_quality_model_name", None)
            result = supabase.table("novel_settings").upsert({**fallback_data, "id": 1}).execute()
            schema_warning = "Database schema is missing ai_quality_model_name. Run scripts/supabase_ai_quality_model.sql to persist the quality model."
        else:
            raise
    saved_row = result.data[0] if result.data else {"id": 1, **data}
    key_catalog = normalize_api_key_catalog(saved_row.get("ai_api_keys"), saved_row.get("ai_api_key") or "")
    return {
        "message": "Cập nhật thành công",
        "schema_warning": schema_warning,
        "data": {
            "id": saved_row.get("id", 1),
            "title": saved_row.get("title"),
            "author": saved_row.get("author"),
            "status": saved_row.get("status"),
            "ai_model_name": saved_row.get("ai_model_name", BULK_TRANSLATION_MODEL_FALLBACK),
            "ai_quality_model_name": saved_row.get("ai_quality_model_name", QUALITY_TRANSLATION_MODEL_FALLBACK),
            "ai_model_catalog": normalize_model_catalog(
                saved_row.get("ai_model_catalog"),
                saved_row.get("ai_model_name") or BULK_TRANSLATION_MODEL_FALLBACK,
            ),
            "has_ai_key": bool(key_catalog),
            "ai_api_keys_count": len(key_catalog),
        },
    }

@app.post("/api/admin/novel/translate", summary="[Admin] Dịch AI thông tin truyện")
async def admin_translate_novel_i18n(
    authorization: Optional[str] = Header(None),
    locale: Optional[str] = Query(None, description="Specific locale to translate"),
):
    """Dịch AI cho Tên truyện, Tác giả, Mô tả từ tiếng Việt sang các locale còn lại."""
    await verify_admin(authorization)

    resp = supabase.table("novel_settings").select("*").eq("id", 1).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Novel settings not found")

    if locale:
        target_locales = [normalize_locale(locale)]
    else:
        target_locales = [item for item in SUPPORTED_LOCALES if item != DEFAULT_LOCALE]

    result = await upsert_novel_translations(resp.data, target_locales)
    return {
        "message": "Đã dịch thông tin truyện",
        "translated_locales": result["translated_locales"],
        "failed_translations": result["failed_translations"],
    }
class HomepageSettings(BaseModel):
    warning_title: Optional[str] = None
    warning_subtitle: Optional[str] = None
    warning_headline: Optional[str] = None
    warning_description: Optional[str] = None
    features_title: Optional[str] = None
    features_json: Optional[list] = None
    requested_locale: str = DEFAULT_LOCALE
    resolved_locale: str = DEFAULT_LOCALE
    is_fallback: bool = False

class HomepageAutoSaveResponse(BaseModel):
    message: str
    settings: dict
    auto_translated_locales: list[str] = []
    failed_translations: list[dict] = []

class Profile(BaseModel):

    id: str

    email: str

    role: str

    display_name: Optional[str] = None

    avatar_url: Optional[str] = None

    created_at: str

class AccountInvite(BaseModel):

    email: str

    password: str

    display_name: str

    role: str = "editor"

@app.get("/api/admin/users", response_model=List[Profile], summary="[Admin] Danh sách nhân sự")

async def admin_get_users(authorization: Optional[str] = Header(None)):

    """Lấy danh sách tất cả nhân sự (Profiles). Chỉdành cho SuperAdmin."""

    user = await verify_admin(authorization)

    

    # Chỉ SuperAdmin mới được xem danh sách nhân sự

    if user["role"] != "superadmin":

        raise HTTPException(status_code=403, detail="Chỉ SuperAdmin mới có quyền xem danh sách nhân sự")

    

    resp = supabase.table("profiles").select("*").order("created_at", desc=True).execute()

    return resp.data

@app.post("/api/admin/invite", summary="[Admin] Tạo tài khoản nhân sự mới")

async def admin_invite_user(

    body: AccountInvite,

    authorization: Optional[str] = Header(None)

):

    """Tạo tài khoản Auth và Profile mới cho nhân viên. Chỉdành cho SuperAdmin."""

    user = await verify_admin(authorization)

    

    # Kiểm tra quyền SuperAdmin

    if user["role"] != "superadmin":

        raise HTTPException(status_code=403, detail="Chỉ SuperAdmin mới có quyền tạo nhân sự mới")

    

    # 1. Tạo user trong hệ thống Auth của Supabase bằng Service Role

    try:

        # auth.admin.create_user cần service_role key

        auth_resp = supabase.auth.admin.create_user({

            "email": body.email,

            "password": body.password,

            "email_confirm": True,

            "user_metadata": {"full_name": body.display_name}

        })

        

        if not auth_resp or not auth_resp.user:

            raise Exception("Supabase không trả về thông tin user mới.")

        # 2. Update role trong bảng profiles

        if body.role != "editor":

            supabase.table("profiles").update({"role": body.role}).eq("id", auth_resp.user.id).execute()

            

        return {"message": "Đã tạo tài khoản thành công", "user_id": auth_resp.user.id}

    except Exception as e:

        error_msg = str(e)

        if "User not allowed" in error_msg:

            detail = "Lỗi: Backend chưa được cấp quyền Admin (Service Role Key). Hãy kiểm tra SUPABASE_KEY."

        else:

            detail = f"Lỗi tạo tài khoản: {error_msg}"

        raise HTTPException(status_code=500, detail=detail)

class ProfileUpdate(BaseModel):

    display_name: Optional[str] = None

    role: Optional[str] = None

@app.get("/api/user/role", summary="Lấy quyền (Role) của người dùng hiện tại")

async def get_current_user_role(authorization: Optional[str] = Header(None)):

    """Kiểm tra quyền của người dùng (editor hay superadmin)."""

    user = await verify_admin(authorization)

    return {"role": user["role"]}

@app.put("/api/admin/personnel/{user_id}", summary="[Admin] Cập nhật nhân sự")

async def admin_update_user(

    user_id: str,

    body: ProfileUpdate,

    authorization: Optional[str] = Header(None)

):

    """Cập nhật profile nhân sự (tên, vai trò, email, mật khẩu). Chỉdành cho SuperAdmin."""

    user = await verify_admin(authorization)

    if user["role"] != "superadmin":

        raise HTTPException(status_code=403, detail="Chỉ SuperAdmin mới có quyền chỉnh sửa nhân sự")

    try:

        from datetime import datetime, timezone

        # Update profile table

        profile_data = {}

        if body.display_name is not None:

            profile_data["display_name"] = body.display_name

        if body.role is not None:

            profile_data["role"] = body.role

        if body.email is not None:

            profile_data["email"] = body.email

        if profile_data:

            profile_data["updated_at"] = datetime.now(timezone.utc).isoformat()

            supabase.table("profiles").update(profile_data).eq("id", user_id).execute()

        # Update Auth fields (email, password)

        auth_updates = {}

        if body.email:

            auth_updates["email"] = body.email

        if body.password:

            if len(body.password) < 6:

                raise HTTPException(status_code=400, detail="Mật khẩu phải có tối thiểu 6 ký tự")

            auth_updates["password"] = body.password

        if auth_updates:

            supabase.auth.admin.update_user_by_id(user_id, auth_updates)

        return {"message": "Đã cập nhật thông tin nhân sự thành công"}

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật: {str(e)}")

@app.delete("/api/admin/users/{user_id}", summary="[Admin] Xoá nhân sự")

async def admin_delete_user(

    user_id: str,

    authorization: Optional[str] = Header(None)

):

    """Xoá tài khoản nhân sự. Chỉdành cho SuperAdmin."""

    user = await verify_admin(authorization)

    

    # Kiểm tra quyền SuperAdmin

    if user["role"] != "superadmin":

        raise HTTPException(status_code=403, detail="Chỉ SuperAdmin mới có quyền xoá nhân sự")

    

    try:

        # Xoá trong Auth (bảng profiles sẽ tự động xoá do CASCADE)

        supabase.auth.admin.delete_user(user_id)

        return {"message": "Đã xoá nhân sự thành công"}

    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Lỗi khi xoá nhân sự: {str(e)}")

# ============================================================

# MAP LOCATIONS API (Phase 09)

# ============================================================

class MapLocation(BaseModel):

    id: str

    name: str

    type: str  # safe_zone, danger_zone, neutral, outpost, ruins

    description: Optional[str] = None

    lat: float

    lng: float

    image_url: Optional[str] = None

    created_at: str

class AdminMapLocationIn(BaseModel):

    name: str

    type: str

    description: Optional[str] = None

    lat: float

    lng: float

    image_url: Optional[str] = None

@app.get("/api/map-locations", response_model=List[MapLocation], summary="Lấy danh sách điểm bản đồ")

async def get_map_locations():

    """Lấy tất cả các điểm đánh dấu trên bản đồ (Công khai)."""

    resp = supabase.table("map_locations").select("*").order("created_at", desc=True).execute()

    rows = resp.data or []

    for row in rows:

        row["description"] = sanitize_html(row.get("description")) if row.get("description") is not None else None

    return rows

@app.post("/api/admin/map-locations", response_model=MapLocation, summary="[Admin] Tạo điểm bản đồ mới")

async def admin_create_map_location(

    body: AdminMapLocationIn,

    authorization: Optional[str] = Header(None)

):

    """Tạo điểm đánh dấu mới trên bản đồ Chỉdành cho Admin."""

    await verify_admin(authorization)

    payload = body.dict()

    payload["description"] = sanitize_html(payload.get("description")) if payload.get("description") is not None else None

    resp = supabase.table("map_locations").insert(payload).execute()

    if not resp.data:

        raise HTTPException(status_code=500, detail="Không thể tạo điểm bản đồ")

    return resp.data[0]

@app.put("/api/admin/map-locations/{location_id}", response_model=MapLocation, summary="[Admin] Cập nhật điểm bản đồ")

async def admin_update_map_location(

    location_id: str,

    body: AdminMapLocationIn,

    authorization: Optional[str] = Header(None)

):

    """Cập nhật thông tin điểm đánh dấu. Chỉdành cho Admin."""

    await verify_admin(authorization)

    payload = body.dict()

    payload["description"] = sanitize_html(payload.get("description")) if payload.get("description") is not None else None

    resp = supabase.table("map_locations").update(payload).eq("id", location_id).execute()

    if not resp.data:

        raise HTTPException(status_code=404, detail="Không tìm thấy điểm bản đồđểcập nhật")

    return resp.data[0]

@app.delete("/api/admin/map-locations/{location_id}", summary="[Admin] Xóa điểm bản đồ")

async def admin_delete_map_location(

    location_id: str,

    authorization: Optional[str] = Header(None)

):

    """Xoá điểm đánh dấu khỏi bản đồ Chỉdành cho Admin."""

    await verify_admin(authorization)

    

    supabase.table("map_locations").delete().eq("id", location_id).execute()

    return {"message": "Đã xoá điểm bản đồthành công"}

def build_default_homepage_settings() -> dict:
    return {
        "warning_title": "CẢNH BÁO KHU VỰC CẤM",
        "warning_subtitle": "BIOSAFETY LEVEL 4 • RESTRICTED ACCESS",
        "warning_headline": "TRẬN ĐỊA SINH TỬ",
        "warning_description": "Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...",
        "features_title": "ĐIỂM NỔI BẬT",
        "features_json": [],
    }

@app.get("/api/homepage", response_model=HomepageSettings)
async def get_homepage_settings_i18n(locale: str = Query(DEFAULT_LOCALE, description="Requested locale")):
    """Lấy cấu hình nội dung hiển thị trên trang chủ theo locale."""
    base_payload = build_default_homepage_settings()
    try:
        resp = supabase.table("homepage_settings").select("*").eq("id", 1).single().execute()
        if resp.data:
            base_payload = prepare_homepage_settings_payload(resp.data)
        else:
            base_payload = prepare_homepage_settings_payload(base_payload)
    except Exception:
        base_payload = prepare_homepage_settings_payload(base_payload)

    translated_payload = apply_homepage_translation(base_payload, locale)
    return HomepageSettings(**translated_payload)

@app.put("/api/admin/homepage", summary="[Admin] Cập nhật cấu hình trang chủ")
async def admin_update_homepage_i18n(
    body: HomepageSettings,
    authorization: Optional[str] = Header(None),
    locale: str = Query(DEFAULT_LOCALE, description="Locale to update"),
):
    """Cập nhật nội dung CMS của trang chủ theo locale."""
    await verify_admin(authorization)

    target_locale = normalize_locale(locale)
    payload = prepare_homepage_settings_payload(body.model_dump(exclude_none=True))
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()

    if target_locale == DEFAULT_LOCALE:
        payload["id"] = 1
        result = supabase.table("homepage_settings").upsert(payload).execute()
        return {"message": "Cập nhật trang chủ thành công", "settings": result.data[0] if result.data else payload}

    payload.update(
        {
            "homepage_settings_id": 1,
            "locale": target_locale,
            "translation_status": "published",
            "translation_source": "human",
            "translated_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": build_content_hash(json.dumps(payload, ensure_ascii=False, sort_keys=True)),
        }
    )
    result = (
        supabase.table("homepage_settings_translations")
        .upsert(payload, on_conflict="homepage_settings_id,locale")
        .execute()
    )
    return {"message": "Cập nhật bản dịch trang chủ thành công", "settings": result.data[0] if result.data else payload}

@app.post("/api/admin/homepage/translate", summary="[Admin] Dịch AI cấu hình trang chủ")
async def admin_translate_homepage_i18n(
    authorization: Optional[str] = Header(None),
    locale: Optional[str] = Query(None, description="Specific locale to translate"),
):
    """Dịch AI cho các field CMS của trang chủ từ tiếng Việt sang các locale còn lại."""
    await verify_admin(authorization)

    try:
        resp = supabase.table("homepage_settings").select("*").eq("id", 1).single().execute()
        base_payload = prepare_homepage_settings_payload(resp.data if resp.data else build_default_homepage_settings())
    except Exception:
        base_payload = prepare_homepage_settings_payload(build_default_homepage_settings())

    if locale:
        target_locales = [normalize_locale(locale)]
    else:
        target_locales = [item for item in SUPPORTED_LOCALES if item != DEFAULT_LOCALE]

    target_locales = build_target_translation_locales(target_locales)
    try:
        translation_result = await upsert_homepage_translations(base_payload, target_locales)
        translated_locales = translation_result["translated_locales"]
        failed_translations = translation_result["failed_translations"]
    except HTTPException as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(target_locales),
                "status_code": exc.status_code,
                "detail": str(exc.detail),
            }
        ]
    except Exception as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(target_locales),
                "status_code": 500,
                "detail": str(exc),
            }
        ]

    return {
        "message": "Đã dịch cấu hình trang chủ",
        "translated_locales": translated_locales,
    }

@app.put("/api/admin/homepage/auto-save", response_model=HomepageAutoSaveResponse, summary="[Admin] Lưu trang chủ và tự động dịch AI")
async def admin_auto_save_homepage_i18n(
    body: HomepageSettings,
    authorization: Optional[str] = Header(None),
    locale: str = Query(DEFAULT_LOCALE, description="Locale to update"),
):
    """Lưu CMS trang chủ. Nếu locale là vi thì tự động dịch sang en, zh-CN và ja."""
    await verify_admin(authorization)

    target_locale = normalize_locale(locale)
    payload = prepare_homepage_settings_payload(body.model_dump(exclude_none=True))
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()

    if target_locale == DEFAULT_LOCALE:
        payload["id"] = 1
        result = supabase.table("homepage_settings").upsert(payload).execute()
        try:
            translation_result = await upsert_homepage_translations(payload, list(TRANSLATION_TARGET_LOCALES))
            translated_locales = translation_result["translated_locales"]
            failed_translations = translation_result["failed_translations"]
        except HTTPException as exc:
            translated_locales = []
            failed_translations = [
                {
                    "locale": ",".join(TRANSLATION_TARGET_LOCALES),
                    "status_code": exc.status_code,
                    "detail": str(exc.detail),
                }
            ]
        except Exception as exc:
            translated_locales = []
            failed_translations = [
                {
                    "locale": ",".join(TRANSLATION_TARGET_LOCALES),
                    "status_code": 500,
                    "detail": str(exc),
                }
            ]

        message = "Đã lưu trang chủ và tự động dịch"
        if failed_translations and translated_locales:
            message = "Đã lưu trang chủ và dịch một phần"
        elif failed_translations and not translated_locales:
            message = "Đã lưu trang chủ, nhưng auto-dịch tạm thời thất bại"

        return {
            "message": message,
            "settings": result.data[0] if result.data else payload,
            "auto_translated_locales": translated_locales,
            "failed_translations": failed_translations,
        }

    payload.update(
        {
            "homepage_settings_id": 1,
            "locale": target_locale,
            "translation_status": "published",
            "translation_source": "human",
            "translated_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": build_content_hash(json.dumps(payload, ensure_ascii=False, sort_keys=True)),
        }
    )
    result = (
        supabase.table("homepage_settings_translations")
        .upsert(payload, on_conflict="homepage_settings_id,locale")
        .execute()
    )
    return {
        "message": "Đã lưu bản dịch trang chủ",
        "settings": result.data[0] if result.data else payload,
        "auto_translated_locales": [],
        "failed_translations": [],
    }

@app.get("/api/_legacy/homepage", response_model=HomepageSettings)
async def get_homepage_settings():
    """Lấy cấu hình nội dung hiển thị trên trang chủ."""

    try:

        resp = supabase.table("homepage_settings").select("*").eq("id", 1).single().execute()

        if not resp.data:

            return HomepageSettings(

                warning_title="CẢNH BÁO KHU VỰC CẤM",

                warning_subtitle="BIOSAFETY LEVEL 4 · RESTRICTED ACCESS",

                warning_headline="TRẬN ĐỊA SINH TỬ",

                warning_description="Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...",

                features_title="ĐIỂM NỔI BẬT",

                features_json=[]

            )

        cleaned = dict(resp.data)

        cleaned["warning_description"] = sanitize_html(cleaned.get("warning_description")) or ""

        return HomepageSettings(**cleaned)

    except Exception:

        # Fallback if table doesn't exist yet

        return HomepageSettings(

            warning_title="CẢNH BÁO KHU VỰC CẤM",

            warning_subtitle="BIOSAFETY LEVEL 4 · RESTRICTED ACCESS",

            warning_headline="TRẬN ĐỊA SINH TỬ",

            warning_description="Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...",

            features_title="ĐIỂM NỔI BẬT",

            features_json=[]

        )

@app.put("/api/_legacy/admin/homepage", summary="[Legacy] Cập nhật cấu hình trang chủ")
async def admin_update_homepage(
    body: HomepageSettings,

    authorization: Optional[str] = Header(None),

):

    """Cập nhật các đoạn text và cấu hình trên trang chủ."""

    await verify_admin(authorization)

    

    data = body.model_dump(exclude_none=True)

    data["warning_description"] = sanitize_html(data.get("warning_description")) or ""

    data["id"] = 1

    data["updated_at"] = "now()"

    

    result = supabase.table("homepage_settings").upsert(data).execute()

    return {"message": "Cập nhật trang chủ thành công", "settings": result.data[0] if result.data else data}

@app.get("/api/admin/chapters/{chapter_number}/content", summary="[Admin] Lấy nội dung chương từ R2")

async def admin_get_chapter_content(

    chapter_number: int,

    authorization: Optional[str] = Header(None),

):

    """Lấy nội dung text thô của chương từ R2 (Proxy qua Backend để tránh CORS)."""

    await verify_admin(authorization)

    # Fetch metadata to get content_url

    resp = (

        supabase.table("chapters")

        .select("content_url")

        .eq("chapter_number", chapter_number)

        .single()

        .execute()

    )

    if not resp.data or not resp.data.get("content_url"):

        raise HTTPException(status_code=404, detail="Không tìm thấy nội dung chương")

    if not r2_client:

        missing = []

        if not R2_ACCESS_KEY: missing.append("R2_ACCESS_KEY_ID")

        if not R2_SECRET_KEY: missing.append("R2_SECRET_ACCESS_KEY")

        if not R2_ENDPOINT: missing.append("R2_ENDPOINT_URL")

        detail = f"R2 chưa được cấu hình. Thiếu biến: {', '.join(missing)}"

        raise HTTPException(status_code=500, detail=detail)

    # Extract object key from URL (more robustly)

    content_url = resp.data["content_url"]

    # Handle possible http/https mismatch or trailing slashes

    import re

    clean_url = re.sub(r'^https?://', '', content_url)

    clean_base = re.sub(r'^https?://', '', R2_PUBLIC_URL)

    object_key = clean_url.replace(clean_base, "").lstrip("/")

    try:

        r2_resp = r2_client.get_object(Bucket=R2_BUCKET, Key=object_key)

        content = r2_resp["Body"].read().decode("utf-8")

        return PlainTextResponse(content)

    except Exception as e:

        raise HTTPException(status_code=502, detail=f"Lỗi khi đọc từ R2: {str(e)}")

# === DELETE chapter route was at the end ===

@app.delete("/api/admin/chapters/{chapter_number}", summary="[Admin] Xóa chương")

async def admin_delete_chapter(

    chapter_number: int,

    authorization: Optional[str] = Header(None),

):

    """Xóa chương: Xóa file trên R2 và xoá metadata trong Supabase."""

    await verify_admin(authorization)

    # Fetch existing chapter

    existing = supabase.table("chapters").select("*").eq("chapter_number", chapter_number).single().execute()

    if not existing.data:

        raise HTTPException(status_code=404, detail=f"Chương {chapter_number} không tìm thấy")

    chapter = existing.data

    # Delete from R2

    if r2_client and chapter.get("content_url"):

        object_key = chapter["content_url"].replace(f"{R2_PUBLIC_URL}/", "")

        try:

            r2_client.delete_object(Bucket=R2_BUCKET, Key=object_key)

        except Exception:

            pass  # Continue even if R2 delete fails

    # Delete from Supabase

    supabase.table("chapters").delete().eq("chapter_number", chapter_number).execute()

    return {"message": f"Đã xóa chương {chapter_number}"}

# === ANALYTICS ROUTES ===

@app.get("/api/admin/analytics/top-chapters", summary="[Admin] Top chương đọc nhiều nhất")

async def admin_get_top_chapters(

    limit: int = Query(10, ge=1, le=50),

    authorization: Optional[str] = Header(None),

):

    """Lấy danh sách các chương có lượt đọc cao nhất."""

    await verify_admin(authorization)

    

    try:

        resp = (

            supabase.table("chapters")

            .select("chapter_number, title, view_count")

            .order("view_count", desc=True)

            .limit(limit)

            .execute()

        )

        return resp.data

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/top-liked", summary="[Admin] Top chương được yêu thích nhất")

async def admin_get_top_liked(

    limit: int = Query(10, ge=1, le=50),

    authorization: Optional[str] = Header(None),

):

    """Lấy danh sách các chương có lượt thả tim cao nhất."""

    await verify_admin(authorization)

    try:

        resp = (

            supabase.table("chapters")

            .select("chapter_number, title, likes_count")

            .order("likes_count", desc=True)

            .limit(limit)

            .execute()

        )

        return resp.data

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

# === COMMENT ROUTES ===

class Comment(BaseModel):

    id: str

    chapter_number: int

    user_name: str

    content: str

    created_at: str

class AdminCommentUpdate(BaseModel):

    content: str

@app.get("/api/admin/comments", summary="[Admin] Lấy danh sách tất cả bình luận")

async def admin_get_comments(

    page: int = Query(1, ge=1),

    limit: int = Query(50, ge=1, le=100),

    authorization: Optional[str] = Header(None)

):

    """Lấy danh sách bình luận trên toàn hệ thống, có phận trang."""

    await verify_admin(authorization)

    try:

        offset = (page - 1) * limit

        resp = (

            supabase.table("comments")

            .select("*", count="exact")

            .order("created_at", desc=True)

            .range(offset, offset + limit - 1)

            .execute()

        )

        total = resp.count or 0

        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        comments = resp.data or []

        for comment in comments:

            comment["user_name"] = sanitize_plaintext(comment.get("user_name")) or "ẩn danh"

            comment["content"] = sanitize_plaintext(comment.get("content")) or ""

        return {

            "comments": comments,

            "total": total,

            "page": page,

            "limit": limit,

            "total_pages": total_pages

        }

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/comments/{comment_id}", summary="[Admin] Sửa bình luận")

async def admin_update_comment(

    comment_id: str,

    body: AdminCommentUpdate,

    authorization: Optional[str] = Header(None)

):

    """Sửa nội dung bình luận của độc giả."""

    await verify_admin(authorization)

    try:

        resp = supabase.table("comments").update({"content": sanitize_plaintext(body.content) or ""}).eq("id", comment_id).execute()

        if not resp.data:

            raise HTTPException(status_code=404, detail="Không tìm thấy bình luận")

        return resp.data[0]

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/comments/{comment_id}", summary="[Admin] Xóa bình luận")

async def admin_delete_comment(

    comment_id: str,

    authorization: Optional[str] = Header(None)

):

    """Xóa một bình luận khỏi hệ thống."""

    await verify_admin(authorization)

    try:

        supabase.table("comments").delete().eq("id", comment_id).execute()

        return {"status": "success", "message": "Đã xóa bình luận"}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

# ============================================================

# IMAGE UPLOAD (CLOUDFLARE R2)

# ============================================================

@app.post("/api/upload/image", summary="Upload ảnh lên Cloudflare R2 (Admin)")

async def upload_image(

    file: UploadFile = File(...),

    authorization: Optional[str] = Header(None)

):

    """Upload ảnh phục vụ cho Editor/Wiki. Yêu cầu quyền Admin."""

    await verify_admin(authorization)

    

    if not r2_client:

        raise HTTPException(status_code=500, detail="Cấu hình Cloudflare R2 chưa hoàn chỉnh")

        

    try:

        import uuid

        from datetime import datetime

        

        # Validate file type

        valid_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]

        if file.content_type not in valid_types:

            raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file ảnh (JPG, PNG, GIF, WEBP)")

            

        # Generate unique filename

        ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'

        date_str = datetime.now().strftime("%Y%m%d")

        unique_id = str(uuid.uuid4())[:8]

        filename = f"uploads/{date_str}_{unique_id}.{ext}"

        

        # Read file

        contents = await file.read()

        

        # Upload to R2 (Wrapped in threadpool to avoid blocking event loop)

        from fastapi.concurrency import run_in_threadpool

        

        await run_in_threadpool(

            r2_client.put_object,

            Bucket=R2_BUCKET,

            Key=filename,

            Body=contents,

            ContentType=file.content_type

        )

        

        # Return URL

        # Đảm bảo R2_PUBLIC_URL không kết thúc bằng /

        base_url = R2_PUBLIC_URL.rstrip('/')

        public_url = f"{base_url}/{filename}"

        return {"url": public_url}

        

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

# ============================================================

# FACTION HIERARCHY (Cây Tổ Chức Thế Lực)

# ============================================================

class FactionMemberIn(BaseModel):

    character_id: Optional[str] = None

    parent_id: Optional[str] = None

    role_title: str = ""

    division: Optional[str] = None

    rank_level: int = 0

    sort_order: int = 0

class FactionMemberOut(BaseModel):

    id: str

    faction_id: str

    character_id: Optional[str] = None

    parent_id: Optional[str] = None

    role_title: str

    division: Optional[str] = None

    rank_level: int

    sort_order: int

    created_at: str

    # Joined character info

    character_name: Optional[str] = None

    character_slug: Optional[str] = None

    character_image: Optional[str] = None

@app.get("/api/wiki/{slug}/hierarchy", summary="Lấy cây tổ chức của thế lực (public)")

async def get_faction_hierarchy(slug: str):

    """Lấy toàn bộ cây phân cấp của 1 thế lực theo slug."""

    try:

        # 1. Get the faction wiki entry

        faction_resp = (

            supabase.table("wiki_entries")

            .select("id, title, category")

            .eq("slug", slug)

            .single()

            .execute()

        )

        if not faction_resp.data:

            raise HTTPException(status_code=404, detail="Không tìm thấy thế lực")

        if faction_resp.data.get("category") != "Thế lực":

            raise HTTPException(status_code=400, detail="Entry này không phải Thế lực")

        faction_id = faction_resp.data["id"]

        # 2. Get all members of this faction

        members_resp = (

            supabase.table("faction_members")

            .select("*")

            .eq("faction_id", faction_id)

            .order("rank_level")

            .order("sort_order")

            .execute()

        )

        members = members_resp.data or []

        # 3. Collect unique character IDs to batch-fetch their info

        char_ids = list(set(m["character_id"] for m in members if m.get("character_id")))

        char_map = {}

        if char_ids:

            chars_resp = (

                supabase.table("wiki_entries")

                .select("id, title, slug, image_url")

                .in_("id", char_ids)

                .execute()

            )

            for c in (chars_resp.data or []):

                char_map[c["id"]] = c

        # 4. Enrich members with character info

        result = []

        for m in members:

            char = char_map.get(m.get("character_id"), {})

            result.append({

                **m,

                "character_name": char.get("title"),

                "character_slug": char.get("slug"),

                "character_image": char.get("image_url"),

            })

        return {

            "faction_id": faction_id,

            "faction_title": faction_resp.data["title"],

            "members": result,

        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/wiki/{faction_id}/members", summary="[Admin] Thêm thành viên vào cây thế lực")

async def admin_add_faction_member(

    faction_id: str,

    body: FactionMemberIn,

    authorization: Optional[str] = Header(None),

):

    """Thêm một node mới vào cây tổ chức. Yêu cầu quyền Admin."""

    await verify_admin(authorization)

    try:

        data = body.model_dump(exclude_none=True)

        data["faction_id"] = faction_id

        result = supabase.table("faction_members").insert(data).execute()

        if not result.data:

            raise HTTPException(status_code=500, detail="Không thể thêm thành viên")

        return result.data[0]

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/wiki/members/{member_id}", summary="[Admin] Sửa thành viên trong cây thế lực")

async def admin_update_faction_member(

    member_id: str,

    body: FactionMemberIn,

    authorization: Optional[str] = Header(None),

):

    """Cập nhật thông tin node trong cây tổ chức."""

    await verify_admin(authorization)

    try:

        data = body.model_dump(exclude_none=True)

        result = supabase.table("faction_members").update(data).eq("id", member_id).execute()

        if not result.data:

            raise HTTPException(status_code=404, detail="Không tìm thấy thành viên")

        return result.data[0]

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/wiki/members/{member_id}", summary="[Admin] Xóa thành viên khỏi cây thế lực")

async def admin_delete_faction_member(

    member_id: str,

    authorization: Optional[str] = Header(None),

):

    """Xóa node khỏi cây. Children sẽ được detach (parent_id = null)."""

    await verify_admin(authorization)

    try:

        # Detach children first (set their parent to null)

        supabase.table("faction_members").update({"parent_id": None}).eq("parent_id", member_id).execute()

        # Delete the member

        supabase.table("faction_members").delete().eq("id", member_id).execute()

        return {"status": "deleted", "id": member_id}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

# ============================================================

# WIKI - BÁCH KHOA TOÀN THƯ

# ============================================================

VALID_WIKI_CATEGORIES = ["Nhân vật", "Sinh vật", "Thế lực", "Vật phẩm", "Địa điểm"]

class WikiEntryOut(BaseModel):

    id: str

    title: str

    category: str

    slug: str

    summary: Optional[str] = None

    content: Optional[str] = None

    image_url: Optional[str] = None

    tags: Optional[list[str]] = None

    sort_order: int = 0

    is_main_character: bool = False

    created_at: str

    updated_at: str

class WikiEntryIn(BaseModel):
    title: str
    category: str
    slug: str
    summary: Optional[str] = None

    content: Optional[str] = None

    image_url: Optional[str] = None

    tags: Optional[list[str]] = None

    sort_order: Optional[int] = None
    is_main_character: Optional[bool] = None

class AdminWikiBatchTranslateRequest(BaseModel):
    category: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    limit: int = 50
    only_missing: bool = True

@app.get("/api/wiki", summary="Lấy danh sách Wiki")

async def get_wiki_entries(

    category: Optional[str] = Query(None, description="Lọc theo category"),

    search: Optional[str] = Query(None, description="Tìm kiếm theo tiêu đề"),

    page: int = Query(1, ge=1, description="Số trang"),

    limit: int = Query(50, ge=1, le=200, description="Số lượng mỗi trang"),

    locale: str = Query(DEFAULT_LOCALE, description="Requested locale"),

):

    """Lấy danh sách tất cả wiki entries, có thể lọc theo category hoặc tìm kiếm."""

    try:

        offset = (page - 1) * limit

        query = supabase.table("wiki_entries").select("*", count="exact")

        if category:

            query = query.eq("category", category)

        if search:

            query = query.ilike("title", f"%{search}%")

        

        resp = (

            query.order("is_main_character", desc=True)

            .order("sort_order", desc=False, nullsfirst=False)

            .order("category")

            .order("title")

            .range(offset, offset + limit - 1)

            .execute()

        )

        

        total = resp.count or 0

        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        

        entries = resp.data or []

        for entry in entries:

            entry["summary"] = sanitize_html(entry.get("summary")) if entry.get("summary") is not None else None

            entry["content"] = sanitize_html(entry.get("content")) if entry.get("content") is not None else None

            apply_wiki_translation(entry, normalize_locale(locale))

        return {

            "entries": entries,

            "total": total,

            "page": page,

            "limit": limit,

            "total_pages": total_pages

        }

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wiki/{slug}", summary="Lấy chi tiết Wiki entry")

async def get_wiki_entry(slug: str, locale: str = Query(DEFAULT_LOCALE, description="Requested locale")):
    """Lấy một wiki entry theo slug."""

    try:

        resp = (

            supabase.table("wiki_entries")

            .select("*")

            .eq("slug", slug)

            .single()

            .execute()

        )

        if not resp.data:

            raise HTTPException(status_code=404, detail="Không tìm thấy entry")

        data = dict(resp.data)
        data["summary"] = sanitize_html(data.get("summary")) if data.get("summary") is not None else None
        data["content"] = sanitize_html(data.get("content")) if data.get("content") is not None else None
        apply_wiki_translation(data, normalize_locale(locale))
        return data
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wiki", summary="T?o Wiki entry m?i (Admin)")

async def create_wiki_entry(

    body: WikiEntryIn,

    authorization: Optional[str] = Header(None),

):

    """Tạo wiki entry mới. Yêu cầu quyền Admin."""

    await verify_admin(authorization)

    try:

        if body.category not in VALID_WIKI_CATEGORIES:

            raise HTTPException(status_code=400, detail=f"Category không hợp lệ. Chọn trong: {VALID_WIKI_CATEGORIES}")

        data = body.model_dump(exclude_none=True)

        data["summary"] = sanitize_html(data.get("summary")) if data.get("summary") is not None else None

        data["content"] = sanitize_html(data.get("content")) if data.get("content") is not None else None

        result = supabase.table("wiki_entries").insert(data).execute()

        return result.data[0]

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/wiki/{entry_id}", summary="Sửa Wiki entry (Admin)")

async def update_wiki_entry(

    entry_id: str,

    body: WikiEntryIn,

    authorization: Optional[str] = Header(None),

):

    """Cập nhật wiki entry theo id. Yêu cầu quyền Admin."""

    await verify_admin(authorization)

    try:

        from datetime import datetime, timezone

        data = body.model_dump(exclude_none=True)

        data["summary"] = sanitize_html(data.get("summary")) if data.get("summary") is not None else None

        data["content"] = sanitize_html(data.get("content")) if data.get("content") is not None else None

        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = supabase.table("wiki_entries").update(data).eq("id", entry_id).execute()

        if not result.data:

            raise HTTPException(status_code=404, detail="Entry không tồn tại")

        return result.data[0]

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/wiki/{entry_id}", summary="X?a Wiki entry (Admin)")

async def delete_wiki_entry(

    entry_id: str,

    authorization: Optional[str] = Header(None),

):

    """Xóa wiki entry theo id. Yêu cầu quyền Admin."""

    await verify_admin(authorization)

    try:

        supabase.table("wiki_entries").delete().eq("id", entry_id).execute()

        return {"status": "deleted", "id": entry_id}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

# ============================================================

#   GUIDE PAGES (Hướng dẫn sử dụng & SOP nội bộ)

# ============================================================

class GuidePageUpdate(BaseModel):

    title: Optional[str] = None

    content: Optional[str] = None

@app.get("/api/guide/{slug}", summary="Lấy trang hướng dẫn public")

async def _public_guide_route(slug: str, locale: str = Query(DEFAULT_LOCALE, description="Requested locale")):
    return await get_public_guide(slug, locale)

def build_guide_translation_slug(slug: str, locale: str) -> str:
    return f"{slug}__{normalize_locale(locale)}"

def resolve_guide_translation(slug: str, locale: str, scope: Optional[str] = None):
    target_locale = normalize_locale(locale)
    if target_locale == DEFAULT_LOCALE:
        return None

    query = supabase.table("guide_pages").select("*").eq("slug", build_guide_translation_slug(slug, target_locale))
    if scope:
        query = query.eq("scope", scope)
    result = query.limit(1).execute()
    if result.data:
        return result.data[0]
    return None

def apply_guide_translation(payload: dict, slug: str, locale: str, scope: Optional[str] = None) -> dict:
    requested_locale = normalize_locale(locale)
    resolved_locale = DEFAULT_LOCALE
    is_fallback = False

    translation = resolve_guide_translation(slug, requested_locale, scope)
    if translation:
        if translation.get("title") is not None:
            payload["title"] = translation.get("title")
        if translation.get("content") is not None:
            payload["content"] = translation.get("content")
        resolved_locale = requested_locale
    elif requested_locale != DEFAULT_LOCALE:
        is_fallback = True

    payload["slug"] = slug
    payload["requested_locale"] = requested_locale
    payload["resolved_locale"] = resolved_locale
    payload["is_fallback"] = is_fallback
    return payload

async def translate_guide_payloads_with_ai(guide_payload: dict, locales: list[str], context_label: str) -> dict[str, dict]:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {}

    glossary_prompt = build_glossary_prompt()
    locale_prompt = build_target_locale_prompt(target_locales)
    source_payload = {
        "title": guide_payload.get("title") or "",
        "content": guide_payload.get("content") or "",
    }
    schema = build_multilocale_object_schema(
        target_locales,
        {
            "title": {"type": "string"},
            "content": {"type": "string"},
        },
    )
    system_instruction = build_guide_multilocale_system_instruction()
    translated_payloads = await generate_structured_translation_payload(
        system_instruction=system_instruction,
        user_prompt=build_guide_multilocale_user_prompt(
            source_payload=source_payload,
            locale_prompt=locale_prompt,
            glossary_prompt=glossary_prompt,
            context_label=context_label,
            source_locale=DEFAULT_LOCALE,
        ),
        response_json_schema=schema,
        parser=lambda raw_text: parse_multilocale_translation_payload(raw_text, target_locales, ["title", "content"]),
    )

    sanitized_payloads: dict[str, dict] = {}
    for locale in target_locales:
        locale_payload = translated_payloads.get(locale) or {}
        translated_title = sanitize_plaintext(str(locale_payload.get("title") or "").strip())
        translated_content = sanitize_html(locale_payload.get("content")) if locale_payload.get("content") is not None else ""
        if not translated_title:
            raise ValueError(f"Missing guide title for locale {locale}")
        sanitized_payloads[locale] = {
            "title": translated_title,
            "content": translated_content,
        }
    return sanitized_payloads

async def upsert_guide_translations(slug: str, scope: str, guide_payload: dict, locales: list[str]) -> dict:
    target_locales = build_target_translation_locales(locales)
    if not target_locales:
        return {"translated_locales": [], "failed_translations": []}

    translated_payloads = await translate_guide_payloads_with_ai(guide_payload, target_locales, f"guide-{slug}")
    updated_at = datetime.now(timezone.utc).isoformat()
    translated_locales = []
    failed_translations = []
    for locale in target_locales:
        translated_payload = translated_payloads.get(locale)
        if not translated_payload:
            failed_translations.append({"locale": locale, "status_code": 502, "detail": "Missing guide translation payload"})
            continue

        supabase.table("guide_pages").upsert(
            {
                "slug": build_guide_translation_slug(slug, locale),
                "scope": scope,
                "title": translated_payload["title"],
                "content": translated_payload.get("content", ""),
                "updated_at": updated_at,
            },
            on_conflict="slug",
        ).execute()
        translated_locales.append(locale)

    return {
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

async def get_public_guide(slug: str, locale: str = Query(DEFAULT_LOCALE, description="Requested locale")):
    """Lấy nội dung trang hướng dẫn có scope = 'public'."""

    try:
        result = supabase.table("guide_pages").select("*").eq("slug", slug).eq("scope", "public").execute()
        if not result.data:
            return apply_guide_translation({"slug": slug, "title": "", "content": "", "scope": "public"}, slug, locale, "public")
        data = dict(result.data[0])
        data["slug"] = slug
        data["content"] = sanitize_html(data.get("content")) or ""
        return apply_guide_translation(data, slug, locale, "public")
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/guide/{slug}", summary="Lấy trang hướng dẫn (Admin)")

async def get_admin_guide(

    slug: str,

    authorization: Optional[str] = Header(None),

):

    """Lấy nội dung bất kỳ trang nào (kể cả internal). Yêu cầu Admin."""

    await verify_admin(authorization)

    try:

        result = supabase.table("guide_pages").select("*").eq("slug", slug).execute()

        if not result.data:

            return {"slug": slug, "title": "", "content": "", "scope": "internal"}

        data = dict(result.data[0])

        data["content"] = sanitize_html(data.get("content")) or ""

        return data

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/guide/{slug}", summary="Cập nhật trang hướng dẫn (Admin)")

async def update_guide(
    slug: str,

    body: GuidePageUpdate,

    authorization: Optional[str] = Header(None),

):

    """Cập nhật hoặc tạo mới trang hướng dẫn. Yêu cầu Admin."""

    await verify_admin(authorization)

    try:

        from datetime import datetime, timezone

        # Determine scope from slug

        scope = "internal" if slug == "admin-sop" else "public"

        existing = supabase.table("guide_pages").select("id").eq("slug", slug).execute()

        data = body.model_dump(exclude_none=True)

        if "content" in data:

            data["content"] = sanitize_html(data.get("content")) or ""

        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        if existing.data:

            result = supabase.table("guide_pages").update(data).eq("slug", slug).execute()

        else:

            data["slug"] = slug

            data["scope"] = scope

            if "title" not in data:

                data["title"] = "Hướng dẫn" if scope == "public" else "SOP Nội bộ"

            if "content" not in data:

                data["content"] = ""

            result = supabase.table("guide_pages").insert(data).execute()

        return result.data[0] if result.data else {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/guide/{slug}/translate", summary="[Admin] Translate guide page to EN/ZH-CN/JA")
async def admin_translate_guide(
    slug: str,
    authorization: Optional[str] = Header(None),
    locale: Optional[str] = Query(None, description="Specific locale to translate"),
):
    await verify_admin(authorization)

    scope = "internal" if slug == "admin-sop" else "public"
    result = supabase.table("guide_pages").select("*").eq("slug", slug).limit(1).execute()
    base_row = dict(result.data[0]) if result.data else {"slug": slug, "scope": scope, "title": "", "content": ""}
    base_payload = {
        "title": sanitize_plaintext(str(base_row.get("title") or "").strip()),
        "content": sanitize_html(base_row.get("content")) if base_row.get("content") is not None else "",
    }

    target_locales = [normalize_locale(locale)] if locale else list(TRANSLATION_TARGET_LOCALES)
    target_locales = build_target_translation_locales(target_locales)
    try:
        translation_result = await upsert_guide_translations(slug, scope, base_payload, target_locales)
        translated_locales = translation_result["translated_locales"]
        failed_translations = translation_result["failed_translations"]
    except HTTPException as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(target_locales),
                "status_code": exc.status_code,
                "detail": str(exc.detail),
            }
        ]
    except Exception as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(target_locales),
                "status_code": 500,
                "detail": str(exc),
            }
        ]

    return {
        "message": "Guide translated",
        "slug": slug,
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

@app.post("/api/admin/wiki/{entry_id}/translate", summary="[Admin] Translate wiki entry to EN/ZH-CN/JA")
async def admin_translate_wiki_entry(
    entry_id: str,
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    entry_resp = (
        supabase.table("wiki_entries")
        .select("*")
        .eq("id", entry_id)
        .limit(1)
        .execute()
    )
    if not entry_resp.data:
        raise HTTPException(status_code=404, detail="Wiki entry not found")

    entry_row = dict(entry_resp.data[0])
    entry_row["summary"] = sanitize_html(entry_row.get("summary")) if entry_row.get("summary") is not None else None
    entry_row["content"] = sanitize_html(entry_row.get("content")) if entry_row.get("content") is not None else None

    try:
        translation_result = await upsert_wiki_translations(entry_row, list(TRANSLATION_TARGET_LOCALES))
        translated_locales = translation_result["translated_locales"]
        failed_translations = translation_result["failed_translations"]
    except HTTPException as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(TRANSLATION_TARGET_LOCALES),
                "status_code": exc.status_code,
                "detail": str(exc.detail),
            }
        ]
    except Exception as exc:
        translated_locales = []
        failed_translations = [
            {
                "locale": ",".join(TRANSLATION_TARGET_LOCALES),
                "status_code": 500,
                "detail": str(exc),
            }
        ]

    return {
        "message": "Wiki translated",
        "entry_id": entry_id,
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }

@app.post("/api/admin/wiki/translate-batch", summary="[Admin] Batch translate wiki entries to EN/ZH-CN/JA")
async def admin_translate_wiki_batch(
    body: AdminWikiBatchTranslateRequest,
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    page = max(1, body.page)
    limit = min(max(1, body.limit), 100)
    offset = (page - 1) * limit

    query = supabase.table("wiki_entries").select("*", count="exact")
    if body.category:
        query = query.eq("category", body.category)
    if body.search:
        query = query.ilike("title", f"%{body.search}%")

    wiki_resp = (
        query.order("is_main_character", desc=True)
        .order("sort_order", desc=False, nullsfirst=False)
        .order("category")
        .order("title")
        .range(offset, offset + limit - 1)
        .execute()
    )
    entry_rows = wiki_resp.data or []
    if not entry_rows:
        raise HTTPException(status_code=404, detail="No wiki entries found in selected batch")

    translation_map: dict[str, set[str]] = {}
    if body.only_missing:
        translation_resp = (
            supabase.table("wiki_entry_translations")
            .select("wiki_entry_id, locale")
            .in_("wiki_entry_id", [row["id"] for row in entry_rows])
            .execute()
        )
        for row in (translation_resp.data or []):
            translation_map.setdefault(row["wiki_entry_id"], set()).add(row["locale"])

    translated_entries = []
    skipped_entries = []
    failed_entries = []

    for entry_row in entry_rows:
        needed_locales = list(TRANSLATION_TARGET_LOCALES)
        if body.only_missing:
            existing_locales = translation_map.get(entry_row["id"], set())
            needed_locales = [locale_code for locale_code in needed_locales if locale_code not in existing_locales]
            if not needed_locales:
                skipped_entries.append({"entry_id": entry_row["id"], "title": entry_row["title"]})
                continue

        sanitized_entry = dict(entry_row)
        sanitized_entry["summary"] = sanitize_html(sanitized_entry.get("summary")) if sanitized_entry.get("summary") is not None else None
        sanitized_entry["content"] = sanitize_html(sanitized_entry.get("content")) if sanitized_entry.get("content") is not None else None
        translation_result = await upsert_wiki_translations(sanitized_entry, needed_locales)
        completed_locales = translation_result["translated_locales"]
        entry_locale_errors = [
            f"{item['locale']}: {item.get('detail') or 'Translation failed'}"
            for item in (translation_result.get("failed_translations") or [])
        ]

        if completed_locales:
            translated_entries.append(
                {
                    "entry_id": entry_row["id"],
                    "title": entry_row["title"],
                    "translated_locales": completed_locales,
                }
            )
        if entry_locale_errors:
            failed_entries.append(
                {
                    "entry_id": entry_row["id"],
                    "title": entry_row["title"],
                    "detail": "\n".join(entry_locale_errors),
                }
            )

    return {
        "message": "Batch wiki translation completed",
        "page": page,
        "limit": limit,
        "only_missing": body.only_missing,
        "translated_count": len(translated_entries),
        "skipped_count": len(skipped_entries),
        "failed_count": len(failed_entries),
        "translated_entries": translated_entries,
        "skipped_entries": skipped_entries,
        "failed_entries": failed_entries,
        "total_entries": wiki_resp.count or len(entry_rows),
    }
