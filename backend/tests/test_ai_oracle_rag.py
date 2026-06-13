import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from contextlib import contextmanager

from backend.routes.ai_oracle import (
    is_oracle_rag_enabled,
    get_rag_context_for_oracle,
    call_ai_provider_result,
)

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

    is_async = func_name != "get_rag_context_for_oracle"
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

# Test 1 & 2: is_oracle_rag_enabled default and values
def test_is_oracle_rag_enabled():
    # Clear env
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

    # Default is False
    assert is_oracle_rag_enabled() is False

    # Test true values (case-insensitive)
    for true_val in ["1", "true", "yes", "on", "TRUE", "Yes", "ON"]:
        os.environ["ORACLE_RAG_ENABLED"] = true_val
        assert is_oracle_rag_enabled() is True

    # Test false values
    for false_val in ["0", "false", "no", "off", "anything_else", ""]:
        os.environ["ORACLE_RAG_ENABLED"] = false_val
        assert is_oracle_rag_enabled() is False

    # Cleanup
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

# Test 3: get_rag_context_for_oracle returns None when flag is OFF
def test_get_rag_context_for_oracle_returns_none_when_disabled():
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

    context = get_rag_context_for_oracle("Hàn Phong", chapter_cap=5)
    assert context is None

# Test 4: get_rag_context_for_oracle catches exceptions and returns None safely
def test_get_rag_context_for_oracle_handles_error_safely():
    os.environ["ORACLE_RAG_ENABLED"] = "true"

    # Mock search function to raise Exception
    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", side_effect=Exception("Database down")):
        context = get_rag_context_for_oracle("Hàn Phong", chapter_cap=5)
        # Should catch exception, print warning, and return None (no crash)
        assert context is None

    # Cleanup
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

# Test 5 & 7: get_rag_context_for_oracle returns formatted context and citations when ON
def test_get_rag_context_for_oracle_success():
    os.environ["ORACLE_RAG_ENABLED"] = "true"

    mock_results = [
        {
            "chapter_number": 1,
            "chapter_title": "Đầu lâu khổng lồ ngoài cửa sổ",
            "chunk_index": 0,
            "content_plain": "Hàn Phong đứng trước bàn giám đốc.",
            "content_hash": "hash123"
        }
    ]

    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=mock_results):
        context_data = get_rag_context_for_oracle("Hàn Phong", chapter_cap=5)
        assert context_data is not None
        assert context_data["chunks_used"] == 1
        assert "[CHƯƠNG 1 - Đầu lâu khổng lồ ngoài cửa sổ | chunk 0]" in context_data["context_text"]
        assert "Hàn Phong đứng trước bàn giám đốc." in context_data["context_text"]
        assert len(context_data["citations"]) == 1
        assert context_data["citations"][0]["content_hash"] == "hash123"

    # Cleanup
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

# Test 6: call_ai_provider_result formats prompt correctly and keeps old prompt when rag_context is empty
@pytest.mark.asyncio
async def test_call_ai_provider_result_prompt_formatting():
    mock_router = MagicMock()
    mock_router.route = AsyncMock()

    # 1. Without RAG context
    with patch("main.get_provider_router", return_value=mock_router, create=True), \
         patch("backend.main.get_provider_router", return_value=mock_router, create=True):

        await call_ai_provider_result(
            question="Hàn Phong là ai?",
            chapter_cap=2,
            wiki_context="Wiki info",
            chapter_context="Chapter info",
            rag_context=""
        )

        # Check that system_instruction does not contain RAG section
        args, kwargs = mock_router.route.call_args
        ai_request = args[0]
        assert "[BẰNG CHỨNG TRÍCH ĐOẠN TỪ CÁC CHƯƠNG TRUYỆN]" not in ai_request.system_instruction
        assert "Wiki info" in ai_request.system_instruction

    mock_router.route.reset_mock()

    # 2. With RAG context (Flag ON behavior)
    with patch("main.get_provider_router", return_value=mock_router, create=True), \
         patch("backend.main.get_provider_router", return_value=mock_router, create=True):

        await call_ai_provider_result(
            question="Hàn Phong là ai?",
            chapter_cap=2,
            wiki_context="Wiki info",
            chapter_context="Chapter info",
            rag_context="RAG content"
        )

        # Check that system_instruction contains RAG section
        args, kwargs = mock_router.route.call_args
        ai_request = args[0]
        assert "[BẰNG CHỨNG TRÍCH ĐOẠN TỪ CÁC CHƯƠNG TRUYỆN]" in ai_request.system_instruction
        assert "RAG content" in ai_request.system_instruction
        assert "Wiki info" in ai_request.system_instruction

