#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any

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

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Audit story growth coverage across chapters and story_chunks.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_story_growth_coverage_audit.json", help="Output JSON path.")
    parser.add_argument("--json", action="store_true", help="Format output as JSON on stdout.")
    args = parser.parse_args()

    print_safe("Auditing story growth coverage from Supabase...")
    
    if not supabase:
        print_safe("Error: Supabase client is not initialized.")
        sys.exit(1)

    # 1. Fetch all chapter numbers from `chapters` table (source)
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

    # 2. Fetch all chapter numbers from `story_chunks` table (existing chunks)
    chunk_chapters = []
    chunk_counts = {}
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
                        ch_val = int(ch)
                        chunk_chapters.append(ch_val)
                        chunk_counts[ch_val] = chunk_counts.get(ch_val, 0) + 1
                    except (ValueError, TypeError):
                        pass
            if len(data) < limit:
                break
            offset += limit
        except Exception as e:
            print_safe(f"Error querying story_chunks table: {e}")
            sys.exit(1)

    # Calculate statistics
    unique_source = sorted(list(set(source_chapters)))
    unique_chunked = sorted(list(set(chunk_chapters)))

    min_source_chapter = unique_source[0] if unique_source else None
    max_source_chapter = unique_source[-1] if unique_source else None
    
    min_chunked_chapter = unique_chunked[0] if unique_chunked else None
    max_chunked_chapter = unique_chunked[-1] if unique_chunked else None

    # Duplicate chapter numbers in source chapters
    duplicate_source = []
    seen = set()
    for ch in source_chapters:
        if ch in seen:
            duplicate_source.append(ch)
        seen.add(ch)
    duplicate_source = sorted(list(set(duplicate_source)))

    # Missing chapter numbers in source sequence (1 to max_source)
    missing_source_seq = []
    if max_source_chapter:
        missing_source_seq = sorted(list(set(range(1, max_source_chapter + 1)) - set(source_chapters)))

    # Missing chapter numbers in chunked compared to source
    missing_in_chunks = sorted(list(set(source_chapters) - set(chunk_chapters)))

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_summary": {
            "total_records": len(source_chapters),
            "unique_chapters_count": len(unique_source),
            "min_chapter": min_source_chapter,
            "max_chapter": max_source_chapter,
            "duplicate_chapters": duplicate_source,
            "missing_in_sequence": missing_source_seq
        },
        "chunked_summary": {
            "total_chunks": len(chunk_chapters),
            "unique_chapters_count": len(unique_chunked),
            "min_chapter": min_chunked_chapter,
            "max_chapter": max_chunked_chapter,
            "missing_relative_to_source": missing_in_chunks
        },
        "chunk_count_by_chapter": {str(ch): count for ch, count in sorted(chunk_counts.items())},
        "last_known_chapter": max_chunked_chapter
    }

    # Save output to JSON
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print_safe(f"Story growth coverage audit report saved to: {output_path}")

    if args.json:
        # Output summary to stdout
        summary = {
            "source_unique_chapters": len(unique_source),
            "source_max_chapter": max_source_chapter,
            "chunked_unique_chapters": len(unique_chunked),
            "chunked_max_chapter": max_chunked_chapter,
            "missing_in_chunks_count": len(missing_in_chunks),
            "duplicate_source_count": len(duplicate_source)
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
