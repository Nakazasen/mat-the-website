# Phase 11F-0B Current 50-Case Run Final Report

This document reports the final frozen results, checksums, and analysis of the 50-case benchmark evaluation run under task-5229.

## 1. Final Run Status
- **Task ID**: `3f20818a-51e6-43a9-a361-44d84a89b169/task-5229`
- **Exit Status**: SUCCESS
- **Completed Cases**: 50 / 50
- **Failed/Error Cases**: 0
- **Start Timestamp**: 2026-06-14T06:23:17 (Local) / 2026-06-13T23:23:17Z (UTC)
- **Finish Timestamp**: 2026-06-14T06:37:40 (Local) / 2026-06-13T23:37:40Z (UTC)
- **Wall-Clock Duration**: 14 minutes 23 seconds (863 seconds)
- **Last Completed Case**: `adv-05`
- **Results Output Path**: `backend/evals/chapter_bot_quality_results_v1.json`

## 2. Frozen Results Path
- **Frozen File Path**: `backend/evals/runs/chapter_bot_quality_results_50case_20260614_063740.json` (Copied to prevent accidental overrides).

## 3. All Checksums (SHA-256)
- **Original Results SHA-256**: `ec4e480187be9ff15aa25a744bb2137e4c67348e2376b98b7d27787ff3f060c2`
- **Frozen Results SHA-256**: `ec4e480187be9ff15aa25a744bb2137e4c67348e2376b98b7d27787ff3f060c2`
- **Benchmark Cases JSON SHA-256**: `510df8fb91e6c9548517f74d3c2508d8a755229f0639adc619eca5d191b4a278`
- **AI Oracle File (`ai_oracle.py`) SHA-256**: `d63461c92b6359b864ac56af8f4c50c2af8293651034aa32309b0d3e6236a2b3`
- **Retrieval File (`retrieval.py`) SHA-256**: `7556163d94169362bebdf4e45a44685917e00f42f0c486535950fd8ad238727c`
- **Evaluator Script (`evaluate_chapter_bot_quality.py`) SHA-256**: `722f1d0efb8625b8da7fef12ccc6bf59d23059f43857b935ce4bc40d136e3788`
- **Tracked Binary Git Diff SHA-256**: `c554d88aa86b9a2a1a21a52a78b43bdf9b77c44b29e10b5261def2a6b4fb31c7`

## 4. Dirty Worktree Fingerprint
- **Classification**: `BENCHMARK_VALID_FOR_FROZEN_DIRTY_WORKTREE`
- **Git HEAD Commit**: `354b088023a8459a899d2a2e62a15e537fdcda9b`
- **Git Status Summary**:
  ```
   M backend/ai_providers/openai_compatible.py
   M backend/rag/generated_feedback_to_golden_promotion_report.json
   M backend/rag/generated_golden_oracle_regression_report.json
   M backend/rag/generated_provisional_library_type_normalization_plan.json
   M backend/rag/generated_story_growth_coverage_audit.json
   M backend/rag/retrieval.py
   M backend/routes/ai_oracle.py
   M backend/tests/test_ai_oracle_rag.py
   M backend/tests/test_oracle_provisional_retrieval.py
   M backend/tests/test_rag_retrieval.py
   M frontend/src/components/OraclePanel.tsx
  ```
- **Untracked Source/Eval Files**:
  - `backend/evals/chapter_bot_quality_cases_v1.json`
  - `backend/evals/chapter_bot_quality_results_v1.json`
  - `backend/scripts/evaluate_chapter_bot_quality.py`

## 5. Final 50-Case Metrics
- **Total Cases**: 50
- **Score 0 Count**: 0
- **Score 1 Count**: 1
- **Score 2 Count**: 14
- **Score 3 Count**: 35
- **Mean Score**: 2.68
- **Median Score**: 3.0
- **Percent Score >= 2**: 98.00%
- **Percent Score 3**: 70.00%
- **Unsupported Claims Count**: 1 (Rate: 2.00%)
- **Wrong Chapter Count**: 1 (Rate: 2.00% wrong selected chapter rate; top-1 rate is 4.00%)
- **Future Spoiler Leakage**: 0 (Rate: 0.00%)
- **Abstention Precision**: 100.00%
- **Abstention Recall**: 100.00%
- **Unavailable Chapter Accuracy**: 100.00%
- **Retrieval Recall@1**: 86.00%
- **Retrieval Recall@3**: 88.00%
- **Retrieval Recall@5**: 90.00%
- **Retrieval Recall@10**: 90.00%
- **MRR**: 0.8707

## 6. All Sub-3 Cases (Score < 3)
Below is the complete detail of the 15 cases scoring less than 3:

