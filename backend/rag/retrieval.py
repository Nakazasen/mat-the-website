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
        non_stop_keywords = [kw for kw in keywords if kw not in STOP_WORDS]
        search_kws = non_stop_keywords if non_stop_keywords else keywords
        or_parts = []
        for kw in search_kws:
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


def normalize_vietnamese_text(text: str) -> str:
    """Lowercase, strip diacritics, and collapse whitespace for matching."""
    import unicodedata
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text.lower().strip())
    base = "".join(c for c in nfkd if not unicodedata.combining(c))
    base = re.sub(r"[^\w\s]", "", base)
    return re.sub(r"\s+", " ", base).strip()


def is_identity_question(question: str) -> bool:
    """Detects whether a question is an identity/entity identification query."""
    q = question.lower().strip()
    q = re.sub(r"[?\s]+$", "", q)

    suffixes = (
        " là ai", " la ai",
        " là gì", " la gi",
        " là vật phẩm gì", " la vat pham gi",
        " là thực thể gì", " la thuc the gi",
        " là sinh vật gì", " la sinh vat gi",
        " là tổ chức gì", " la to chuc gi",
        " là kỹ năng gì", " la ky nang gi",
        " là nhân vật nào", " la nhan vat nao"
    )
    if q.endswith(suffixes):
        return True

    prefixes = (
        "ai là ", "ai la ",
        "giới thiệu ", "gioi thieu ",
        "thông tin về ", "thong tin ve ",
        "nhân vật ", "nhan vat "
    )
    if q.startswith(prefixes):
        return True

    return False


def extract_entity_name(question: str) -> str:
    """Extracts potential entity/character name from an identity question."""
    q = question.strip()
    q = re.sub(r"[?\s]+$", "", q)
    q_lower = q.lower()

    suffixes = [
        " là vật phẩm gì", " la vat pham gi",
        " là thực thể gì", " la thuc the gi",
        " là sinh vật gì", " la sinh vat gi",
        " là nhân vật nào", " la nhan vat nao",
        " là tổ chức gì", " la to chuc gi",
        " là kỹ năng gì", " la ky nang gi",
        " là ai", " la ai",
        " là gì", " la gi"
    ]
    for suffix in suffixes:
        if q_lower.endswith(suffix):
            return q[:-len(suffix)].strip()

    prefixes = [
        "thông tin về ", "thong tin ve ",
        "giới thiệu ", "gioi thieu ",
        "nhân vật ", "nhan vat ",
        "ai là ", "ai la "
    ]
    for prefix in prefixes:
        if q_lower.startswith(prefix):
            return q[len(prefix):].strip()

    return q


def is_exact_or_near_match(record_name: str, entity_name: str) -> bool:
    """Checks if a record name is an exact or near match for the queried entity name."""
    norm_query_entity = normalize_vietnamese_text(entity_name)
    norm_record_name = normalize_vietnamese_text(record_name)
    if not norm_query_entity or not norm_record_name:
        return False
    is_exact = (norm_query_entity == norm_record_name)
    is_near = (norm_query_entity in norm_record_name or norm_record_name in norm_query_entity)
    if is_exact or is_near:
        return True

    # Tokenize and compute coverage
    query_tokens = [t for t in norm_query_entity.split() if t]
    record_tokens = [t for t in norm_record_name.split() if t]

    important_query_tokens = [t for t in query_tokens if t not in STOP_WORDS]
    important_record_tokens = [t for t in record_tokens if t not in STOP_WORDS]

    overlap_tokens = set(important_query_tokens) & set(important_record_tokens)
    token_coverage = len(overlap_tokens) / len(important_query_tokens) if important_query_tokens else 0.0
    return (token_coverage >= 0.75 and len(overlap_tokens) >= 2)


