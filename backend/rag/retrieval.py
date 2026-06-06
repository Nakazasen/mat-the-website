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

def extract_search_keywords(query: str) -> list[str]:
    """Extracts unique lowercase search keywords of length >= 3 for fallback queries."""
    normalized = normalize_search_query(query)
    if not normalized:
        return []
    words = [w.strip().lower() for w in re.split(r"[^\w\u00C0-\u024FĐđ]+", normalized) if w.strip()]

    seen = set()
    deduped = []
    for w in words:
        if w not in seen and len(w) >= 3:
            seen.add(w)
            deduped.append(w)
    return deduped

def score_lexical_result(row: dict, query: str, keywords: list[str]) -> tuple[float, list[str]]:
    """Calculates a lexical relevance score and reasons for a retrieved chunk row."""
    title = (row.get("chapter_title") or "").strip()
    content = (row.get("content_plain") or row.get("content") or "").strip()

    score = 0.0
    reasons = []

    query_lower = query.lower().strip()
    title_lower = title.lower()
    content_lower = content.lower()

    # 1. Full phrase in chapter title (+100)
    if query_lower and query_lower in title_lower:
        score += 100.0
        reasons.append("title_phrase")

    # 2. Full phrase in chunk content (+80)
    if query_lower and query_lower in content_lower:
        score += 80.0
        reasons.append("content_phrase")

    # 3. FTS index match (+40)
    if row.get("temp_fts_match"):
        score += 40.0
        reasons.append("fts")

    # 4. Individual keyword matches in chapter title (+10 each)
    for kw in keywords:
        if kw in title_lower:
            score += 10.0
            reasons.append(f"title_keyword:{kw}")

    # 5. Individual keyword matches in chunk content (+5 each)
    for kw in keywords:
        if kw in content_lower:
            score += 5.0
            reasons.append(f"content_keyword:{kw}")

    return score, reasons

def merge_retrieval_results(result_lists: list[list[dict]], query: str, limit: int) -> list[dict]:
    """Deduplicates, scores, sorts, and formats retrieval results from multiple queries."""
    keywords = extract_search_keywords(query)
    unique_results = {}

    for results in result_lists:
        for r in results:
            h = r.get("content_hash")
            if not h:
                continue

            if h not in unique_results:
                # Shallow copy to avoid mutating original rows
                unique_results[h] = dict(r)
            else:
                if r.get("temp_fts_match"):
                    unique_results[h]["temp_fts_match"] = True

    scored_list = []
    for r in unique_results.values():
        score, reasons = score_lexical_result(r, query, keywords)

        content = r.get("content", "")
        content_plain = r.get("content_plain", "")
        plain = content_plain if content_plain else content
        preview = plain[:200] + "..." if len(plain) > 200 else plain

        match_reasons = []
        if "title_phrase" in reasons:
            match_reasons.append("title_phrase")
        if "content_phrase" in reasons:
            match_reasons.append("content_phrase")
        if any(w.startswith("title_keyword:") for w in reasons):
            match_reasons.append("title_keyword")
        if any(w.startswith("content_keyword:") for w in reasons):
            match_reasons.append("content_keyword")
        if "fts" in reasons:
            match_reasons.append("fts")

        formatted = {
            "chapter_number": r.get("chapter_number"),
            "chapter_title": r.get("chapter_title"),
            "chunk_index": r.get("chunk_index"),
            "content_preview": preview,
            "content_plain": plain,
            "content_hash": r.get("content_hash"),
            "score": score,
            "source": "story_chunks_hybrid_lexical",
            "match_reasons": match_reasons
        }
        scored_list.append(formatted)

    # Sort by score (DESC), chapter_number (ASC), chunk_index (ASC)
    # chapter_number ASC prioritizes earlier information and acts as a spoiler buffer
    scored_list.sort(key=lambda item: (
        -item["score"],
        item["chapter_number"] or 9999,
        item["chunk_index"] or 0
    ))

    return scored_list[:limit]

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

def search_story_chunks_hybrid_lexical(
    supabase,
    query: str,
    chapter_cap: int | None = None,
    limit: int = 5
) -> list[dict]:
    """
    Performs hybrid lexical search by querying PostgreSQL FTS, ILIKE phrase,
    and ILIKE keywords, then merges and ranks the results using scoring rules.
    """
    if not query or not query.strip():
        return []

    if not supabase:
        print("Warning: Supabase client is None. Cannot perform hybrid search.")
        return []

    result_lists = []

    # 1. Full-text search (simple config)
    fts_results = []
    tsquery = build_tsquery_terms(query)
    if tsquery:
        try:
            q = supabase.table("story_chunks").select("*")
            if chapter_cap is not None:
                q = q.lte("chapter_number", chapter_cap)
            q = q.limit(limit * 2)
            q = q.text_search("content_plain", tsquery, options={"config": "simple"})
            resp = q.execute()
            for row in resp.data or []:
                row["temp_fts_match"] = True
                fts_results.append(row)
        except Exception as e:
            print(f"FTS query error: {e}")
    result_lists.append(fts_results)

    # 2. ILIKE phrase matching in content_plain
    phrase_content_results = []
    try:
        q = supabase.table("story_chunks").select("*").ilike("content_plain", f"%{query.strip()}%")
        if chapter_cap is not None:
            q = q.lte("chapter_number", chapter_cap)
        q = q.limit(limit * 2)
        resp = q.execute()
        phrase_content_results = resp.data or []
    except Exception as e:
        print(f"ILIKE phrase content query error: {e}")
    result_lists.append(phrase_content_results)

    # 3. ILIKE phrase matching in chapter_title
    phrase_title_results = []
    try:
        q = supabase.table("story_chunks").select("*").ilike("chapter_title", f"%{query.strip()}%")
        if chapter_cap is not None:
            q = q.lte("chapter_number", chapter_cap)
        q = q.limit(limit * 2)
        resp = q.execute()
        phrase_title_results = resp.data or []
    except Exception as e:
        print(f"ILIKE phrase title query error: {e}")
    result_lists.append(phrase_title_results)

    # 4. Fallback: individual keyword matching (OR)
    keyword_results = []
    keywords = extract_search_keywords(query)
    if keywords:
        or_parts = []
        for kw in keywords:
            or_parts.append(f"chapter_title.ilike.%{kw}%")
            or_parts.append(f"content_plain.ilike.%{kw}%")

        if or_parts:
            try:
                q = supabase.table("story_chunks").select("*").or_(",".join(or_parts))
                if chapter_cap is not None:
                    q = q.lte("chapter_number", chapter_cap)
                q = q.limit(limit * 2)
                resp = q.execute()
                keyword_results = resp.data or []
            except Exception as e:
                print(f"ILIKE keywords query error: {e}")
    result_lists.append(keyword_results)

    # Merge, score, deduplicate, and limit
    return merge_retrieval_results(result_lists, query, limit)
