import re
import hashlib
from typing import Dict, List, Any
from backend.rag.provisional_library import normalize_name

# Vietnamese action verbs to detect clauses/actions in entity/item/ability/location/faction names
ACTION_VERBS = {
    "giết", "cứu", "tiến vào", "tấn công", "phát hiện", "thăng cấp", "chạy", "nhảy", "ăn", "uống",
    "nói", "hỏi", "đi", "đứng", "nằm", "ngồi", "thấy", "nghe", "biết", "nghĩ", "muốn", "cần",
    "nhận được", "tiêu diệt", "bắt đầu", "kết thúc", "xuất hiện", "tìm thấy", "nhặt được", "sử dụng"
}

def is_noise_name(name: str) -> bool:
    """Checks if a name is likely noise (too short, too long, contains junk, or is a clause)."""
    if not name:
        return True
    
    name_stripped = name.strip()
    
    # 1. Too short
    if len(name_stripped) < 2:
        return True
        
    # 2. Too long (more than 12 words)
    words = name_stripped.split()
    if len(words) > 12:
        return True
        
    # 3. Contains junk characters
    junk_symbols = set("@#$%^&*_+=<>|\\~`[]{}")
    if any(char in junk_symbols for char in name_stripped):
        return True
        
    # 4. Looks like a clause/action rather than a proper noun
    first_word_lower = words[0].lower()
    if first_word_lower in ACTION_VERBS:
        return True
        
    # If the name contains lowercase verbs and has many lowercase words, it's likely a clause.
    lowercase_words = [w for w in words if w.islower()]
    if len(lowercase_words) / len(words) >= 0.5:
        if any(verb in name_stripped.lower() for verb in ACTION_VERBS):
            return True
            
    return False

def has_valid_name(record: Dict[str, Any]) -> bool:
    """Returns True if the record has a valid (non-noise) name."""
    name = record.get("name", "")
    return not is_noise_name(name)

def score_record_quality(record: Dict[str, Any]) -> Dict[str, Any]:
    """Scores the quality of a record and identifies issues/discard reasons."""
    name = record.get("name", "")
    t_type = record.get("type", "")
    summary = record.get("summary", "")
    evidence = record.get("evidence", [])
    confidence = record.get("confidence", 0.0)
    
    discard_reasons = []
    reasons = []
    score = 0.0
    
    # Check baseline discard reasons
    if not name or len(name.strip()) < 2:
        discard_reasons.append("name_too_short")
    elif len(name.split()) > 12:
        discard_reasons.append("name_too_long")
    elif is_noise_name(name):
        discard_reasons.append("noise_name")
        
    if not summary or summary.strip() == "":
        discard_reasons.append("empty_summary")
        
    if not evidence or len(evidence) == 0:
        discard_reasons.append("no_evidence")
        
    if record.get("is_weaker_duplicate"):
        discard_reasons.append("duplicate_weaker")
        
    # Calculate score
    # Base score is based on confidence (0.0 to 1.0) -> scaled to 10
    score += confidence * 10.0
    
    # Evidence count bonus: each evidence counts for 2 points, cap at 10
    evidence_count = len(evidence)
    score += min(10.0, evidence_count * 2.0)
    
    # Type specific heuristics
    if t_type in ["faction", "location", "ability"] and evidence_count >= 2:
        score += 2.0
        reasons.append("valuable_type_bonus")
        
    if t_type in ["event", "relationship"]:
        if len(summary.split()) > 8:
            score += 1.0
            reasons.append("detailed_summary_bonus")
            
    if t_type == "entity":
        words = name.split()
        if all(w[0].isupper() for w in words if w and w[0].isalpha()):
            score += 1.0
            reasons.append("proper_noun_casing_bonus")
            
    score = round(score, 2)
    
    return {
        "quality_score": score,
        "reasons": reasons,
        "discard_reasons": discard_reasons
    }

