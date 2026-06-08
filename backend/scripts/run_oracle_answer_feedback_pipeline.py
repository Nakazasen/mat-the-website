#!/usr/bin/env python3
import os
import sys
import json
import argparse
import datetime
from typing import Dict, List, Any
from collections import Counter

# Ensure correct path resolution
backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
parent_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website"
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

try:
    from main import supabase
except ImportError:
    from backend.main import supabase

from backend.rag.oracle_feedback_classifier import classify_oracle_feedback, extract_entity_name_simple
from backend.rag.oracle_answer_patch_builder import build_oracle_patches, normalize_query_pattern

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def fetch_pending_feedbacks(limit: int = 1000) -> List[Dict[str, Any]]:
    try:
        res = supabase.table("rag_feedback").select("*").eq("status", "pending").limit(limit).execute()
        return res.data or []
    except Exception as e:
        print_safe(f"Error fetching pending feedbacks: {e}")
        return []

def fetch_existing_patches() -> List[Dict[str, Any]]:
    try:
        res = supabase.table("oracle_answer_effective_patches").select("*").execute()
        return res.data or []
    except Exception as e:
        print_safe(f"Error fetching existing oracle patches: {e}")
        return []

def build_feedback_summaries(feedbacks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Groups feedbacks by normalized query pattern and aggregates counts."""
    groups = {}
    for row in feedbacks:
        q_norm = normalize_query_pattern(row.get("question") or "")
        if not q_norm:
            continue
        if q_norm not in groups:
            groups[q_norm] = []
        groups[q_norm].append(row)

    summaries = []
    for q_norm, rows in groups.items():
        total = len(rows)
        # Classify each
        shallow = 0
        misclassification = 0
        irrelevant = 0
        missing = 0
        stale = 0
        wrong_summary = 0
        too_mech = 0
        unknown = 0
        
        comments = []
        for r in rows:
            cls = classify_oracle_feedback(
                question=r.get("question"),
                answer=r.get("answer"),
                user_feedback=r.get("user_comment"),
                source=r.get("source"),
                chapter_progress=r.get("chapter_progress")
            )
            it = cls["issue_type"]
            if it == "answer_quality_too_shallow":
                shallow += 1
            elif it == "intent_misclassification":
                misclassification += 1
            elif it == "irrelevant_entities":
                irrelevant += 1
            elif it == "missing_exact_entity":
                missing += 1
            elif it == "stale_cache":
                stale += 1
            elif it == "wrong_chapter_summary":
                wrong_summary += 1
            elif it == "too_mechanical":
                too_mech += 1
            else:
                unknown += 1

            if r.get("user_comment"):
                comments.append({
                    "comment": r.get("user_comment"),
                    "created_at": r.get("created_at")
                })

        comments_sorted = sorted(comments, key=lambda x: x.get("created_at") or "", reverse=True)[:5]

        summaries.append({
            "query_pattern": q_norm,
            "total_feedback": total,
            "shallow_count": shallow,
            "misclassification_count": misclassification,
            "irrelevant_count": irrelevant,
            "missing_entity_count": missing,
            "stale_cache_count": stale,
            "wrong_summary_count": wrong_summary,
            "too_mechanical_count": too_mech,
            "unknown_count": unknown,
            "top_comments": comments_sorted,
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    return summaries

def clear_oracle_cache_selectively(patterns_and_entities: List[str], dry_run: bool) -> int:
    if not patterns_and_entities:
        return 0
    try:
        # Fetch all cache entries
        res = supabase.table("oracle_cache").select("question_hash", "chapter_cap", "response").execute()
        cache_entries = res.data or []
        
        deleted_count = 0
        for entry in cache_entries:
            resp = (entry.get("response") or "").lower()
            qh = entry.get("question_hash")
            cc = entry.get("chapter_cap")
            
            match = False
            for term in patterns_and_entities:
                if term.lower() in resp:
                    match = True
                    break
                    
            if match and qh and cc is not None:
                if not dry_run:
                    supabase.table("oracle_cache").delete().eq("question_hash", qh).eq("chapter_cap", cc).execute()
                deleted_count += 1
        return deleted_count
    except Exception as e:
        print_safe(f"Error clearing cache selectively: {e}")
        return 0

def run_pipeline(dry_run: bool = True, clear_cache: bool = True) -> dict:
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    errors = []
    
    # 1. Fetch pending feedbacks
    feedbacks = fetch_pending_feedbacks()
    feedback_count = len(feedbacks)
    print_safe(f"Found {feedback_count} pending feedbacks.")
    
    if feedback_count == 0:
        return {
            "feedback_rows_read": 0,
            "summary_rows_written": 0,
            "patches_written": 0,
            "cache_rows_deleted": 0,
            "dry_run": dry_run,
            "ok": True
        }

    # 2. Build summaries
    summaries = build_feedback_summaries(feedbacks)
    
    # 3. Build candidate patches
    candidate_patches = build_oracle_patches(feedbacks)
    
    # 4. Fetch existing patches to perform deduplication
    existing = fetch_existing_patches()
    existing_keys = {(p.get("query_pattern"), p.get("patch_type")) for p in existing}
    
    new_patches = []
    for p in candidate_patches:
        key = (p["query_pattern"], p["patch_type"])
        if key not in existing_keys:
            new_patches.append(p)
            existing_keys.add(key)

    # 5. Database Writes
    summaries_written = 0
    patches_written = 0
    
    if not dry_run:
        # A. Upsert summaries
        if summaries:
            try:
                res = supabase.table("oracle_answer_feedback_summary").upsert(summaries).execute()
                summaries_written = len(res.data or [])
            except Exception as e:
                errors.append(f"Failed to upsert summaries: {e}")
                
        # B. Insert new patches
        if new_patches:
            try:
                res = supabase.table("oracle_answer_effective_patches").insert(new_patches).execute()
                patches_written = len(res.data or [])
            except Exception as e:
                errors.append(f"Failed to insert patches: {e}")
                
        # C. Update feedback status to 'resolved'
        feedback_ids = [fb.get("id") for fb in feedbacks if fb.get("id")]
        if feedback_ids:
            try:
                supabase.table("rag_feedback").update({"status": "resolved"}).in_("id", feedback_ids).execute()
            except Exception as e:
                errors.append(f"Failed to resolve feedbacks: {e}")
    else:
        summaries_written = len(summaries)
        patches_written = len(new_patches)

    # 6. Cache Invalidation
    cache_cleared = 0
    if clear_cache:
        terms_to_clear = set()
        for p in candidate_patches:
            if p.get("target_entity"):
                terms_to_clear.add(p["target_entity"])
            if p.get("query_pattern"):
                clean = p["query_pattern"].replace(" là ai", "").replace(" là gì", "").strip()
                if len(clean) >= 2:
                    terms_to_clear.add(clean)
        cache_cleared = clear_oracle_cache_selectively(list(terms_to_clear), dry_run=dry_run)

    return {
        "feedback_rows_read": feedback_count,
        "summary_rows_written": summaries_written,
        "patches_written": patches_written,
        "cache_rows_deleted": cache_cleared,
        "dry_run": dry_run,
        "ok": len(errors) == 0,
        "errors": errors
    }

def main():
    parser = argparse.ArgumentParser(description="Run RAG Oracle Answer feedback loop pipeline.")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Dry run simulation mode.")
    parser.add_argument("--write", action="store_true", help="Execute DB updates (disable dry-run).")
    parser.add_argument("--clear-cache", action="store_true", help="Clear oracle_cache entries selectively.")
    parser.add_argument("--json", action="store_true", help="Print result as JSON.")
    args = parser.parse_args()

    # Determine dry_run flag
    dry_run = True
    if args.write:
        dry_run = False
    elif args.dry_run:
        dry_run = True

    report = run_pipeline(dry_run=dry_run, clear_cache=args.clear_cache)

    if args.json:
        print_safe(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_safe("-" * 60)
        print_safe("ORACLE FEEDBACK PIPELINE REPORT:")
        print_safe(f"Mode: {'DRY-RUN' if report['dry_run'] else 'WRITE'}")
        print_safe(f"Feedbacks read: {report['feedback_rows_read']}")
        print_safe(f"Summaries written: {report['summary_rows_written']}")
        print_safe(f"Patches written: {report['patches_written']}")
        print_safe(f"Cache entries cleared: {report['cache_rows_deleted']}")
        if report.get("errors"):
            print_safe(f"Errors: {report['errors']}")
        print_safe("-" * 60)

if __name__ == "__main__":
    main()
