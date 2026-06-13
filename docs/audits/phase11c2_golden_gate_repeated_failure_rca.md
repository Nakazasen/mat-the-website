# Phase 11C-2-FIX1 — Infra-Aware Warm-up, Retry, and Failure Classification Report

## 1. Classification
**PASS_PHASE_11C2_FIX1_INFRA_AWARE_GOLDEN_GATE**

## 2. Root Cause Cũ (Phát hiện từ RCA)
- **Render Free Tier Cold-Start**: Backend Render tự động ngủ sau 15 phút không hoạt động.
- **Workflow schedule mỗi 6 giờ**: Khi workflow kích hoạt, Render backend chắc chắn đang ngủ.
- **HTTP Timeout cứng 20s**: Script runner gọi API kiểm thử và cấu hình timeout cứng 20 giây, thấp hơn thời gian backend khởi động lại (cold-start) từ 30 đến 50 giây. Do đó, request đầu tiên luôn bị lỗi timeout (`The read operation timed out`), làm hỏng runner với exit code 1.

## 3. Files Changed (Danh sách các file thay đổi/thêm mới)
- [NEW] [warm_up_oracle_backend.py](file:///d:/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/scripts/warm_up_oracle_backend.py): Script thực hiện đánh thức backend bằng cách ping `/api/health`.
- [NEW] [test_oracle_backend_warmup.py](file:///d:/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/tests/test_oracle_backend_warmup.py): Bộ kiểm thử độc lập cho tính năng warm-up.
- [MODIFY] [.github/workflows/golden-oracle-regression.yml](file:///d:/Sandbox/Web_matthesinhhoanguyco/mat-the-website/.github/workflows/golden-oracle-regression.yml): Tích hợp bước warm-up trước kiểm thử.
- [MODIFY] [run_golden_oracle_regression_cases.py](file:///d:/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/scripts/run_golden_oracle_regression_cases.py): Bổ sung cơ chế retry, phân loại lỗi và cấu hình timeout.
- [MODIFY] [test_oracle_regression_runner.py](file:///d:/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/tests/test_oracle_regression_runner.py): Mở rộng bộ unit tests để kiểm tra retry và exit codes.
- [MODIFY] [phase11c2_golden_gate_repeated_failure_rca.md](file:///d:/Sandbox/Web_matthesinhhoanguyco/mat-the-website/docs/audits/phase11c2_golden_gate_repeated_failure_rca.md): Cập nhật báo cáo RCA và kiểm chứng sửa lỗi.

## 4. Warm-up Behavior (Hành vi của bước khởi động backend)
- Script warm-up sẽ gửi HTTP GET đến `/api/health` của môi trường đích.
- Hỗ trợ các tham số: `--attempts` (mặc định 5), `--timeout` (mặc định 90s), `--backoff-seconds` (mặc định 10s).
- Chỉ coi là thành công khi HTTP Status trả về là 200 và JSON chứa `"status": "ok"`.
- Ghi nhật ký đầy đủ về số attempt, độ trễ và git commit của production.
- Nếu warm-up thất bại sau khi hết số lần retry, script kết thúc với exit code 2 (infra_failure), làm dừng workflow ngay lập tức trước khi chạy bước kiểm thử ngữ nghĩa tiếp theo.

## 5. Retry Conditions (Các điều kiện kích hoạt Retry lỗi hạ tầng)
Runner chỉ thực hiện retry khi gặp các lỗi hạ tầng tạm thời:
- Gặp ngoại lệ timeout (`socket.timeout`, `TimeoutError`, hoặc nội dung thông điệp có chứa "timed out").
- Lỗi mạng hoặc ngắt kết nối (`ConnectionRefusedError`, `ConnectionResetError`, `URLError`, v.v.).
- Nhận phản hồi HTTP Status thuộc nhóm lỗi tạm thời/quá tải: `429`, `502`, `503`, `504`.

## 6. Những lỗi KHÔNG được Retry
Runner tuyệt đối không retry và kết luận kết quả kiểm thử thất bại ngay lập tức đối với:
- Phản hồi HTTP 200 bình thường nhưng vi phạm các ràng buộc ngữ nghĩa (chứa forbidden terms, forbidden patterns).
- Hệ thống bị lộ raw system tag (`[DỮ LIỆU HỆ THỐNG]`).
- Thiếu các required terms mong muốn trong câu trả lời.
- Expected abstain text không khớp.
- Lỗi cấu hình dữ liệu đầu vào hoặc case schema không hợp lệ.
- Không có case hoạt động nào (`total active cases = 0`).

## 7. Failure Classes và Exit Codes
Hệ thống sử dụng các exit code chuẩn để báo cáo rõ nguyên nhân lỗi:
- **`0`**: Thành công. Toàn bộ các kiểm thử ngữ nghĩa đều PASS.
- **`1`** (`semantic_failure`): Lỗi hồi quy ngữ nghĩa thật (Semantic Regression).
- **`2`** (`infra_failure`): Lỗi hạ tầng (Timeout, lỗi kết nối hoặc HTTP error 503/429/500 sau khi hết lượt retry).
- **`3`** (`configuration_failure`): Lỗi cấu hình (Không có case nào hoạt động, lỗi schema JSON đầu vào, hoặc lỗi Supabase DB connection).

## 8. Kết quả chạy Tests local
Tất cả 401 test của dự án đều vượt qua thành công:
```
backend/tests/test_oracle_regression_runner.py: 13 passed
backend/tests/test_oracle_backend_warmup.py: 4 passed
Tổng cộng: 401 passed, 3 warnings in 9.12s
```

## 9. Production/Manual Workflow Run ID
- **Run ID**: `27450575463`
- **Link**: https://github.com/Nakazasen/mat-the-website/actions/runs/27450575463
- **Kết quả**: Thành công tuyệt đối (`success`).

## 10. Artifact và Step Summary Result
- **Report Artifact**: `golden-regression-report` kích thước 815 bytes được tạo và tải lên thành công.
- **Nội dung Artifact**: Chứa đầy đủ các thuộc tính phân loại lỗi mới như `failure_class`, `attempts`, `http_statuses`, `attempt_latencies_ms`, `production_git_commit`, v.v.
- **Step Summary**: Đã in bảng chi tiết trực quan lên giao diện GitHub Actions qua `$GITHUB_STEP_SUMMARY` hiển thị trạng thái từng case và phân loại lỗi rõ ràng.

## 11. Node.js Deprecation Warning
- **Xác định**: Cảnh báo do GitHub Actions runner hiển thị đối với `actions/checkout@v4`, `actions/setup-python@v5`, và `actions/upload-artifact@v4`.
- **Xử lý**: Trì hoãn xử lý (deferred) vì đây là các cảnh báo nền tảng không chặn thực thi và không phải root cause làm fail job.

## 12. Commit Hash
- **Commit SHA**: `7c24638508963b3cae1a4fd5261a38ea6d7aa8fb` (Cập nhật tiếp theo sau commit báo cáo này).

## 13. Xác nhận Ràng buộc
- Xác nhận cổng kiểm thử ngữ nghĩa Oracle (Semantic Gate) vẫn hoạt động chế độ **fail-closed** khi phát hiện hồi quy thật.
- Không cấu hình runner luôn thoát code 0 để trốn lỗi.
- Không sửa cơ sở dữ liệu production.
- Không chỉnh sửa wiki_entries hoặc provisional_library.
- Không làm lộ bất kỳ secret hoặc token bảo mật nào.

## 14. Kế hoạch tiếp theo
- Sau khi cổng CI/CD kiểm thử Oracle regression gate đã hoạt động ổn định và chính xác, quay lại thực hiện tiếp Phase 11E-SEC1 liên quan đến trust và security.
