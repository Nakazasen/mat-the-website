# Draft Knowledge: Chương 261

- source_id: ingest-7cb3f00d10489411
- raw_file: raw/Chương 261.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 7: Paragraph: Cao tầng thôn Xuân Lê có tam đương gia, ngũ đại tướng, cùng vài tiểu đầu mục lâu nhâu khác, trong đó có một vị đương gia và 3 tên đại tướng muốn làm phản sao, Đổng Thành làm người cũng thật thất bại, Hà Tam xin của hắn 3 chiếc nhẫn chống chịu, chẳng lẽ chính là 3 người này? Section order 9: Paragraph: - Anh điều chỉnh kế hoạch một chút, nói cần tăng cường phòng thủ cho nhóm đội viên yếu nhược, đồng thời cung cấp nước uống đầy đủ cho họ. Xin ý kiến bên kia xem thế n...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- theo

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Con
- Section
- Heading
- Paragraph
- Phong
- Tam

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
- explain Chương 261
- summarize Chương 261
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 261.docx Chapter title: Chương 261: Con bài tẩy của Đổng Thành Section count: 59 Section order 1: Heading: Chương 261: Con bài tẩy của Đổng Thành Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Vài phút sau, Lý Võ Lạc đã mang theo một tập tài liệu tới tìm Hàn Phong báo cáo: Section order 4: Paragraph: - Thủ lĩnh, đây là kế hoạch tác chiến buổi chiều, mời thủ lĩnh cho ý kiến và phê duyệt. Section order 5: Paragraph: Hàn Phong đưa tay tiếp nhận, hắn nhìn sơ qua một chút sắp xếp tổ chức tấn công chiều nay, sau đó tập trung nhìn vào 4 cái tên đứng liền nhau. Section order 6: Paragraph: Hà Tam, Uông Hùng, Thường Vân, Triệu Nhược Pháp. Section order 7: Paragraph: Cao tầng thôn Xuân Lê có tam đương gia, ngũ đại tướng, cùng vài tiểu đầu mục lâu nhâu khác, trong đó có một vị đương gia và 3 tên đại tướng muốn làm phản sao, Đổng Thành làm người cũng thật thất bại, Hà Tam xin của hắn 3 chiếc nhẫn chống chịu, chẳng lẽ chính là 3 người này? Section order 8: Paragraph: Hàn Phong trầm ngâm một lát rồi nhẹ nhàng dùng bút chì gạch một đường mờ nhạt xuống dưới chân 4 cái tên này, lại tiếp tục gạch xuống vài cái tên bất kỳ cả quân ta lẫn quân mình, sau đó nói với Lý Võ Lạc: Section order 9: Paragraph: - Anh điều chỉnh kế hoạch một chút, nói cần tăng cường phòng thủ cho nhóm đội viên yếu nhược, đồng thời cung cấp nước uống đầy đủ cho họ. Xin ý kiến bên kia xem thế nào. Section order 10: Paragraph: Lý Võ Lạc có chút khó hiểu, mệnh lệnh này của Hàn Phong tương đối chung chung, không đưa ra chỉ đạo nào cụ thể. Như là phân bổ bao nhiêu phòng thủ, phòng thủ t...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 261.docx; chapter_title=Chương 261: Con bài tẩy của Đổng Thành; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=58 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
