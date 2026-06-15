from __future__ import annotations

from dataclasses import asdict
from typing import Protocol, Any

from backend.rag.autonomous_learning import LearningRecord, TrustState
from backend.rag.autonomous_retrieval import dedup_fingerprint, canonical_json

class AutonomousLearningStore(Protocol):
    def save_record(self, record: LearningRecord) -> None: ...
    def get_record(self, record_id: str) -> LearningRecord | None: ...
    def list_records(self) -> list[LearningRecord]: ...
    def append_audit(self, record_id: str, event: dict) -> None: ...

class InMemoryAutonomousLearningStore:
    def __init__(self) -> None:
        self.records: dict[str, LearningRecord] = {}
        self.versions: dict[str, dict[str, Any]] = {}
        self.audit_events: list[dict[str, Any]] = []
        self.write_targets: list[str] = []
        self.fingerprints: set[str] = set()

    def _snapshot(self, record: LearningRecord) -> dict[str, Any]:
        payload = asdict(record)
        payload["source_type"] = record.source_type.value
        payload["current_trust_state"] = record.current_trust_state.value
        payload["dedup_fingerprint"] = dedup_fingerprint(record.source_type.value, record.originating_question, record.corrected_proposed_fact)
        return payload

    def save_record(self, record: LearningRecord) -> None:
        self.write_targets.append("autonomous_learning_records")
        snapshot = self._snapshot(record)
        fp = snapshot["dedup_fingerprint"]
        if fp in self.fingerprints and record.record_id not in self.records:
            record.audit("deduplicated", "equivalent autonomous learning record rejected")
            return
        self.fingerprints.add(fp)
        version_id = dedup_fingerprint(record.record_id, str(record.version), canonical_json(snapshot))
        snapshot["version_id"] = version_id
        self.versions[version_id] = snapshot
        setattr(record, "current_version_id", version_id)
        self.records[record.record_id] = record

    def get_record(self, record_id: str) -> LearningRecord | None:
        return self.records.get(record_id)

    def list_records(self) -> list[LearningRecord]:
        return list(self.records.values())

    def append_audit(self, record_id: str, event: dict) -> None:
        self.write_targets.append("autonomous_learning_audit_events")
        self.audit_events.append({"record_id": record_id, "event": event})
        rec = self.records[record_id]
        rec.audit_trail.append(event)

    def restore_version(self, record_id: str, version_id: str) -> LearningRecord | None:
        snapshot = self.versions.get(version_id)
        rec = self.records.get(record_id)
        if not snapshot or not rec:
            return None
        rec.corrected_proposed_fact = snapshot["corrected_proposed_fact"]
        rec.source_citations = list(snapshot.get("source_citations") or [])
        rec.chapter_numbers = list(snapshot.get("chapter_numbers") or [])
        rec.source_chunk_ids = list(snapshot.get("source_chunk_ids") or [])
        rec.current_trust_state = TrustState(snapshot["current_trust_state"])
        rec.trust_score = float(snapshot.get("trust_score") or 0)
        rec.retrieval_weight = float(snapshot.get("retrieval_weight") or 0)
        rec.rollback_target = snapshot.get("rollback_target")
        rec.audit("restored", "restored complete immutable version snapshot", version_id=version_id)
        return rec

    def wrote_to_wiki_entries(self) -> bool:
        return "wiki_entries" in self.write_targets

class SupabaseAutonomousLearningStore:
    def __init__(self, supabase) -> None:
        self.supabase = supabase

    def _payload(self, record: LearningRecord) -> dict[str, Any]:
        payload = asdict(record)
        payload["source_type"] = record.source_type.value
        payload["current_trust_state"] = record.current_trust_state.value
        payload["dedup_fingerprint"] = dedup_fingerprint(record.source_type.value, record.originating_question, record.corrected_proposed_fact)
        return payload

    def save_record(self, record: LearningRecord) -> None:
        payload = self._payload(record)
        version_snapshot = dict(payload)
        version_id = dedup_fingerprint(record.record_id, str(record.version), canonical_json(version_snapshot))
        payload["current_version_id"] = version_id
        self.supabase.table("autonomous_learning_records").upsert(payload).execute()
        self.supabase.table("autonomous_learning_record_versions").insert({
            "version_id": version_id,
            "record_id": record.record_id,
            "version": record.version,
            "snapshot": version_snapshot,
            "trust_state": record.current_trust_state.value,
            "dedup_fingerprint": payload["dedup_fingerprint"],
        }).execute()
        self.append_audit(record.record_id, {"event": "saved", "record_id": record.record_id, "version_id": version_id})

    def get_record(self, record_id: str) -> LearningRecord | None:
        raise NotImplementedError("Hydration is intentionally implemented in application service layer")

    def list_records(self) -> list[LearningRecord]:
        raise NotImplementedError("Use filtered service queries in application code")

    def append_audit(self, record_id: str, event: dict) -> None:
        self.supabase.table("autonomous_learning_audit_events").insert({
            "record_id": record_id,
            "event": event,
        }).execute()
