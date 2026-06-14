#!/usr/bin/env python3
"""Phase 11F-3D immutable clean answer collector.

This process prepares public Oracle requests and seals raw answers. It never
loads gold facts, never scores, and never imports legacy evaluators.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ORACLE_PATH = ROOT / "backend/routes/ai_oracle.py"
DEFAULT_CONTRACT_PATH = ROOT / "backend/evals/phase11f3d_evaluator_contract.json"
FORBIDDEN_COLLECTION_PATHS = {
    "backend/evals/chapter_bot_quality_cases_v2_pro_reviewed.json",
    "backend/evals/phase11f3b_targeted_repair_cases_pro_reviewed.json",
    "backend/scripts/evaluate_phase11f3c_stage1.py",
    "backend/scripts/evaluate_phase11f3c_stage2.py",
    "backend/scratch/phase11f3c_contaminated_worktree.patch",
}
GOLD_FIELD_NAMES = {
    "required_facts",
    "optional_facts",
    "soft_scoring_facts",
    "human_reference_answer",
    "gold_evidence_refs",
    "root_cause",
    "desired_repair_layer",
    "acceptance_requirement",
    "expected_chapters",
    "benchmark_score",
}
INVALID_MUTATION = "INVALID_SOURCE_OR_EVALUATOR_MUTATED_DURING_RUN"


@dataclass(frozen=True)
class RuntimeConfig:
    provider: str
    model: str
    temperature: float
    timeout_seconds: int


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_not_forbidden_path(path: Path) -> None:
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(ROOT).as_posix()
    except ValueError:
        # Pytest temp manifests are allowed for dry-run integrity tests.
        return
    if rel in FORBIDDEN_COLLECTION_PATHS or "/runs/phase11f3c_stage" in rel:
        raise ValueError(f"collector prohibited from reading legacy/gold path: {rel}")


def validate_contract(contract: dict[str, Any]) -> None:
    required = {
        "collection_and_scoring_separated": True,
        "gold_loaded_after_collection_sealed": True,
        "case_id_passed_to_oracle": False,
        "cache_bypass": True,
        "silent_provider_fallback": False,
        "override_hits_allowed": 0,
        "benchmark_fields_reachable_allowed": False,
        "source_mutation_invalidates_run": True,
        "collector_mutation_invalidates_run": True,
        "query_manifest_mutation_invalidates_run": True,
        "raw_answers_mutable_after_seal": False,
        "legacy_evaluators_prohibited": True,
        "contaminated_artifacts_prohibited": True,
    }
    for key, expected in required.items():
        if contract.get(key) != expected:
            raise ValueError(f"invalid evaluator contract field {key}")


def load_query_manifest(path: Path) -> list[dict[str, Any]]:
    assert_not_forbidden_path(path)
    cases = load_json(path)
    if not isinstance(cases, list) or not cases:
        raise ValueError("query manifest must be a non-empty list")
    if len(cases) > 12:
        raise ValueError("query manifest may contain at most 12 cases")
    seen: set[str] = set()
    clean: list[dict[str, Any]] = []
    for case in cases:
        if set(case) != {"case_id", "question", "chapter_progress"}:
            raise ValueError("query manifest contains non-sanitized fields")
        if any(field in case for field in GOLD_FIELD_NAMES):
            raise ValueError("gold/benchmark field reached collector")
        if case["case_id"] in seen:
            raise ValueError(f"duplicate case_id: {case['case_id']}")
        seen.add(case["case_id"])
        if case["chapter_progress"] != 0:
            raise ValueError("phase11f3d collector requires public chapter_progress 0")
        clean.append(case)
    return clean


def build_oracle_request(case: dict[str, Any]) -> dict[str, Any]:
    request = {
        "question": case["question"],
        "chapter_progress": 0,
        "debug_bypass_cache": True,
    }
    if "case_id" in request:
        raise AssertionError("case_id must never be passed to Oracle")
    return request


def default_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        provider=os.getenv("PHASE11F3D_PROVIDER", "UNSET_PINNED_PROVIDER"),
        model=os.getenv("PHASE11F3D_MODEL", "UNSET_PINNED_MODEL"),
        temperature=float(os.getenv("PHASE11F3D_TEMPERATURE", "0")),
        timeout_seconds=int(os.getenv("PHASE11F3D_TIMEOUT_SECONDS", "60")),
    )


def relevant_provider_config(config: RuntimeConfig) -> dict[str, Any]:
    return {
        "provider": config.provider,
        "model": config.model,
        "temperature": config.temperature,
        "timeout_seconds": config.timeout_seconds,
        "secrets_exposed": False,
        "silent_provider_fallback": False,
    }


def validate_case_result(result: dict[str, Any]) -> None:
    if result.get("benchmark_field_reachable") is True:
        raise ValueError("benchmark fields became reachable during collection")
    if int(result.get("override_hit_count", 0)) != 0:
        raise ValueError("override hit count must remain zero")
    if not result.get("abstained") and not result.get("citations") and not result.get("bounded_curated_entity_metadata"):
        raise ValueError("non-abstain answer without source evidence")


def validate_sealed_artifact(artifact: dict[str, Any], expected_cases: list[dict[str, Any]]) -> None:
    expected_ids = [case["case_id"] for case in expected_cases]
    got_ids = [case["case_id"] for case in artifact.get("cases", [])]
    if len(got_ids) != len(expected_ids):
        raise ValueError("missing cases in raw answer artifact")
    if len(set(got_ids)) != len(got_ids):
        raise ValueError("duplicate case IDs in raw answer artifact")
    if got_ids != expected_ids:
        raise ValueError("raw answer artifact case order/selection mismatch")
    for case in artifact["cases"]:
        validate_case_result(case)


def collect_answers(
    manifest_path: Path,
    output_path: Path,
    oracle_call: Callable[[dict[str, Any], RuntimeConfig], dict[str, Any]],
    contract_path: Path = DEFAULT_CONTRACT_PATH,
    runtime_config: RuntimeConfig | None = None,
) -> dict[str, Any]:
    contract = load_json(contract_path)
    validate_contract(contract)
    cases = load_query_manifest(manifest_path)
    runtime_config = runtime_config or default_runtime_config()

    initial = {
        "production_source_sha256": sha256_path(PRODUCTION_ORACLE_PATH),
        "collector_sha256": sha256_path(Path(__file__).resolve()),
        "query_manifest_sha256": sha256_path(manifest_path),
        "contract_sha256": sha256_path(contract_path),
    }
    results: list[dict[str, Any]] = []
    start = utc_now()
    for index, case in enumerate(cases, start=1):
        for key, value in initial.items():
            if key == "contract_sha256":
                continue
            current = {
                "production_source_sha256": sha256_path(PRODUCTION_ORACLE_PATH),
                "collector_sha256": sha256_path(Path(__file__).resolve()),
                "query_manifest_sha256": sha256_path(manifest_path),
            }[key]
            if current != value:
                raise RuntimeError(INVALID_MUTATION)
        request = build_oracle_request(case)
        case_start = utc_now()
        error_status = None
        try:
            raw = oracle_call(request, runtime_config)
        except Exception as exc:  # pragma: no cover - exercised by real CLI failures
            raw = {}
            error_status = f"{type(exc).__name__}: {exc}"
        case_end = utc_now()
        record = {
            "case_id": case["case_id"],
            "question": case["question"],
            "chapter_progress": 0,
            "raw_answer": raw.get("answer", ""),
            "abstained": bool(raw.get("abstained", False)),
            "abstain_reason": raw.get("abstain_reason"),
            "citations": raw.get("citations", []),
            "selected_chunk_ids": raw.get("selected_chunk_ids", []),
            "selected_chapter_numbers": raw.get("selected_chapter_numbers", []),
            "retrieval_trace": raw.get("retrieval_trace", {}),
            "evidence_trace": raw.get("evidence_trace", {}),
            "provider": runtime_config.provider,
            "model": runtime_config.model,
            "temperature": runtime_config.temperature,
            "timeout": runtime_config.timeout_seconds,
            "cache_bypass_status": request["debug_bypass_cache"],
            "draft_call_count": int(raw.get("draft_call_count", 0)),
            "verifier_call_count": int(raw.get("verifier_call_count", 0)),
            "repair_call_count": int(raw.get("repair_call_count", 0)),
            "override_hit_count": int(raw.get("override_hit_count", 0)),
            "benchmark_field_reachable": bool(raw.get("benchmark_field_reachable", False)),
            "bounded_curated_entity_metadata": bool(raw.get("bounded_curated_entity_metadata", False)),
            "start_timestamp": case_start,
            "end_timestamp": case_end,
            "per_case_error_status": error_status,
            "execution_index": index,
        }
        validate_case_result(record)
        results.append(record)

    final = {
        "production_source_sha256": sha256_path(PRODUCTION_ORACLE_PATH),
        "collector_sha256": sha256_path(Path(__file__).resolve()),
        "query_manifest_sha256": sha256_path(manifest_path),
    }
    for key, value in final.items():
        if value != initial[key]:
            raise RuntimeError(INVALID_MUTATION)

    artifact = {
        "artifact_type": "PHASE11F3D_RAW_ANSWERS",
        "sealed": False,
        "start_timestamp": start,
        "end_timestamp": utc_now(),
        "case_count": len(cases),
        "execution_count": len(results),
        "provider_model_configuration": relevant_provider_config(runtime_config),
        "checksums": initial | {"scorer_sha256": None},
        "cases": results,
        "process_exit_code": 0,
    }
    validate_sealed_artifact(artifact, cases)
    artifact["raw_answer_artifact_sha256"] = sha256_json({k: v for k, v in artifact.items() if k != "raw_answer_artifact_sha256"})
    artifact["sealed"] = True
    output_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return artifact


def unavailable_oracle_call(_request: dict[str, Any], _runtime_config: RuntimeConfig) -> dict[str, Any]:
    raise RuntimeError("live collection is intentionally not implemented in this phase")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--contract", default=DEFAULT_CONTRACT_PATH, type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs without calling Oracle")
    args = parser.parse_args(argv)
    if args.dry_run:
        validate_contract(load_json(args.contract))
        load_query_manifest(args.manifest)
        print("dry-run-ok")
        return 0
    collect_answers(args.manifest, args.output, unavailable_oracle_call, args.contract)
    return 0


if __name__ == "__main__":
    sys.exit(main())
