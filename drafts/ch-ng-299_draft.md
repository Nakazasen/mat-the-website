# Draft Knowledge: Chương 299

- source_id: ingest-4683df60a512495c
- raw_file: raw/Chương 299.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Nếu hắn đủ mạnh, quản cái gì chính phủ với xe tăng, tới liền đón, thậm chí trực tiếp công phá qua Tam Giang luôn. Chẳng qua thực lực của hắn đặt tại Liễu Lâm này có thể coi như đứng đầu, nhưng đặt tại nơi khác thực sự là không dậy nổi, vô cùng bất lực. Section order 7: Paragraph: Ngồi trong phòng hội nghị, nhìn Hàn Phong đang đọc báo cáo trên ghế chủ vị, Sử Thắng có chút tâm thần không yên. Một mặt hắn đã tránh được việc phải đối mặt với chính phủ huyện Tam Giang,...

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
- Phong
- Hi

### Modules
- none

### Errors
- 500 m
- 4000 m

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
- explain Chương 299
- summarize Chương 299
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 299.docx Chapter title: Chương 299: Tình hình thi đàn Section count: 66 Section order 1: Heading: Chương 299: Tình hình thi đàn Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Nếu hắn đủ mạnh, quản cái gì chính phủ với xe tăng, tới liền đón, thậm chí trực tiếp công phá qua Tam Giang luôn. Chẳng qua thực lực của hắn đặt tại Liễu Lâm này có thể coi như đứng đầu, nhưng đặt tại nơi khác thực sự là không dậy nổi, vô cùng bất lực. Section order 4: Paragraph: Chỉ có cách tạm thời câu giờ, lợi dụng thời gian trống này nhằm nỗ lực gia tăng thực lực cá nhân, gia tăng lực ngưng tụ tập thể, chế tạo ra một quân đoàn vừa thiện chiến vừa sẵn sàng nhận lệnh, đó mới là con đường phát triển chính xác. Section order 5: Paragraph: Tạm gác việc này lại, Hàn Phong bước lên xe bán tải cùng với Ngô Soái trở về căn cứ. Việc lùng sục huyện thị này không thể xong ngay được, nhưng tình báo về thi đàn tại Xuân Lê, hẳn là đã về tới rồi. Section order 6: Paragraph: Quả nhiên khi bọn họ trở lại tổng bộ trấn Hi Vọng, đám người Sử Thắng đã mang theo tin tức tình báo từ tiền tuyến trở về. Section order 7: Paragraph: Ngồi trong phòng hội nghị, nhìn Hàn Phong đang đọc báo cáo trên ghế chủ vị, Sử Thắng có chút tâm thần không yên. Một mặt hắn đã tránh được việc phải đối mặt với chính phủ huyện Tam Giang, một mặt hắn lại hơi cắn rứt khi đã né tránh việc này, cắn rứt khi đã “phản bội”. Section order 8: Paragraph: Hàn Phong vẫn chuyên chú đọc nhẩm báo cáo, trong lòng càng lúc càng cảm thấy trầm trọng, đồng thời cũng cảm giác một cỗ nguy cơ vô hình đang bao phủ. Section orde...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 299.docx; chapter_title=Chương 299: Tình hình thi đàn; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=65 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
