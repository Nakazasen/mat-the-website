import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.security_utils import get_git_commit, get_git_branch
from backend.rag.retrieval import is_event_plot_question


def test_git_metadata_helpers():
    with patch.dict(os.environ, {"RENDER_GIT_COMMIT": "test-commit-sha", "RENDER_GIT_BRANCH": "test-branch"}):
        assert get_git_commit() == "test-commit-sha"
        assert get_git_branch() == "test-branch"

    with patch.dict(os.environ, {}, clear=True):
        # Should fallback to running subprocess git or return None
        # We patch subprocess to check fallback logic
        with patch("subprocess.check_output") as mock_sub:
            mock_sub.return_value = b"fallback-sha\n"
            assert get_git_commit() == "fallback-sha"

            mock_sub.return_value = b"fallback-branch\n"
            assert get_git_branch() == "fallback-branch"


def test_is_event_plot_question():
    assert is_event_plot_question("chiến dịch lệ giang diễn ra như thế nào?") is True
    assert is_event_plot_question("diễn biến chương 5") is True
    assert is_event_plot_question("sự kiện tiếp theo là gì?") is True
    assert is_event_plot_question("Hàn Phong là ai?") is False
    assert is_event_plot_question("Tinh thể tiến hóa là gì?") is False


@pytest.mark.asyncio
async def test_get_wiki_context_phrase_gating():
    # Test that get_wiki_context filters out irrelevant entities (e.g. Zombie Cấp 3)
    # when "Lệ Giang" is mentioned.
    from backend.routes.ai_oracle import get_wiki_context

    mock_supabase = MagicMock()

    # Dummy search outputs
    dummy_wiki = [
        {"title": "Lệ Giang", "category": "location", "summary": "Sông Lệ Giang gần huyện Tam Giang", "source": "wiki_entries"},
        {"title": "Zombie Cấp 3", "category": "monster", "summary": "Zombie tiến hóa", "source": "wiki_entries"},
    ]
    dummy_prov = [
        {"name": "Thể Thôn Phệ Lệ Giang", "type": "entity", "summary": "Thể thôn phệ tại Lệ Giang", "quality_class": "high_confidence", "source": "provisional_library"},
        {"name": "Quân Lệnh Như Sơn", "type": "item", "summary": "Vật phẩm Quân lệnh", "quality_class": "high_confidence", "source": "provisional_library"},
    ]


    with patch("backend.rag.retrieval.search_wiki_entries", return_value=dummy_wiki), \
         patch("backend.rag.retrieval.search_provisional_library", return_value=dummy_prov), \
         patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=[]):


        # Test exact phrase gating: "Lệ Giang"
        context = await get_wiki_context(mock_supabase, "chiến dịch lệ giang diễn ra như thế nào?", 829)

        # Should contain "Lệ Giang" and "Thể Thôn Phệ Lệ Giang"
        assert "Lệ Giang" in context
        assert "Thể Thôn Phệ Lệ Giang" in context

        # Should NOT contain "Zombie Cấp 3" or "Quân Lệnh Như Sơn"
        assert "Zombie Cấp 3" not in context
        assert "Quân Lệnh Như Sơn" not in context

        # Since it is an event plot query, it should have triggered story chunks search
        assert "[DIỄN BIẾN TRUYỆN CHO" in context or "WIKI_EMPTY_CONTEXT" not in context


@pytest.mark.asyncio
async def test_get_rag_context_forces_event_plot():
    # Test that get_rag_context_for_oracle forces retrieval for event/plot questions
    # even if ORACLE_RAG_ENABLED is false/not set.
    from backend.routes.ai_oracle import get_rag_context_for_oracle

    with patch.dict(os.environ, {"ORACLE_RAG_ENABLED": "false"}), \
         patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical") as mock_search, \
         patch("backend.rag.context_builder.build_rag_context_block") as mock_build:

        mock_search.return_value = [{"content_plain": "Test chunk"}]
        mock_build.return_value = {"context_text": "Story details", "chunks_used": 1}

        # Event question should query story chunks
        res = get_rag_context_for_oracle("chiến dịch lệ giang diễn ra như thế nào?", 829)
        assert res is not None
        assert res["context_text"] == "Story details"
        mock_search.assert_called_once()


def test_clean_answer_for_reader():
    from backend.routes.ai_oracle import clean_answer_for_reader
    assert clean_answer_for_reader("[DỮ LIỆU HỆ THỐNG]\nSome answer") == "Some answer"
    assert clean_answer_for_reader("No tag here") == "No tag here"
    assert clean_answer_for_reader("") == ""
    assert clean_answer_for_reader(None) == ""


@pytest.mark.asyncio
async def test_ask_oracle_admin_vs_reader():
    from backend.routes.ai_oracle import ask_oracle, OracleRequest
    from unittest.mock import AsyncMock, MagicMock

    mock_supabase = MagicMock()

    with patch("backend.routes.ai_oracle.check_cache", new_callable=AsyncMock) as mock_cache, \
         patch("backend.routes.ai_oracle.is_admin_request", new_callable=AsyncMock) as mock_admin, \
         patch("backend.main.supabase", mock_supabase):

        mock_cache.return_value = "[DỮ LIỆU HỆ THỐNG]\nCached answer content"
        body = OracleRequest(question="test question", chapter_progress=10)
        mock_request = MagicMock()
        mock_response = MagicMock()

        # Test as admin
        mock_admin.return_value = True
        res_admin = await ask_oracle(body, mock_request, mock_response)
        assert "[DỮ LIỆU HỆ THỐNG]" in res_admin.answer

        # Test as normal reader
        mock_admin.return_value = False
        res_reader = await ask_oracle(body, mock_request, mock_response)
        assert "[DỮ LIỆU HỆ THỐNG]" not in res_reader.answer
        assert res_reader.answer == "Cached answer content"


