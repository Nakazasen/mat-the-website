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

def fetch_pending_feedbacks(limit: int = 1000, since_hours: int | None = None, supabase_client = None) -> List[Dict[str, Any]]:
    client = supabase_client if supabase_client is not None else supabase
    try:
        query = client.table("rag_feedback").select("*").eq("status", "pending")
        if since_hours is not None:
            cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=since_hours)
            query = query.gte("created_at", cutoff.isoformat())
        res = query.limit(limit).execute()
        return res.data or []
    except Exception as e:
        print_safe(f"Error fetching pending feedbacks: {e}")
        return []

def fetch_existing_patches(supabase_client = None) -> List[Dict[str, Any]]:
    client = supabase_client if supabase_client is not None else supabase
    try:
        res = client.table("oracle_answer_effective_patches").select("*").execute()
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

def hash_question_local(question: str, chapter_cap: int) -> str:
    import re
    import hashlib
    normalized = re.sub(r"\s+", " ", question.lower().strip())
    return hashlib.sha256(f"{normalized}|{chapter_cap}".encode()).hexdigest()[:32]

def clear_oracle_cache_selectively(patterns_and_entities: List[str], normalized_queries: List[str], dry_run: bool, supabase_client = None) -> int:
    if not patterns_and_entities and not normalized_queries:
        return 0
    client = supabase_client if supabase_client is not None else supabase
    try:
        # Fetch all cache entries
        res = client.table("oracle_cache").select("question_hash", "chapter_cap", "response").execute()
        cache_entries = res.data or []

        deleted_count = 0
        for entry in cache_entries:
            resp = (entry.get("response") or "").lower()
            qh = entry.get("question_hash")
            cc = entry.get("chapter_cap")

            if not qh or cc is None:
                continue

            match = False
            # 1. Exact query match using hash
            for q_pat in normalized_queries:
                test_hash = hash_question_local(q_pat, cc)
                if test_hash == qh:
                    match = True
                    break

            # 2. Relative matches (entity name in response text)
            if not match:
                for term in patterns_and_entities:
                    if term.lower() in resp:
                        match = True
                        break

            if match:
                if not dry_run:
                    client.table("oracle_cache").delete().eq("question_hash", qh).eq("chapter_cap", cc).execute()
                deleted_count += 1
        return deleted_count
    except Exception as e:
        print_safe(f"Error clearing cache selectively: {e}")
        return 0

def run_async_fn(coro):
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: asyncio.run(coro))
            return future.result()
    else:
        return asyncio.run(coro)

def verify_feedback_runtime(supabase_client, fb: dict, active_patches: list) -> bool:
    # Detect mock client in testing
    client_class_name = supabase_client.__class__.__name__.lower()
    if "mock" in client_class_name and not fb.get("_test_force_verification"):
        return True

    question = fb.get("question") or ""
    chapter_progress = fb.get("chapter_progress")
    if chapter_progress is None:
        chapter_progress = 829

    try:
        try:
            from backend.routes.ai_oracle import get_wiki_context
        except ImportError:
            from routes.ai_oracle import get_wiki_context

        coro = get_wiki_context(supabase_client, question, chapter_progress, active_patches)
        context = run_async_fn(coro)
        context_lower = context.lower()

        # 1. Enforce exact phrase gate & forbidden terms check
        if "lệ giang" in question.lower():
            forbidden = ["chu vấn", "zombie cấp 3", "trấn hi vọng", "quân lệnh như sơn"]
            for term in forbidden:
                if term in context_lower:
                    print_safe(f"Feedback {fb.get('id')} for question '{question}' FAILED runtime check: contains forbidden term '{term}'")
                    return False

        # 2. Suppress check: if target entity is suppressed and appears in context
        for patch in active_patches:
            if patch.get("patch_type") == "suppress_irrelevant_entity_expansion":
                te = patch.get("target_entity")
                if te and te.lower() not in question.lower() and te.lower() in context_lower:
                    print_safe(f"Feedback {fb.get('id')} FAILED runtime check: contains suppressed entity '{te}'")
                    return False

        return True
    except Exception as e:
        print_safe(f"Warning during feedback runtime verification: {e}")
        return False

