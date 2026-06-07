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

def perform_restore(input_path: str, dry_run: bool = True) -> Dict[str, Any]:
    """Load backup file, delete all current records, and insert the backup records in batches."""
    with open(input_path, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    summary = {
        "read_count": len(records),
        "deleted_count": 0,
        "inserted_count": 0,
        "failed_count": 0,
        "errors": []
    }
    
    if dry_run:
        print_safe("DRY-RUN mode. No database mutations will be performed.")
        summary["inserted_count"] = len(records)
        return summary
        
    # 1. Delete all current records
    print_safe("Deleting all existing rows from provisional_library...")
    try:
        # neq("id", "0") matches all text IDs
        del_res = supabase.table("provisional_library").delete().neq("id", "0").execute()
        summary["deleted_count"] = len(del_res.data) if del_res.data else 0
        print_safe(f"Deleted existing records.")
    except Exception as e:
        print_safe(f"Warning during delete: {e}")
        summary["errors"].append(f"Delete warning: {e}")
        
    # 2. Bulk insert backed up records in batches of 100
    batch_size = 100
    print_safe(f"Inserting {len(records)} records in batches of {batch_size}...")
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        
        # Clean up records to match table schema fields (remove extra fields if any)
        clean_batch = []
        for r in batch:
            clean_rec = {
                "id": r.get("id"),
                "name": r.get("name"),
                "normalized_name": r.get("normalized_name"),
                "type": r.get("type"),
                "summary": r.get("summary"),
                "evidence": r.get("evidence", []),
                "confidence": float(r.get("confidence", 0.0)),
                "quality_class": r.get("quality_class"),
                "status": r.get("status", "provisional"),
                "source": r.get("source", "story_chunks_auto_extract"),
                "feedback_score": int(r.get("feedback_score", 0)),
                "needs_review": bool(r.get("needs_review", False)),
                "chapter_numbers": r.get("chapter_numbers", []),
                "first_chapter": r.get("first_chapter"),
                "last_chapter": r.get("last_chapter")
            }
            clean_batch.append(clean_rec)
            
        try:
            supabase.table("provisional_library").insert(clean_batch).execute()
            summary["inserted_count"] += len(clean_batch)
        except Exception as e:
            summary["failed_count"] += len(clean_batch)
            summary["errors"].append(str(e))
            print_safe(f"Batch {i // batch_size} insert failed: {e}")
            
    return summary

def main():
    parser = argparse.ArgumentParser(description="Restore provisional_library from a JSON backup file.")
    parser.add_argument("--input", type=str, required=True, help="Path to backup JSON file.")
    parser.add_argument("--dry-run", action="store_true", help="Validate input and count records without database modification.")
    parser.add_argument("--write", action="store_true", help="Perform the destructive restore operation.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    args = parser.parse_args()
    
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
        
    print_safe(f"Restoring provisional_library from backup file: {input_path}")
    
    try:
        summary = perform_restore(input_path, dry_run=args.dry_run)
        print_safe(f"Restore finished. Summary: Read: {summary['read_count']}, Inserted: {summary['inserted_count']}, Failed: {summary['failed_count']}")
        
        if args.json:
            print(json.dumps(summary, indent=2))
    except Exception as e:
        print_safe(f"Restore failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