@pytest.mark.asyncio
async def test_le_giang_campaign_does_not_match_location_only_chunks():
    from backend.routes.ai_oracle import get_wiki_context
    mock_supabase = MagicMock()

    dummy_chunks = [
        {"content_plain": "gần sông Lệ Giang...", "chapter_title": "Chương 55", "source": "story_chunks"},
        {"content_plain": "cầu Lệ Giang...", "chapter_title": "Chương 100", "source": "story_chunks"},
        {"content_plain": "bờ sông Lệ Giang...", "chapter_title": "Chương 150", "source": "story_chunks"},
    ]

    with patch("backend.rag.retrieval.search_wiki_entries", return_value=[]), \
         patch("backend.rag.retrieval.search_provisional_library", return_value=[]), \
         patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=dummy_chunks):

         context = await get_wiki_context(mock_supabase, "chiến dịch lệ giang diễn ra như thế nào?", 829)
         assert "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang." in context


@pytest.mark.asyncio
async def test_le_giang_campaign_accepts_event_chunks():
    from backend.routes.ai_oracle import get_wiki_context
    mock_supabase = MagicMock()

    dummy_chunks = [
        {"content_plain": "Một nhiệm vụ khó khăn như thanh tẩy Thể Thôn Phệ Lệ Giang, chính phủ chắc chắn phải huy động...", "chapter_title": "Chương 180", "source": "story_chunks"},
    ]

    with patch("backend.rag.retrieval.search_wiki_entries", return_value=[]), \
         patch("backend.rag.retrieval.search_provisional_library", return_value=[]), \
         patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=dummy_chunks):

         context = await get_wiki_context(mock_supabase, "chiến dịch lệ giang diễn ra như thế nào?", 829)
         assert "thanh tẩy Thể Thôn Phệ Lệ Giang" in context


@pytest.mark.asyncio
async def test_event_plot_cache_hit_rejected_when_semantically_stale():
    from backend.routes.ai_oracle import ask_oracle, OracleRequest
    from unittest.mock import AsyncMock
    mock_supabase = MagicMock()

    # Mocking cache returning stale location-only content
    stale_cache = "[DỮ LIỆU HỆ THỐNG]\nsông Lệ Giang gần cầu Lệ Giang, bờ sông Lệ Giang chứa tài nguyên thủy sản và kho vũ khí."

    with patch("backend.routes.ai_oracle.check_cache", new_callable=AsyncMock) as mock_check, \
         patch("backend.routes.ai_oracle.delete_cache_entry", new_callable=AsyncMock) as mock_delete, \
         patch("backend.routes.ai_oracle.get_wiki_context", new_callable=AsyncMock) as mock_wiki, \
         patch("backend.main.supabase", mock_supabase):

         mock_check.return_value = stale_cache
         mock_wiki.return_value = "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang."

         body = OracleRequest(question="chiến dịch lệ giang diễn ra như thế nào?", chapter_progress=829)
         mock_req = MagicMock()
         mock_res = MagicMock()

         res = await ask_oracle(body, mock_req, mock_res)

         # The stale cache must be deleted
         mock_delete.assert_called_once()
         # The recomputed clean answer should be returned
         assert "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang." in res.answer


def test_runtime_truth_report_requires_semantic_terms():
    import json
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rag", "generated_oracle_runtime_truth_report.json")
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert len(report) > 0
    case = report[0]
    assert "semantic_required_any_terms" in case
    assert "semantic_forbidden_patterns" in case
    assert "chiến dịch" in case["semantic_required_any_terms"]
    assert "sông Lệ Giang" in case["semantic_forbidden_patterns"]


@pytest.mark.asyncio
async def test_oracle_answer_for_le_giang_campaign_abstains_when_no_semantic_evidence():
    from backend.routes.ai_oracle import ask_oracle, OracleRequest
    from unittest.mock import AsyncMock
    mock_supabase = MagicMock()

    # Mock search_story_chunks to return only location/non-event chunks
    dummy_chunks = [
        {"content_plain": "sông Lệ Giang", "chapter_title": "Chương 55", "source": "story_chunks"},
        {"content_plain": "cầu Lệ Giang", "chapter_title": "Chương 100", "source": "story_chunks"},
    ]

    with patch("backend.routes.ai_oracle.check_cache", new_callable=AsyncMock) as mock_cache, \
         patch("backend.rag.retrieval.search_wiki_entries", return_value=[]), \
         patch("backend.rag.retrieval.search_provisional_library", return_value=[]), \
         patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=dummy_chunks), \
         patch("backend.main.supabase", mock_supabase):

         mock_cache.return_value = None
         body = OracleRequest(question="chiến dịch lệ giang diễn ra như thế nào?", chapter_progress=829)
         mock_req = MagicMock()
         mock_res = MagicMock()

         res = await ask_oracle(body, mock_req, mock_res)
         assert res.answer == "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang."
