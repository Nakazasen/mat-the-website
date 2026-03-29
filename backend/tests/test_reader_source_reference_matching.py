import pytest

from backend.routes import reader_learning


def test_find_best_matching_block_uses_fuzzy_when_token_match_fails():
    blocks = [
        "han phong dung truoc ban giam doc",
        "bach tuong vi xuat hien trong phong",
    ]
    selected_text = "hanphongdungtruocban"

    best_index, best_score = reader_learning._find_best_matching_block(
        blocks,
        selected_text,
        context_sentence=None,
    )

    assert best_index == 0
    assert best_score > 0


def test_cap_excerpt_limits_sentence_count():
    text = "Cau 1. Cau 2. Cau 3. Cau 4."
    excerpt = reader_learning._cap_excerpt(text, max_sentences=2, max_chars=999)
    assert excerpt == "Cau 1. Cau 2."


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


def test_build_source_reference_confidence_levels():
    assert (
        reader_learning._build_source_reference_confidence(
            "sentence",
            0.62,
            0.9,
            "Han Phong stood before the director's desk in silence.",
            "Han Phong dung truoc ban giam doc, im lang chiu tran.",
        )
        == "high"
    )
    assert (
        reader_learning._build_source_reference_confidence(
            "sentence",
            0.58,
            0.55,
            "Han Phong stood before the desk.",
            "Han Phong dung truoc ban.",
        )
        == "medium"
    )
    assert (
        reader_learning._build_source_reference_confidence(
            "sentence",
            0.2,
            0.2,
            "short",
            "-",
        )
        == "low"
    )
    assert (
        reader_learning._build_source_reference_confidence(
            "paragraph",
            0.8,
            0.0,
            "This is a longer translated paragraph used for alignment checks.",
            "Day la mot doan goc tieng Viet dai hon de kiem tra doi chieu.",
        )
        == "medium"
    )
    assert (
        reader_learning._build_source_reference_confidence(
            "paragraph",
            0.6,
            0.0,
            "Medium block score paragraph.",
            "Doan ngan.",
        )
        == "low"
    )


def test_extract_sentence_alignment_entries_filters_invalid_payload():
    entries = reader_learning._extract_sentence_alignment_entries(
        {
            "entries": [
                {"translated_excerpt": "Alpha sentence.", "source_excerpt": "Cau alpha."},
                {"translated_excerpt": "", "source_excerpt": "Missing translated"},
                {"translated_excerpt": "Missing source", "source_excerpt": ""},
                "invalid-item",
            ]
        }
    )

    assert len(entries) == 1
    assert entries[0]["translated_excerpt"] == "Alpha sentence."
    assert entries[0]["source_excerpt"] == "Cau alpha."


def test_resolve_source_reference_from_alignment_prefers_sentence_match():
    entries = [
        {"translated_excerpt": "Han Phong stood in silence.", "source_excerpt": "Han Phong dung im lang."},
        {"translated_excerpt": "The director kept shouting.", "source_excerpt": "Giam doc van quat thao."},
    ]
    result = reader_learning._resolve_source_reference_from_alignment(
        entries,
        selected_text="Han Phong stood in silence.",
        context_sentence="Han Phong stood in silence.",
    )

    assert result is not None
    assert result["match_mode"] == "sentence"
    assert result["translated_excerpt"] == "Han Phong stood in silence."
    assert result["source_excerpt"] == "Han Phong dung im lang."


def test_resolve_source_reference_from_alignment_uses_context_block_to_disambiguate():
    entries = [
        {"translated_excerpt": "The director kept shouting.", "source_excerpt": "Giam doc van quat thao."},
        {"translated_excerpt": "She should have looked at herself in the mirror instead.", "source_excerpt": "Co ta nen tu soi guong truoc da."},
        {"translated_excerpt": "Han Phong gritted his teeth.", "source_excerpt": "Han Phong nghien rang."},
        {"translated_excerpt": "The director kept shouting.", "source_excerpt": "Lao giam doc van chui rua khong ngot."},
        {"translated_excerpt": "She should have looked at herself in the mirror instead.", "source_excerpt": "Dang le ao nu kia phai tu nhin lai minh trong guong."},
        {"translated_excerpt": "Han Phong turned away in silence.", "source_excerpt": "Han Phong lang lang quay mat di."},
    ]

    result = reader_learning._resolve_source_reference_from_alignment(
        entries,
        selected_text="She should have looked at herself in the mirror instead.",
        context_sentence="She should have looked at herself in the mirror instead.",
        context_block=(
            "The director kept shouting. "
            "She should have looked at herself in the mirror instead. "
            "Han Phong turned away in silence."
        ),
    )

    assert result is not None
    assert result["match_mode"] == "sentence"
    assert result["source_excerpt"] == "Dang le ao nu kia phai tu nhin lai minh trong guong."
    assert result["paragraph_index"] == 4


