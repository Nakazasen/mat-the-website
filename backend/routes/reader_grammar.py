from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/reader", tags=["reader_grammar"])

LookupSource = Literal["cache", "rule_based", "ai", "placeholder"]
GrammarHintCategory = Literal[
    "grammar",
    "structure",
    "idiom",
    "phrasal_verb",
    "collocation",
    "conjugation",
    "aspect",
    "tone",
]


class ReaderGrammarHint(BaseModel):
    title: str
    explanation_vi: str
    example_fragment: Optional[str] = None
    category: GrammarHintCategory = "grammar"


class ReaderGrammarHintsRequest(BaseModel):
    locale: str = "vi"
    sentence_text: str = Field(..., min_length=1, max_length=1200)
    chapter_id: Optional[int] = None


class ReaderGrammarHintsResponse(BaseModel):
    sentence_text: str
    locale: str
    hints: list[ReaderGrammarHint] = Field(default_factory=list)
    source: LookupSource


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


def _get_supabase():
    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase
    return supabase


def _normalize_sentence(text: Optional[str], max_length: int = 1200) -> Optional[str]:
    normalized = " ".join((text or "").strip().split())
    if not normalized:
        return None
    return normalized[:max_length]


def _grammar_cache_key(sentence_text: str) -> str:
    build_content_hash = _get_build_content_hash()
    return f"grammar::{build_content_hash(sentence_text)}"


def _append_hint(
    hints: list[ReaderGrammarHint],
    *,
    title: str,
    explanation_vi: str,
    example_fragment: str,
    category: GrammarHintCategory,
) -> None:
    if len(hints) >= 3:
        return

    signature = (title.strip().lower(), example_fragment.strip().lower())
    existing = {(item.title.strip().lower(), (item.example_fragment or "").strip().lower()) for item in hints}
    if signature in existing:
        return

    hints.append(
        ReaderGrammarHint(
            title=title.strip(),
            explanation_vi=explanation_vi.strip(),
            example_fragment=example_fragment.strip() or None,
            category=category,
        )
    )


def _build_en_rule_based_hints(sentence_text: str) -> list[ReaderGrammarHint]:
    lowered = sentence_text.lower()
    hints: list[ReaderGrammarHint] = []

    phrasal_verbs = [
        "give up",
        "look for",
        "find out",
        "carry on",
        "wake up",
        "pick up",
        "turn out",
        "set up",
        "take over",
        "come back",
        "go on",
        "figure out",
    ]
    for phrase in phrasal_verbs:
        if re.search(rf"\b{re.escape(phrase)}\b", lowered):
            _append_hint(
                hints,
                title=phrase,
                explanation_vi="Đây là phrasal verb. Nghĩa của cả cụm thường khác nghĩa tách rời của từng từ.",
                example_fragment=phrase,
                category="phrasal_verb",
            )

    idioms = {
        "at the end of the day": "Cụm này thường dùng để chốt lại ý chính hoặc kết luận cuối cùng.",
        "out of the blue": "Cụm này diễn tả việc gì đó xảy ra rất bất ngờ, không báo trước.",
        "a piece of cake": "Đây là idiom mang nghĩa rất dễ làm, không phải nói về bánh thật.",
    }
    for phrase, explanation in idioms.items():
        if phrase in lowered:
            _append_hint(
                hints,
                title=phrase,
                explanation_vi=explanation,
                example_fragment=phrase,
                category="idiom",
            )

    collocations = {
        "make sure": "Đây là collocation rất thường gặp, mang nghĩa đảm bảo hoặc chắc chắn rằng.",
        "pay attention": "Cụm này thường đi cùng giới từ to để diễn tả việc chú ý vào điều gì đó.",
        "take care": "Collocation quen thuộc, tùy ngữ cảnh có thể là chăm sóc hoặc cẩn thận.",
    }
    for phrase, explanation in collocations.items():
        if phrase in lowered:
            _append_hint(
                hints,
                title=phrase,
                explanation_vi=explanation,
                example_fragment=phrase,
                category="collocation",
            )

    return hints


