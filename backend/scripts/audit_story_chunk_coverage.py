#!/usr/bin/env python3
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

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Audit story chunk coverage up to 829 chapters.")
    parser.add_argument("--expected-chapters", type=int, default=829, help="Total number of expected chapters.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_story_coverage_report.json", help="Output JSON path.")
    parser.add_argument("--json", action="store_true", help="Format output as JSON on stdout.")
    args = parser.parse_args()

    print_safe(f"Auditing story chunks from database...")
    
    all_chapters = set()
    chunk_counts = {}
    
    # Query chapter_number from story_chunks using pagination
    limit = 1000
    offset = 0
    while True:
        try:
            res = supabase.table("story_chunks")\
                .select("chapter_number")\
                .range(offset, offset + limit - 1)\
                .execute()
            data = res.data or []
            if not data:
                break
            for row in data:
                ch = row.get("chapter_number")
                if ch is not None:
                    try:
                        ch = int(ch)
                        all_chapters.add(ch)
                        chunk_counts[ch] = chunk_counts.get(ch, 0) + 1
                    except (ValueError, TypeError):
                        pass
            if len(data) < limit:
                break
            offset += limit
        except Exception as e:
            print_safe(f"Error querying database: {e}")
            sys.exit(1)
            
    print_safe(f"Processed {offset + len(data) if 'data' in locals() else offset} rows in total.")

    available_chapters = sorted(list(all_chapters))
    expected_set = set(range(1, args.expected_chapters + 1))
    missing_chapters = sorted(list(expected_set - all_chapters))
    
    min_chapter = min(available_chapters) if available_chapters else None
    max_chapter = max(available_chapters) if available_chapters else None
    
    # Find top 10 sparse chapters (lowest chunk count)
    sparse_chapters = sorted(
        [{"chapter_number": ch, "chunk_count": count} for ch, count in chunk_counts.items()],
        key=lambda x: x["chunk_count"]
    )[:10]
    
    report = {
        "total_chapters_expected": args.expected_chapters,
        "total_chapters_available": len(available_chapters),
        "min_chapter": min_chapter,
        "max_chapter": max_chapter,
        "missing_chapters_count": len(missing_chapters),
        "missing_chapters": missing_chapters,
        "chunk_count_by_chapter": {str(ch): count for ch, count in sorted(chunk_counts.items())},
        "top_sparse_chapters": sparse_chapters
    }
    
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print_safe(f"Story coverage report generated and saved to: {output_path}")
    
    if args.json:
        # Print a short JSON summary to stdout
        summary = {
            "total_chapters_expected": args.expected_chapters,
            "total_chapters_available": len(available_chapters),
            "missing_chapters_count": len(missing_chapters),
            "min_chapter": min_chapter,
            "max_chapter": max_chapter
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
