import pytest
from backend.scripts.oracle_self_learning_regression_pack import (
    score_ha_huyen_suong,
    score_chapter_summary,
    score_tinh_the_zombie,
    score_bang_doc,
    score_han_phong,
    score_doan_doi
)

def test_score_ha_huyen_suong():
    # Valid response
    valid_resp = "[DỮ LIỆU HỆ THỐNG] Hạ Huyền Sương là nhân vật trong Chương 816..."
    valid_resp += " " * 100  # Ensure length is long enough
    passed, reason = score_ha_huyen_suong(valid_resp)
    assert passed is True
    assert reason == ""

    # Missing name
    passed, reason = score_ha_huyen_suong("Nhân vật này xuất hiện ở Chương 816...")
    assert passed is False
    assert "Missing 'Hạ Huyền Sương' name" in reason

    # Missing chapter context
    passed, reason = score_ha_huyen_suong("Hạ Huyền Sương là một nhân vật nữ vô cùng xinh đẹp...")
    assert passed is False
    assert "Missing chapter 816 reference" in reason

    # Too short
    passed, reason = score_ha_huyen_suong("Hạ Huyền Sương Chương 816")
    assert passed is False
    assert "too short/shallow" in reason


def test_score_chapter_summary():
    # Valid response
    valid_resp = "Tóm tắt Chương 820: Hàn Phong ăn lẩu đun nước tắm..."
    passed, reason = score_chapter_summary(valid_resp)
    assert passed is True
    assert reason == ""

    # Contains fallback entity list
    invalid_resp = "Phân loại: nhân vật. Tóm tắt Chương 820."
    passed, reason = score_chapter_summary(invalid_resp)
    assert passed is False
    assert "Contains entity category list markup" in reason

    # Missing summary keywords
    passed, reason = score_chapter_summary("Hàn Phong ăn lẩu và đun nước cùng Hạ Huyền Sương.")
    assert passed is False
    assert "Missing summary keywords" in reason

    # Missing plot details
    passed, reason = score_chapter_summary("Tóm tắt nội dung chương truyện: Không có gì xảy ra cả.")
    assert passed is False
    assert "Missing chapter 820 plot details" in reason


def test_score_tinh_the_zombie():
    # Valid response
    valid_resp = "Tinh thể zombie là vật phẩm crystal_core từ Chương 9..."
    passed, reason = score_tinh_the_zombie(valid_resp)
    assert passed is True

    # Missing name
    passed, reason = score_tinh_the_zombie("Đây là crystal_core dùng để nâng cấp.")
    assert passed is False
    assert "Missing 'Tinh thể zombie'" in reason

    # Missing context/category
    passed, reason = score_tinh_the_zombie("Tinh thể zombie là vật phẩm.")
    assert passed is False
    assert "Missing core category or evidence details" in reason

    # Contains Phá Tâm Linh
    passed, reason = score_tinh_the_zombie("Tinh thể zombie thuộc loại crystal_core. Phá Tâm Linh là kỹ năng của Hàn Phong.")
    assert passed is False
    assert "Incorrectly references 'Phá Tâm Linh'" in reason


def test_score_bang_doc():
    assert score_bang_doc("Băng Độc là một loại độc tố.")[0] is True
    assert score_bang_doc("Chất độc hàn băng này rất nguy hiểm.")[0] is False


def test_score_han_phong():
    # Valid response
    valid_resp = "Hàn Phong là nhân vật chính trong truyện mạt thế..."
    passed, reason = score_han_phong(valid_resp)
    assert passed is True

    # Missing name
    passed, reason = score_han_phong("Main nhân vật chính của chúng ta.")
    assert passed is False
    assert "Missing 'Hàn Phong' name" in reason

    # Missing protagonist context
    passed, reason = score_han_phong("Hàn Phong là một nhân vật xuất hiện ở chương đầu.")
    assert passed is False
    assert "Missing main protagonist context" in reason


def test_score_doan_doi():
    # Treating it as faction
    passed, reason = score_doan_doi("đoàn đội là thế lực đóng vai trò quan trọng trong truyện.")
    assert passed is False
    assert "Treats generic term" in reason

    # Explaining it as general word
    passed, reason = score_doan_doi("đoàn đội là một từ chung dùng để chỉ các nhóm nhỏ, bị loại bỏ hoặc discard trong danh mục.")
    assert passed is True
