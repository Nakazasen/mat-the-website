# Draft Knowledge: Chương 223

- source_id: ingest-2430710b740fde9b
- raw_file: raw/Chương 223.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Tất cả các tiểu đội trưởng khác cũng đều lặng cả người, sau đó là một cỗ bi thương xen lẫn sợ hãi thổi bùng lên trong tâm trí. Hàn Phong… Hàn Phong lại ôm theo quái vật sắp sửa tự bạo biến mất. Section order 17: Paragraph: Từng lời từng lời của Hàn Phong vang lên bên tai Tường Vi, sau đó vô hạn lặp lại tận sâu trong tâm khảm, hoá thành một cơn lốc tâm linh trùng kích khắp mọi ngõ ngách, để cho nàng cả người thoáng chốc cứng đờ. Ngay từ ngày đầu tiên gặp nhau, hắn đ...

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
- Con
- Section
- Heading
- Paragraph
- Phong
- Vi

### Modules
- none

### Errors
- 400 m

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
- explain Chương 223
- summarize Chương 223
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 223.docx Chapter title: Chương 223: Con đường từ máu và sinh mạng. Section count: 68 Section order 1: Heading: Chương 223: Con đường từ máu và sinh mạng. Section order 2: Paragraph: 9–11 minutes Section order 3: Paragraph: Khoảnh khắc Hàn Phong xách theo thể thao túng biến mất, Ngô Soái hai mắt gần như muốn nứt ra. Section order 4: Paragraph: Đâu rồi? Đại ca đi đâu rồi? Hắn mang theo quả bom nguy hiểm kia đi đâu rồi! Section order 5: Paragraph: Tất cả các tiểu đội trưởng khác cũng đều lặng cả người, sau đó là một cỗ bi thương xen lẫn sợ hãi thổi bùng lên trong tâm trí. Hàn Phong… Hàn Phong lại ôm theo quái vật sắp sửa tự bạo biến mất. Section order 6: Paragraph: Cái kia… Quái vật kia chỉ cần hét lên một tiếng, dù khoảng cách xa tới cả cây số, mấy trăm nhân loại cũng không thể nào chịu nổi. Vậy nếu một mình hứng chịu đòn toàn lực trong thời khắc cuối cùng của nó, kia sẽ là cái dạng gì khả năng… Section order 7: Paragraph: Tường Vi đứng trong đám người, khuôn mặt cũng sớm trở nên tái nhợt. Section order 8: Paragraph: “Tường Vi, rất nhanh thôi cô liền sẽ nhận ra, một tên thổ phỉ có rất nhiều thời điểm còn tốt đẹp hơn một chính khách…” Section order 9: Paragraph: “Tôi chán ghét sự tuyệt vọng, chán ghét sự chờ đợi và ban ơn…” Section order 10: Paragraph: “Chúng tôi chỉ là những sinh mạng khốn khổ không có giá trị nên bị bỏ rơi mà thôi…” Section order 11: Paragraph: “Tôi sẽ đem đến cho họ sức mạnh, đem đến cho họ hi vọng, đem đến cho họ khả năng tự cứu…” Section order 12: Paragraph: “Quyết chiến tới đây vô cùng nguy hiểm, có khả năng tôi sẽ ch.ết đi, bởi vậy t...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 223.docx; chapter_title=Chương 223: Con đường từ máu và sinh mạng.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=67 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
