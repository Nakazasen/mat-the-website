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


@router.get("/character", response_model=Optional[CharacterProfile])
async def get_character(
    name: str = Query(min_length=2, max_length=100),
    chapter: int = Query(ge=1, default=9999, description="Reader's current chapter (spoiler cap)"),
):
    """
    Returns a character profile from the wiki, filtered by chapter progress.
    Returns null if not found so the reader UI can fail softly.
    """
    supabase = _get_supabase()
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        row = query_character(supabase, name.strip(), chapter)
        if not row:
            normalized_query = normalize_name(name)
            row = query_character(supabase, normalized_query, chapter)

        if not row:
            return None

        chapter_introduced = row.get("chapter_introduced")
        if chapter_introduced is not None and chapter_introduced > chapter:
            return None

        return CharacterProfile(
            name=row.get("name") or row.get("title") or name,
            faction=row.get("faction"),
            status=row.get("status"),
            ability=row.get("ability"),
            first_appearance=row.get("first_appearance") or chapter_introduced,
            description=row.get("description") or row.get("summary"),
        )
    except Exception:
        return None
