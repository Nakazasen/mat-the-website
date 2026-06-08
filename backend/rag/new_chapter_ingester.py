import os
import re
import sys
from typing import List, Dict, Any, Optional

# Path resolution
backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.rag.chunking import (
    normalize_story_text,
    chunk_text,
    estimate_token_count,
    stable_content_hash
)
from backend.rag.new_chapter_source_reader import (
    validate_new_chapter_source,
    build_new_chapter_manifest
)

def build_chunks_for_new_chapter(chapter: Dict[str, Any], max_chars: int = 3500, overlap_chars: int = 450) -> List[Dict[str, Any]]:
    """Generates chunk payloads for a given parsed chapter (without chapter_id)."""
    chapter_number = chapter["chapter_number"]
    title = chapter["title"]
    content = chapter["content"]
    
    # 1. Normalize
    normalized_text = normalize_story_text(content)
    
    # 2. Chunk
    chunks = chunk_text(normalized_text, max_chars=max_chars, overlap_chars=overlap_chars)
    
    payloads = []
    for idx, chunk in enumerate(chunks):
        chunk_hash = stable_content_hash(chunk)
        token_count = estimate_token_count(chunk)
        char_count = len(chunk)
        
        metadata = {
            "chapter_number": chapter_number,
            "chapter_title": title,
            "chunk_index": idx,
            "source": "r2_chapter" if "source_path" not in chapter else "local_intake_chapter",
            "rag_version": "phase_3a_no_embedding"
        }
        
        payload = {
            "chapter_id": None, # Filled after inserting chapter
            "chapter_number": chapter_number,
            "chapter_title": title,
            "chunk_index": idx,
            "content": chunk,
            "content_plain": chunk,
            "token_count": token_count,
            "char_count": char_count,
            "content_hash": chunk_hash,
            "metadata": metadata,
            "embedding": None
        }
        payloads.append(payload)
        
    return payloads

def build_new_chapter_db_plan(chapters: List[Dict[str, Any]], current_last_chapter: int, strict: bool = True) -> Dict[str, Any]:
    """Validates source chapters and builds the dry-run insertion plan."""
    manifest = build_new_chapter_manifest(chapters, current_last_chapter, strict=strict)
    if not manifest["ok"]:
        return {
            "ok": False,
            "errors": manifest["errors"],
            "warnings": [],
            "planned_chapter_inserts": [],
            "planned_chunk_inserts_count": 0
        }
        
    planned_chapters = []
    total_chunks = 0
    
    # Manifest new chapters are valid candidates
    # Let's map original chapter info (content) to planned chapters list
    chapter_map = {c["chapter_number"]: c for c in chapters}
    
    for val_ch in manifest["new_chapters"]:
        ch_num = val_ch["chapter_number"]
        orig_ch = chapter_map[ch_num]
        
        # Estimate words
        word_count = len(orig_ch["content"].split())
        
        # Build placeholder R2 URL
        slug = f"chuong-{ch_num}"
        # A simple slugify matching backend
        title_slug = re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', orig_ch["title"].lower()).strip())
        if title_slug:
            slug = f"{slug}-{title_slug}"
        content_url = f"https://local-placeholder/chapters/{ch_num:04d}-{slug}.txt"
        
        planned_chapters.append({
            "chapter_number": ch_num,
            "title": orig_ch["title"],
            "content_url": content_url,
            "word_count": word_count,
            "is_side_story": False,
            "content": orig_ch["content"] # temporary field for processing chunks
        })
        
        chunks = build_chunks_for_new_chapter(orig_ch)
        total_chunks += len(chunks)
        
    return {
        "ok": True,
        "mode": "DRY_RUN",
        "current_last_chapter": current_last_chapter,
        "new_chapters_detected": [c["chapter_number"] for c in planned_chapters],
        "planned_chapter_inserts": [
            {
                "chapter_number": c["chapter_number"],
                "title": c["title"],
                "content_url": c["content_url"],
                "word_count": c["word_count"],
                "is_side_story": c["is_side_story"]
            } for c in planned_chapters
        ],
        "planned_chunk_inserts_count": total_chunks,
        "raw_planned_chapters": planned_chapters, # internal use
        "errors": [],
        "warnings": []
    }

def clear_oracle_cache_for_chapter(supabase, chapter_number: int, dry_run: bool = True) -> int:
    """Selective invalidation: clear oracle cache queries with progress >= new chapter number."""
    if not supabase:
        return 0
    try:
        res = supabase.table("oracle_cache").select("question_hash, chapter_cap").gte("chapter_cap", chapter_number).execute()
        rows = res.data or []
        if not rows:
            return 0
        if dry_run:
            return len(rows)
            
        count = 0
        for r in rows:
            qh = r.get("question_hash")
            cc = r.get("chapter_cap")
            if qh and cc is not None:
                supabase.table("oracle_cache").delete().eq("question_hash", qh).eq("chapter_cap", cc).execute()
                count += 1
        return count
    except Exception as e:
        print(f"Warning: Failed to clear oracle cache for chapter {chapter_number}: {e}")
        return 0

