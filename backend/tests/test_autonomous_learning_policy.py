import subprocess
from pathlib import Path

from backend.rag.autonomous_feedback_processor import FeedbackEvent, FeedbackSignal, process_feedback_event
from backend.rag.autonomous_learning import (
    PROHIBITED_ADMIN_STATES,
    EvidenceItem,
    TrustState,
    assert_no_admin_approval_state,
    create_self_evaluation_event,
    validate_evidence,
    transition_trust_state,
    run_shadow_validation,
    run_canary_validation,
    admin_disable_record,
    admin_restore_record,
    eligible_for_retrieval,
)
from backend.rag.autonomous_learning_store import InMemoryAutonomousLearningStore

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "golden-oracle-regression.yml"

def canonical_evidence(n=1):
    return [EvidenceItem(citation=f"story:{i}", chapter_number=1, chunk_id=f"c{i}", canonical=True, independent_source_id=f"s{i}") for i in range(n)]

def make_record(evidence=None):
    evidence = evidence or canonical_evidence(1)
    return create_self_evaluation_event(originating_question="q", original_answer="a", corrected_proposed_fact="fact", evidence=evidence)

def promote_to_probationary(record, evidence):
    validation = validate_evidence(record, evidence, 10)
    return transition_trust_state(record, validation), validation

def test_no_mandatory_admin_approval_state_exists():
    assert_no_admin_approval_state()
    assert not ({s for s in PROHIBITED_ADMIN_STATES} & {s.value for s in TrustState})

def test_system_promotes_candidate_automatically_after_policy_passes():
    evidence = canonical_evidence(2)
    rec = make_record(evidence)
    rec, validation = promote_to_probationary(rec, evidence)
    assert rec.current_trust_state == TrustState.PROBATIONARY
    shadow = run_shadow_validation(rec)
    transition_trust_state(rec, validation, shadow=shadow, targeted_regression_passed=True)
    assert rec.current_trust_state == TrustState.TRUSTED

def test_unsupported_user_feedback_does_not_promote():
    event = FeedbackEvent(event_id="f1", signal=FeedbackSignal.CORRECTION_TEXT, original_question="q", original_answer="a", correction_text="unsupported")
    rec = process_feedback_event(event, chapter_cap=10)
    assert rec.current_trust_state == TrustState.OBSERVED

def test_self_evaluation_creates_learning_event():
    rec = make_record()
    assert rec.source_type.value == "SELF_EVALUATION"
    assert rec.audit_trail

def test_explicit_feedback_creates_learning_event():
    event = FeedbackEvent(event_id="f2", signal=FeedbackSignal.THUMBS_DOWN, original_question="q", original_answer="a", correction_text="fact", evidence=canonical_evidence())
    rec = process_feedback_event(event, chapter_cap=10)
    assert rec.source_type.value == "USER_FEEDBACK_EXPLICIT"

def test_implicit_correction_creates_learning_event():
    event = FeedbackEvent(event_id="f3", signal=FeedbackSignal.NEXT_MESSAGE_CORRECTION, original_question="q", original_answer="a", correction_text="fact", evidence=canonical_evidence())
    rec = process_feedback_event(event, chapter_cap=10)
    assert rec.source_type.value == "USER_FEEDBACK_IMPLICIT"

def test_canonical_source_evidence_raises_trust():
    evidence = canonical_evidence()
    rec = make_record(evidence)
    validation = validate_evidence(rec, evidence, 10)
    assert validation.canonical_confirmation
    assert rec.trust_score > 0

def test_contradiction_lowers_trust():
    evidence = [EvidenceItem(citation="canon", chapter_number=1, canonical=True, conflicts=True)]
    rec = make_record(evidence)
    rec.current_trust_state = TrustState.TRUSTED
    validation = validate_evidence(rec, evidence, 10)
    transition_trust_state(rec, validation)
    assert rec.current_trust_state == TrustState.DEMOTED

