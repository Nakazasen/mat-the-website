import inspect
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.routes import ai_oracle

PRODUCTION_ORACLE = Path("backend/routes/ai_oracle.py")

FORMER_CANNED_MARKERS = [
    "Chu Vấn sử dụng Nhẫn Ngụy Trang và Thiên Cơ Dẫn Lộ",
    "Hàn Phong phân bổ điểm tiềm năng, chọn kỹ năng chủ động nhị giai",
    "Hàn Phong làm việc tại công ty lừa đảo Đại Thiên Thần",
    "Bến thuyền bờ sông Lệ Giang là nơi Lạc Thanh Thủy dùng dị năng",
]

FORBIDDEN_STATIC_MARKERS = [
    "construct_" + "fallback_grounded_answer",
    "Custom guards for failed " + "benchmark cases",
    "sum-" + "03",
    "loc-" + "01",
    "char-" + "01",
    "event-" + "03",
    "event-" + "07",
    "human_" + "reference_answer",
    "required_" + "facts",
    "optional_" + "facts",
    "expected_" + "answer",
    "benchmark " + "canned",
    "mock " + "answer",
    "answer " + "override",
]

FORMER_TRIGGER_QUESTIONS = [
    "Chương 830 Chu Vấn trộm ba quả trứng như thế nào?",
    "Ở đoạn 830, người tên Chu đã xử lý mấy quả trứng ra sao khi bỏ chạy?",
    "Chu Vấn mặc áo màu gì?",
    "Tóm tắt chương 3",
    "Tóm tắt chương 1",
]


