from __future__ import annotations

import html
import hashlib
import logging
import re
from difflib import SequenceMatcher
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional
from urllib.parse import quote

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/reader", tags=["reader_learning"])
logger = logging.getLogger(__name__)

LookupSource = Literal["cache", "rule_based", "ai", "placeholder"]


class ReaderExternalLink(BaseModel):
    label: str
    url: str


class ReaderLookupRequest(BaseModel):
    locale: str = "vi"
    term: str = Field(..., min_length=1, max_length=120)
    context_sentence: Optional[str] = Field(default=None, max_length=1200)
    chapter_id: Optional[int] = None


class ReaderLookupResponse(BaseModel):
    term: str
    normalized_term: str
    locale: str
    reading: Optional[str] = None
    meaning_vi: Optional[str] = None
    pos: Optional[str] = None
    notes: Optional[str] = None
    source: LookupSource
    external_links: list[ReaderExternalLink] = Field(default_factory=list)


class ReaderSaveVocabRequest(BaseModel):
    locale: str = "vi"
    term: str = Field(..., min_length=1, max_length=120)
    normalized_term: Optional[str] = Field(default=None, max_length=160)
    reading: Optional[str] = Field(default=None, max_length=160)
    meaning_vi: Optional[str] = None
    pos: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = None
    context_sentence: Optional[str] = None
    chapter_id: Optional[int] = None
    source: str = Field(default="lookup", max_length=40)


class ReaderSavedVocabItem(BaseModel):
    id: str
    user_id: str
    locale: str
    term: str
    normalized_term: str
    reading: Optional[str] = None
    meaning_vi: Optional[str] = None
    pos: Optional[str] = None
    notes: Optional[str] = None
    context_sentence: Optional[str] = None
    chapter_id: Optional[int] = None
    source: str
    created_at: str
    updated_at: str
    review_count: int = 0
    next_review_at: Optional[str] = None
    interval_days: Optional[int] = None
    ease: Optional[float] = None
    due_for_review: bool = False


class ReaderSavedVocabListResponse(BaseModel):
    items: list[ReaderSavedVocabItem]
    total: int
    page: int
    limit: int


class ReaderSaveSentenceRequest(BaseModel):
    locale: str = "vi"
    sentence_text: str = Field(..., min_length=1, max_length=4000)
    meaning_vi: Optional[str] = None
    note: Optional[str] = None
    chapter_id: Optional[int] = None


class ReaderSavedSentenceItem(BaseModel):
    id: str
    user_id: str
    locale: str
    sentence_text: str
    meaning_vi: Optional[str] = None
    note: Optional[str] = None
    chapter_id: Optional[int] = None
    created_at: str


class ReaderSavedSentenceListResponse(BaseModel):
    items: list[ReaderSavedSentenceItem]
    total: int
    page: int
    limit: int


class ReaderReviewRequest(BaseModel):
    saved_vocab_id: str
    grade: int = Field(..., ge=0, le=3)


class ReaderReviewResponse(BaseModel):
    saved_vocab_id: str
    ease: float
    interval_days: int
    next_review_at: Optional[str] = None
    review_count: int


class ReaderSentenceTtsRequest(BaseModel):
    locale: str = "vi"
    sentence_text: str = Field(..., min_length=1, max_length=200)
    speed: float = Field(default=1.0, ge=0.5, le=1.5)
    chapter_id: Optional[int] = None
    voice: Optional[str] = None


class ReaderSentenceTtsResponse(BaseModel):
    status: str
    detail: str
    audio_url: Optional[str] = None
    provider: Optional[str] = None
    cached: bool = False


class ReaderSentenceInsightRequest(BaseModel):
    locale: str = "vi"
    sentence_text: str = Field(..., min_length=1, max_length=1200)
    chapter_id: Optional[int] = None


class ReaderSentenceInsightResponse(BaseModel):
    sentence_text: str
    locale: str
    meaning_vi: Optional[str] = None
    notes: Optional[str] = None
    source: LookupSource


class ReaderSourceReferenceRequest(BaseModel):
    locale: str = "vi"
    selected_text: str = Field(..., min_length=1, max_length=1200)
    context_sentence: Optional[str] = Field(default=None, max_length=2000)
    context_block: Optional[str] = Field(default=None, max_length=4000)
    chapter_id: int = Field(..., ge=1)


class ReaderSourceReferenceResponse(BaseModel):
    locale: str
    source_locale: str = "vi"
    selected_text: str
    translated_excerpt: Optional[str] = None
    source_excerpt: str
    paragraph_index: Optional[int] = None
    match_mode: Literal["sentence", "paragraph"] = "paragraph"
    confidence: Literal["high", "medium", "low"] = "low"
    source: LookupSource


class ReaderLearningStatsResponse(BaseModel):
    saved_vocab_count: int
    saved_sentence_count: int
    review_due_count: int


def _get_supabase():
    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase
    return supabase


def _normalize_locale(locale: Optional[str]) -> str:
    try:
        from main import normalize_locale
    except ImportError:
        from backend.main import normalize_locale
    return normalize_locale(locale or "vi")


def _get_build_content_hash():
    try:
        from main import build_content_hash
    except ImportError:
        from backend.main import build_content_hash
    return build_content_hash


def _get_generate_structured_translation_payload():
    try:
        from main import generate_structured_translation_payload
    except ImportError:
        from backend.main import generate_structured_translation_payload
    return generate_structured_translation_payload


def _get_parse_json_like_payload():
    try:
        from main import parse_json_like_payload
    except ImportError:
        from backend.main import parse_json_like_payload
    return parse_json_like_payload


def _get_build_rule_based_lookup():
    try:
        from routes.reader_lookup_rules import build_rule_based_lookup
    except ImportError:
        from backend.routes.reader_lookup_rules import build_rule_based_lookup
    return build_rule_based_lookup


def _get_fetch_r2_content():
    try:
        from main import fetch_r2_content
    except ImportError:
        from backend.main import fetch_r2_content
    return fetch_r2_content


def _get_resolve_chapter_translation():
    try:
        from main import resolve_chapter_translation
    except ImportError:
        from backend.main import resolve_chapter_translation
    return resolve_chapter_translation


def _get_build_chapter_sentence_alignment():
    try:
        from main import build_chapter_sentence_alignment
    except ImportError:
        from backend.main import build_chapter_sentence_alignment
    return build_chapter_sentence_alignment


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


def _normalize_term(term: str) -> str:
    return " ".join((term or "").strip().split()).lower()


def _normalize_sentence(text: Optional[str], max_length: int = 1200) -> Optional[str]:
    normalized = " ".join((text or "").strip().split())
    if not normalized:
        return None
    return normalized[:max_length]


def _strip_html_to_text(text: Optional[str]) -> str:
    if not text:
        return ""
    normalized = re.sub(r"(?i)<br\s*/?>", "\n", text)
    normalized = re.sub(r"(?i)</p\s*>", "\n\n", normalized)
    normalized = re.sub(r"(?i)</div\s*>", "\n\n", normalized)
    normalized = re.sub(r"<[^>]+>", "", normalized)
    normalized = html.unescape(normalized)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.strip()


def _split_text_blocks(text: Optional[str]) -> list[str]:
    plain_text = _strip_html_to_text(text)
    if not plain_text:
        return []
    blocks = [block.strip() for block in re.split(r"\n\s*\n+", plain_text) if block.strip()]
    if blocks:
        return blocks
    return [line.strip() for line in plain_text.split("\n") if line.strip()]


def _normalize_match_text(text: Optional[str]) -> str:
    normalized = _strip_html_to_text(text).lower()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[^\w\s\u00C0-\u024F\u3040-\u30ff\u3400-\u9fff]", "", normalized)
    return normalized.strip()


