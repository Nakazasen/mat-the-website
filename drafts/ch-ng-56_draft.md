# Draft Knowledge: Chương 56

- source_id: ingest-06737171e1d96a3e
- raw_file: raw/Chương 56.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 56: Thanh lý xung quanh Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 56: Thanh lý xung quanh Section order 9: Paragraph: Nhẫn hoả cầu này là của Lang Uy Nhất. Trong lúc rối bời, gã chưa kịp thôi động đã bị Hàn Phong khống chế.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- lang

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- Thanh
- Section
- Heading
- Paragraph

### Modules
- none

### Errors
- 400

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
- explain Chương 56
- summarize Chương 56
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 56.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 56: Thanh lý xung quanh Section count: 70 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 56: Thanh lý xung quanh Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Đối với chuyện này, Hàn Phong không có ý kiến gì. Ngô Soái đã cấp 7, đã thừa sức đảm đương một phía rồi. Section order 4: Paragraph: Bọn họ ở chỗ này tiêu tốn hơn 1 tiếng đồng hồ, bên kia đoán chừng cũng đã chất hết tất cả vật tư lên xe bus, xe bán tải, người nào cũng chuẩn bị tâm thế bỏ chạy khi hành động thất bại rồi. Tưởng không hay, nhưng hoá ra lại hay không tưởng, biến vụng thành khéo, sẵn tiện chạy loạn thì giờ chuyển nhà luôn. Section order 5: Paragraph: Hàn Phong cũng không rảnh rỗi, hắn đặt mục tiêu lên cấp 9 mà lại bị những chuyện ngoài lề kéo chân quá lâu, không thể chậm trễ hơn nữa, bởi vậy nhanh chóng vung tay lên, 4 chiếc nhẫn rơi lách cách trên mặt bàn. Section order 6: Paragraph: - Những người còn lại trong hành động này đều chọn một chút súng đạn làm chiến lợi phẩm, chúng ta chia nhau 4 chiếc nhẫn và phần còn lại. Về phần gậy bóng chày và trảm mã đao, chia cho đội ngũ dưới trướng. Section order 7: Paragraph: Ngô Soái khều khều, lấy một chiếc nhẫn nhanh nhẹn, một chiếc nhẫn hoả cầu. Section order 8: Paragraph: “Đinh! Nhẫn hoả cầu level 2! +1 trí lực. Có thêm kỹ năng: Hoả cầu. Triệu hồi một hoả cầu đánh vào mục tiêu, kèm theo hiệu quả bạo tạc. Mỗi ngày 2 lượt, làm lạnh 12h/lượt” Section order 9: Paragraph: Nhẫn hoả cầu này là của Lang Uy Nhất. Trong lúc rối bời, gã chưa kịp thôi động đã...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 56.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 56: Thanh lý xung quanh; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=69 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
