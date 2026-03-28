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

