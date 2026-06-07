import re
import hashlib
from typing import List, Dict, Any

# Common Vietnamese sentence starters to exclude from proper noun extractions
STARTER_WORDS = {
    "Khi", "Nhưng", "Nếu", "Tuy", "Bởi", "Vì", "Thế", "Vậy", "Sau", "Trong", "Tại", 
    "Từ", "Cho", "Đến", "Với", "Như", "Các", "Những", "Một", "Hai", "Ba", "Ngày", 
    "Lúc", "Tuy nhiên", "Đột nhiên", "Bỗng nhiên", "Cô", "Anh", "Hắn", "Nàng", "Tôi"
}

def normalize_name(text: str) -> str:
    """Standardizes the name by stripping extra spaces, removing common leading/trailing punctuation."""
    if not text:
        return ""
    # Strip quotes, parentheses, braces, commas, periods
    cleaned = re.sub(r'^[\s"\'\(,.\-\*]+|[\s"\'\),.\-\*]+$', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def classify_term(name: str, context: str) -> str:
    """Classifies a term into entity, item, ability, location, faction, event, relationship."""
    n_lower = name.lower()
    c_lower = context.lower()
    
    # 1. Ability keywords
    ability_kws = ["dị năng", "kỹ năng", "chiêu thức", "băng thứ", "băng giáp", "dịch năng"]
    if any(kw in n_lower for kw in ability_kws) or (any(kw in c_lower for kw in ability_kws) and any(kw in n_lower for kw in ["băng", "hỏa", "lôi", "thổ", "không gian", "tốc độ", "sức mạnh"])):
        return "ability"
        
    # 2. Item keywords
    item_kws = ["tinh thể", "vật phẩm", "trang bị", "vũ khí", "dịch thể", "hộp thực phẩm", "thẻ triệu hồi", "thẻ giao dịch", "thẻ bài"]
    if any(kw in n_lower for kw in item_kws):
        return "item"
    if n_lower == "thẻ" or any(kw in n_lower for kw in ["thẻ", "vũ khí", "súng", "dao"]):
        return "item"
        
    # 3. Location keywords
    loc_kws = ["căn cứ", "thành phố", "trường học", "bệnh viện", "tòa nhà", "căng tin", "phòng điện", "nhà kho", "tầng hầm", "khu vực", "địa điểm", "phòng điều hành"]
    if any(kw in n_lower for kw in loc_kws):
        return "location"
        
    # 4. Faction keywords
    fac_kws = ["công ty", "quân đội", "tổ chức", "thế lực", "bang hội", "đại thiên thần", "phòng quản lý"]
    if any(kw in n_lower for kw in fac_kws) or n_lower == "đội" or n_lower.startswith("đội săn") or n_lower.startswith("đội tuần"):
        return "faction"
        
    # 5. Relationship keywords
    rel_kws = ["đồng đội", "đối thủ", "kẻ thù", "bạn bè", "sếp", "trợ lý"]
    if any(kw in n_lower for kw in rel_kws) or (any(kw in c_lower for kw in rel_kws) and " và " in name):
        return "relationship"
        
    # 6. Event keywords
    event_kws = ["xuất hiện", "giết", "cứu", "nhận được", "tiến vào", "tấn công", "phát hiện", "thăng cấp"]
    if any(kw in n_lower for kw in event_kws):
        return "event"
        
    return "entity"

def extract_candidate_terms(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Scans chunks to extract candidate terms (proper nouns, keyword matches, events, relationships)."""
    candidates = []
    
    for chunk in chunks:
        content = chunk.get("content_plain") or chunk.get("content") or ""
        chapter_number = chunk.get("chapter_number")
        chapter_title = chunk.get("chapter_title")
        chunk_index = chunk.get("chunk_index")
        content_hash = chunk.get("content_hash")
        
        if not content:
            continue
            
        # Split chunk into sentences for context mapping
        sentences = [s.strip() for s in re.split(r'[.!?。！？]\s+', content) if s.strip()]
        
        # 1. Proper nouns extraction (2+ capitalized words)
        proper_nouns = re.findall(r'\b[A-ZÀ-Ỹ][a-zà-ỹ]*(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]*)+\b', content)
        for name in proper_nouns:
            words = name.split()
            # Clean up starters (e.g. "Khi Hàn Phong" -> "Hàn Phong")
            if len(words) > 2 and words[0] in STARTER_WORDS:
                name = " ".join(words[1:])
                
            name_clean = normalize_name(name)
            if not name_clean or len(name_clean.split()) < 2:
                continue
                
            # Find context sentence
            context_sentence = ""
            for s in sentences:
                if name_clean in s:
                    context_sentence = s
                    break
            if not context_sentence:
                context_sentence = content[:200]
                
            candidates.append({
                "name": name_clean,
                "type": "proper_noun", # will classify below
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
        keywords_phrases = [
            (r'tinh thể zombie', "item"),
            (r'thẻ triệu hồi', "item"),
            (r'dị năng băng', "ability"),
            (r'căng tin', "location"),
            (r'phòng điều hành', "location")
        ]
        for pattern, t_type in keywords_phrases:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for m in matches:
                m_clean = normalize_name(m)
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
        # e.g., Sentence contains proper name + action verb
        event_verbs = ["xuất hiện", "giết zombie", "giết chết con zombie", "cứu", "nhận được tinh thể", "tiến vào", "tấn công", "phát hiện", "thăng cấp"]
        for s in sentences:
            found_names = [name for name in proper_nouns if name in s]
            if found_names:
                for verb in event_verbs:
                    if verb in s.lower():
                        # Extract event
                        primary_name = found_names[0]
                        event_name = f"{primary_name} {verb}"
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
        # e.g., Sentence contains two proper names + relationship keyword
        rel_keywords = ["sếp", "trợ lý", "cứu", "giúp", "đồng đội", "đối thủ", "kẻ thù", "bạn"]
        for s in sentences:
            found_names = sorted(list(set([normalize_name(name) for name in proper_nouns if name in s])))
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

def score_confidence(record: Dict[str, Any]) -> float:
    """Calculates confidence score based on the amount of evidence.
    
    Formula: min(1.0, 0.1 + 0.2 * len(evidence)) rounded to 2 decimal places.
    """
    evidence_list = record.get("evidence", [])
    return round(min(1.0, 0.1 + 0.2 * len(evidence_list)), 2)

def build_provisional_record(term: Dict[str, Any], evidence_list: List[Dict[str, Any]], min_evidence: int = 2) -> Dict[str, Any]:
    """Builds a provisional record dict matching the requested schema."""
    name = term["name"]
    t_type = term["type"]
    if t_type == "proper_noun":
        t_type = classify_term(name, term["context"])
        
    # Generate stable ID from name and type
    id_str = f"{t_type}_{name.lower()}"
    stable_id = hashlib.md5(id_str.encode('utf-8')).hexdigest()
    
    # Formulate a safe, grounded summary based on evidence preview
    summary = ""
    if evidence_list:
        first_preview = evidence_list[0].get("preview") or ""
        # Clean preview to extract first sentence
        first_sentence = re.split(r'[.!?。！？]', first_preview)[0].strip()
        if first_sentence:
            summary = f"Thực thể '{name}' xuất hiện trong truyện. Chi tiết: '{first_sentence}'."
        else:
            summary = f"Thực thể '{name}' xuất hiện trong truyện."
    else:
        summary = f"Thực thể '{name}' xuất hiện trong truyện."
        
    status = "provisional" if len(evidence_list) >= min_evidence else "weak_evidence"
    
    record = {
        "id": stable_id,
        "name": name,
        "type": t_type,
        "summary": summary,
        "evidence": evidence_list,
        "confidence": 0.0,
        "status": status,
        "source": "story_chunks_auto_extract",
        "feedback_score": 0,
        "needs_review": False
    }
    record["confidence"] = score_confidence(record)
    return record

def merge_duplicate_records(records: List[Dict[str, Any]], min_evidence: int = 2) -> List[Dict[str, Any]]:
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
                "needs_review": r["needs_review"]
            }
            
        # Combine evidence, avoiding duplicates by content_hash
        seen_hashes = {ev["content_hash"] for ev in merged[key]["evidence"] if ev.get("content_hash")}
        for ev in r["evidence"]:
            h = ev.get("content_hash")
            if not h or h not in seen_hashes:
                merged[key]["evidence"].append(ev)
                if h:
                    seen_hashes.add(h)
                    
    results = list(merged.values())
    for r in results:
        # Re-score confidence
        r["confidence"] = score_confidence(r)
        
        # Sort evidence by chapter_number and chunk_index
        r["evidence"].sort(key=lambda ev: (ev.get("chapter_number") or 9999, ev.get("chunk_index") or 0))
        
        # Update status if evidence is below min_evidence
        if len(r["evidence"]) < min_evidence:
            r["status"] = "weak_evidence"
            
    return results
