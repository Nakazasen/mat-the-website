# Autonomous Two-Source RAG Learning Loop Audit

## Deployment State

Implemented locally only. No push, no deploy, and no live model calls were performed during implementation or tests.

## Two Learning Sources

- Source A: `SELF_EVALUATION` records are created by the bounded scheduled learning loop and deterministic trust engine.
- Source B: `USER_FEEDBACK_EXPLICIT` and `USER_FEEDBACK_IMPLICIT` records are processed by the feedback processor.

## Trust Lifecycle

The trust state machine is automatic and contains only:

- `OBSERVED`
- `PROBATIONARY`
- `TRUSTED`
- `DEMOTED`
- `QUARANTINED`
- `RETIRED`

No normal path requires admin approval, Apply-to-Wiki, or a manual queue.

## Automatic Promotion Policy

- `OBSERVED` promotes to `PROBATIONARY` when source provenance exists, chapter scope is valid, no future leakage exists, no critical contradiction exists, and support score passes threshold.
- `PROBATIONARY` promotes to `TRUSTED` only after independent confirmations or canonical source confirmation plus shadow validation and targeted regression policy.
- Unsupported user feedback remains `OBSERVED`.

## Shadow and Canary Behavior

- Shadow validation compares source support, contradiction, future leakage, latency, and retrieval quality before live retrieval eligibility.
- Canary regression triggers automatic rollback and demotion.

## Automatic Rollback

Rollback restores the previous version target, preserves audit history, records the reason, and removes the harmful record from retrieval by demoting it.

## User Feedback Ingestion

Explicit and implicit feedback are normalized into learning records and processed through the same trust engine as self-evaluation.

## Retrieval Integration

Trusted records are eligible for retrieval automatically. Quarantined, observed, retired, and admin-disabled records are excluded. Probationary records are available only for shadow retrieval.

## Admin Role

Admin is non-blocking and limited to monitoring/emergency controls: disable, restore, demote, quarantine, and freeze-style control metadata.

## Prohibited Write Targets

The implementation does not write directly to `wiki_entries`, benchmark gold, application source code, credentials, push/deploy state, or canonical content. The migration creates only autonomous learning tables.

## Bounded Schedule

The GitHub workflow remains scheduled but is bounded to at most two questions per run, one attempt, timeout <= 15 seconds, no full static suite, no full DB suite, no 50-case run, no retry storm, no push, and no deploy.

## Tests

Deterministic tests cover the requested autonomous learning requirements and workflow constraints. The tests use no live production or live model requests.
