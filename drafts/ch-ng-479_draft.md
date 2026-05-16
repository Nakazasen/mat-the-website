# Draft Knowledge: Chương 479

- source_id: ingest-122c4330f29166b7
- raw_file: raw/Chương 479.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 62: Paragraph: Trường hợp thứ nhất, nếu Tam Giang thực sự nhúng tay vào chuyện này, vậy thì hắn trực tiếp nhận sai trước luôn, tự nhận luật pháp của trấn Hi Vọng còn yếu kém, sau đó ngay lập tức cho ra bản sửa đổi bổ sung chi tiết cụ thể. Section order 3: Paragraph: Trong khi cuộc họp của cao tầng diễn ra trong phòng, bên ngoài sân rộng, hai nhân viên công tác thuộc phòng quản lý trị an cũng đang thực hiện nhiệm vụ tuyên truyền thông tin. Section order 8: Paragraph: Bức ảnh đầu...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- tham
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Trong
- Hi
- Kha

### Modules
- none

### Errors
- 479
- 479: Lu

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
- explain Chương 479
- summarize Chương 479
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 479.docx Chapter title: Chương 479: Luật phòng chống tham nhũng Section count: 82 Section order 1: Heading: Chương 479: Luật phòng chống tham nhũng Section order 2: Paragraph: 11–13 minutes Section order 3: Paragraph: Trong khi cuộc họp của cao tầng diễn ra trong phòng, bên ngoài sân rộng, hai nhân viên công tác thuộc phòng quản lý trị an cũng đang thực hiện nhiệm vụ tuyên truyền thông tin. Section order 4: Paragraph: Đều đặn mỗi 7 giờ sáng hàng ngày, các thông cáo mới sẽ được dán tại bảng bố cáo trung tâm. Thường thì cao tầng họp bàn có vấn đề gì thì đều sẽ thông báo ở đây, ai ai cũng đều cần phải biết cả, kể cả là binh lính hay dân thường. Cư dân trấn Hi Vọng sau 24 ngày tận thế thì cũng dần quen với việc tiếp nhận thông tin kiểu này rồi. Section order 5: Paragraph: Một trong hai đội viên bước lên bảng bố cáo dán xuống 27 tấm ảnh lớn, đây là ảnh chân dung của 27 người, bất quá tất cả đều đã được xử lý làm mờ, kể cả nhìn kỹ cũng khó nhận ra. Section order 6: Paragraph: Bên dưới mỗi tấm ảnh lại có chú thích, thể hiện ra danh tính của chủ nhân bức ảnh. Section order 7: Paragraph: Chẳng qua cũng giống như ảnh, chú thích này chỉ có phần họ, không có phần tên, người không liên quan rất khó xác định ai với ai. Section order 8: Paragraph: Bức ảnh đầu tiên là của một người họ Kha, khuôn mặt trên ảnh đã được làm mờ, nhưng đa số đều có thể nhận ra đây là một nam nhân. Section order 9: Paragraph: Những tấm ảnh này vừa ra, mấy trăm cư dân bên dưới đã bắt đầu xì xào bàn tán. Section order 10: Paragraph: - Là cái gì đây a. Section order 11: Paragraph: - Nhìn có vẻ ng...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 479.docx; chapter_title=Chương 479: Luật phòng chống tham nhũng; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=81 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