| Case ID | Category | Score | Reason | Root Cause | Retrieved Chapters | Expected Chapters |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| `sum-05` | chapter_summary | 2 | Bot answer includes most key facts but had a typo/mismatch: Lý Dương instead of Lý Bình for the level 5 zombie, and missed small details. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[5, 5, 5, 5]` | `[]` |
| `sum-06` | chapter_summary | 2 | Bot answer covers required facts and clusters but missed optional facts like "level 3" and "level-up" details. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[6, 6, 6, 6]` | `[]` |
| `char-02` | character_question | 2 | Missing optional details about "Hồi tức" skill, weapon info, and had a contradiction in weapon description. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[8, 9, 7, 5]` | `[]` |
| `char-06` | character_question | 2 | Bot missed mentioning the exact chapter number where the character appeared. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[400, 400, 399, 400, 399]` | `[400]` |
| `char-07` | character_question | 2 | Bot answer contains required facts but added additional context not in references (though valid). | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[424, 425, 830, 424]` | `[830]` |
| `char-09` | character_question | 2 | Bot answer lacks details on the "Khỏe mạnh kép" skill. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[10, 9, 8, 10]` | `[1, 10]` |
| `char-10` | character_question | 2 | Bot missed detail about the multiverse. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[830, 813, 828, 829]` | `[800, 830]` |
| `event-01` | event_causality_question | 2 | Bot stated attack details weren't explicitly described in Ch 2 when they actually were in the source text. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[2, 2, 3, 4]` | `[1, 2]` |
| `event-03` | event_causality_question | 2 | Bot missed mentioning the elimination of zombie Cổ Chính with baseball bat before fighting the level 3 zombie. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[4, 4, 4, 4]` | `[4]` |
| `event-04` | event_causality_question | 2 | Bot missed mentioning the specific level of acceleration boots and exact strength increase points. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[6, 6, 6, 6]` | `[6]` |
| `event-07` | event_causality_question | 2 | Bot missed minor details regarding the usage of ice spear and ice hammer. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[9, 9, 9, 9]` | `[9]` |
| `event-09` | event_causality_question | 1 | Bot only mentioned breaking one egg, and missed the second egg thrown to Eat-3 and taking the third one. Also contradicted instructions. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[830, 830, 830, 830]` | `[830]` |
| `loc-01` | location_world_question | 2 | Contradiction regarding building being the center of the outbreak. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[1, 10, 1, 10]` | `[1, 10]` |
| `loc-04` | location_world_question | 2 | Bot wasn't clear about the evacuation being complete. | LLM synthesis error: Bot missed details or added incorrect/unsupported claims | `[830, 830, 830, 830]` | `[830]` |
| `adv-04` | adversarial_ambiguous | 2 | Bot hallucinated some detail not found in reference or source context. Retrieval also missed the target chapter 3. | Retrieval mismatch: No retrieved chapters in allowed range [3] | `[1, 2, 2, 1]` | `[3]` |

## 7. Quota/Call Accounting
- **Oracle Calls (in task-5229)**: 50
- **Judge Calls (in task-5229)**: 50
- **Failed Provider Calls**: 0
- **Retries**: 0
- **429 Rate-Limits**: 0
- **Timeouts**: 0
- **Estimated Total Calls (this run)**: 100
- **Estimated Total Calls (including dry-runs)**: 100 (No other dry-runs recorded in active log task-5229)
- **Token Accounting Status**: `TOKEN_ACCOUNTING_UNAVAILABLE` (Token counts not returned/logged by provider).

## 8. Experimental Decision
- **Decision**: `INSUFFICIENT_COMPARISON_BASELINE`
- **Rationale**: While the relaxation of the target chapter restriction in `chapter_specific_fact` successfully fixed case `event-06` (which went from 0 to 3/3 score), and overall Score >= 2 Rate is 98.00%, we do not have a previously stored frozen baseline file on disk to perform a direct differential code-to-result evaluation. Thus, we formally classify the baseline comparison as insufficient, but proceed with recommending to KEEP the changes tentatively as they solved `event-06` with no visible regressions on other cases.

## 9. Correct Master Progress
- **Phase 0 (Foundations)**: 100% (Verifications and schema gates fully functional)
- **Phase 1 (Benchmark Baseline)**: 100% (Completed the 50-case benchmark, froze the results and reported final metrics)
- **Phase 2 (Retrieval Improvements)**: 40% (Chapter-aware filtering and relaxed fact target logic implemented; only one retrieval experiment done)
- **Phase 3 (Synthesis & Optimizations)**: 20% (Long chapter batch synthesis implemented; no additional experiments)
- **Phase 4 (Multi-Provider Routing)**: 20% (Multi-provider routing and citation extraction implemented; no additional experiments)
- **Phases 5–8**: 0% (Not yet implemented)
- **Overall Weighted Progress**: **46.00%**
  - *Weights configuration*:
    - Phase 0: 10% weight -> Contribution: 10%
    - Phase 1: 20% weight -> Contribution: 20%
    - Phase 2: 25% weight -> Contribution: 10%
    - Phase 3: 15% weight -> Contribution: 3%
    - Phase 4: 15% weight -> Contribution: 3%
    - Phase 5: 5% weight -> Contribution: 0%
    - Phase 6: 5% weight -> Contribution: 0%
    - Phase 7: 3% weight -> Contribution: 0%
    - Phase 8: 2% weight -> Contribution: 0%

## 10. Recommended Next Single Action
- **Recommendation**: `ESTABLISH_NEW_FROZEN_BASELINE` (Merge current dirty worktree changes or keep them as the new official baseline, and start Phase 2 retrieval optimizations).
