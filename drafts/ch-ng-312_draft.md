# Draft Knowledge: Chương 312

- source_id: ingest-5d2ef44e3e38aa9c
- raw_file: raw/Chương 312.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Cuộc họp do hai người Ngô Soái, Chu Vấn chủ trì xem như diễn ra tốt đẹp, những tưởng bởi vì không có Hàn Phong tại ghế chủ vị thì sẽ hỗn loạn nhưng thực tế thì không hề, sau những phút đầu có chút cầm chừng rụt rè, giai đoạn sau đã có rất nhiều đề xuất được đưa ra. Các đề mục bọn họ bàn luận chủ yếu là về việc làm sao thanh lý thây ma còn sót lại tại khu vực nội bộ huyện Liễu Lâm, huấn luyện tân binh, xây dựng và tái thiết cuộc sống, cùng với việc đảm bảo nguồn lươ...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Chu
- Phong
- Thao

### Modules
- none

### Errors
- none

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
- explain Chương 312
- summarize Chương 312
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 312.docx Chapter title: Chương 312: Xử lý công việc Section count: 45 Section order 1: Heading: Chương 312: Xử lý công việc Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Cuộc họp do hai người Ngô Soái, Chu Vấn chủ trì xem như diễn ra tốt đẹp, những tưởng bởi vì không có Hàn Phong tại ghế chủ vị thì sẽ hỗn loạn nhưng thực tế thì không hề, sau những phút đầu có chút cầm chừng rụt rè, giai đoạn sau đã có rất nhiều đề xuất được đưa ra. Các đề mục bọn họ bàn luận chủ yếu là về việc làm sao thanh lý thây ma còn sót lại tại khu vực nội bộ huyện Liễu Lâm, huấn luyện tân binh, xây dựng và tái thiết cuộc sống, cùng với việc đảm bảo nguồn lương thực trong tương lai. Section order 4: Paragraph: Giống như được cởi bỏ một cái áp lực nào đó, mọi người thảo luận và trao đổi vô cùng nhiệt tình, ý tưởng chia quân thành nhiều tiểu tổ 7 người rồi sử dụng xe bán tải, xe jeep cơ động cao chạy quanh quanh tìm diệt thây ma đã được thông qua. Vài ý tưởng táo bạo thậm chí có phần cực đoan cũng được đề xuất, như là trích xuất máu người tình nguyện hiến tặng để làm mồi dụ thây ma, như là dùng xác thây ma để làm bẫy dụ cá, làm chất dinh dưỡng trồng rau dại biến dị… Section order 5: Paragraph: Có ý kiến còn đề xuất ghi âm âm thanh la hét của nhân loại rồi phát qua loa phóng thanh đặt trên xe tải, mục đích là chạy vòng vòng dụ dỗ đám thây ma ở các thôn trấn xung quanh tụ tập lại để tiêu diệt cho tiện. Section order 6: Paragraph: Đối với đề xuất này Hàn Phong cũng không biết nên khóc hay nên cười, thật sự đủ sáng tạo và lập dị, nhưng hắn cũng không ngại để cho b...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 312.docx; chapter_title=Chương 312: Xử lý công việc; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=44 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
