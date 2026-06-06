#!/usr/bin/env python3
"""
Build RAG Context Demo Script
Retrieves story chunks for a query and compiles them into a RAG context block.
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

from backend.rag.retrieval import search_story_chunks_hybrid_lexical
from backend.rag.context_builder import build_rag_context_block

def main():
    # Ensure stdout/stderr handles UTF-8 on Windows environments
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

    parser = argparse.ArgumentParser(description="Build RAG context from search query")
    parser.add_argument("--query", type=str, required=True, help="Search query string")
    parser.add_argument("--chapter-cap", type=int, default=None, help="Spoiler protection cap (chapter number <= N)")
    parser.add_argument("--limit", type=int, default=5, help="Maximum search results to retrieve")
    parser.add_argument("--max-chunks", type=int, default=5, help="Maximum chunks to use in context block")
    parser.add_argument("--max-total-chars", type=int, default=6000, help="Maximum character length of final context block")

    args = parser.parse_args()

    print("=" * 60)
    print("RAG Context Builder Demo CLI")
    print(f"Query          : {args.query}")
    print(f"Chapter Cap    : {args.chapter_cap}")
    print(f"Search Limit   : {args.limit}")
    print(f"Max Chunks     : {args.max_chunks}")
    print(f"Max Total Chars: {args.max_total_chars}")
    print("=" * 60)

    if not supabase:
        print("Error: Supabase client is not initialized.")
        sys.exit(1)

    # 1. Retrieve matching chunks using hybrid lexical search
    results = search_story_chunks_hybrid_lexical(
        supabase=supabase,
        query=args.query,
        chapter_cap=args.chapter_cap,
        limit=args.limit
    )

    # 2. Compile chunks into a unified RAG context block
    context_data = build_rag_context_block(
        results=results,
        max_chunks=args.max_chunks,
        max_total_chars=args.max_total_chars
    )

    print(f"Chunks Used    : {context_data['chunks_used']}")
    print(f"Total Chars    : {context_data['total_chars']}")
    print(f"Source         : {context_data['source']}")
    print("=" * 60)

    print("Citations:")
    for idx, cite in enumerate(context_data['citations']):
        print(f" [{idx + 1}] Chương {cite['chapter_number']} - {cite['chapter_title']} | chunk {cite['chunk_index']} (hash: {cite['content_hash'][:10]})")
    print("-" * 60)

    print("Context Preview:")
    context_text = context_data['context_text']
    if len(context_text) > 800:
        print(context_text[:800] + "\n... [TRUNCATED PREVIEW] ...")
    else:
        print(context_text)
    print("=" * 60)

if __name__ == "__main__":
    main()
