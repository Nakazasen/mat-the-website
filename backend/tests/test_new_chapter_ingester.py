import pytest
import os
from unittest.mock import MagicMock
from backend.rag.new_chapter_ingester import (
    build_chunks_for_new_chapter,
    build_new_chapter_db_plan,
    insert_chapters_and_chunks,
    clear_oracle_cache_for_chapter
)

def test_build_chunks_for_new_chapter():
    chapter = {
        "chapter_number": 830,
        "title": "Chương 830: Bình Minh Khởi Đầu",
        "content": "Nội dung chương 830. Diệp Phàm thức tỉnh sức mạnh hệ lôi. Sấm sét giáng xuống mặt đất đập tan bầy tang thi.",
        "source_path": "ch830"
    }
    chunks = build_chunks_for_new_chapter(chapter, max_chars=50, overlap_chars=10)
    assert len(chunks) > 0
    for idx, c in enumerate(chunks):
        assert c["chapter_number"] == 830
        assert c["chapter_title"] == "Chương 830: Bình Minh Khởi Đầu"
        assert c["chunk_index"] == idx
        assert c["content"] != ""
        assert c["content_hash"] != ""
        assert c["token_count"] > 0
        assert c["char_count"] > 0

def test_build_plan_empty_folder():
    plan = build_new_chapter_db_plan([], current_last_chapter=829)
    assert plan["ok"] is True
    assert len(plan["planned_chapter_inserts"]) == 0
    assert plan["planned_chunk_inserts_count"] == 0

def test_build_plan_valid_single():
    chapters = [
        {
            "chapter_number": 830,
            "title": "Chương 830: Khởi Đầu Mới",
            "content": "Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
            "char_count": 98,
            "source_path": "ch830"
        }
    ]
    plan = build_new_chapter_db_plan(chapters, current_last_chapter=829)
    assert plan["ok"] is True
    assert len(plan["planned_chapter_inserts"]) == 1
    assert plan["planned_chapter_inserts"][0]["chapter_number"] == 830
    assert plan["planned_chapter_inserts"][0]["title"] == "Chương 830: Khởi Đầu Mới"
    assert plan["planned_chunk_inserts_count"] > 0

def test_build_plan_valid_sequence():
    chapters = [
        {
            "chapter_number": 830,
            "title": "Chương 830: Tiêu đề 830",
            "content": "Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
            "char_count": 98,
            "source_path": "ch830"
        },
        {
            "chapter_number": 831,
            "title": "Chương 831: Tiêu đề 831",
            "content": "Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
            "char_count": 98,
            "source_path": "ch831"
        }
    ]
    plan = build_new_chapter_db_plan(chapters, current_last_chapter=829)
    assert plan["ok"] is True
    assert len(plan["planned_chapter_inserts"]) == 2
    assert plan["new_chapters_detected"] == [830, 831]

def test_build_plan_sequence_gap():
    chapters = [
        {
            "chapter_number": 831,
            "title": "Chương 831: Tiêu đề 831",
            "content": "Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
            "char_count": 98,
            "source_path": "ch831"
        }
    ]
    plan = build_new_chapter_db_plan(chapters, current_last_chapter=829, strict=True)
    assert plan["ok"] is False
    assert "sequence gaps" in plan["errors"][0].lower()

def test_build_plan_historical_duplicate():
    chapters = [
        {
            "chapter_number": 820,
            "title": "Chương 820: Trùng lịch sử",
            "content": "Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
            "char_count": 98,
            "source_path": "ch820"
        }
    ]
    plan = build_new_chapter_db_plan(chapters, current_last_chapter=829)
    assert plan["ok"] is False
    assert "is <=" in plan["errors"][0]

def test_insert_dry_run_safety():
    mock_supabase = MagicMock()
    
    plan = {
        "ok": True,
        "planned_chunk_inserts_count": 5,
        "raw_planned_chapters": [
            {
                "chapter_number": 830,
                "title": "Chương 830: Khởi Đầu Mới",
                "content_url": "mock_url",
                "word_count": 10,
                "is_side_story": False,
                "content": "Nội dung chương 830."
            }
        ]
    }
    
    result = insert_chapters_and_chunks(mock_supabase, plan, dry_run=True)
    assert result["mode"] == "DRY_RUN"
    assert result["ok"] is True
    assert result["chapters_inserted"] == 1
    assert result["story_chunks_inserted"] == 5
    assert result["cache_rows_deleted"] == 0
    
    # Supabase must not have been called for insertion
    assert mock_supabase.table.call_count == 0

def test_no_llm_or_embedding():
    import backend.rag.new_chapter_ingester as ingester
    with open(ingester.__file__, "r", encoding="utf-8") as f:
        content = f.read().lower()
        
    assert "openai" not in content
    assert "gemini" not in content
    assert "google" not in content
    assert "embed_query" not in content
    assert "embed_documents" not in content
    assert "openaiembeddings" not in content
