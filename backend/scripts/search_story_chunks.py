#!/usr/bin/env python3
"""
Search Story Chunks Script
Performs full-text search on the story_chunks table using PostgreSQL GIN index.
"""

import argparse
import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from backend.database import supabase
except ImportError:
    supabase = None

from backend.rag.retrieval import (
    search_story_chunks_text,
    search_story_chunks_hybrid_lexical,
)

def main():
    # Ensure stdout/stderr handles UTF-8 on Windows environments (like cp932)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Search on story_chunks table")
    parser.add_argument("--query", type=str, required=True, help="Search query string")
    parser.add_argument("--chapter-cap", type=int, default=None, help="Spoiler protection cap (chapter number <= N)")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results to retrieve")
    parser.add_argument("--mode", type=str, choices=["fts", "hybrid"], default="hybrid", help="Search mode (fts or hybrid, default: hybrid)")

    args = parser.parse_args()

    print("=" * 60)
    print("RAG Search Retrieval CLI")
    print(f"Query          : {args.query}")
    print(f"Chapter Cap    : {args.chapter_cap}")
    print(f"Limit          : {args.limit}")
    print(f"Mode           : {args.mode}")
    print("=" * 60)

    if not supabase:
        print("Error: Supabase client is not initialized.")
        sys.exit(1)

    if args.mode == "hybrid":
        results = search_story_chunks_hybrid_lexical(
            supabase=supabase,
            query=args.query,
            chapter_cap=args.chapter_cap,
            limit=args.limit
        )
    else:
        results = search_story_chunks_text(
            supabase=supabase,
            query=args.query,
            chapter_cap=args.chapter_cap,
            limit=args.limit
        )

    print(f"Results Count  : {len(results)}")
    print("=" * 60)

    for idx, r in enumerate(results):
        print(f"Result #{idx + 1}")
        print(f"Chapter        : {r['chapter_number']}")
        print(f"Title          : {r['chapter_title']}")
        print(f"Chunk Index    : {r['chunk_index']}")
        print(f"Preview        : {r['content_preview']}")
        print(f"Source         : {r['source']}")
        if "score" in r:
            print(f"Score          : {r['score']}")
        if "match_reasons" in r:
            print(f"Match Reasons  : {', '.join(r['match_reasons'])}")
        print("-" * 60)

if __name__ == "__main__":
    main()
