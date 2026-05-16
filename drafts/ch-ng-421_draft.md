# Draft Knowledge: Chương 421

- source_id: ingest-d8387e912f5e0aa4
- raw_file: raw/Chương 421.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 9: Paragraph: Đây là thanh âm của một nhân viên công tác về vận động "nhân quyền" của Tam Giang. Section order 12: Paragraph: - Con ơi... Huhuhu... Con ơi, con có tội tình gì chứ... Section order 22: Paragraph: - Chính quyền Tam Giang đang che giấu tội phạm khủng bố, tôi sẽ viết công hàm yêu cầu bọn họ giao ra tên sát nhân này...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- thanh
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Tam Giang
- Huhuhu
- Con

### Modules
- none

### Errors
- 421
- 421: Cu

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
- explain Chương 421
- summarize Chương 421
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 421.docx Chapter title: Chương 421: Cuộc chiến truyền thông Section count: 95 Section order 1: Heading: Chương 421: Cuộc chiến truyền thông Section order 2: Paragraph: 11–13 minutes Section order 3: Paragraph: - Đúng, kế hoạch đổ lỗi cho đội viên đội chấp pháp sẽ không chỉ dừng lại ở việc thao túng anh ta giết người, tôi cũng được lệnh sẽ tự sát trong quá trình bị giam giữ để gia tăng sức ép... Section order 4: Paragraph: - Đúng, tôi biết điều này sẽ dùng để kích động chiến tranh... Section order 5: Paragraph: - Tôi không bị ép cung... Section order 6: Paragraph: Đây là thanh âm của Phó Tế Tường, hắn đã thú nhận toàn bộ tội danh. Section order 7: Paragraph: - Chúng tôi không hề biết Chương Lãm sẽ chọn giết bé gái đó, trong kế hoạch, anh ta sẽ giết một cựu chiến binh cụt tay, người này cũng đã đồng ý hi sinh cảm tử, không hề có chuyện chúng tôi nhắm mục tiêu vào dân thường... Section order 8: Paragraph: - Đúng, kế hoạch đã được chuẩn bị tỉ mỉ từ trước... Section order 9: Paragraph: Đây là thanh âm của một nhân viên công tác về vận động "nhân quyền" của Tam Giang. Section order 10: Paragraph: - Huhuhu... Tôi đã làm gì chứ, tôi đã đắc tội ai chứ, tại sao lại vu oan cho tôi... Tôi không phải một sát nhân a... Section order 11: Paragraph: Đây là thanh âm khóc lóc kêu oan của Điền Mạnh. Section order 12: Paragraph: - Con ơi... Huhuhu... Con ơi, con có tội tình gì chứ... Section order 13: Paragraph: - Tôi không cần 100 cân lương thực đó nữa, trả con lại cho tôi... Section order 14: Paragraph: Đây là thanh âm khóc lóc thảm thương của thiếu phụ mất con. Section o...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 421.docx; chapter_title=Chương 421: Cuộc chiến truyền thông; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=94 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
