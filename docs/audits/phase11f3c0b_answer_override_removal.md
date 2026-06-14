# Phase 11F-3C0B Answer Override Removal Report

## Classification

`FAIL_PHASE_11F3C0_PUBLIC_ANSWER_OVERRIDE_CONFIRMED` was addressed by removing
production answer override paths from the Oracle answer verification/repair flow.

## Production changes

- Removed `construct_fallback_grounded_answer` from `backend/routes/ai_oracle.py`.
- Removed benchmark-specific custom guard branches from `run_deterministic_guard`.
- Replaced the final failed post-guard override with safe abstention:
  `Dữ liệu hiện có chưa đủ để kết luận.`
- Preserved the existing curated wiki override boundary used by tests so feedback
  policy tests continue to exercise database/provisional behavior instead of
  being bypassed by curated test fixtures.

## Regression coverage

Added `backend/tests/test_oracle_no_source_coded_answer_overrides.py` to verify:

- Former exact trigger questions do not return hard-coded canned answers.
- Future-chapter prompts do not leak chapter-830 content with a low cap.
- Empty retrieval/provider-unavailable paths abstain instead of synthesizing story
  details.
- The removed fallback function and benchmark-specific guard markers are absent
  from the production Oracle source.
- Curated wiki snippets remain bounded entity metadata, do not match exact
  benchmark questions, and respect chapter caps.

Updated `backend/tests/test_oracle_grounded_generation_phase11f3a.py` to isolate
provider failure and empty-generation tests from the local wiki fast path.

## Validation

Commands run:

```powershell
$env:PYTHONIOENCODING='utf-8'; uv run pytest backend/tests/test_oracle_no_source_coded_answer_overrides.py -q
```

Result: `16 passed, 1 warning`.

```powershell
$env:PYTHONIOENCODING='utf-8'; uv run pytest backend/tests/test_oracle_grounded_generation_phase11f3a.py -q
```

Result: `34 passed, 1 warning`.

```powershell
$env:PYTHONIOENCODING='utf-8'; uv run pytest backend/tests/test_oracle_chapter_gate_benchmark.py::test_chapter_gate_micro_benchmark -q -s
```

Result: `1 passed, 1 warning`.

```powershell
$env:PYTHONIOENCODING='utf-8'; uv run pytest backend/tests/test_oracle_no_source_coded_answer_overrides.py backend/tests/test_oracle_provisional_retrieval.py::test_get_entity_context_for_oracle_feedback_policies -q
```

Result: `17 passed, 1 warning`.

```powershell
$env:PYTHONIOENCODING='utf-8'; uv run pytest backend/tests -q
```

Result: `551 passed, 1 warning`.

```powershell
$env:PYTHONIOENCODING='utf-8'; uv run python -m compileall backend
```

Result: successful compile traversal.

## Explicit non-actions

Per constraints, this cleanup did not:

- Run live LLM evaluation.
- Run Stage 1.
- Run Stage 2.
- Run the full 50-case benchmark.
- Modify evaluator live behavior.
- Push or deploy.
