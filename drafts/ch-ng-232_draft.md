# Draft Knowledge: Chương 232

- source_id: ingest-8bfdb1600073bcb8
- raw_file: raw/Chương 232.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Sau khi nhìn Hà Tam thu nhẫn chống chịu vào trong tay, Hàn Phong mới thoải mái ngửa người ra sau ghế rồi nói: Section order 7: Paragraph: Nhưng mục tiêu chủ yếu lần này của hắn vẫn là vũ khí đạn dược. Sau màn dạo đầu đã nhìn thấy đủ tín hiệu hữu hảo từ phe Hàn Phong, Hà Tam không muốn lòng vòng thêm nữa, quyết định trực tiếp đề cập: Section order 12: Paragraph: Nhạc Sơn, Lý Võ Lạc, Quan Bình nghe thấy vậy thì thở phào một hơi. May mắn mà Hàn Phong không trao đổi vũ...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Sau
- Tam
- Phong

### Modules
- none

### Errors
- 5000 vi

### Processes
- none

## Perception Pipeline
- document_type: text_document
- document_type_confidence: 0.78
- signals: docx_container, paragraphs, headings
- native_structured: confidence=0.80
- ocr: confidence=0.00
- vision_layout: confidence=0.22
- document_classifier: confidence=0.78
- provider_semantic: confidence=0.00

## Provider Assistance
- used=False; status=skipped; selected=; fail_count=0; latency_ms=0; token_estimate=0

## Possible Queries
- explain Chương 232
- summarize Chương 232
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 232.docx Chapter title: Chương 232: Lý do Section count: 78 Section order 1: Heading: Chương 232: Lý do Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Sau khi nhìn Hà Tam thu nhẫn chống chịu vào trong tay, Hàn Phong mới thoải mái ngửa người ra sau ghế rồi nói: Section order 4: Paragraph: - Về đề xuất của Đổng huynh đệ, chúng tôi xin ghi nhận. Chúng tôi ở bên này đúng là đang cần xăng dầu và nhiên liệu, vừa hay lại đang dư thừa rất nhiều lương thực thực phẩm, chúng ta hai bên hảo hữu, có thể trao đổi lẫn nhau. Section order 5: Paragraph: Xăng dầu dùng trong chiến đấu đã tiêu tốn khá nhiều, hiện tại trữ lượng toàn trấn chỉ còn khoảng 10.000 lít xăng, 6000 lít dầu, trấn Hi Vọng đã bắt đầu cần tính toán tới việc tìm kiếm nguồn cung dự trữ. Nhất là trong bối cảnh sắp tới bọn họ cần đẩy quân về trung tâm huyện Liễu Lâm, tới các thôn xã thành trấn xung quanh thanh lý thây ma rải rác, tìm kiếm tài nguyên và người sống sót, còn cần chạy máy phát phát điện cho đèn chiếu sáng, máy bơm nước, máy tính văn phòng, sạc acquy… Xăng dầu là không bao giờ sợ thừa. Section order 6: Paragraph: Hà Tam nghe vậy thì thở phào. Thực ra một trong các hạng mục hắn muốn trao đổi đúng là có lương thực. Chiến tranh rất cần lương thực, cần cho binh lính ăn no, đội viên dự bị ăn no, lũ người thường cũng phải ăn no để còn có sức xây dựng công sự. Section order 7: Paragraph: Nhưng mục tiêu chủ yếu lần này của hắn vẫn là vũ khí đạn dược. Sau màn dạo đầu đã nhìn thấy đủ tín hiệu hữu hảo từ phe Hàn Phong, Hà Tam không muốn lòng vòng thêm nữa, quyết định trực tiếp đề cập...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 232.docx; chapter_title=Chương 232: Lý do; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=77 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
