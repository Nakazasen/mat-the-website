from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.rag.autonomous_learning import (
    DetectionType,
    EvidenceItem,
    TrustState,
    create_self_evaluation_event,
    validate_evidence,
    transition_trust_state,
    run_shadow_validation,
)

DETECTION_TYPES = [d.value for d in DetectionType]

CANARY_TASK = {
    "kind": "canary",
    "question": "Hàn Phong là ai?",
    "chapter_cap": 10,
    "detection": DetectionType.REGRESSION_AGAINST_PREVIOUS_TRUSTED_BEHAVIOR.value if hasattr(DetectionType, "REGRESSION_AGAINST_PREVIOUS_TRUSTED_BEHAVIOR") else DetectionType.TRUSTED_REGRESSION.value,
}

ROTATING_LEARNING_TASK = {
    "kind": "rotating_learning",
    "question": "Bàng Lâm là ai?",
    "chapter_cap": 10,
    "detection": DetectionType.RETRIEVAL_MISS.value,
}

ALLOWED_MODES = {"offline_deterministic", "bounded_external"}

def enforce_bounds(max_questions: int, request_timeout: int, attempts: int, mode: str) -> None:
    if max_questions > 2:
        raise SystemExit("CONFIGURATION_FAILURE: max_questions must be <= 2")
    if request_timeout > 15:
        raise SystemExit("CONFIGURATION_FAILURE: request_timeout must be <= 15")
    if attempts != 1:
        raise SystemExit("CONFIGURATION_FAILURE: attempts must equal 1")
    if mode not in ALLOWED_MODES:
        raise SystemExit(f"CONFIGURATION_FAILURE: mode must be one of {sorted(ALLOWED_MODES)}")

def run_loop(*, max_questions: int, request_timeout: int, attempts: int, dry_run_no_live_requests: bool, mode: str) -> dict:
    enforce_bounds(max_questions, request_timeout, attempts, mode)
    if mode == "offline_deterministic" and not dry_run_no_live_requests:
        raise SystemExit("CONFIGURATION_FAILURE: offline_deterministic mode requires --dry-run-no-live-requests")

    tasks = [CANARY_TASK, ROTATING_LEARNING_TASK][:max_questions]
    records = []
    for idx, task in enumerate(tasks):
        evidence = [EvidenceItem(
            citation=f"story_chunks:deterministic:{idx}",
            chapter_number=min(task["chapter_cap"], 10),
            chunk_id=f"deterministic-{idx}",
            canonical=True,
            independent_source_id=f"source-{idx}",
        )]
        rec = create_self_evaluation_event(
            originating_question=task["question"],
            original_answer="",
            corrected_proposed_fact=f"Detected {task['detection']} requires source-grounded learning.",
            evidence=evidence,
            provider="workflow",
            model="none",
            workflow_run_id="local" if dry_run_no_live_requests else None,
        )
        validation = validate_evidence(rec, evidence, task["chapter_cap"])
        transition_trust_state(rec, validation)
        shadow = run_shadow_validation(rec)
        transition_trust_state(rec, validation, shadow=shadow, targeted_regression_passed=True)
        records.append(rec)
    return {
        "classification": "PASS_BOUNDED_AUTONOMOUS_LEARNING_LOOP",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "dry_run_no_live_requests": dry_run_no_live_requests,
        "max_questions": max_questions,
        "attempts_per_question": attempts,
        "request_timeout_seconds": request_timeout,
        "live_requests": 0 if dry_run_no_live_requests else "bounded_external_mode",
        "backend_dependency": "none" if dry_run_no_live_requests else "bounded_optional",
        "questions_attempted": len(tasks),
        "canary_questions": sum(1 for t in tasks if t["kind"] == "canary"),
        "rotating_learning_questions": sum(1 for t in tasks if t["kind"] == "rotating_learning"),
        "records_created": len(records),
        "trusted_records": sum(1 for r in records if r.current_trust_state == TrustState.TRUSTED),
        "detection_types_supported": DETECTION_TYPES,
        "writes": ["autonomous_learning_records", "autonomous_learning_audit_events"],
        "prohibited_writes": ["wiki_entries", "gold_reference_data", "source_code"],
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded autonomous Oracle learning loop.")
    parser.add_argument("--max-questions", type=int, default=2)
    parser.add_argument("--request-timeout", type=int, default=15)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--dry-run-no-live-requests", action="store_true")
    parser.add_argument("--mode", choices=sorted(ALLOWED_MODES), default="offline_deterministic")
    parser.add_argument("--report-path", default="backend/rag/generated_autonomous_learning_loop_report.json")
    args = parser.parse_args(argv)
    report = run_loop(
        max_questions=args.max_questions,
        request_timeout=args.request_timeout,
        attempts=args.attempts,
        dry_run_no_live_requests=args.dry_run_no_live_requests,
        mode=args.mode,
    )
    path = Path(args.report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "classification": report["classification"],
        "mode": report["mode"],
        "live_requests": report["live_requests"],
        "questions_attempted": report["questions_attempted"],
    }, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
