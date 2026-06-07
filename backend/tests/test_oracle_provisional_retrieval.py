import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from contextlib import contextmanager

from backend.rag.retrieval import (
    search_wiki_entries,
    search_provisional_library,
    merge_oracle_knowledge_results
)
from backend.routes.ai_oracle import SYSTEM_PROMPT_TEMPLATE, build_rag_answer_prompt

@contextmanager
def patch_oracle_func(func_name, **kwargs):
    import sys
    patched = []
    targets = []
    for mod_name in list(sys.modules.keys()):
        if mod_name.endswith("routes.ai_oracle"):
            targets.append(f"{mod_name}.{func_name}")
    if not targets:
        targets = [f"routes.ai_oracle.{func_name}", f"backend.routes.ai_oracle.{func_name}"]

    is_async = func_name not in ("get_rag_context_for_oracle",)
    mock_obj = AsyncMock(**kwargs) if is_async else MagicMock(**kwargs)
    for target in targets:
        try:
            p = patch(target, mock_obj)
            p.start()
            patched.append(p)
        except Exception:
            pass
    try:
        yield mock_obj
    finally:
        for p in patched:
            try:
                p.stop()
            except Exception:
                pass

# Mocking Supabase query execution
class MockSupabase:
    def __init__(self, data):
        self.data = data
        self.queries = []

    def table(self, table_name):
        self.queries.append(table_name)
        return MockQueryBuilder(self, table_name)

class MockQueryBuilder:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.filters = {}

    def select(self, fields):
        self.filters["select"] = fields
        return self

    def ilike(self, field, value):
        self.filters[f"ilike_{field}"] = value
        return self

    def or_(self, value):
        self.filters["or"] = value
        return self

    def in_(self, field, values):
        self.filters[f"in_{field}"] = values
        return self

    def limit(self, value):
        self.filters["limit"] = value
        return self

    def execute(self):
        class MockResponse:
            def __init__(self, data):
                self.data = data
        return MockResponse(self.client.data.get(self.table_name, []))

# 1. Test search_wiki_entries
def test_search_wiki_entries():
    mock_data = {
        "wiki_entries": [
            {
                "title": "Hàn Phong",
                "category": "Nhân vật",
                "summary": "Nhân vật chính",
                "content": "Băng hệ dị năng"
            },
            {
                "title": "Tinh thể zombie đột biến",
                "category": "Vật phẩm",
                "summary": "Tinh thể hiếm",
                "content": "Dùng để nâng cấp"
            }
        ]
    }
    client = MockSupabase(mock_data)

    # Check simple search without chapter cap
    results = search_wiki_entries(client, "Hàn Phong", limit=5)
    assert len(results) == 1
    assert results[0]["title"] == "Hàn Phong"
    assert results[0]["source"] == "wiki_entries"
    assert results[0]["quality_class"] == "canon"

    # Check search matches title properly
    results = search_wiki_entries(client, "zombie", limit=5)
    assert len(results) == 1
    assert results[0]["title"] == "Tinh thể zombie đột biến"

