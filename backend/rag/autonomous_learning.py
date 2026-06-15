from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable
import hashlib

PROHIBITED_ADMIN_STATES = {
    "PENDING_ADMIN_APPROVAL",
    "WAITING_FOR_ADMIN",
    "REQUIRES_MANUAL_APPLY",
    "ADMIN_MUST_CONFIRM",
    "PUBLIC_APPLY_TO_WIKI",
}

class SourceType(str, Enum):
    SELF_EVALUATION = "SELF_EVALUATION"
    USER_FEEDBACK_EXPLICIT = "USER_FEEDBACK_EXPLICIT"
    USER_FEEDBACK_IMPLICIT = "USER_FEEDBACK_IMPLICIT"

class TrustState(str, Enum):
    OBSERVED = "OBSERVED"
    PROBATIONARY = "PROBATIONARY"
    TRUSTED = "TRUSTED"
    DEMOTED = "DEMOTED"
    QUARANTINED = "QUARANTINED"
    RETIRED = "RETIRED"

class DetectionType(str, Enum):
    UNSUPPORTED_ANSWER = "unsupported_answer"
    MISSING_CORE_FACTS = "missing_core_facts"
    CONTRADICTION = "contradiction"
    WRONG_CHAPTER = "wrong_chapter"
    FUTURE_LEAKAGE = "future_leakage"
    RETRIEVAL_MISS = "retrieval_miss"
    FALSE_ABSTENTION = "false_abstention"
    ANSWER_INSTABILITY = "answer_instability"
    VERIFIER_DISAGREEMENT = "verifier_disagreement"
    TRUSTED_REGRESSION = "regression_against_previous_trusted_behavior"

@dataclass
class EvidenceItem:
    citation: str
    chapter_number: int | None = None
    chunk_id: str | None = None
    canonical: bool = False
    independent_source_id: str | None = None
    supports_entity: bool = True
    supports_action: bool = True
    supports_object: bool = True
    supports_number: bool = True
    supports_order: bool = True
    conflicts: bool = False
    from_benchmark_gold: bool = False
    model_generated_only: bool = False

@dataclass
class ValidationResult:
    provenance_exists: bool
    within_chapter_cap: bool
    future_leakage: bool
    benchmark_gold_copy: bool
    canonical_conflict: bool
    model_generated_only: bool
    fact_atoms_supported: bool
    duplicate_merged: bool = False
    conflict_count: int = 0
    support_score: float = 0.0
    confidence_score: float = 0.0
    independent_evidence_count: int = 0
    canonical_confirmation: bool = False

    @property
    def may_influence_retrieval(self) -> bool:
        return (
            self.provenance_exists
            and self.within_chapter_cap
            and not self.future_leakage
            and not self.benchmark_gold_copy
            and not self.canonical_conflict
            and not self.model_generated_only
            and self.fact_atoms_supported
        )

@dataclass
class ShadowResult:
    passed: bool
    source_support: float = 1.0
    completeness: float = 1.0
    contradiction: bool = False
    future_leakage: bool = False
    latency_ms: int = 0
    retrieval_quality: float = 1.0
    reason: str = "shadow_passed"

@dataclass
class CanaryResult:
    passed: bool
    unsupported_claims_increased: bool = False
    future_leakage: bool = False
    contradiction: bool = False
    user_rejection_count: int = 0
    canonical_disproof: bool = False
    retrieval_quality_declined: bool = False
    latency_or_memory_exceeded: bool = False
    answer_quality_declined: bool = False
    reason: str = "canary_passed"

@dataclass
class LearningRecord:
    record_id: str
    source_type: SourceType
    originating_question: str
    original_answer: str
    corrected_proposed_fact: str
    source_citations: list[str] = field(default_factory=list)
    chapter_numbers: list[int] = field(default_factory=list)
    source_chunk_ids: list[str] = field(default_factory=list)
    user_feedback_reference: str | None = None
    provider: str | None = None
    model: str | None = None
    creation_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_count: int = 0
    independent_evidence_count: int = 0
    contradiction_count: int = 0
    support_score: float = 0.0
    confidence_score: float = 0.0
    trust_score: float = 0.0
    current_trust_state: TrustState = TrustState.OBSERVED
    retrieval_weight: float = 0.0
    version: int = 1
    previous_version: int | None = None
    rollback_target: int | None = None
    promotion_reason: str | None = None
    demotion_reason: str | None = None
    last_validation_timestamp: str | None = None
    workflow_run_id: str | None = None
    user_feedback_event_id: str | None = None
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    disabled_by_admin: bool = False

    def audit(self, event: str, detail: str, **extra: Any) -> None:
        self.audit_trail.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "detail": detail,
            **extra,
        })

