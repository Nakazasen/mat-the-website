# Draft Knowledge: Chương 236

- source_id: ingest-432500a59489e9bb
- raw_file: raw/Chương 236.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Sau khi nhìn chiếc xe của thôn Xuân Lê biến mất ngoài cổng căn cứ, Hàn Phong bắt đầu vòng qua phòng quân y, thăm hỏi động viên đám thương binh, phân phát cơ số phiếu lương thực vật tư, hứa hẹn cùng cam đoan đảm bảo đủ thứ, tới đây mới kết thúc quá trình “lấy lòng, giữ chân, xây dựng danh tiếng” của hắn. Section order 9: Paragraph: Xây dựng một căn cứ hơn 400 nhân khẩu, lượng exp mà cá nhân hắn thu được ngoài định mức mỗi ngày không dưới 4000 exp, sau này sẽ còn tăn...

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
- Section
- Heading
- Paragraph
- Sau
- Phong
- Trong

### Modules
- none

### Errors
- 400 nh
- 4000 exp

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
- explain Chương 236
- summarize Chương 236
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 236.docx Chapter title: Chương 236: Dùng ớt biến dị Section count: 59 Section order 1: Heading: Chương 236: Dùng ớt biến dị Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Sau khi nhìn chiếc xe của thôn Xuân Lê biến mất ngoài cổng căn cứ, Hàn Phong bắt đầu vòng qua phòng quân y, thăm hỏi động viên đám thương binh, phân phát cơ số phiếu lương thực vật tư, hứa hẹn cùng cam đoan đảm bảo đủ thứ, tới đây mới kết thúc quá trình “lấy lòng, giữ chân, xây dựng danh tiếng” của hắn. Section order 4: Paragraph: Lại lần lượt thăm qua khu nuôi trồng ươm giống, khu thử nghiệm thực phẩm chưa rõ nguồn gốc, cũng chạy qua phòng hậu cần bàn bạc công việc với Phương Tường, hầu hết vấn đề quan trọng nhất coi như đã được giải quyết xong xuôi. Section order 5: Paragraph: Trọn vẹn tiêu tốn gần một giờ đồng hồ, Hàn Phong không khỏi che miệng ngáp một cái nhìn lên vầng trăng bắt đầu treo lên cao, đã 7h tối rồi. Ngày thứ 13 dị biến, chỉ 2 ngày nữa là tròn nửa tháng, cũng là ngày trăng tròn đầu tiên sau tận thế. Section order 6: Paragraph: Hắn thản nhiên động niệm kỹ năng Ảnh Chiếu Ánh Trăng, để cho nó tự hành hấp thụ năng lực, sau đó từ tốn bước về phía nhà ăn sĩ quan. Section order 7: Paragraph: Làm người đứng đầu đâu phải lúc nào cũng sung sướng như vậy, đối nội rồi đối ngoại, cân bằng lợi ích, bày ra vẻ mặt khiến người ta mệt mỏi, chạy ngược chạy xuôi sắp tắt thở tới nơi. Trong khi người khác đang bắt đầu ôm mỹ nhân trên giường, hắn còn chưa kịp ăn uống hay tắm rửa gì đây. Section order 8: Paragraph: “Thôi, vì cái tương lai đớp tinh thạch exp miễn phí, cố g...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 236.docx; chapter_title=Chương 236: Dùng ớt biến dị; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=58 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
