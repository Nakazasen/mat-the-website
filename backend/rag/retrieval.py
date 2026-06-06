"""
RAG Retrieval Module
Provides full-text search retrieval capabilities on the story_chunks table.
"""

import re

def normalize_search_query(query: str) -> str:
    """Standardizes search queries by removing leading/trailing spaces and collapsing whitespace."""
    if not query:
        return ""
    return re.sub(r"\s+", " ", query.strip())

def build_tsquery_terms(query: str) -> str:
    """Converts a plain text query into a format suitable for Postgres to_tsquery (simple config)."""
    normalized = normalize_search_query(query)
    if not normalized:
        return ""
    
    # Split query into words, matching alphanumeric characters (including Vietnamese accented characters)
    words = [w for w in re.split(r"[^\w\u00C0-\u024FĐđ]+", normalized) if w.strip()]
    if not words:
        return ""
        
    # Join terms with '&' operator for AND matching
    return " & ".join(words)

def format_retrieval_result(row: dict) -> dict:
    """Formats a database row from story_chunks into a clean retrieval result structure."""
    content = row.get("content", "")
    content_plain = row.get("content_plain", "")
    plain = content_plain if content_plain else content
    
    preview = plain[:200] + "..." if len(plain) > 200 else plain
    
    return {
        "chapter_number": row.get("chapter_number"),
        "chapter_title": row.get("chapter_title"),
        "chunk_index": row.get("chunk_index"),
        "content_preview": preview,
        "content_plain": plain,
        "rank": row.get("rank") or 0.0,
        "content_hash": row.get("content_hash"),
        "source": "story_chunks_fts"
    }

def search_story_chunks_text(
    supabase,
    query: str,
    chapter_cap: int | None = None,
    limit: int = 5
) -> list[dict]:
    """
    Searches the story_chunks table using PostgreSQL full-text search.
    Applies spoiler protection by filtering chapter_number <= chapter_cap.
    """
    if not query or not query.strip():
        return []
        
    tsquery = build_tsquery_terms(query)
    if not tsquery:
        return []
        
    if not supabase:
        print("Warning: Supabase client is None. Cannot perform search.")
        return []
        
    try:
        # Build select query on story_chunks table
        q = supabase.table("story_chunks").select("*")
        
        # Spoiler protection filter
        if chapter_cap is not None:
            q = q.lte("chapter_number", chapter_cap)
            
        # Limit results
        q = q.limit(limit)
        
        # Apply full text search using simple configuration matching the index
        q = q.text_search("content_plain", tsquery, options={"config": "simple"})
        
        resp = q.execute()
        results = resp.data or []
        
        return [format_retrieval_result(r) for r in results]
    except Exception as e:
        print(f"Error searching story chunks: {e}")
        return []
