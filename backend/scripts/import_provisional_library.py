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

from backend.rag.provisional_library_importer import (
    load_ranked_library,
    filter_importable_records,
    upsert_provisional_records,
    summarize_import
)

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Import high and medium confidence provisional library records to Supabase.")
    parser.add_argument("--input", type=str, default="backend/rag/generated_provisional_library_ranked.json", help="Input ranked JSON library path.")
    parser.add_argument("--quality", nargs="+", default=["high_confidence", "medium_confidence"], help="List of allowed quality classes to import.")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry-run (no DB write).")
    parser.add_argument("--write", action="store_true", help="Commit writes to the database.")
    parser.add_argument("--limit", type=int, default=2000, help="Limit maximum records to import.")
    parser.add_argument("--json", action="store_true", help="Format console summary output as JSON.")
    
    args = parser.parse_args()
    
    # Default is dry-run unless --write is passed and --dry-run is not
    dry_run = True
    if args.write and not args.dry_run:
        dry_run = False
        
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print_safe(f"Input file does not exist: {input_path}")
        sys.exit(1)
        
    print_safe(f"Loading ranked provisional library from: {input_path}")
    try:
        all_records = load_ranked_library(input_path)
    except Exception as e:
        print_safe(f"Error loading ranked library: {e}")
        sys.exit(1)
        
    print_safe(f"Loaded {len(all_records)} total records from ranked library.")
    
    # Filter by quality class
    importable_records = filter_importable_records(all_records, allowed_quality=args.quality)
    print_safe(f"Filtered {len(importable_records)} records matching quality classes: {args.quality}")
    
    # Apply limit
    if len(importable_records) > args.limit:
        print_safe(f"Limiting import count from {len(importable_records)} to {args.limit} records.")
        importable_records = importable_records[:args.limit]
        
    skipped_count = len(all_records) - len(importable_records)
    
    import_stats = summarize_import(importable_records)
    
    print_safe("Upserting records to Supabase...")
    upsert_summary = upsert_provisional_records(supabase, importable_records, dry_run=dry_run)
    
    cli_summary = {
        "dry_run": dry_run,
        "total_records": len(all_records),
        "importable_count": len(importable_records),
        "skipped_count": skipped_count,
        "import_stats": import_stats,
        "upsert_summary": upsert_summary
    }
    
    if args.json:
        print_safe("-" * 60)
        print_safe("IMPORT SUMMARY:")
        print_safe(json.dumps(cli_summary, indent=2, ensure_ascii=False))
        print_safe("-" * 60)
    else:
        print_safe("-" * 60)
        print_safe("IMPORT SUMMARY:")
        print_safe(f"Mode: {'DRY-RUN (No Database Writes)' if dry_run else 'WRITE (Supabase DB Commit)'}")
        print_safe(f"Total processed in ranked JSON: {cli_summary['total_records']}")
        print_safe(f"Eligible for import: {cli_summary['importable_count']}")
        print_safe(f"Skipped (low quality/limit): {cli_summary['skipped_count']}")
        print_safe(f"Successfully upserted: {upsert_summary['upserted']}")
        print_safe(f"Failed: {upsert_summary['failed']}")
        if upsert_summary["errors"]:
            print_safe(f"Errors encountered: {upsert_summary['errors']}")
        print_safe("-" * 60)
        
if __name__ == "__main__":
    main()