def _overlap_score(query: str, candidate: str) -> float:
    if not query or not candidate:
        return 0.0
    if query in candidate:
        return 1.0 + (len(query) / max(len(candidate), 1))

    query_tokens = [token for token in query.split(" ") if token]
    if not query_tokens:
        return 0.0
    hits = sum(1 for token in query_tokens if token in candidate)
    if hits == 0:
        # Fallback for no-space languages (ja/zh) and long merged selections where
        # token containment is too strict. Keep bounded score so exact substring still wins.
        fuzzy = SequenceMatcher(None, query[:800], candidate[:2400]).ratio()
        return fuzzy * 0.8
    return hits / len(query_tokens)


def _find_best_matching_block(translated_blocks: list[str], selected_text: str, context_sentence: Optional[str]) -> tuple[Optional[int], float]:
    normalized_selected = _normalize_match_text(selected_text)
    normalized_context = _normalize_match_text(context_sentence)
    best_index: Optional[int] = None
    best_score = 0.0

    for index, block in enumerate(translated_blocks):
        normalized_block = _normalize_match_text(block)
        score = max(
            _overlap_score(normalized_selected, normalized_block),
            _overlap_score(normalized_context, normalized_block),
        )
        if score > best_score:
            best_score = score
            best_index = index

    return best_index, best_score


def _block_start_offsets(blocks: list[str]) -> tuple[list[int], int]:
    offsets: list[int] = []
    cursor = 0
    for block in blocks:
        normalized = _normalize_match_text(block)
        offsets.append(cursor)
        cursor += len(normalized) + 1
    return offsets, max(cursor, 1)


def _map_source_block_index_by_relative_position(
    translated_blocks: list[str],
    source_blocks: list[str],
    translated_index: int,
) -> int:
    if not translated_blocks or not source_blocks:
        return 0
    safe_translated_index = max(0, min(translated_index, len(translated_blocks) - 1))
    translated_offsets, translated_total = _block_start_offsets(translated_blocks)
    source_offsets, source_total = _block_start_offsets(source_blocks)

    translated_pos = translated_offsets[safe_translated_index]
    relative = translated_pos / max(translated_total - 1, 1)
    target_source_pos = int(relative * max(source_total - 1, 1))

    mapped_index = len(source_offsets) - 1
    for index, start in enumerate(source_offsets):
        if start >= target_source_pos:
            mapped_index = index
            break
    return max(0, min(mapped_index, len(source_blocks) - 1))


def _split_sentences(text: Optional[str]) -> list[str]:
    plain_text = _strip_html_to_text(text)
    if not plain_text:
        return []
    parts = re.split(r"(?<=[.!?。！？…])[\s\"'”’）】]*", plain_text)
    sentences = [part.strip() for part in parts if part and part.strip()]
    return sentences if sentences else [plain_text.strip()]


def _join_sentence_window(sentences: list[str], start_index: int, count: int) -> str:
    if not sentences:
        return ""
    safe_start = max(0, min(start_index, len(sentences) - 1))
    safe_count = max(1, count)
    safe_end = min(len(sentences), safe_start + safe_count)
    return " ".join(sentence.strip() for sentence in sentences[safe_start:safe_end] if sentence and sentence.strip()).strip()


def _cap_excerpt(text: Optional[str], max_sentences: int, max_chars: int) -> str:
    plain_text = _strip_html_to_text(text)
    if not plain_text:
        return ""
    sentences = _split_sentences(plain_text)
    excerpt = " ".join(sentences[: max(1, max_sentences)]).strip() if sentences else plain_text
    if len(excerpt) <= max_chars:
        return excerpt
    return excerpt[:max_chars].rstrip()


def _build_source_reference_confidence(
    match_mode: Literal["sentence", "paragraph"],
    block_score: float,
    sentence_score: float,
    translated_excerpt: str,
    source_excerpt: str,
) -> Literal["high", "medium", "low"]:
    translated_len = len((_normalize_match_text(translated_excerpt) or "").strip())
    source_len = len((_normalize_match_text(source_excerpt) or "").strip())
    if translated_len == 0 or source_len == 0:
        return "low"
    too_short_source = source_len > 0 and source_len < 12

    if match_mode == "sentence":
        if (
            not too_short_source
            and sentence_score >= 0.86
            and block_score >= 0.58
            and translated_len >= 18
            and source_len >= 16
        ):
            return "high"
        if sentence_score >= 0.55 or block_score >= 0.62:
            return "medium"
        return "low"

    # Paragraph mode has inherently higher uncertainty after alignment.
    # Keep it capped at medium to avoid overclaiming confidence.
    if block_score >= 0.68 and translated_len >= 32 and source_len >= 28:
        return "medium"
    return "low"


def _selected_sentence_window_size(selected_text: str) -> int:
    selected_sentences = _split_sentences(selected_text)
    if len(selected_sentences) >= 2:
        return min(len(selected_sentences), 4)

    normalized_selected = _normalize_match_text(selected_text)
    if len(normalized_selected) >= 200:
        return 3
    if len(normalized_selected) >= 120:
        return 2
    return 1


def _extract_sentence_alignment_entries(raw_alignment: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_alignment, dict):
        return []
    raw_entries = raw_alignment.get("entries")
    if not isinstance(raw_entries, list):
        return []

    entries: list[dict[str, Any]] = []
    for item in raw_entries:
        if not isinstance(item, dict):
            continue
        translated_excerpt = _normalize_sentence(str(item.get("translated_excerpt") or ""), max_length=800) or ""
        source_excerpt = _normalize_sentence(str(item.get("source_excerpt") or ""), max_length=800) or ""
        if not translated_excerpt or not source_excerpt:
            continue
        entries.append(
            {
                "translated_excerpt": translated_excerpt,
                "source_excerpt": source_excerpt,
                "chunk_index": int(item.get("chunk_index") or 0) if str(item.get("chunk_index") or "").isdigit() else None,
                "translated_index": int(item.get("translated_index") or 0) if str(item.get("translated_index") or "").isdigit() else None,
                "source_start": int(item.get("source_start") or 0) if str(item.get("source_start") or "").isdigit() else None,
                "source_end": int(item.get("source_end") or 0) if str(item.get("source_end") or "").isdigit() else None,
            }
        )
    return entries


def _get_translation_alignment_version() -> int:
    try:
        from main import TRANSLATION_ALIGNMENT_VERSION
    except ImportError:
        from backend.main import TRANSLATION_ALIGNMENT_VERSION
    return int(TRANSLATION_ALIGNMENT_VERSION)


def _alignment_content_hash(text: Optional[str]) -> str:
    build_content_hash = _get_build_content_hash()
    return build_content_hash(_strip_html_to_text(text) or "")


def _alignment_needs_regeneration(
    raw_alignment: Any,
    *,
    source_text: str,
    translated_text: str,
) -> bool:
    if not isinstance(raw_alignment, dict):
        return True

    if int(raw_alignment.get("version") or 0) < _get_translation_alignment_version():
        return True

    expected_source_hash = _alignment_content_hash(source_text)
    expected_translated_hash = _alignment_content_hash(translated_text)
    stored_source_hash = str(raw_alignment.get("source_content_hash") or "").strip()
    stored_translated_hash = str(raw_alignment.get("translated_content_hash") or "").strip()

    if stored_source_hash != expected_source_hash:
        return True
    if stored_translated_hash != expected_translated_hash:
        return True

    return False


