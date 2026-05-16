# Draft Knowledge: Chương 130

- source_id: ingest-0c8ef53bfb1b852c
- raw_file: raw/Chương 130.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Trang bị level 3 cũng chia ra mạnh yếu. Trang bị level 3 như Nhẫn Duy Tâm có thể phát ra 3 lượt công kích mỗi ngày đã rất mạnh. Section order 7: Paragraph: Đây là một chiếc nhẫn mạnh mẽ không thua kém Thánh Quang liên của Hàn Phong. Section order 10: Paragraph: Hai chiếc nhẫn level 3, tất cả những người bên phía Đổng Thành đều là hơi thở vô cùng gấp gáp.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- giai

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Trang
- Duy
- Quang

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
- explain Chương 130
- summarize Chương 130
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 130.docx Chapter title: Chương 130: Thực lực của Ngô Soái Section count: 115 Section order 1: Heading: Chương 130: Thực lực của Ngô Soái Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Nhẫn Tịnh Hoá này mới trưa nay được Ngô Soái lật thẻ nhận được, còn chưa kịp thử lần nào. Section order 4: Paragraph: Đổng Thành nheo mắt nhìn Nhẫn Tịnh Hoá, trong mắt không khỏi bốc lên tham lam. Section order 5: Paragraph: Trang bị level 3 cũng chia ra mạnh yếu. Trang bị level 3 như Nhẫn Duy Tâm có thể phát ra 3 lượt công kích mỗi ngày đã rất mạnh. Section order 6: Paragraph: Nhưng nếu chỉ có thể phát ra một lần công kích, vậy thì lần công kích đó sẽ mạnh hơn cả ba lượt công kích lẻ tẻ cộng lại. Section order 7: Paragraph: Đây là một chiếc nhẫn mạnh mẽ không thua kém Thánh Quang liên của Hàn Phong. Section order 8: Paragraph: Ngô Soái lại lấy ra một cái nhẫn nữa nói: Section order 9: Paragraph: - Đây là Nhẫn Khốn Cùng, gia tăng 3 điểm sức mạnh, cũng có thể kích hoạt 1 lượt kỹ năng 24h làm lạnh. Section order 10: Paragraph: Hai chiếc nhẫn level 3, tất cả những người bên phía Đổng Thành đều là hơi thở vô cùng gấp gáp. Section order 11: Paragraph: Ngô Soái hứng thú xoay người nhìn về phía Bành Lực nói: Section order 12: Paragraph: - Thế này đi, lực lượng ai cũng muốn, chi bằng chúng ta làm một cái giao lưu lực lượng… Nếu vị Bành đại ca này có thể chạm được vào người tôi, tôi không chỉ thua 2 chiếc nhẫn này mà toàn bộ 7 chiếc nhẫn của tôi cũng sẽ giao ra. Đổi lại, nếu tôi đánh hộc máu Bành đại ca, tôi chỉ cần chiếc nhẫn màu tím trên ngón trỏ kia thôi. S...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 130.docx; chapter_title=Chương 130: Thực lực của Ngô Soái; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=114 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