def _build_ja_rule_based_hints(sentence_text: str) -> list[ReaderGrammarHint]:
    hints: list[ReaderGrammarHint] = []
    rules: list[tuple[str, str, str, GrammarHintCategory]] = [
        (r"ている", "〜ている", "Mẫu này thường diễn tả trạng thái đang diễn ra hoặc kết quả còn duy trì.", "aspect"),
        (r"てしま", "〜てしまう", "Mẫu này thường gợi ý sắc thái lỡ, xong hẳn, hoặc có chút tiếc nuối.", "tone"),
        (r"ようになる", "〜ようになる", "Mẫu này diễn tả sự thay đổi dẫn đến việc bắt đầu có thể hoặc có thói quen làm gì đó.", "grammar"),
        (r"わけではない", "〜わけではない", "Mẫu này dùng để phủ định một phần: không hẳn là..., không phải hoàn toàn là....", "structure"),
        (r"ことがある", "〜ことがある", "Mẫu này thường diễn tả kinh nghiệm hoặc việc thỉnh thoảng xảy ra.", "grammar"),
        (r"しか.+ない", "〜しか…ない", "Mẫu này nhấn mạnh ý chỉ có bấy nhiêu, ngoài ra không có gì khác.", "structure"),
        (r"ばかり", "〜ばかり", "Tùy ngữ cảnh, mẫu này có thể là toàn là..., vừa mới..., hoặc chỉ chăm chăm vào....", "tone"),
        (r"られる", "〜られる", "Dạng này có thể là bị động, khả năng hoặc kính ngữ; cần đọc theo ngữ cảnh cụ thể.", "conjugation"),
        (r"させ", "〜させる", "Dạng sai khiến: khiến hoặc cho ai đó làm gì.", "conjugation"),
    ]
    for pattern, title, explanation, category in rules:
        match = re.search(pattern, sentence_text)
        if match:
            _append_hint(
                hints,
                title=title,
                explanation_vi=explanation,
                example_fragment=match.group(0),
                category=category,
            )
    return hints


def _build_zh_rule_based_hints(sentence_text: str) -> list[ReaderGrammarHint]:
    hints: list[ReaderGrammarHint] = []

    if "把" in sentence_text:
        _append_hint(
            hints,
            title="把字句",
            explanation_vi="Cấu trúc 把 đưa tân ngữ lên trước để nhấn mạnh cách đối tượng bị tác động hoặc xử lý.",
            example_fragment="把",
            category="structure",
        )
    if "被" in sentence_text:
        _append_hint(
            hints,
            title="被字句",
            explanation_vi="Cấu trúc 被 thường dùng để diễn tả bị động, nhấn vào việc chủ thể bị tác động.",
            example_fragment="被",
            category="structure",
        )
    if "了" in sentence_text:
        _append_hint(
            hints,
            title="了",
            explanation_vi="了 thường đánh dấu hoàn thành, thay đổi trạng thái hoặc một sự việc đã xảy ra trong ngữ cảnh.",
            example_fragment="了",
            category="aspect",
        )
    if "着" in sentence_text:
        _append_hint(
            hints,
            title="着",
            explanation_vi="着 thường gợi ý trạng thái đang duy trì hoặc hành động diễn ra song song.",
            example_fragment="着",
            category="aspect",
        )
    if "过" in sentence_text:
        _append_hint(
            hints,
            title="过",
            explanation_vi="过 thường dùng để nói về trải nghiệm từng có trong quá khứ.",
            example_fragment="过",
            category="aspect",
        )
    if "越来越" in sentence_text:
        _append_hint(
            hints,
            title="越来越…",
            explanation_vi="Cấu trúc này diễn tả mức độ thay đổi dần theo hướng ngày càng hơn.",
            example_fragment="越来越",
            category="grammar",
        )
    return hints


def _build_rule_based_hints(locale: str, sentence_text: str) -> list[ReaderGrammarHint]:
    if locale == "en":
        return _build_en_rule_based_hints(sentence_text)
    if locale == "ja":
        return _build_ja_rule_based_hints(sentence_text)
    if locale == "zh-CN":
        return _build_zh_rule_based_hints(sentence_text)
    return []


def _grammar_hints_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "hints": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "explanation_vi": {"type": "string"},
                        "example_fragment": {"type": "string"},
                        "category": {
                            "type": "string",
                            "enum": [
                                "grammar",
                                "structure",
                                "idiom",
                                "phrasal_verb",
                                "collocation",
                                "conjugation",
                                "aspect",
                                "tone",
                            ],
                        },
                    },
                    "required": ["title", "explanation_vi", "example_fragment", "category"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["hints"],
        "additionalProperties": False,
    }


def _grammar_hints_prompt(locale: str, sentence_text: str) -> tuple[str, str]:
    locale_label = {
        "en": "tiếng Anh",
        "ja": "tiếng Nhật",
        "zh-CN": "tiếng Trung giản thể",
    }.get(locale, locale)
    system_instruction = (
        "Bạn là trợ lý học ngữ pháp trong trang đọc truyện. "
        "Hãy chỉ ra tối đa 3 điểm ngữ pháp, cấu trúc hoặc cụm từ đáng học nhất trong câu, "
        "và trả về JSON đúng schema."
    )
    user_prompt = (
        f"Ngôn ngữ nguồn: {locale_label}\n"
        f"Câu cần phân tích: {sentence_text}\n\n"
        "Yêu cầu:\n"
        "1. Chỉ chọn các điểm thực sự đáng học đối với người đọc truyện.\n"
        "2. Mỗi hint gồm:\n"
        "   - title: tên mẫu/cấu trúc ngắn gọn\n"
        "   - explanation_vi: giải thích bằng tiếng Việt trong 1-2 câu\n"
        "   - example_fragment: đoạn trích ngắn đúng từ câu, nếu có\n"
        "   - category: một trong grammar, structure, idiom, phrasal_verb, collocation, conjugation, aspect, tone\n"
        "3. Nếu câu không có điểm ngữ pháp nổi bật, trả mảng hints rỗng.\n"
        "4. Không dùng markdown, không viết dài dòng.\n"
    )
    return system_instruction, user_prompt


