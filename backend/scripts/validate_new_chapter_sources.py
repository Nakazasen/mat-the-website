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
    from database import supabase
except ImportError:
    from backend.database import supabase

from backend.rag.new_chapter_source_reader import (
    load_new_chapters_from_folder,
    build_new_chapter_manifest
)

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Validate incoming new chapter source files against contract rules.")
    parser.add_argument("--source-dir", type=str, default="backend/data/new_chapters", help="Folder containing new chapter text files.")
    parser.add_argument("--current-last-chapter", type=str, default="auto", help="Last chapter number in database or 'auto' to query.")
    parser.add_argument("--strict", action="store_true", default=True, help="Enforce sequence gaps validation (default: True)")
    parser.add_argument("--no-strict", dest="strict", action="store_false", help="Disable gap sequence validation")
    parser.add_argument("--output", type=str, default="backend/rag/generated_new_chapter_source_validation.json", help="Path to save validation manifest.")
    parser.add_argument("--json", action="store_true", help="Format output as JSON on stdout.")
    
    args = parser.parse_args()

    if not args.json:
        print_safe("=" * 60)
        print_safe("New Chapter Ingest Validation Run")
        print_safe(f"Source Folder: {args.source_dir}")
        print_safe(f"Strict Mode  : {args.strict}")
        print_safe("=" * 60)

    # 1. Resolve current last chapter number
    last_chapter = 829
    if args.current_last_chapter == "auto":
        if supabase:
            try:
                res = supabase.table("story_chunks").select("chapter_number").order("chapter_number", desc=True).limit(1).execute()
                if res.data:
                    last_chapter = int(res.data[0].get("chapter_number", 829))
            except Exception as e:
                if not args.json:
                    print_safe(f"Warning: Failed to query database: {e}. Defaulting last chapter to 829.")
        else:
            if not args.json:
                print_safe("Warning: Supabase client not initialized. Defaulting last chapter to 829.")
    else:
        try:
            last_chapter = int(args.current_last_chapter)
        except ValueError:
            print_safe(f"Error: Invalid chapter number: {args.current_last_chapter}")
            sys.exit(1)

    if not args.json:
        print_safe(f"Resolved current last chapter: {last_chapter}")

    # 2. Scan and parse files
    chapters = load_new_chapters_from_folder(args.source_dir)
    
    # 3. Build manifest
    manifest = build_new_chapter_manifest(chapters, last_chapter, strict=args.strict)
    manifest["current_last_chapter"] = last_chapter
    
    # Save output to JSON
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    if not args.json:
        print_safe(f"Validation report saved to: {output_path}")
        print_safe(f"Run status: {manifest['status']}")
        print_safe(f"Chapters scanned: {manifest['chapters_count']}")
        print_safe(f"Valid candidates: {len(manifest['new_chapters'])}")
        if manifest["errors"]:
            print_safe("\nErrors encountered:")
            for err in manifest["errors"]:
                print_safe(f" - {err}")
        print_safe("=" * 60)
        
    if args.json:
        # Output summary as JSON to stdout
        summary = {
            "status": manifest["status"],
            "ok": manifest["ok"],
            "write_required": manifest["write_required"],
            "chapters_count": manifest["chapters_count"],
            "new_chapters_count": len(manifest["new_chapters"]),
            "current_last_chapter": last_chapter,
            "errors": manifest["errors"]
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
