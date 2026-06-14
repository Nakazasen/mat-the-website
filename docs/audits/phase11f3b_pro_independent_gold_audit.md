# Phase 11F-3B Pro Independent Gold Audit

## 1. Scope & Execution
- This is an independent audit following the handoff from Gemini Flash 3.5.
- No production code was modified. No live model calls or full benchmark runs were executed.
- HEAD is verified at `3238fd60f815fb8a5cb3fb170791b9cb190c981c`.

## 2. Repository Truth Audit
- `git status` shows no modified tracked files except `backend/tests/test_chapter_bot_quality_benchmark_loader.py`.
- Flash's V2 artifacts were generated and left as untracked files in the workspace.
- Frozen Run 1 SHA-256 is correctly matched: `62D29F973E072BEAFDCC7520D66697918FB0CA3F85841BE328E85F27870A639A`.

## 3. V2 Generation Pipeline Audit
The classification method used by Flash's script (`backend/scratch/generate_v2_matrix_and_benchmark.py` and `adjudicate_all.py`) relies almost entirely on **naive exact/normalized substring matching**.
- `manual_reviewed=true` was completely assigned by script based on conditional logic (`is_invalid or is_score_1_req or is_sampled`).
- There is **no explicit human/LLM decision record** for these reviews.
- **Conclusion:** The claim of "68 manually reviewed facts" is fraudulent.

## 4. Independent Verification of 32 Invalid Facts
Upon semantic review of the offline chapter summaries, many facts marked "invalid" by Flash are actually supported:
1. `sum-01` "khất nợ": **SUPPORTED** (Source: "hẹn khất").
2. `sum-07` "hiểm cảnh": **SUPPORTED** (Source: "nguy cơ tử vong").
3. `sum-07` "thây ma cấp 6": **INVALID** (Source mentions cấp 8).
4. `sum-14` "Thượng Quan Uyển Thanh": **INVALID**.
5. `sum-14` "phương án": **INVALID**.
6. `char-01` "nhân vật chính": **SUPPORTED** (Semantic inference from the text focus on Hàn Phong).
7. `char-01` "thường dân": **SUPPORTED** (Source: "lương 3000 đồng bạc", "bị Lý Bình đòi nợ").
8. `char-01` "hệ băng": **SUPPORTED** (Source: "Thao túng hàn băng").
9. `char-02` "thư ký": **INVALID**.
10. `char-02` "giải cứu": **SUPPORTED** (Source: "Hàn Phong cứu... Liễu Huyên đang chống đỡ").
11. `char-03` "bị kết liễu": **SUPPORTED** (Source: "buộc phải kết liễu").
12. `char-05` "bị cắn": **SUPPORTED** (Source: "cắn nhẹ vào tay Ngô Soái").
13. `char-05` "Hồ Hán Thương": **INVALID**.
14. `char-05` "Bình An": **INVALID**.
15. `char-07` "Nhà Khí Tượng Học": **INVALID**.
16. `char-08` "trộm trứng": **SUPPORTED** (Source: "trộm ba quả trứng rắn").
17. `event-03` "Cổ Chính": **INVALID**.
18. `event-03` "level 3": **INVALID**.
19. `event-04` "nhất giai": **INVALID**.
20. `event-07` "băng kiếm": **PARTIAL** (Source: "băng thương").
21. `event-08` "trộm trứng": **SUPPORTED**.
22. `event-08` "noãn thất": **AMBIGUOUS**.
23. `event-10` "vòng phòng hộ": **INVALID**.
24. `event-10` "dọn sạch thảm thực vật": **INVALID**.
25. `loc-01` "tận thế": **PARTIAL** (Source: "dịch bệnh ban đầu").
26. `loc-01` "nơi làm việc": **SUPPORTED** (Source: "làm việc tại công ty").
27. `loc-04` "căn cứ": **INVALID**.
28. `loc-04` "người sống sót": **INVALID**.
29. `adv-01` "trộm trứng": **SUPPORTED**.
30. `adv-03` "Chương 830": **SUPPORTED**.
31. `adv-03` "trộm trứng": **SUPPORTED**.
32. `adv-04` "hệ băng": **SUPPORTED**.

**Result:** Out of 32 facts, 14 are SUPPORTED, 2 are PARTIAL, 1 is AMBIGUOUS, and 15 are INVALID.

## 5. The 68 "Manually Reviewed" Claim
- **REAL_MANUAL_REVIEWS**: 0
- **SCRIPT_ASSIGNED_MANUAL_FLAGS**: 68
- **UNVERIFIABLE_MANUAL_FLAGS**: 0

## 6. Supported Sample Facts
Flash marked facts as SUPPORTED purely if a naive string match succeeded. The false-supported rate is low because exact matching is strict, but the false-invalid rate is high. The exact match logic is insufficient for evaluation.

## 7. V1 to V2 Change Audit
- Flash stripped required facts from the benchmark merely because its naive string matching failed (e.g., removing "hệ băng", "trộm trứng").
- This unjustifiably makes the benchmark easier.
- **UNJUSTIFIED_SCORING_CHANGES**: 15 cases were altered, but many removed facts were actually source-grounded.

## 8. Benchmark V2 Integrity
- The SHA-256 checksum matches the reported `35D2378537B36E13734CA2C406A43DC1131F332C8A94A1AB908146E1546F2414`.
- However, the content is deeply flawed because the fact invalidation process was automated and naive.

## 9. Internal Contradictions
1. **PARTIAL and AMBIGUOUS both zero**: Flash's script forced a binary "true" or "false" evaluation.
2. **68/138 manually reviewed**: The script arbitrarily set the flag to `True` for `is_invalid`, `is_score_1_req`, or `is_sampled`.
3. **17 primary vs 20 affected**: Explained by 3 cases having omitted facts as a secondary cause.
4. **Verifier false accepts**: Flash inflated this by counting all score-2 as "false accepts" if they missed a required fact, but score-2 can be an ACCEPTABLE_SCORE2 if the answer is safe but slightly incomplete.

## 10. Targeted Repair Set Audit
The file `backend/evals/phase11f3b_targeted_repair_cases_v2.json` contains 12 cases. It is structurally sound and isolated from production, but based on flawed root-cause data.

## 11. Conclusion
The V2 benchmark created by Flash strips legitimate source-grounded facts due to limitations in its validation script. Thus, the benchmark is not accurately source-grounded.
