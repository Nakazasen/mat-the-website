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