def search_wiki_entries(
    supabase,
    query: str,
    chapter_cap: int | None = None,
    limit: int = 5
) -> list[dict]:
    """
    Searches the wiki_entries table.
    Note: wiki_entries does not have a chapter column, so no spoiler cap filter is applied here.
    """
    if not query or not query.strip():
        return []
    if not supabase:
        print("Warning: Supabase client is None in search_wiki_entries.")
        return []

    keywords = extract_search_keywords(query)
    if not keywords:
        return []

    try:
        # Build query for matching keywords in title or summary or content (filtering out stop words to avoid query saturation)
        non_stop_keywords = [kw for kw in keywords if kw not in STOP_WORDS]
        search_kws = non_stop_keywords if non_stop_keywords else keywords
        or_parts = []
        for kw in search_kws:
            or_parts.append(f"title.ilike.%{kw}%")
            or_parts.append(f"summary.ilike.%{kw}%")
            or_parts.append(f"content.ilike.%{kw}%")

        q = supabase.table("wiki_entries").select("title, category, summary, content")
        if or_parts:
            q = q.or_(",".join(or_parts))

        resp = q.limit(100).execute()
        rows = resp.data or []

        # Score and rank rows in Python
        scored_rows = []
        query_lower = query.lower().strip()
        for row in rows:
            title = (row.get("title") or "").strip()
            summary = (row.get("summary") or "").strip()
            content = (row.get("content") or "").strip()

            title_lower = title.lower()
            summary_lower = summary.lower()
            content_lower = content.lower()

            score = 0.0
            # Phrase matches
            if query_lower in title_lower:
                score += 100.0
            if query_lower in summary_lower:
                score += 50.0
            if query_lower in content_lower:
                score += 30.0

            # Keyword matches
            for kw in keywords:
                if kw in title_lower:
                    score += 10.0
                if kw in summary_lower:
                    score += 5.0
                if kw in content_lower:
                    score += 2.0

            scored_rows.append((score, row))

        # Sort and return top limit
        scored_rows.sort(key=lambda x: x[0], reverse=True)

        results = []
        non_stop_kws = [kw for kw in keywords if kw not in STOP_WORDS]
        n_kws = len(non_stop_kws)
        threshold = 12.0 if n_kws >= 2 else (5.0 if n_kws == 1 else 0.0)

        for score, row in scored_rows:
            if score < threshold:
                continue
            title = row.get("title", "")

            category = row.get("category", "")
            summary = row.get("summary") or row.get("content") or ""
            results.append({
                "title": title,
                "name": title,
                "type": category,
                "category": category,
                "summary": summary,
                "source": "wiki_entries",
                "quality_class": "canon",
                "confidence": 1.0,
                "evidence": []
            })

        return results[:limit]
    except Exception as e:
        print(f"Error searching wiki entries: {e}")
        return []