def classify_quality(record: Dict[str, Any]) -> str:
    """Classifies a record into high_confidence, medium_confidence, weak_evidence, or discard_candidate."""
    discard_reasons = record.get("discard_reasons", [])
    if discard_reasons:
        return "discard_candidate"
        
    evidence_count = len(record.get("evidence", []))
    confidence = record.get("confidence", 0.0)
    
    if evidence_count >= 3 and confidence >= 0.7:
        return "high_confidence"
    elif evidence_count >= 2 and confidence >= 0.5:
        return "medium_confidence"
    elif evidence_count == 1:
        return "weak_evidence"
        
    return "weak_evidence"

def rank_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Scores, deduplicates, classifies, and ranks a list of records."""
    # First pass: clear duplicate flag
    for r in records:
        r["is_weaker_duplicate"] = False
        
    # Group by normalized name
    groups = {}
    for r in records:
        norm = normalize_name(r.get("name", "")).lower()
        if not norm:
            continue
        if norm not in groups:
            groups[norm] = []
        groups[norm].append(r)
        
    # Deduplicate: find weaker duplicates for each group
    for norm, grp in groups.items():
        if len(grp) <= 1:
            continue
            
        def get_priority(rec):
            name = rec.get("name", "")
            is_noise = is_noise_name(name)
            evidence_count = len(rec.get("evidence", []))
            confidence = rec.get("confidence", 0.0)
            
            t_type = rec.get("type", "")
            type_prio = 0
            if t_type in ["item", "ability", "location", "faction", "relationship", "event"]:
                type_prio = 1
            return (not is_noise, confidence, evidence_count, type_prio)
            
        grp.sort(key=get_priority, reverse=True)
        
        # Mark all but the first as weaker duplicates
        for r in grp[1:]:
            r["is_weaker_duplicate"] = True
            
    # Second pass: score all records and apply quality class
    scored_records = []
    for r in records:
        q_info = score_record_quality(r)
        r_copy = dict(r)
        r_copy["quality_score"] = q_info["quality_score"]
        r_copy["reasons"] = q_info["reasons"]
        r_copy["discard_reasons"] = q_info["discard_reasons"]
        r_copy["quality_class"] = classify_quality(r_copy)
        scored_records.append(r_copy)
        
    # Stable sort by name ascending, then by quality priority descending
    scored_records.sort(key=lambda x: x.get("name", ""))
    scored_records.sort(key=lambda x: (
        4 if x["quality_class"] == "high_confidence" else
        3 if x["quality_class"] == "medium_confidence" else
        2 if x["quality_class"] == "weak_evidence" else 1,
        x.get("confidence", 0.0),
        len(x.get("evidence", [])),
        x.get("quality_score", 0.0)
    ), reverse=True)
    
    return scored_records

def build_quality_report(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates the quality report summarizing statistics of the records."""
    total = len(records)
    high_count = 0
    med_count = 0
    weak_count = 0
    discard_count = 0
    
    by_type = {}
    top_high_confidence = []
    top_discard_reasons = {}
    
    for r in records:
        q_class = r.get("quality_class", "weak_evidence")
        if q_class == "high_confidence":
            high_count += 1
            if len(top_high_confidence) < 10:
                top_high_confidence.append({
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "type": r.get("type"),
                    "confidence": r.get("confidence"),
                    "evidence_count": len(r.get("evidence", [])),
                    "quality_score": r.get("quality_score")
                })
        elif q_class == "medium_confidence":
            med_count += 1
        elif q_class == "weak_evidence":
            weak_count += 1
        elif q_class == "discard_candidate":
            discard_count += 1
            
        t_type = r.get("type", "unknown")
        by_type[t_type] = by_type.get(t_type, 0) + 1
        
        for reason in r.get("discard_reasons", []):
            top_discard_reasons[reason] = top_discard_reasons.get(reason, 0) + 1
            
    sorted_discard_reasons = dict(sorted(top_discard_reasons.items(), key=lambda item: item[1], reverse=True))
    
    return {
        "total": total,
        "high_confidence": high_count,
        "medium_confidence": med_count,
        "weak_evidence": weak_count,
        "discard_candidate": discard_count,
        "by_type": by_type,
        "top_high_confidence": top_high_confidence,
        "top_discard_reasons": sorted_discard_reasons
    }
