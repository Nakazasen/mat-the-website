# Phase 11F-3C0C Final Provenance Seal

## Classification

`PASS_PHASE_11F3C0C_FINAL_PROVENANCE_SEALED`

## Two-commit lineage

- Branch: `main`
- Starting cleanup code HEAD: `67669790dbf00cedec1caeb65b3256769446f926`
- Parent audit-seal commit: `2dc382ea291d2c5fffd6dce3d5bda3a9919d10fe`
- Cleanup parent valid: yes

### Parent audit-seal commit

- Message: `docs(oracle): revoke answer-override-contaminated evidence`
- Scope: documentation-only audit/revocation files.
- Files: 4.

### Cleanup code commit

- Message: `Remove oracle answer overrides`
- Scope: expected cleanup code, tests, and cleanup report.
- Files: 4.

## Generated RAG drift preservation and restoration

Four tracked generated files were dirty at the start of this hygiene step:

1. `backend/rag/generated_feedback_to_golden_promotion_report.json`
2. `backend/rag/generated_golden_oracle_regression_report.json`
3. `backend/rag/generated_provisional_library_type_normalization_plan.json`
4. `backend/rag/generated_story_growth_coverage_audit.json`

Evidence artifacts were captured and left uncommitted:

- `backend/scratch/phase11f3c0c_generated_rag_drift.patch`
- `backend/scratch/phase11f3c0c_generated_rag_drift_manifest.json`

Initial drift classification: `generated_runtime_drift` for all 4 files.
No source requirement, manually curated data, or business truth change was
identified in the generated drift manifest.

After the final full backend run, the same four generated files drifted again.
Evidence artifacts were captured and left uncommitted:

- `backend/scratch/phase11f3c0c_post_test_generated_rag_drift.patch`
- `backend/scratch/phase11f3c0c_post_test_generated_rag_drift_manifest.json`

Post-test drift classification: `generated_runtime_drift_after_tests` for all 4
files. The files were restored to `HEAD` after evidence capture. Restoring these
generated outputs does not stale the source/test validation because no production
or test file was modified after the final test gates.

## Final committed checksums

Required final source/test byte checks were verified by comparing worktree bytes
to `HEAD:<path>` bytes before the final test gates.

| Path | SHA-256 |
|---|---|
| `backend/routes/ai_oracle.py` | `c9cf70919275625234c49958c182a90bb5a9f43e3a41ddc3d56d092b20042e1a` |
| `backend/tests/test_oracle_no_source_coded_answer_overrides.py` | `bed4ebc1ccadb271b6a75e03e5a59217168094fb6abc1437e45df38c0a1ffea6` |
| `backend/tests/test_oracle_grounded_generation_phase11f3a.py` | `95cc4b2d0a5c97eec8c5746617780045b6af1873864418b10cf26b539d40e167` |

Additional committed report checksum retained from the previous seal:

| Path | SHA-256 |
|---|---|
| `docs/audits/phase11f3c0b_answer_override_removal.md` | `1953f8c158fc7ec4e8cc34ef83948113e92f57c9effb68d22482d171af4972f1` |
| `docs/audits/phase11f3c0_quality_evidence_revocation_manifest.json` | `c3bdf088a0c1243a89918bf1c36435f8a6130d74deb1394c7364ab46954cf7dc` |

## Static anti-override gate

Production source scanned at final cleanup HEAD:
`backend/routes/ai_oracle.py`.

Forbidden marker matches: 0.

Searched markers:

- `construct_fallback_grounded_answer`
- `Custom guards for failed benchmark cases`
- `sum-03`
- `loc-01`
- `char-01`
- `event-03`
- `event-07`
- `human_reference_answer`
- `required_facts`
- `optional_facts`
- `expected_answer`
- `benchmark canned`
- `mock answer`
- `answer override`

Safe-behavior confirmation:

- No request-controlled substring branch returns a complete story answer.
- No failed verifier installs a story literal.
- Empty retrieval plus unavailable provider safely abstains.
- Curated wiki boundary remains unchanged.
- Suspect canned story literals remaining: 0.

## Final test gates on exact committed source/test bytes

Environment:

```powershell
$env:PYTHONIOENCODING='utf-8'
```

### Targeted anti-override tests

Command:

```powershell
uv run pytest backend/tests/test_oracle_no_source_coded_answer_overrides.py -q
```

Result: `16 passed, 1 warning in 0.36s`.
Exit code: 0.
Observed run timestamp: `2026-06-14T23:29:49Z` to `2026-06-14T23:29:52Z`.

### Grounded generation tests

Command:

```powershell
uv run pytest backend/tests/test_oracle_grounded_generation_phase11f3a.py -q
```

Result: `34 passed, 1 warning in 2.03s`.
Exit code: 0.
Observed run timestamp: `2026-06-14T23:29:57Z` to `2026-06-14T23:30:00Z`.

### Chapter gate micro-benchmark unit test

Command:

```powershell
uv run pytest backend/tests/test_oracle_chapter_gate_benchmark.py::test_chapter_gate_micro_benchmark -q -s
```

Result: `1 passed, 1 warning in 1.43s`.
Exit code: 0.
Observed run timestamp: `2026-06-14T23:30:05Z` to `2026-06-14T23:30:08Z`.

### Full backend suite

Command:

```powershell
uv run pytest backend/tests -q
```

Result: `551 passed, 1 warning in 45.10s`.
Exit code: 0.
Task log:
`C:/Users/Admin/.gemini/antigravity-ide/brain/2891927e-e124-4cf2-b688-493748331e0f/.system_generated/tasks/task-276.log`
Observed start timestamp: `2026-06-14T23:30:12Z`.
Observed finish timestamp: `2026-06-14T23:30:59Z`.

No production or test file was modified after starting these gates. The only
post-test tracked drift was generated RAG output, captured and restored as noted
above.

## Compileall result

Command:

```powershell
uv run python -m compileall backend
```

Result: successful compile traversal.
Exit code: 0.
Observed timestamp: `2026-06-14T23:31:11Z` to `2026-06-14T23:31:12Z`.

`git diff --check` passed after compileall.

## Final worktree

Before this documentation-only provenance commit:

- Tracked worktree: clean.
- Staged state: clean.
- `HEAD`: `67669790dbf00cedec1caeb65b3256769446f926`.
- `git show --check HEAD`: passed.
- `origin/main...HEAD`: `0 9`.
- Untracked files: 138.

Untracked files are classified as forensic/runtime/contaminated artifacts and
were not treated as current evidence. They include scratch evidence, evaluator
run outputs, old Stage 1/2 artifacts, local DB/config/runtime files, and other
untracked audit materials. They were not deleted.

## Revoked evidence status

- Full Run 1: `ANSWER_OVERRIDE_CONTAMINATED_RUN_NOT_CLEAN_QUALITY_EVIDENCE`
- Phase 11F-3A targeted artifact:
  `ANSWER_OVERRIDE_CONTAMINATED_TARGETED_RUN_NOT_CLEAN_QUALITY_EVIDENCE`
- Phase 11F-3C Stage 1 acceptance: revoked / not clean quality evidence.
- All Phase 11F-3C Stage 2 artifacts: revoked / not clean quality evidence.

## Explicit non-actions

- Live model calls: 0.
- Stage 1: not run.
- Stage 2: not run.
- Full 50-case benchmark: not run.
- New evaluator: not created.
- Push: not performed.
- Deploy: not authorized.

## Progress

- Master Phase 4: 40–45%.
- Overall Super RAG: 40–43%.

## Next action

Create and commit an immutable clean evaluator specification.
