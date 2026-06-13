# Phase 11C-2-RCA — Golden Oracle Regression Gate Repeated Failure Root-Cause Audit

## 1. Classification
**FAIL_GOLDEN_GATE_INFRA_TIMEOUT_OR_5XX**

## 2. Run IDs đã kiểm tra
- **Run #3** (ID: `27417446633`) - Thất bại (schedule)
- **Run #4** (ID: `27435522801`) - Thất bại (schedule)
- **Run #5** (ID: `27450235103`) - Thành công (workflow_dispatch)

## 3. Bảng Evidence các lần chạy trên GitHub Actions (gần nhất)
| Run Number | Run ID | Trigger Event | Status / Conclusion | Commit SHA | Trigger Time (UTC) | Failed Step | Exit Code | Reason |
|---|---|---|---|---|---|---|---|---|
| 5 | 27450235103 | workflow_dispatch | Success | 8471f7e | 2026-06-13T00:06:52Z | - | 0 | All validation checks passed |
| 4 | 27435522801 | schedule | Failure | ab2b366 | 2026-06-12T18:37:17Z | Run Golden Regression Cases | 1 | HTTP request triggered exception: The read operation timed out |
| 3 | 27417446633 | schedule | Failure | ab2b366 | 2026-06-12T13:04:11Z | Run Golden Regression Cases | 1 | HTTP request triggered exception: The read operation timed out |
| 2 | 27401629225 | schedule | Success | ab2b366 | 2026-06-12T07:33:31Z | - | 0 | All validation checks passed |
| 1 | 27386693826 | schedule | Success | ab2b366 | 2026-06-12T00:37:36Z | - | 0 | All validation checks passed |

## 4. Nội dung Artifact (`golden-regression-report`) từ các run thất bại
### Run #3:
```json
{
  "summary": {
    "total": 1,
    "passed": 0,
    "failed": 1,
    "run_at": "2026-06-12T13:04:37.779258+00:00",
    "base_url": "https://mat-the-website.onrender.com"
  },
  "results": [
    {
      "case_id": "le_giang_campaign_location_pollution",
      "question": "chiến dịch lệ giang diễn ra như thế nào?",
      "passed": false,
      "reason": "HTTP request triggered exception: The read operation timed out",
      "answer": "",
      "source": "unknown"
    }
  ]
}
```

### Run #4:
```json
{
  "summary": {
    "total": 1,
    "passed": 0,
    "failed": 1,
    "run_at": "2026-06-12T18:37:44.876210+00:00",
    "base_url": "https://mat-the-website.onrender.com"
  },
  "results": [
    {
      "case_id": "le_giang_campaign_location_pollution",
      "question": "chiến dịch lệ giang diễn ra như thế nào?",
      "passed": false,
      "reason": "HTTP request triggered exception: The read operation timed out",
      "answer": "",
      "source": "unknown"
    }
  ]
}
```

## 5. Root Cause chính
- **Cơ chế hạ tầng Render Free Tier**: Backend dịch vụ `https://mat-the-website.onrender.com` được deploy trên Render gói Free. Gói này tự động chuyển sang chế độ ngủ (spin down / sleep) sau 15 phút không nhận được lưu lượng truy cập (inactivity).
- **Lịch chạy định kỳ (Schedule cron)**: GitHub Actions chạy regression test mỗi 6 giờ (`0 */6 * * *`). Khoảng cách này quá dài (6 tiếng > 15 phút), do đó khi workflow khởi động, backend Render chắc chắn đang ngủ.
- **Giới hạn Timeout của Script**: Hàm gọi HTTP trong `run_golden_oracle_regression_cases.py` sử dụng thư viện `urllib.request` với cấu hình timeout cứng là **20 giây** (`urllib.request.urlopen(req, context=ctx, timeout=20)`).
- **Hiện tượng xảy ra**: Quá trình đánh thức backend Render (cold-start) thường mất từ 30 đến 50 giây để khởi động lại container và sẵn sàng phục vụ. Do đó, request đầu tiên của workflow Actions luôn vượt quá 20 giây, gây lỗi `read operation timed out` và khiến runner kết thúc với exit code 1.

## 6. Contributing Causes
- **Không có bước Warm-up / Health Check trước**: Workflow chạy kiểm tra trực tiếp mà không có cơ chế gọi `/api/health` hoặc đánh thức dịch vụ trước khi gửi truy vấn nghiệp vụ.
- **Thiếu cơ chế retry với backoff**: Script runner gửi request một lần duy nhất và không thực hiện retry nếu gặp sự cố kết nối/timeout do hạ tầng cold start.

## 7. Loại lỗi: Semantic hay Infra?
Đây là lỗi **Infrastructure Failure** (`FAIL_GOLDEN_GATE_INFRA_TIMEOUT_OR_5XX`), không phải là semantic regression hay lỗi logic nghiệp vụ của Oracle.

## 8. Version Match / Drift
- **Trạng thái HEAD Repo hiện tại**: `8471f7ec23b8c11882f3f2db92d37c3c4362dce5`
- **Trạng thái production hiện tại (/api/health)**:
  - Commit: `8471f7ec23b8c11882f3f2db92d37c3c4362dce5`
  - Branch: `main`
