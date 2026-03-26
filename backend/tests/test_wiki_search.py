import pytest

from backend.routes import wiki_search


class FakeQuery:
    def __init__(self, rows):
        self._rows = list(rows)

    def select(self, _fields):
        return self

    def ilike(self, field_name, pattern):
        needle = pattern.strip("%").lower()
        self._rows = [
            row for row in self._rows
            if needle in str(row.get(field_name, "")).lower()
        ]
        return self

    def eq(self, field_name, value):
        self._rows = [row for row in self._rows if row.get(field_name) == value]
        return self

    def lte(self, field_name, value):
        self._rows = [
            row for row in self._rows
            if row.get(field_name) is not None and row.get(field_name) <= value
        ]
        return self

    def order(self, field_name, desc=False):
        self._rows = sorted(
            self._rows,
            key=lambda row: row.get(field_name) if row.get(field_name) is not None else -1,
            reverse=desc,
        )
        return self

    def limit(self, value):
        self._rows = self._rows[:value]
        return self

    def execute(self):
        return type("FakeResponse", (), {"data": self._rows})()


class FakeSupabase:
    def __init__(self, tables):
        self._tables = tables

    def table(self, table_name):
        return FakeQuery(self._tables.get(table_name, []))


@pytest.mark.asyncio
async def test_get_character_uses_title_schema_and_summary_fallback(monkeypatch):
    fake_tables = {
        "wiki_entries": [
            {
                "id": "char-1",
                "title": "Han Phong",
                "faction": "Tram Chi Huy",
                "status": "Dang chien dau",
                "ability": "Thong tri he thong",
                "chapter_introduced": 5,
                "summary": "Nhan vat trung tam cua truyen.",
            }
        ]
    }
    monkeypatch.setattr(wiki_search, "_get_supabase", lambda: FakeSupabase(fake_tables))

    profile = await wiki_search.get_character(name="Han Phong", chapter=10)

    assert profile is not None
    assert profile.name == "Han Phong"
    assert profile.first_appearance == 5
    assert profile.description == "Nhan vat trung tam cua truyen."


@pytest.mark.asyncio
async def test_get_character_blocks_future_spoilers(monkeypatch):
    fake_tables = {
        "wiki_entries": [
            {
                "title": "Mat Na Do",
                "status": "Bi an",
                "chapter_introduced": 25,
            }
        ]
    }
    monkeypatch.setattr(wiki_search, "_get_supabase", lambda: FakeSupabase(fake_tables))

    profile = await wiki_search.get_character(name="Mat Na Do", chapter=10)

    assert profile is None


@pytest.mark.asyncio
async def test_get_character_falls_back_to_name_field(monkeypatch):
    fake_tables = {
        "wiki_entries": [
            {
                "name": "Tran Phong",
                "faction": "Doanh trai Tay Bac",
                "status": "Bi thuong",
                "ability": "Xa kich",
                "first_appearance": 3,
                "description": "Dong doi cua nhan vat chinh.",
            }
        ]
    }
    monkeypatch.setattr(wiki_search, "_get_supabase", lambda: FakeSupabase(fake_tables))

    profile = await wiki_search.get_character(name="Tran Phong", chapter=10)

    assert profile is not None
    assert profile.name == "Tran Phong"
    assert profile.first_appearance == 3
    assert profile.description == "Dong doi cua nhan vat chinh."


@pytest.mark.asyncio
async def test_get_character_uses_translation_when_locale_is_available(monkeypatch):
    fake_tables = {
        "wiki_entries": [
            {
                "id": "char-1",
                "title": "Han Phong",
                "summary": "Ban goc tieng Viet",
                "chapter_introduced": 2,
            }
        ],
        "wiki_entry_translations": [
            {
                "wiki_entry_id": "char-1",
                "locale": "zh-CN",
                "title": "韩枫",
                "summary": "中文条目",
            }
        ],
    }
    monkeypatch.setattr(wiki_search, "_get_supabase", lambda: FakeSupabase(fake_tables))

    profile = await wiki_search.get_character(name="Han Phong", chapter=10, locale="zh-CN")

    assert profile is not None
    assert profile.name == "韩枫"
    assert profile.description == "中文条目"
