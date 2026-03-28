from backend.routes import reader_learning


def test_find_best_matching_block_uses_fuzzy_when_token_match_fails():
    blocks = [
        "han phong dung truoc ban giam doc",
        "bach tuong vi xuat hien trong phong",
    ]
    # Simulates merged no-space selection from CJK text where strict token containment fails.
    selected_text = "hanphongdungtruocban"

    best_index, best_score = reader_learning._find_best_matching_block(
        blocks,
        selected_text,
        context_sentence=None,
    )

    assert best_index == 0
    assert best_score > 0


def test_cap_excerpt_limits_sentence_count():
    text = "Câu 1. Câu 2. Câu 3. Câu 4."
    excerpt = reader_learning._cap_excerpt(text, max_sentences=2, max_chars=999)
    assert excerpt == "Câu 1. Câu 2."


def test_cap_excerpt_limits_characters_when_single_long_sentence():
    text = "a" * 1200
    excerpt = reader_learning._cap_excerpt(text, max_sentences=3, max_chars=200)
    assert len(excerpt) == 200


def test_map_source_block_index_by_relative_position_handles_count_mismatch():
    translated_blocks = [
        "t0",
        "t1",
        "t2",
        "t3",
    ]
    source_blocks = [
        "s0",
        "s1",
    ]
    mapped_first = reader_learning._map_source_block_index_by_relative_position(
        translated_blocks,
        source_blocks,
        0,
    )
    mapped_last = reader_learning._map_source_block_index_by_relative_position(
        translated_blocks,
        source_blocks,
        3,
    )

    assert mapped_first == 0
    assert mapped_last == 1
