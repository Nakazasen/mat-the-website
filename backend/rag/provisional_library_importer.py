import json
from typing import List, Dict, Any
from backend.rag.provisional_library import normalize_name

def load_ranked_library(path: str) -> List[Dict[str, Any]]:
    """Loads a grouped ranked library and flattens it into a single list."""
    with open(path, "r", encoding="utf-8") as f:
        library = json.load(f)
    
    flat_records = []
    for key, records in library.items():
        if isinstance(records, list):
            flat_records.extend(records)
    return flat_records

def filter_importable_records(records: List[Dict[str, Any]], allowed_quality=("high_confidence", "medium_confidence")) -> List[Dict[str, Any]]:
    """Filters records based on their quality class."""
    return [r for r in records if r.get("quality_class") in allowed_quality]

def build_db_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares the database payload matching the provisional_library table columns."""
    name = record.get("name", "")
    norm_name = normalize_name(name)
    evidence = record.get("evidence", [])
    
    # Extract chapter numbers
    chapters = set()
    for ev in evidence:
        ch_num = ev.get("chapter_number")
        if ch_num is not None:
            try:
                chapters.add(int(ch_num))
            except (ValueError, TypeError):
                pass
    chapter_list = sorted(list(chapters))
    
    first_ch = chapter_list[0] if chapter_list else None
    last_ch = chapter_list[-1] if chapter_list else None
    
    return {
        "id": record.get("id"),
        "name": name,
        "normalized_name": norm_name,
        "type": record.get("type"),
        "summary": record.get("summary"),
        "evidence": evidence,
        "confidence": float(record.get("confidence", 0.0)),
        "quality_class": record.get("quality_class"),
        "status": record.get("status", "provisional"),
        "source": record.get("source", "story_chunks_auto_extract"),
        "feedback_score": int(record.get("feedback_score", 0)),
        "needs_review": bool(record.get("needs_review", False)),
        "chapter_numbers": chapter_list,
        "first_chapter": first_ch,
        "last_chapter": last_ch
    }

def upsert_provisional_records(supabase, records: List[Dict[str, Any]], dry_run: bool = True) -> Dict[str, Any]:
    """Upserts database payloads into provisional_library table in batches."""
    summary = {
        "processed": len(records),
        "upserted": 0,
        "failed": 0,
        "errors": []
    }
    if dry_run:
        summary["upserted"] = len(records)
        return summary
        
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        payloads = [build_db_payload(r) for r in batch]
        try:
            res = supabase.table("provisional_library").upsert(payloads).execute()
            summary["upserted"] += len(payloads)
        except Exception as e:
            summary["failed"] += len(payloads)
            summary["errors"].append(str(e))
            
    return summary

def summarize_import(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarizes counts of importable records by type and quality class."""
    by_type = {}
    by_quality = {}
    for r in records:
        t_type = r.get("type", "unknown")
        q_class = r.get("quality_class", "unknown")
        by_type[t_type] = by_type.get(t_type, 0) + 1
        by_quality[q_class] = by_quality.get(q_class, 0) + 1
    return {
        "total": len(records),
        "by_type": by_type,
        "by_quality": by_quality
    }
