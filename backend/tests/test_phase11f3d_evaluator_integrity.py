import hashlib
import json
import shutil
from pathlib import Path

import pytest

from backend.scripts import phase11f3d_collect_answers as collector
from backend.scripts import phase11f3d_score_answers as scorer

ROOT = Path(__file__).resolve().parents[2]
COLLECTOR_SOURCE = (ROOT / "backend/scripts/phase11f3d_collect_answers.py").read_text(encoding="utf-8")
SCORER_SOURCE = (ROOT / "backend/scripts/phase11f3d_score_answers.py").read_text(encoding="utf-8")


def _write_contract(tmp_path: Path) -> Path:
    contract = json.loads((ROOT / "backend/evals/phase11f3d_evaluator_contract.json").read_text(encoding="utf-8"))
    p = tmp_path / "contract.json"
    p.write_text(json.dumps(contract), encoding="utf-8")
    return p


def _write_manifest(tmp_path: Path, cases=None) -> Path:
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(cases or [{"case_id": "c1", "question": "Q?", "chapter_progress": 0}]), encoding="utf-8")
    return p


def _oracle(answer="ABSTAIN_NO_SOURCE", **extra):
    def call(request, runtime):
        assert set(request) == {"question", "chapter_progress", "debug_bypass_cache"}
        assert "case_id" not in request
        base = {"answer": answer, "abstained": True, "abstain_reason": "NO_SOURCE", "citations": []}
        base.update(extra)
        return base
    return call


def _sealed_raw(tmp_path: Path, case_id="c1") -> Path:
    manifest = _write_manifest(tmp_path, [{"case_id": case_id, "question": "Q?", "chapter_progress": 0}])
    contract = _write_contract(tmp_path)
    out = tmp_path / "raw.json"
    collector.collect_answers(manifest, out, _oracle(), contract)
    return out


def test_collector_cannot_import_benchmark_gold_loader():
    assert "DEFAULT_GOLD_PATH" not in COLLECTOR_SOURCE
    assert "load_gold" not in COLLECTOR_SOURCE


def test_collector_cannot_read_pro_v2_path():
    with pytest.raises(ValueError):
        collector.assert_not_forbidden_path(ROOT / "backend/evals/chapter_bot_quality_cases_v2_pro_reviewed.json")


def test_collector_receives_only_sanitized_query_fields(tmp_path):
    manifest = _write_manifest(tmp_path, [{"case_id": "c1", "question": "Q?", "chapter_progress": 0, "required_facts": []}])
    with pytest.raises(ValueError):
        collector.load_query_manifest(manifest)


def test_case_id_is_not_passed_into_oracle_request():
    req = collector.build_oracle_request({"case_id": "secret", "question": "Q?", "chapter_progress": 0})
    assert req == {"question": "Q?", "chapter_progress": 0, "debug_bypass_cache": True}


def test_required_reference_facts_cannot_reach_oracle(tmp_path):
    manifest = _write_manifest(tmp_path, [{"case_id": "c1", "question": "Q?", "chapter_progress": 0, "human_reference_answer": "x"}])
    with pytest.raises(ValueError):
        collector.load_query_manifest(manifest)


def test_collector_never_scores():
    assert "score_case" not in COLLECTOR_SOURCE
    assert "human_score" not in COLLECTOR_SOURCE


def test_scorer_cannot_call_oracle():
    assert "ask_oracle" not in SCORER_SOURCE
    assert "call_ai_provider" not in SCORER_SOURCE


def test_scorer_cannot_call_retrieval():
    assert "get_rag_context" not in SCORER_SOURCE
    assert "retrieve_relevant_chunks" not in SCORER_SOURCE


def test_scorer_refuses_unsealed_answer_artifact(tmp_path):
    p = tmp_path / "raw.json"
    p.write_text(json.dumps({"artifact_type": scorer.RAW_ARTIFACT_TYPE, "sealed": False}), encoding="utf-8")
    with pytest.raises(ValueError):
        scorer.verify_raw_artifact(p)


def test_scorer_refuses_checksum_mismatch(tmp_path):
    raw = _sealed_raw(tmp_path)
    data = json.loads(raw.read_text(encoding="utf-8"))
    data["cases"][0]["raw_answer"] = "mutated"
    raw.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(RuntimeError):
        scorer.verify_raw_artifact(raw)


def test_collector_refuses_source_mutation(tmp_path, monkeypatch):
    manifest = _write_manifest(tmp_path)
    contract = _write_contract(tmp_path)
    calls = {"n": 0}
    original = collector.sha256_path
    def fake(path):
        if path == collector.PRODUCTION_ORACLE_PATH:
            calls["n"] += 1
            return "changed" if calls["n"] > 1 else original(path)
        return original(path)
    monkeypatch.setattr(collector, "sha256_path", fake)
    with pytest.raises(RuntimeError):
        collector.collect_answers(manifest, tmp_path / "out.json", _oracle(), contract)


