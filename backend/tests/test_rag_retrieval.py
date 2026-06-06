import pytest
from backend.rag.retrieval import (
    normalize_search_query,
    build_tsquery_terms,
    format_retrieval_result,
    search_story_chunks_text,
)

# Test 1: normalize_search_query removes leading/trailing spaces and collapses inner spaces
def test_normalize_search_query():
    assert normalize_search_query("   Hàn    Phong   ") == "Hàn Phong"
    assert normalize_search_query("") == ""
    assert normalize_search_query(None) == ""

# Test 2: build_tsquery_terms joins terms with & and handles empty queries
def test_build_tsquery_terms():
    assert build_tsquery_terms("Hàn Phong") == "Hàn & Phong"
    assert build_tsquery_terms("   ") == ""
    assert build_tsquery_terms("!!!") == ""

# Test 3 & 4: format_retrieval_result structures response correctly
def test_format_retrieval_result():
    row = {
        "chapter_number": 1,
        "chapter_title": "Ngày Tận Thế",
        "chunk_index": 0,
        "content": "Đây là nội dung cực kỳ dài... " * 10,
        "content_plain": "Đây là nội dung cực kỳ dài... " * 10,
        "content_hash": "hash123",
        "rank": 0.95
    }

    formatted = format_retrieval_result(row)
    assert formatted["source"] == "story_chunks_fts"
    assert formatted["chapter_number"] == 1
    assert formatted["chunk_index"] == 0
    assert formatted["content_preview"].endswith("...")
    assert len(formatted["content_preview"]) <= 203  # 200 + '...'
    assert formatted["content_plain"] == row["content_plain"]
    assert formatted["rank"] == 0.95
    assert formatted["content_hash"] == "hash123"

# Test 5: search function respects chapter_cap using mock Supabase client
def test_search_story_chunks_respects_chapter_cap():
    called_lte_val = None
    called_limit_val = None
    called_text_search_query = None

    class MockQueryBuilder:
        def select(self, fields):
            return self

        def text_search(self, col, query, options=None):
            nonlocal called_text_search_query
            called_text_search_query = query
            return self

        def lte(self, col, val):
            nonlocal called_lte_val
            called_lte_val = val
            return self

        def limit(self, val):
            nonlocal called_limit_val
            called_limit_val = val
            return self

        def execute(self):
            class MockResponse:
                data = [
                    {
                        "chapter_number": 3,
                        "chapter_title": "Chương 3",
                        "chunk_index": 0,
                        "content": "Matched content",
                        "content_plain": "Matched content",
                        "content_hash": "hash"
                    }
                ]
            return MockResponse()

    class MockSupabase:
        def table(self, name):
            return MockQueryBuilder()

    mock_sb = MockSupabase()

    # 1. Search with chapter_cap
    results = search_story_chunks_text(
        supabase=mock_sb,
        query="Diệp Phàm",
        chapter_cap=5,
        limit=3
    )

    assert len(results) == 1
    assert results[0]["chapter_number"] == 3
    assert called_text_search_query == "Diệp & Phàm"
    assert called_lte_val == 5
    assert called_limit_val == 3

    # 2. Search without chapter_cap
    called_lte_val = None
    search_story_chunks_text(
        supabase=mock_sb,
        query="Diệp Phàm",
        chapter_cap=None
    )
    assert called_lte_val is None  # Should not apply lte filter

# Test 6: empty query returns empty list without crashing
def test_empty_query_handling():
    results1 = search_story_chunks_text(None, "")
    assert results1 == []

    results2 = search_story_chunks_text(None, "   ")
    assert results2 == []

# Test 7: extract_search_keywords filters out whitespace and short words
def test_extract_search_keywords():
    from backend.rag.retrieval import extract_search_keywords
    assert extract_search_keywords("   Hàn    Phong   a  ") == ["hàn", "phong"]
    assert extract_search_keywords("") == []

