# Draft Knowledge: Chương 132

- source_id: ingest-72e652e80b2d45e6
- raw_file: raw/Chương 132.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 18: Paragraph: Trong xe, không khí yên tĩnh đến cực điểm, ngay cả Quan Bình, Lý Võ Lạc những người lòng mang bất mãn cũng phải rụt cổ lại. Section order 49: Paragraph: Sau đó hắn thản nhiên quay qua Lý Võ Lạc và Quan Bình rồi nói: Section order 51: Paragraph: Hai vị quân nhân nhìn nhau một cái, sau đó vội bước theo sau Hàn Phong.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- theo

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Sau
- Vi
- Phong

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
- explain Chương 132
- summarize Chương 132
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 132.docx Chapter title: Chương 132: Đây là tận thế sao? Section count: 117 Section order 1: Heading: Chương 132: Đây là tận thế sao? Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Sau khi chạy khỏi cổng thôn Xuân Lê, đoàn xe không gặp bất kỳ cản trở nào nữa. Section order 4: Paragraph: Tường Vi ngồi phía sau Hàn Phong, lúc này đột nhiên nói: Section order 5: Paragraph: - Hàn đại đội trưởng, tuỳ tiện gọi người khác là tì nữ không phải là hành động thân sĩ. Section order 6: Paragraph: “ch.ết tiệt! Là do ả Liễu Huyên kia gọi trước, không phải tôi tự nghĩ ra, cô đi mà tìm ả nói chuyện.” Section order 7: Paragraph: Hàn Phong một bên uỷ khuất nghĩ thầm, một bên tuỳ tiện nói: Section order 8: Paragraph: - Tình thế cấp bách, xin lỗi vì đã mạo phạm. Thế này đi, tôi lấy 100 cống hiến cá nhân ra đền bù cho cô. Section order 9: Paragraph: Tường Vi bàn tay nắm chặt, nhưng vẫn nhẹ nhàng phản bác: Section order 10: Paragraph: - Đây không phải vấn đề cống hiến có thể giải quyết. Section order 11: Paragraph: Hàn Phong có chút đau đầu, hắn đưa tay bóp bóp trán, nghiêm túc nói: Section order 12: Paragraph: - 1000 cống hiến. Section order 13: Paragraph: Tường Vi nghe vậy, thiếu chút tức tới mức chửi bậy, nàng lạnh lùng gọi thẳng tên đối phương: Section order 14: Paragraph: - Hàn Phong! Section order 15: Paragraph: Hàn Phong giả bộ không nghe thấy âm thanh tức giận của Tường Vi, hắn nghẹo cổ qua một bên nhìn đường rồi lơ đãng nói tiếp: Section order 16: Paragraph: - 1001 cống hiến. Section order 17: Paragraph: - Hỗn đản! Section order 18: Paragraph: Tr...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 132.docx; chapter_title=Chương 132: Đây là tận thế sao?; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=116 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
