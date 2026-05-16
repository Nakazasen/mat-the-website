# Draft Knowledge: Chương 183

- source_id: ingest-90ae0490ad0998a4
- raw_file: raw/Chương 183.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 8: Paragraph: - Ninh Thường, Ninh Thường, chị phải tỉnh táo lên, tiểu Vân còn cần chị tới bảo hộ. Quân y, quân y đâu… Section order 11: Paragraph: Hàn Phong cầm tay Châu Lam lôi ngược về phía sau, tránh đi cú cắn của vị đội viên Ninh Thường chỉ còn lại nửa người này, hắn trầm giọng nói: Section order 14: Paragraph: Châu Lam mặt đầy nước mắt giãy thoát khỏi tay Hàn Phong, nàng ta chống hai tay xuống nền đất rồi khóc ầm lên:

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- nghi

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Con
- Lam
- Trang

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
- explain Chương 183
- summarize Chương 183
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 183.docx Chapter title: Chương 183: Lợi thế của nhân loại Section count: 86 Section order 1: Heading: Chương 183: Lợi thế của nhân loại Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Nữ đội viên khuôn mặt đã hoá thành màu đen kịt, ngay cả da thịt cũng xuất hiện mục ruỗng, răng cùng tóc tự động mọc dài ra từ trong miệng, thế nhưng nàng ta vẫn nghẹn ngào hô lên: Section order 4: Paragraph: - Con của tôi… Bảo hộ… Section order 5: Paragraph: Châu Lam khuôn mặt sớm vương đầy nước mắt, nàng ta vươn tay muốn nắm lấy bàn tay đội viên xấu số này, thế nhưng quang hoa nhu hoà toả ra từ trang bị level 4 khiến cho hai bên không thể chạm vào nhau. Section order 6: Paragraph: Trang bị này không nhiễm bụi bẩn. Section order 7: Paragraph: Châu Lam vội vã gấp gáp hô lên: Section order 8: Paragraph: - Ninh Thường, Ninh Thường, chị phải tỉnh táo lên, tiểu Vân còn cần chị tới bảo hộ. Quân y, quân y đâu… Section order 9: Paragraph: Nàng ta hốt hoảng hô lớn, đồng thời giơ tay muốn phóng xuất kỹ năng trị liệu, thế nhưng chỉ số thể lực cùng trí lực đều chỉ còn lại 1 điểm, không đủ điều kiện thi triển. Section order 10: Paragraph: Sau một hồi hoàng hốt, chiếc vòng tay trị liệu level 2 trên tay trái nàng ta chợt sáng lên, nhưng ngay lập tức lại bị một bàn tay khác đè chặt lại. Section order 11: Paragraph: Hàn Phong cầm tay Châu Lam lôi ngược về phía sau, tránh đi cú cắn của vị đội viên Ninh Thường chỉ còn lại nửa người này, hắn trầm giọng nói: Section order 12: Paragraph: - Nàng ta đã ch.ết. Section order 13: Paragraph: Thây ma Ninh Thường dùng hai tay bò tớ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 183.docx; chapter_title=Chương 183: Lợi thế của nhân loại; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=85 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
