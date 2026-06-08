import re
import hashlib
from typing import List, Dict, Any, Optional

def normalize_cache_term(term: str) -> str:
    """
    Normalizes a term for cache invalidation.
    Collapses multiple whitespaces and trims outer whitespace.
    Keeps casing and accents since Postgres ILIKE is case-insensitive but accent-sensitive.
    """
    if not term:
        return ""
    return re.sub(r"\s+", " ", term.strip())

def build_cache_invalidation_terms(records_or_names: list) -> List[str]:
    """
    Extracts a list of unique, normalized terms for cache invalidation.
    Accepts a list of strings or a list of dictionaries/records containing a 'name' key.
    """
    if not records_or_names:
        return []
        
    terms = []
    for item in records_or_names:
        if isinstance(item, dict):
            term = item.get("name")
        else:
            term = item
            
        if isinstance(term, str):
            norm = normalize_cache_term(term)
            if norm:
                terms.append(norm)
                
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for t in terms:
        t_low = t.lower()
        if t_low not in seen:
            seen.add(t_low)
            deduped.append(t)
    return deduped

def find_oracle_cache_rows_for_terms(
    supabase,
    terms: List[str],
    chapter_cap: Optional[int] = None,
    limit: int = 1000,
    question_hashes: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Queries the oracle_cache table and returns rows where the response
    contains any of the target terms, or the question_hash matches.
    """
    if not supabase:
        return []
        
    if not terms and not question_hashes:
        return []
        
    or_filters = []
    
    if terms:
        for term in terms:
            # Escape commas in the term for Postgrest OR filter
            safe_term = term.replace(",", "\\,")
            or_filters.append(f"response.ilike.%{safe_term}%")
            
    if question_hashes:
        for qh in question_hashes:
            or_filters.append(f"question_hash.eq.{qh}")
            
    try:
        query = supabase.table("oracle_cache").select("*")
        
        if or_filters:
            query = query.or_(",".join(or_filters))
            
        if chapter_cap is not None:
            query = query.eq("chapter_cap", chapter_cap)
            
        resp = query.limit(limit).execute()
        return resp.data or []
    except Exception as e:
        print(f"Warning: find_oracle_cache_rows_for_terms failed: {e}")
        return []

def clear_oracle_cache_for_terms(
    supabase,
    terms: List[str],
    dry_run: bool = True,
    chapter_cap: Optional[int] = None,
    question_hashes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Finds and deletes matching oracle cache entries.
    Returns a report of matched and deleted rows.
    """
    report = {
        "dry_run": dry_run,
        "terms": terms,
        "matched_rows": 0,
        "deleted_rows": 0,
        "skipped_reason": None
    }
    
    if not supabase:
        report["skipped_reason"] = "Supabase client not initialized"
        return report
        
    if not terms and not question_hashes:
        report["skipped_reason"] = "No terms or question hashes provided"
        return report
        
    try:
        rows = find_oracle_cache_rows_for_terms(
            supabase,
            terms,
            chapter_cap=chapter_cap,
            question_hashes=question_hashes
        )
        report["matched_rows"] = len(rows)
        
        if not rows:
            return report
            
        if dry_run:
            return report
            
        deleted_count = 0
        for row in rows:
            qh = row.get("question_hash")
            cc = row.get("chapter_cap")
            if qh and cc is not None:
                supabase.table("oracle_cache").delete().eq("question_hash", qh).eq("chapter_cap", cc).execute()
                deleted_count += 1
                
        report["deleted_rows"] = deleted_count
    except Exception as e:
        report["skipped_reason"] = f"Error during cache invalidation: {str(e)}"
        
    return report
