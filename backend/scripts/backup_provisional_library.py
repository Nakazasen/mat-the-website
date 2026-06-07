#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime, timezone

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

def perform_backup(output_path: str) -> list:
    """Retrieve all rows from provisional_library in pages and save them to a JSON file."""
    records = []
    limit = 1000
    offset = 0
    
    while True:
        res = supabase.table("provisional_library").select("*").range(offset, offset + limit - 1).execute()
        data = res.data
        if not data:
            break
        records.extend(data)
        if len(data) < limit:
            break
        offset += limit
        
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        
    return records

def main():
    parser = argparse.ArgumentParser(description="Backup the current provisional_library table from Supabase.")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_output = f"backend/rag/backups/provisional_library_backup_{timestamp}.json"
    parser.add_argument("--output", type=str, default=default_output, help="Path to save the JSON backup file.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON to stdout.")
    args = parser.parse_args()
    
    output_path = os.path.abspath(args.output)
    print_safe(f"Backing up provisional_library to: {output_path}")
    
    try:
        records = perform_backup(output_path)
        print_safe(f"Backup complete! Backed up {len(records)} records.")
        
        if args.json:
            summary = {
                "backup_path": output_path,
                "record_count": len(records),
                "timestamp": timestamp
            }
            print(json.dumps(summary, indent=2))
    except Exception as e:
        print_safe(f"Backup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
