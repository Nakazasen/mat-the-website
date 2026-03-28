from backend.routes import wiki_search


def test_query_character_translation_match_vi_returns_tuple():
    row, translation = wiki_search.query_character_translation_match(
        supabase=None,
        search_value="Han Phong",
        chapter=10,
        locale="vi",
    )
    assert row is None
    assert translation is None


def test_alias_match_score_handles_diacritics():
    score = wiki_search._alias_match_score("Bach Tuong Vi", "Bạch Tường Vi")
    assert score >= 0.9


def test_alias_match_score_handles_compact_name():
    score = wiki_search._alias_match_score("HanPhong", "Han Phong")
    assert score >= 0.85


def test_build_search_candidates_deduplicates_normalized_forms():
    candidates = wiki_search._build_search_candidates("  Bạch   Tường  Vi ")
    assert "Bạch   Tường  Vi" in candidates
    assert "bach tuong vi" in candidates
    assert "bachtuongvi" in candidates


def test_select_best_manual_alias_row_prioritizes_locale_bonus():
    rows = [
        {"wiki_entry_id": "1", "alias": "Han Phong", "locale": "any"},
        {"wiki_entry_id": "2", "alias": "Han Phong", "locale": "en"},
    ]
    row, score = wiki_search._select_best_manual_alias_row(rows, "HanPhong", "en")
    assert row is not None
    assert row["wiki_entry_id"] == "2"
    assert score > 0
