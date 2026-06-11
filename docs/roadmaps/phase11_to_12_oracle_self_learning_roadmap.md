# Lộ Trình Phát Triển Hệ Thống Tự Học AI Oracle (Phase 11 & 12 Self-Learning Roadmap)

Lộ trình này vạch ra các giai đoạn phát triển tuần tự từ **Phase 11B** đến **Phase 12F** nhằm xây dựng hệ thống tự học hướng AGI (AGI-like Self-Learning System) hoàn chỉnh, thực tế và kiểm chứng được.

---

## Giai Đoạn 11: Ổn Định Runtime, Phân Loại & Đánh Giá Hồi Quy (Verification & Quality Assurance)

### Phase 11B — Production Runtime Truth Gate
* **Mục tiêu**: Ngăn chặn rác lọt vào ngữ cảnh Oracle ở runtime bằng cách lọc nghiêm ngặt các thực thể dựa trên từ khóa câu hỏi chính xác và loại bỏ các thực thể bị cấm/gắn cờ lỗi.
* **Files likely affected**: `backend/routes/ai_oracle.py`, `backend/rag/retrieval.py`
* **DB migration**: Không cần.
* **Test bắt buộc**: Unit test lọc thực thể dựa trên câu hỏi Lệ Giang (đảm bảo không còn Trấn Hi Vọng, Zombie Cấp 3).
* **Production smoke bắt buộc**: `POST /oracle/ask` với câu hỏi Lệ Giang trả về 200 và zero forbidden terms.
* **Rủi ro**: Lọc quá chặt làm mất đi một số context hữu ích nếu người dùng viết sai chính tả.
* **Kế hoạch khôi phục (Rollback plan)**: `git checkout HEAD~1 backend/routes/ai_oracle.py`.

### Phase 11C — Golden Regression Memory from Feedback
* **Mục tiêu**: Tự động chuyển đổi các feedback đã sửa đổi (resolved) thành các ca test hồi quy (Golden Tests) lưu trong DB để đảm bảo cập nhật mã nguồn không làm lỗi cũ lặp lại.
* **Files likely affected**: `backend/scripts/oracle_self_learning_regression_pack.py`, `backend/models/regression.py`
* **DB migration**: Tạo bảng `oracle_regression_tests` lưu: `question`, `chapter_progress`, `expected_signature`, `forbidden_terms`.
* **Test bắt buộc**: Chạy gói kiểm thử hồi quy tự động đọc từ DB.
* **Production smoke bắt buộc**: Cron chạy regression pack kiểm tra 100% các case cũ đạt kết quả PASS trên production.
* **Rủi ro**: Dữ liệu cốt truyện thay đổi ở chương mới làm sai lệch kỳ vọng của Golden Test cũ.
* **Kế hoạch khôi phục (Rollback plan)**: Cho phép cờ `active` trong bảng regression để tắt/bật nhanh từng test case.

### Phase 11D — Intent Router V2
* **Mục tiêu**: Sử dụng LLM phân loại ý định câu hỏi (Entity lookup vs Event/Plot progression vs Chapter summary) thay vì chỉ dùng regex cứng, giúp RAG nạp đúng loại context.
* **Files likely affected**: `backend/rag/retrieval.py`, `backend/routes/ai_oracle.py`
* **DB migration**: Không cần.
* **Test bắt buộc**: Chạy test phân loại ý định của 50 câu hỏi mẫu (đạt độ chính xác > 95%).
* **Production smoke bắt buộc**: Độc giả hỏi câu diễn biến chương trả về tóm tắt chương; hỏi nhân vật trả về thông tin nhân vật.
* **Rủi ro**: Tăng độ trễ (latency) của câu trả lời do phải chạy thêm một bước phân loại qua LLM.
* **Kế hoạch khôi phục (Rollback plan)**: Fallback về regex classifier nếu LLM router lỗi hoặc phản hồi chậm (> 2s).

