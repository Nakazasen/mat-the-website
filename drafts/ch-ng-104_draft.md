# Draft Knowledge: Chương 104

- source_id: ingest-7dd042fc1250a7b6
- raw_file: raw/Chương 104.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 104: Chuẩn bị trước đại chiến Section order 16: Paragraph: Xuân Hoa Xuân Thu mang theo hồi hộp tiến vào phòng. Nhưng sau khi nhận ra chủ nhân còn dậy sớm hơn các nàng, đã sớm làm xong công tác cá nhân, mặc vào y phục chiến đấu thường ngày, các nàng không khỏi dâng lên xấu hổ. Section order 35: Paragraph: Sau giai đoạn chào hỏi, Hàn Phong nhìn một vòng rồi gật đầu ra hiệu, Liễu Huyên sớm chuẩn bị xong, đưa tới tay từng tiểu đội trưở...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- tham

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
- explain Chương 104
- summarize Chương 104
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 104.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 104: Chuẩn bị trước đại chiến Section count: 102 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 104: Chuẩn bị trước đại chiến Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Cũng may quá trình săn bắn không gặp trắc trở gì cả, bọn họ thuận lợi thăng cấp, an toàn trở về. Section order 4: Paragraph: Nghĩ tới xong xuôi, Hàn Phong nhanh chóng hoàn thành tắm rửa, sau đó mặc vào đồ ngủ chui lên giường đắp chăn. Section order 5: Paragraph: Cần phải nghỉ ngơi đầy đủ mới có sức cho đại chiến ngày mai. Section order 6: Paragraph: Một lúc sau, hắn lại tỉnh lại, chạy vào phòng tắm bê ra một chậu nước, sau đó búng tay biến chậu nước thành băng đá. Section order 7: Paragraph: Thời tiết quá nóng, phải có đá lạnh giải toả nhiệt độ mới coi như ổn thoả được. Section order 8: Paragraph: Thời điểm những ngày đầu tiên, băng đá hắn tạo ra rất nhanh sẽ tan rã do cạn kiệt năng lượng gia trì. Sau bao nhiêu cường hoá, hiện tại nó có thể duy trì cả đêm cũng không tan hết. Section order 9: Paragraph: Quả nhiên sau khi có không khí mát mẻ tràn ngập, hắn đã ngủ rất ngon giấc. Section order 10: Paragraph: Sáng hôm sau, mặt trời còn chưa có ló dạng, Hàn Phong đã tỉnh lại. Section order 11: Paragraph: Hắn trước đây đã luôn dậy sớm như vậy. Cơm áo gạo tiền, nhân viên tầng chót phải tự học cách thức giấc mà tới giờ làm chấm công, hiện tại xem như vẫn giữ lại được thói quen tốt này. Section order 12: Paragraph: Bây giờ cũng không thể buông lỏng được, bên ngoài tuy không có nợ nần tiền bạc truy...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 104.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 104: Chuẩn bị trước đại chiến; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=101 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
