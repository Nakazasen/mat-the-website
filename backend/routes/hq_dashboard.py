"""
Base HQ Dashboard API
GET /hq/status?chapter={n}&faction={key}
Returns the most recent resource snapshot for the given faction at or before chapter n.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
try:
    from database import supabase
except ImportError:
    from backend.database import supabase

router = APIRouter(prefix="/hq", tags=["hq_dashboard"])


class HQSnapshot(BaseModel):
    chapter_id: int
    faction: str
    food_days: int
    crystal_count: int
    water_unit: int
    warriors: int
    researchers: int
    civilians: int
    wall_level: int
    territory_km2: int
    morale: int
    # Derived field for UI
    total_population: int


@router.get("/status", response_model=HQSnapshot)
async def get_hq_status(
    chapter: int = Query(ge=1, description="Current chapter number"),
    faction: str = Query(default="main", description="Faction key"),
):
    """
    Returns the most recent HQ snapshot at or before the given chapter.
    This ensures no future data is revealed (spoiler-safe).
    """
    try:
        result = (
            supabase.table("hq_snapshots")
            .select("*")
            .eq("faction", faction)
            .lte("chapter_id", chapter)  # Only chapters up to current
            .order("chapter_id", desc=True)
            .limit(1)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"No HQ snapshot found for faction '{faction}' at chapter {chapter}",
            )

        row = result.data[0]
        return HQSnapshot(
            **{k: row[k] for k in HQSnapshot.model_fields if k != "total_population"},
            total_population=row["warriors"] + row["researchers"] + row["civilians"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_hq_history(
    chapter: int = Query(ge=1),
    faction: str = Query(default="main"),
    limit: int = Query(default=5, le=10),
):
    """
    Returns the last N snapshots up to the current chapter.
    Used by the Dashboard to draw progression charts.
    """
    try:
        result = (
            supabase.table("hq_snapshots")
            .select("chapter_id, food_days, crystal_count, warriors, morale")
            .eq("faction", faction)
            .lte("chapter_id", chapter)
            .order("chapter_id", desc=True)
            .limit(limit)
            .execute()
        )
        return list(reversed(result.data))  # Chronological order for charts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