def _record_id(source_type: SourceType, question: str, fact: str) -> str:
    raw = f"{source_type}:{question}:{fact}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]

def create_learning_event(
    *,
    source_type: SourceType,
    originating_question: str,
    original_answer: str,
    corrected_proposed_fact: str,
    evidence: Iterable[EvidenceItem] = (),
    provider: str | None = None,
    model: str | None = None,
    workflow_run_id: str | None = None,
    user_feedback_event_id: str | None = None,
) -> LearningRecord:
    evidence_list = list(evidence)
    rec = LearningRecord(
        record_id=_record_id(source_type, originating_question, corrected_proposed_fact),
        source_type=source_type,
        originating_question=originating_question,
        original_answer=original_answer,
        corrected_proposed_fact=corrected_proposed_fact,
        source_citations=[e.citation for e in evidence_list],
        chapter_numbers=[e.chapter_number for e in evidence_list if e.chapter_number is not None],
        source_chunk_ids=[e.chunk_id for e in evidence_list if e.chunk_id],
        user_feedback_reference=user_feedback_event_id,
        provider=provider,
        model=model,
        workflow_run_id=workflow_run_id,
        user_feedback_event_id=user_feedback_event_id,
        evidence_count=len(evidence_list),
        independent_evidence_count=len({e.independent_source_id or e.citation for e in evidence_list}),
    )
    rec.audit("created", "autonomous learning event created")
    return rec

def create_self_evaluation_event(**kwargs: Any) -> LearningRecord:
    return create_learning_event(source_type=SourceType.SELF_EVALUATION, **kwargs)

def create_explicit_feedback_event(**kwargs: Any) -> LearningRecord:
    return create_learning_event(source_type=SourceType.USER_FEEDBACK_EXPLICIT, **kwargs)

def create_implicit_feedback_event(**kwargs: Any) -> LearningRecord:
    return create_learning_event(source_type=SourceType.USER_FEEDBACK_IMPLICIT, **kwargs)

def validate_evidence(record: LearningRecord, evidence: Iterable[EvidenceItem], chapter_cap: int) -> ValidationResult:
    items = list(evidence)
    provenance = bool(items) and all(i.citation for i in items)
    within_cap = all(i.chapter_number is None or i.chapter_number <= chapter_cap for i in items)
    future = not within_cap
    benchmark = any(i.from_benchmark_gold for i in items)
    conflict_count = sum(1 for i in items if i.conflicts)
    model_only = bool(items) and all(i.model_generated_only for i in items)
    atoms_supported = bool(items) and all(
        i.supports_entity and i.supports_action and i.supports_object and i.supports_number and i.supports_order
        for i in items
    )
    independent = len({i.independent_source_id or i.citation for i in items})
    support_score = 0.0
    if items:
        support_score = sum(
            1 for i in items
            if not i.conflicts and not i.model_generated_only and not i.from_benchmark_gold
        ) / len(items)
    canonical = any(i.canonical and not i.conflicts for i in items)
    confidence = min(1.0, support_score * 0.6 + min(independent, 2) * 0.2 + (0.2 if canonical else 0.0))
    result = ValidationResult(
        provenance_exists=provenance,
        within_chapter_cap=within_cap,
        future_leakage=future,
        benchmark_gold_copy=benchmark,
        canonical_conflict=conflict_count > 0 and any(i.canonical and i.conflicts for i in items),
        model_generated_only=model_only,
        fact_atoms_supported=atoms_supported,
        conflict_count=conflict_count,
        support_score=support_score,
        confidence_score=confidence,
        independent_evidence_count=independent,
        canonical_confirmation=canonical,
    )
    record.evidence_count = len(items)
    record.independent_evidence_count = independent
    record.contradiction_count = conflict_count
    record.support_score = support_score
    record.confidence_score = confidence
    record.trust_score = confidence
    record.last_validation_timestamp = datetime.now(timezone.utc).isoformat()
    record.audit("validated", "evidence validation completed", validation=result.__dict__)
    return result