# 2. Test search_provisional_library quality gate and evidence filtering
def test_search_provisional_library():
    mock_data = {
        "provisional_library": [
            {
                "id": "1",
                "name": "Bàng Lâm",
                "type": "entity",
                "summary": "Phản phái",
                "confidence": 0.8,
                "quality_class": "high_confidence",
                "first_chapter": 2,
                "evidence": [
                    {"chapter_number": 2, "content_preview": "Bàng Lâm xuất hiện"},
                    {"chapter_number": 6, "content_preview": "Bàng Lâm bị đánh bại"}
                ]
            },
            {
                "id": "2",
                "name": "Tinh thể đột biến cấp 2",
                "type": "item",
                "summary": "Vật phẩm cấp cao",
                "confidence": 0.3,
                "quality_class": "weak_evidence",  # Should be skipped by quality gate
                "first_chapter": 3,
                "evidence": [
                    {"chapter_number": 3, "content_preview": "Tìm thấy tinh thể"}
                ]
            }
        ]
    }
    client = MockSupabase(mock_data)

    # Quality gate test: only high/medium confidence
    results = search_provisional_library(client, "Bàng Lâm", limit=5)
    assert len(results) == 1
    assert results[0]["name"] == "Bàng Lâm"
    assert results[0]["quality_class"] == "high_confidence"

    results = search_provisional_library(client, "tinh thể", limit=5)
    assert len(results) == 0  # weak_evidence is skipped

    # Spoiler filtering on evidence list test
    results = search_provisional_library(client, "Bàng Lâm", chapter_cap=3, limit=5)
    assert len(results) == 1
    assert len(results[0]["evidence"]) == 1  # Chapter 6 evidence is filtered out
    assert results[0]["evidence"][0]["chapter_number"] == 2
    assert results[0]["first_chapter"] == 2

    # Spoiler filtering out the entire record if no evidence remains or first_chapter > cap
    results = search_provisional_library(client, "Bàng Lâm", chapter_cap=1, limit=5)
    assert len(results) == 0  # first_chapter is 2, cap is 1

# 3. Precision tests for provisional library search
def test_search_provisional_library_precision():
    mock_data = {
        "provisional_library": [
            {
                "id": "1",
                "name": "Phá Tâm Linh",
                "type": "ability",
                "summary": "Kỹ năng dị năng giả",
                "confidence": 0.9,
                "quality_class": "high_confidence",
                "first_chapter": 5,
                "evidence": [
                    {"chapter_number": 5, "content_preview": "Hàn Phong học được Phá Tâm Linh"}
                ]
            },
            {
                "id": "2",
                "name": "Tinh thể zombie",
                "type": "item",
                "summary": "Vật phẩm nâng cấp",
                "confidence": 0.8,
                "quality_class": "medium_confidence",
                "first_chapter": 4,
                "evidence": [
                    {"chapter_number": 4, "content_preview": "Hàn Phong tìm thấy tinh thể zombie"}
                ]
            }
        ]
    }
    client = MockSupabase(mock_data)

    # 1. Query "Tinh thể zombie là gì?" should NOT return "Phá Tâm Linh"
    results = search_provisional_library(client, "Tinh thể zombie là gì?", limit=5)
    assert len(results) == 1
    assert results[0]["name"] == "Tinh thể zombie"

    # 2. Query "Phá Tâm Linh là gì?" should return "Phá Tâm Linh"
    results = search_provisional_library(client, "Phá Tâm Linh là gì?", limit=5)
    assert len(results) == 1
    assert results[0]["name"] == "Phá Tâm Linh"

    # 3. Unrelated query like "Vũ khí đột biến là gì?" should return 0 since names do not match
    results = search_provisional_library(client, "Vũ khí đột biến là gì?", limit=5)
    assert len(results) == 0

# 4. Test merge_oracle_knowledge_results
def test_merge_oracle_knowledge_results():
    wiki_results = [
        {
            "title": "Hàn Phong",
            "name": "Hàn Phong",
            "category": "Nhân vật",
            "summary": "Nhân vật chính",
            "source": "wiki_entries",
            "quality_class": "canon"
        }
    ]
    provisional_results = [
        {
            "title": "Hàn Phong",
            "name": "Hàn Phong",
            "category": "Nhân vật",
            "summary": "Dị năng giả hệ băng",
            "source": "provisional_library",
            "quality_class": "high_confidence"
        },
        {
            "title": "Tinh thể zombie",
            "name": "Tinh thể zombie",
            "category": "Vật phẩm",
            "summary": "Vật phẩm nâng cấp",
            "source": "provisional_library",
            "quality_class": "medium_confidence"
        }
    ]

    # Merge should prioritize canon and deduplicate
    merged = merge_oracle_knowledge_results(wiki_results, provisional_results, limit=5)
    assert len(merged) == 2
    assert merged[0]["source"] == "wiki_entries"  # Canon version preserved
    assert merged[1]["source"] == "provisional_library"  # Tinh thể zombie included

