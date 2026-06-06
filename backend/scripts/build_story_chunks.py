#!/usr/bin/env python3
"""
Build Story Chunks Script
Processes novel chapters, cleans up HTML, breaks content into RAG-friendly chunks,
and outputs a summary report. Supports dry-run by default.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Try imports
try:
    from backend.database import supabase
except ImportError:
    supabase = None

try:
    from backend.main import fetch_r2_content
except ImportError:
    import httpx
    def fetch_r2_content(content_url: str) -> str:
        response = httpx.get(content_url, timeout=20.0)
        response.raise_for_status()
        return response.text

from backend.rag.chunking import (
    strip_html_to_text,
    normalize_story_text,
    estimate_token_count,
    chunk_text,
    stable_content_hash,
)

SAMPLE_HTML = """
<div class="chapter-content">
    <p>Đây là nội dung chương truyện mạt thế giả lập để kiểm tra thuật toán chunking.</p>
    <p>Nhân vật chính Diệp Phàm bước đi trong màn đêm tĩnh mịch. Gió lạnh rít gào qua các khe nứt của tòa nhà đổ nát.</p>
    <p>Bất ngờ, một bóng đen lao ra từ góc tối! Đó là một con tang thi cấp 1 hung tợn. Diệp Phàm nhanh nhẹn né tránh và vung đao kết liễu nó.</p>
    <p>Hệ thống vang lên âm thanh lạnh lùng: "Tiêu diệt tang thi cấp 1, nhận 1 điểm tích lũy."</p>
    <script>console.log("Mật thế sinh hóa nguy cơ");</script>
    <style>.chapter-content { font-size: 16px; }</style>
</div>
"""

async def process_chapter(chapter_num: int, title: str, content_html: str, args):
    # 1. Clean HTML to plain text
    plain_text = strip_html_to_text(content_html)
    
    # 2. Normalize text
    normalized_text = normalize_story_text(plain_text)
    
    # 3. Chunk text
    chunks = chunk_text(
        normalized_text, 
        max_chars=args.max_chars, 
        overlap_chars=args.overlap_chars
    )
    
    total_chars = len(normalized_text)
    estimated_tokens = estimate_token_count(normalized_text)
    
    # Report
    print("-" * 60)
    print(f"Chapter Number   : {chapter_num}")
    print(f"Title            : {title}")
    print(f"Chunks Count     : {len(chunks)}")
    print(f"Total Chars      : {total_chars}")
    print(f"Estimated Tokens : {estimated_tokens}")
    
    if chunks:
        first_chunk = chunks[0]
        preview = first_chunk[:200].replace("\n", " ") + "..." if len(first_chunk) > 200 else first_chunk
        print(f"First Chunk Preview: {preview}")
    else:
        print("First Chunk Preview: (No chunks generated)")
        
    # Database operations
    if args.write and not args.dry_run:
        if not supabase:
            print("Error: Supabase client is not initialized. Cannot write to DB.")
            return len(chunks)
            
        print(f"Writing {len(chunks)} chunks to Database...")
        for idx, chunk in enumerate(chunks):
            chunk_hash = stable_content_hash(chunk)
            payload = {
                "chapter_number": chapter_num,
                "chapter_title": title,
                "chunk_index": idx,
                "content": chunk,
                "content_plain": chunk,
                "token_count": estimate_token_count(chunk),
                "char_count": len(chunk),
                "content_hash": chunk_hash,
                "metadata": {"source": "build_story_chunks_script_cli"},
            }
            try:
                # Upsert table
                supabase.table("story_chunks").upsert(
                    payload, 
                    on_conflict="chapter_number,chunk_index,content_hash"
                ).execute()
            except Exception as e:
                print(f"Error writing chunk {idx}: {e}")
    else:
        if args.write:
            print("[DRY-RUN] DB Write simulated (use --no-dry-run to write to DB)")
            
    return len(chunks)

async def main_async():
    parser = argparse.ArgumentParser(description="Dry-run story chunking builder")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run without writing to database (default: True)")
    parser.add_argument("--no-dry-run", dest="dry-run", action="store_false", help="Disable dry-run mode (allow DB writing)")
    parser.add_argument("--write", action="store_true", default=False, help="Perform database operations")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of chapters to process")
    parser.add_argument("--chapter-number", type=int, default=None, help="Process specific chapter number")
    parser.add_argument("--max-chars", type=int, default=3500, help="Maximum characters per chunk")
    parser.add_argument("--overlap-chars", type=int, default=450, help="Overlap characters between chunks")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RAG Story Chunking Runner")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE-DB-WRITE'}")
    print(f"Write flag: {args.write}")
    print(f"Chunk Config: Max chars = {args.max_chars}, Overlap = {args.overlap_chars}")
    print("=" * 60)
    
    # Check if database is accessible and if we can query it
    chapters = []
    if supabase:
        try:
            query = supabase.table("chapters").select("id, chapter_number, title, content_url").order("chapter_number")
            if args.chapter_number is not None:
                query = query.eq("chapter_number", args.chapter_number)
            if args.limit is not None:
                query = query.limit(args.limit)
                
            resp = query.execute()
            if resp.data:
                chapters = resp.data
                print(f"Fetched {len(chapters)} chapters from Supabase database.")
        except Exception as e:
            print(f"Warning: Failed to fetch chapters from DB: {e}")
            
    if not chapters:
        print("Using sample mock text mode...")
        mock_chapter = {
            "chapter_number": args.chapter_number or 1,
            "title": "Chương 1: Ngày Tận Thế Bắt Đầu (Sample Mock)",
            "content_html": SAMPLE_HTML
        }
        chapters = [mock_chapter]
        
    total_chunks = 0
    for ch in chapters:
        chapter_num = ch.get("chapter_number")
        title = ch.get("title", f"Chương {chapter_num}")
        
        # Resolve content
        content_html = ch.get("content_html")
        if not content_html:
            content_url = ch.get("content_url")
            if content_url:
                try:
                    content_html = fetch_r2_content(content_url)
                except Exception as e:
                    print(f"Error fetching R2 content for chapter {chapter_num}: {e}")
                    print("Using sample mock text fallback for this chapter.")
                    content_html = SAMPLE_HTML
            else:
                content_html = SAMPLE_HTML
                
        chunks_count = await process_chapter(chapter_num, title, content_html, args)
        total_chunks += chunks_count
        
    print("=" * 60)
    print(f"Process completed. Total chunks generated: {total_chunks}")
    print("=" * 60)

if __name__ == "__main__":
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
    asyncio.run(main_async())