def search_provisional_library(
    supabase,
    query: str,
    chapter_cap: int | None = None,
    limit: int = 5
) -> list[dict]:
    """
    Searches the provisional_library table.
    Only allows high_confidence and medium_confidence.
    Filters evidence by chapter_cap.
    """
    if not query or not query.strip():
        return []
    if not supabase:
        print("Warning: Supabase client is None in search_provisional_library.")
        return []

    keywords = extract_search_keywords(query)
    if not keywords:
        return []

    try:
        # Multi-pass retrieval to avoid query saturation on common words
        is_identity = is_identity_question(query)
        entity_name = extract_entity_name(query) if is_identity else ""

        rows = []
        if is_identity and entity_name:
            # Pass 1: Try phrase/exact match on the identity entity name first
            try:
                resp = supabase.table("provisional_library").select("*")\
                    .in_("quality_class", ["high_confidence", "medium_confidence"])\
                    .neq("status", "discard")\
                    .or_(f"name.ilike.%{entity_name}%,summary.ilike.%{entity_name}%")\
                    .limit(100)\
                    .execute()
                rows = resp.data or []
            except Exception as e:
                print(f"Phrase match query error: {e}")

        if not rows:
            # Pass 2: Clean and try phrase match on query (without trailing question marks/identity suffixes)
            clean_query = query.strip()
            clean_query = re.sub(r"[?\s]+$", "", clean_query)
            clean_query = re.sub(
                r"\s+(?:l[àa]\s+(?:g[ìi]|ai)|l[àa]\s+v[ậa]t\s+ph[ẩa]m\s+g[ìi]|l[àa]\s+th[ựu]c\s+th[ểe]\s+g[ìi]|l[àa]\s+sinh\s+v[ậa]t\s+g[ìi]|l[àa]\s+t[ổo]\s+ch[ứu]c\s+g[ìi]|l[àa]\s+k[ỹy]\s+n[ăa]ng\s+g[ìi]|l[àa]\s+nh[âa]n\s+v[ậa]t\s+n[àa]o)$",
                "",
                clean_query,
                flags=re.IGNORECASE
            )
            if clean_query:
                try:
                    resp = supabase.table("provisional_library").select("*")\
                        .in_("quality_class", ["high_confidence", "medium_confidence"])\
                        .neq("status", "discard")\
                        .or_(f"name.ilike.%{clean_query}%,summary.ilike.%{clean_query}%")\
                        .limit(100)\
                        .execute()
                    rows = resp.data or []
                except Exception as e:
                    print(f"Clean query phrase match error: {e}")

        if not rows:
            # Pass 3: Fallback to keyword match OR query (filtering out stop words)
            non_stop_keywords = [kw for kw in keywords if kw not in STOP_WORDS]
            search_kws = non_stop_keywords if non_stop_keywords else keywords
            or_parts = []
            for kw in search_kws:
                or_parts.append(f"name.ilike.%{kw}%")
                or_parts.append(f"summary.ilike.%{kw}%")

            q = supabase.table("provisional_library").select("*")\
                .in_("quality_class", ["high_confidence", "medium_confidence"])\
                .neq("status", "discard")
            if or_parts:
                q = q.or_(",".join(or_parts))

            resp = q.limit(1000).execute()
            rows = resp.data or []

        # Batch-fetch summaries for the retrieved provisional candidates
        pids = [row.get("id") for row in rows if row.get("id")]
        summaries = {}
        if pids:
            try:
                sum_resp = supabase.table("provisional_library_feedback_summary").select("*").in_("provisional_id", pids).execute()
                for s in (sum_resp.data or []):
                    summaries[s.get("provisional_id")] = s
            except Exception as e:
                print(f"Error fetching provisional feedback summaries: {e}")

        # Batch-fetch active patches
        patches = []
        try:
            patch_resp = supabase.table("provisional_library_effective_patches").select("*").eq("effective_status", "active").execute()
            patches = patch_resp.data or []
        except Exception as e:
            print(f"Error fetching provisional knowledge patches: {e}")

        scored_rows = []
        query_lower = query.lower().strip()
        for row in rows:
            pid = row.get("id")
            summary_info = summaries.get(pid) if pid else None

            effective_status = "trusted"
            oracle_policy = "allow"
            dispute_score = 0.0
            total_feedback = 0

            if summary_info:
                effective_status = summary_info.get("effective_status", "trusted")
                oracle_policy = summary_info.get("oracle_policy", "allow")
                dispute_score = float(summary_info.get("dispute_score", 0.0))
                total_feedback = int(summary_info.get("total_feedback", 0))

            if oracle_policy == "block" or effective_status == "hidden_from_oracle":
                continue

            # Apply patches early
            summary_override = None
            type_override = None
            hide_record = False
            deprioritize_record = False
            warn_record = False

            query_norm = " ".join(query.lower().split())
            is_identity = is_identity_question(query)
            entity_name = extract_entity_name(query) if is_identity else ""
            entity_name_norm = " ".join(entity_name.lower().split()) if entity_name else ""

            for patch in patches:
                ptype = patch.get("patch_type")
                target_id = patch.get("target_id")
                target_name = patch.get("target_name")
                qp = patch.get("query_pattern")

                matches_pid = (target_id == pid)

                if ptype == "hide_record" and matches_pid:
                    hide_record = True
                elif ptype == "deprioritize_record" and matches_pid:
                    deprioritize_record = True
                elif ptype == "warn_record" and matches_pid:
                    warn_record = True
                if matches_pid:
                    if patch.get("effective_summary"):
                        summary_override = patch.get("effective_summary")
                    if patch.get("effective_type"):
                        type_override = patch.get("effective_type")
                elif ptype == "suppress_related_for_identity_query":
                    matches_query = False
                    if qp and query_norm == " ".join(qp.lower().split()):
                        matches_query = True
                    elif is_identity and target_name and entity_name_norm == " ".join(target_name.lower().split()):
                        matches_query = True

                    if matches_query:
                        suppressed_ids = patch.get("suppress_record_ids") or []
                        suppressed_patterns = patch.get("suppress_name_patterns") or []
                        if pid in suppressed_ids:
                            hide_record = True
                        elif any(pat.lower() in row.get("name", "").lower() for pat in suppressed_patterns if pat):
                            hide_record = True

            if hide_record:
                continue

            quality_class = row.get("quality_class", "")
            if quality_class not in ["high_confidence", "medium_confidence"]:
                continue
            name = (row.get("name") or "").strip()
            summary = summary_override if summary_override else (row.get("summary") or "").strip()
            confidence = float(row.get("confidence", 0.0))
            first_ch = row.get("first_chapter")

            # Spoiler cap filter
            if chapter_cap is not None:
                if first_ch is not None and first_ch > chapter_cap:
                    continue

            # Filter evidence list programmatically
            evidence = row.get("evidence") or []
            if not isinstance(evidence, list):
                evidence = []
            filtered_evidence = []
            for ev in evidence:
                ch_num = ev.get("chapter_number")
                if chapter_cap is not None and ch_num is not None:
                    try:
                        if int(ch_num) > chapter_cap:
                            continue
                    except (ValueError, TypeError):
                        pass
                filtered_evidence.append(ev)

            if chapter_cap is not None and not filtered_evidence:
                continue

            name_lower = name.lower()
            summary_lower = summary.lower()

            score = 0.0

            if is_identity:
                norm_query_entity = normalize_vietnamese_text(entity_name)
                norm_record_name = normalize_vietnamese_text(name)

                # Tokenize and compute coverage
                query_tokens = [t for t in norm_query_entity.split() if t]
                record_tokens = [t for t in norm_record_name.split() if t]

                important_query_tokens = [t for t in query_tokens if t not in STOP_WORDS]
                important_record_tokens = [t for t in record_tokens if t not in STOP_WORDS]

                overlap_tokens = set(important_query_tokens) & set(important_record_tokens)
                token_coverage = len(overlap_tokens) / len(important_query_tokens) if important_query_tokens else 0.0

                # Precision gates
                is_exact = (norm_query_entity == norm_record_name)
                is_near = (norm_query_entity in norm_record_name or norm_record_name in norm_query_entity)
                is_coverage = (token_coverage >= 0.75 and len(overlap_tokens) >= 2)

                if is_exact or is_near or is_coverage:
                    if is_exact:
                        score = 200.0
                    else:
                        score = 100.0 + token_coverage * 50.0

                    # Type match bonus
                    type_val = type_override if type_override else row.get("type", "")
                    type_val_lower = type_val.lower()
                    type_matched = False
                    if type_val_lower == "item" and any(k in query_lower for k in ["vật phẩm", "vat pham", "tinh thể", "tinh the"]):
                        type_matched = True
                    elif type_val_lower == "ability" and any(k in query_lower for k in ["kỹ năng", "ky nang", "dị năng", "di nang"]):
                        type_matched = True
                    elif type_val_lower == "entity" and any(k in query_lower for k in ["nhân vật", "nhan vat", "zombie"]):
                        type_matched = True

                    if type_matched:
                        score += 30.0

                    score += confidence * 20.0
            else:
                # Phrase matches
                if query_lower in name_lower:
                    score += 100.0
                if query_lower in summary_lower:
                    score += 50.0

                # Keyword matches
                for kw in keywords:
                    if kw in name_lower:
                        score += 10.0
                    if kw in summary_lower:
                        score += 5.0

                # Confidence boost
                if score > 0:
                    score += confidence * 20.0

            if deprioritize_record:
                score = score * 0.2
            elif oracle_policy == "deprioritize":
                score = score * 0.5

            # Deprioritize needs_review strongly
            if row.get("needs_review"):
                score = score * 0.1

            scored_rows.append((score, confidence, row, filtered_evidence, effective_status, oracle_policy, dispute_score, total_feedback, summary_override, type_override, warn_record))

        # Sort by score DESC, confidence DESC
        scored_rows.sort(key=lambda x: (x[0], x[1]), reverse=True)

        results = []
        non_stop_kws = [kw for kw in keywords if kw not in STOP_WORDS]
        n_kws = len(non_stop_kws)
        threshold = 15.0 if n_kws >= 2 else (8.0 if n_kws == 1 else 0.0)

        for score, confidence, row, filtered_evidence, eff_status, pol, disp_score, tot_fb, sum_ovr, typ_ovr, warn_rec in scored_rows:
            if score < threshold:
                continue
            name = row.get("name", "")

            type_val = typ_ovr if typ_ovr else row.get("type", "")
            summary = sum_ovr if sum_ovr else row.get("summary", "")
            quality_class = row.get("quality_class", "")

            # Recalculate first_chapter if needed
            chaps = []
            for ev in filtered_evidence:
                ch_num = ev.get("chapter_number")
                if ch_num is not None:
                    try:
                        chaps.append(int(ch_num))
                    except (ValueError, TypeError):
                        pass
            first_ch = min(chaps) if chaps else row.get("first_chapter")

            display_summary = summary
            if pol == "warn" or eff_status in ("disputed", "duplicate_suspected", "needs_review") or warn_rec or row.get("needs_review"):
                display_summary = f"[CẢNH BÁO CỘNG ĐỒNG: mục này đang bị báo lỗi] {summary}"

            results.append({
                "title": name,
                "name": name,
                "type": type_val,
                "category": type_val,
                "summary": display_summary,
                "source": "provisional_library",
                "quality_class": quality_class,
                "confidence": confidence,
                "evidence": filtered_evidence,
                "first_chapter": first_ch,
                "effective_status": eff_status,
                "oracle_policy": pol,
                "dispute_score": disp_score,
                "total_feedback": tot_fb,
                "patch_type": "effective_summary" if sum_ovr else ("effective_type" if typ_ovr else ("warn_record" if warn_rec else None))
            })

        # Filter out noise blacklisted terms
        noise_blacklist = {"ác độc", "ác ý", "âm ẩm", "đây đã"}
        filtered_results = [r for r in results if r.get("name", "").lower().strip() not in noise_blacklist]
        return filtered_results[:limit]
    except Exception as e:
        print(f"Error searching provisional library: {e}")
        return []


