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

from backend.rag.new_chapter_source_reader import load_new_chapters_from_folder
from backend.rag.new_chapter_ingester import (
    build_new_chapter_db_plan,
    insert_chapters_and_chunks
)

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Ingest new chapters from raw files into database chapters & story_chunks.")
    parser.add_argument("--source-dir", type=str, default="backend/data/new_chapters", help="Folder containing new chapter text files.")
    parser.add_argument("--strict", action="store_true", default=True, help="Enforce sequence gaps validation (default: True)")
    parser.add_argument("--no-strict", dest="strict", action="store_false", help="Disable gap sequence validation")
    parser.add_argument("--write", action="store_true", help="Perform actual database writes (disables default dry-run).")
    parser.add_argument("--clear-cache", action="store_true", default=True, help="Automatically clear relevant oracle cache (default: True)")
    parser.add_argument("--output", type=str, default="backend/rag/generated_new_chapter_ingest_result.json", help="Path to save execution results.")
    parser.add_argument("--json", action="store_true", help="Format output as JSON on stdout.")
    
    args = parser.parse_args()

    dry_run = not args.write

    if not args.json:
        print_safe("=" * 60)
        print_safe("RAG New Chapter Ingest Pipeline")
        print_safe(f"Mode         : {'DRY-RUN' if dry_run else 'WRITE (LIVE-DB)'}")
        print_safe(f"Source Folder: {args.source_dir}")
        print_safe(f"Strict Mode  : {args.strict}")
        print_safe("=" * 60)

    # 1. Resolve current last chapter number
    last_chapter = 829
    if supabase:
        try:
            res = supabase.table("story_chunks").select("chapter_number").order("chapter_number", desc=True).limit(1).execute()
            if res.data:
                last_chapter = int(res.data[0].get("chapter_number", 829))
        except Exception as e:
            if not args.json:
                print_safe(f"Warning: Failed to fetch last chapter from database: {e}. Defaulting to 829.")
    else:
        if not args.json:
            print_safe("Warning: Supabase client not initialized. Defaulting last chapter to 829.")

    if not args.json:
        print_safe(f"Resolved current last chapter: {last_chapter}")

    # 2. Load new chapter files
    chapters = load_new_chapters_from_folder(args.source_dir)
    
    # 3. Build plan
    plan = build_new_chapter_db_plan(chapters, last_chapter, strict=args.strict)
    
    if not plan["ok"]:
        result = {
            "mode": "DRY_RUN" if dry_run else "WRITE",
            "ok": False,
            "chapters_inserted": 0,
            "story_chunks_inserted": 0,
            "cache_rows_deleted": 0,
            "errors": plan.get("errors", ["Plan build failed"]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    else:
        # 4. Execute ingestion (dry-run or live write)
        result = insert_chapters_and_chunks(supabase, plan, dry_run=dry_run)
        result["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Include planned metrics in dry-run result
        if dry_run:
            result["current_last_chapter"] = last_chapter
            result["new_chapters_detected"] = plan["new_chapters_detected"]
            result["planned_chapter_inserts"] = plan["planned_chapter_inserts"]
            result["planned_chunk_inserts"] = plan["planned_chunk_inserts_count"]
            result["write_required"] = False
            result["errors"] = plan["errors"]
            
    # Save output to JSON
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    if not args.json:
        print_safe(f"Execution report saved to: {output_path}")
        print_safe(f"Ingestion outcome ok: {result.get('ok', False)}")
        print_safe(f"Chapters inserted   : {result.get('chapters_inserted', 0)}")
        print_safe(f"Chunks inserted     : {result.get('story_chunks_inserted', 0)}")
        print_safe(f"Cache cleared rows  : {result.get('cache_rows_deleted', 0)}")
        if result.get("errors"):
            print_safe("\nErrors encountered:")
            for err in result["errors"]:
                print_safe(f" - {err}")
        print_safe("=" * 60)
        
    if args.json:
        # Output summary as JSON to stdout
        summary = {
            "mode": result.get("mode"),
            "ok": result.get("ok", False),
            "chapters_inserted": result.get("chapters_inserted", 0),
            "story_chunks_inserted": result.get("story_chunks_inserted", 0),
            "cache_rows_deleted": result.get("cache_rows_deleted", 0),
            "errors": result.get("errors", [])
        }
        # In dry-run mode, add details
        if dry_run:
            summary.update({
                "current_last_chapter": result.get("current_last_chapter"),
                "new_chapters_count": len(result.get("new_chapters_detected", [])),
                "planned_chunk_inserts": result.get("planned_chunk_inserts")
            })
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