def test_resolve_source_reference_from_alignment_rejects_partial_paragraph_match():
    entries = [
        {"translated_excerpt": "Han Phong could only feel jealous.", "source_excerpt": "Han chi con biet ghen tuc."},
        {
            "translated_excerpt": "Heh, Liu Xuan wasn't any better; with that arrogant look she gave him, she should have looked at herself in the mirror instead.",
            "source_excerpt": "Ao nu kia cung chang ra gi, dang le nen tu soi lai minh trong guong.",
        },
    ]

    result = reader_learning._resolve_source_reference_from_alignment(
        entries,
        selected_text="with that arrogant look she gave him, she should have looked at herself in the mirror instead.",
        context_sentence="Heh, Liu Xuan wasn't any better; with that arrogant look she gave him, she should have looked at herself in the mirror instead.",
        context_block=(
            "Han Phong could only feel jealous as he stepped out of the director's office and closed the door behind him. "
            "Heh, Liu Xuan wasn't any better; with that arrogant look she gave him, "
            "she should have looked at herself in the mirror instead. "
            "That woman really made one's bones go soft."
        ),
    )

    assert result is None


def test_should_match_sentence_rejects_multi_sentence_selection():
    assert (
        reader_learning._should_match_sentence(
            "その濁った瞳には、正気のかけらもなかった。 この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
            "その濁った瞳には、正気のかけらもなかった。 この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
        )
        is False
    )


def test_resolve_source_reference_from_alignment_maps_multi_sentence_selection_as_paragraph():
    entries = [
        {
            "translated_excerpt": "その濁った瞳には、正気のかけらもなかった。",
            "source_excerpt": "Đôi mắt đục ngầu ấy không còn chút tỉnh táo nào.",
        },
        {
            "translated_excerpt": "この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
            "source_excerpt": "Nhìn cảnh tượng này, trong đầu Hàn Phong tự nhiên hiện lên một từ có hai chữ.",
        },
        {
            "translated_excerpt": "それはゾンビだった。",
            "source_excerpt": "Đó là zombie.",
        },
    ]

    selected_text = (
        "その濁った瞳には、正気のかけらもなかった。 "
        "この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。"
    )
    result = reader_learning._resolve_source_reference_from_alignment(
        entries,
        selected_text=selected_text,
        context_sentence=selected_text,
        context_block=selected_text,
    )

    assert result is not None
    assert result["match_mode"] == "paragraph"
    assert result["translated_excerpt"] == selected_text
    assert result["source_excerpt"] == (
        "Đôi mắt đục ngầu ấy không còn chút tỉnh táo nào. "
        "Nhìn cảnh tượng này, trong đầu Hàn Phong tự nhiên hiện lên một từ có hai chữ."
    )


def test_resolve_source_reference_from_alignment_prefers_exact_sentence_over_context_window():
    entries = [
        {
            "translated_excerpt": "ハン・フォンはこの膿が流れる顔の持ち主を知っていた。",
            "source_excerpt": "Hàn Phong biết chủ nhân của khuôn mặt chảy mủ này.",
        },
        {
            "translated_excerpt": "そこには同僚のリュウ・チンがいた。",
            "source_excerpt": "Ở đó có đồng nghiệp Lưu Chinh.",
        },
        {
            "translated_excerpt": "この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
            "source_excerpt": "Nhìn cảnh tượng này, trong đầu Hàn Phong tự nhiên hiện lên một từ gồm hai chữ.",
        },
    ]

    result = reader_learning._resolve_source_reference_from_alignment(
        entries,
        selected_text="この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
        context_sentence="この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
        context_block="ハン・フォンはこの膿が流れる顔の持ち主を知っていた。 そこには同僚のリュウ・チンがいた。",
    )

    assert result is not None
    assert result["match_mode"] == "sentence"
    assert result["translated_excerpt"] == "この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。"
    assert result["source_excerpt"] == "Nhìn cảnh tượng này, trong đầu Hàn Phong tự nhiên hiện lên một từ gồm hai chữ."


def test_resolve_source_reference_from_alignment_rejects_wrong_sentence_when_selected_not_covered():
    entries = [
        {
            "translated_excerpt": "ハン・フォンはこの膿が流れる顔の持ち主を知っていた。",
            "source_excerpt": "Hàn Phong biết chủ nhân của khuôn mặt chảy mủ này.",
        },
        {
            "translated_excerpt": "そこには同僚のリュウ・チンがいた。",
            "source_excerpt": "Ở đó có đồng nghiệp Lưu Chinh.",
        },
    ]

    result = reader_learning._resolve_source_reference_from_alignment(
        entries,
        selected_text="この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
        context_sentence="この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
        context_block="ハン・フォンはこの膿が流れる顔の持ち主を知っていた。 そこには同僚のリュウ・チンがいた。",
    )

    assert result is None