def test_future_leakage_quarantines_automatically():
    evidence = [EvidenceItem(citation="future", chapter_number=99, canonical=True)]
    rec = make_record(evidence)
    validation = validate_evidence(rec, evidence, 10)
    transition_trust_state(rec, validation)
    assert rec.current_trust_state == TrustState.QUARANTINED

def test_shadow_failure_prevents_promotion():
    evidence = canonical_evidence(2)
    rec = make_record(evidence)
    rec, validation = promote_to_probationary(rec, evidence)
    shadow = run_shadow_validation(rec, source_support=0.1)
    transition_trust_state(rec, validation, shadow=shadow, targeted_regression_passed=True)
    assert rec.current_trust_state == TrustState.PROBATIONARY

def test_canary_regression_triggers_rollback():
    evidence = canonical_evidence(2)
    rec = make_record(evidence)
    rec.version = 2
    rec.previous_version = 1
    rec.current_trust_state = TrustState.PROBATIONARY
    run_canary_validation(rec, unsupported_claims_increased=True, reason="unsupported_claims_increased")
    assert rec.current_trust_state == TrustState.DEMOTED
    assert rec.rollback_target == 1

def test_previous_version_is_restored_automatically():
    evidence = canonical_evidence(2)
    rec = make_record(evidence)
    rec.version = 3
    rec.previous_version = 2
    run_canary_validation(rec, answer_quality_declined=True, reason="answer_quality_declined")
    assert rec.rollback_target == 2

def test_audit_history_is_preserved():
    rec = make_record()
    run_shadow_validation(rec)
    run_canary_validation(rec, contradiction=True, reason="contradiction")
    assert len(rec.audit_trail) >= 3

def test_trusted_records_enter_retrieval_automatically():
    rec = make_record(canonical_evidence(2))
    rec.current_trust_state = TrustState.TRUSTED
    assert eligible_for_retrieval(rec)

def test_quarantined_records_cannot_enter_retrieval():
    rec = make_record()
    rec.current_trust_state = TrustState.QUARANTINED
    assert not eligible_for_retrieval(rec)

def test_no_wiki_entries_writes():
    store = InMemoryAutonomousLearningStore()
    rec = make_record()
    store.save_record(rec)
    assert not store.wrote_to_wiki_entries()

def test_no_source_code_answer_generation():
    assert "hardcoded answer" not in (ROOT / "backend" / "rag" / "autonomous_learning.py").read_text(encoding="utf-8").lower()

def test_no_benchmark_gold_access():
    text = (ROOT / "backend" / "scripts" / "run_autonomous_learning_loop.py").read_text(encoding="utf-8")
    assert "golden_oracle_regression_cases" not in text
    assert "benchmark" not in text.lower()

def test_admin_inactivity_does_not_block_learning():
    evidence = canonical_evidence(2)
    rec = make_record(evidence)
    rec, validation = promote_to_probationary(rec, evidence)
    transition_trust_state(rec, validation, shadow=run_shadow_validation(rec), targeted_regression_passed=True)
    assert rec.current_trust_state == TrustState.TRUSTED

def test_admin_can_disable_restore_without_being_required():
    rec = make_record()
    admin_disable_record(rec)
    assert rec.current_trust_state == TrustState.QUARANTINED
    admin_restore_record(rec)
    assert rec.current_trust_state == TrustState.PROBATIONARY

def test_scheduled_workflow_asks_maximum_two_questions():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "schedule:" in text
    assert "--max-questions" in text
    assert "MAX_QUESTIONS" in text
    assert "-gt 2" in text

def test_user_feedback_and_self_evaluation_use_same_trust_engine():
    assert process_feedback_event.__globals__["validate_evidence"] is validate_evidence
    assert process_feedback_event.__globals__["transition_trust_state"] is transition_trust_state

def test_no_live_requests_occur_during_unit_tests():
    result = subprocess.run([
        "python", "backend/scripts/run_autonomous_learning_loop.py", "--dry-run-no-live-requests", "--report-path", "backend/rag/generated_test_autonomous_learning_loop_report.json"
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    assert '"live_requests": 0' in result.stdout

def test_no_automatic_push_or_deploy_occurs():
    text = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "git push" not in text
    assert "deploy" not in text
