import os
import sys
import json
import argparse
from typing import Dict, List, Any

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

from backend.rag.provisional_feedback_aggregator import summarize_feedback

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def fetch_feedback_records(limit: int) -> List[Dict[str, Any]]:
    try:
        # Fetch feedback records from Supabase
        res = supabase.table("provisional_library_feedback").select("*").limit(limit).execute()
        return res.data or []
    except Exception as e:
        print_safe(f"Error fetching feedback from Supabase: {e}")
        return []

def upsert_summaries(summaries: List[Dict[str, Any]], dry_run: bool) -> Dict[str, Any]:
    stats = {"upserted": 0, "failed": 0, "errors": []}
    if not summaries:
        return stats

    if dry_run:
        stats["upserted"] = len(summaries)
        return stats

    # Batch upsert in sizes of 100
    batch_size = 100
    for i in range(0, len(summaries), batch_size):
        batch = summaries[i:i+batch_size]
        try:
            res = supabase.table("provisional_library_feedback_summary").upsert(batch).execute()
            stats["upserted"] += len(res.data or [])
        except Exception as e:
            stats["failed"] += len(batch)
            stats["errors"].append(str(e))
            
    return stats

def main():
    parser = argparse.ArgumentParser(description="Aggregate provisional library community feedback and rozhod oracle confidence policies.")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry-run (no DB write).")
    parser.add_argument("--write", action="store_true", help="Commit summaries to the database.")
    parser.add_argument("--limit", type=int, default=5000, help="Limit maximum feedback rows to fetch.")
    parser.add_argument("--json", action="store_true", help="Format console summary output as JSON.")
    
    args = parser.parse_args()
    
    # Default is dry-run unless --write is passed and --dry-run is not
    dry_run = True
    if args.write and not args.dry_run:
        dry_run = False

    print_safe(f"Fetching public feedback rows from Supabase (Limit: {args.limit})...")
    feedback_rows = fetch_feedback_records(args.limit)
    print_safe(f"Retrieved {len(feedback_rows)} total feedback rows.")

    print_safe("Aggregating feedback rows...")
    summaries = summarize_feedback(feedback_rows)
    print_safe(f"Generated {len(summaries)} feedback summaries.")

    print_safe("Saving summaries to Supabase...")
    upsert_stats = upsert_summaries(summaries, dry_run=dry_run)

    # Decided stats
    status_stats = {}
    policy_stats = {}
    for s in summaries:
        status = s.get("effective_status", "trusted")
        policy = s.get("oracle_policy", "allow")
        status_stats[status] = status_stats.get(status, 0) + 1
        policy_stats[policy] = policy_stats.get(policy, 0) + 1

    cli_summary = {
        "dry_run": dry_run,
        "total_feedback_rows": len(feedback_rows),
        "summarized_records": len(summaries),
        "status_distribution": status_stats,
        "policy_distribution": policy_stats,
        "upsert_stats": upsert_stats
    }

    if args.json:
        print_safe("-" * 60)
        print_safe("AGGREGATION SUMMARY:")
        print_safe(json.dumps(cli_summary, indent=2, ensure_ascii=False))
        print_safe("-" * 60)
    else:
        print_safe("-" * 60)
        print_safe("AGGREGATION SUMMARY:")
        print_safe(f"Mode: {'DRY-RUN (No Database Writes)' if dry_run else 'WRITE (Supabase DB Commit)'}")
        print_safe(f"Total processed feedback rows: {cli_summary['total_feedback_rows']}")
        print_safe(f"Summarized unique records: {cli_summary['summarized_records']}")
        print_safe(f"Status distribution: {cli_summary['status_distribution']}")
        print_safe(f"Oracle policy distribution: {cli_summary['policy_distribution']}")
        print_safe(f"Successfully upserted summaries: {upsert_stats['upserted']}")
        print_safe(f"Failed summaries: {upsert_stats['failed']}")
        if upsert_stats["errors"]:
            print_safe(f"Errors: {upsert_stats['errors']}")
        print_safe("-" * 60)

if __name__ == "__main__":
    main()