### Phase 11E — Evidence-first Answer Engine
* **Mục tiêu**: Oracle chỉ khẳng định thông tin khi có bằng chứng (evidence) và đính kèm số chương tham chiếu. Tự động từ chối (abstain) trả lời nếu độ tự tin của context RAG dưới ngưỡng.
* **Files likely affected**: `backend/routes/ai_oracle.py`, `backend/prompts/oracle_prompts.py`
* **DB migration**: Không cần.
* **Test bắt buộc**: Hỏi câu không có trong cốt truyện, đảm bảo Oracle trả "Dữ liệu chưa đủ giải mã" và không bịa đặt.
* **Production smoke bắt buộc**: Hỏi "Hàn Phong ăn lẩu chương nào?" phải trả về tham chiếu "Chương 820".
* **Rủi ro**: Độc giả cảm thấy Oracle quá cứng nhắc và từ chối trả lời nhiều câu hỏi suy diễn.
* **Kế hoạch khôi phục (Rollback plan)**: Điều chỉnh prompt template để hạ thấp hoặc nâng cao ngưỡng từ chối trả lời.

### Phase 11F — Library Self-Curation Engine
* **Mục tiêu**: Tự động làm sạch thư viện provisional: gộp thực thể trùng lặp (duplicate detection), chuẩn hóa loại thực thể (type normalization), và loại bỏ rác.
* **Files likely affected**: `backend/scripts/normalize_provisional_library_types.py`, `backend/scripts/rank_provisional_library.py`
* **DB migration**: Không cần.
* **Test bắt buộc**: Test gộp hai thực thể "zombie cấp 3" và "zombie cap 3" thành một thực thể chuẩn.
* **Production smoke bắt buộc**: Dashboard thư viện giảm số lượng bản ghi ảo và không còn bản ghi trùng lặp.
* **Rủi ro**: Xóa nhầm các thực thể có tên gần giống nhau nhưng là hai đối tượng khác nhau.
* **Kế hoạch khôi phục (Rollback plan)**: Lưu vết lịch sử thay đổi (changelog) để có thể khôi phục lại trạng thái cũ.

### Phase 11G — Author Feedback Priority
* **Mục tiêu**: Ưu tiên tuyệt đối phản hồi từ Tác giả/Admin. Khi Admin gửi feedback sửa chữa, patch được sinh và áp dụng lập tức ở chế độ `active` mà không cần kiểm duyệt số lượng hay cron.
* **Files likely affected**: `backend/routes/ai_oracle.py`, `backend/scripts/run_oracle_answer_feedback_pipeline.py`
* **DB migration**: Thêm trường `is_admin_author` vào bảng `rag_feedback`.
* **Test bắt buộc**: Test tạo patch lập tức khi feedback được gắn cờ admin.
* **Production smoke bắt buộc**: Admin sửa câu trả lời trên UI, hỏi lại câu đó thấy kết quả cập nhật ngay lập tức.
* **Rủi ro**: Admin gõ sai lỗi chính tả sẽ trực tiếp làm sai lệch câu trả lời cho toàn bộ người dùng ngay lập tức.
* **Kế hoạch khôi phục (Rollback plan)**: Cung cấp giao diện rollback patch một chạm (one-click rollback) cho Admin.

### Phase 11H — Self-Healing Cache & Deploy Version Proof
* **Mục tiêu**: Tự động xóa cache của các câu hỏi liên quan ngay khi patch mới được kích hoạt hoặc khi có chương mới được xuất bản. Đảm bảo version proof hiển thị build time chính xác.
* **Files likely affected**: `backend/routes/ai_oracle.py`, `backend/security_utils.py`
* **DB migration**: Không cần.
* **Test bắt buộc**: Viết test giả lập lưu cache, kích hoạt patch, và xác nhận cache bị invalidate tự động.
* **Production smoke bắt buộc**: Deploy bản vá mới, kiểm tra cache của câu hỏi bị xóa lập tức mà không cần xóa tay.
* **Rủi ro**: Xóa cache quá nhiều làm tăng tải cho LLM API.
* **Kế hoạch khôi phục (Rollback plan)**: Giới hạn tần suất xóa cache (rate-limit cache invalidation).

