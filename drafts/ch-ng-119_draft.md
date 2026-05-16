# Draft Knowledge: Chương 119

- source_id: ingest-e8d911127e8214ed
- raw_file: raw/Chương 119.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 119: Dự đoán Section order 5: Paragraph: - Tôi muốn anh dùng số vũ khí này trên việc mở một con đường dẫn tới huyện Tam Giang. Section order 13: Paragraph: - Tôi dự định sẽ dẫn đội ngũ dưới trướng thẳng hướng trung tâm huyện Liễu Lâm, từ đó có thể đi qua cầu Liễu Hà để tới bờ đông huyện Tam Giang.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- Section
- Heading
- Paragraph
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
- explain Chương 119
- summarize Chương 119
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 119.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 119: Dự đoán Section count: 103 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 119: Dự đoán Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Hàn Phong nhướng mày hỏi lại: Section order 4: Paragraph: - Là điều gì? Tường Vi nhẹ nhàng vuốt tóc, sau đó thản nhiên nói: Section order 5: Paragraph: - Tôi muốn anh dùng số vũ khí này trên việc mở một con đường dẫn tới huyện Tam Giang. Section order 6: Paragraph: Hàn Phong trong lòng chợt động, giống như tuỳ ý mà hỏi: Section order 7: Paragraph: - Theo cô thì nên đi con đường nào? Section order 8: Paragraph: Hắn sau khi nói câu này lại tiếp tục tiêu hao 2 trí lực cho kỹ năng Phá Tâm Linh. Section order 9: Paragraph: Tường Vi im lặng một lúc lâu, giống như đang thực sự suy xét, sau đó thở dài đáp: Section order 10: Paragraph: - Tôi không biết, tôi không có chủ kiến gì, tôi chỉ muốn anh đảm bảo điều này. Section order 11: Paragraph: “ch.ết tiệt, ả này thật khó đối phó.” Section order 12: Paragraph: Hàn Phong trong lòng mắng thầm một câu, nhưng bên ngoài vẫn tỏ ra bình thản, gật đầu nói: Section order 13: Paragraph: - Tôi dự định sẽ dẫn đội ngũ dưới trướng thẳng hướng trung tâm huyện Liễu Lâm, từ đó có thể đi qua cầu Liễu Hà để tới bờ đông huyện Tam Giang. Section order 14: Paragraph: Tường Vi lập tức mỉm cười nói: Section order 15: Paragraph: - Tốt, tôi tin anh. Section order 16: Paragraph: Hàn Phong trong lòng cười lạnh, cô đương nhiên là tin rồi. Section order 17: Paragraph: Nhìn biểu hiện của nàng ta, hắn trong lòng đã...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 119.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 119: Dự đoán; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=102 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
