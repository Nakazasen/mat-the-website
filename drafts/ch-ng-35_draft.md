# Draft Knowledge: Chương 35

- source_id: ingest-74aa12a1641e0770
- raw_file: raw/Chương 35.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 35: Lại chiến F1 Section order 8: Paragraph: 5 chiếc xe với 15 người sống sót lục tục đi xuống. Lần hành động này chỉ có Đinh Vũ và Triệu Hà Vân ở lại canh chừng, những người còn lại, bao quát hai đứa bé gái Phương Hoa, Đinh Tịnh Nhi, đều được huy động đi thu gom vật tư. Section order 16: Paragraph: Hàn Phong cảnh giác nhìn quanh, vừa chém giết thây ma bị hấp dẫn tới, vừa đề phòng có biến xuất hiện. Khu vực này từng bị thể thôn phệ...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- thanh

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- F1 Section
- Section
- Heading
- Paragraph

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
- explain Chương 35
- summarize Chương 35
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 35.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 35: Lại chiến F1 Section count: 89 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 35: Lại chiến F1 Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Tận thế nguy hiểm, nhưng vẫn ẩn chứa cơ hội lớn lao. Người tụt hậu giai đoạn đầu, nếu có cơ duyên tốt thì vẫn có một đường để xoay người. Section order 4: Paragraph: Đằng sau ghế sau, Chu Vấn đang nhiệt tình tham khảo ý kiến của Ngô Soái, mà người kia cũng tương đối thoải mái chỉ cho hắn kinh nghiệm chiến đấu. Dạo gần đây Ngô Soái thường xuyên luyện tập nín hơi, vậy nên khi có cơ hội nói chuyện, hắn đều nói rất nhiều. Section order 5: Paragraph: Đoàn xe 5 chiếc tông ngã hàng loạt thây ma, chẳng mấy chốc đã tới cửa hàng tiện lợi. Section order 6: Paragraph: Hàn Phong là người đầu tiên nhảy xuống xe, hắn tiện tay chém bay đầu một thây ma level 1, sau đó kêu lên: Section order 7: Paragraph: - Ngô Soái, Phương Tường, Mã Mộng Đình phụ trách cảnh giới, những người còn lại mau vào cửa hàng thu thập vật tư! Section order 8: Paragraph: 5 chiếc xe với 15 người sống sót lục tục đi xuống. Lần hành động này chỉ có Đinh Vũ và Triệu Hà Vân ở lại canh chừng, những người còn lại, bao quát hai đứa bé gái Phương Hoa, Đinh Tịnh Nhi, đều được huy động đi thu gom vật tư. Section order 9: Paragraph: Hàn Phong cầm thanh phong đao chém bay đầu một thây ma cấp ba, trong miệng thởi dài tiếc nuối. Section order 10: Paragraph: Vận khí vẫn kém như vậy, một cái rắm cũng không rơi ra. Section order 11: Paragraph: Bên phía đối diện, Ngô Soái hai ta...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 35.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 35: Lại chiến F1; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=88 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