@pytest.mark.asyncio
async def test_ask_oracle_endpoint_rag_routing():
    import sys
    print("\nALL AI ORACLE MODULES IN SYS:", [k for k in sys.modules.keys() if "ai_oracle" in k])
    try:
        from main import app
    except ImportError:
        from backend.main import app

    from fastapi.testclient import TestClient
    client = TestClient(app)

    # 1. When ORACLE_RAG_ENABLED is OFF
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

    with patch_oracle_func("call_ai_provider_result") as mock_call, \
         patch_oracle_func("check_cache", return_value=None), \
         patch_oracle_func("get_wiki_context", return_value=""), \
         patch_oracle_func("get_chapter_context", return_value=""), \
         patch_oracle_func("check_rate_limit", return_value=True):

        mock_result = MagicMock()
        mock_result.status = "success"
        mock_result.text = "Mock answer that is long enough to pass validation"
        mock_call.return_value = mock_result

        response = client.post("/oracle/ask", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10
        })

        print("DEBUG RESPONSE status:", response.status_code)
        print("DEBUG RESPONSE text:", response.text.encode('ascii', errors='backslashreplace').decode('ascii'))
        print("DEBUG mock_call called:", mock_call.called)
        if mock_call.called:
            print("DEBUG mock_call call_args:", str(mock_call.call_args).encode('ascii', errors='backslashreplace').decode('ascii'))

        assert response.status_code == 200
        assert response.json()["answer"] == "Mock answer that is long enough to pass validation"
        assert response.json()["source"] == "ai_provider"

        args, kwargs = mock_call.call_args
        assert len(args) < 5 or args[4] == ""

    # 2. When ORACLE_RAG_ENABLED is ON
    os.environ["ORACLE_RAG_ENABLED"] = "true"

    with patch_oracle_func("call_ai_provider_result") as mock_call, \
         patch_oracle_func("check_cache", return_value=None), \
         patch_oracle_func("get_wiki_context", return_value=""), \
         patch_oracle_func("get_chapter_context", return_value=""), \
         patch_oracle_func("check_rate_limit", return_value=True), \
         patch_oracle_func("get_rag_context_for_oracle", return_value={"context_text": "Mock RAG Context", "citations": []}):

        mock_result = MagicMock()
        mock_result.status = "success"
        mock_result.text = "Mock RAG answer that is long enough to pass validation"
        mock_call.return_value = mock_result

        response = client.post("/oracle/ask", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10
        })

        assert response.status_code == 200
        assert response.json()["answer"] == "Mock RAG answer that is long enough to pass validation"

        args, kwargs = mock_call.call_args
        assert args[4] == "Mock RAG Context"

    # Cleanup
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]


@pytest.mark.asyncio
async def test_ask_oracle_rag_preview_endpoint():
    try:
        from main import app
    except ImportError:
        from backend.main import app

    from fastapi.testclient import TestClient
    client = TestClient(app)

    # 1. No token env -> 403 Forbidden
    if "ORACLE_RAG_PREVIEW_TOKEN" in os.environ:
        del os.environ["ORACLE_RAG_PREVIEW_TOKEN"]

    response = client.post("/oracle/rag-preview", json={
        "question": "Hàn Phong là ai?",
        "chapter_progress": 10
    })
    assert response.status_code == 403
    assert "token not configured" in response.json()["detail"].lower()

    # Set token env
    os.environ["ORACLE_RAG_PREVIEW_TOKEN"] = "preview_secret_token_123"

    # 2. Has token env but missing header -> 403
    response = client.post("/oracle/rag-preview", json={
        "question": "Hàn Phong là ai?",
        "chapter_progress": 10
    })
    assert response.status_code == 403
    assert "invalid rag preview token" in response.json()["detail"].lower()

    # 3. Wrong token -> 403
    headers = {"X-Oracle-Rag-Preview-Token": "wrong_token"}
    response = client.post("/oracle/rag-preview", json={
        "question": "Hàn Phong là ai?",
        "chapter_progress": 10
    }, headers=headers)
    assert response.status_code == 403
    assert "invalid rag preview token" in response.json()["detail"].lower()

    # Prepare headers with correct token for subsequent tests
    headers = {"X-Oracle-Rag-Preview-Token": "preview_secret_token_123"}

    # 4. Correct token + mock retrieval has context -> 200, chunks_used > 0
    mock_results = [
        {
            "chapter_number": 1,
            "chapter_title": "Đầu lâu khổng lồ ngoài cửa sổ",
            "chunk_index": 0,
            "content_plain": "Hàn Phong đứng trước bàn giám đốc.",
            "content_hash": "hash123"
        }
    ]
    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=mock_results):
        response = client.post("/oracle/rag-preview", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10,
            "limit": 5,
            "max_chunks": 4
        }, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["rag_used"] is True
        assert data["chunks_used"] == 1
        assert "Hàn Phong đứng trước bàn giám đốc." in data["context_preview"]
        assert len(data["citations"]) == 1
        assert data["citations"][0]["content_hash"] == "hash123"

    # 5. Correct token + no results -> 200, rag_used false
    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=[]):
        response = client.post("/oracle/rag-preview", json={
            "question": "Không tồn tại nhân vật này",
            "chapter_progress": 10
        }, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["rag_used"] is False
        assert data["chunks_used"] == 0
        assert data["context_preview"] == ""
        assert data["citations"] == []

    # 6. Retrieval exception -> HTTP 503, no crash
    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", side_effect=Exception("Database connection timed out")):
        response = client.post("/oracle/rag-preview", json={
            "question": "Hàn Phong",
            "chapter_progress": 10
        }, headers=headers)

        assert response.status_code == 503
        assert "Database connection timed out" in response.json()["detail"]

    # 7. Endpoint does not call AI provider
    with patch_oracle_func("call_ai_provider_result") as mock_call:
        with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=[]):
            response = client.post("/oracle/rag-preview", json={
                "question": "Hàn Phong là ai?",
                "chapter_progress": 10
            }, headers=headers)
            assert response.status_code == 200
            assert mock_call.called is False

    # Cleanup token env
    if "ORACLE_RAG_PREVIEW_TOKEN" in os.environ:
        del os.environ["ORACLE_RAG_PREVIEW_TOKEN"]