def _merge_excerpt_segments(segments: list[str]) -> str:
    merged: list[str] = []
    for raw_segment in segments:
        segment = str(raw_segment or "").strip()
        if not segment:
            continue
        if not merged:
            merged.append(segment)
            continue

        previous = merged[-1]
        if segment == previous:
            continue

        overlap = 0
        max_overlap = min(len(previous), len(segment))
        for size in range(max_overlap, 0, -1):
            if previous.endswith(segment[:size]):
                overlap = size
                break

        if overlap >= max(12, len(segment) // 4):
            merged[-1] = previous + segment[overlap:]
        else:
            merged.append(segment)

    return " ".join(merged).strip()


def _join_alignment_window(entries: list[dict[str, Any]], start_index: int, count: int, field_name: str) -> str:
    if not entries:
        return ""
    safe_start = max(0, min(start_index, len(entries) - 1))
    safe_count = max(1, count)
    safe_end = min(len(entries), safe_start + safe_count)
    return _merge_excerpt_segments(
        [
            str(item.get(field_name) or "").strip()
            for item in entries[safe_start:safe_end]
            if str(item.get(field_name) or "").strip()
        ]
    )


def _context_excerpt_coverage_score(context_block: Optional[str], translated_excerpt: Optional[str]) -> float:
    normalized_context = _normalize_match_text(context_block)
    normalized_excerpt = _normalize_match_text(translated_excerpt)
    if not normalized_context or not normalized_excerpt:
        return 0.0
    return _overlap_score(normalized_context, normalized_excerpt)


def _selected_excerpt_coverage_score(selected_text: Optional[str], translated_excerpt: Optional[str]) -> float:
    normalized_selected = _normalize_match_text(selected_text)
    normalized_excerpt = _normalize_match_text(translated_excerpt)
    if not normalized_selected or not normalized_excerpt:
        return 0.0
    return _overlap_score(normalized_selected, normalized_excerpt)


def _find_alignment_sentence_candidate(
    entries: list[dict[str, Any]],
    selected_text: str,
    context_sentence: Optional[str],
    context_window: Optional[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    normalized_selected = _normalize_match_text(selected_text)
    normalized_context = _normalize_match_text(context_sentence)
    if not entries or not normalized_selected:
        return None

    window_start = int(context_window["start_index"]) if context_window else 0
    window_end = window_start + int(context_window["window_size"]) if context_window else 0
    candidates: list[dict[str, Any]] = []

    for index, item in enumerate(entries):
        translated_excerpt = str(item.get("translated_excerpt") or "")
        normalized_excerpt = _normalize_match_text(translated_excerpt)
        if not normalized_excerpt:
            continue
        selected_score = _overlap_score(normalized_selected, normalized_excerpt)
        context_score = _overlap_score(normalized_context, normalized_excerpt) if normalized_context else 0.0
        exact_match = normalized_selected in normalized_excerpt or normalized_excerpt in normalized_selected
        in_context_window = bool(context_window) and window_start <= index < window_end
        if exact_match or selected_score >= 0.5 or (in_context_window and context_score >= 0.5):
            candidates.append(
                {
                    "index": index,
                    "selected_score": selected_score,
                    "context_score": context_score,
                    "exact_match": exact_match,
                    "in_context_window": in_context_window,
                    "translated_excerpt": translated_excerpt,
                }
            )

    if not candidates:
        return None

    exact_candidates = [candidate for candidate in candidates if candidate["exact_match"]]
    if exact_candidates:
        candidates = exact_candidates

    candidates.sort(
        key=lambda candidate: (
            0 if candidate["exact_match"] else 1,
            0 if candidate["in_context_window"] else 1,
            -float(candidate["selected_score"]),
            -float(candidate["context_score"]),
            abs(len(_normalize_match_text(candidate["translated_excerpt"])) - len(normalized_selected)),
            int(candidate["index"]),
        )
    )
    return candidates[0]


def _resolve_alignment_context_window(
    entries: list[dict[str, Any]],
    context_block: Optional[str],
) -> Optional[dict[str, Any]]:
    normalized_context = _normalize_match_text(context_block)
    if not entries or not normalized_context:
        return None

    preferred_window = min(max(len(_split_sentences(context_block)), 1), 6)
    window_sizes = sorted(
        {
            max(1, preferred_window - 1),
            preferred_window,
            min(6, preferred_window + 1),
        }
    )
    best_match: Optional[dict[str, Any]] = None

    for window_size in window_sizes:
        if window_size <= 0 or window_size > len(entries):
            continue
        for start_index in range(0, len(entries) - window_size + 1):
            translated_window = _join_alignment_window(entries, start_index, window_size, "translated_excerpt")
            score = _overlap_score(normalized_context, _normalize_match_text(translated_window))
            if best_match is None or score > float(best_match["score"]):
                best_match = {
                    "start_index": start_index,
                    "window_size": window_size,
                    "score": score,
                }

    if not best_match or float(best_match["score"]) < 0.5:
        return None
    return best_match


def _resolve_source_reference_from_alignment(
    entries: list[dict[str, Any]],
    selected_text: str,
    context_sentence: Optional[str],
    context_block: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    if not entries:
        return None

    sentence_mode_requested = _should_match_sentence(selected_text, context_sentence)
    selected_window_size = _selected_sentence_window_size(selected_text)
    context_window = _resolve_alignment_context_window(entries, context_block)
    search_offset = 0
    search_entries = entries
    paragraph_score = 0.0
    if context_window:
        search_offset = int(context_window["start_index"])
        search_entries = entries[search_offset : search_offset + int(context_window["window_size"])]
        paragraph_score = float(context_window["score"])

    translated_candidates = [str(item["translated_excerpt"]) for item in search_entries]
    best_local_index, best_score = _find_best_matching_block(translated_candidates, selected_text, context_sentence)
    match_mode: Literal["sentence", "paragraph"] = "paragraph"
    window_size = min(max(1, selected_window_size), 4)
    window_start = search_offset
    if sentence_mode_requested:
        sentence_candidate = _find_alignment_sentence_candidate(entries, selected_text, context_sentence, context_window)
        if sentence_candidate:
            best_score = float(sentence_candidate["selected_score"])
            window_start = int(sentence_candidate["index"])
        elif best_local_index is None or best_score < 0.5:
            return None
        else:
            window_start = search_offset + best_local_index
        match_mode = "sentence"
        window_size = 1
    elif best_local_index is not None and best_score >= 0.32:
        window_start = search_offset + best_local_index
    elif context_window and paragraph_score >= 0.55:
        window_start = int(context_window["start_index"])
        window_size = int(context_window["window_size"])
    else:
        return None

    translated_excerpt = _join_alignment_window(entries, window_start, window_size, "translated_excerpt")
    source_excerpt = _join_alignment_window(entries, window_start, window_size, "source_excerpt")
    if not translated_excerpt or not source_excerpt:
        return None

    translated_excerpt = _cap_excerpt(
        translated_excerpt,
        max_sentences=1 if match_mode == "sentence" else 3,
        max_chars=320 if match_mode == "sentence" else 620,
    )
    source_excerpt = _cap_excerpt(
        source_excerpt,
        max_sentences=1 if match_mode == "sentence" else 3,
        max_chars=320 if match_mode == "sentence" else 620,
    )
    if match_mode == "sentence":
        coverage_score = _selected_excerpt_coverage_score(selected_text, translated_excerpt)
        if coverage_score < 0.88:
            return None
    if match_mode == "paragraph" and context_block:
        coverage_score = _context_excerpt_coverage_score(context_block, translated_excerpt)
        if coverage_score < 0.78:
            return None

    block_score = max(best_score, paragraph_score)
    confidence = _build_source_reference_confidence(
        match_mode,
        block_score,
        best_score if match_mode == "sentence" else 0.0,
        translated_excerpt,
        source_excerpt,
    )
    return {
        "translated_excerpt": translated_excerpt,
        "source_excerpt": source_excerpt,
        "match_mode": match_mode,
        "paragraph_index": window_start,
        "confidence": confidence,
        "score": block_score,
    }


def _filtered_sentence_count(text: Optional[str]) -> int:
    return len(
        [
            sentence
            for sentence in _split_sentences(text)
            if len(_normalize_match_text(sentence)) >= 6
        ]
    )


def _source_reference_structure_is_reliable(source_text: Optional[str], translated_text: Optional[str]) -> bool:
    source_count = _filtered_sentence_count(source_text)
    translated_count = _filtered_sentence_count(translated_text)
    if source_count == 0 or translated_count == 0:
        return False

    ratio = translated_count / max(source_count, 1)
    return 0.67 <= ratio <= 1.5


def _should_match_sentence(selected_text: str, context_sentence: Optional[str]) -> bool:
    if len(_split_sentences(selected_text)) != 1:
        return False
    if context_sentence and len(_split_sentences(context_sentence)) != 1:
        return False

    normalized_selected = _normalize_match_text(selected_text)
    normalized_context = _normalize_match_text(context_sentence)
    if not normalized_selected or not normalized_context:
        return False
    if normalized_selected == normalized_context:
        return True
    length_gap = abs(len(normalized_selected) - len(normalized_context))
    if length_gap > max(12, len(normalized_context) // 5):
        return False
    return _overlap_score(normalized_selected, normalized_context) >= 0.92


def _context_hash(context_sentence: Optional[str]) -> str:
    normalized = _normalize_sentence(context_sentence)
    if not normalized:
        return "global"
    return hashlib.sha256(normalized.lower().encode("utf-8")).hexdigest()[:24]


def _sentence_cache_key(sentence_text: str) -> str:
    build_content_hash = _get_build_content_hash()
    return f"sentence::{build_content_hash(sentence_text)}"


def _preview_text(text: Optional[str], max_length: int = 96) -> str:
    normalized = _normalize_sentence(text, max_length=max_length) or ""
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[:max_length]}..."


def _log_reader_event(level: str, event: str, **context: Any) -> None:
    log_method = getattr(logger, level, logger.info)
    safe_context = {
        key: value
        for key, value in context.items()
        if value is not None and value != ""
    }
    log_method("reader_learning %s %s", event, safe_context)


def _persist_sentence_alignment(
    supabase: Any,
    translation_row: dict[str, Any],
    alignment_payload: dict[str, Any],
) -> None:
    translation_id = translation_row.get("id")
    if not translation_id:
        return
    try:
        (
            supabase.table("chapter_translations")
            .update({"sentence_alignment": alignment_payload})
            .eq("id", translation_id)
            .execute()
        )
    except Exception as exc:
        _log_reader_event(
            "warning",
            "source_reference_alignment_persist_failed",
            chapter_id=translation_row.get("chapter_id"),
            locale=translation_row.get("locale"),
            detail=str(exc),
        )


def _build_external_links(locale: str, term: str) -> list[ReaderExternalLink]:
    query = term.strip()
    if not query:
        return []
    encoded = quote(query)
    if locale == "ja":
        return [
            ReaderExternalLink(label="Jotoba", url=f"https://jotoba.de/search/0/{encoded}"),
            ReaderExternalLink(label="Jisho", url=f"https://jisho.org/search/{encoded}"),
        ]
    if locale == "zh-CN":
        return [
            ReaderExternalLink(
                label="MDBG",
                url=f"https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={encoded}",
            ),
            ReaderExternalLink(label="Pleco", url=f"https://www.pleco.com/?search={encoded}"),
        ]
    if locale == "en":
        return [
            ReaderExternalLink(
                label="Cambridge",
                url=f"https://dictionary.cambridge.org/dictionary/english/{encoded}",
            ),
            ReaderExternalLink(
                label="Longman",
                url=f"https://www.ldoceonline.com/dictionary/{encoded}",
            ),
        ]
    return []


def _build_vi_rule_based_lookup(term: str) -> ReaderLookupResponse:
    normalized_term = _normalize_term(term)
    return ReaderLookupResponse(
        term=term,
        normalized_term=normalized_term,
        locale="vi",
        reading=None,
        meaning_vi=term,
        pos="từ/cụm tiếng Việt",
        notes="Đây là nội dung tiếng Việt. Tra nhanh chủ yếu hữu ích hơn với Anh, Nhật và Trung.",
        source="rule_based",
        external_links=[],
    )


def _build_vi_sentence_insight(sentence_text: str) -> ReaderSentenceInsightResponse:
    return ReaderSentenceInsightResponse(
        sentence_text=sentence_text,
        locale="vi",
        meaning_vi=sentence_text,
        notes="Đây là câu tiếng Việt gốc, nên phần diễn giải thêm chưa cần thiết.",
        source="rule_based",
    )


def _lookup_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "meaning_vi": {"type": "string"},
            "reading": {"type": "string"},
            "pos": {"type": "string"},
            "notes": {"type": "string"},
        },
        "required": ["meaning_vi", "reading", "pos", "notes"],
        "additionalProperties": False,
    }


def _sentence_insight_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "meaning_vi": {"type": "string"},
            "notes": {"type": "string"},
        },
        "required": ["meaning_vi", "notes"],
        "additionalProperties": False,
    }