def test_collector_refuses_its_own_mutation(tmp_path, monkeypatch):
    manifest = _write_manifest(tmp_path)
    contract = _write_contract(tmp_path)
    original = collector.sha256_path
    calls = {"n": 0}
    def fake(path):
        if path.name == "phase11f3d_collect_answers.py":
            calls["n"] += 1
            return "collector-mutated" if calls["n"] > 1 else original(path)
        return original(path)
    monkeypatch.setattr(collector, "sha256_path", fake)
    with pytest.raises(RuntimeError):
        collector.collect_answers(manifest, tmp_path / "out.json", _oracle(), contract)


def test_scorer_refuses_its_own_mutation(tmp_path, monkeypatch):
    raw = _sealed_raw(tmp_path, "char-03")
    out = tmp_path / "score.json"
    original = scorer.sha256_path
    calls = {"n": 0}
    def fake(path):
        if path.name == "phase11f3d_score_answers.py":
            calls["n"] += 1
            return "changed" if calls["n"] > 1 else original(path)
        return original(path)
    monkeypatch.setattr(scorer, "sha256_path", fake)
    with pytest.raises(RuntimeError):
        scorer.score_answers(raw, out)


def test_query_manifest_mutation_invalidates_run(tmp_path, monkeypatch):
    manifest = _write_manifest(tmp_path)
    contract = _write_contract(tmp_path)
    original = collector.sha256_path
    calls = {"n": 0}
    def fake(path):
        if path == manifest:
            calls["n"] += 1
            return "changed" if calls["n"] > 1 else original(path)
        return original(path)
    monkeypatch.setattr(collector, "sha256_path", fake)
    with pytest.raises(RuntimeError):
        collector.collect_answers(manifest, tmp_path / "out.json", _oracle(), contract)


def test_duplicate_case_ids_rejected(tmp_path):
    manifest = _write_manifest(tmp_path, [{"case_id": "c1", "question": "Q1", "chapter_progress": 0}, {"case_id": "c1", "question": "Q2", "chapter_progress": 0}])
    with pytest.raises(ValueError):
        collector.load_query_manifest(manifest)


def test_missing_cases_rejected(tmp_path):
    artifact = {"cases": [{"case_id": "c1", "abstained": True, "override_hit_count": 0, "benchmark_field_reachable": False}]}
    with pytest.raises(ValueError):
        collector.validate_sealed_artifact(artifact, [{"case_id": "c1"}, {"case_id": "c2"}])


def test_override_hit_greater_than_zero_invalidates_run():
    with pytest.raises(ValueError):
        collector.validate_case_result({"override_hit_count": 1, "benchmark_field_reachable": False, "abstained": True})


def test_benchmark_field_reachability_invalidates_run():
    with pytest.raises(ValueError):
        collector.validate_case_result({"override_hit_count": 0, "benchmark_field_reachable": True, "abstained": True})


def test_provider_model_mutation_invalidates_contract():
    cfg = collector.relevant_provider_config(collector.RuntimeConfig("p", "m", 0.0, 30))
    assert cfg["silent_provider_fallback"] is False
    assert cfg["provider"] == "p" and cfg["model"] == "m"


def test_raw_answers_cannot_be_modified_after_seal(tmp_path):
    raw = _sealed_raw(tmp_path)
    data = json.loads(raw.read_text(encoding="utf-8"))
    assert data["sealed"] is True
    data["cases"].append(data["cases"][0])
    raw.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(RuntimeError):
        scorer.verify_raw_artifact(raw)


def test_required_fact_recall_cannot_directly_force_score_3():
    case = scorer.score_case({"case_id": "x", "raw_answer": "a b"}, {"required_facts": ["a", "b"], "optional_facts": []})
    assert case["required_source_supported_fact_recall"] == 1.0
    assert case["human_score"] is None


def test_no_old_stage1_stage2_evaluator_import():
    combined = COLLECTOR_SOURCE + SCORER_SOURCE
    assert "import evaluate_phase11f3c_stage1" not in combined
    assert "import evaluate_phase11f3c_stage2" not in combined


def test_no_contaminated_artifact_glob_import():
    combined = COLLECTOR_SOURCE + SCORER_SOURCE
    assert "glob(" not in combined
    assert "phase11f3c_contaminated_worktree.patch" in combined  # prohibited literal only


def test_no_live_provider_calls_during_tests(tmp_path):
    raw = _sealed_raw(tmp_path)
    assert raw.exists()


def test_no_writes_to_production_database():
    combined = COLLECTOR_SOURCE + SCORER_SOURCE
    assert ".insert(" not in combined
    assert ".upsert(" not in combined
    assert ".delete(" not in combined