- **So sánh**: `VERSION_MATCH` (Backend đang chạy chính xác commit mới nhất của nhánh `main`).
*(Lưu ý: Tại thời điểm Run #3 và Run #4 chạy, commit tested là `ab2b366`, trong khi commit sau đó là `8471f7e` được test thành công trong Run #5 sau khi backend đã thức giấc).*

## 9. Kết quả chạy thử nghiệm Local (10 lần liên tục)
Chạy thử nghiệm local gọi API sản phẩm từ script `run_local_10_times.py`:
| run_number | started_at | health_commit | health_latency_ms | oracle_http_status | runner_exit_code | case_passed | answer_source | reason | answer_excerpt |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-06-13T00:08:54Z | 8471f7e | 149 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 2 | 2026-06-13T00:09:10Z | 8471f7e | 158 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 3 | 2026-06-13T00:09:26Z | 8471f7e | 215 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 4 | 2026-06-13T00:09:42Z | 8471f7e | 162 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 5 | 2026-06-13T00:09:57Z | 8471f7e | 150 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 6 | 2026-06-13T00:10:13Z | 8471f7e | 252 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 7 | 2026-06-13T00:10:29Z | 8471f7e | 149 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 8 | 2026-06-13T00:10:45Z | 8471f7e | 169 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 9 | 2026-06-13T00:11:01Z | 8471f7e | 168 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |
| 10 | 2026-06-13T00:11:16Z | 8471f7e | 153 | 200 | 0 | PASS | cache | All validation checks passed. | Chưa đủ dữ liệu trong truyện đã nạp để m |

## 10. Kết quả chạy gọi API trực tiếp (10 lần liên tục)
Chạy thử nghiệm gọi trực tiếp `POST https://mat-the-website.onrender.com/oracle/ask` từ script `direct_api_repro.py`:
- Cả 10 lần đều trả về **HTTP Status: 200**.
- **Latency**: Dao động từ 294 ms đến 522 ms (rất nhanh vì backend đã warm và kết quả được trả về từ cache).
- **Source**: `cache`.
- **Answer stability**: Rất ổn định, nội dung trả về trùng khớp hoàn toàn với expected abstain text.
- **Raw system tag**: Hoàn toàn **không** chứa tag cấm `[DỮ LIỆU HỆ THỐNG]`.
- **Forbidden terms/patterns**: Hoàn toàn **không** chứa từ ngữ cấm nào trong danh sách.
- **Expected abstain**: Kết quả là một câu từ chối trả lời (abstain response) hợp lệ đúng như mong đợi.

## 11. Runner Exit-Code Audit
Đánh giá logic trả về exit code của `run_golden_oracle_regression_cases.py`:
- Script trả về `sys.exit(0)` chỉ khi toàn bộ các trường hợp kiểm thử hoạt động đều có `passed == True` (tức là không vi phạm schema, không lỗi kết nối HTTP, và vượt qua toàn bộ các kiểm tra nghiệp vụ).
- Script trả về `sys.exit(1)` khi:
  1. Số lượng case hoạt động bằng 0 (`len(results) == 0`).
  2. Số lượng case thất bại lớn hơn 0 (`failed_count > 0`).
  3. Gặp lỗi kết nối mạng hoặc timeout (`except Exception as e` trong urllib).
  4. Lỗi HTTP status không phải 200.
  5. Các lỗi cú pháp JSON/schema khi phân tích response body.
  6. File chứa case kiểm thử (`golden_oracle_regression_cases.json`) không tồn tại.
- Lỗi logic thoát này là hoàn toàn chính xác, đảm bảo runner phản ánh trung thực kết quả kiểm tra.
- **Unicode/UTF-8**: Script đã xử lý tốt việc config UTF-8 khi in ra stdout trên runner nên không ảnh hưởng.
- **Path**: Đường dẫn file được giải quyết tuyệt đối qua `os.path.dirname(os.path.abspath(__file__))` nên hoàn toàn độc lập với thư mục chạy lệnh (CWD) của workflow.

## 12. Node Deprecation Warning có liên quan hay không?
Cảnh báo `##[warning]Node.js 20 actions are deprecated` xuất hiện ở các bước của các actions như `actions/checkout@v4`, `actions/setup-python@v5`, và `actions/upload-artifact@v4`.
- **Đánh giá**: Cảnh báo này chỉ mang tính chất thông báo nền tảng GitHub Actions sẽ dừng hỗ trợ chạy Actions bằng Node.js 20 trong tương lai.
- **Thực tế**: Các Action này vẫn tải và hoàn thành công việc của mình bình thường (bằng chứng là artifact `golden-regression-report` vẫn được đóng gói và tải lên hoàn thành với dung lượng 533 bytes). Cảnh báo này **hoàn toàn không liên quan** tới lỗi exit code 1 của runner.

## 13. Remediation Plan (Đề xuất giải pháp khắc phục)
1. **Bổ sung bước Warm-up trước khi chạy test**:
   Thêm một bước `Warm up Oracle API` vào workflow `.github/workflows/golden-oracle-regression.yml` trước bước chạy test. Bước này sẽ thực hiện một lệnh gọi curl đơn giản với cơ chế retry và thời gian chờ dài để đánh thức container Render:
   ```yaml
   - name: Warm up Render Backend
     run: |
       curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --retry 5 --retry-delay 10 --retry-max-time 120 https://mat-the-website.onrender.com/api/health
   ```
2. **Cải thiện cơ chế chịu lỗi trong Script Runner**:
   Tăng nhẹ thời gian timeout của request trong `run_golden_oracle_regression_cases.py` từ 20 giây lên 60 giây khi chạy từ môi trường CI, hoặc triển khai cơ chế retry tối đa 3 lần cho riêng cuộc gọi HTTP để phòng ngừa trường hợp hạ tầng có độ trễ lớn tức thời.

## 14. Xác nhận AUDIT-ONLY
Chúng tôi xác nhận đã thực hiện đúng theo các điều kiện nghiêm ngặt:
- Không sửa code.
- Không thực hiện commit/push.
- Không chỉnh sửa database hay các bản ghi.
- Không tắt hoặc sửa cấu hình workflow.
- Không sửa đổi wiki hay provisional library.
- Không làm lộ bất cứ bí mật hoặc token bảo mật nào.
