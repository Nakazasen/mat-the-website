from __future__ import annotations

from dataclasses import asdict
from typing import Protocol

from backend.rag.autonomous_learning import LearningRecord

class AutonomousLearningStore(Protocol):
    def save_record(self, record: LearningRecord) -> None: ...
    def get_record(self, record_id: str) -> LearningRecord | None: ...
    def list_records(self) -> list[LearningRecord]: ...
    def append_audit(self, record_id: str, event: dict) -> None: ...

class InMemoryAutonomousLearningStore:
    def __init__(self) -> None:
        self.records: dict[str, LearningRecord] = {}
        self.write_targets: list[str] = []

    def save_record(self, record: LearningRecord) -> None:
        self.write_targets.append("autonomous_learning_records")
        self.records[record.record_id] = record

    def get_record(self, record_id: str) -> LearningRecord | None:
        return self.records.get(record_id)

    def list_records(self) -> list[LearningRecord]:
        return list(self.records.values())

    def append_audit(self, record_id: str, event: dict) -> None:
        self.write_targets.append("autonomous_learning_audit_events")
        rec = self.records[record_id]
        rec.audit_trail.append(event)

    def wrote_to_wiki_entries(self) -> bool:
        return "wiki_entries" in self.write_targets

class SupabaseAutonomousLearningStore:
    def __init__(self, supabase) -> None:
        self.supabase = supabase

    def save_record(self, record: LearningRecord) -> None:
        payload = asdict(record)
        payload["source_type"] = record.source_type.value
        payload["current_trust_state"] = record.current_trust_state.value
        self.supabase.table("autonomous_learning_records").upsert(payload).execute()
        self.append_audit(record.record_id, {"event": "saved", "record_id": record.record_id})

    def get_record(self, record_id: str) -> LearningRecord | None:
        raise NotImplementedError("Hydration is intentionally implemented in application service layer")

    def list_records(self) -> list[LearningRecord]:
        raise NotImplementedError("Use filtered service queries in application code")

    def append_audit(self, record_id: str, event: dict) -> None:
        self.supabase.table("autonomous_learning_audit_events").insert({
            "record_id": record_id,
            "event": event,
        }).execute()
