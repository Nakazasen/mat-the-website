import re
from typing import List, Dict, Any, Optional

def normalize_chapter_title(text: str) -> str:
    """Normalizes the chapter title by removing HTML and extra spaces."""
    if not text:
        return ""
    # Remove HTML tags if any
    cleaned = re.sub(r'<[^>]*>', '', text)
    # Normalize spacing
    return " ".join(cleaned.strip().split())

def extract_chapter_number(title_or_text: str) -> Optional[int]:
    """Extracts chapter number from title or text (e.g. 'Chương 830: ...' -> 830)."""
    if not title_or_text:
        return None
    normalized = normalize_chapter_title(title_or_text)
    
    # Match patterns like "Chương 830", "Chapter 830", "Chg 830", "C. 830", "C830"
    match = re.search(r'(?:chương|chapter|chg|c\.?)\s*(\d+)', normalized, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Match digit prefix like "830. Tên chương"
    match_prefix = re.search(r'^(\d+)\b', normalized)
    if match_prefix:
        return int(match_prefix.group(1))
        
    # Fallback to find any standalone number
    match_fallback = re.search(r'\b(\d+)\b', normalized)
    if match_fallback:
        return int(match_fallback.group(1))
        
    return None

def detect_missing_chapters(existing_chapters: List[int], source_chapters: List[int]) -> List[int]:
    """Returns a list of chapters in source_chapters that are not in existing_chapters."""
    existing_set = set(existing_chapters)
    return sorted(list(set(ch for ch in source_chapters if ch not in existing_set)))

def build_new_chapter_ingest_plan(existing_chapters: List[int], source_chapters: List[int]) -> Dict[str, Any]:
    """Builds a dry-run plan for ingestion comparing existing with source chapters."""
    existing_sorted = sorted(list(set(existing_chapters)))
    source_sorted = sorted(list(set(source_chapters)))
    
    current_last_chapter = existing_sorted[-1] if existing_sorted else 0
    detected_source_last_chapter = source_sorted[-1] if source_sorted else 0
    
    # New chapters to ingest: those present in source but not in existing
    new_chapters_to_ingest = detect_missing_chapters(existing_sorted, source_sorted)
    
    # Skipped: those in source and already in existing
    existing_set = set(existing_sorted)
    skipped_existing_chapters = sorted(list(set(ch for ch in source_sorted if ch in existing_set)))
    
    # Gaps in source chapters (sequence from 1 to detected_source_last_chapter)
    source_set = set(source_sorted)
    missing_gaps = []
    if detected_source_last_chapter > 0:
        missing_gaps = sorted(list(set(range(1, detected_source_last_chapter + 1)) - source_set))
        
    warnings = []
    if missing_gaps:
        warnings.append(f"Gaps detected in source chapters sequence: {len(missing_gaps)} chapters missing.")
        
    # Check duplicate chapters in input lists (if duplicates existed in original raw lists)
    # Since we set-converted them inside this function, we can check original lists if needed,
    # but the calling function can also handle duplicates check.
    
    status = "NEW_CHAPTERS_DETECTED" if new_chapters_to_ingest else "NO_NEW_CHAPTERS_FOUND"
    
    return {
        "status": status,
        "current_last_chapter": current_last_chapter,
        "detected_source_last_chapter": detected_source_last_chapter,
        "new_chapters_to_ingest": new_chapters_to_ingest,
        "skipped_existing_chapters": skipped_existing_chapters,
        "missing_gaps": missing_gaps,
        "warnings": warnings,
        "write_required": False
    }
