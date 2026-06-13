# Phase 11F-0B - 50-Case Chapter Bot Quality Benchmark

This document defines the quality baseline benchmark for the **Super RAG evidence-first** upgrade.

- **Benchmark Checksum (SHA-256)**: `f731f417a1cb47d617c1e4c001c795296133145a0e302322b1e16dcab68614d6`
- **File Location**: [chapter_bot_quality_cases_v1.json](file:///d:/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/evals/chapter_bot_quality_cases_v1.json)
- **Total Cases**: 50

---

## Case Distribution

| Category | Cases Count | Purpose |
| :--- | :---: | :--- |
| **Chapter Summary** | 15 | Summarizing specific chapters (e.g. Ch 1, Ch 830, etc.) covering short, medium, and long chapters. |
| **Character Question** | 10 | Questions on main/supporting characters (e.g., Hàn Phong, Chu Vấn, La Thiên Dật). |
| **Event / Causality** | 10 | Action sequences, causal chains, and plot events. |
| **Location / World** | 5 | World lore details, bases, and locations (e.g. Trấn Hi Vọng). |
| **Unavailable / Out-of-Scope** | 5 | Future chapters or real-world off-topic questions. (Acceptable abstain = True). |
| **Adversarial / Ambiguous** | 5 | Prompt injections, typo-ridden names, and spoiler-baiting questions. |

---

## Schema Reference

Each benchmark case conforms to the following schema:
- `case_id`: Unique string ID.
- `category`: Category string.
- `question`: The input query string.
- `chapter_progress`: The maximum chapter reader is allowed to view (clamping progress).
- `explicit_target_chapter`: Target chapter if asking about a specific chapter summary.
- `allowed_chapter_range`: List of chapters containing the evidence.
- `expected_chunk_refs`: List of chunk identifiers expected to be retrieved.
- `required_facts`: Substrings that must be present in the correct answer.
- `optional_facts`: Substrings that may be present.
- `forbidden_facts`: Substrings that must NOT be present (to prevent hallucination/spoilers).
- `important_event_clusters`: Critical events that must be covered.
- `acceptable_abstain`: Boolean if the bot is allowed to say it doesn't know.
- `human_reference_answer`: Human-written golden standard answer.
- `reference_author`: Creator of reference.
- `reference_method`: Method of reference acquisition.
