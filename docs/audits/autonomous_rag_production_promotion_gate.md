# Autonomous RAG Production Promotion Gate

Timestamp: 2026-06-16 06:43 +07
Starting HEAD verified locally: `dc34a0d`

## Decision

Status: **LOCAL GATE PASS / READY FOR SCOPED COMMIT**.

This gate validates the autonomous two-source RAG learning wiring before push and redeploy. It does not claim production is complete until the scoped commit, push, Render redeploy, and non-live production smoke test are completed.

## User Requirements Checked

- Admin is not a normal-path bottleneck.
- Learning accepts Source A: self-evaluation events.
- Learning accepts Source B: direct user feedback events.
- User feedback writes remain server-sanitized and do not trust client-spoofed provenance.
- Autonomous knowledge is stored outside `wiki_entries`.
- Retrieval uses only trusted autonomous records.
- Workflow remains scheduled but bounded.
- No local heavy production regression was run.
- No production `/oracle/ask` live LLM call was made in this gate.
- No secrets were printed, logged, committed, or rotated.

## Implemented Scope

### Schema

Migration: `backend/migrations/20260616_autonomous_learning.sql`

- Adds `autonomous_learning_feedback_events`.
- Adds `autonomous_learning_records`.
- Adds immutable `autonomous_learning_record_versions`.
- Adds immutable `autonomous_learning_audit_events`.
- Adds RLS policies.
- Adds trust-state and score constraints.
- Adds deduplication fingerprints.
- Does not reference or write to `wiki_entries`.

### Persistence

File: `backend/rag/autonomous_learning_store.py`

- Saves feedback event metadata.
- Saves current record state.
- Saves version snapshots.
- Saves audit events.
- Fetches trusted records for retrieval.

### Retrieval

File: `backend/rag/autonomous_retrieval.py`

- Filters autonomous records to trusted state.
- Enforces chapter cap.
- Converts trusted records into RAG context snippets.
- Preserves trace metadata.

### Oracle Route Wiring

File: `backend/routes/ai_oracle.py`

- Merges trusted autonomous learning context into Oracle RAG context.
- Preserves legacy RAG trace selected chunk IDs.
- Adds `/oracle/feedback` autonomous processing side-effect.
- Keeps legacy `rag_feedback` insert contract for existing clients/tests.
- Uses server-derived trust provenance; spoofed client fields are ignored.

### Scheduled Workflow

File: `.github/workflows/golden-oracle-regression.yml`

- Keeps 6-hour schedule.
- Replaces unsafe full production regression with bounded autonomous loop.
- Enforces max 2 questions.
- Enforces max 15s request timeout.
- Enforces attempts = 1.
- Adds single backend health probe.
- Adds migration-readiness fail-closed checks.
- Keeps concurrency cancellation.

## Verification Evidence

### Full backend gate

Command:

```powershell
uv run pytest backend/tests -q
```

Result:

```text
617 passed, 1 warning in 47.57s
```

### Targeted autonomous/workflow gate

Command:

```powershell
uv run pytest backend/tests/test_autonomous_learning_policy.py backend/tests/test_autonomous_learning_integration.py backend/tests/test_golden_regression_workflow.py backend/tests/test_phase11f3d_evaluator_integrity.py backend/tests/test_oracle_no_source_coded_answer_overrides.py -q
```

Result:

```text
83 passed, 1 warning
```

### Regression fixes validated

Command:

```powershell
uv run pytest backend/tests/test_oracle_chapter_summary_coverage.py::test_general_lore_retrieval_and_gating_behavior backend/tests/test_oracle_feedback_to_golden_promotion.py::test_client_malicious_payload_fails_to_elevate backend/tests/test_oracle_feedback_to_golden_promotion.py::test_authenticated_reader_payload_fails_to_elevate backend/tests/test_oracle_feedback_to_golden_promotion.py::test_anonymous_payload_spoofed_fields_ignored_in_route backend/tests/test_rag_feedback.py::test_submit_valid_feedback -q
```

Result:

```text
5 passed, 1 warning
```

### Compile and whitespace gate

Earlier targeted gate included:

```powershell
uv run python -m compileall backend
git diff --check
```

Result: PASS.

## Production Safety Notes

- The scheduled workflow still exists but is bounded and fail-closed.
- The autonomous learning tables are separate from canonical wiki content.
- Client-provided trust fields do not elevate privilege.
- Authenticated reader provenance is server-derived only.
- Mock/test Supabase clients are guarded from autonomous side-effect writes to keep legacy feedback tests deterministic.

## Remaining Production Steps

1. Commit only scoped files.
2. Push `main`.
3. Redeploy Render.
4. Run non-live production smoke test.
5. Confirm service health after deploy.

## Residual Risks

- Database migration still must be applied in the production Supabase environment before the new autonomous persistence path can fully operate.
- Render deployment may fail independently of code gates due to environment/configuration issues.
- The old historical token exposure risk remains accepted by user decision and was not remediated in this phase.
