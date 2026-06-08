import pytest
import os
import tempfile
from backend.rag.new_chapter_source_reader import (
    parse_chapter_file,
    validate_new_chapter_source,
    build_new_chapter_manifest,
    load_new_chapters_from_folder,
    validate_new_chapter_payload
)

def test_parse_chapter_file_valid():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "chapter_0830.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("Chương 830: Bình Minh Khởi Đầu\nNội dung chương truyện ở đây. Diệp Phàm thức tỉnh sức mạnh.")
            
        parsed = parse_chapter_file(filepath)
        assert parsed["chapter_number"] == 830
        assert parsed["title"] == "Chương 830: Bình Minh Khởi Đầu"
        assert parsed["content"] == "Nội dung chương truyện ở đây. Diệp Phàm thức tỉnh sức mạnh."
        assert parsed["char_count"] == len("Nội dung chương truyện ở đây. Diệp Phàm thức tỉnh sức mạnh.")

def test_parse_chapter_file_invalid_name():
    with pytest.raises(ValueError):
        parse_chapter_file("invalid_filename.txt")

def test_validate_new_chapter_source_rules():
    # Valid candidate
    ch_valid = {
        "chapter_number": 830,
        "title": "Chương 830: Tiêu đề hợp lệ",
        "content": "Nội dung truyện Diệp Phàm bước vào hành trình mới đầy thử thách.",
        "char_count": 60
    }
    val = validate_new_chapter_source(ch_valid, current_last_chapter=829)
    assert val["is_valid"] is True
    assert len(val["errors"]) == 0

    # Rule 1: Empty content
    ch_empty_content = ch_valid.copy()
    ch_empty_content["content"] = ""
    val = validate_new_chapter_source(ch_empty_content, current_last_chapter=829)
    assert val["is_valid"] is False
    assert "empty" in val["errors"][0].lower()

    # Rule 2: Title number mismatch
    ch_mismatch = ch_valid.copy()
    ch_mismatch["title"] = "Chương 835: Tiêu đề lệch số"
    val = validate_new_chapter_source(ch_mismatch, current_last_chapter=829)
    assert val["is_valid"] is False
    assert "mismatch" in val["errors"][0].lower()

    # Rule 3: Historical chapter
    val_historical = validate_new_chapter_source(ch_valid, current_last_chapter=835)
    assert val_historical["is_valid"] is False
    assert "is <=" in val_historical["errors"][0]

def test_build_manifest_sequence_gaps():
    chapters = [
        {"chapter_number": 830, "title": "Chương 830: Tiêu đề", "content": "Nội dung truyện Diệp Phàm bước vào hành trình mới đầy thử thách.", "char_count": 60, "source_path": "ch830"},
        {"chapter_number": 832, "title": "Chương 832: Tiêu đề", "content": "Nội dung truyện Diệp Phàm bước vào hành trình mới đầy thử thách.", "char_count": 60, "source_path": "ch832"}
    ]
    
    # Gap 831 is missing. Strict mode should report error
    manifest = build_new_chapter_manifest(chapters, current_last_chapter=829, strict=True)
    assert manifest["ok"] is False
    assert manifest["status"] == "VALIDATION_FAILED"
    assert 831 in manifest["gaps"]
    assert any("gaps" in err.lower() for err in manifest["errors"])

    # Non-strict mode should allow it
    manifest_non_strict = build_new_chapter_manifest(chapters, current_last_chapter=829, strict=False)
    assert manifest_non_strict["ok"] is True
    assert manifest_non_strict["status"] == "VALIDATION_PASSED"
    assert 831 in manifest_non_strict["gaps"]

def test_build_manifest_allow_sequence():
    chapters = [
        {"chapter_number": 830, "title": "Chương 830: Tiêu đề", "content": "Nội dung truyện Diệp Phàm bước vào hành trình mới đầy thử thách.", "char_count": 60, "source_path": "ch830"},
        {"chapter_number": 831, "title": "Chương 831: Tiêu đề", "content": "Nội dung truyện Diệp Phàm bước vào hành trình mới đầy thử thách.", "char_count": 60, "source_path": "ch831"}
    ]
    manifest = build_new_chapter_manifest(chapters, current_last_chapter=829, strict=True)
    assert manifest["ok"] is True
    assert manifest["status"] == "VALIDATION_PASSED"
    assert len(manifest["gaps"]) == 0

def test_empty_folder_returns_no_source():
    manifest = build_new_chapter_manifest([], current_last_chapter=829)
    assert manifest["status"] == "NO_SOURCE_FILES_FOUND"
    assert manifest["ok"] is True
    assert manifest["write_required"] is False

def test_no_llm_or_embedding():
    import backend.rag.new_chapter_source_reader as reader
    with open(reader.__file__, "r", encoding="utf-8") as f:
        content = f.read().lower()
        
    assert "openai" not in content
    assert "gemini" not in content
    assert "google" not in content
    assert "embed_query" not in content
    assert "embed_documents" not in content
    assert "openaiembeddings" not in content

def test_validate_new_chapter_payload():
    # Valid payload
    val = validate_new_chapter_payload(
        chapter_number=830,
        title="Chương 830: Khởi Đầu Mới",
        content="Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
        current_last_chapter=829
    )
    assert val["is_valid"] is True
    assert len(val["errors"]) == 0
    assert "diệp phàm" in val["content"].lower()

    # Invalid empty title
    val_empty_title = validate_new_chapter_payload(
        chapter_number=830,
        title="",
        content="Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
        current_last_chapter=829
    )
    assert val_empty_title["is_valid"] is False
    assert "title is empty" in val_empty_title["errors"][0].lower()

    # Invalid content too short
    val_short = validate_new_chapter_payload(
        chapter_number=830,
        title="Chương 830: Ngắn",
        content="Quá ngắn",
        current_last_chapter=829
    )
    assert val_short["is_valid"] is False
    assert "short" in val_short["errors"][0]

    # HTML content forbidden
    val_html = validate_new_chapter_payload(
        chapter_number=830,
        title="Chương 830: HTML",
        content="<script>alert('hack')</script> Nội dung chương truyện ở đây dài hơn năm mươi ký tự để tránh bị báo lỗi quá ngắn.",
        current_last_chapter=829
    )
    assert val_html["is_valid"] is False
    assert "html tags or script elements" in val_html["errors"][0].lower()

    # Sequence gap rejected in strict
    val_gap = validate_new_chapter_payload(
        chapter_number=832,
        title="Chương 832: Gaps",
        content="Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
        current_last_chapter=829,
        strict=True
    )
    assert val_gap["is_valid"] is False
    assert "sequence gap" in val_gap["errors"][0].lower()