def _lookup_prompt(locale: str, term: str, context_sentence: Optional[str]) -> tuple[str, str]:
    locale_label = {
        "en": "tiếng Anh",
        "ja": "tiếng Nhật",
        "zh-CN": "tiếng Trung giản thể",
    }.get(locale, locale)
    context_text = context_sentence or "(không có câu ngữ cảnh)"
    system_instruction = (
        "Bạn là trợ lý tra từ ngoại ngữ trong trang đọc truyện. "
        "Hãy trả về JSON ngắn gọn, đúng schema, không thêm markdown."
    )
    user_prompt = (
        f"Ngôn ngữ nguồn: {locale_label}\n"
        f"Từ hoặc cụm cần tra: {term}\n"
        f"Câu ngữ cảnh: {context_text}\n\n"
        "Yêu cầu:\n"
        "1. meaning_vi: nghĩa tiếng Việt ngắn gọn, đúng theo ngữ cảnh hiện tại.\n"
        "2. reading:\n"
        '   - en: IPA hoặc phát âm gần đúng rất ngắn\n'
        '   - ja: kana hoặc cách đọc ngắn gọn\n'
        '   - zh-CN: pinyin\n'
        '   - nếu không chắc thì trả ""\n'
        "3. pos: từ loại hoặc nhãn ngắn như noun, verb, idiom, proper noun.\n"
        "4. notes: tối đa 2 câu ngắn; nếu là tên riêng, idiom hoặc phrasal verb thì nêu rõ.\n"
        "5. Không lan man, không trả quá dài.\n"
    )
    return system_instruction, user_prompt


def _sentence_insight_prompt(locale: str, sentence_text: str) -> tuple[str, str]:
    locale_label = {
        "en": "tiếng Anh",
        "ja": "tiếng Nhật",
        "zh-CN": "tiếng Trung giản thể",
    }.get(locale, locale)
    system_instruction = (
        "Bạn là trợ lý học ngoại ngữ trong trang đọc truyện. "
        "Hãy diễn giải ngắn gọn ý của cả câu sang tiếng Việt và trả về JSON đúng schema."
    )
    user_prompt = (
        f"Ngôn ngữ nguồn: {locale_label}\n"
        f"Câu cần diễn giải: {sentence_text}\n\n"
        "Yêu cầu:\n"
        "1. meaning_vi: diễn giải ngắn gọn cả câu bằng tiếng Việt tự nhiên, tối đa 2 câu.\n"
        "2. notes: ghi chú ngắn về sắc thái, ý quan trọng hoặc điểm đáng chú ý của câu; tối đa 2 câu.\n"
        "3. Không dùng markdown, không lan man.\n"
    )
    return system_instruction, user_prompt


def _parse_lookup_payload(raw_text: str) -> dict[str, str]:
    parse_json_like_payload = _get_parse_json_like_payload()
    parsed = parse_json_like_payload(raw_text)
    return {
        "meaning_vi": str(parsed.get("meaning_vi") or "").strip(),
        "reading": str(parsed.get("reading") or "").strip(),
        "pos": str(parsed.get("pos") or "").strip(),
        "notes": str(parsed.get("notes") or "").strip(),
    }


def _parse_sentence_insight_payload(raw_text: str) -> dict[str, str]:
    parse_json_like_payload = _get_parse_json_like_payload()
    parsed = parse_json_like_payload(raw_text)
    return {
        "meaning_vi": str(parsed.get("meaning_vi") or "").strip(),
        "notes": str(parsed.get("notes") or "").strip(),
    }


async def _lookup_with_ai(locale: str, term: str, context_sentence: Optional[str]) -> ReaderLookupResponse:
    generate_structured_translation_payload = _get_generate_structured_translation_payload()
    system_instruction, user_prompt = _lookup_prompt(locale, term, context_sentence)
    payload = await generate_structured_translation_payload(
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        response_json_schema=_lookup_schema(),
        parser=_parse_lookup_payload,
        timeout_seconds=45.0,
    )

    return ReaderLookupResponse(
        term=term,
        normalized_term=_normalize_term(term),
        locale=locale,
        reading=payload.get("reading") or None,
        meaning_vi=payload.get("meaning_vi") or None,
        pos=payload.get("pos") or None,
        notes=payload.get("notes") or None,
        source="ai",
        external_links=_build_external_links(locale, term),
    )


