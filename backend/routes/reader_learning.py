from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional
from urllib.parse import quote

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
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


def _context_hash(context_sentence: Optional[str]) -> str:
    normalized = _normalize_sentence(context_sentence)
    if not normalized:
        return "global"
    return hashlib.sha256(normalized.lower().encode("utf-8")).hexdigest()[:24]


def _sentence_cache_key(sentence_text: str) -> str:
    build_content_hash = _get_build_content_hash()
    return f"sentence::{build_content_hash(sentence_text)}"


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
            if not cached.external_links:
                cached.external_links = _build_external_links(locale, term)
            return cached

    response = await _lookup_with_ai(locale, term, context_sentence)
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sentence_text không được để trống.")

    if locale == "vi":
        return _build_vi_sentence_insight(sentence_text)

    cached = _get_cached_sentence_insight(locale, sentence_text)
    if cached:
        return cached

    response = await _sentence_insight_with_ai(locale, sentence_text)
    _cache_payload(
        locale=locale,
        normalized_term=_sentence_cache_key(sentence_text),
        context_hash="global",
        payload=response.dict(),
        source=response.source,
    )
    return response


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
async def create_reader_sentence_tts(body: ReaderSentenceTtsRequest, request: Request):
    locale = _normalize_locale(body.locale)
    sentence_text = _normalize_sentence(body.sentence_text, max_length=200)
    if not sentence_text:
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
    except Exception:
        pass

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
