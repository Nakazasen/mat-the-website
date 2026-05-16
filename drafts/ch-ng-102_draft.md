# Draft Knowledge: Chương 102

- source_id: ingest-1c34f66bba0e5a87
- raw_file: raw/Chương 102.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 102: Tờ giấy quỷ dị. Section order 55: Paragraph: Nghe thấy ẩn ý trong lời Hàn Phong, Phương Tường khuôn mặt trở lên xám xịt, lại bắt đầu kể khổ: Section order 63: Paragraph: Sau khi Phương Tường rời đi, Hàn Phong mới thở ra một hơi, đem số tinh thạch còn lại chuyển hết thành điểm exp.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- tinh

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Vi

### Modules
- none

### Errors
- 400 c

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
- explain Chương 102
- summarize Chương 102
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 102.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 102: Tờ giấy quỷ dị. Section count: 115 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 102: Tờ giấy quỷ dị. Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Bản kỹ năng mà nàng ta muốn chọn chính là kỹ năng nhất giai hồi tức. Section order 4: Paragraph: Tiêu tốn 3 trí lực, hồi phục 5 thể lực. Section order 5: Paragraph: Tường Vi không khỏi kinh ngạc: Section order 6: Paragraph: - Tại sao? Tôi nghĩ nó đâu có gì đặc biệt? Hàn Phong nhanh chóng nói: Section order 7: Paragraph: - Tôi sớm đã muốn học nó. Section order 8: Paragraph: Tường Vi lại kỳ quái hỏi ngược lại: Section order 9: Paragraph: - Vậy sao anh không học nó luôn đi mà còn bày ra đây cho tôi chọn? Section order 10: Paragraph: Đứng trước vấn đề này, Hàn Phong có chút không biết phải làm sao đáp lại. Section order 11: Paragraph: Hắn không thể trả lời rằng do kỹ năng này quá yếu nên hắn chưa thèm học a. Section order 12: Paragraph: Sau khi rối rắm một hồi, cân nhắc thiệt hơn, hắn mới dò hỏi: Section order 13: Paragraph: - Tại sao cô muốn kỹ năng này? Section order 14: Paragraph: Tường Vi thản nhiên đáp lại: Section order 15: Paragraph: - Tôi dùng trí lực hồi phục thể lực cho Trần Diệu Âm, nàng ta sẽ duy trì vòng bảo vệ ngăn công kích bên ngoài, hai chúng tôi sẽ an toàn. Section order 16: Paragraph: Câu trả lời để cho Hàn Phong không nhịn được dâng lên kỳ quái. Section order 17: Paragraph: Cũng là cách hay a… Bất quá, làm sao có cảm giác co đầu rút cổ như rùa đen. Section order 18: Paragraph: Hai nữ nhân n...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 102.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 102: Tờ giấy quỷ dị.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=114 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
