"""
Wiki Search Endpoint (Backend)
GET /wiki/character?name=...&chapter=...

Searches the Supabase wiki for character information,
filtered to only include data from chapters ≤ chapter_progress.
This provides spoiler-free Quick Scan data for the HUD.
"""

import re
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from database import supabase

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


@router.get("/character", response_model=Optional[CharacterProfile])
async def get_character(
    name: str = Query(min_length=2, max_length=100),
    chapter: int = Query(ge=1, default=9999, description="Reader's current chapter (spoiler cap)"),
):
    """
    Returns a character profile from the wiki, filtered by chapter progress.
    Returns null if not found (not a 404 — soft fail for UI).
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        # Try exact name match first
        result = (
            supabase.table("wiki_entries")
            .select("name, faction, status, ability, first_appearance, description, chapter_introduced")
            .ilike("name", f"%{name.strip()}%")   # Case-insensitive partial match
            .lte("chapter_introduced", chapter)   # Spoiler cap: only chapters ≤ reader progress
            .order("chapter_introduced", desc=False)
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        row = result.data[0]
        return CharacterProfile(
            name=row.get("name", name),
            faction=row.get("faction"),
            status=row.get("status"),
            ability=row.get("ability"),
            first_appearance=row.get("first_appearance") or row.get("chapter_introduced"),
            description=row.get("description"),
        )

    except Exception as e:
        # Soft fail — don't break the reader if wiki is unavailable
        return None
