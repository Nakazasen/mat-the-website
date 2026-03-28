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
