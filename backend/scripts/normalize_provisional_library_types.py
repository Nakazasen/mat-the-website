#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path

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

def main():
    parser = argparse.ArgumentParser(description="Normalize types/categories in provisional_library.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Validate and output plan without writing (default).")
    parser.add_argument("--write", action="store_true", help="Perform actual updates in database. Overrides dry-run.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of updates to perform.")
    parser.add_argument("--clear-cache", action="store_true", help="Clear oracle_cache for normalized concept names.")
    parser.add_argument("--cache-dry-run", action="store_true", help="Dry-run cache invalidation.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_provisional_library_type_normalization_plan.json", help="Path to save normalization plan.")
    
    args = parser.parse_args()

    # Dry run is False only when --write is explicitly passed
    is_dry_run = not args.write

    if not supabase:
        print_safe("Error: Supabase client not initialized.")
        sys.exit(1)

    print_safe("Fetching records from database...")
    all_rows = []
    batch_size = 1000
    start = 0
    while True:
        try:
            res = supabase.table("provisional_library").select("id, name, type, source, quality_class").range(start, start + batch_size - 1).execute()
            data = res.data or []
            all_rows.extend(data)
            if len(data) < batch_size:
                break
            start += batch_size
        except Exception as e:
            print_safe(f"Error fetching batch starting at {start}: {e}")
            sys.exit(1)

    from backend.rag.provisional_library_type_normalizer import build_type_normalization_plan

    plan = build_type_normalization_plan(all_rows)
    changed_records = [p for p in plan if p["needs_normalization"] and p["old_type"] != p["new_type"]]

    if args.limit:
        changed_records = changed_records[:args.limit]

    summary = {
        "mode": "WRITE" if not is_dry_run else "DRY-RUN",
        "total_records_scanned": len(all_rows),
        "total_to_update": len(changed_records),
        "updated_successfully": 0,
        "failed_updates": 0,
        "errors": []
    }

    if is_dry_run:
        print_safe("DRY-RUN mode active. No database mutations will be performed.")
    else:
        print_safe(f"Performing updates on {len(changed_records)} records...")
        updated_names = []
        for idx, rec in enumerate(changed_records):
            r_id = rec["id"]
            new_type = rec["new_type"]
            name = rec["name"]
            try:
                supabase.table("provisional_library").update({"type": new_type}).eq("id", r_id).execute()
                summary["updated_successfully"] += 1
                updated_names.append(name)
            except Exception as e:
                summary["failed_updates"] += 1
                summary["errors"].append({"id": r_id, "name": name, "error": str(e)})
                print_safe(f"Failed to update {name} ({r_id}): {e}")

        # Clear cache if requested
        if args.clear_cache and updated_names:
            print_safe(f"Running cache invalidation for {len(updated_names)} normalized concepts...")
            from backend.rag.oracle_cache_invalidation import clear_oracle_cache_for_terms, build_cache_invalidation_terms
            terms = build_cache_invalidation_terms(updated_names)
            cache_report = clear_oracle_cache_for_terms(
                supabase,
                terms=terms,
                dry_run=args.cache_dry_run
            )
            summary["cache_invalidation"] = cache_report
            print_safe(f"Cache invalidation report: matched={cache_report['matched_rows']}, deleted={cache_report['deleted_rows']}, dry_run={cache_report['dry_run']}")

    # Save full plan report
    report_output = {
        "summary": summary,
        "records_to_normalize": changed_records
    }
    
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_output, f, indent=2, ensure_ascii=False)

    print_safe(f"Plan report saved to: {output_path}")
    if args.json:
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
