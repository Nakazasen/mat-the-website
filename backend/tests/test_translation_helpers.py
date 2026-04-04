import backend.main as main
import pytest
from fastapi import HTTPException


def test_build_target_translation_locales_filters_duplicates_and_vi():
    locales = main.build_target_translation_locales(["vi", "en", "EN", "zh-cn", "ja", "ja"])

    assert locales == ["en", "zh-CN", "ja"]


def test_chunk_translation_source_text_preserves_all_content():
    source = ("Doan 1.\n\n" + ("abc " * 1200) + "\n\nDoan 2.\n\n" + ("xyz " * 1200)).strip()

    chunks = main.chunk_translation_source_text(source, max_chars=1200)

    assert len(chunks) > 1
    assert "".join(chunks).replace("\n", "").replace(" ", "") == source.replace("\n", "").replace(" ", "")


def test_parse_multilocale_translation_payload_reads_nested_translations():
    payload = """
    {
      "translations": {
        "en": { "title": "Hello", "content": "World" },
        "zh-CN": { "title": "Ni Hao", "content": "Shi Jie" },
        "ja": { "title": "Konnichiwa", "content": "Sekai" }
      }
    }
    """

    parsed = main.parse_multilocale_translation_payload(payload, ["en", "zh-CN", "ja"], ["title", "content"])

    assert parsed["en"]["title"] == "Hello"
    assert parsed["zh-CN"]["content"] == "Shi Jie"
    assert parsed["ja"]["title"] == "Konnichiwa"


def test_build_guide_translation_slug_uses_locale_suffix():
    assert main.build_guide_translation_slug("reader-guide", "zh-cn") == "reader-guide__zh-CN"


def test_parse_json_like_payload_raises_useful_error_for_invalid_json():
    with pytest.raises(ValueError) as exc_info:
        main.parse_json_like_payload('{"title":"abc","content":"unterminated}')

    assert "Could not parse JSON payload" in str(exc_info.value)
    assert "Snippet:" in str(exc_info.value)


def test_build_chapter_sentence_alignment_preserves_sentence_order():
    source_chunks = ["S1. S2.", "S3. S4."]
    translated_chunks = ["T1. T2.", "T3. T4."]

    payload = main.build_chapter_sentence_alignment(
        source_text="\n\n".join(source_chunks),
        translated_text="\n\n".join(translated_chunks),
        source_chunks=source_chunks,
        translated_chunks=translated_chunks,
    )

    assert payload["version"] == main.TRANSLATION_ALIGNMENT_VERSION
    assert payload["chunk_count"] == 2
    assert payload["source_sentence_count"] == 4
    assert payload["translated_sentence_count"] == 4
    assert len(payload["entries"]) == 4
    assert payload["entries"][0]["translated_excerpt"] == "T1."
    assert payload["entries"][0]["source_excerpt"] == "S1."
    assert payload["entries"][3]["translated_excerpt"] == "T4."
    assert payload["entries"][3]["source_excerpt"] == "S4."


def test_build_chapter_sentence_alignment_splits_contiguous_japanese_sentences():
    payload = main.build_chapter_sentence_alignment(
        source_text="Cau 1. Cau 2.",
        translated_text="文1。文2。",
    )

    assert payload["translated_sentence_count"] == 2
    assert len(payload["entries"]) == 2
    assert payload["entries"][0]["translated_excerpt"] == "文1。"
    assert payload["entries"][1]["translated_excerpt"] == "文2。"


def test_build_chapter_sentence_alignment_includes_content_hashes():
    payload = main.build_chapter_sentence_alignment(
        source_text="Cau 1. Cau 2.",
        translated_text="Sentence 1. Sentence 2.",
    )

    assert payload["source_content_hash"] == main.build_content_hash("Cau 1. Cau 2.")
    assert payload["translated_content_hash"] == main.build_content_hash("Sentence 1. Sentence 2.")


def test_build_translation_publish_gate_report_flags_unreliable_structure():
    source_text = "Source sentence one is long enough. Source sentence two is long enough."
    translated_text = (
        "Translated sentence one is long enough. "
        "Translated sentence two is long enough. "
        "Translated sentence three is long enough. "
        "Translated sentence four is long enough."
    )
    alignment = main.build_chapter_sentence_alignment(source_text=source_text, translated_text=translated_text)

    report = main._build_translation_publish_gate_report(
        source_text=source_text,
        translated_text=translated_text,
        target_locale="en",
        sentence_alignment=alignment,
    )

    assert report["passed"] is False
    assert "sentence_ratio_out_of_range" in report["reasons"]
    assert report["sentence_ratio"] == 2.0