async def _sentence_insight_with_ai(locale: str, sentence_text: str) -> ReaderSentenceInsightResponse:
    generate_structured_translation_payload = _get_generate_structured_translation_payload()
    system_instruction, user_prompt = _sentence_insight_prompt(locale, sentence_text)
    payload = await generate_structured_translation_payload(
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        response_json_schema=_sentence_insight_schema(),
        parser=_parse_sentence_insight_payload,
        timeout_seconds=45.0,
    )

    return ReaderSentenceInsightResponse(
        sentence_text=sentence_text,
        locale=locale,
        meaning_vi=payload.get("meaning_vi") or None,
        notes=payload.get("notes") or None,
        source="ai",
    )


def _raise_schema_error(exc: Exception) -> None:
    _log_reader_event("error", "schema_unavailable", detail=str(exc))
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "Reader learning schema chưa sẵn sàng. "
            "Hãy chạy scripts/supabase_reader_learning.sql. "
            f"Chi tiết: {exc}"
        ),
    )


def _verify_reader_user(authorization: Optional[str]) -> dict[str, Optional[str]]:
    token = _extract_bearer_token(authorization)
    if not token:
        _log_reader_event("warning", "auth_missing_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu token xác thực người dùng.",
        )

    supabase = _get_supabase()
    try:
        user_resp = supabase.auth.get_user(token)
    except Exception as exc:
        _log_reader_event("warning", "auth_invalid_token", detail=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Không xác thực được token người dùng: {exc}",
        )

    if not user_resp or not user_resp.user:
        _log_reader_event("warning", "auth_unknown_user")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token người dùng không hợp lệ hoặc đã hết hạn.",
        )

    return {
        "id": user_resp.user.id,
        "email": user_resp.user.email,
    }


def _deserialize_lookup_payload(row: dict[str, Any]) -> Optional[ReaderLookupResponse]:
    payload = row.get("payload_json")
    if not isinstance(payload, dict):
        return None

    links_raw = payload.get("external_links") or []
    links: list[ReaderExternalLink] = []
    for item in links_raw:
        if isinstance(item, dict) and item.get("label") and item.get("url"):
            links.append(ReaderExternalLink(label=str(item["label"]), url=str(item["url"])))

    try:
        return ReaderLookupResponse(
            term=str(payload.get("term") or ""),
            normalized_term=str(payload.get("normalized_term") or ""),
            locale=str(payload.get("locale") or row.get("locale") or "vi"),
            reading=(str(payload["reading"]).strip() if payload.get("reading") else None),
            meaning_vi=(str(payload["meaning_vi"]).strip() if payload.get("meaning_vi") else None),
            pos=(str(payload["pos"]).strip() if payload.get("pos") else None),
            notes=(str(payload["notes"]).strip() if payload.get("notes") else None),
            source="cache",
            external_links=links,
        )
    except Exception:
        return None


def _deserialize_sentence_insight_payload(row: dict[str, Any]) -> Optional[ReaderSentenceInsightResponse]:
    payload = row.get("payload_json")
    if not isinstance(payload, dict):
        return None

    try:
        return ReaderSentenceInsightResponse(
            sentence_text=str(payload.get("sentence_text") or ""),
            locale=str(payload.get("locale") or row.get("locale") or "vi"),
            meaning_vi=(str(payload["meaning_vi"]).strip() if payload.get("meaning_vi") else None),
            notes=(str(payload["notes"]).strip() if payload.get("notes") else None),
            source="cache",
        )
    except Exception:
        return None


def _get_cache_row(locale: str, normalized_term: str, context_hash: str) -> Optional[dict[str, Any]]:
    supabase = _get_supabase()
    try:
        result = (
            supabase.table("reader_lookup_cache")
            .select("payload_json, expires_at, locale")
            .eq("locale", locale)
            .eq("normalized_term", normalized_term)
            .eq("context_hash", context_hash)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        _raise_schema_error(exc)

    if not result.data:
        return None

    row = result.data[0]
    expires_at = row.get("expires_at")
    if expires_at:
        try:
            expires_at_dt = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            if expires_at_dt < datetime.now(timezone.utc):
                return None
        except Exception:
            return None

    return row


def _get_cached_lookup(locale: str, normalized_term: str, context_hash: str) -> Optional[ReaderLookupResponse]:
    row = _get_cache_row(locale, normalized_term, context_hash)
    if not row:
        return None
    return _deserialize_lookup_payload(row)


def _get_cached_sentence_insight(locale: str, sentence_text: str) -> Optional[ReaderSentenceInsightResponse]:
    row = _get_cache_row(locale, _sentence_cache_key(sentence_text), "global")
    if not row:
        return None
    return _deserialize_sentence_insight_payload(row)


def _cache_payload(
    *,
    locale: str,
    normalized_term: str,
    context_hash: str,
    payload: dict[str, Any],
    source: LookupSource,
) -> None:
    supabase = _get_supabase()
    try:
        supabase.table("reader_lookup_cache").upsert(
            {
                "locale": locale,
                "normalized_term": normalized_term,
                "context_hash": context_hash,
                "payload_json": payload,
                "source": source,
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
            },
            on_conflict="locale,normalized_term,context_hash",
        ).execute()
    except Exception:
        pass


@router.post("/lookup", response_model=ReaderLookupResponse)
async def lookup_reader_term(body: ReaderLookupRequest):
    locale = _normalize_locale(body.locale)
    term = " ".join(body.term.strip().split())
    context_sentence = _normalize_sentence(body.context_sentence)

    if not term:
        _log_reader_event("warning", "lookup_empty_term", locale=locale)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="term không được để trống.")

    if locale == "vi":
        return _build_vi_rule_based_lookup(term)

    normalized_term = _normalize_term(term)
    context_hash = _context_hash(context_sentence)
    build_rule_based_lookup = _get_build_rule_based_lookup()
    rule_based_payload = build_rule_based_lookup(locale, term, context_sentence)
    cache_normalized_term = rule_based_payload.get("normalized_term") if rule_based_payload else None
    if not cache_normalized_term:
        cache_normalized_term = normalized_term

    if rule_based_payload and rule_based_payload.get("meaning_vi"):
        _log_reader_event(
            "info",
            "lookup_rule_based_hit",
            locale=locale,
            term=_preview_text(term),
            normalized_term=cache_normalized_term,
            chapter_id=body.chapter_id,
        )
        response = ReaderLookupResponse(
            term=term,
            normalized_term=cache_normalized_term,
            locale=locale,
            reading=rule_based_payload.get("reading"),
            meaning_vi=rule_based_payload.get("meaning_vi"),
            pos=rule_based_payload.get("pos"),
            notes=rule_based_payload.get("notes"),
            source="rule_based",
            external_links=_build_external_links(locale, term),
        )
        _cache_payload(
            locale=locale,
            normalized_term=cache_normalized_term,
            context_hash=context_hash,
            payload={
                **response.dict(),
                "external_links": [item.dict() for item in response.external_links],
            },
            source=response.source,
        )
        return response

    cached = _get_cached_lookup(locale, cache_normalized_term, context_hash)
    if cached:
        if locale in {"ja", "zh-CN"} and not cached.reading:
            cached = None
        else:
            _log_reader_event(
                "info",
                "lookup_cache_hit",
                locale=locale,
                term=_preview_text(term),
                normalized_term=cache_normalized_term,
                chapter_id=body.chapter_id,
            )
            if not cached.external_links:
                cached.external_links = _build_external_links(locale, term)
            return cached

    try:
        response = await _lookup_with_ai(locale, term, context_sentence)
    except Exception as exc:
        _log_reader_event(
            "error",
            "lookup_ai_failed",
            locale=locale,
            term=_preview_text(term),
            normalized_term=cache_normalized_term,
            chapter_id=body.chapter_id,
            detail=str(exc),
        )
        raise

    _log_reader_event(
        "info",
        "lookup_ai_success",
        locale=locale,
        term=_preview_text(term),
        normalized_term=cache_normalized_term,
        chapter_id=body.chapter_id,
    )
    if rule_based_payload:
        if not response.reading and rule_based_payload.get("reading"):
            response.reading = rule_based_payload.get("reading")
        if not response.pos and rule_based_payload.get("pos"):
            response.pos = rule_based_payload.get("pos")
        if not response.notes and rule_based_payload.get("notes"):
            response.notes = rule_based_payload.get("notes")
    _cache_payload(
        locale=locale,
        normalized_term=cache_normalized_term,
        context_hash=context_hash,
        payload={
            **response.dict(),
            "external_links": [item.dict() for item in response.external_links],
        },
        source=response.source,
    )
    return response


