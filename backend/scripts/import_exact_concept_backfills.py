#!/usr/bin/env python3
import os
import sys
import json
import argparse
from typing import List, Dict, Any
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from backend.database import supabase
except ImportError:
    supabase = None

def print_safe(text):
    """Safely print text to stdout."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def build_db_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares the database payload matching the provisional_library table columns."""
    name = record.get("name", "")
    evidence = record.get("evidence", [])
    chapter_list = record.get("chapter_numbers", [])
    first_ch = record.get("first_chapter")
    last_ch = record.get("last_chapter")
    
    return {
        "id": record.get("id"),
        "name": name,
        "normalized_name": record.get("normalized_name", name),
        "type": record.get("type"),
        "summary": record.get("summary"),
        "evidence": evidence,
        "confidence": float(record.get("confidence", 0.0)),
        "quality_class": record.get("quality_class"),
        "status": record.get("status", "provisional"),
        "source": record.get("source", "exact_concept_backfill_v1"),
        "feedback_score": int(record.get("feedback_score", 0)),
        "needs_review": bool(record.get("needs_review", False)),
        "chapter_numbers": chapter_list,
        "first_chapter": first_ch,
        "last_chapter": last_ch
    }

def main():
    parser = argparse.ArgumentParser(description="Import exact concept backfills into Supabase.")
    parser.add_argument("--input", type=str, default="backend/rag/generated_exact_concept_backfills.json", help="Path to candidates JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and count records without writing.")
    parser.add_argument("--write", action="store_true", help="Upsert records to database.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    parser.add_argument("--clear-cache", action="store_true", help="Clear oracle_cache entries related to imported concepts.")
    parser.add_argument("--cache-dry-run", action="store_true", help="Dry-run cache invalidation (do not delete).")
    args = parser.parse_args()

    # Must specify either dry-run or write
    if not args.dry_run and not args.write:
        print_safe("Error: You must specify either --dry-run or --write.")
        sys.exit(1)
        
    if args.dry_run and args.write:
        print_safe("Error: Cannot specify both --dry-run and --write.")
        sys.exit(1)

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print_safe(f"Input file not found: {input_path}")
        sys.exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)
        
    print_safe(f"Loaded {len(candidates)} candidates from {input_path}")

    summary = {
        "planned_upsert": len(candidates),
        "upserted": 0,
        "failed": 0,
        "errors": []
    }

    if args.dry_run:
        print_safe("DRY-RUN mode active. No database mutations will be performed.")
        if args.json:
            print(json.dumps(summary, indent=2))
        return

    # Write mode
    if not supabase:
        print_safe("Error: Supabase client not initialized.")
        sys.exit(1)

    batch_size = 50
    print_safe(f"Upserting {len(candidates)} candidates in batches of {batch_size}...")
    
    upserted_names = []
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        payloads = [build_db_payload(c) for c in batch]
        
        try:
            res = supabase.table("provisional_library").upsert(payloads).execute()
            summary["upserted"] += len(payloads)
            upserted_names.extend([p["name"] for p in payloads])
        except Exception as e:
            summary["failed"] += len(payloads)
            summary["errors"].append(str(e))
            print_safe(f"Batch {i // batch_size} failed: {e}")
            
    print_safe(f"Import finished! Upserted: {summary['upserted']}, Failed: {summary['failed']}")

    # Cache Invalidation Integration
    if args.clear_cache and upserted_names:
        print_safe(f"Running cache invalidation for {len(upserted_names)} concepts...")
        from backend.rag.oracle_cache_invalidation import clear_oracle_cache_for_terms, build_cache_invalidation_terms
        terms = build_cache_invalidation_terms(upserted_names)
        cache_report = clear_oracle_cache_for_terms(
            supabase,
            terms=terms,
            dry_run=args.cache_dry_run
        )
        summary["cache_invalidation"] = cache_report
        print_safe(f"Cache invalidation report: matched={cache_report['matched_rows']}, deleted={cache_report['deleted_rows']}, dry_run={cache_report['dry_run']}")
        if cache_report.get("skipped_reason"):
            print_safe(f"Cache invalidation warning: {cache_report['skipped_reason']}")

    if args.json:
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
