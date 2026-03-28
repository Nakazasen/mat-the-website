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