@router.post("/sentence-insight", response_model=ReaderSentenceInsightResponse)
async def sentence_insight(body: ReaderSentenceInsightRequest):
    locale = _normalize_locale(body.locale)
    sentence_text = _normalize_sentence(body.sentence_text)

    if not sentence_text:
        _log_reader_event("warning", "sentence_insight_empty", locale=locale, chapter_id=body.chapter_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sentence_text không được để trống.")

    if locale == "vi":
        return _build_vi_sentence_insight(sentence_text)

    cached = _get_cached_sentence_insight(locale, sentence_text)
    if cached:
        _log_reader_event(
            "info",
            "sentence_insight_cache_hit",
            locale=locale,
            chapter_id=body.chapter_id,
            sentence=_preview_text(sentence_text),
        )
        return cached

    try:
        response = await _sentence_insight_with_ai(locale, sentence_text)
    except Exception as exc:
        _log_reader_event(
            "error",
            "sentence_insight_ai_failed",
            locale=locale,
            chapter_id=body.chapter_id,
            sentence=_preview_text(sentence_text),
            detail=str(exc),
        )
        raise
    _log_reader_event(
        "info",
        "sentence_insight_ai_success",
        locale=locale,
        chapter_id=body.chapter_id,
        sentence=_preview_text(sentence_text),
    )
    _cache_payload(
        locale=locale,
        normalized_term=_sentence_cache_key(sentence_text),
        context_hash="global",
        payload=response.dict(),
        source=response.source,
    )
    return response


@router.post("/source-reference", response_model=ReaderSourceReferenceResponse)
async def source_reference(body: ReaderSourceReferenceRequest):
    locale = _normalize_locale(body.locale)
    selected_text = _normalize_sentence(body.selected_text, max_length=1200)
    context_sentence = _normalize_sentence(body.context_sentence, max_length=2000)
    context_block = _normalize_sentence(body.context_block, max_length=4000)

    if not selected_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="selected_text không được để trống.")

    if locale == "vi":
        vi_mode: Literal["sentence", "paragraph"] = "sentence" if _should_match_sentence(selected_text, context_sentence) else "paragraph"
        return ReaderSourceReferenceResponse(
            locale=locale,
            selected_text=selected_text,
            translated_excerpt=context_sentence or selected_text,
            source_excerpt=context_sentence or selected_text,
            paragraph_index=None,
            match_mode=vi_mode,
            confidence="high" if vi_mode == "sentence" else "medium",
            source="rule_based",
        )

    supabase = _get_supabase()
    fetch_r2_content = _get_fetch_r2_content()
    resolve_chapter_translation = _get_resolve_chapter_translation()
    build_chapter_sentence_alignment = _get_build_chapter_sentence_alignment()

    chapter_result = (
        supabase.table("chapters")
        .select("id, chapter_number, content_url")
        .eq("id", body.chapter_id)
        .limit(1)
        .execute()
    )
    chapter_row = dict(chapter_result.data[0]) if chapter_result.data else None
    if not chapter_row:
        _log_reader_event("warning", "source_reference_chapter_missing", locale=locale, chapter_id=body.chapter_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy chương để đối chiếu.")

    translation = resolve_chapter_translation(chapter_row["id"], locale)
    if not translation or not translation.get("content"):
        _log_reader_event("warning", "source_reference_translation_missing", locale=locale, chapter_id=body.chapter_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chương này chưa có bản dịch để đối chiếu.")
    translated_content = str(translation.get("content") or "")

    try:
        source_content = fetch_r2_content(chapter_row["content_url"])
    except Exception as exc:
        _log_reader_event(
            "error",
            "source_reference_source_fetch_failed",
            locale=locale,
            chapter_id=body.chapter_id,
            detail=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Không tải được bản gốc tiếng Việt.")

    structure_is_reliable = _source_reference_structure_is_reliable(
        source_content,
        translated_content,
    )
    raw_alignment = translation.get("sentence_alignment") if isinstance(translation, dict) else None
    alignment_is_stale = _alignment_needs_regeneration(
        raw_alignment,
        source_text=source_content,
        translated_text=translated_content,
    )
    alignment_entries = [] if alignment_is_stale else _extract_sentence_alignment_entries(raw_alignment)

    if alignment_entries:
        alignment_match = _resolve_source_reference_from_alignment(
            alignment_entries,
            selected_text,
            context_sentence,
            context_block,
        )
        if alignment_match:
            _log_reader_event(
                "info",
                "source_reference_alignment_hit",
                locale=locale,
                chapter_id=body.chapter_id,
                paragraph_index=alignment_match["paragraph_index"],
                score=round(float(alignment_match["score"]), 3),
                match_mode=alignment_match["match_mode"],
                confidence=alignment_match["confidence"],
            )
            return ReaderSourceReferenceResponse(
                locale=locale,
                selected_text=selected_text,
                translated_excerpt=alignment_match["translated_excerpt"],
                source_excerpt=alignment_match["source_excerpt"],
                paragraph_index=alignment_match["paragraph_index"],
                match_mode=alignment_match["match_mode"],
                confidence=alignment_match["confidence"],
                source="rule_based",
            )

    generated_alignment: Optional[dict[str, Any]] = None
    generated_alignment_entries: list[dict[str, Any]] = []
    try:
        generated_alignment = build_chapter_sentence_alignment(
            source_text=source_content,
            translated_text=translated_content,
        )
        generated_alignment_entries = _extract_sentence_alignment_entries(generated_alignment)
    except Exception:
        generated_alignment = None
        generated_alignment_entries = []

    if generated_alignment and generated_alignment_entries:
        if alignment_is_stale or not alignment_entries:
            _persist_sentence_alignment(supabase, translation, generated_alignment)
        generated_alignment_match = _resolve_source_reference_from_alignment(
            generated_alignment_entries,
            selected_text,
            context_sentence,
            context_block,
        )
        if generated_alignment_match:
            _log_reader_event(
                "info",
                "source_reference_alignment_generated_hit",
                locale=locale,
                chapter_id=body.chapter_id,
                paragraph_index=generated_alignment_match["paragraph_index"],
                score=round(float(generated_alignment_match["score"]), 3),
                match_mode=generated_alignment_match["match_mode"],
                confidence=generated_alignment_match["confidence"],
                regenerated=alignment_is_stale or not alignment_entries,
            )
            return ReaderSourceReferenceResponse(
                locale=locale,
                selected_text=selected_text,
                translated_excerpt=generated_alignment_match["translated_excerpt"],
                source_excerpt=generated_alignment_match["source_excerpt"],
                paragraph_index=generated_alignment_match["paragraph_index"],
                match_mode=generated_alignment_match["match_mode"],
                confidence=generated_alignment_match["confidence"],
                source="rule_based",
            )

    translated_blocks = _split_text_blocks(translation.get("content"))
    source_blocks = _split_text_blocks(source_content)

    if not translated_blocks or not source_blocks:
        _log_reader_event("warning", "source_reference_empty_blocks", locale=locale, chapter_id=body.chapter_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không đủ dữ liệu để đối chiếu đoạn gốc.")

    if not structure_is_reliable:
        _log_reader_event(
            "warning",
            "source_reference_unreliable_structure",
            locale=locale,
            chapter_id=body.chapter_id,
            source_sentence_count=_filtered_sentence_count(source_content),
            translated_sentence_count=_filtered_sentence_count(str(translation.get("content") or "")),
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bản dịch chương này đang lệch cấu trúc nên chưa thể đối chiếu Gốc VI ổn định.",
        )

    block_query = context_block or context_sentence or selected_text
    best_index, best_score = _find_best_matching_block(translated_blocks, block_query, selected_text)
    if best_index is None or best_score < (0.5 if context_block else 0.35):
        _log_reader_event(
            "warning",
            "source_reference_no_match",
            locale=locale,
            chapter_id=body.chapter_id,
            selected=_preview_text(selected_text),
            context=_preview_text(context_sentence),
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chưa tìm được đoạn gốc tiếng Việt tương ứng.")

    if abs(len(translated_blocks) - len(source_blocks)) > 2:
        _log_reader_event(
            "warning",
            "source_reference_block_count_mismatch",
            locale=locale,
            chapter_id=body.chapter_id,
            translated_blocks=len(translated_blocks),
            source_blocks=len(source_blocks),
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chưa thể đối chiếu ổn định cho đoạn này. Hãy thử bôi đen gọn hơn.",
        )

    source_index = min(best_index, max(len(source_blocks) - 1, 0))
    translated_excerpt = selected_text.strip()
    source_excerpt = source_blocks[source_index].strip()
    match_mode: Literal["sentence", "paragraph"] = "paragraph"
    sentence_score = 0.0

    translated_block_excerpt = translated_blocks[best_index].strip()
    translated_sentences = _split_sentences(translated_block_excerpt)
    source_sentences = _split_sentences(source_excerpt)
    sentence_index, sentence_score = _find_best_matching_block(
        translated_sentences,
        selected_text,
        context_sentence,
    )
    selected_window_size = _selected_sentence_window_size(selected_text)

    if sentence_index is not None and source_sentences:
        mapped_sentence_index = min(sentence_index, max(len(source_sentences) - 1, 0))
        aligned_source_excerpt = _join_sentence_window(source_sentences, mapped_sentence_index, selected_window_size)
        if aligned_source_excerpt:
            source_excerpt = aligned_source_excerpt
        candidate_translated_excerpt = translated_sentences[sentence_index].strip()
        selected_coverage = _selected_excerpt_coverage_score(selected_text, candidate_translated_excerpt)

        if _should_match_sentence(selected_text, context_sentence) and sentence_score >= 0.35 and selected_coverage >= 0.88:
            match_mode = "sentence"
            translated_excerpt = candidate_translated_excerpt
            source_excerpt = _join_sentence_window(source_sentences, mapped_sentence_index, 1) or source_excerpt
        elif sentence_score >= 0.2 and selected_coverage >= 0.72:
            translated_excerpt = selected_text.strip()
        elif _should_match_sentence(selected_text, context_sentence):
            _log_reader_event(
                "warning",
                "source_reference_sentence_fallback_rejected",
                locale=locale,
                chapter_id=body.chapter_id,
                sentence_score=round(sentence_score, 3),
                coverage_score=round(selected_coverage, 3),
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chưa tìm được đoạn gốc tiếng Việt tương ứng.")

    source_excerpt = _cap_excerpt(
        source_excerpt,
        max_sentences=1 if match_mode == "sentence" else 3,
        max_chars=320 if match_mode == "sentence" else 620,
    )
    confidence = _build_source_reference_confidence(
        match_mode,
        best_score,
        sentence_score,
        translated_excerpt,
        source_excerpt,
    )

    _log_reader_event(
        "info",
        "source_reference_success",
        locale=locale,
        chapter_id=body.chapter_id,
        paragraph_index=source_index,
        score=round(best_score, 3),
        match_mode=match_mode,
        confidence=confidence,
    )
    return ReaderSourceReferenceResponse(
        locale=locale,
        selected_text=selected_text,
        translated_excerpt=translated_excerpt,
        source_excerpt=source_excerpt,
        paragraph_index=source_index,
        match_mode=match_mode,
        confidence=confidence,
        source="rule_based",
    )


@router.post("/save-vocab", response_model=ReaderSavedVocabItem)
async def save_reader_vocab(body: ReaderSaveVocabRequest, authorization: Optional[str] = Header(default=None)):
    user = _verify_reader_user(authorization)
    locale = _normalize_locale(body.locale)
    normalized_term = body.normalized_term or _normalize_term(body.term)

    payload = {
        "user_id": user["id"],
        "locale": locale,
        "term": body.term.strip(),
        "normalized_term": normalized_term,
        "reading": body.reading,
        "meaning_vi": body.meaning_vi,
        "pos": body.pos,
        "notes": body.notes,
        "context_sentence": body.context_sentence,
        "chapter_id": body.chapter_id,
        "source": body.source,
    }

    supabase = _get_supabase()
    try:
        result = supabase.table("reader_saved_vocab").insert(payload).execute()
    except Exception as exc:
        _log_reader_event(
            "error",
            "save_vocab_failed",
            user_id=user["id"],
            locale=locale,
            term=_preview_text(body.term),
            chapter_id=body.chapter_id,
            detail=str(exc),
        )
        _raise_schema_error(exc)

    if not result.data:
        _log_reader_event("error", "save_vocab_empty_result", user_id=user["id"], locale=locale, term=_preview_text(body.term))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không lưu được từ vựng.")
    _log_reader_event("info", "save_vocab_success", user_id=user["id"], locale=locale, term=_preview_text(body.term), chapter_id=body.chapter_id)
    return ReaderSavedVocabItem(**result.data[0])


@router.get("/saved-vocab", response_model=ReaderSavedVocabListResponse)
async def get_saved_reader_vocab(
    locale: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    authorization: Optional[str] = Header(default=None),
):
    user = _verify_reader_user(authorization)
    supabase = _get_supabase()

    query = (
        supabase.table("reader_saved_vocab")
        .select("*", count="exact")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
    )
    if locale:
        query = query.eq("locale", _normalize_locale(locale))

    start = (page - 1) * limit
    end = start + limit - 1

    try:
        result = query.range(start, end).execute()
    except Exception as exc:
        _raise_schema_error(exc)

    rows = result.data or []
    review_map: dict[str, dict[str, Any]] = {}
    vocab_ids = [row.get("id") for row in rows if row.get("id")]
    if vocab_ids:
        try:
            review_result = (
                supabase.table("reader_vocab_reviews")
                .select("saved_vocab_id,ease,interval_days,next_review_at,review_count")
                .in_("saved_vocab_id", vocab_ids)
                .execute()
            )
            review_map = {
                row.get("saved_vocab_id"): row
                for row in (review_result.data or [])
                if row.get("saved_vocab_id")
            }
        except Exception as exc:
            _log_reader_event("warning", "saved_vocab_review_join_failed", detail=str(exc), user_id=user["id"])

    now_iso = datetime.now(timezone.utc).isoformat()
    items: list[ReaderSavedVocabItem] = []
    for row in rows:
        review = review_map.get(row.get("id"))
        merged_row = dict(row)
        if review:
            next_review_at = review.get("next_review_at")
            merged_row.update(
                {
                    "review_count": int(review.get("review_count") or 0),
                    "next_review_at": next_review_at,
                    "interval_days": int(review.get("interval_days") or 0),
                    "ease": float(review.get("ease") or 0),
                    "due_for_review": bool(next_review_at and str(next_review_at) <= now_iso),
                }
            )
        items.append(ReaderSavedVocabItem(**merged_row))

    return ReaderSavedVocabListResponse(items=items, total=result.count or 0, page=page, limit=limit)


@router.post("/save-sentence", response_model=ReaderSavedSentenceItem)
async def save_reader_sentence(
    body: ReaderSaveSentenceRequest,
    authorization: Optional[str] = Header(default=None),
):
    user = _verify_reader_user(authorization)
    payload = {
        "user_id": user["id"],
        "locale": _normalize_locale(body.locale),
        "sentence_text": body.sentence_text.strip(),
        "meaning_vi": body.meaning_vi,
        "note": body.note,
        "chapter_id": body.chapter_id,
    }

    supabase = _get_supabase()
    try:
        result = supabase.table("reader_saved_sentences").insert(payload).execute()
    except Exception as exc:
        _log_reader_event(
            "error",
            "save_sentence_failed",
            user_id=user["id"],
            locale=payload["locale"],
            chapter_id=body.chapter_id,
            sentence=_preview_text(body.sentence_text),
            detail=str(exc),
        )
        _raise_schema_error(exc)

    if not result.data:
        _log_reader_event("error", "save_sentence_empty_result", user_id=user["id"], locale=payload["locale"], chapter_id=body.chapter_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không lưu được câu mẫu.")
    _log_reader_event("info", "save_sentence_success", user_id=user["id"], locale=payload["locale"], chapter_id=body.chapter_id)
    return ReaderSavedSentenceItem(**result.data[0])


@router.get("/saved-sentences", response_model=ReaderSavedSentenceListResponse)
async def get_saved_reader_sentences(
    locale: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    authorization: Optional[str] = Header(default=None),
):
    user = _verify_reader_user(authorization)
    supabase = _get_supabase()

    query = (
        supabase.table("reader_saved_sentences")
        .select("*", count="exact")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
    )
    if locale:
        query = query.eq("locale", _normalize_locale(locale))

    start = (page - 1) * limit
    end = start + limit - 1

    try:
        result = query.range(start, end).execute()
    except Exception as exc:
        _raise_schema_error(exc)

    items = [ReaderSavedSentenceItem(**row) for row in (result.data or [])]
    return ReaderSavedSentenceListResponse(items=items, total=result.count or 0, page=page, limit=limit)


@router.post("/review-vocab", response_model=ReaderReviewResponse)
async def review_reader_vocab(
    body: ReaderReviewRequest,
    authorization: Optional[str] = Header(default=None),
):
    user = _verify_reader_user(authorization)
    supabase = _get_supabase()

    try:
        vocab_result = (
            supabase.table("reader_saved_vocab")
            .select("id")
            .eq("id", body.saved_vocab_id)
            .eq("user_id", user["id"])
            .limit(1)
            .execute()
        )
    except Exception as exc:
        _raise_schema_error(exc)

    if not vocab_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy mục từ đã lưu.")

    try:
        existing = (
            supabase.table("reader_vocab_reviews")
            .select("*")
            .eq("saved_vocab_id", body.saved_vocab_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        _raise_schema_error(exc)

    current = (existing.data or [{}])[0]
    current_ease = float(current.get("ease", 2.5))
    current_count = int(current.get("review_count", 0))

    if body.grade <= 0:
        interval_days = 0
        ease = max(1.3, current_ease - 0.2)
    elif body.grade == 1:
        interval_days = 1
        ease = max(1.5, current_ease - 0.05)
    elif body.grade == 2:
        interval_days = 3
        ease = current_ease + 0.05
    else:
        interval_days = 7
        ease = current_ease + 0.1

    now = datetime.now(timezone.utc)
    next_review_at = now if interval_days == 0 else now + timedelta(days=interval_days)
    payload = {
        "saved_vocab_id": body.saved_vocab_id,
        "ease": round(ease, 2),
        "interval_days": interval_days,
        "next_review_at": next_review_at.isoformat(),
        "last_reviewed_at": now.isoformat(),
        "review_count": current_count + 1,
    }

    try:
        result = supabase.table("reader_vocab_reviews").upsert(payload, on_conflict="saved_vocab_id").execute()
    except Exception as exc:
        _log_reader_event(
            "error",
            "review_vocab_failed",
            user_id=user["id"],
            saved_vocab_id=body.saved_vocab_id,
            grade=body.grade,
            detail=str(exc),
        )
        _raise_schema_error(exc)

    row = (result.data or [payload])[0]
    _log_reader_event(
        "info",
        "review_vocab_success",
        user_id=user["id"],
        saved_vocab_id=body.saved_vocab_id,
        grade=body.grade,
        review_count=int(row.get("review_count", payload["review_count"])),
    )
    return ReaderReviewResponse(
        saved_vocab_id=body.saved_vocab_id,
        ease=float(row.get("ease", payload["ease"])),
        interval_days=int(row.get("interval_days", interval_days)),
        next_review_at=row.get("next_review_at", payload["next_review_at"]),
        review_count=int(row.get("review_count", payload["review_count"])),
    )


@router.post("/sentence-tts", response_model=ReaderSentenceTtsResponse)
async def create_reader_sentence_tts(body: ReaderSentenceTtsRequest, request: Request):
    locale = _normalize_locale(body.locale)
    sentence_text = _normalize_sentence(body.sentence_text, max_length=200)
    if not sentence_text:
        _log_reader_event("warning", "sentence_tts_empty", locale=locale, chapter_id=body.chapter_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sentence_text không được để trống.")

    build_content_hash = _get_build_content_hash()
    content_hash = build_content_hash(sentence_text)
    entity_id = body.chapter_id or 0
    voice = body.voice or "default"
    audio_url = (
        f"{str(request.base_url).rstrip('/')}/api/tts"
        f"?lang={quote(locale)}&speed={body.speed}&text={quote(sentence_text)}"
    )
    cached = False

    supabase = _get_supabase()
    try:
        existing = (
            supabase.table("tts_audio_cache")
            .select("audio_url")
            .eq("entity_type", "sentence")
            .eq("entity_id", entity_id)
            .eq("locale", locale)
            .eq("voice", voice)
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
                    "entity_type": "sentence",
                    "entity_id": entity_id,
                    "locale": locale,
                    "voice": voice,
                    "provider": "google-translate-tts",
                    "content_hash": content_hash,
                    "audio_url": audio_url,
                },
                on_conflict="entity_type,entity_id,locale,voice,content_hash",
            ).execute()
    except Exception as exc:
        _log_reader_event(
            "warning",
            "sentence_tts_cache_write_failed",
            locale=locale,
            chapter_id=body.chapter_id,
            sentence=_preview_text(sentence_text),
            detail=str(exc),
        )

    _log_reader_event(
        "info",
        "sentence_tts_ready",
        locale=locale,
        chapter_id=body.chapter_id,
        sentence=_preview_text(sentence_text),
        cached=cached,
    )
    return ReaderSentenceTtsResponse(
        status="ready",
        detail="Âm thanh câu đã sẵn sàng.",
        audio_url=audio_url,
        provider="google-translate-tts",
        cached=cached,
    )


@router.get("/learning-stats", response_model=ReaderLearningStatsResponse)
async def get_reader_learning_stats(authorization: Optional[str] = Header(default=None)):
    user = _verify_reader_user(authorization)
    supabase = _get_supabase()

    try:
        vocab_result = (
            supabase.table("reader_saved_vocab")
            .select("id", count="exact")
            .eq("user_id", user["id"])
            .execute()
        )
        sentence_result = (
            supabase.table("reader_saved_sentences")
            .select("id", count="exact")
            .eq("user_id", user["id"])
            .execute()
        )
        vocab_ids_result = (
            supabase.table("reader_saved_vocab")
            .select("id")
            .eq("user_id", user["id"])
            .execute()
        )
    except Exception as exc:
        _raise_schema_error(exc)

    vocab_ids = [row["id"] for row in (vocab_ids_result.data or []) if row.get("id")]
    review_due_count = 0
    if vocab_ids:
        try:
            review_result = (
                supabase.table("reader_vocab_reviews")
                .select("saved_vocab_id", count="exact")
                .in_("saved_vocab_id", vocab_ids)
                .lte("next_review_at", datetime.now(timezone.utc).isoformat())
                .execute()
            )
            review_due_count = review_result.count or 0
        except Exception as exc:
            _raise_schema_error(exc)

    return ReaderLearningStatsResponse(
        saved_vocab_count=vocab_result.count or 0,
        saved_sentence_count=sentence_result.count or 0,
        review_due_count=review_due_count,
    )