# 5. Test warning instructions in prompt templates
def test_prompt_warnings():
    assert "THƯ VIỆN TỰ ĐỘNG" in SYSTEM_PROMPT_TEMPLATE
    assert "chưa phải canon wiki chính thức" in SYSTEM_PROMPT_TEMPLATE

    prompt = build_rag_answer_prompt("question", "entity", "story", 10)
    assert "THƯ VIỆN TỰ ĐỘNG" in prompt
    assert "chưa phải canon wiki chính thức" in prompt

# 6. Test ask_oracle local wiki response warning appending
@pytest.mark.asyncio
async def test_ask_oracle_local_wiki_warning():
    try:
        from main import app
    except ImportError:
        from backend.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

    # We patch get_wiki_context to return a string containing provisional prefix
    prov_context = "[THƯ VIỆN TỰ ĐỘNG - high_confidence] Tinh thể zombie: Dùng để nâng cấp. Evidence: Chương 5"

    with patch_oracle_func("check_cache", return_value=None), \
         patch_oracle_func("get_wiki_context", return_value=prov_context), \
         patch_oracle_func("get_chapter_context", return_value=""), \
         patch_oracle_func("check_rate_limit", return_value=True), \
         patch_oracle_func("store_cache", return_value=None):

         response = client.post("/oracle/ask", json={
             "question": "Tinh thể zombie",
             "chapter_progress": 10
         })

         assert response.status_code == 200
         data = response.json()
         assert data["source"] == "local_wiki"
         assert "Lưu ý: Dữ liệu trên được trích xuất tự động từ truyện, chưa phải canon wiki chính thức." in data["answer"]


def test_is_exact_or_near_match_logic():
    from backend.rag.retrieval import is_exact_or_near_match
    assert is_exact_or_near_match("Hàn Phong", "Hàn Phong là ai?") is True
    assert is_exact_or_near_match("Tinh thể zombie", "Tinh thể zombie là gì?") is True
    assert is_exact_or_near_match("Zombie Cấp 3 (Biến Thể)", "Tinh thể zombie là gì?") is False
    assert is_exact_or_near_match("Phá Tâm Linh", "Phá Tâm Linh là gì?") is True


@pytest.mark.asyncio
async def test_get_wiki_context_abstention_clarification():
    from backend.routes.ai_oracle import get_wiki_context
    mock_data = {
        "wiki_entries": [
            {
                "title": "Zombie Cấp 3 (Biến Thể)",
                "category": "Sinh vật",
                "summary": "Một loại zombie nguy hiểm.",
                "content": "Xuất hiện nhiều ở thành phố."
            }
        ],
        "provisional_library": []
    }
    client = MockSupabase(mock_data)

    res = await get_wiki_context(client, "Tinh thể zombie là gì?", chapter_cap=10)
    assert "[CHƯA CÓ MỤC ĐỊNH DANH CHÍNH XÁC]" in res
    assert "Chưa tìm thấy mục chính xác cho 'Tinh thể zombie'" in res
    assert "Các mục liên quan tìm thấy:" in res
    assert "[CANON WIKI] Zombie Cấp 3 (Biến Thể)" in res

    mock_data_exact = {
        "wiki_entries": [
            {
                "title": "Hàn Phong",
                "category": "Nhân vật",
                "summary": "Đoàn trưởng",
                "content": ""
            }
        ],
        "provisional_library": []
    }
    client_exact = MockSupabase(mock_data_exact)
    res_exact = await get_wiki_context(client_exact, "Hàn Phong là ai?", chapter_cap=10)
    assert "[CHƯA CÓ MỤC ĐỊNH DANH CHÍNH XÁC]" not in res_exact
    assert "[CANON WIKI] Hàn Phong" in res_exact
