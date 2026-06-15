from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.rag.autonomous_learning import (
    EvidenceItem,
    LearningRecord,
    SourceType,
    create_explicit_feedback_event,
    create_implicit_feedback_event,
    validate_evidence,
    transition_trust_state,
    run_shadow_validation,
)

class FeedbackSignal(str, Enum):
    THUMBS_DOWN = "thumbs_down"
    CORRECTION_TEXT = "correction_text"
    USER_SOURCE = "user_provided_source"
    WRONG_ANSWER_REPORT = "answer_is_wrong"
    CORRECTED_FACT = "corrected_entity_fact_relation"
    REVISE_REQUEST = "request_to_revise_answer"
    IMMEDIATE_REPHRASE = "immediate_rephrasing"
    NEXT_MESSAGE_CORRECTION = "next_message_correction"
    REPEATED_DISSATISFACTION = "repeated_dissatisfaction"
    EVIDENCE_REQUEST_AFTER_ABANDON = "evidence_request_after_abandon"
    REPEATED_FAILURE_PATTERN = "repeated_failure_pattern"
    STRONG_DISAGREEMENT = "strong_disagreement"

@dataclass
class FeedbackEvent:
    event_id: str
    signal: FeedbackSignal
    original_question: str
    original_answer: str
    correction_text: str = ""
    user_source: str | None = None
    evidence: list[EvidenceItem] | None = None

    @property
    def source_type(self) -> SourceType:
        if self.signal in {
            FeedbackSignal.IMMEDIATE_REPHRASE,
            FeedbackSignal.NEXT_MESSAGE_CORRECTION,
            FeedbackSignal.REPEATED_DISSATISFACTION,
            FeedbackSignal.EVIDENCE_REQUEST_AFTER_ABANDON,
            FeedbackSignal.REPEATED_FAILURE_PATTERN,
            FeedbackSignal.STRONG_DISAGREEMENT,
        }:
            return SourceType.USER_FEEDBACK_IMPLICIT
        return SourceType.USER_FEEDBACK_EXPLICIT

def process_feedback_event(event: FeedbackEvent, *, chapter_cap: int) -> LearningRecord:
    evidence = event.evidence or []
    proposed = event.correction_text or event.user_source or "feedback indicates answer needs revision"
    factory = create_implicit_feedback_event if event.source_type == SourceType.USER_FEEDBACK_IMPLICIT else create_explicit_feedback_event
    record = factory(
        originating_question=event.original_question,
        original_answer=event.original_answer,
        corrected_proposed_fact=proposed,
        evidence=evidence,
        user_feedback_event_id=event.event_id,
    )
    validation = validate_evidence(record, evidence, chapter_cap)
    transition_trust_state(record, validation)
    if record.current_trust_state.value == "PROBATIONARY":
        shadow = run_shadow_validation(record)
        transition_trust_state(record, validation, shadow=shadow, targeted_regression_passed=True)
    record.audit("feedback_processed", "eligible feedback processed through autonomous trust engine", signal=event.signal.value)
    return record