def test_translation_locale_mismatch_score_ignores_titlecase_proper_nouns():
    text = 'Han Phong crossed the Long River and met "Tram Thanh" near Duong Hoanh.'

    assert main._translation_locale_mismatch_score(text, "en") == 0


def test_translation_locale_mismatch_score_flags_lowercase_vietnamese_text():
    text = "Han Phong said anh không được đỡ đầu và cần trở về ngay."

    assert main._translation_locale_mismatch_score(text, "en") > 0


def test_is_translation_retryable_treats_transient_unavailable_as_retryable():
    exc = HTTPException(status_code=503, detail="This model is currently experiencing high demand. Please try again later.")

    assert main.is_translation_retryable(exc) is True


def test_rebalance_translation_blocks_to_source_restores_block_count():
    source_text = "Doan 1.\n\nDoan 2.\n\nDoan 3."
    translated_text = "Sentence 1. Sentence 2. Sentence 3."

    rebalanced = main._rebalance_translation_blocks_to_source(source_text, translated_text)

    assert len(main._split_text_blocks_for_translation_quality(rebalanced)) == 3


def test_prepare_translation_candidate_for_publish_normalizes_block_delta():
    source_text = "Doan 1.\n\nDoan 2.\n\nDoan 3."
    translated_text = "Sentence 1. Sentence 2. Sentence 3."

    prepared = main._prepare_translation_candidate_for_publish(
        source_text=source_text,
        translated_text=translated_text,
        target_locale="en",
    )

    assert prepared["gate_report"]["block_delta"] == 0


@pytest.mark.asyncio
async def test_repair_chapter_translation_candidate_until_publishable_repairs_failed_gate(monkeypatch):
    async def fake_refine_chapter_translation_with_ai(**kwargs):
        assert "quality gate" in (kwargs.get("repair_notes") or "").lower()
        return {
            "title": "Fixed title",
            "content": "Sentence 1.\n\nSentence 2.",
            "sentence_alignment": main.build_chapter_sentence_alignment(
                source_text="Doan 1.\n\nDoan 2.",
                translated_text="Sentence 1.\n\nSentence 2.",
            ),
        }

    monkeypatch.setattr(main, "refine_chapter_translation_with_ai", fake_refine_chapter_translation_with_ai)

    result = await main.repair_chapter_translation_candidate_until_publishable(
        source_title="Chuong 1",
        source_content="Doan 1.\n\nDoan 2.",
        chapter_number=1,
        target_locale="en",
        candidate_title="Draft",
        candidate_content="Sentence 1. Sentence 2. Sentence 3. Sentence 4.",
    )

    assert result["gate_report"]["passed"] is True
    assert result["title"] == "Fixed title"


@pytest.mark.asyncio
async def test_admin_translate_chapters_batch_ignores_empty_numeric_gap(monkeypatch):
    class FakeExecuteResult:
        def __init__(self, data):
            self.data = data

    class FakeQuery:
        def select(self, _fields):
            return self

        def gte(self, _key, _value):
            return self

        def lte(self, _key, _value):
            return self

        def order(self, _key):
            return self

        def execute(self):
            return FakeExecuteResult([])

    class FakeSupabase:
        def table(self, _table_name):
            return FakeQuery()

    async def fake_verify_admin(_authorization):
        return None

    monkeypatch.setattr(main, "supabase", FakeSupabase())
    monkeypatch.setattr(main, "verify_admin", fake_verify_admin)

    result = await main.admin_translate_chapters_batch(
        main.AdminBatchTranslateRequest(start_chapter=739, end_chapter=740, only_missing=True),
        authorization="Bearer test",
    )

    assert result["message"] == "No chapters found in selected range"
    assert result["translated_count"] == 0
    assert result["skipped_count"] == 0
    assert result["failed_count"] == 0
    assert result["failed_chapters"] == []


