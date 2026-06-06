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

def extract_chapters_from_query(query: str) -> list[int]:
    query_lower = query.lower()
    chapters = []

    # Match patterns like "chương 5-6", "chương 5 - 6", "chương 5 đến 6"
    range_matches = re.findall(r'chương\s*(\d+)\s*(?:-|đến)\s*(\d+)', query_lower)
    for start, end in range_matches:
        try:
            s, e = int(start), int(end)
            if s <= e:
                chapters.extend(range(s, e + 1))
        except ValueError:
            pass

    # Match pattern like "chương 5" or "chương 5, 6"
    single_matches = re.finditer(r'chương\s*(\d+)(?:\s*,\s*(\d+))?', query_lower)
    for m in single_matches:
        try:
            chapters.append(int(m.group(1)))
            if m.group(2):
                chapters.append(int(m.group(2)))
        except ValueError:
            pass

    return list(set(chapters))

def extract_search_keywords(query: str) -> list[str]:
    """Extracts unique lowercase search keywords of length >= 2 for fallback queries."""
    normalized = normalize_search_query(query)
    if not normalized:
        return []
    words = [w.strip().lower() for w in re.split(r"[^\w\u00C0-\u024FĐđ]+", normalized) if w.strip()]

    seen = set()
    deduped = []
    for w in words:
        if w not in seen and len(w) >= 2:
            seen.add(w)
            deduped.append(w)
    return deduped

STOP_WORDS = {
    "là", "và", "của", "trong", "có", "ở", "này", "cái", "gì", "ai", "đây", "đó",
    "nào", "được", "để", "cho", "với", "như", "những", "các", "tại", "thì", "mà",
    "the", "and", "of", "in", "to", "a", "is", "that", "it", "on", "for", "with"
}

def get_keywords_proximity_boost(content_lower: str, non_stop_kws: list[str]) -> float:
    """Calculates a score boost if non-stop keywords appear near each other in the content."""
    if len(non_stop_kws) < 2:
        return 0.0

    # Find all start positions for each non-stop keyword (using \b boundaries to avoid partial match)
    indices = []
    for kw in non_stop_kws:
        positions = [m.start() for m in re.finditer(r'\b' + re.escape(kw) + r'\b', content_lower)]
        if positions:
            indices.append((kw, positions))

    # Need at least 2 distinct keywords present in the content
    if len(indices) < 2:
        return 0.0

    # Flatten positions into a single list of (pos, keyword)
    all_positions = []
    for kw, positions in indices:
        for pos in positions:
            all_positions.append((pos, kw))
    all_positions.sort()

    min_span = float('inf')
    # Find minimum character span containing at least 2 distinct keywords
    for i in range(len(all_positions)):
        seen_kws = {all_positions[i][1]}
        for j in range(i + 1, len(all_positions)):
            seen_kws.add(all_positions[j][1])
            if len(seen_kws) >= 2:
                span = all_positions[j][0] - all_positions[i][0]
                if span < min_span:
                    min_span = span
                break

    if min_span < 100:
        return 50.0
    elif min_span < 200:
        return 25.0
    return 0.0

def score_lexical_result(row: dict, query: str, keywords: list[str]) -> tuple[float, list[str]]:
    """Calculates an improved lexical relevance score and reasons for a retrieved chunk row."""
    title = (row.get("chapter_title") or "").strip()
    content = (row.get("content_plain") or row.get("content") or "").strip()
    chapter_num = row.get("chapter_number")

    score = 0.0
    reasons = []

    query_lower = query.lower().strip()
    title_lower = title.lower()
    content_lower = content.lower()

    # 1. Full phrase in chapter title (+150)
    if query_lower and query_lower in title_lower:
        score += 150.0
        reasons.append("title_phrase")

    # 2. Full phrase in chunk content (+100)
    if query_lower and query_lower in content_lower:
        score += 100.0
        reasons.append("content_phrase")

    # 3. FTS index match (+40)
    if row.get("temp_fts_match"):
        score += 40.0
        reasons.append("fts")

    # 4. Individual keyword matches in chapter title and content (using \b boundaries to avoid partial match)
    non_stop_kws = []
    matched_non_stop = []
    for kw in keywords:
        is_stop = kw in STOP_WORDS
        if not is_stop:
            non_stop_kws.append(kw)

        kw_score_title = 2.0 if is_stop else 25.0
        kw_score_content = 1.0 if is_stop else 12.0

        has_title_match = bool(re.search(r'\b' + re.escape(kw) + r'\b', title_lower))
        has_content_match = bool(re.search(r'\b' + re.escape(kw) + r'\b', content_lower))

        if has_title_match:
            score += kw_score_title
            reasons.append(f"title_keyword:{kw}")
            score += 25.0
            reasons.append(f"title_exact_keyword:{kw}")
            if not is_stop:
                matched_non_stop.append(kw)

        if has_content_match:
            score += kw_score_content
            reasons.append(f"content_keyword:{kw}")
            if not is_stop and kw not in matched_non_stop:
                matched_non_stop.append(kw)

    # 5. Proximity boost for non-stop keywords in content
    proximity_boost = get_keywords_proximity_boost(content_lower, non_stop_kws)
    if proximity_boost > 0:
        score += proximity_boost
        reasons.append(f"proximity_boost:{proximity_boost}")

    # 6. Chapter number exact match boost (+150)
    if chapter_num is not None:
        query_chaps = extract_chapters_from_query(query)
        if chapter_num in query_chaps:
            score += 150.0
            reasons.append(f"chapter_match_boost:{chapter_num}")

    # 7. Keyword coverage ratio penalty for multi-keyword queries
    has_chapter_match = any(w.startswith("chapter_match_boost:") for w in reasons)
    if not has_chapter_match and len(non_stop_kws) > 1:
        match_ratio = len(matched_non_stop) / len(non_stop_kws)
        if match_ratio < 0.35:
            score = 0.0
            reasons.append("penalty_low_coverage_zeroed")
        elif match_ratio < 0.6:
            penalty_factor = (match_ratio / 0.6) ** 2
            score *= penalty_factor
            reasons.append(f"penalty_low_coverage_scaled:{penalty_factor:.2f}")

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

    # Calculate dynamic threshold based on number of non-stop keywords
    non_stop_kws = [kw for kw in keywords if kw not in STOP_WORDS]
    n_kws = len(non_stop_kws)
    if n_kws <= 1:
        threshold = 10.0
    elif n_kws == 2:
        threshold = 20.0
    else:
        threshold = 30.0

    scored_list = []
    for r in unique_results.values():
        score, reasons = score_lexical_result(r, query, keywords)

        if score < threshold:
            continue

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