def _parse_grammar_hints_payload(raw_text: str) -> dict[str, Any]:
    parse_json_like_payload = _get_parse_json_like_payload()
    parsed = parse_json_like_payload(raw_text)
    hints_raw = parsed.get("hints") or []
    hints: list[dict[str, str]] = []
    if isinstance(hints_raw, list):
        for item in hints_raw[:3]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            explanation_vi = str(item.get("explanation_vi") or "").strip()
            category = str(item.get("category") or "grammar").strip()
            if not title or not explanation_vi:
                continue
            if category not in {
                "grammar",
                "structure",
                "idiom",
                "phrasal_verb",
                "collocation",
                "conjugation",
                "aspect",
                "tone",
            }:
                category = "grammar"
            hints.append(
                {
                    "title": title,
                    "explanation_vi": explanation_vi,
                    "example_fragment": str(item.get("example_fragment") or "").strip(),
                    "category": category,
                }
            )
    return {"hints": hints}


async def _grammar_hints_with_ai(locale: str, sentence_text: str) -> ReaderGrammarHintsResponse:
    generate_structured_translation_payload = _get_generate_structured_translation_payload()
    system_instruction, user_prompt = _grammar_hints_prompt(locale, sentence_text)
    payload = await generate_structured_translation_payload(
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        response_json_schema=_grammar_hints_schema(),
        parser=_parse_grammar_hints_payload,
        timeout_seconds=45.0,
    )
    return ReaderGrammarHintsResponse(
        sentence_text=sentence_text,
        locale=locale,
        hints=[ReaderGrammarHint(**item) for item in (payload.get("hints") or [])[:3]],
        source="ai",
    )


def _deserialize_payload(row: dict[str, Any]) -> Optional[ReaderGrammarHintsResponse]:
    payload = row.get("payload_json")
    if not isinstance(payload, dict):
        return None
    hints_raw = payload.get("hints") or []
    hints: list[ReaderGrammarHint] = []
    if isinstance(hints_raw, list):
        for item in hints_raw[:3]:
            if not isinstance(item, dict):
                continue
            try:
                hints.append(ReaderGrammarHint(**item))
            except Exception:
                continue
    try:
        return ReaderGrammarHintsResponse(
            sentence_text=str(payload.get("sentence_text") or ""),
            locale=str(payload.get("locale") or row.get("locale") or "vi"),
            hints=hints,
            source="cache",
        )
    except Exception:
        return None


def _cache_payload(locale: str, sentence_text: str, payload: dict[str, Any], source: LookupSource) -> None:
    supabase = _get_supabase()
    try:
        supabase.table("reader_lookup_cache").upsert(
            {
                "locale": locale,
                "normalized_term": _grammar_cache_key(sentence_text),
                "context_hash": "global",
                "payload_json": payload,
                "source": source,
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
            },
            on_conflict="locale,normalized_term,context_hash",
        ).execute()
    except Exception:
        pass


def _get_cached_payload(locale: str, sentence_text: str) -> Optional[ReaderGrammarHintsResponse]:
    supabase = _get_supabase()
    try:
        result = (
            supabase.table("reader_lookup_cache")
            .select("payload_json, expires_at, locale")
            .eq("locale", locale)
            .eq("normalized_term", _grammar_cache_key(sentence_text))
            .eq("context_hash", "global")
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Reader learning schema chưa sẵn sàng. "
                "Hãy chạy scripts/supabase_reader_learning.sql. "
                f"Chi tiết: {exc}"
            ),
        )

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

    return _deserialize_payload(row)


@router.post("/grammar-hints", response_model=ReaderGrammarHintsResponse)
async def grammar_hints(body: ReaderGrammarHintsRequest):
    locale = _normalize_locale(body.locale)
    sentence_text = _normalize_sentence(body.sentence_text)

    if not sentence_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sentence_text không được để trống.")

    if locale == "vi":
        return ReaderGrammarHintsResponse(sentence_text=sentence_text, locale=locale, hints=[], source="rule_based")

    cached = _get_cached_payload(locale, sentence_text)
    if cached:
        return cached

    hints = _build_rule_based_hints(locale, sentence_text)
    source: LookupSource = "rule_based"

    if len(hints) < 2:
        try:
            ai_payload = await _grammar_hints_with_ai(locale, sentence_text)
            for hint in ai_payload.hints:
                _append_hint(
                    hints,
                    title=hint.title,
                    explanation_vi=hint.explanation_vi,
                    example_fragment=hint.example_fragment or "",
                    category=hint.category,
                )
            if ai_payload.hints:
                source = "ai"
        except Exception:
            source = "rule_based"

    response = ReaderGrammarHintsResponse(
        sentence_text=sentence_text,
        locale=locale,
        hints=hints,
        source=source,
    )
    _cache_payload(locale, sentence_text, response.dict(), response.source)
    return response
