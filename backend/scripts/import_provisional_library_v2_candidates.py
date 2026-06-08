#!/usr/bin/env python3
import os
import sys
import json
import argparse
from typing import List, Dict, Any

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

def print_safe(text):
    """Safely print text to stdout."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def build_db_payload(record: Dict[str, Any], source_value: str = "story_chunks_auto_extract_v2") -> Dict[str, Any]:
    """Prepares the database payload matching the provisional_library table columns."""
    name = record.get("name", "")
    evidence = record.get("evidence", [])
    
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
        "source": source_value,
        "feedback_score": int(record.get("feedback_score", 0)),
        "needs_review": bool(record.get("needs_review", False)),
        "chapter_numbers": chapter_list,
        "first_chapter": first_ch,
        "last_chapter": last_ch
    }

def main():
    parser = argparse.ArgumentParser(description="Import V2 provisional library candidates into Supabase.")
    parser.add_argument("--input", type=str, default="backend/rag/generated_provisional_library_v2_import_candidates.json", help="Path to candidates JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode: validate and count records without writing.")
    parser.add_argument("--write", action="store_true", help="Write mode: upsert records to database.")
    parser.add_argument("--replace-version", type=str, default="v2", help="Version to set in the source column.")
    parser.add_argument("--backup-path", type=str, default=None, help="Verify that a valid backup JSON exists at this path before writing.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    parser.add_argument("--clear-cache", action="store_true", help="Clear oracle_cache entries related to imported concepts.")
    parser.add_argument("--cache-dry-run", action="store_true", help="Dry-run cache invalidation (do not delete).")
    parser.add_argument("--cache-limit-terms", type=int, default=200, help="Maximum number of concept terms to invalidate cache for (default 200).")
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
        
    print_safe(f"Loaded {len(candidates)} import candidates from {input_path}")
    
    # Verify backup path if write mode and backup-path specified
    if args.write and args.backup_path:
        backup_file = os.path.abspath(args.backup_path)
        if not os.path.exists(backup_file):
            print_safe(f"Error: Specified backup path does not exist: {backup_file}")
            print_safe("Aborting write operation to prevent data loss without backup.")
            sys.exit(1)
        else:
            print_safe(f"Backup file verified at: {backup_file}")

    source_val = f"story_chunks_auto_extract_{args.replace_version}"
    
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
        
    # Write mode - batch upserts
    batch_size = 100
    print_safe(f"Upserting {len(candidates)} candidates in batches of {batch_size}...")
    
    upserted_names = []
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        payloads = [build_db_payload(c, source_value=source_val) for c in batch]
        
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

        orig_count = len(terms)
        truncated = False
        if orig_count > args.cache_limit_terms:
            terms = terms[:args.cache_limit_terms]
            truncated = True
            print_safe(f"Warning: Cache invalidation terms truncated from {orig_count} to limit of {args.cache_limit_terms}.")

        cache_report = clear_oracle_cache_for_terms(
            supabase,
            terms=terms,
            dry_run=args.cache_dry_run
        )
        cache_report["truncated"] = truncated
        cache_report["original_terms_count"] = orig_count
        summary["cache_invalidation"] = cache_report

        print_safe(f"Cache invalidation report: matched={cache_report['matched_rows']}, deleted={cache_report['deleted_rows']}, dry_run={cache_report['dry_run']}, truncated={truncated}")
        if cache_report.get("skipped_reason"):
            print_safe(f"Cache invalidation warning: {cache_report['skipped_reason']}")

    if args.json:
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
