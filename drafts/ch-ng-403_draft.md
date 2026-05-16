# Draft Knowledge: Chương 403

- source_id: ingest-aa50a78fb8601fdc
- raw_file: raw/Chương 403.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 8: Paragraph: - Anh là nhân viên công tác chính phủ huyện Tam Giang đúng không? Kể lại đầu đuôi câu chuyện cho tất cả mọi người cùng nghe. Section order 12: Paragraph: Sau Phó Tế Tường, Hàn Phong lại chỉ định ngẫu nhiên 3 người khác trong đám đông kể lại sự việc, từ thông tin của bọn họ, hành động vừa mới diễn ra đã dần được lộ rõ. Section order 17: Paragraph: Chưa hết, nữ tử nhân viên công tác huyện Tam Giang nhìn cảnh này thì lao lên ngăn cản, đội viên Điền Mạnh tiếp tục chém...

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
- Phong
- Anh
- Tam Giang

### Modules
- none

### Errors
- 403

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
- explain Chương 403
- summarize Chương 403
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 403.docx Chapter title: Chương 403 Section count: 87 Section order 1: Heading: Chương 403 Section order 2: Paragraph: 11–14 minutes Section order 3: Paragraph: Hàn Phong trầm giọng hỏi rõ nguyên do, đội viên đội chấp pháp bị trói chặt lập tức kêu lớn thanh minh mình không giết người, trong khi hai đội viên đứng bên cạnh thì tần ngần do dự, không biết đáp sao cho phải. Section order 4: Paragraph: Thấy tình cảnh này, hắn càng thêm gằn giọng hừ lạnh nói: Section order 5: Paragraph: - Nói hết toàn bộ! Nếu phát hiện có giấu giếm bao che, vậy thì quy vào tội đồng phạm. Section order 6: Paragraph: Âm thanh quán lớn của hắn doạ cho hai người kia sợ tới xanh mặt, vội vã mồm năm miệng mười kể lại không sót một chút chi tiết. Section order 7: Paragraph: Hàn Phong nghe xong câu chuyện lại tiếp tục chỉ Phó Tế Tường đứng bên cạnh ra lệnh: Section order 8: Paragraph: - Anh là nhân viên công tác chính phủ huyện Tam Giang đúng không? Kể lại đầu đuôi câu chuyện cho tất cả mọi người cùng nghe. Section order 9: Paragraph: Phó Tế Tường có chút nổi lên gai ốc nhè nhẹ, điều này dường như không nằm trong kịch bản. Section order 10: Paragraph: Đáng lẽ gã họ Hàn kia phải cố gắng thanh minh, cố gắng bao che, thậm chí bắt nhốt bọn họ để bịt miệng mới đúng chứ, tại sao lại muốn công khai làm rõ mọi chuyện ở đây. Section order 11: Paragraph: Thế nhưng thời gian không đợi người, ông ta không thể suy nghĩ quá nhiều, chỉ có thể kiên trì kể ra sự việc, thậm chí không dám kể lể quá trớn, dù sao xung quanh cũng có một đám người cũng cùng nhau quan sát tình hình. Section order 12: Paragraph...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 403.docx; chapter_title=Chương 403; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=86 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
