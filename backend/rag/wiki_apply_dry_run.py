"""
Wiki Apply Dry-Run Module
Provides dry-run validation, payload building, and duplicate detection
for importing wiki candidates into wiki_entries without modifying the database.
"""

import re
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

VALID_WIKI_CATEGORIES = ["Nhân vật", "Sinh vật", "Thế lực", "Vật phẩm", "Địa điểm"]

def generate_slug(title: str) -> str:
    """Generates a URL-friendly slug from a title string."""
    if not title:
        return ""
    # Lowercase and strip whitespace
    val = title.lower().strip()
    # Remove accents/diacritics
    val = unicodedata.normalize('NFKD', val)
    val = "".join(c for c in val if not unicodedata.combining(c))
    # Replace common Vietnamese characters manually if necessary, or let normalization handle it
    # NFKD removes diacritics from Vietnamese characters (đ -> d, etc.)
    # However, let's explicitly map 'đ' to 'd' because unicodedata doesn't decompose 'đ'
    val = val.replace('đ', 'd')
    # Replace non-alphanumeric characters with hyphens
    val = re.sub(r'[^\w\s-]', '', val)
    # Replace whitespace/underscores with hyphens
    val = re.sub(r'[\s_]+', '-', val)
    # Replace multiple hyphens with a single one
    val = re.sub(r'-+', '-', val)
    return val.strip('-')

def build_wiki_entry_payload(candidate: dict) -> dict:
    """Transforms a wiki candidate dictionary into a wiki_entries DB payload."""
    title = str(candidate.get("entity_name") or "").strip()
    category = str(candidate.get("entity_type") or "Sinh vật").strip()
    
    # Fallback to category normalization
    if category not in VALID_WIKI_CATEGORIES:
        from rag.wiki_candidate_builder import map_entity_type_to_wiki_category
        category = map_entity_type_to_wiki_category(category)
        
    summary = str(candidate.get("summary") or "").strip()
    content = str(candidate.get("content") or "").strip()
    
    aliases = candidate.get("aliases")
    if not isinstance(aliases, list):
        aliases = []
        
    slug = generate_slug(title)
    
    return {
        "title": title,
        "category": category,
        "slug": slug,
        "summary": summary,
        "content": content,
        "tags": aliases,
        "is_main_character": False,
        "sort_order": 999
    }

def validate_wiki_entry_payload(payload: dict) -> dict:
    """Validates schema requirements of a wiki_entries payload."""
    errors = []
    
    title = payload.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        errors.append("Field 'title' is required and must be a non-empty string.")
        
    category = payload.get("category")
    if not category or category not in VALID_WIKI_CATEGORIES:
        errors.append(f"Field 'category' must be one of {VALID_WIKI_CATEGORIES}.")
        
    slug = payload.get("slug")
    if not slug or not isinstance(slug, str) or not slug.strip():
        errors.append("Field 'slug' is required and must be a non-empty string.")
        
    summary = payload.get("summary")
    if not summary or not isinstance(summary, str) or not summary.strip():
        errors.append("Field 'summary' is required and must be a non-empty string.")
        
    content = payload.get("content")
    if not content or not isinstance(content, str) or not content.strip():
        errors.append("Field 'content' is required and must be a non-empty string.")
        
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def detect_existing_wiki_entry(supabase, title: str, slug: str) -> dict:
    """Checks the database to identify if a wiki entry with matching title or slug already exists."""
    if not supabase:
        return {"duplicate_title": False, "duplicate_slug": False, "exists": False}
        
    try:
        # Check title
        title_res = supabase.table("wiki_entries").select("id, title, slug").eq("title", title).execute()
        dup_title = bool(title_res.data)
        
        # Check slug
        slug_res = supabase.table("wiki_entries").select("id, title, slug").eq("slug", slug).execute()
        dup_slug = bool(slug_res.data)
        
        existing_entry = None
        if dup_title:
            existing_entry = title_res.data[0]
        elif dup_slug:
            existing_entry = slug_res.data[0]
            
        return {
            "duplicate_title": dup_title,
            "duplicate_slug": dup_slug,
            "exists": dup_title or dup_slug,
            "existing_entry": existing_entry
        }
    except Exception as e:
        print(f"Warning: detect_existing_wiki_entry failed: {e}")
        return {"duplicate_title": False, "duplicate_slug": False, "exists": False}

