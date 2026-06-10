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
