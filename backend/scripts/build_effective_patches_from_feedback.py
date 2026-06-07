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

from backend.rag.effective_patch_engine import build_patch_payloads

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def fetch_feedback_records(limit: int) -> List[Dict[str, Any]]:
    try:
        res = supabase.table("provisional_library_feedback").select("*").limit(limit).execute()
        return res.data or []
    except Exception as e:
        print_safe(f"Error fetching feedback: {e}")
        return []

def fetch_provisional_records(pids: List[str]) -> Dict[str, Dict[str, Any]]:
    if not pids:
        return {}
    try:
        # Fetch in batches of 100
        records = {}
        batch_size = 100
        for i in range(0, len(pids), batch_size):
            batch = pids[i:i+batch_size]
            res = supabase.table("provisional_library").select("*").in_("id", batch).execute()
            for r in (res.data or []):
                if r.get("id"):
                    records[r["id"]] = r
        return records
    except Exception as e:
        print_safe(f"Error fetching provisional records: {e}")
        return {}

def upsert_patches(patches: List[Dict[str, Any]], dry_run: bool) -> Dict[str, Any]:
    stats = {"upserted": 0, "failed": 0, "errors": []}
    if not patches:
        return stats

    if dry_run:
        stats["upserted"] = len(patches)
        return stats

    # Convert sets or lists to json serialization-ready structures
    cleaned_patches = []
    for p in patches:
        clean = dict(p)
        # Convert any sets to lists if present
        for k, v in clean.items():
            if isinstance(v, set):
                clean[k] = list(v)
        cleaned_patches.append(clean)

    # Batch upsert in sizes of 100
    batch_size = 100
    for i in range(0, len(cleaned_patches), batch_size):
        batch = cleaned_patches[i:i+batch_size]
        try:
            # We use target_type and target_id or query_pattern as conflict targets, but GenRandomUUID handles insert
            # To perform upsert correctly on query_pattern / target, we can upsert or simply insert.
            # Supabase upsert requires unique constraint or conflict columns.
            # In our schema: CREATE TABLE ... (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), ...)
            # Let's execute upsert with no conflict columns (which acts as insert since id is primary key), or we can upsert.
            # Actually, to prevent duplicate patches, we can do a lookup or just upsert using 'id' if they have one.
            # But since these are generated dynamically, we can query existing patches and deduplicate or just insert.
            # Let's perform insert for new patches, but we can also use upsert.
            # Supabase upsert on table will insert if no conflict is specified, but since id is generated on DB, it defaults to insert.
            res = supabase.table("provisional_library_effective_patches").insert(batch).execute()
            stats["upserted"] += len(res.data or [])
        except Exception as e:
            stats["failed"] += len(batch)
            stats["errors"].append(str(e))
            
    return stats

def main():
    parser = argparse.ArgumentParser(description="Build effective knowledge patches from community feedback.")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry-run (no DB write).")
    parser.add_argument("--write", action="store_true", help="Commit patches to the database.")
    parser.add_argument("--limit", type=int, default=5000, help="Limit maximum feedback rows to fetch.")
    parser.add_argument("--json", action="store_true", help="Format console summary output as JSON.")
    
    args = parser.parse_args()
    
    dry_run = True
    if args.write and not args.dry_run:
        dry_run = False

    print_safe(f"Fetching public feedback rows from Supabase (Limit: {args.limit})...")
    feedback_rows = fetch_feedback_records(args.limit)
    print_safe(f"Retrieved {len(feedback_rows)} total feedback rows.")

    pids = list(set(str(row["provisional_id"]) for row in feedback_rows if row.get("provisional_id")))
    print_safe(f"Found {len(pids)} unique target provisional IDs.")
    
    provisional_records = fetch_provisional_records(pids)
    print_safe(f"Retrieved {len(provisional_records)} matching provisional library records.")

    print_safe("Generating knowledge patches...")
    patches = build_patch_payloads(feedback_rows, provisional_records)
    print_safe(f"Generated {len(patches)} effective knowledge patches.")

    print_safe("Saving patches to Supabase...")
    upsert_stats = upsert_patches(patches, dry_run=dry_run)

    # Distribution stats
    type_stats = {}
    policy_stats = {}
    for p in patches:
        ptype = p.get("patch_type", "unknown")
        policy = p.get("oracle_policy", "allow")
        type_stats[ptype] = type_stats.get(ptype, 0) + 1
        policy_stats[policy] = policy_stats.get(policy, 0) + 1

    cli_summary = {
        "dry_run": dry_run,
        "total_feedback_rows": len(feedback_rows),
        "target_provisional_records": len(provisional_records),
        "generated_patches": len(patches),
        "patch_types_distribution": type_stats,
        "policy_distribution": policy_stats,
        "upsert_stats": upsert_stats
    }

    if args.json:
        print_safe("-" * 60)
        print_safe("PATCH GENERATION SUMMARY:")
        print_safe(json.dumps(cli_summary, indent=2, ensure_ascii=False))
        print_safe("-" * 60)
    else:
        print_safe("-" * 60)
        print_safe("PATCH GENERATION SUMMARY:")
        print_safe(f"Mode: {'DRY-RUN (No Database Writes)' if dry_run else 'WRITE (Supabase DB Commit)'}")
        print_safe(f"Total processed feedback rows: {cli_summary['total_feedback_rows']}")
        print_safe(f"Generated patches: {cli_summary['generated_patches']}")
        print_safe(f"Patch types distribution: {cli_summary['patch_types_distribution']}")
        print_safe(f"Oracle policy distribution: {cli_summary['policy_distribution']}")
        print_safe(f"Successfully upserted patches: {upsert_stats['upserted']}")
        print_safe(f"Failed patches: {upsert_stats['failed']}")
        if upsert_stats["errors"]:
            print_safe(f"Errors: {upsert_stats['errors']}")
        print_safe("-" * 60)

if __name__ == "__main__":
    main()