@pytest.mark.asyncio
async def test_admin_improve_quality_batch_ignores_empty_numeric_gap(monkeypatch):
    class FakeExecuteResult:
        def __init__(self, data):
            self.data = data

    class FakeQuery:
        def select(self, _fields):
            return self

        def gte(self, _key, _value):
            return self

        def lte(self, _key, _value):
            return self

        def order(self, _key):
            return self

        def execute(self):
            return FakeExecuteResult([])

    class FakeSupabase:
        def table(self, _table_name):
            return FakeQuery()

    async def fake_verify_admin(_authorization):
        return None

    monkeypatch.setattr(main, "supabase", FakeSupabase())
    monkeypatch.setattr(main, "verify_admin", fake_verify_admin)

    result = await main.admin_improve_chapters_quality_batch(
        main.AdminBatchImproveQualityRequest(start_chapter=739, end_chapter=740, only_unrefined=True, force=False),
        authorization="Bearer test",
    )

    assert result["message"] == "No chapters found in selected range"
    assert result["translated_count"] == 0
    assert result["skipped_count"] == 0
    assert result["failed_count"] == 0
    assert result["failed_chapters"] == []


@pytest.mark.asyncio
async def test_translate_chapter_payload_with_ai_uses_structured_flow(monkeypatch):
    async def fake_translate_chapter_payloads_with_ai(**kwargs):
        assert kwargs["target_locales"] == ["en"]
        return {"en": {"title": "Hello", "content": "World"}}

    monkeypatch.setattr(main, "translate_chapter_payloads_with_ai", fake_translate_chapter_payloads_with_ai)

    payload = await main.translate_chapter_payload_with_ai(
        title="Xin chao",
        content="Noi dung",
        source_locale="vi",
        target_locale="en",
        context_label="chapter-1",
    )

    assert payload == {"title": "Hello", "content": "World"}


@pytest.mark.asyncio
async def test_upsert_chapter_translations_failure_upsert_includes_required_text_fields(monkeypatch):
    class FakeExecuteResult:
        def __init__(self, data):
            self.data = data

    class FakeQuery:
        def __init__(self, table_name, store):
            self.table_name = table_name
            self.store = store

        def select(self, _fields):
            return self

        def eq(self, _key, _value):
            return self

        def in_(self, _key, _value):
            return self

        def limit(self, _value):
            return self

        def execute(self):
            if self.table_name == "chapter_translations":
                return FakeExecuteResult([])
            return FakeExecuteResult([{"id": 999, "chapter_number": 817, "title": "Thu linh te hai."}])

        def upsert(self, payload, on_conflict=None):
            self.store.append({"table": self.table_name, "payload": payload, "on_conflict": on_conflict})
            return self

    class FakeSupabase:
        def __init__(self):
            self.upserts = []

        def table(self, table_name):
            return FakeQuery(table_name, self.upserts)

    fake_supabase = FakeSupabase()
    monkeypatch.setattr(main, "supabase", fake_supabase)
    monkeypatch.setattr(main, "CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED", True)

    async def fake_translate_chapter_payloads_with_ai(**_kwargs):
        raise HTTPException(status_code=503, detail="AI translation is not configured")

    monkeypatch.setattr(main, "translate_chapter_payloads_with_ai", fake_translate_chapter_payloads_with_ai)

    with pytest.raises(HTTPException):
        await main.upsert_chapter_translations(
            chapter_row={"id": 999, "chapter_number": 817, "title": "Thu linh te hai."},
            title="Thu linh te hai.",
            content="Noi dung chuong",
            locales=["en"],
        )

    failed_payloads = [
        item["payload"]
        for item in fake_supabase.upserts
        if item["table"] == "chapter_translations" and item["payload"].get("translation_status") == "failed"
    ]
    assert failed_payloads
    assert failed_payloads[0]["title"] == ""
    assert failed_payloads[0]["content"] == ""