def insert_chapters_and_chunks(supabase, plan: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
    """Performs database insertions and clear oracle cache. Re-evaluates R2 upload if configured."""
    if not plan.get("ok"):
        return {
            "mode": "DRY_RUN" if dry_run else "WRITE",
            "ok": False,
            "errors": plan.get("errors", ["Invalid plan"]),
            "chapters_inserted": 0,
            "story_chunks_inserted": 0,
            "cache_rows_deleted": 0
        }
        
    planned_chapters = plan.get("raw_planned_chapters", [])
    if not planned_chapters:
        return {
            "mode": "DRY_RUN" if dry_run else "WRITE",
            "ok": True,
            "chapters_inserted": 0,
            "story_chunks_inserted": 0,
            "cache_rows_deleted": 0,
            "errors": []
        }
        
    if dry_run:
        return {
            "mode": "DRY_RUN",
            "ok": True,
            "chapters_inserted": len(planned_chapters),
            "story_chunks_inserted": plan["planned_chunk_inserts_count"],
            "cache_rows_deleted": 0,
            "errors": []
        }
        
    # Live write mode
    if not supabase:
        return {
            "mode": "WRITE",
            "ok": False,
            "errors": ["Supabase client not initialized"],
            "chapters_inserted": 0,
            "story_chunks_inserted": 0,
            "cache_rows_deleted": 0
        }
        
    # Check R2 credentials in environment to upload chapter if possible
    r2_client = None
    R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID") or os.getenv("R2_ACCESS_KEY")
    R2_SECRET_KEY = os.getenv("R2_SECRET_ACCESS_KEY") or os.getenv("R2_SECRET_KEY")
    R2_ENDPOINT = os.getenv("R2_ENDPOINT_URL") or os.getenv("R2_ENDPOINT")
    R2_BUCKET = os.getenv("R2_BUCKET_NAME", "mat-the")
    R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL") or os.getenv("R2_PUBLIC_BASE_URL") or ""
    
    if R2_ACCESS_KEY and R2_SECRET_KEY and R2_ENDPOINT:
        try:
            import boto3
            from botocore.config import Config
            r2_client = boto3.client(
                's3',
                endpoint_url=R2_ENDPOINT,
                aws_access_key_id=R2_ACCESS_KEY,
                aws_secret_access_key=R2_SECRET_KEY,
                config=Config(signature_version='s3v4'),
                region_name='auto',
            )
        except Exception as e:
            print(f"Warning: Failed to init boto3 client: {e}")
            
    chapters_inserted_count = 0
    story_chunks_inserted_count = 0
    cache_rows_deleted = 0
    errors = []
    
    for ch in planned_chapters:
        ch_num = ch["chapter_number"]
        title = ch["title"]
        content = ch["content"]
        word_count = ch["word_count"]
        is_side_story = ch["is_side_story"]
        
        final_content_url = ch["content_url"]
        
        # Perform R2 upload if client is available
        if r2_client and R2_PUBLIC_URL:
            try:
                slug = f"chuong-{ch_num}"
                title_slug = re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', title.lower()).strip())
                if title_slug:
                    slug = f"{slug}-{title_slug}"
                object_key = f"chapters/{ch_num:04d}-{slug}.txt"
                
                r2_client.put_object(
                    Bucket=R2_BUCKET,
                    Key=object_key,
                    Body=content.encode("utf-8"),
                    ContentType="text/plain; charset=utf-8"
                )
                final_content_url = f"{R2_PUBLIC_URL}/{object_key}"
            except Exception as e:
                # Log but continue with placeholder url fallback
                print(f"Warning: R2 upload failed for chapter {ch_num}: {e}")
                
        # 1. Insert into chapters table
        chapter_payload = {
            "chapter_number": ch_num,
            "title": title,
            "content_url": final_content_url,
            "word_count": word_count,
            "is_side_story": is_side_story
        }
        
        try:
            res_chapter = supabase.table("chapters").insert(chapter_payload).execute()
            if not res_chapter.data:
                raise ValueError("Insert returned no data.")
            chapter_id = res_chapter.data[0]["id"]
            chapters_inserted_count += 1
            
            # 2. Build chunks with correct chapter_id
            chunks = build_chunks_for_new_chapter(ch)
            for chunk in chunks:
                chunk["chapter_id"] = chapter_id
                
            # 3. Insert chunks into story_chunks
            if chunks:
                supabase.table("story_chunks").insert(chunks).execute()
                story_chunks_inserted_count += len(chunks)
                
            # 4. Clear cache for terms/chapters
            cleared = clear_oracle_cache_for_chapter(supabase, ch_num, dry_run=False)
            cache_rows_deleted += cleared
            
        except Exception as e:
            err_msg = f"Failed to ingest chapter {ch_num}: {e}"
            errors.append(err_msg)
            print(f"Error: {err_msg}")
            
    ok = len(errors) == 0
    return {
        "mode": "WRITE",
        "ok": ok,
        "chapters_inserted": chapters_inserted_count,
        "story_chunks_inserted": story_chunks_inserted_count,
        "cache_rows_deleted": cache_rows_deleted,
        "errors": errors
    }
