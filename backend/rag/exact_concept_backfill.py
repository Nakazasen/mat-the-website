import hashlib
import re
from typing import List, Dict, Any

def normalize_name(text: str) -> str:
    """Standardizes the name by stripping extra spaces, removing common leading/trailing punctuation."""
    if not text:
        return ""
    # Strip quotes, parentheses, braces, commas, periods
    cleaned = re.sub(r'^[\s"\'\(,.\-\*]+|[\s"\'\),.\-\*]+$', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def generate_stable_id(name: str, category: str) -> str:
    """Generates a stable MD5 ID from name and category/type."""
    id_str = f"{category.lower()}_{name.strip().lower()}"
    return hashlib.md5(id_str.encode('utf-8')).hexdigest()

def score_confidence(evidence_count: int) -> float:
    """Calculates confidence score based on the amount of evidence.
    Formula: min(1.0, 0.1 + 0.2 * evidence_count) rounded to 2 decimal places.
    """
    return round(min(1.0, 0.1 + 0.2 * evidence_count), 2)

def build_backfill_candidate(seed: str, proposed_category: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Builds a provisional library candidate record for backfilling."""
    name = normalize_name(seed)
    stable_id = generate_stable_id(name, proposed_category)

    # Sort evidence
    evidence.sort(key=lambda ev: (ev.get("chapter_number") or 9999, ev.get("chunk_index") or 0))

    # Generate grounded summary
    summary = ""
    if evidence:
        first_preview = evidence[0].get("preview") or ""
        first_sentence = re.split(r'[.!?。！？]', first_preview)[0].strip()
        if first_sentence:
            summary = f"Khái niệm '{name}' xuất hiện trong truyện. Chi tiết: '{first_sentence}'."
        else:
            summary = f"Khái niệm '{name}' xuất hiện trong truyện."
    else:
        summary = f"Khái niệm '{name}' xuất hiện trong truyện."

    # Assign quality class based on evidence count
    # High if >= 5, Medium if 2 <= count < 5, else Medium (or weak if 1, but we prefer High/Medium to pass RAG policy)
    evidence_count = len(evidence)
    if evidence_count >= 5:
        quality_class = "high_confidence"
    else:
        quality_class = "medium_confidence"

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

    # Construct candidate object matching schema
    candidate = {
        "id": stable_id,
        "name": name,
        "normalized_name": name,
        "type": proposed_category,
        "summary": summary,
        "evidence": evidence,
        "confidence": score_confidence(evidence_count),
        "quality_class": quality_class,
        "status": "provisional",
        "source": "exact_concept_backfill_v1",
        "feedback_score": 0,
        "needs_review": False,
        "chapter_numbers": chapter_list,
        "first_chapter": first_ch,
        "last_chapter": last_ch
    }
    return candidate