@pytest.mark.asyncio
async def test_upsert_chapter_translations_repairs_and_publishes(monkeypatch):
    class FakeExecuteResult:
        def __init__(self, data):
            self.data = data

    class FakeQuery:
        def __init__(self, table_name, store):
            self.table_name = table_name
            self.store = store

        def select(self, _fields):
            return self

        def eq(self, _key, _value):
            return self

        def in_(self, _key, _value):
            return self

        def limit(self, _value):
            return self

        def execute(self):
            if self.table_name == "chapter_translations":
                return FakeExecuteResult([])
            return FakeExecuteResult([{"id": 999, "chapter_number": 900, "title": "Chuong 900"}])

        def upsert(self, payload, on_conflict=None):
            self.store.append({"table": self.table_name, "payload": payload, "on_conflict": on_conflict})
            return self

    class FakeSupabase:
        def __init__(self):
            self.upserts = []

        def table(self, table_name):
            return FakeQuery(table_name, self.upserts)

    fake_supabase = FakeSupabase()
    monkeypatch.setattr(main, "supabase", fake_supabase)
    monkeypatch.setattr(main, "CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED", True)

    async def fake_translate_chapter_payloads_with_ai(**_kwargs):
        return {
            "en": {
                "title": "Bad draft",
                "content": "Sentence 1. Sentence 2. Sentence 3. Sentence 4.",
                "sentence_alignment": main.build_chapter_sentence_alignment(
                    source_text="Doan 1.\n\nDoan 2.",
                    translated_text="Sentence 1. Sentence 2. Sentence 3. Sentence 4.",
                ),
            }
        }

    async def fake_refine_chapter_translation_with_ai(**_kwargs):
        return {
            "title": "Fixed draft",
            "content": "Sentence 1.\n\nSentence 2.",
            "sentence_alignment": main.build_chapter_sentence_alignment(
                source_text="Doan 1.\n\nDoan 2.",
                translated_text="Sentence 1.\n\nSentence 2.",
            ),
        }

    monkeypatch.setattr(main, "translate_chapter_payloads_with_ai", fake_translate_chapter_payloads_with_ai)
    monkeypatch.setattr(main, "refine_chapter_translation_with_ai", fake_refine_chapter_translation_with_ai)

    result = await main.upsert_chapter_translations(
        chapter_row={"id": 999, "chapter_number": 900, "title": "Chuong 900"},
        title="Chuong 900",
        content="Doan 1.\n\nDoan 2.",
        locales=["en"],
    )

    assert result["translated_locales"] == ["en"]
    assert result["failed_translations"] == []

    published_payloads = [
        item["payload"]
        for item in fake_supabase.upserts
        if item["table"] == "chapter_translations" and item["payload"].get("translation_status") == "published"
    ]
    assert published_payloads
    assert published_payloads[-1]["title"] == "Fixed draft"
    assert published_payloads[-1]["content"] == "Sentence 1.\n\nSentence 2."


@pytest.mark.asyncio
async def test_import_manual_chapter_translation_publishes_when_gate_passes(monkeypatch):
    class FakeExecuteResult:
        def __init__(self, data):
            self.data = data

    class FakeQuery:
        def __init__(self, table_name, store):
            self.table_name = table_name
            self.store = store

        def select(self, _fields):
            return self

        def eq(self, _key, _value):
            return self

        def limit(self, _value):
            return self

        def execute(self):
            if self.table_name == "chapter_translations":
                return FakeExecuteResult([])
            return FakeExecuteResult([])

        def upsert(self, payload, on_conflict=None):
            self.store.append({"table": self.table_name, "payload": payload, "on_conflict": on_conflict})
            return self

    class FakeSupabase:
        def __init__(self):
            self.upserts = []

        def table(self, table_name):
            return FakeQuery(table_name, self.upserts)

    fake_supabase = FakeSupabase()
    monkeypatch.setattr(main, "supabase", fake_supabase)
    monkeypatch.setattr(main, "CHAPTER_TRANSLATION_ALIGNMENT_SUPPORTED", True)

    result = await main.import_manual_chapter_translation(
        chapter_row={"id": 999, "chapter_number": 900, "title": "Chuong 900"},
        source_title="Chuong 900",
        source_content="Doan 1.\n\nDoan 2.",
        locale="en",
        translated_title="Imported draft",
        translated_content="Sentence 1.\n\nSentence 2.",
    )

    assert result["translated_locales"] == ["en"]
    assert result["failed_translations"] == []
    published_payloads = [
        item["payload"]
        for item in fake_supabase.upserts
        if item["table"] == "chapter_translations" and item["payload"].get("translation_status") == "published"
    ]
    assert published_payloads
    assert published_payloads[-1]["translation_source"] == "manual_import"