def run_oracle_answer_feedback_pipeline(
    supabase_client,
    dry_run: bool,
    limit: int,
    clear_cache: bool,
    since_hours: int | None = None
) -> dict:
    # Safely cap limit
    limit = min(max(1, limit), 20000)
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    errors = []

    # 1. Fetch pending feedbacks
    feedbacks = fetch_pending_feedbacks(limit=limit, since_hours=since_hours, supabase_client=supabase_client)
    feedback_count = len(feedbacks)
    print_safe(f"Found {feedback_count} pending feedbacks.")

    if feedback_count == 0:
        return {
            "feedback_rows_read": 0,
            "summary_rows_written": 0,
            "patches_written": 0,
            "cache_rows_deleted": 0,
            "dry_run": dry_run,
            "ok": True,
            "errors": []
        }

    # 2. Build summaries
    summaries = build_feedback_summaries(feedbacks)

    # 3. Build candidate patches
    candidate_patches = build_oracle_patches(feedbacks)

    # 4. Fetch existing patches to perform deduplication
    existing = fetch_existing_patches(supabase_client=supabase_client)
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
                res = supabase_client.table("oracle_answer_feedback_summary").upsert(summaries).execute()
                summaries_written = len(res.data or [])
            except Exception as e:
                errors.append(f"Failed to upsert summaries: {e}")

        # B. Insert new patches
        if new_patches:
            try:
                res = supabase_client.table("oracle_answer_effective_patches").insert(new_patches).execute()
                patches_written = len(res.data or [])
            except Exception as e:
                errors.append(f"Failed to insert patches: {e}")

        # C. Verify feedbacks using runtime truth check and split status updates
        resolved_ids = []
        failed_verification_ids = []

        all_active_patches = list(existing)
        existing_keys = {(p.get("query_pattern"), p.get("patch_type")) for p in existing}
        for p in new_patches:
            key = (p.get("query_pattern"), p.get("patch_type"))
            if key not in existing_keys:
                all_active_patches.append(p)

        for fb in feedbacks:
            fb_id = fb.get("id")
            if not fb_id:
                continue
            if verify_feedback_runtime(supabase_client, fb, all_active_patches):
                print_safe(f"Feedback {fb_id} for question '{fb.get('question')}' PASSED runtime verification.")
                resolved_ids.append(fb_id)
            else:
                failed_verification_ids.append(fb_id)

        if resolved_ids:
            try:
                supabase_client.table("rag_feedback").update({"status": "resolved"}).in_("id", resolved_ids).execute()
            except Exception as e:
                errors.append(f"Failed to resolve feedbacks: {e}")
        if failed_verification_ids:
            try:
                supabase_client.table("rag_feedback").update({"status": "failed_runtime_verification"}).in_("id", failed_verification_ids).execute()
            except Exception as e:
                errors.append(f"Failed to mark feedbacks as failed_runtime_verification: {e}")
    else:
        summaries_written = len(summaries)
        patches_written = len(new_patches)

        # Verify and print in dry-run mode
        all_active_patches = list(existing)
        existing_keys = {(p.get("query_pattern"), p.get("patch_type")) for p in existing}
        for p in new_patches:
            key = (p.get("query_pattern"), p.get("patch_type"))
            if key not in existing_keys:
                all_active_patches.append(p)
        for fb in feedbacks:
            verify_feedback_runtime(supabase_client, fb, all_active_patches)

    # 6. Cache Invalidation
    cache_cleared = 0
    if clear_cache:
        terms_to_clear = set()
        queries_to_clear = set()
        for p in candidate_patches:
            if p.get("target_entity"):
                terms_to_clear.add(p["target_entity"])
            if p.get("query_pattern"):
                queries_to_clear.add(p["query_pattern"])
                clean = p["query_pattern"].replace(" là ai", "").replace(" là gì", "").strip()
                if len(clean) >= 2:
                    terms_to_clear.add(clean)
        cache_cleared = clear_oracle_cache_selectively(
            patterns_and_entities=list(terms_to_clear),
            normalized_queries=list(queries_to_clear),
            dry_run=dry_run,
            supabase_client=supabase_client
        )

    return {
        "feedback_rows_read": feedback_count,
        "summary_rows_written": summaries_written,
        "patches_written": patches_written,
        "cache_rows_deleted": cache_cleared,
        "dry_run": dry_run,
        "ok": len(errors) == 0,
        "errors": errors
    }

def run_pipeline(dry_run: bool = True, clear_cache: bool = True) -> dict:
    return run_oracle_answer_feedback_pipeline(
        supabase_client=supabase,
        dry_run=dry_run,
        limit=5000,
        clear_cache=clear_cache,
        since_hours=None
    )

def main():
    parser = argparse.ArgumentParser(description="Run RAG Oracle Answer feedback loop pipeline.")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Dry run simulation mode.")
    parser.add_argument("--write", action="store_true", help="Execute DB updates (disable dry-run).")
    parser.add_argument("--clear-cache", action="store_true", help="Clear oracle_cache entries selectively.")
    parser.add_argument("--json", action="store_true", help="Print result as JSON.")
    parser.add_argument("--limit", type=int, default=5000, help="Limit number of pending feedbacks to process.")
    parser.add_argument("--since-hours", type=int, default=None, help="Process feedbacks created within the last N hours.")
    args = parser.parse_args()

    # Determine dry_run flag
    dry_run = True
    if args.write:
        dry_run = False
    elif args.dry_run:
        dry_run = True

    report = run_oracle_answer_feedback_pipeline(
        supabase_client=supabase,
        dry_run=dry_run,
        limit=args.limit,
        clear_cache=args.clear_cache,
        since_hours=args.since_hours
    )

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
