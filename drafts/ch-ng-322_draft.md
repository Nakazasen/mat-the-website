# Draft Knowledge: Chương 322

- source_id: ingest-b5f54907c5760bd9
- raw_file: raw/Chương 322.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Đạn bộc phá bắn ra từ mồm B1 có tốc độ không phải rất nhanh, tính toán chỉ khoảng dưới 100m/s, so với tốc độ của đạn PG-2 HEAT bắn ra từ súng chống tăng RPG-2 mà nhân loại sử dụng thì tương đương. Viên đạn tà tà bay trong không khí, tới phía trước trận địa nhân loại đã chuẩn bị sẵn thì va phải lưới mắt cáo, sau đó ầm ầm nổ tung. Section order 6: Paragraph: Thay vì tốn thời gian và công sức liên tục duy trì kỹ năng như Thao Túng Đại Địa để chặn bộc đạn, hoặc mất côn...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- level

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- B1
- PG-2 HEAT
- RPG-2

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
- explain Chương 322
- summarize Chương 322
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 322.docx Chapter title: Chương 322: Lợi dụng tất cả nguồn lực Section count: 51 Section order 1: Heading: Chương 322: Lợi dụng tất cả nguồn lực Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Đạn bộc phá bắn ra từ mồm B1 có tốc độ không phải rất nhanh, tính toán chỉ khoảng dưới 100m/s, so với tốc độ của đạn PG-2 HEAT bắn ra từ súng chống tăng RPG-2 mà nhân loại sử dụng thì tương đương. Viên đạn tà tà bay trong không khí, tới phía trước trận địa nhân loại đã chuẩn bị sẵn thì va phải lưới mắt cáo, sau đó ầm ầm nổ tung. Section order 4: Paragraph: Tương tự như việc đạn diệt quỷ khi gặp “thi khí” sẽ bốc cháy, bộc đạn do thây ma phát ra cũng sẽ bốc cháy ngay khi gặp “nhân khí”. Trên lưới mắt cáo buộc lấy rất nhiều những mảnh vải rách thấm đẫm nước tiểu nhân loại, đây chính là “khí tức” để kích hoạt phản ứng nổ tung của bộc đạn. Section order 5: Paragraph: Vụ nổ tạo ra áp lực nho nhỏ, đánh cho một mảnh lưới thép run lên bần bật. Nhưng lưới mắt cáo bản chất vốn đã chi chít lỗ thủng, vụ nổ từ bộc đạn không có mấy uy lực sát thương vật lý, chỉ mạnh mẽ về mặt gây ra hiệu ứng thây ma hoá, cuối cùng đã hoàn toàn bị kết cấu rỗng này phân tán hết sạch uy lực, không gây ra bao nhiêu tổn hại tới lưới thép. Section order 6: Paragraph: Thay vì tốn thời gian và công sức liên tục duy trì kỹ năng như Thao Túng Đại Địa để chặn bộc đạn, hoặc mất công dồn nhân lực quan trọng đi canh chừng phá huỷ bộc đạn trên đường bay, Hàn Phong đã xây dựng lên thành luỹ cố định này để chặn lại bộc đạn 24/24, không tốn bất kỳ công sức nào đi duy trì hay canh chừng. Sectio...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 322.docx; chapter_title=Chương 322: Lợi dụng tất cả nguồn lực; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=50 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
