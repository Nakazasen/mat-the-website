# Draft Knowledge: Chương 230

- source_id: ingest-cda71fa6ab578dab
- raw_file: raw/Chương 230.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Nghe được câu trả lời của Tường Vi, Hàn Phong cuối cùng cũng thả lỏng bàn tay, đồng thời khoé miệng hơi nhếch lên một đường cong lạnh lùng. Section order 5: Paragraph: Phía bên kia, vị trưởng ban chỉ huy thông tin huyện Tam Giang nhận được xác nhận thì thở phào, sau đó nhanh chóng hỏi lại: Section order 14: Paragraph: - Quan Bình? Cậu là Quan Bình? Cậu còn sống sao?

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- quan
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Nghe
- Vi
- Phong

### Modules
- none

### Errors
- 531

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
- explain Chương 230
- summarize Chương 230
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 230.docx Chapter title: Chương 230: Chỉ vậy thôi sao? Section count: 91 Section order 1: Heading: Chương 230: Chỉ vậy thôi sao? Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Nghe được câu trả lời của Tường Vi, Hàn Phong cuối cùng cũng thả lỏng bàn tay, đồng thời khoé miệng hơi nhếch lên một đường cong lạnh lùng. Section order 4: Paragraph: Trúng đích! Section order 5: Paragraph: Phía bên kia, vị trưởng ban chỉ huy thông tin huyện Tam Giang nhận được xác nhận thì thở phào, sau đó nhanh chóng hỏi lại: Section order 6: Paragraph: - Tôi là Hạ Quân, xin hỏi cô là… Section order 7: Paragraph: Bởi vì bên kia chưa nêu danh tính, hắn ta buộc phải hỏi lại để xác nhận tình hình cũng như tiện xưng hô. Section order 8: Paragraph: Tường Vi có chút bối rối, nàng không có chức vụ cụ thể tại trấn Hi Vọng, cũng không tiện nói ra thân thế bản thân. Hàn Phong tâm tư nhanh nhạy, rất tuỳ ý phất tay nói: Section order 9: Paragraph: - Hãy để Quan tiểu đội trưởng phụ trách liên lạc. Section order 10: Paragraph: Tường Vi âm thầm thở ra, nhanh chóng chuyển bộ đàm qua bên cạnh. Section order 11: Paragraph: Quan Bình là nhân viên chính phủ chính thức, được công nhận bởi chính quyền sau tận thế, xét về tính chính thống, hắn là chính thống nhất, lời nói có đảm bảo và uy tín nhất. Lúc này đây tiếp nhận bộ đàm từ tay Tường Vi, hắn ta có chút run rẩy vì kích động mà nói: Section order 12: Paragraph: - Tôi là Quan Bình, phi phàm giả số hiệu 127 thuộc tiểu đội trinh sát số 4. Xác nhận. Section order 13: Paragraph: Bên kia im lặng một chút, sau đó vang lên thanh âm v...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 230.docx; chapter_title=Chương 230: Chỉ vậy thôi sao?; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=90 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
