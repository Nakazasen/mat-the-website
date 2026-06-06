import json
from unittest.mock import MagicMock, patch

from backend.rag.entity_drafts import (
    normalize_entity_name,
    guess_entity_type,
    build_entity_draft,
    build_missing_entity_drafts
)

def test_normalize_entity_name():
    assert normalize_entity_name("  Hàn   Phong  ") == "Hàn Phong"
    assert normalize_entity_name("\nLâm Nhã\tVy\n") == "Lâm Nhã Vy"
    assert normalize_entity_name("") == ""
    assert normalize_entity_name(None) == ""

def test_guess_entity_type_heuristics():
    # Test character
    res_char = [{"content_plain": "Nhân vật này rất trung thành với Hàn Phong."}]
    assert guess_entity_type("Vương Mạnh", res_char) == "character"
    
    # Test organization
    res_org = [{"content_plain": "Tập đoàn hay quân đội Đại Thiên Thần."}]
    assert guess_entity_type("Quân đội", res_org) == "organization"
    
    # Test item
    res_item = [{"content_plain": "Sử dụng tinh thể zombie hoặc dịch thể cường hóa để tăng lực."}]
    assert guess_entity_type("Dịch thể cường hóa", res_item) == "item"
    
    # Test ability
    res_ab = [{"content_plain": "Thức tỉnh dị năng hệ băng hoặc kỹ năng Băng Thứ."}]
    assert guess_entity_type("Băng Thứ", res_ab) == "ability"
    
    # Test location
    res_loc = [{"content_plain": "Đi tới tầng hầm hay nhà kho sảnh căng tin."}]
    assert guess_entity_type("Nhà kho", res_loc) == "location"
    
    # Test creature
    res_cr = [{"content_plain": "Con zombie đột biến khổng lồ gầm rú."}]
    assert guess_entity_type("Zombie", res_cr) == "creature"
    
    # Test default unknown
    assert guess_entity_type("Một thứ lạ", []) == "unknown"

def test_build_entity_draft_no_spoofing():
    mock_evidence = [
        {
            "chapter_number": 1,
            "chapter_title": "Chương 1",
            "chunk_index": 2,
            "content_plain": "Đoạn văn trích dẫn từ truyện.",
            "content_hash": "hash123"
        }
    ]
    
    draft = build_entity_draft("Lâm Nhã Vy", mock_evidence)
    
    # 1. name và status
    assert draft["entity_name"] == "Lâm Nhã Vy"
    assert draft["status"] == "needs_review"
    
    # 2. Không bịa summary (phải là needs_review)
    assert draft["summary"] == "needs_review"
    
    # 3. Suggested wiki entry
    assert draft["suggested_wiki_entry"]["title"] == "Lâm Nhã Vy"
    assert draft["suggested_wiki_entry"]["category"] == "character"
    assert draft["suggested_wiki_entry"]["content"] == "needs_review"
    
    # 4. Evidence fields mapped correctly
    assert len(draft["evidence"]) == 1
    ev = draft["evidence"][0]
    assert ev["chapter_number"] == 1
    assert ev["chapter_title"] == "Chương 1"
    assert ev["chunk_index"] == 2
    assert ev["preview"] == "Đoạn văn trích dẫn từ truyện."
    assert ev["content_hash"] == "hash123"

def test_entity_type_default_unknown_without_evidence():
    draft = build_entity_draft("Thứ gì đó lạ hoắc", [])
    assert draft["entity_type"] == "unknown"
    assert draft["suggested_wiki_entry"]["category"] == "needs_review"

def test_build_drafts_no_db_write():
    mock_supabase = MagicMock()
    
    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=[]) as mock_search:
        drafts = build_missing_entity_drafts(["Lâm Nhã Vy"], chapter_cap=10, supabase=mock_supabase)
        
        # Verify search was called
        mock_search.assert_called_once()
        
        # Verify no database mutation methods were called on supabase client
        assert mock_supabase.table.called is False or mock_supabase.table().insert.called is False
        assert mock_supabase.table.called is False or mock_supabase.table().upsert.called is False
        assert mock_supabase.table.called is False or mock_supabase.table().delete.called is False

def test_draft_json_serializable():
    mock_evidence = [
        {
            "chapter_number": 2,
            "chapter_title": "Chương 2",
            "chunk_index": 0,
            "content_plain": "Bằng chứng.",
            "content_hash": "hash456"
        }
    ]
    draft = build_entity_draft("Trương Hạo", mock_evidence)
    
    # Serializes without raising TypeError
    json_str = json.dumps(draft)
    parsed = json.loads(json_str)
    assert parsed["entity_name"] == "Trương Hạo"
    assert parsed["evidence"][0]["chapter_number"] == 2