def test_is_identity_question():
    from backend.routes.ai_oracle import is_identity_question
    # True patterns
    assert is_identity_question("Hàn Phong là ai?") is True
    assert is_identity_question("Công ty Đại Thiên Thần là gì?") is True
    assert is_identity_question("Dịch thể gen cường hóa là vật phẩm gì?") is True
    assert is_identity_question("Đầu lâu khổng lồ là thực thể gì?") is True
    assert is_identity_question("Zombie đột biến cấp 1 là sinh vật gì?") is True
    assert is_identity_question("Quân đội là tổ chức gì?") is True
    assert is_identity_question("Thăng cấp kỹ năng là gì?") is True
    assert is_identity_question("Giới thiệu Hàn Phong") is True
    assert is_identity_question("Thông tin về Bàng Lâm") is True
    assert is_identity_question("Lý Đức là nhân vật nào?") is True

    # False patterns (non-identity, no_data, anti_spoiler)
    assert is_identity_question("đầu lâu khổng lồ xuất hiện ở đâu?") is False
    assert is_identity_question("chương 2 xảy ra chuyện gì?") is False
    assert is_identity_question("Hàn Phong làm gì sau khi tận thế xảy ra?") is False
    assert is_identity_question("tóm tắt chương 3") is False


@pytest.mark.asyncio
async def test_ask_oracle_rag_answer_preview_endpoint():
    try:
        from main import app
    except ImportError:
        from backend.main import app

    from fastapi.testclient import TestClient
    client = TestClient(app)

    # 1. No token env -> 403 Forbidden
    if "ORACLE_RAG_PREVIEW_TOKEN" in os.environ:
        del os.environ["ORACLE_RAG_PREVIEW_TOKEN"]

    response = client.post("/oracle/rag-answer-preview", json={
        "question": "Hàn Phong là ai?",
        "chapter_progress": 10
    })
    assert response.status_code == 403
    assert "token not configured" in response.json()["detail"].lower()

    # Set token env
    os.environ["ORACLE_RAG_PREVIEW_TOKEN"] = "preview_secret_token_123"
    headers = {"X-Oracle-Rag-Preview-Token": "preview_secret_token_123"}

    # 2. Sai token -> 403
    bad_headers = {"X-Oracle-Rag-Preview-Token": "wrong_token"}
    response = client.post("/oracle/rag-answer-preview", json={
        "question": "Hàn Phong là ai?",
        "chapter_progress": 10
    }, headers=bad_headers)
    assert response.status_code == 403
    assert "invalid rag preview token" in response.json()["detail"].lower()

    # 3. Đúng token nhưng no context -> 200, rag_used=false, answer mặc định, không gọi AI router
    try:
        import main
        patch_path = "main.get_provider_router"
    except ImportError:
        patch_path = "backend.main.get_provider_router"

    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=[]), \
         patch_oracle_func("get_entity_context_for_oracle", return_value=None) as mock_entity_getter, \
         patch(patch_path) as mock_router_getter:

        response = client.post("/oracle/rag-answer-preview", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10
        }, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["rag_used"] is False
        assert data["chunks_used"] == 0
        assert data["answer"] == "Dữ liệu hiện có chưa đủ để kết luận."
        assert data["citations"] == []
        assert mock_router_getter.called is False

    # 4. Đúng token + có wiki/entity context cho identity query -> Gọi AI router và trả về câu trả lời 200 với entity_profile_rag_answer_preview
    mock_results = [
        {
            "chapter_number": 1,
            "chapter_title": "Đầu lâu khổng lồ ngoài cửa sổ",
            "chunk_index": 0,
            "content_plain": "Hàn Phong đứng trước bàn giám đốc.",
            "content_hash": "hash123"
        }
    ]
    mock_entity = {
        "context_text": "- Hàn Phong: Nhân vật chính của truyện, mang dị năng hệ băng.",
        "citations": [{"title": "Hàn Phong", "category": "Nhân vật", "source": "wiki_entries"}],
        "source": "entity_profile"
    }

    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=mock_results), \
         patch_oracle_func("get_entity_context_for_oracle", return_value=mock_entity) as mock_entity_getter, \
         patch(patch_path) as mock_router_getter:

        mock_router = MagicMock()
        mock_router.route = AsyncMock()
        mock_router_getter.return_value = mock_router

        from backend.ai_providers.base import AIResult
        mock_ai_result = AIResult(
            status="success",
            text="Hàn Phong là nhân vật chính của bộ truyện Mạt Thế Sinh Hóa Nguy Cơ.",
            provider="mock_provider",
            model="mock_model"
        )
        mock_router.route.return_value = mock_ai_result

        response = client.post("/oracle/rag-answer-preview", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10,
            "limit": 5,
            "max_chunks": 4
        }, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["rag_used"] is True
        assert data["chunks_used"] == 1
        assert "nhân vật chính" in data["answer"].lower()
        assert len(data["answer"]) >= 24  # MIN_CACHEABLE_LENGTH
        assert data["source"] == "entity_profile_rag_answer_preview"
        assert len(data["citations"]) == 2  # 1 entity profile, 1 story chunk
        assert data["citations"][0]["title"] == "Hàn Phong"
        assert data["citations"][1]["content_hash"] == "hash123"

        args, kwargs = mock_router.route.call_args
        ai_request = args[0]
        assert "ENTITY_CONTEXT" in ai_request.system_instruction
        assert "STORY_EVIDENCE" in ai_request.system_instruction
        assert "Hàn Phong" in ai_request.system_instruction
        assert "ƯU TIÊN HÀNG ĐẦU thông tin định danh từ ENTITY_CONTEXT" in ai_request.system_instruction

    # 5. Đúng token + identity query không có wiki/entity context -> fallback_story_chunks_rag_answer_preview
    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=mock_results), \
         patch_oracle_func("get_entity_context_for_oracle", return_value=None) as mock_entity_getter, \
         patch(patch_path) as mock_router_getter:

        mock_router = MagicMock()
        mock_router.route = AsyncMock()
        mock_router_getter.return_value = mock_router

        from backend.ai_providers.base import AIResult
        mock_ai_result = AIResult(
            status="success",
            text="Chỉ tìm thấy Hàn Phong xuất hiện trong chương 1.",
            provider="mock_provider",
            model="mock_model"
        )
        mock_router.route.return_value = mock_ai_result

        response = client.post("/oracle/rag-answer-preview", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10
        }, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["rag_used"] is True
        assert data["chunks_used"] == 1
        assert data["source"] == "fallback_story_chunks_rag_answer_preview"
        assert len(data["citations"]) == 1
        assert data["citations"][0]["content_hash"] == "hash123"

    # 6. AI provider router error -> 502 Bad Gateway
    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=mock_results), \
         patch_oracle_func("get_entity_context_for_oracle", return_value=None) as mock_entity_getter, \
         patch(patch_path) as mock_router_getter:

        mock_router = MagicMock()
        mock_router.route = AsyncMock()
        mock_router_getter.return_value = mock_router

        from backend.ai_providers.base import AIResult
        mock_ai_result = AIResult(
            status="error",
            error_message="Quota exceeded",
            provider="mock_provider"
        )
        mock_router.route.return_value = mock_ai_result

        response = client.post("/oracle/rag-answer-preview", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10
        }, headers=headers)

        assert response.status_code == 502
        assert "Multi-provider router error: Quota exceeded" in response.json()["detail"]

    # Cleanup token env
    if "ORACLE_RAG_PREVIEW_TOKEN" in os.environ:
        del os.environ["ORACLE_RAG_PREVIEW_TOKEN"]
