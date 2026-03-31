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
        "zh-CN": { "title": "你好", "content": "世界" },
        "ja": { "title": "こんにちは", "content": "世界" }
      }
    }
    """

    parsed = main.parse_multilocale_translation_payload(payload, ["en", "zh-CN", "ja"], ["title", "content"])

    assert parsed["en"]["title"] == "Hello"
    assert parsed["zh-CN"]["content"] == "世界"
    assert parsed["ja"]["title"] == "こんにちは"


def test_build_guide_translation_slug_uses_locale_suffix():
    assert main.build_guide_translation_slug("reader-guide", "zh-cn") == "reader-guide__zh-CN"


def test_parse_json_like_payload_raises_useful_error_for_invalid_json():
    with pytest.raises(ValueError) as exc_info:
        main.parse_json_like_payload('{"title":"abc","content":"unterminated}')

    assert "Could not parse JSON payload" in str(exc_info.value)
    assert "Snippet:" in str(exc_info.value)


def test_build_chapter_sentence_alignment_preserves_sentence_order():
    source_chunks = [
        "S1. S2.",
        "S3. S4.",
    ]
    translated_chunks = [
        "T1. T2.",
        "T3. T4.",
    ]
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
        source_text="Câu 1. Câu 2.",
        translated_text="文1。文2。",
    )

    assert payload["translated_sentence_count"] == 2
    assert len(payload["entries"]) == 2
    assert payload["entries"][0]["translated_excerpt"] == "文1。"
    assert payload["entries"][1]["translated_excerpt"] == "文2。"


def test_build_chapter_sentence_alignment_includes_content_hashes():
    payload = main.build_chapter_sentence_alignment(
        source_text="Câu 1. Câu 2.",
        translated_text="Sentence 1. Sentence 2.",
    )

    assert payload["source_content_hash"] == main.build_content_hash("Câu 1. Câu 2.")
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


def test_is_translation_retryable_treats_transient_unavailable_as_retryable():
    exc = HTTPException(status_code=503, detail="This model is currently experiencing high demand. Please try again later.")

    assert main.is_translation_retryable(exc) is True


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
        return {
            "en": {
                "title": "Hello",
                "content": "World",
            }
        }

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
            self.filters = {}

        def select(self, _fields):
            return self

        def eq(self, key, value):
            self.filters[key] = value
            return self

        def in_(self, key, value):
            self.filters[key] = value
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
    assert failed_payloads, "Expected failed upsert payload to be recorded"
    assert failed_payloads[0]["title"] == ""
    assert failed_payloads[0]["content"] == ""


@pytest.mark.asyncio
async def test_upsert_chapter_translations_quality_gate_blocks_publish(monkeypatch):
    class FakeExecuteResult:
        def __init__(self, data):
            self.data = data

    class FakeQuery:
        def __init__(self, table_name, store):
            self.table_name = table_name
            self.store = store
            self.filters = {}

        def select(self, _fields):
            return self

        def eq(self, key, value):
            self.filters[key] = value
            return self

        def in_(self, key, value):
            self.filters[key] = value
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
        source_text = "S1. S2."
        translated_text = "T1. T2. T3. T4."
        return {
            "en": {
                "title": "Bad structure",
                "content": translated_text,
                "sentence_alignment": main.build_chapter_sentence_alignment(
                    source_text=source_text,
                    translated_text=translated_text,
                ),
            }
        }

    monkeypatch.setattr(main, "translate_chapter_payloads_with_ai", fake_translate_chapter_payloads_with_ai)

    result = await main.upsert_chapter_translations(
        chapter_row={"id": 999, "chapter_number": 900, "title": "Chuong 900"},
        title="Chuong 900",
        content="S1. S2.",
        locales=["en"],
    )

    assert result["translated_locales"] == []
    assert result["failed_translations"]
    assert result["failed_translations"][0]["status_code"] == 422
    assert "Quality gate blocked publish" in result["failed_translations"][0]["detail"]

    failed_payloads = [
        item["payload"]
        for item in fake_supabase.upserts
        if item["table"] == "chapter_translations" and item["payload"].get("translation_status") == "failed"
    ]
    assert failed_payloads
    assert failed_payloads[-1]["title"] == "Bad structure"
    assert failed_payloads[-1]["content"] == "T1. T2. T3. T4."


@pytest.mark.asyncio
async def test_improve_chapter_translations_quality_gate_blocks_publish(monkeypatch):
    class FakeExecuteResult:
        def __init__(self, data):
            self.data = data

    class FakeQuery:
        def __init__(self, table_name, store):
            self.table_name = table_name
            self.store = store
            self.filters = {}

        def select(self, _fields):
            return self

        def eq(self, key, value):
            self.filters[key] = value
            return self

        def in_(self, key, value):
            self.filters[key] = value
            return self

        def limit(self, _value):
            return self

        def execute(self):
            if self.table_name == "chapter_translations":
                return FakeExecuteResult(
                    [
                        {
                            "locale": "en",
                            "attempt_count": 0,
                            "title": "Current title",
                            "content": "S1. S2.",
                            "summary": "S1. S2.",
                            "translated_at": None,
                            "sentence_alignment": main.build_chapter_sentence_alignment(
                                source_text="S1. S2.",
                                translated_text="S1. S2.",
                            ),
                        }
                    ]
                )
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

    async def fake_refine_chapter_translation_with_ai(**_kwargs):
        source_text = "S1. S2."
        improved_text = "T1. T2. T3. T4."
        return {
            "title": "Improved but blocked",
            "content": improved_text,
            "sentence_alignment": main.build_chapter_sentence_alignment(
                source_text=source_text,
                translated_text=improved_text,
            ),
        }

    monkeypatch.setattr(main, "refine_chapter_translation_with_ai", fake_refine_chapter_translation_with_ai)

    result = await main.improve_chapter_translations(
        chapter_row={"id": 999, "chapter_number": 900, "title": "Chuong 900"},
        title="Chuong 900",
        content="S1. S2.",
        locales=["en"],
    )

    assert result["translated_locales"] == []
    assert result["failed_translations"]
    assert result["failed_translations"][0]["status_code"] == 422
    assert "Quality gate blocked publish" in result["failed_translations"][0]["detail"]

    failed_payloads = [
        item["payload"]
        for item in fake_supabase.upserts
        if item["table"] == "chapter_translations" and item["payload"].get("translation_status") == "failed"
    ]
    assert failed_payloads
    assert failed_payloads[-1]["title"] == "Improved but blocked"
    assert failed_payloads[-1]["content"] == "T1. T2. T3. T4."
