import json
from pathlib import Path

from backend.rag.autonomous_feedback_processor import FeedbackEvent, FeedbackSignal, process_feedback_event
from backend.rag.autonomous_learning import EvidenceItem, TrustState, create_self_evaluation_event, validate_evidence, transition_trust_state, run_shadow_validation, run_canary_validation
from backend.rag.autonomous_learning_store import InMemoryAutonomousLearningStore
from backend.rag.autonomous_retrieval import fetch_autonomous_context_items, merge_autonomous_context, normalize_record_row

ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "backend/migrations/20260616_autonomous_learning.sql"

class Resp:
    def __init__(self, data): self.data = data
class Query:
    def __init__(self, data): self.data=data
    def select(self,*a,**k): return self
    def in_(self,*a,**k): return self
    def order(self,*a,**k): return self
    def limit(self,*a,**k): return self
    def execute(self): return Resp(self.data)
class FakeSupabase:
    def __init__(self, rows): self.rows=rows; self.tables=[]
    def table(self, name): self.tables.append(name); return Query(self.rows)

def evidence(ch=1):
    return [EvidenceItem(citation="story:1", chapter_number=ch, chunk_id="chunk-1", canonical=True, independent_source_id="story:1")]

def row(state="TRUSTED", ch=1):
    return {
        "record_id":"r1","current_version_id":"v1","source_type":"SELF_EVALUATION",
        "corrected_proposed_fact":"Hàn Phong fact from source","source_citations":["story:1"],
        "chapter_numbers":[ch],"source_chunk_ids":["chunk-1"],"current_trust_state":state,
        "trust_score":0.95,"retrieval_weight":1.0
    }

def test_self_evaluation_persists_to_store_with_version():
    rec=create_self_evaluation_event(originating_question="q", original_answer="a", corrected_proposed_fact="fact", evidence=evidence())
    store=InMemoryAutonomousLearningStore(); store.save_record(rec)
    assert store.get_record(rec.record_id) is rec
    assert store.versions

def test_feedback_persists_to_store_with_dedup():
    ev=FeedbackEvent(event_id="e1", signal=FeedbackSignal.CORRECTION_TEXT, original_question="q", original_answer="a", correction_text="fact", evidence=evidence())
    rec=process_feedback_event(ev, chapter_cap=10)
    store=InMemoryAutonomousLearningStore(); store.save_record(rec); store.save_record(rec)
    assert len(store.records)==1
    assert not store.wrote_to_wiki_entries()

def test_implicit_correction_persists():
    ev=FeedbackEvent(event_id="e2", signal=FeedbackSignal.NEXT_MESSAGE_CORRECTION, original_question="q", original_answer="a", correction_text="fact", evidence=evidence())
    rec=process_feedback_event(ev, chapter_cap=10)
    assert rec.source_type.value == "USER_FEEDBACK_IMPLICIT"

def test_trusted_record_reaches_real_retrieval_merge():
    items=fetch_autonomous_context_items(FakeSupabase([row()]), question="Hàn Phong", chapter_cap=10)
    merged=merge_autonomous_context({"context_text":"base","citations":[],"chunks_used":1}, items)
    assert items and "AUTONOMOUS_LEARNING" in merged["context_text"]
    assert merged["citations"][-1]["record_id"] == "r1"

def test_probationary_record_does_not_alter_live_retrieval():
    assert fetch_autonomous_context_items(FakeSupabase([row("PROBATIONARY")]), question="Hàn Phong", chapter_cap=10) == []

def test_quarantined_record_cannot_reach_retrieval():
    assert normalize_record_row(row("QUARANTINED")) is None

def test_chapter_cap_removes_future_facts():
    assert fetch_autonomous_context_items(FakeSupabase([row("TRUSTED", ch=99)]), question="Hàn Phong", chapter_cap=10) == []

def test_rollback_restores_complete_previous_snapshot():
    rec=create_self_evaluation_event(originating_question="q", original_answer="a", corrected_proposed_fact="v1", evidence=evidence())
    store=InMemoryAutonomousLearningStore(); store.save_record(rec); v1=getattr(rec,"current_version_id")
    rec.corrected_proposed_fact="v2"; rec.version=2; rec.current_trust_state=TrustState.TRUSTED; store.save_record(rec)
    store.restore_version(rec.record_id, v1)
    assert rec.corrected_proposed_fact == "v1"

def test_migration_has_version_rls_indexes_append_only_and_no_wiki_fk():
    sql=MIGRATION.read_text(encoding="utf-8").lower()
    assert "autonomous_learning_record_versions" in sql
    assert "rollback_target_version_id" in sql and "previous_version_id" in sql
    assert "enable row level security" in sql
    assert "append-only" in sql
    assert "idx_autonomous_records_retrieval" in sql
    assert "references wiki_entries" not in sql
    assert "service_role" in sql

def test_public_cannot_set_trusted_policy_static():
    sql=MIGRATION.read_text(encoding="utf-8").lower()
    assert "current_trust_state = 'trusted'" in sql
    assert "auth.role() = 'service_role'" in sql

def test_canary_failure_triggers_rollback_policy():
    rec=create_self_evaluation_event(originating_question="q", original_answer="a", corrected_proposed_fact="fact", evidence=evidence())
    rec.version=2; rec.previous_version=1
    run_canary_validation(rec, contradiction=True, reason="contradiction")
    assert rec.current_trust_state == TrustState.DEMOTED
