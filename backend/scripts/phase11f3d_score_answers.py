#!/usr/bin/env python3
"""Phase 11F-3D immutable clean gold scorer.

This process scores already sealed raw answers. It never calls Oracle, retrieval,
or answer repair, and it never mutates raw answers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT_PATH = ROOT / "backend/evals/phase11f3d_evaluator_contract.json"
DEFAULT_GOLD_PATH = ROOT / "backend/evals/chapter_bot_quality_cases_v2_pro_reviewed.json"
DEFAULT_TARGETED_PATH = ROOT / "backend/evals/phase11f3b_targeted_repair_cases_pro_reviewed.json"
INVALID_MUTATION = "INVALID_SOURCE_OR_EVALUATOR_MUTATED_DURING_RUN"
RAW_ARTIFACT_TYPE = "PHASE11F3D_RAW_ANSWERS"

SCORING_METRICS = [
    "official_judge_score",
    "required_source_supported_fact_recall",
    "optional_fact_recall",
    "abstention_correctness",
    "unsupported_claim_count",
    "contradiction_count",
    "wrong_chapter_count",
    "future_leakage_count",
    "retrieval_coverage",
    "verifier_false_accept_indicators",
    "repair_improvement_regression",
    "provider_model_call_accounting",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_raw_artifact(path: Path) -> dict[str, Any]:
    artifact = load_json(path)
    if artifact.get("artifact_type") != RAW_ARTIFACT_TYPE or artifact.get("sealed") is not True:
        raise ValueError("raw answer artifact is not sealed")
    original = artifact.get("raw_answer_artifact_sha256")
    if not original:
        raise ValueError("sealed raw answer artifact missing checksum")
    clone = dict(artifact)
    clone.pop("raw_answer_artifact_sha256", None)
    clone["sealed"] = False
    data = json.dumps(clone, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(data).hexdigest() != original:
        raise RuntimeError(INVALID_MUTATION)
    return artifact


def verify_contract(contract: dict[str, Any]) -> None:
    if contract.get("collection_and_scoring_separated") is not True:
        raise ValueError("collection/scoring separation disabled")
    if contract.get("gold_loaded_after_collection_sealed") is not True:
        raise ValueError("gold must load only after sealed collection")
    if contract.get("raw_answers_mutable_after_seal") is not False:
        raise ValueError("raw answers must be immutable after seal")
    if contract.get("scorer_mutation_invalidates_run") is not True:
        raise ValueError("scorer mutation must invalidate run")


def load_gold_after_seal(raw_artifact: dict[str, Any], gold_path: Path, targeted_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if raw_artifact.get("sealed") is not True:
        raise ValueError("cannot load gold before raw answers are sealed")
    return load_json(gold_path), load_json(targeted_path)


def required_fact_recall(answer: str, required_facts: list[str]) -> float:
    if not required_facts:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for fact in required_facts if str(fact).lower() in answer_lower)
    return hits / len(required_facts)


def score_case(raw_case: dict[str, Any], gold_case: dict[str, Any]) -> dict[str, Any]:
    answer = raw_case.get("raw_answer", "") or ""
    req_recall = required_fact_recall(answer, gold_case.get("required_facts", []))
    opt_recall = required_fact_recall(answer, gold_case.get("optional_facts", []))
    # Recall is preserved as recall only; it never forces a human score.
    return {
        "case_id": raw_case["case_id"],
        "official_judge_score": None,
        "raw_judge_response": None,
        "parsed_judge_result": None,
        "judge_parse_errors": [],
        "required_source_supported_fact_recall": req_recall,
        "optional_fact_recall": opt_recall,
        "abstention_correctness": None,
        "unsupported_claim_count": None,
        "contradiction_count": None,
        "wrong_chapter_count": None,
        "future_leakage_count": None,
        "retrieval_coverage": {
            "citations": raw_case.get("citations", []),
            "selected_chunk_ids": raw_case.get("selected_chunk_ids", []),
            "selected_chapter_numbers": raw_case.get("selected_chapter_numbers", []),
        },
        "verifier_false_accept_indicators": [],
        "repair_improvement_regression": None,
        "provider_model_call_accounting": {
            "provider": raw_case.get("provider"),
            "model": raw_case.get("model"),
            "draft_call_count": raw_case.get("draft_call_count", 0),
            "verifier_call_count": raw_case.get("verifier_call_count", 0),
            "repair_call_count": raw_case.get("repair_call_count", 0),
        },
        "human_score": None,
    }


def score_answers(
    raw_path: Path,
    output_path: Path,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
    gold_path: Path = DEFAULT_GOLD_PATH,
    targeted_path: Path = DEFAULT_TARGETED_PATH,
) -> dict[str, Any]:
    initial = {
        "scorer_sha256": sha256_path(Path(__file__).resolve()),
        "raw_answer_artifact_sha256": sha256_path(raw_path),
        "contract_sha256": sha256_path(contract_path),
        "gold_sha256": sha256_path(gold_path),
        "targeted_source_sha256": sha256_path(targeted_path),
    }
    contract = load_json(contract_path)
    verify_contract(contract)
    raw = verify_raw_artifact(raw_path)
    gold, targeted = load_gold_after_seal(raw, gold_path, targeted_path)
    targeted_ids = [case["case_id"] for case in targeted]
    gold_by_id = {case["case_id"]: case for case in gold}
    raw_ids = [case["case_id"] for case in raw.get("cases", [])]
    if raw_ids != targeted_ids[: len(raw_ids)]:
        raise ValueError("raw answer case selection does not match targeted source order")
    scored = [score_case(case, gold_by_id[case["case_id"]]) for case in raw["cases"]]
    final = {
        "scorer_sha256": sha256_path(Path(__file__).resolve()),
        "raw_answer_artifact_sha256": sha256_path(raw_path),
        "contract_sha256": sha256_path(contract_path),
        "gold_sha256": sha256_path(gold_path),
        "targeted_source_sha256": sha256_path(targeted_path),
    }
    if final != initial:
        raise RuntimeError(INVALID_MUTATION)
    report = {
        "artifact_type": "PHASE11F3D_SCORE_REPORT",
        "created_at": utc_now(),
        "checksums": initial,
        "metrics_preserved_separately": SCORING_METRICS,
        "case_count": len(scored),
        "cases": scored,
    }
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--contract", default=DEFAULT_CONTRACT_PATH, type=Path)
    parser.add_argument("--gold", default=DEFAULT_GOLD_PATH, type=Path)
    parser.add_argument("--targeted", default=DEFAULT_TARGETED_PATH, type=Path)
    args = parser.parse_args(argv)
    score_answers(args.raw, args.output, args.contract, args.gold, args.targeted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
