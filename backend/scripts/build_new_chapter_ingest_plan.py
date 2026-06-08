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

from backend.rag.story_growth_detector import build_new_chapter_ingest_plan

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Build dry-run new chapter ingest plan.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_new_chapter_ingest_plan.json", help="Output JSON path.")
    parser.add_argument("--json", action="store_true", help="Format output as JSON on stdout.")
    args = parser.parse_args()

    print_safe("Building new chapter ingestion plan...")
    
    if not supabase:
        print_safe("Error: Supabase client is not initialized.")
        sys.exit(1)

    # 1. Fetch source chapters
    source_chapters = []
    limit = 1000
    offset = 0
    while True:
        try:
            res = supabase.table("chapters").select("chapter_number").range(offset, offset + limit - 1).execute()
            data = res.data or []
            if not data:
                break
            for row in data:
                ch = row.get("chapter_number")
                if ch is not None:
                    try:
                        source_chapters.append(int(ch))
                    except (ValueError, TypeError):
                        pass
            if len(data) < limit:
                break
            offset += limit
        except Exception as e:
            print_safe(f"Error querying chapters table: {e}")
            sys.exit(1)

    # 2. Fetch chunked chapters
    chunk_chapters = []
    offset = 0
    while True:
        try:
            res = supabase.table("story_chunks").select("chapter_number").range(offset, offset + limit - 1).execute()
            data = res.data or []
            if not data:
                break
            for row in data:
                ch = row.get("chapter_number")
                if ch is not None:
                    try:
                        chunk_chapters.append(int(ch))
                    except (ValueError, TypeError):
                        pass
            if len(data) < limit:
                break
            offset += limit
        except Exception as e:
            print_safe(f"Error querying story_chunks table: {e}")
            sys.exit(1)

    # Call detector logic
    plan = build_new_chapter_ingest_plan(chunk_chapters, source_chapters)
    plan["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Save output to JSON
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
        
    print_safe(f"New chapter ingest plan saved to: {output_path}")

    # Log specific outcomes based on detection
    if plan["status"] == "NO_NEW_CHAPTERS_FOUND":
        print_safe("Status: NO_NEW_CHAPTERS_FOUND (No new chapters detected in source relative to database).")
    else:
        print_safe(f"Status: NEW_CHAPTERS_DETECTED (Found {len(plan['new_chapters_to_ingest'])} new chapters to ingest).")

    if args.json:
        # Output summary to stdout
        summary = {
            "status": plan["status"],
            "current_last_chapter": plan["current_last_chapter"],
            "detected_source_last_chapter": plan["detected_source_last_chapter"],
            "new_chapters_count": len(plan["new_chapters_to_ingest"])
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