### Phase 11I — Continuous Learning Dashboard
* **Mục tiêu**: Cải tiến dashboard hiển thị trạng thái trung thực: hiển thị số lượng ca test hồi quy đang chạy trên production, số bản vá đang hoạt động, tỷ lệ phản hồi chính xác thực tế.
* **Files likely affected**: `frontend/src/app/admin/dashboard/page.tsx` (hoặc tương đương)
* **DB migration**: Tạo bảng thống kê hiệu năng hàng ngày `oracle_telemetry_daily`.
* **Test bắt buộc**: Chạy kiểm tra tích hợp dữ liệu dashboard.
* **Production smoke bắt buộc**: Admin dashboard hiển thị chính xác kết quả của phiên kiểm thử hồi quy gần nhất từ production.
* **Rủi ro**: Lộ thông tin nhạy cảm của hệ thống giám sát.
* **Kế hoạch khôi phục (Rollback plan)**: Phân quyền xem dashboard chỉ cho Admin/Tác giả.

### Phase 11J — Oracle Research Mode
* **Mục tiêu**: Độc giả có thể kích hoạt "Research Mode" để Oracle thực hiện truy vấn đa bước (multi-step search) trên toàn bộ database cốt truyện để trả lời các câu hỏi phức tạp về dòng thời gian hoặc các sự kiện chồng chéo.
* **Files likely affected**: `backend/routes/ai_oracle.py`, `backend/rag/retrieval.py`
* **DB migration**: Không cần.
* **Test bắt buộc**: Test truy vấn tìm mối quan hệ giữa 3 nhân vật xuất hiện cách nhau 300 chương.
* **Production smoke bắt buộc**: Chọn chế độ Research Mode, Oracle phản hồi kèm theo sơ đồ phân tích các chương liên quan.
* **Rủi ro**: Chi phí token LLM tăng cao do phải chạy nhiều câu lệnh suy diễn liên tiếp.
* **Kế hoạch khôi phục (Rollback plan)**: Giới hạn số lượt sử dụng Research Mode trên mỗi user/ngày.

---

## Giai Đoạn 12: Tự Động Trích Xuất, Đồ Thị Tri Thức & Hệ Thống Đánh Giá Multi-Agent (AGI-like Evolution)

### Phase 12A — New Chapter Knowledge Delta Extractor
* **Mục tiêu**: Tự động trích xuất các tri thức thay đổi (Knowledge Delta) ngay khi chương mới được xuất bản và cập nhật lập tức vào provisional library.
* **Files likely affected**: `backend/scripts/ingest_new_chapters.py`, `backend/scripts/build_provisional_library.py`
* **DB migration**: Không cần.
* **Test bắt buộc**: Nạp chương mới giả lập, kiểm tra các candidate thực thể được sinh tự động trong provisional library.
* **Production smoke bắt buộc**: Đăng chương 830, kiểm tra provisional library tự xuất hiện thực thể mới xuất hiện ở chương 830.
* **Rủi ro**: Nạp thông tin rác hoặc trích xuất sai tên thực thể do câu cú phức tạp của tác giả.
* **Kế hoạch khôi phục (Rollback plan)**: Đánh dấu các thực thể mới trích xuất là `staged` và cần Admin duyệt trước khi hiển thị cho Oracle.

### Phase 12B — Relationship/Timeline Graph
* **Mục tiêu**: Xây dựng đồ thị quan hệ nhân vật và dòng thời gian sự kiện (timeline graph) để hỗ trợ Oracle trả lời đúng các câu hỏi logic bắc cầu (ví dụ: A là đệ tử của B, B là kẻ thù của C -> quan hệ của A và C).
* **Files likely affected**: `backend/rag/graph_builder.py`, `backend/routes/ai_oracle.py`
* **DB migration**: Tạo bảng `knowledge_graph_edges` lưu `source_node`, `target_node`, `relation_type`, `evidence_chapters`.
* **Test bắt buộc**: Chạy truy vấn đồ thị tìm mối quan hệ gián tiếp.
* **Production smoke bắt buộc**: Oracle trả lời đúng các câu hỏi quan hệ gia tộc/thế lực phức tạp.
* **Rủi ro**: Đồ thị quá lớn làm chậm tốc độ xử lý hoặc bị lặp vòng vô hạn (cyclic paths).
* **Kế hoạch khôi phục (Rollback plan)**: Thiết lập chiều sâu tìm kiếm tối đa (max_depth = 3).

