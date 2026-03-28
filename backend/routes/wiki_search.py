"""
Wiki Search Endpoint (Backend)
GET /wiki/character?name=...&chapter=...

Searches the Supabase wiki for character information,
filtered to only include data from chapters <= chapter_progress.
This provides spoiler-safe Quick Scan data for the HUD.
"""

import re
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