def merge_oracle_knowledge_results(
    wiki_results: list[dict],
    provisional_results: list[dict],
    limit: int = 5
) -> list[dict]:
    """
    Merges wiki_entries and provisional_library search results.
    Prioritises wiki_entries (canon) and deduplicates by normalized name.
    """
    merged = []
    seen_names = set()

    def norm(n: str) -> str:
        return re.sub(r"\s+", "", n.lower().strip())

    for r in wiki_results:
        name_val = r.get("title") or r.get("name") or ""
        if name_val:
            seen_names.add(norm(name_val))
        merged.append(r)

    for r in provisional_results:
        name_val = r.get("title") or r.get("name") or ""
        if norm(name_val) in seen_names:
            continue
        merged.append(r)

    return merged[:limit]


def is_event_plot_question(question: str) -> bool:
    """Detects event/campaign plot queries asking how they unfolded."""
    if not question:
        return False
    q = question.lower().strip()
    q = re.sub(r"[?\s]+$", "", q)

    # Check for keywords indicating plot development/event occurrences
    event_indicators = (
        "diễn ra như thế nào", "diễn ra ra sao", "diễn biến",
        "nội dung", "sự kiện", "xảy ra như thế nào", "xảy ra ra sao",
        "tóm tắt", "diễn ra thế nào"
    )
    if any(ind in q for ind in event_indicators):
        return True

    # Also check if the query starts with "chiến dịch" or contains "chiến dịch" and asks about occurrence/details
    if "chiến dịch" in q and any(w in q for w in ["như thế nào", "ra sao", "thế nào", "gì", "ở đâu"]):
        return True

    return False
