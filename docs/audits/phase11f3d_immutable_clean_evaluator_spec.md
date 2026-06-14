# Phase 11F-3D Immutable Clean Evaluator Specification

## Threat model

Phase 11F-3C confirmed that production answer overrides and benchmark-shaped
branches can contaminate quality evidence. The 11F-3D evaluator therefore treats
benchmark gold as toxic during answer collection and isolates scoring into a
separate process that runs only after raw answers are sealed.

## Prior contamination incidents

Revoked evidence includes full Run 1, the Phase 11F-3A targeted artifact, Phase
11F-3C Stage 1 acceptance, and all Phase 11F-3C Stage 2 artifacts. Legacy Stage
1/2 scripts and their output artifacts are prohibited inputs for this evaluator.
They may be referenced only as revoked lineage.

## Process separation

The evaluator is split into two executable scripts:

- `backend/scripts/phase11f3d_collect_answers.py`
- `backend/scripts/phase11f3d_score_answers.py`

The collector prepares public Oracle requests and seals raw answers. It never
loads gold facts and never scores. The scorer reads a sealed raw answer artifact
and then loads Pro-reviewed V2 gold. It never calls Oracle, retrieval, generation,
verification, or repair.

## Sanitized manifest schema

`backend/evals/phase11f3d_targeted_query_manifest.json` contains at most 12 cases.
Each case contains only:

```json
{
  "case_id": "...",
  "question": "...",
  "chapter_progress": 0
}
```

The manifest must not contain required facts, optional facts, soft scoring facts,
reference answers, evidence refs, root causes, desired repair layers, acceptance
requirements, expected chapters beyond the public cap, or benchmark scores.

## Collector inputs and outputs

Collector inputs are explicit committed paths only:

- sanitized query manifest;
- committed production Oracle source for checksumming;
- runtime provider/model configuration without secrets;
- immutable evaluator contract.

Collector Oracle request payload is restricted to:

```json
{
  "question": "...",
  "chapter_progress": 0,
  "debug_bypass_cache": true
}
```

`case_id` labels the raw output externally but must never be passed into Oracle.
The collector writes a sealed raw answer artifact with answer text, abstention
metadata, citations, selected chunks/chapters, traces, provider/model accounting,
call counts, override hit count, benchmark reachability flag, per-case timestamps,
case errors, and checksums for source/evaluator inputs.

The collector refuses success on missing cases, duplicate case IDs, checksum
mutation, reachable benchmark fields, nonzero override hits, or non-abstain
answers without source evidence unless explicitly bounded curated entity metadata.

## Scorer inputs and outputs

The scorer runs only after a sealed raw answer artifact exists. It reads:

- sealed raw answer artifact;
- Pro-reviewed V2 gold;
- targeted source set;
- scoring/evaluator contract.

The scorer verifies checksums before loading gold and again before completion. It
must not call Oracle, retrieval, generation, verification, or repair; mutate raw
answers; change case selection; inject expected facts into production; or score
through case-specific branches.

## Scoring contract

The scorer preserves these metrics separately:

1. Official judge score, if later authorized.
2. Required source-supported fact recall.
3. Optional fact recall.
4. Abstention correctness.
5. Unsupported-claim count.
6. Contradiction count.
7. Wrong-chapter count.
8. Future-leakage count.
9. Retrieval coverage.
10. Verifier false-accept indicators.
11. Repair improvement/regression.
12. Provider/model call accounting.

Required-fact recall never automatically forces `human_score = 3`. If a Judge is
later authorized, raw Judge response, parsed result, and parse errors must all be
stored. Judge output must never be monkey-patched.

## Mutation invalidation

Before collection, the collector records SHA-256 for production Oracle, collector,
scorer, evaluator contract, query manifest, Pro-reviewed V2 benchmark, targeted
source set, and provider/model configuration. During collection it rechecks the
production source, collector, and query manifest after every case and at process
end.

Scoring rechecks the scorer, raw answer artifact, benchmark, targeted source set,
and contract. Any mismatch invalidates the entire run as:

`INVALID_SOURCE_OR_EVALUATOR_MUTATED_DURING_RUN`

No partial PASS is allowed after mutation.

## Clean-worktree requirement

Future live evaluation must run from a fresh detached worktree or equivalent
clean checkout created from a committed SHA. The live worktree must contain no
untracked forensic files, old Stage 1/2 scripts, contaminated results, scratch
patches, or local benchmark overrides. Evaluator inputs must be explicit committed
paths; recursive globs are prohibited.

## Failure classifications

- `INVALID_SOURCE_OR_EVALUATOR_MUTATED_DURING_RUN`
- `INVALID_BENCHMARK_FIELDS_REACHABLE_DURING_COLLECTION`
- `INVALID_OVERRIDE_HIT_DETECTED`
- `INVALID_UNSEALED_RAW_ANSWER_ARTIFACT`
- `INVALID_DUPLICATE_CASE_IDS`
- `INVALID_MISSING_CASES`

## Later targeted baseline protocol

The later live baseline must run exactly one execution per targeted case, with a
pinned provider, pinned model, pinned temperature, explicit timeout, no retries
that change provider/model, no evaluator edits during or after the run, and full
run invalidation on any checksum mismatch.

## Prohibited legacy files

The evaluator must not import, glob, or consume:

- `backend/scripts/evaluate_phase11f3c_stage1.py`
- `backend/scripts/evaluate_phase11f3c_stage2.py`
- `backend/evals/runs/phase11f3c_stage1_*.json`
- `backend/evals/runs/phase11f3c_stage2_*.json`
- `backend/scratch/phase11f3c_contaminated_worktree.patch`
- old contaminated Run 1 and targeted artifacts

## Phase boundary

No live evaluation is performed in Phase 11F-3D0. No live model is called, no old
Stage 1/2 evaluator is run, no 50-case benchmark is run, production Oracle is not
modified, and benchmark V1/V2 files are not modified.
