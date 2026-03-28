from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from urllib.parse import quote

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/reader", tags=["reader_learning"])

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
    sentence_text: str = Field(..., min_length=1, max_length=1200)
    speed: float = Field(default=1.0, ge=0.5, le=1.5)


class ReaderSentenceTtsResponse(BaseModel):
    status: str
    detail: str
    audio_url: Optional[str] = None
    provider: Optional[str] = None


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


def _context_hash(context_sentence: Optional[str]) -> str:
    normalized = " ".join((context_sentence or "").strip().split()).lower()
    if not normalized:
        return "global"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]


def _build_external_links(locale: str, term: str) -> list[ReaderExternalLink]:
    query = term.strip()
    if not query:
        return []
    encoded = quote(query)
    if locale == "ja":
        return [ReaderExternalLink(label="Jotoba", url=f"https://jotoba.de/search/0/{encoded}")]
    if locale == "zh-CN":
        return [
            ReaderExternalLink(
                label="MDBG",
                url=f"https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={encoded}",
            )
        ]
    if locale == "en":
        return [
            ReaderExternalLink(
                label="Cambridge",
                url=f"https://dictionary.cambridge.org/dictionary/english/{encoded}",
            )
        ]
    return []


def _build_placeholder_lookup(locale: str, term: str) -> ReaderLookupResponse:
    notes = (
        "MVP scaffold: hiện mới cố định contract, cache và luồng lưu học liệu. "
        "Bước tiếp theo là nối rule-based lookup và AI giải nghĩa theo ngữ cảnh."
    )
    return ReaderLookupResponse(
        term=term,
        normalized_term=_normalize_term(term),
        locale=locale,
        meaning_vi=None,
        pos=None,
        notes=notes,
        source="placeholder",
        external_links=_build_external_links(locale, term),
    )


def _raise_schema_error(exc: Exception) -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "Reader learning schema chưa sẵn sàng. Hãy chạy scripts/supabase_reader_learning.sql. "
            f"Chi tiết: {exc}"
        ),
    )


def _verify_reader_user(authorization: Optional[str]) -> dict:
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu token xác thực người dùng.",
        )

    supabase = _get_supabase()
    try:
        user_resp = supabase.auth.get_user(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Không xác thực được token người dùng: {exc}",
        )

    if not user_resp or not user_resp.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token người dùng không hợp lệ hoặc đã hết hạn.",
        )

    return {
        "id": user_resp.user.id,
        "email": user_resp.user.email,
    }


@router.post("/lookup", response_model=ReaderLookupResponse)
async def lookup_reader_term(body: ReaderLookupRequest):
    locale = _normalize_locale(body.locale)
    term = " ".join(body.term.strip().split())
    if not term:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="term không được để trống.")

    supabase = _get_supabase()
    context_hash = _context_hash(body.context_sentence)
    normalized_term = _normalize_term(term)

    try:
        result = (
            supabase.table("reader_lookup_cache")
            .select("payload_json, expires_at, source")
            .eq("locale", locale)
            .eq("normalized_term", normalized_term)
            .eq("context_hash", context_hash)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        _raise_schema_error(exc)

    if result.data:
        row = result.data[0]
        expires_at = row.get("expires_at")
        if not expires_at or datetime.fromisoformat(expires_at.replace("Z", "+00:00")) > datetime.now(timezone.utc):
            payload = row.get("payload_json") or {}
            payload.setdefault("term", term)
            payload.setdefault("normalized_term", normalized_term)
            payload.setdefault("locale", locale)
            payload.setdefault("source", "cache")
            payload.setdefault("external_links", [link.dict() for link in _build_external_links(locale, term)])
            return ReaderLookupResponse(**payload)

    return _build_placeholder_lookup(locale, term)


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
        _raise_schema_error(exc)

    if not result.data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không lưu được từ vựng.")
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

    items = [ReaderSavedVocabItem(**row) for row in (result.data or [])]
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
        _raise_schema_error(exc)

    if not result.data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không lưu được câu mẫu.")
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
        _raise_schema_error(exc)

    row = (result.data or [payload])[0]
    return ReaderReviewResponse(
        saved_vocab_id=body.saved_vocab_id,
        ease=float(row.get("ease", payload["ease"])),
        interval_days=int(row.get("interval_days", interval_days)),
        next_review_at=row.get("next_review_at", payload["next_review_at"]),
        review_count=int(row.get("review_count", payload["review_count"])),
    )


@router.post("/sentence-tts", response_model=ReaderSentenceTtsResponse)
async def create_reader_sentence_tts(body: ReaderSentenceTtsRequest):
    _normalize_locale(body.locale)
    return ReaderSentenceTtsResponse(
        status="not_implemented",
        detail="Sentence TTS skeleton đã sẵn sàng. Bước tiếp theo là nối vào pipeline TTS hiện có theo từng câu.",
        audio_url=None,
        provider=None,
    )
