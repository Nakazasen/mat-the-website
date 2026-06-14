# Phase 11F-3B Pro V2 Gold Integrity Seal

## 1. Lineage and Checksums
- **Locked V1 Checksum:** `510DF8FB91E6C9548517F74D3C2508D8A755229F0639ADC619ECA5D191B4A278`
- **Frozen Run 1 Checksum:** `62D29F973E072BEAFDCC7520D66697918FB0CA3F85841BE328E85F27870A639A`
- **Rejected Flash V2 Checksum:** `35D2378537B36E13734CA2C406A43DC1131F332C8A94A1AB908146E1546F2414`
- **New Pro V2 Checksum:** `E767B2FFF126FB7DD32011BE34F156DE9A2C59EBC4C8206A443677791163947B`

## 2. Review Methodology
An independent semantic review of the 32 disputed facts against the offline chapter source data. No automated naive string matching was used for validation. V2 was constructed directly from the locked V1 base to ensure zero contamination from Flash's rejected outputs.

## 3. Disputed Fact Adjudication
- **Invalid Confirmed (15):** sum-07 (thây ma cấp 6), sum-14 (Thượng Quan Uyển Thanh), sum-14 (phương án), char-02 (thư ký), char-05 (Hồ Hán Thương), char-05 (Bình An), char-07 (Nhà Khí Tượng Học), event-03 (Cổ Chính), event-03 (level 3), event-04 (nhất giai), event-10 (vòng phòng hộ), event-10 (dọn sạch thảm thực vật), loc-04 (căn cứ), loc-04 (người sống sót)
- **Supported Restored (14):** sum-01 (khất nợ), sum-07 (hiểm cảnh), char-01 (nhân vật chính), char-01 (thường dân), char-01 (hệ băng), char-02 (giải cứu), char-03 (bị kết liễu), char-05 (bị cắn), char-08 (trộm trứng), event-08 (trộm trứng), loc-01 (nơi làm việc), adv-01 (trộm trứng), adv-03 (Chương 830), adv-03 (trộm trứng), adv-04 (hệ băng)
- **Partial (2):** event-07 (băng kiếm -> downgraded to optional), loc-01 (tận thế -> downgraded to soft only)
- **Ambiguous (1):** event-08 (noãn thất -> downgraded to soft only)

## 4. Final Counts & Scoring Changes
- **Total Facts:** 138
- **Unjustified Scoring Changes Reversed:** 15
- **Genuinely Manually Reviewed:** 32 (by Pro)

## 5. V2 Integrity Tests
- Integrity tests executed via `pytest backend/tests/test_chapter_bot_quality_benchmark_loader.py` passed with 100% success.
- Checked: 50 cases, exact IDs preserved, structural integrity identical to V1.

## 6. Offline Re-analysis
- **Official V1 Score (>=2):** 68.00%
- **Pro V2 Required Fact Recall:** 67.81%
- **Pro V2 Optional Fact Recall:** 51.61%
- **Cases Penalized Solely by Invalid Facts:** 3
- **Real Generation Failure Cases:** 20
- **Verifier False Accepts:** 16

## 7. Recomputed Root Causes
- **DRAFT_OMITTED_SUPPORTED_FACTS:** 15
- **VERIFIER_REQUIRED_COMPLETENESS_FALSE_ACCEPT:** 16
- **VERIFIER_OPTIONAL_COMPLETENESS_MISS:** 4
- **ACCEPTABLE_SCORE2:** 7
- **DRAFT_UNSUPPORTED_CLAIM:** 1
- **DRAFT_CONTRADICTION:** 1
- **RETRIEVAL_WRONG_CHAPTER:** 1
- **RETRIEVAL_RIGHT_CHAPTER_WRONG_CHUNKS:** 2
- **GOLD_REFERENCE_DEFECT:** 3

## 8. Targeted Repair Set
A maximum of 12 cases curated at `backend/evals/phase11f3b_targeted_repair_cases_pro_reviewed.json` containing:
- 6 required omission cases
- 2 unsupported claim cases
- 2 verifier false accepts
- 1 right-chapter/wrong-chunk failure
- 1 wrong-chapter failure

## 9. Deployment Status
- **Production Code Changed:** No
- **Live Model Calls:** 0
- **Commit:** NOT_PERFORMED
- **Push:** NOT_PERFORMED
- **Deploy:** NOT_AUTHORIZED

## 10. Master Progress
- **Master Phase 4:** 55–60%
- **Overall Super RAG:** 45–47%
