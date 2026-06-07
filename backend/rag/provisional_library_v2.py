# provisional_library_v2.py
import re
import hashlib
from typing import List, Dict, Any
from backend.rag.library_taxonomy_v2 import (
    classify_term_v2,
    is_rejected_v2,
    TAXONOMY_V2_LABELS
)

STARTER_WORDS = {
    "Khi", "Nhưng", "Nếu", "Tuy", "Bởi", "Vì", "Thế", "Vậy", "Sau", "Trong", "Tại", 
    "Từ", "Cho", "Đến", "Với", "Như", "Các", "Những", "Một", "Hai", "Ba", "Ngày", 
    "Lúc", "Tuy nhiên", "Đột nhiên", "Bỗng nhiên", "Cô", "Anh", "Hắn", "Nàng", "Tôi"
}

def normalize_name(text: str) -> str:
    """Standardizes the name by stripping extra spaces, removing common leading/trailing punctuation."""
    if not text:
        return ""
    cleaned = re.sub(r'^[\s"\'\(,.\-\*]+|[\s"\'\),.\-\*]+$', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned

def extract_candidate_terms_v2(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Scans chunks to extract candidate terms applying Taxonomy V2 rules and noise filters."""
    candidates = []
    
    UPPER_CHARS = "A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĂĐĨŨƠƯẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲÝỴỶỸ"
    LOWER_CHARS = "a-zàáâãèéêìíòóôõùúýăđĩũơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳýỵỷỹ"
    
    # Pre-compiled regex patterns for heuristic keywords extraction
    heuristic_patterns = [
        (r'zombie cấp \d+', "zombie_species"),
        (r'tang thi cấp \d+', "zombie_species"),
        (r'tinh thể zombie', "crystal_core"),
        (r'tinh thạch khai phá', "crystal_core"),
        (r'tinh thạch nguyện ước', "crystal_core"),
        (rf'sách kỹ năng [{UPPER_CHARS}][{LOWER_CHARS}]*(?:\s+[{UPPER_CHARS}][{LOWER_CHARS}]*)*', "skill_book"),
        (rf'dị năng [{LOWER_CHARS}{UPPER_CHARS}\s]+', "ability_skill"),
        (rf'kỹ năng [{LOWER_CHARS}{UPPER_CHARS}\s]+', "ability_skill"),
        (r'căn cứ Hi Vọng', "location_base"),
        (r'súng diệt quỷ', "weapon")
    ]
    
    for chunk in chunks:
        content = chunk.get("content_plain") or chunk.get("content") or ""
        chapter_number = chunk.get("chapter_number")
        chapter_title = chunk.get("chapter_title")
        chunk_index = chunk.get("chunk_index")
        content_hash = chunk.get("content_hash")
        
        if not content:
            continue
            
        sentences = [s.strip() for s in re.split(r'[.!?。！？]\s+', content) if s.strip()]
        
        # 1. Proper nouns extraction (2+ capitalized words)
        proper_nouns = re.findall(rf'\b[{UPPER_CHARS}][{LOWER_CHARS}]*(?:\s+[{UPPER_CHARS}][{LOWER_CHARS}]*)+\b', content)
        for name in proper_nouns:
            words = name.split()
            # Clean up starters (e.g. "Khi Hàn Phong" -> "Hàn Phong")
            if len(words) > 2 and words[0] in STARTER_WORDS:
                name = " ".join(words[1:])
                
            name_clean = normalize_name(name)
            if is_rejected_v2(name_clean):
                continue
                
            # Find context sentence
            context_sentence = ""
            for s in sentences:
                if name_clean in s:
                    context_sentence = s
                    break
            if not context_sentence:
                context_sentence = content[:200]
                
            t_type = classify_term_v2(name_clean, context_sentence)
            
            candidates.append({
                "name": name_clean,
                "type": t_type,
                "context": context_sentence,
                "evidence": {
                    "chapter_number": chapter_number,
                    "chapter_title": chapter_title,
                    "chunk_index": chunk_index,
                    "content_hash": content_hash,
                    "preview": context_sentence[:200] + "..." if len(context_sentence) > 200 else context_sentence
                }
            })
            
        # 2. Heuristic keywords phrase extraction (lowercase item/ability terms)
        for pattern, t_type in heuristic_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for m in matches:
                m_clean = normalize_name(m)
                if is_rejected_v2(m_clean):
                    continue
                context_sentence = ""
                for s in sentences:
                    if m.lower() in s.lower():
                        context_sentence = s
                        break
                candidates.append({
                    "name": m_clean,
                    "type": t_type,
                    "context": context_sentence or content[:200],
                    "evidence": {
                        "chapter_number": chapter_number,
                        "chapter_title": chapter_title,
                        "chunk_index": chunk_index,
                        "content_hash": content_hash,
                        "preview": context_sentence[:200] + "..." if len(context_sentence) > 200 else context_sentence
                    }
                })

        # 3. Events extraction
        event_verbs = ["xuất hiện", "giết zombie", "giết chết con zombie", "cứu", "nhận được tinh thể", "tiến vào", "tấn công", "phát hiện", "thăng cấp"]
        for s in sentences:
            found_names = [name for name in proper_nouns if name in s]
            if found_names:
                for verb in event_verbs:
                    if verb in s.lower():
                        primary_name = normalize_name(found_names[0])
                        event_name = f"{primary_name} {verb}"
                        if is_rejected_v2(event_name):
                            continue
                        candidates.append({
                            "name": event_name,
                            "type": "event",
                            "context": s,
                            "evidence": {
                                "chapter_number": chapter_number,
                                "chapter_title": chapter_title,
                                "chunk_index": chunk_index,
                                "content_hash": content_hash,
                                "preview": s[:200] + "..." if len(s) > 200 else s
                            }
                        })
                        break

        # 4. Relationships extraction
        rel_keywords = ["sếp", "trợ lý", "cứu", "giúp", "đồng đội", "đối thủ", "kẻ thù", "bạn"]
        for s in sentences:
            found_names = sorted(list(set([normalize_name(name) for name in proper_nouns if name in s])))
            # Filter names
            found_names = [name for name in found_names if not is_rejected_v2(name)]
            if len(found_names) >= 2:
                for rkw in rel_keywords:
                    if rkw in s.lower():
                        rel_name = f"{found_names[0]} và {found_names[1]}"
                        candidates.append({
                            "name": rel_name,
                            "type": "relationship",
                            "context": s,
                            "evidence": {
                                "chapter_number": chapter_number,
                                "chapter_title": chapter_title,
                                "chunk_index": chunk_index,
                                "content_hash": content_hash,
                                "preview": s[:200] + "..." if len(s) > 200 else s
                            }
                        })
                        break
                        
    return candidates

def score_confidence_v2(record: Dict[str, Any]) -> float:
    """Calculates confidence score based on the amount of evidence.
    
    Formula: min(1.0, 0.1 + 0.2 * len(evidence)) rounded to 2 decimal places.
    """
    evidence_list = record.get("evidence", [])
    return round(min(1.0, 0.1 + 0.2 * len(evidence_list)), 2)

def score_record_quality_v2(record: Dict[str, Any]) -> Dict[str, Any]:
    """Scores the quality of a record and identifies issues/discard reasons for V2."""
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
    elif is_rejected_v2(name):
        discard_reasons.append("rejected_noise")
        
    if not summary or summary.strip() == "":
        discard_reasons.append("empty_summary")
        
    if not evidence or len(evidence) == 0:
        discard_reasons.append("no_evidence")
        
    if record.get("is_weaker_duplicate"):
        discard_reasons.append("duplicate_weaker")
        
    # Base score scaled to 10
    score += confidence * 10.0
    
    # Evidence count bonus
    evidence_count = len(evidence)
    score += min(10.0, evidence_count * 2.0)
    
    # Type specific heuristics
    if t_type in ["organization_faction", "location_base", "ability_skill", "zombie_species", "crystal_core"] and evidence_count >= 2:
        score += 2.0
        reasons.append("valuable_type_bonus")
        
    if t_type in ["event", "relationship"]:
        if len(summary.split()) > 8:
            score += 1.0
            reasons.append("detailed_summary_bonus")
            
    if t_type == "character":
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

def classify_quality_v2(record: Dict[str, Any]) -> str:
    """Classifies record quality into high_confidence, medium_confidence, weak_evidence, or discard_candidate."""
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

def build_provisional_record_v2(term: Dict[str, Any], evidence_list: List[Dict[str, Any]], min_evidence: int = 2) -> Dict[str, Any]:
    """Builds a provisional record dict matching the V2 schema."""
    name = term["name"]
    t_type = term["type"]
    
    id_str = f"{t_type}_{name.lower()}"
    stable_id = hashlib.md5(id_str.encode('utf-8')).hexdigest()
    
    summary = ""
    if evidence_list:
        first_preview = evidence_list[0].get("preview") or ""
        first_sentence = re.split(r'[.!?。！？]', first_preview)[0].strip()
        if first_sentence:
            summary = f"[{TAXONOMY_V2_LABELS.get(t_type, t_type)}] '{name}' xuất hiện trong truyện. Chi tiết: '{first_sentence}'."
        else:
            summary = f"[{TAXONOMY_V2_LABELS.get(t_type, t_type)}] '{name}' xuất hiện trong truyện."
    else:
        summary = f"[{TAXONOMY_V2_LABELS.get(t_type, t_type)}] '{name}' xuất hiện trong truyện."
        
    status = "provisional" if len(evidence_list) >= min_evidence else "weak_evidence"
    
    record = {
        "id": stable_id,
        "name": name,
        "type": t_type,
        "summary": summary,
        "evidence": evidence_list,
        "confidence": 0.0,
        "status": status,
        "source": "story_chunks_auto_extract_v2",
        "feedback_score": 0,
        "needs_review": False,
        "is_weaker_duplicate": False
    }
    record["confidence"] = score_confidence_v2(record)
    
    # Calculate quality metrics
    q_info = score_record_quality_v2(record)
    record["quality_score"] = q_info["quality_score"]
    record["reasons"] = q_info["reasons"]
    record["discard_reasons"] = q_info["discard_reasons"]
    record["quality_class"] = classify_quality_v2(record)
    
    return record

def merge_duplicate_records_v2(records: List[Dict[str, Any]], min_evidence: int = 2) -> List[Dict[str, Any]]:
    """Groups records by name and type, merging their evidence and updating confidence/status."""
    merged = {}
    
    for r in records:
        key = (r["name"].lower(), r["type"])
        if key not in merged:
            merged[key] = {
                "id": r["id"],
                "name": r["name"],
                "type": r["type"],
                "summary": r["summary"],
                "evidence": [],
                "confidence": 0.0,
                "status": "provisional",
                "source": r["source"],
                "feedback_score": 0,
                "needs_review": r["needs_review"],
                "is_weaker_duplicate": False
            }
            
        seen_hashes = {ev["content_hash"] for ev in merged[key]["evidence"] if ev.get("content_hash")}
        for ev in r["evidence"]:
            h = ev.get("content_hash")
            if not h or h not in seen_hashes:
                merged[key]["evidence"].append(ev)
                if h:
                    seen_hashes.add(h)
                    
    results = []
    for r in merged.values():
        # Re-score confidence
        r["confidence"] = score_confidence_v2(r)
        
        # Sort evidence by chapter_number and chunk_index
        r["evidence"].sort(key=lambda ev: (ev.get("chapter_number") or 9999, ev.get("chunk_index") or 0))
        
        # Update status if evidence is below min_evidence
        if len(r["evidence"]) < min_evidence:
            r["status"] = "weak_evidence"
            
        # Recalculate quality metrics
        q_info = score_record_quality_v2(r)
        r["quality_score"] = q_info["quality_score"]
        r["reasons"] = q_info["reasons"]
        r["discard_reasons"] = q_info["discard_reasons"]
        r["quality_class"] = classify_quality_v2(r)
        
        results.append(r)
        
    return results