def test_alignment_needs_regeneration_when_version_or_hash_is_stale():
    current_version = reader_learning._get_translation_alignment_version()
    fresh_alignment = {
        "version": current_version,
        "source_content_hash": reader_learning._alignment_content_hash("Câu 1."),
        "translated_content_hash": reader_learning._alignment_content_hash("文1。"),
    }

    assert reader_learning._alignment_needs_regeneration(
        fresh_alignment,
        source_text="Câu 1.",
        translated_text="文1。",
    ) is False
    assert reader_learning._alignment_needs_regeneration(
        {
            **fresh_alignment,
            "version": current_version - 1,
        },
        source_text="Câu 1.",
        translated_text="文1。",
    ) is True
    assert reader_learning._alignment_needs_regeneration(
        {
            **fresh_alignment,
            "translated_content_hash": "outdated",
        },
        source_text="Câu 1.",
        translated_text="文1。",
    ) is True


@pytest.mark.asyncio
async def test_source_reference_regenerates_stale_alignment_for_japanese_selection(monkeypatch):
    class FakeExecuteResult:
        def __init__(self, data):
            self.data = data

    class FakeQuery:
        def __init__(self, table_name, store):
            self.table_name = table_name
            self.store = store
            self.filters = {}
            self.update_payload = None

        def select(self, _fields):
            return self

        def eq(self, key, value):
            self.filters[key] = value
            return self

        def limit(self, _value):
            return self

        def update(self, payload):
            self.update_payload = payload
            return self

        def execute(self):
            if self.table_name == "chapters":
                return FakeExecuteResult([{"id": 77, "chapter_number": 77, "content_url": "https://example.com/ch77.txt"}])
            if self.table_name == "chapter_translations" and self.update_payload is not None:
                self.store.append({"filters": dict(self.filters), "payload": dict(self.update_payload)})
                return FakeExecuteResult([{"id": 701}])
            return FakeExecuteResult([])

    class FakeSupabase:
        def __init__(self):
            self.updates = []

        def table(self, table_name):
            return FakeQuery(table_name, self.updates)

    source_text = "Câu mở đầu. Nhìn cảnh tượng này, trong đầu Hàn Phong tự nhiên hiện lên một từ có hai chữ. Câu kết."
    translated_text = "導入文。 この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。 結び。"
    stale_alignment = {
        "version": 1,
        "entries": [
            {
                "translated_excerpt": "ハン・フォンはこの膿が流れる顔の持ち主を知っていた。",
                "source_excerpt": "Hàn Phong biết chủ nhân của khuôn mặt chảy mủ này.",
            }
        ],
    }
    generated_alignment = {
        "version": reader_learning._get_translation_alignment_version(),
        "source_content_hash": reader_learning._alignment_content_hash(source_text),
        "translated_content_hash": reader_learning._alignment_content_hash(translated_text),
        "entries": [
            {"translated_excerpt": "導入文。", "source_excerpt": "Câu mở đầu."},
            {
                "translated_excerpt": "この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
                "source_excerpt": "Nhìn cảnh tượng này, trong đầu Hàn Phong tự nhiên hiện lên một từ có hai chữ.",
            },
            {"translated_excerpt": "結び。", "source_excerpt": "Câu kết."},
        ],
    }

    fake_supabase = FakeSupabase()
    monkeypatch.setattr(reader_learning, "_get_supabase", lambda: fake_supabase)
    monkeypatch.setattr(reader_learning, "_get_fetch_r2_content", lambda: (lambda _url: source_text))
    monkeypatch.setattr(
        reader_learning,
        "_get_resolve_chapter_translation",
        lambda: (
            lambda _chapter_id, _locale: {
                "id": 701,
                "chapter_id": 77,
                "locale": "ja",
                "content": translated_text,
                "sentence_alignment": stale_alignment,
            }
        ),
    )
    monkeypatch.setattr(
        reader_learning,
        "_get_build_chapter_sentence_alignment",
        lambda: (lambda **_kwargs: generated_alignment),
    )

    payload = reader_learning.ReaderSourceReferenceRequest(
        locale="ja",
        chapter_id=77,
        selected_text="この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
        context_sentence="この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。",
        context_block=translated_text,
    )

    result = await reader_learning.source_reference(payload)

    assert result.translated_excerpt == "この光景を見て、ハン・フォンの頭の中に、二文字の単語が自然と浮かび上がった。"
    assert result.source_excerpt == "Nhìn cảnh tượng này, trong đầu Hàn Phong tự nhiên hiện lên một từ có hai chữ."
    assert fake_supabase.updates
    assert fake_supabase.updates[-1]["payload"]["sentence_alignment"] == generated_alignment


def test_source_reference_structure_is_reliable_rejects_large_sentence_drift():
    source_text = "Cau mot. Cau hai. Cau ba. Cau bon."
    translated_text = (
        "Sentence one. Sentence two. Sentence three. Sentence four. "
        "Sentence five. Sentence six. Sentence seven. Sentence eight."
    )

    assert reader_learning._source_reference_structure_is_reliable(source_text, translated_text) is False


def test_source_reference_structure_is_reliable_accepts_small_sentence_drift():
    source_text = "Cau mot. Cau hai. Cau ba. Cau bon."
    translated_text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."

    assert reader_learning._source_reference_structure_is_reliable(source_text, translated_text) is True