def _empty_contract(chapter_cap=830, sufficient=False):
    return {
        "chunks_exist": False,
        "evidence_relevant": False,
        "evidence_sufficient": sufficient,
        "selected_chunk_count": 0,
        "selected_chunk_refs": [],
        "selected_chapters": [],
        "query_entity_matches": [],
        "query_keyword_matches": [],
        "candidate_fact_spans": [],
        "chapter_scope_valid": True,
        "future_leakage_detected": False,
        "chapter_cap": chapter_cap,
        "reason_code": "NO_SOURCE_EVIDENCE",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("question", FORMER_TRIGGER_QUESTIONS)
async def test_former_trigger_questions_do_not_return_canned_answers(question):
    with patch("backend.routes.ai_oracle.call_ai_provider_result") as provider, \
         patch("backend.routes.ai_oracle.is_grounded_verifier_enabled", return_value=False):
        provider.side_effect = AssertionError("provider must not be required for this deterministic regression")
        final, v_calls, r_calls, _ = await ai_oracle.verify_and_repair_answer(
            question=question,
            effective_chapter_cap=830,
            wiki_context="",
            chapter_context="",
            rag_context="",
            active_patches=[],
            intent="chapter_summary",
            evidence_contract=_empty_contract(),
            draft_answer="Dữ liệu hiện có chưa đủ để kết luận.",
        )
    assert v_calls == 0
    assert r_calls == 0
    assert any(phrase in final.lower() for phrase in ai_oracle.ABSTENTION_PHRASES)
    assert all(marker not in final for marker in FORMER_CANNED_MARKERS)


@pytest.mark.asyncio
async def test_low_chapter_cap_does_not_leak_future_answer():
    final, _, _, _ = await ai_oracle.verify_and_repair_answer(
        question="Chương 830 Chu Vấn trộm trứng như thế nào?",
        effective_chapter_cap=10,
        wiki_context="",
        chapter_context="",
        rag_context="",
        active_patches=[],
        intent="event_sequence",
        evidence_contract=_empty_contract(chapter_cap=10),
        draft_answer="Dữ liệu hiện có chưa đủ để kết luận.",
    )
    assert "Chu Vấn" not in final
    assert "trứng rắn" not in final
    assert any(phrase in final.lower() for phrase in ai_oracle.ABSTENTION_PHRASES)


@pytest.mark.asyncio
async def test_provider_unavailable_empty_retrieval_abstains_non_abstain_prohibited():
    with patch("backend.routes.ai_oracle.is_grounded_verifier_enabled", return_value=False):
        final, _, _, _ = await ai_oracle.verify_and_repair_answer(
            question="Nhân vật Z làm gì trong lâu đài?",
            effective_chapter_cap=3,
            wiki_context="",
            chapter_context="",
            rag_context="",
            active_patches=[],
            intent="general_lore",
            evidence_contract=_empty_contract(chapter_cap=3),
            draft_answer="Dữ liệu hiện có chưa đủ để kết luận.",
        )
    assert any(phrase in final.lower() for phrase in ai_oracle.ABSTENTION_PHRASES)
    assert all(marker not in final for marker in FORMER_CANNED_MARKERS)


def test_no_production_function_named_construct_fallback_grounded_answer():
    assert not hasattr(ai_oracle, "construct_" + "fallback_grounded_answer")
    assert "construct_" + "fallback_grounded_answer" not in PRODUCTION_ORACLE.read_text(encoding="utf-8")


def test_no_benchmark_guard_comment_or_case_ids_in_production():
    content = PRODUCTION_ORACLE.read_text(encoding="utf-8")
    for marker in FORBIDDEN_STATIC_MARKERS:
        assert marker not in content


def test_no_long_story_answer_literals_in_production_source():
    content = PRODUCTION_ORACLE.read_text(encoding="utf-8")
    offline_start = content.index("OFFLINE_CHAPTER_DATA = {")
    offline_end = content.index("DEFAULT_MODEL_CATALOG", offline_start)
    production_without_offline_fixture = content[:offline_start] + content[offline_end:]
    for marker in FORMER_CANNED_MARKERS:
        assert marker not in production_without_offline_fixture


def test_curated_wiki_override_signature_has_no_case_id_or_question_input():
    sig = inspect.signature(ai_oracle.get_curated_wiki_override)
    assert list(sig.parameters) == ["name", "chapter_cap"]


def test_curated_wiki_override_does_not_match_exact_benchmark_question():
    exact_question = "Chương 830 Chu Vấn trộm ba quả trứng như thế nào?"
    assert ai_oracle.get_curated_wiki_override(exact_question, 830) is None


def test_curated_wiki_override_does_not_return_long_event_chain_answer(monkeypatch):
    monkeypatch.delitem(sys.modules, "pytest", raising=False)
    monkeypatch.delitem(sys.modules, "unittest", raising=False)
    item = ai_oracle.get_curated_wiki_override("Chu Vấn", 830)
    assert item is not None
    desc = item["desc"]
    assert len(desc) < 180
    assert "ném vỡ" not in desc
    assert "quả thứ hai" not in desc
    assert "ôm quả cuối" not in desc


def test_curated_wiki_override_respects_chapter_cap(monkeypatch):
    monkeypatch.delitem(sys.modules, "pytest", raising=False)
    monkeypatch.delitem(sys.modules, "unittest", raising=False)
    assert ai_oracle.get_curated_wiki_override("Chu Vấn", 829) is None
    assert ai_oracle.get_curated_wiki_override("Chu Vấn", 830) is not None


def test_curated_wiki_near_neighbor_and_unknown_entity_no_canned_answer(monkeypatch):
    monkeypatch.delitem(sys.modules, "pytest", raising=False)
    monkeypatch.delitem(sys.modules, "unittest", raising=False)
    assert ai_oracle.get_curated_wiki_override("Chu Vấn mặc áo màu gì", 830) is None
    assert ai_oracle.get_curated_wiki_override("Nhân vật Z", 830) is None


@pytest.mark.asyncio
async def test_curated_snippet_not_used_when_chapter_evidence_required_and_absent():
    # Curated snippets are metadata, but the verifier/repair safety path must not create an event answer
    # when chapter evidence is empty.
    final, _, _, _ = await ai_oracle.verify_and_repair_answer(
        question="Chu Vấn trộm ba quả trứng như thế nào?",
        effective_chapter_cap=830,
        wiki_context="[CANON WIKI] Chu Vấn: dị năng giả chương 830.",
        chapter_context="",
        rag_context="",
        active_patches=[],
        intent="event_sequence",
        evidence_contract=_empty_contract(chapter_cap=830),
        draft_answer="Dữ liệu hiện có chưa đủ để kết luận.",
    )
    assert any(phrase in final.lower() for phrase in ai_oracle.ABSTENTION_PHRASES)
    assert "ném vỡ" not in final
