import pytest

from backend import main


class _Resp:
    def __init__(self, data=None):
        self.data = data if data is not None else []


class _Table:
    def __init__(self, db, name):
        self.db = db
        self.name = name

    def select(self, fields="*"):
        return self

    def eq(self, *args, **kwargs):
        return self

    def in_(self, *args, **kwargs):
        return self

    def upsert(self, payload, on_conflict=None):
        self.db.upserts.append((self.name, payload.copy(), on_conflict))
        return self

    def limit(self, *args, **kwargs):
        return self

    def execute(self):
        return _Resp([])


class _FakeSupabase:
    def __init__(self):
        self.upserts = []

    def table(self, name):
        return _Table(self, name)


@pytest.mark.asyncio
async def test_chapter_translation_requests_each_locale_independently(monkeypatch):
    calls = []
    fake_db = _FakeSupabase()
    monkeypatch.setattr(main, "supabase", fake_db)
    monkeypatch.setattr(main, "chapter_translation_alignment_supported", lambda: False)
    monkeypatch.setattr(main, "chunk_translation_source_text", lambda content: [content])

    async def fake_translate(**kwargs):
        locales = kwargs["target_locales"]
        calls.append(tuple(locales))
        locale = locales[0]
        if locale == "en":
            raise RuntimeError("provider unavailable")
        return {locale: {"title": f"title-{locale}", "content": f"content-{locale}"}}

    async def fake_repair(**kwargs):
        return {
            "title": kwargs["candidate_title"],
            "content": kwargs["candidate_content"],
            "sentence_alignment": {},
            "gate_report": {"passed": True},
        }

    monkeypatch.setattr(main, "translate_chapter_payloads_with_ai", fake_translate)
    monkeypatch.setattr(main, "repair_chapter_translation_candidate_until_publishable", fake_repair)

    result = await main.upsert_chapter_translations(
        {"id": 123, "chapter_number": 834},
        "Tiêu đề",
        "Nội dung tiếng Việt",
        ["en", "zh-CN", "ja"],
    )

    assert calls == [("en",), ("zh-CN",), ("ja",)]
    assert set(result["translated_locales"]) == {"zh-CN", "ja"}
    assert result["failed_translations"] == [
        {"locale": "en", "status_code": 502, "detail": "provider unavailable"}
    ]

    published_locales = {
        payload["locale"]
        for table, payload, _ in fake_db.upserts
        if table == "chapter_translations" and payload.get("translation_status") == "published"
    }
    failed_locales = {
        payload["locale"]
        for table, payload, _ in fake_db.upserts
        if table == "chapter_translations" and payload.get("translation_status") == "failed"
    }
    assert published_locales == {"zh-CN", "ja"}
    assert "en" in failed_locales