def is_unsafe_content(text: str) -> bool:
    """Checks if text contains test/mock/placeholder keywords."""
    if not text:
        return False
    t = text.lower()
    blacklist = [
        "smoke test",
        "test",
        "mock",
        "placeholder",
        "todo",
        "chỉ dùng để kiểm thử",
        "not applied to wiki_entries",
        "needs human fill"
    ]
    for item in blacklist:
        if item in t:
            return True
    return False

def check_unsafe_candidate(candidate: dict) -> bool:
    """Checks if any candidate metadata fields contain unsafe content."""
    for field in ["entity_name", "summary", "content", "notes"]:
        if is_unsafe_content(candidate.get(field)):
            return True

    aliases = candidate.get("aliases") or []
    for alias in aliases:
        if is_unsafe_content(alias):
            return True

    return False

def build_apply_plan(candidates: list[dict], supabase=None) -> dict:
    """Evaluates candidates and constructs a comprehensive dry-run import plan with safety gates."""
    plan_entries = []
    
    total = 0
    eligible_count = 0
    ineligible_count = 0
    duplicate_count = 0
    
    for candidate in candidates:
        total += 1
        corr_id = str(candidate.get("correction_id") or "")
        entity_name = str(candidate.get("entity_name") or "")
        
        summary = str(candidate.get("summary") or "").strip()
        content = str(candidate.get("content") or "").strip()
        
        # 1. Skip if empty summary/content
        if not summary or not content:
            ineligible_count += 1
            plan_entries.append({
                "correction_id": corr_id,
                "entity_name": entity_name,
                "eligible": False,
                "reason": "needs_human_fill",
                "payload": None
            })
            continue
            
        # 2. Check for unsafe test/mock/placeholder content
        if check_unsafe_candidate(candidate):
            ineligible_count += 1
            plan_entries.append({
                "correction_id": corr_id,
                "entity_name": entity_name,
                "eligible": False,
                "reason": "unsafe_test_or_placeholder_content",
                "payload": None
            })
            continue

        # 3. Human Review Gate
        human_review_req = candidate.get("human_review_required", True)
        canon_reviewed = candidate.get("canon_reviewed", False)
        if human_review_req is True and canon_reviewed is not True:
            ineligible_count += 1
            plan_entries.append({
                "correction_id": corr_id,
                "entity_name": entity_name,
                "eligible": False,
                "reason": "canon_review_required",
                "payload": None
            })
            continue

        # 4. Build payload
        payload = build_wiki_entry_payload(candidate)
        
        # 5. Validate payload
        val_res = validate_wiki_entry_payload(payload)
        if not val_res["valid"]:
            ineligible_count += 1
            plan_entries.append({
                "correction_id": corr_id,
                "entity_name": entity_name,
                "eligible": False,
                "reason": f"validation_error: {', '.join(val_res['errors'])}",
                "payload": payload
            })
            continue
            
        # 6. Check duplicates in DB if connection provided
        if supabase:
            dup_res = detect_existing_wiki_entry(supabase, payload["title"], payload["slug"])
            if dup_res["exists"]:
                duplicate_count += 1
                ineligible_count += 1
                
                reason = "duplicate_title" if dup_res["duplicate_title"] else "duplicate_slug"
                plan_entries.append({
                    "correction_id": corr_id,
                    "entity_name": entity_name,
                    "eligible": False,
                    "reason": reason,
                    "payload": payload,
                    "existing_entry": dup_res["existing_entry"]
                })
                continue
                
        # If all checks pass, it's eligible
        eligible_count += 1
        plan_entries.append({
            "correction_id": corr_id,
            "entity_name": entity_name,
            "eligible": True,
            "payload": payload
        })
        
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_candidates": total,
            "eligible_count": eligible_count,
            "ineligible_count": ineligible_count,
            "duplicate_count": duplicate_count
        },
        "plan_entries": plan_entries
    }