def transition_trust_state(
    record: LearningRecord,
    validation: ValidationResult,
    *,
    shadow: ShadowResult | None = None,
    canary: CanaryResult | None = None,
    targeted_regression_passed: bool = False,
    supported_answer_regresses: bool = False,
    unsupported_claim_introduced: bool = False,
) -> LearningRecord:
    if record.disabled_by_admin:
        record.current_trust_state = TrustState.QUARANTINED
        record.retrieval_weight = 0.0
        record.demotion_reason = "admin_disabled"
        record.audit("admin_override", "record disabled by admin")
        return record
    if validation.future_leakage:
        record.current_trust_state = TrustState.QUARANTINED
        record.retrieval_weight = 0.0
        record.demotion_reason = "future_leakage"
        record.audit("quarantined", "future leakage detected")
        return record
    if validation.canonical_conflict or validation.conflict_count > 0:
        record.current_trust_state = TrustState.DEMOTED if record.current_trust_state == TrustState.TRUSTED else TrustState.QUARANTINED
        record.retrieval_weight = 0.0
        record.demotion_reason = "contradiction_detected"
        record.audit("demoted", "contradiction detected")
        return record
    if not validation.may_influence_retrieval or validation.support_score < 0.7:
        record.current_trust_state = TrustState.OBSERVED
        record.retrieval_weight = 0.0
        record.audit("observed", "insufficient support for promotion")
        return record
    if record.current_trust_state == TrustState.OBSERVED:
        record.current_trust_state = TrustState.PROBATIONARY
        record.retrieval_weight = 0.05
        record.promotion_reason = "sufficient_provenance_no_future_leakage"
        record.audit("promoted", "OBSERVED to PROBATIONARY")
        return record
    if record.current_trust_state == TrustState.PROBATIONARY:
        shadow_passed = shadow.passed if shadow is not None else False
        can_trust = (
            validation.independent_evidence_count >= 2
            or (
                validation.canonical_confirmation
                and shadow_passed
                and targeted_regression_passed
                and not supported_answer_regresses
                and not unsupported_claim_introduced
            )
        )
        if not shadow_passed:
            record.audit("shadow_blocked", "shadow validation failed or missing")
            return record
        if canary and not canary.passed:
            return rollback_record(record, canary.reason)
        if can_trust:
            record.current_trust_state = TrustState.TRUSTED
            record.retrieval_weight = 1.0
            record.promotion_reason = "automatic_policy_passed"
            record.audit("promoted", "PROBATIONARY to TRUSTED")
    return record

def run_shadow_validation(record: LearningRecord, *, source_support: float = 1.0, contradiction: bool = False, future_leakage: bool = False, retrieval_quality: float = 1.0, latency_ms: int = 0) -> ShadowResult:
    passed = source_support >= 0.7 and not contradiction and not future_leakage and retrieval_quality >= 0.7
    result = ShadowResult(passed=passed, source_support=source_support, contradiction=contradiction, future_leakage=future_leakage, retrieval_quality=retrieval_quality, latency_ms=latency_ms, reason="shadow_passed" if passed else "shadow_failed")
    record.audit("shadow_validation", result.reason, result=result.__dict__)
    return result

def run_canary_validation(record: LearningRecord, **kwargs: Any) -> CanaryResult:
    result = CanaryResult(passed=not any(bool(v) for k, v in kwargs.items() if k != "reason"), **kwargs)
    record.audit("canary_validation", result.reason, result=result.__dict__)
    if not result.passed:
        rollback_record(record, result.reason)
    return result

def rollback_record(record: LearningRecord, reason: str) -> LearningRecord:
    previous = record.previous_version or max(1, record.version - 1)
    record.rollback_target = previous
    record.current_trust_state = TrustState.DEMOTED
    record.retrieval_weight = 0.0
    record.demotion_reason = reason
    record.audit("rollback", "automatic rollback restored previous trusted version", rollback_target=previous, reason=reason)
    return record

def retire_record(record: LearningRecord, reason: str = "superseded") -> LearningRecord:
    record.current_trust_state = TrustState.RETIRED
    record.retrieval_weight = 0.0
    record.demotion_reason = reason
    record.audit("retired", reason)
    return record

def admin_disable_record(record: LearningRecord, reason: str = "admin emergency disable") -> LearningRecord:
    record.disabled_by_admin = True
    record.current_trust_state = TrustState.QUARANTINED
    record.retrieval_weight = 0.0
    record.audit("admin_disabled", reason)
    return record

def admin_restore_record(record: LearningRecord, target_state: TrustState = TrustState.PROBATIONARY) -> LearningRecord:
    record.disabled_by_admin = False
    record.current_trust_state = target_state
    record.retrieval_weight = 0.05 if target_state == TrustState.PROBATIONARY else (1.0 if target_state == TrustState.TRUSTED else 0.0)
    record.audit("admin_restored", "admin restored record without being required for normal operation")
    return record

def eligible_for_retrieval(record: LearningRecord, *, shadow: bool = False) -> bool:
    if record.disabled_by_admin:
        return False
    if record.current_trust_state == TrustState.TRUSTED:
        return True
    if shadow and record.current_trust_state == TrustState.PROBATIONARY:
        return True
    return False

def assert_no_admin_approval_state() -> None:
    state_values = {s.value for s in TrustState}
    overlap = state_values & PROHIBITED_ADMIN_STATES
    if overlap:
        raise AssertionError(f"Prohibited admin approval states exist: {sorted(overlap)}")