### Phase 12C — Active Learning Queue
* **Mục tiêu**: Hệ thống chủ động gợi ý các câu hỏi chưa rõ nghĩa hoặc các thực thể có độ tin cậy thấp cho Admin/Độc giả bình chọn để hoàn thiện tri thức nhanh nhất.
* **Files likely affected**: `backend/routes/active_learning.py`
* **DB migration**: Tạo bảng `active_learning_queue` lưu các câu hỏi cần được gán nhãn/bình chọn.
* **Test bắt buộc**: Kiểm tra hàng đợi tự động sinh câu hỏi gợi ý từ các log chat lỗi.
* **Production smoke bắt buộc**: User thấy danh mục "Câu hỏi tuần này cần bạn giải đáp" trên giao diện thư viện.
* **Rủi ro**: Độc giả spam bình chọn phá hoại tri thức chuẩn.
* **Kế hoạch khôi phục (Rollback plan)**: Chỉ ghi nhận bình chọn từ các tài khoản có điểm cống hiến hoặc cấp độ đọc cao.

### Phase 12D — Auto Repair Proposal Engine
* **Mục tiêu**: Hệ thống tự động đề xuất sửa đổi tri thức (Auto-repair Proposal) khi phát hiện xung đột dữ liệu (ví dụ: Chương 10 ghi nhân vật A dùng kiếm, Chương 500 ghi nhân vật A chuyển sang dùng đao).
* **Files likely affected**: `backend/scripts/auto_repair_proposal.py`
* **DB migration**: Tạo bảng `auto_repair_proposals` lưu đề xuất sửa đổi.
* **Test bắt buộc**: Test phát hiện xung đột vũ khí của nhân vật chính Hàn Phong và sinh đề xuất cập nhật.
* **Production smoke bắt buộc**: Admin nhận được đề xuất sửa đổi trên Dashboard và chỉ cần bấm duyệt.
* **Rủi ro**: Sinh quá nhiều đề xuất rác hoặc đề xuất sai do LLM hiểu sai ngữ cảnh tu từ.
* **Kế hoạch khôi phục (Rollback plan)**: Giới hạn quyền tự động ghi đè, bắt buộc qua bộ lọc phê duyệt của Admin.

### Phase 12E — Multi-agent Critic/Evaluator (Chỉ chạy khi được bật)
* **Mục tiêu**: Thiết lập mô hình Multi-agent: Một Agent sinh câu trả lời (Generator), một Agent phản biện (Critic) kiểm tra chéo độ chính xác dựa trên bằng chứng cốt truyện trước khi trả kết quả về cho độc giả.
* **Files likely affected**: `backend/routes/ai_oracle.py`, `backend/rag/critic_agent.py`
* **DB migration**: Không cần.
* **Test bắt buộc**: Giả lập Generator trả lời sai cốt truyện, kiểm tra Critic phát hiện và ép Generator viết lại.
* **Production smoke bắt buộc**: Độc giả nhận câu trả lời đã được hai Agent đồng thuận và ký số (verified signature).
* **Rủi ro**: Tăng gấp đôi chi phí Token và thời gian phản hồi (latency).
* **Kế hoạch khôi phục (Rollback plan)**: Có thể tắt/bật nhanh qua biến môi trường `ORACLE_MULTLAGENT_EVALUATOR_ENABLED=false`.

### Phase 12F — Long-term World Model
* **Mục tiêu**: Tổng hợp tri thức toàn bộ câu chuyện thành một "World Model" duy nhất. Hệ thống không chỉ tìm kiếm văn bản đơn thuần mà hiểu sâu sắc về thế giới mạt thế của tác phẩm (thang sức mạnh, các tổ chức, các loại zombie).
* **Files likely affected**: `backend/rag/world_model.py`
* **DB migration**: Tạo bảng cấu trúc tri thức thế giới `world_model_canon`.
* **Test bắt buộc**: Truy vấn các câu hỏi mang tính tổng hợp cao về thế giới quan của truyện.
* **Production smoke bắt buộc**: Oracle giải thích mạch lạc logic tiến hóa của thây ma trong truyện.
* **Rủi ro**: Quá phức tạp để xây dựng và duy trì tính nhất quán.
* **Kế hoạch khôi phục (Rollback plan)**: Fallback về RAG hybrid truyền thống nếu World Model bị lệch tri thức.
