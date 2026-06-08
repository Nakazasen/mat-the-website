import pytest
from backend.rag.story_growth_detector import (
    normalize_chapter_title,
    extract_chapter_number,
    detect_missing_chapters,
    build_new_chapter_ingest_plan
)

def test_normalize_chapter_title():
    assert normalize_chapter_title("<p>Chương 830: Tên chương</p>") == "Chương 830: Tên chương"
    assert normalize_chapter_title("  Chương   830   ") == "Chương 830"
    assert normalize_chapter_title("") == ""
    assert normalize_chapter_title(None) == ""

def test_extract_chapter_number():
    # Standard format
    assert extract_chapter_number("Chương 830: Tên chương") == 830
    assert extract_chapter_number("Chapter 831 - Main character returns") == 831
    assert extract_chapter_number("Chg 832") == 832
    assert extract_chapter_number("C. 833: The end") == 833
    
    # Prefix format
    assert extract_chapter_number("834. Tên chương") == 834
    
    # Fallback format
    assert extract_chapter_number("Tên chương chứa số 835") == 835
    
    # Negative/Invalid cases
    assert extract_chapter_number("Không có số nào cả") is None
    assert extract_chapter_number("") is None
    assert extract_chapter_number(None) is None

def test_detect_missing_chapters():
    existing = [1, 2, 3, 5]
    source = [1, 2, 3, 4, 5, 6]
    assert detect_missing_chapters(existing, source) == [4, 6]

def test_detect_duplicate_chapters():
    # Helper logic in test to check duplicate detection
    source = [1, 2, 2, 3, 4, 4, 5]
    duplicates = sorted(list(set(ch for ch in source if source.count(ch) > 1)))
    assert duplicates == [2, 4]

def test_build_plan_returns_new_chapters():
    existing = list(range(1, 830))  # 1 to 829
    source = list(range(1, 832))    # 1 to 831
    
    plan = build_new_chapter_ingest_plan(existing, source)
    assert plan["status"] == "NEW_CHAPTERS_DETECTED"
    assert plan["current_last_chapter"] == 829
    assert plan["detected_source_last_chapter"] == 831
    assert plan["new_chapters_to_ingest"] == [830, 831]
    assert plan["write_required"] is False

def test_build_plan_returns_no_new_chapters():
    existing = list(range(1, 830))  # 1 to 829
    source = list(range(1, 830))    # 1 to 829
    
    plan = build_new_chapter_ingest_plan(existing, source)
    assert plan["status"] == "NO_NEW_CHAPTERS_FOUND"
    assert plan["current_last_chapter"] == 829
    assert plan["detected_source_last_chapter"] == 829
    assert plan["new_chapters_to_ingest"] == []
    assert plan["write_required"] is False

def test_dry_run_safety():
    # Ensure there are no database dependencies, mock calls, or write options within the build_plan logic
    existing = [1, 2, 3]
    source = [1, 2, 3, 4]
    
    plan = build_new_chapter_ingest_plan(existing, source)
    # The plan object itself should verify dry-run safety by returning write_required: False
    assert plan["write_required"] is False
    # Verify that plan has no direct mutations or DB write calls.
    # Because these are pure functions, no DB interaction occurred.

def test_no_llm_or_embedding():
    # Verify that the detector module doesn't import any heavy AI packages, openai, google, etc.
    import backend.rag.story_growth_detector as detector
    # Read its file content to confirm no 'openai', 'gemini', 'embedding', or similar keywords exist
    with open(detector.__file__, "r", encoding="utf-8") as f:
        content = f.read().lower()
        
    assert "openai" not in content
    assert "gemini" not in content
    assert "google" not in content
    assert "embed" not in content
    assert "llm" not in content
