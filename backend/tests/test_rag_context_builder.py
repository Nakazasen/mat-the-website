import pytest
from backend.rag.context_builder import (
    build_citation,
    trim_context_text,
    build_rag_context_block,
)

# Test 1: build_citation formats result with chapter_number, chapter_title, chunk_index
def test_build_citation():
    row = {
        "chapter_number": 1,
        "chapter_title": "Đầu lâu khổng lồ ngoài cửa sổ",
        "chunk_index": 2
    }
    citation = build_citation(row)
    assert citation == "Chương 1 - Đầu lâu khổng lồ ngoài cửa sổ | chunk 2"

    # Edge cases
    assert build_citation({"chapter_number": 3}) == "Chương 3"
    assert build_citation({"chapter_title": "Tận thế"}) == "Tận thế"
    assert build_citation({"chunk_index": 0}) == "chunk 0"

# Test 2 & 3: trim_context_text cuts at max_chars, appends '...', and preserves non-empty strings
def test_trim_context_text():
    text = "Hàn Phong là một nhân vật chính của bộ truyện này."
    # Truncate
    trimmed = trim_context_text(text, max_chars=15)
    assert trimmed.endswith("...")
    assert len(trimmed) <= 15

    # Do not truncate if text is short enough
    assert trim_context_text(text, max_chars=100) == text

    # Do not empty valid text
    assert trim_context_text("abc", max_chars=2) == "ab"
    assert trim_context_text("", max_chars=10) == ""
    assert trim_context_text("   ", max_chars=10) == ""

# Test 4 & 5: build_rag_context_block limits max_chunks and max_total_chars
def test_build_rag_context_block_limits():
    results = [
        {"chapter_number": 1, "chapter_title": "C1", "chunk_index": 0, "content_plain": "Content A", "content_hash": "hashA"},
        {"chapter_number": 1, "chapter_title": "C1", "chunk_index": 1, "content_plain": "Content B", "content_hash": "hashB"},
        {"chapter_number": 2, "chapter_title": "C2", "chunk_index": 0, "content_plain": "Content C", "content_hash": "hashC"},
    ]

    # Limit to max_chunks = 2
    context_data = build_rag_context_block(results, max_chunks=2)
    assert context_data["chunks_used"] == 2
    assert "Content C" not in context_data["context_text"]

    # Limit max_total_chars to small value
    # Format of each block is: "[CHƯƠNG 1 - C1 | chunk 0]\nContent A" (length: 29 + 9 = 38)
    # Plus "\n\n" (2) and second block (38). Total = 78
    # If max_total_chars is 40, only the first block should be added
    context_data_small = build_rag_context_block(results, max_total_chars=40)
    assert context_data_small["chunks_used"] == 1
    assert "Content B" not in context_data_small["context_text"]

# Test 6: citations are structured properly
def test_build_rag_context_citations():
    results = [
        {"chapter_number": 1, "chapter_title": "C1", "chunk_index": 0, "content_plain": "Content A", "content_hash": "hashA"}
    ]
    context_data = build_rag_context_block(results)
    assert len(context_data["citations"]) == 1
    cite = context_data["citations"][0]
    assert cite["chapter_number"] == 1
    assert cite["chapter_title"] == "C1"
    assert cite["chunk_index"] == 0
    assert cite["content_hash"] == "hashA"
    assert cite["source"] == "story_chunks"

# Test 7: empty results list returns clean structure and doesn't crash
def test_build_rag_context_empty_results():
    context_data = build_rag_context_block([])
    assert context_data["context_text"] == ""
    assert context_data["citations"] == []
    assert context_data["chunks_used"] == 0
    assert context_data["total_chars"] == 0
    assert context_data["source"] == "story_chunks_hybrid_context"

# Test 8 & 9: context_text formats header and maps correct source
def test_build_rag_context_formatting():
    results = [
        {"chapter_number": 1, "chapter_title": "Đầu lâu", "chunk_index": 0, "content_plain": "Test content", "content_hash": "hash1"}
    ]
    context_data = build_rag_context_block(results)
    assert "[CHƯƠNG 1 - Đầu lâu | chunk 0]" in context_data["context_text"]
    assert "Test content" in context_data["context_text"]
    assert context_data["source"] == "story_chunks_hybrid_context"
