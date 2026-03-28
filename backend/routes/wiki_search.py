"""
Wiki Search Endpoint (Backend)
GET /wiki/character?name=...&chapter=...

Searches the Supabase wiki for character information,
filtered to only include data from chapters <= chapter_progress.
This provides spoiler-safe Quick Scan data for the HUD.
"""

import re
from difflib import SequenceMatcher
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel


def _get_supabase():
    """Lazy import to avoid circular/path issues on Render."""
    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase
    return supabase


router = APIRouter(prefix="/wiki", tags=["wiki_search"])


class CharacterProfile(BaseModel):
    name: str
    slug: Optional[str] = None
    image_url: Optional[str] = None
    faction: Optional[str] = None
    status: Optional[str] = None
    ability: Optional[str] = None
    first_appearance: Optional[int] = None
    description: Optional[str] = None


def normalize_name(name: str) -> str:
    """Lowercase, strip diacritics, remove punctuation for fuzzy matching."""
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", name.lower().strip())
    return re.sub(r"[^\w\s]", "", "".join(c for c in nfkd if not unicodedata.combining(c))).strip()


def _compact_name(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _alias_match_score(search_value: str, alias_value: str) -> float:
    query = normalize_name(search_value)
    alias = normalize_name(alias_value)
    if not query or not alias:
        return 0.0

    if query == alias:
        return 1.0
    if query in alias or alias in query:
        return 0.92

    query_compact = _compact_name(query)
    alias_compact = _compact_name(alias)
    if query_compact and alias_compact and (query_compact in alias_compact or alias_compact in query_compact):
        return 0.86

    query_tokens = [token for token in query.split(" ") if token]
    alias_tokens = [token for token in alias.split(" ") if token]
    if query_tokens and alias_tokens:
        overlap = len(set(query_tokens) & set(alias_tokens)) / max(len(set(query_tokens)), 1)
        if overlap >= 0.75:
            return 0.8

    return SequenceMatcher(None, query_compact[:120], alias_compact[:120]).ratio() * 0.75


def query_character_alias_match_fuzzy(supabase, search_value: str, chapter: int, locale: str):
    if not search_value:
        return None, None

    try:
        entries_result = (
            supabase.table("wiki_entries")
            .select("*")
            .eq("category", "Nhân vật")
            .limit(500)
            .execute()
        )
        entries = list(entries_result.data or [])
    except Exception:
        return None, None

    spoiler_safe_entries = []
    for entry in entries:
        chapter_introduced = entry.get("chapter_introduced")
        if chapter_introduced is not None and chapter_introduced > chapter:
            continue
        spoiler_safe_entries.append(entry)

    if not spoiler_safe_entries:
        return None, None

    entry_ids = [entry.get("id") for entry in spoiler_safe_entries if entry.get("id")]
    translations_by_entry: dict[str, list[dict]] = {}
    if entry_ids:
        try:
            translation_result = (
                supabase.table("wiki_entry_translations")
                .select("wiki_entry_id, locale, title, summary, content")
                .in_("wiki_entry_id", entry_ids)
                .limit(3000)
                .execute()
            )
            for row in (translation_result.data or []):
                key = str(row.get("wiki_entry_id") or "")
                if not key:
                    continue
                translations_by_entry.setdefault(key, []).append(row)
        except Exception:
            translations_by_entry = {}

    best_entry = None
    best_translation = None
    best_score = 0.0

    for entry in spoiler_safe_entries:
        alias_candidates: list[tuple[str, Optional[dict], float]] = []
        if entry.get("title"):
            alias_candidates.append((str(entry.get("title")), None, 0.0))
        if entry.get("name"):
            alias_candidates.append((str(entry.get("name")), None, 0.0))
        if isinstance(entry.get("tags"), list):
            for tag in entry.get("tags") or []:
                if tag:
                    alias_candidates.append((str(tag), None, 0.0))

        entry_translations = translations_by_entry.get(str(entry.get("id")), [])
        for translation in entry_translations:
            title = translation.get("title")
            if not title:
                continue
            locale_bonus = 0.06 if translation.get("locale") == locale else 0.0
            alias_candidates.append((str(title), translation, locale_bonus))

        for alias_text, alias_translation, bonus in alias_candidates:
            score = _alias_match_score(search_value, alias_text) + bonus
            if score > best_score:
                best_score = score
                best_entry = entry
                best_translation = alias_translation

    if best_score < 0.72:
        return None, None
    return best_entry, best_translation


def query_character(supabase, search_value: str, chapter: int):
    attempts = [
        ("title", True),
        ("name", True),
        ("title", False),
        ("name", False),
    ]

    for field_name, spoiler_safe in attempts:
        try:
            query = (
                supabase.table("wiki_entries")
                .select("*")
                .ilike(field_name, f"%{search_value}%")
                .limit(1)
            )

            if spoiler_safe:
                query = query.lte("chapter_introduced", chapter).order("chapter_introduced", desc=False)
            else:
                query = query.order(field_name, desc=False)

            result = query.execute()
            if result.data:
                return result.data[0]
        except Exception:
            continue

    return None


def query_character_alias_match(supabase, search_value: str, chapter: int):
    if not search_value:
        return None

    try:
        result = (
            supabase.table("wiki_entries")
            .select("*")
            .contains("tags", [search_value])
            .limit(5)
            .execute()
        )
        for entry in (result.data or []):
            chapter_introduced = entry.get("chapter_introduced")
            if chapter_introduced is not None and chapter_introduced > chapter:
                continue
            return entry
    except Exception:
        return None

    return None


def query_character_translation_match(supabase, search_value: str, chapter: int, locale: str):
    if not locale or locale == "vi":
        return None, None

    attempts = [
        search_value,
        normalize_name(search_value),
    ]

    for candidate in attempts:
        if not candidate:
            continue
        try:
            translation_result = (
                supabase.table("wiki_entry_translations")
                .select("wiki_entry_id, title, summary, content")
                .eq("locale", locale)
                .ilike("title", f"%{candidate}%")
                .limit(5)
                .execute()
            )
            for translation_row in (translation_result.data or []):
                wiki_entry_id = translation_row.get("wiki_entry_id")
                if not wiki_entry_id:
                    continue
                entry_result = (
                    supabase.table("wiki_entries")
                    .select("*")
                    .eq("id", wiki_entry_id)
                    .limit(1)
                    .execute()
                )
                if not entry_result.data:
                    continue
                entry = entry_result.data[0]
                chapter_introduced = entry.get("chapter_introduced")
                if chapter_introduced is not None and chapter_introduced > chapter:
                    continue
                return entry, translation_row
        except Exception:
            continue

    return None, None


def query_character_translation_match_any_locale(supabase, search_value: str, chapter: int):
    if not search_value:
        return None, None

    attempts = [
        search_value,
        normalize_name(search_value),
    ]

    for candidate in attempts:
        if not candidate:
            continue
        try:
            translation_result = (
                supabase.table("wiki_entry_translations")
                .select("wiki_entry_id, locale, title, summary, content")
                .ilike("title", f"%{candidate}%")
                .limit(8)
                .execute()
            )
            for translation_row in (translation_result.data or []):
                wiki_entry_id = translation_row.get("wiki_entry_id")
                if not wiki_entry_id:
                    continue
                entry_result = (
                    supabase.table("wiki_entries")
                    .select("*")
                    .eq("id", wiki_entry_id)
                    .limit(1)
                    .execute()
                )
                if not entry_result.data:
                    continue
                entry = entry_result.data[0]
                chapter_introduced = entry.get("chapter_introduced")
                if chapter_introduced is not None and chapter_introduced > chapter:
                    continue
                return entry, translation_row
        except Exception:
            continue

    return None, None


def query_character_translation(supabase, wiki_entry_id: str, locale: str):
    if not wiki_entry_id or locale == "vi":
        return None
    try:
        result = (
            supabase.table("wiki_entry_translations")
            .select("*")
            .eq("wiki_entry_id", wiki_entry_id)
            .eq("locale", locale)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


@router.get("/character", response_model=Optional[CharacterProfile])
async def get_character(
    name: str = Query(min_length=2, max_length=100),
    chapter: int = Query(ge=1, default=9999, description="Reader's current chapter (spoiler cap)"),
    locale: str = Query(default="vi"),
):
    """
    Returns a character profile from the wiki, filtered by chapter progress.
    Returns null if not found so the reader UI can fail softly.
    """
    supabase = _get_supabase()
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        row, translation = query_character_translation_match(supabase, name.strip(), chapter, locale)
        if not row:
            row = query_character_alias_match(supabase, name.strip(), chapter)
        if not row:
            row = query_character(supabase, name.strip(), chapter)
        if not row:
            normalized_query = normalize_name(name)
            row, translation = query_character_translation_match(supabase, normalized_query, chapter, locale)
            if not row:
                row = query_character_alias_match(supabase, normalized_query, chapter)
            if not row:
                row = query_character(supabase, normalized_query, chapter)
        if not row:
            row, translation = query_character_alias_match_fuzzy(supabase, name.strip(), chapter, locale)
        if not row:
            row, translation = query_character_translation_match_any_locale(supabase, name.strip(), chapter)
        if not row:
            normalized_query = normalize_name(name)
            row, translation = query_character_translation_match_any_locale(supabase, normalized_query, chapter)

        if not row:
            return None

        chapter_introduced = row.get("chapter_introduced")
        if chapter_introduced is not None and chapter_introduced > chapter:
            return None

        if not translation:
            translation = query_character_translation(supabase, row.get("id"), locale)
        resolved_name = row.get("name") or row.get("title") or name
        resolved_description = row.get("description") or row.get("summary")
        if translation:
            resolved_name = translation.get("title") or resolved_name
            resolved_description = translation.get("summary") or translation.get("content") or resolved_description

        return CharacterProfile(
            name=resolved_name,
            slug=row.get("slug"),
            image_url=row.get("image_url"),
            faction=row.get("faction"),
            status=row.get("status"),
            ability=row.get("ability"),
            first_appearance=row.get("first_appearance") or chapter_introduced,
            description=resolved_description,
        )
    except Exception:
        return None