# Test 8: score_lexical_result matches scoring rules and assigns reasons
def test_score_lexical_result_priorities():
    from backend.rag.retrieval import score_lexical_result, extract_search_keywords

    query = "Hàn Phong"
    keywords = extract_search_keywords(query)

    # 1. Matching full title phrase
    row_title_match = {
        "chapter_title": "Cuộc chiến của Hàn Phong",
        "content_plain": "Không có gì"
    }
    score1, reasons1 = score_lexical_result(row_title_match, query, keywords)
    assert "title_phrase" in reasons1
    assert "title_keyword" in [r.split(":")[0] for r in reasons1]

    # 2. Matching content keyword
    row_content_match = {
        "chapter_title": "Chương khác",
        "content_plain": "Hàn Phong đi dạo"
    }
    score2, reasons2 = score_lexical_result(row_content_match, query, keywords)
    assert "content_phrase" in reasons2

    # 3. Verify title phrase score is higher than content keyword score
    assert score1 > score2

    # 4. Verify title phrase has higher priority
    row_only_keyword = {
        "chapter_title": "Chương khác",
        "content_plain": "Hàn và Phong gặp nhau" # only matches keywords, not full phrase
    }
    score3, reasons3 = score_lexical_result(row_only_keyword, query, keywords)
    assert "content_phrase" not in reasons3
    assert score1 > score3

# Test 9: merge_retrieval_results deduplicates rows by content_hash
def test_merge_retrieval_results_deduplicates():
    from backend.rag.retrieval import merge_retrieval_results

    list1 = [
        {"content_hash": "hash1", "chapter_number": 1, "chapter_title": "C1", "content_plain": "A", "chunk_index": 0},
        {"content_hash": "hash2", "chapter_number": 2, "chapter_title": "C2", "content_plain": "A B", "chunk_index": 0}
    ]
    list2 = [
        {"content_hash": "hash1", "chapter_number": 1, "chapter_title": "C1", "content_plain": "A", "chunk_index": 0, "temp_fts_match": True},
        {"content_hash": "hash3", "chapter_number": 3, "chapter_title": "C3", "content_plain": "A C", "chunk_index": 0}
    ]

    merged = merge_retrieval_results([list1, list2], "A", limit=5)
    assert len(merged) == 3
    # Check deduplicated row maps source and has reasons
    row_hash1 = next(item for item in merged if item["content_hash"] == "hash1")
    assert row_hash1["source"] == "story_chunks_hybrid_lexical"
    assert "fts" in row_hash1["match_reasons"]

# Test 10: hybrid search respects chapter_cap
def test_hybrid_search_respects_chapter_cap():
    from backend.rag.retrieval import search_story_chunks_hybrid_lexical

    called_lte_values = []

    class MockQueryBuilder:
        def select(self, fields):
            return self

        def text_search(self, col, query, options=None):
            return self

        def ilike(self, col, pattern):
            return self

        def or_(self, pattern):
            return self

        def lte(self, col, val):
            called_lte_values.append(val)
            return self

        def limit(self, val):
            return self

        def execute(self):
            class MockResponse:
                data = [
                    {"content_hash": "h1", "chapter_number": 2, "chapter_title": "Title", "content_plain": "Hàn Phong ở đây", "chunk_index": 0}
                ]
            return MockResponse()

    class MockSupabase:
        def table(self, name):
            return MockQueryBuilder()

    mock_sb = MockSupabase()

    results = search_story_chunks_hybrid_lexical(
        supabase=mock_sb,
        query="Hàn Phong",
        chapter_cap=4,
        limit=5
    )

    assert len(results) == 1
    # Check that lte was called with 4
    assert 4 in called_lte_values
    assert results[0]["source"] == "story_chunks_hybrid_lexical"

# Test 11: hybrid search handles empty queries gracefully
def test_hybrid_empty_query_handling():
    from backend.rag.retrieval import search_story_chunks_hybrid_lexical
    assert search_story_chunks_hybrid_lexical(None, "") == []
    assert search_story_chunks_hybrid_lexical(None, "   ") == []
