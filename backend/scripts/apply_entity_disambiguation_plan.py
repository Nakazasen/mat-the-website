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
    parser = argparse.ArgumentParser(description="Apply entity disambiguation plan to database.")
    parser.add_argument("--plan", type=str, default="backend/rag/generated_entity_disambiguation_plan.json", help="Path to JSON plan file.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run (default): output statistics without writing.")
    parser.add_argument("--write", action="store_true", help="Write changes to database. Overrides dry-run.")
    parser.add_argument("--min-confidence", type=float, default=0.1, help="Minimum confidence threshold for update_type action (default 0.1).")
    parser.add_argument("--clear-cache", action="store_true", help="Clear oracle_cache for modified concept names.")
    parser.add_argument("--cache-dry-run", action="store_true", help="Dry-run cache invalidation.")
    parser.add_argument("--json", action="store_true", help="Print execution summary JSON to stdout.")
    
    args = parser.parse_args()

    # Dry-run is False only if --write is explicitly passed
    is_dry_run = not args.write

    if not supabase:
        print_safe("Error: Supabase client not initialized.")
        sys.exit(1)

    plan_path = os.path.abspath(args.plan)
    if not os.path.exists(plan_path):
        print_safe(f"Error: Plan file not found: {plan_path}")
        sys.exit(1)

    with open(plan_path, "r", encoding="utf-8") as f:
        plan_report = json.load(f)

    # We also need confidence values of records since the plan file does not store the full row
    # Let's retrieve confidence for all rows from database to verify threshold
    print_safe("Fetching confidence values for verification...")
    confidence_map = {}
    batch_size = 1000
    start = 0
    while True:
        try:
            res = supabase.table("provisional_library").select("id, confidence").range(start, start + batch_size - 1).execute()
            data = res.data or []
            for d in data:
                confidence_map[d["id"]] = float(d.get("confidence", 0.0))
            if len(data) < batch_size:
                break
            start += batch_size
        except Exception as e:
            print_safe(f"Error fetching confidence values: {e}")
            sys.exit(1)

    summary = {
        "mode": "WRITE" if not is_dry_run else "DRY-RUN",
        "update_type_processed": 0,
        "manual_review_marked": 0,
        "noise_candidate_discarded": 0,
        "failed_updates": 0,
        "errors": []
    }

    modified_names = []

    if is_dry_run:
        print_safe("DRY-RUN mode active. No database mutations will be performed.")
        # Simulating statistics
        for item in plan_report.get("to_update_type", []):
            r_id = item["id"]
            conf = confidence_map.get(r_id, 0.0)
            if conf >= args.min_confidence:
                summary["update_type_processed"] += 1
        summary["manual_review_marked"] = len(plan_report.get("to_mark_manual_review", []))
        summary["noise_candidate_discarded"] = len(plan_report.get("to_mark_noise_candidate", []))
    else:
        # 1. Apply Type Updates (action == "update_type")
        print_safe("Applying type updates...")
        for item in plan_report.get("to_update_type", []):
            r_id = item["id"]
            new_type = item["new_type"]
            name = item["name"]
            conf = confidence_map.get(r_id, 0.0)
            
            if conf < args.min_confidence:
                # Skip if below confidence threshold
                continue
                
            try:
                supabase.table("provisional_library").update({"type": new_type}).eq("id", r_id).execute()
                summary["update_type_processed"] += 1
                modified_names.append(name)
            except Exception as e:
                summary["failed_updates"] += 1
                summary["errors"].append({"id": r_id, "name": name, "error": str(e)})
                print_safe(f"Failed to update type for {name}: {e}")

        # 2. Mark Manual Review (action == "manual_review")
        print_safe("Marking manual review records...")
        for item in plan_report.get("to_mark_manual_review", []):
            r_id = item["id"]
            name = item["name"]
            try:
                supabase.table("provisional_library").update({"needs_review": True}).eq("id", r_id).execute()
                summary["manual_review_marked"] += 1
                # No name added to modified_names for cache clear since type did not change
            except Exception as e:
                summary["failed_updates"] += 1
                summary["errors"].append({"id": r_id, "name": name, "error": str(e)})
                print_safe(f"Failed to mark review for {name}: {e}")

        # 3. Mark Noise Candidate (action == "noise_candidate")
        print_safe("Discarding noise candidates...")
        for item in plan_report.get("to_mark_noise_candidate", []):
            r_id = item["id"]
            name = item["name"]
            try:
                # Set status to discard and needs_review to True
                supabase.table("provisional_library").update({"status": "discard", "needs_review": True}).eq("id", r_id).execute()
                summary["noise_candidate_discarded"] += 1
                modified_names.append(name)
            except Exception as e:
                summary["failed_updates"] += 1
                summary["errors"].append({"id": r_id, "name": name, "error": str(e)})
                print_safe(f"Failed to discard noise {name}: {e}")

        # Clear cache for names of concepts whose type or status changed
        if args.clear_cache and modified_names:
            print_safe(f"Running cache invalidation for {len(modified_names)} modified concepts...")
            from backend.rag.oracle_cache_invalidation import clear_oracle_cache_for_terms, build_cache_invalidation_terms
            terms = build_cache_invalidation_terms(modified_names)
            cache_report = clear_oracle_cache_for_terms(
                supabase,
                terms=terms,
                dry_run=args.cache_dry_run
            )
            summary["cache_invalidation"] = cache_report
            print_safe(f"Cache invalidation report: matched={cache_report['matched_rows']}, deleted={cache_report['deleted_rows']}, dry_run={cache_report['dry_run']}")

    print_safe("Disambiguation plan application finished.")
    print_safe(f"Results: {summary}")
    if args.json:
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
