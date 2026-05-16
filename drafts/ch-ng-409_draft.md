# Draft Knowledge: Chương 409

- source_id: ingest-d68d8059d2b5a2fa
- raw_file: raw/Chương 409.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: - Mày không tự sát à? "ch.ết tiệt... Tại sao lũ khốn này lại có thiên tài địa bảo của Tam Giang chứ..." Section order 6: Paragraph: Thua trận không thua khí thế, Chương Lãm nghiến răng gầm gừ một câu, đồng thời đưa ánh mắt lạnh lẽo tới ghê rợn nhìn qua Hàn Phong, đáp lại hắn chính là một cú sút bằng gầm giầy thẳng vào giữa mặt. Section order 8: Paragraph: Hàn Phong đá một cú ngay giữa mặt tên này, đá hắn bay về phía Ngô Soái và Chu Vấn đang đứng bên cạnh rồi thản n...

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
- Tam Giang
- Tao
- Thua

### Modules
- none

### Errors
- 409

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
- explain Chương 409
- summarize Chương 409
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 409.docx Chapter title: Chương 409 Section count: 90 Section order 1: Heading: Chương 409 Section order 2: Paragraph: 11–14 minutes Section order 3: Paragraph: - Mày không tự sát à? "ch.ết tiệt... Tại sao lũ khốn này lại có thiên tài địa bảo của Tam Giang chứ..." Section order 4: Paragraph: Hắn đang trúng phải hiệu ứng áp chế từ nho đen biến dị, tạm thời không thể sử dụng kỹ năng trên bậc nhị giai, chỉ dựa vào bộ trang bị thì tuyệt đối không làm nên cơm cháo gì cả. Section order 5: Paragraph: - Tao là sát thủ, không phải samurai mà tự sát! Section order 6: Paragraph: Thua trận không thua khí thế, Chương Lãm nghiến răng gầm gừ một câu, đồng thời đưa ánh mắt lạnh lẽo tới ghê rợn nhìn qua Hàn Phong, đáp lại hắn chính là một cú sút bằng gầm giầy thẳng vào giữa mặt. Section order 7: Paragraph: Bốp! Section order 8: Paragraph: Hàn Phong đá một cú ngay giữa mặt tên này, đá hắn bay về phía Ngô Soái và Chu Vấn đang đứng bên cạnh rồi thản nhiên nói: Section order 9: Paragraph: - Tốt thôi, tước hết trang bị của hắn đi. Section order 10: Paragraph: Ngô Soái hưng phấn thò tay tát bốp một cái nữa, đem Chương Lãm tát ngất ngay tại chỗ, sau đó là nhanh nhẹn đem cả 10 chiếc nhẫn trên tay gã này tháo xuống. Chu Vấn cũng lột áo khoác tận thế, vòng cổ, giày phản lực, đai lưng, kính mắt... của tên này, tổng cộng trên người gã ta có gần 20 món vật phẩm, trong đó có tới 13 khoả trang bị level 3. Section order 11: Paragraph: Số lượng tài nguyên cấp cao này gần tương đương với tài nguyên của thi đàn 2 vạn nơi đầu cầu Liễu Hà rồi, có thể nói tên sát thủ này được đầu tư vô cùng nh...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 409.docx; chapter_title=Chương 409; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=89 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
