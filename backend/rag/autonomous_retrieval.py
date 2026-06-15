from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

TRUST_STATES = {"OBSERVED", "PROBATIONARY", "TRUSTED", "DEMOTED", "QUARANTINED", "RETIRED"}
SOURCE_TYPES = {"SELF_EVALUATION", "USER_FEEDBACK_EXPLICIT", "USER_FEEDBACK_IMPLICIT"}
EXCLUDED_STATES = {"OBSERVED", "QUARANTINED", "RETIRED"}

@dataclass(frozen=True)
class AutonomousContextItem:
    record_id: str
    version_id: str
    trust_state: str
    trust_score: float
    retrieval_weight: float
    source_citations: list[str]
    chapter_numbers: list[int]
    source_chunk_ids: list[str]
    provenance_type: str
    corrected_proposed_fact: str

    def to_context_text(self) -> str:
        return (
            f"[AUTONOMOUS_LEARNING record={self.record_id} version={self.version_id} "
            f"state={self.trust_state} trust={self.trust_score:.2f} weight={self.retrieval_weight:.2f} "
            f"provenance={self.provenance_type}]\n{self.corrected_proposed_fact}"
        )

    def to_citation(self) -> dict[str, Any]:
        return {
            "source": "autonomous_learning",
            "record_id": self.record_id,
            "version_id": self.version_id,
            "trust_state": self.trust_state,
            "trust_score": self.trust_score,
            "retrieval_weight": self.retrieval_weight,
            "source_citations": self.source_citations,
            "chapter_numbers": self.chapter_numbers,
            "source_chunk_ids": self.source_chunk_ids,
            "provenance_type": self.provenance_type,
        }

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def dedup_fingerprint(*parts: str) -> str:
    return hashlib.sha256("\u241f".join(parts).encode("utf-8")).hexdigest()

def chapter_safe(chapter_numbers: list[int], chapter_cap: int | None) -> bool:
    if chapter_cap is None:
        return True
    for ch in chapter_numbers:
        try:
            if int(ch) > int(chapter_cap):
                return False
        except (TypeError, ValueError):
            return False
    return True

def normalize_record_row(row: dict[str, Any]) -> AutonomousContextItem | None:
    state = str(row.get("current_trust_state") or "").upper()
    if state not in TRUST_STATES or state in EXCLUDED_STATES:
        return None
    if state == "PROBATIONARY":
        return None
    if state == "DEMOTED" and float(row.get("retrieval_weight") or 0) <= 0:
        return None
    if state != "TRUSTED" and state != "DEMOTED":
        return None
    source_type = str(row.get("source_type") or "")
    if source_type not in SOURCE_TYPES:
        return None
    version_id = str(row.get("current_version_id") or row.get("record_id") or "")
    chapters = [int(x) for x in (row.get("chapter_numbers") or []) if str(x).isdigit()]
    return AutonomousContextItem(
        record_id=str(row.get("record_id")),
        version_id=version_id,
        trust_state=state,
        trust_score=max(0.0, min(1.0, float(row.get("trust_score") or 0))),
        retrieval_weight=max(0.0, min(1.0, float(row.get("retrieval_weight") or 0))),
        source_citations=list(row.get("source_citations") or []),
        chapter_numbers=chapters,
        source_chunk_ids=list(row.get("source_chunk_ids") or []),
        provenance_type=source_type,
        corrected_proposed_fact=str(row.get("corrected_proposed_fact") or ""),
    )

def fetch_autonomous_context_items(
    supabase,
    *,
    question: str,
    chapter_cap: int | None,
    limit: int = 3,
    include_shadow: bool = False,
) -> list[AutonomousContextItem]:
    if not supabase:
        return []
    try:
        query = (
            supabase.table("autonomous_learning_records")
            .select("record_id,current_version_id,source_type,corrected_proposed_fact,source_citations,chapter_numbers,source_chunk_ids,current_trust_state,trust_score,retrieval_weight,last_validation_timestamp")
            .in_("current_trust_state", ["TRUSTED"] + (["PROBATIONARY"] if include_shadow else []))
            .order("trust_score", desc=True)
            .limit(max(1, min(limit, 5)))
        )
        resp = query.execute()
    except Exception:
        return []
    items: list[AutonomousContextItem] = []
    q = " ".join((question or "").lower().split())
    for row in (getattr(resp, "data", None) or []):
        item = normalize_record_row(row)
        if not item:
            continue
        if not chapter_safe(item.chapter_numbers, chapter_cap):
            continue
        fact_lower = item.corrected_proposed_fact.lower()
        if q and len(q) > 2 and not any(tok in fact_lower for tok in q.split() if len(tok) >= 3):
            # Keep retrieval bounded but do not require brittle full-text matching.
            if item.trust_score < 0.9:
                continue
        items.append(item)
    return items[:limit]

def merge_autonomous_context(context_data: dict[str, Any] | None, items: list[AutonomousContextItem]) -> dict[str, Any] | None:
    if not items:
        return context_data
    base = dict(context_data or {"context_text": "", "citations": [], "chunks_used": 0})
    extra_text = "\n\n".join(item.to_context_text() for item in items)
    base["context_text"] = (base.get("context_text") or "") + ("\n\n" if base.get("context_text") else "") + extra_text
    cits = list(base.get("citations") or [])
    cits.extend(item.to_citation() for item in items)
    base["citations"] = cits
    base["chunks_used"] = int(base.get("chunks_used") or 0) + len(items)
    base["autonomous_learning_items"] = [item.to_citation() for item in items]
    return base

def append_version_snapshot(supabase, record_id: str, snapshot: dict[str, Any]) -> str | None:
    version_id = snapshot.get("version_id") or dedup_fingerprint(record_id, canonical_json(snapshot), datetime.now(timezone.utc).isoformat())
    payload = {"version_id": version_id, "record_id": record_id, "snapshot": snapshot}
    try:
        supabase.table("autonomous_learning_record_versions").insert(payload).execute()
    except Exception:
        return None
    return str(version_id)
