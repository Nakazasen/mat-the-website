# Draft Knowledge: Chương 360

- source_id: ingest-254690fd629837ee
- raw_file: raw/Chương 360.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Hàn Phong còn nhớ rõ tại đầu cầu Lệ Giang có một quái vật Thể Thôn Phệ level 30 đang trấn giữ, hiện tại hắn không rõ nó đã tiến hoá tới cấp độ bao nhiêu, thế nhưng trước đó nó chỉ cần hét một tiếng đã đủ chấn bị thương nặng mấy người Ngô Soái đứng cách xa cả cây số. Quái vật tại phương hướng trấn Hạ Sa còn mạnh hơn thế. Một đầu Eat-3 level 32. Section order 9: Paragraph: Tin mừng là Chu Vấn đã phát hiện ra “yếu điểm” của Thể Thao Túng. Quái vật kia hoàn toàn ngó lơ...

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
- Giang
- Sa

### Modules
- none

### Errors
- 500-1000m khi

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
- explain Chương 360
- summarize Chương 360
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 360.docx Chapter title: Chương 360: Thiếu thốn nhân tài Section count: 47 Section order 1: Heading: Chương 360: Thiếu thốn nhân tài Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Việc đối diện một thi đàn luôn luôn là việc cực kỳ khó khăn, thế nhưng việc đối diện một quái vật cấp cao cũng là việc khó khăn tới tuyệt vọng, nhất là với loại quái vật như Thể Thôn Phệ, thứ sinh vật có năng lực tác chiến kinh khủng nhất trong số các chủng loài thây ma. Section order 4: Paragraph: Hàn Phong còn nhớ rõ tại đầu cầu Lệ Giang có một quái vật Thể Thôn Phệ level 30 đang trấn giữ, hiện tại hắn không rõ nó đã tiến hoá tới cấp độ bao nhiêu, thế nhưng trước đó nó chỉ cần hét một tiếng đã đủ chấn bị thương nặng mấy người Ngô Soái đứng cách xa cả cây số. Quái vật tại phương hướng trấn Hạ Sa còn mạnh hơn thế. Một đầu Eat-3 level 32. Section order 5: Paragraph: Một đội quân có thể chiến thắng một thi đàn, bởi vì 95% thành phần thi đàn là các cá thể yếu nhược hơn nhân loại, 5% kia cũng vẫn trong tầm nhận thức, nhân loại vẫn có thể phản ứng lại. Nhưng khi đối diện một quái vật có cấp độ cao vượt trội, vượt thoát khỏi tầm nhận thức, vậy thì 95% nhân loại cũng chỉ là mồi nhắm mà thôi, thậm chí là 99% nhân loại khi đối diện Eat-3 đều không thể phản ứng. Section order 6: Paragraph: Người ta thường nói lượng biến sẽ sinh ra chất biến, thế nhưng để “biến” được thì cần rất nhiều điều kiện. Trấn Hi Vọng đã thất bại trong việc tìm kiếm kỹ năng có thể tổng hợp sức mạnh khi giết Thể Thao Túng M2 level 28, đó chính là chiếc chìa khoá để dẫn tới chất biến, bọn họ khô...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 360.docx; chapter_title=Chương 360: Thiếu thốn nhân tài; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=46 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
