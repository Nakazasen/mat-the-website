"""
RAG Entity Drafts Module
Provides functionality to build reviewable entity profile drafts from story retrieval evidence.
"""

import re
from typing import Any, List, Dict

def normalize_entity_name(name: str) -> str:
    """Standardizes entity name by removing leading/trailing spaces and collapsing whitespace."""
    if not name:
        return ""
    return re.sub(r"\s+", " ", name.strip())

def guess_entity_type(entity_name: str, evidence_results: List[Dict[str, Any]]) -> str:
    """Guesses the entity type based on simple keyword heuristics from name and evidence content."""
    normalized_name = normalize_entity_name(entity_name)
    combined_text = (normalized_name + " " + " ".join([r.get("content_plain", "") or r.get("content", "") for r in evidence_results])).lower()
    
    # Priority keyword search
    if any(kw in combined_text for kw in ["nhân vật", "hắn", "nàng", "anh ta", "cô ta", "giám đốc", "lâm nhã vy", "trương hạo", "vương mạnh", "lý đức", "bàng lâm", "sếp"]):
        return "character"
    if any(kw in combined_text for kw in ["công ty", "tổ chức", "thế lực", "quân đội", "bang hội", "đại thiên thần"]):
        return "organization"
    if any(kw in combined_text for kw in ["vật phẩm", "trang bị", "vũ khí", "dịch thể", "hộp thực phẩm", "tinh thể"]):
        return "item"
    if any(kw in combined_text for kw in ["dị năng", "kỹ năng", "chiêu thức", "băng thứ", "băng giáp", "thăng cấp"]):
        return "ability"
    if any(kw in combined_text for kw in ["tòa nhà", "căng tin", "phòng điện", "nhà kho", "tầng hầm", "khu vực", "địa điểm"]):
        return "location"
    if any(kw in combined_text for kw in ["zombie", "quái vật", "đột biến", "sinh vật", "thực thể"]):
        return "creature"
    return "unknown"

def build_entity_draft(entity_name: str, evidence_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Builds a reviewable entity draft dictionary matching the required schema."""
    normalized_name = normalize_entity_name(entity_name)
    guessed_type = guess_entity_type(normalized_name, evidence_results)
    
    evidence = []
    for r in evidence_results:
        content = r.get("content_plain") or r.get("content") or ""
        preview = r.get("content_preview") or (content[:200] + "..." if len(content) > 200 else content)
        
        evidence.append({
            "chapter_number": r.get("chapter_number"),
            "chapter_title": r.get("chapter_title"),
            "chunk_index": r.get("chunk_index"),
            "preview": preview,
            "content_hash": r.get("content_hash")
        })
        
    return {
        "entity_name": normalized_name,
        "entity_type": guessed_type,
        "summary": "needs_review",
        "status": "needs_review",
        "evidence": evidence,
        "suggested_wiki_entry": {
            "title": normalized_name,
            "category": guessed_type if guessed_type != "unknown" else "needs_review",
            "content": "needs_review"
        },
        "notes": "Generated from retrieval evidence only; human review required."
    }

def build_missing_entity_drafts(entities: List[str], chapter_cap: int = 10, supabase: Any = None) -> List[Dict[str, Any]]:
    """Retrieves story evidence and builds draft profiles for a list of missing entities."""
    drafts = []
    from backend.rag.retrieval import search_story_chunks_hybrid_lexical
    
    for ent in entities:
        results = []
        if supabase:
            try:
                results = search_story_chunks_hybrid_lexical(
                    supabase=supabase,
                    query=ent,
                    chapter_cap=chapter_cap,
                    limit=5
                )
            except Exception as e:
                print(f"Warning: search failed for {ent}: {e}")
                
        draft = build_entity_draft(ent, results)
        drafts.append(draft)
        
    return drafts
