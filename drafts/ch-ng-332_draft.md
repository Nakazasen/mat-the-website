# Draft Knowledge: Chương 332

- source_id: ingest-a1ed795ef332eb3d
- raw_file: raw/Chương 332.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Tờ giấy này chứa thông tin về 25 nhân vật nổi bật của huyện Tam Giang, ngoài ra còn có vài dự định mà Hàn Phong muốn làm. Ngô Soái sẽ “đi sứ” bên kia, tất nhiên cần phải hết sức tận dụng cơ hội này. Section order 11: Paragraph: - Nếu nhóm Tam Giang dám hành động một cách khắc nghiệt, chúng ta sẽ dẫn quân đột kích qua bắn vài chục viên đạn chống tăng vào mặt đối phương, sau đó trực tiếp đánh sập cầu Liễu Hà, từ nay chính thức đoạn tuyệt. Section order 23: Paragraph:...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- level
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Tam Giang
- Hi

### Modules
- none

### Errors
- 400 ng

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
- explain Chương 332
- summarize Chương 332
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 332.docx Chapter title: Chương 332 Section count: 58 Section order 1: Heading: Chương 332 Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong phẩy phẩy tay mấy cái rồi ném tiếp một tờ giấy có ghi thông tin tình báo cho Ngô Soái rồi thản nhiên nói: Section order 4: Paragraph: - Đệ tìm cách xác nhận những thông tin này… Section order 5: Paragraph: Tờ giấy này chứa thông tin về 25 nhân vật nổi bật của huyện Tam Giang, ngoài ra còn có vài dự định mà Hàn Phong muốn làm. Ngô Soái sẽ “đi sứ” bên kia, tất nhiên cần phải hết sức tận dụng cơ hội này. Section order 6: Paragraph: Ngô Soái sau khi đọc xong, hai tay không khỏi đấm vào nhau rồi trầm giọng đáp lại: Section order 7: Paragraph: - Thật muốn làm thịt vài người mà, aizzz… Section order 8: Paragraph: Hàn Phong mặt không biểu cảm. Vài kẻ đúng thật là rất đáng bị giết, trấn Hi Vọng còn chưa làm gì bọn họ đã muốn chủ trương dẫn quân san bằng, cái này không phải thù địch bình thường, cái này là hết thuốc chữa rồi. Bất quá, hiện tại còn chưa phải lúc hành động. Section order 9: Paragraph: Ngô Soái bóp bóp trán mấy cái rồi thở dài hỏi: Section order 10: Paragraph: - Đại ca, nếu quả thật bọn họ làm việc không theo quy tắc thì sao? Hàn Phong trầm ngâm một lát rồi nở một nụ cười lạnh: Section order 11: Paragraph: - Nếu nhóm Tam Giang dám hành động một cách khắc nghiệt, chúng ta sẽ dẫn quân đột kích qua bắn vài chục viên đạn chống tăng vào mặt đối phương, sau đó trực tiếp đánh sập cầu Liễu Hà, từ nay chính thức đoạn tuyệt. Section order 12: Paragraph: - …!!! Section order 13: Paragraph: Đoàn...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 332.docx; chapter_title=Chương 332; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=57 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
