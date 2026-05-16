# Draft Knowledge: Chương 388

- source_id: ingest-084e753063e5b7a1
- raw_file: raw/Chương 388.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Nghe được âm thanh nửa xa lạ nửa quen thuộc này, Hàn Phong rốt cuộc cũng thở ra một hơi may mắn. Tốt rồi, gián điệp vẫn chưa bị làm thịt, chứng tỏ chính quyền Tam Giang chưa tới mức trở mặt ngay sau đại chiến, đám người chạy qua bên đó xem như vẫn tương đối an toàn. Section order 6: Paragraph: Sau đoạn tâm tình này, đối phương bắt đầu báo cáo lại chi tiết bộ khung pháp lý mà căn cứ người sống sót huyện Tam Giang đang áp dụng, bắt đầu từ những điều khoản chung lớn n...

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
- Nghe
- Phong
- Tam Giang

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
- explain Chương 388
- summarize Chương 388
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 388.docx Chapter title: Chương 388: Chiến tranh tới gần Section count: 55 Section order 1: Heading: Chương 388: Chiến tranh tới gần Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Nghe được âm thanh nửa xa lạ nửa quen thuộc này, Hàn Phong rốt cuộc cũng thở ra một hơi may mắn. Tốt rồi, gián điệp vẫn chưa bị làm thịt, chứng tỏ chính quyền Tam Giang chưa tới mức trở mặt ngay sau đại chiến, đám người chạy qua bên đó xem như vẫn tương đối an toàn. Section order 4: Paragraph: Sau câu chào hỏi quen thuộc, vẫn như cũ là một chút tâm tình thường lệ, chủ yếu xoay quanh tình hình những người đã di chuyển qua bên kia sông đang sống sót ra sao, cuộc sống mới thế nào, đã ổn định và hoà nhập môi trường hay chưa, cùng với tình hình thăng cấp cả về thực lực cá nhân lẫn địa vị nắm giữ, thậm chí là sơ lược về việc mỗi người đang gặp phải khó khăn vướng mắc gì. Section order 5: Paragraph: Nghe qua thật không thể không liên tưởng tới một đoạn báo cáo trong cuộc họp thường nhật tại trấn Hi Vọng, có điều điễn đạt theo hướng thoải mái tuỳ tiện hơn, tương đối giống một cuộc trò chuyện giữa hai người bạn. Section order 6: Paragraph: Sau đoạn tâm tình này, đối phương bắt đầu báo cáo lại chi tiết bộ khung pháp lý mà căn cứ người sống sót huyện Tam Giang đang áp dụng, bắt đầu từ những điều khoản chung lớn nhất cho tới điều khoản riêng nhỏ nhất, các điều khoản vụ, điều khoản bổ sung, phụ lục, ghi chú, trọn vẹn 30 phút vừa lắng nghe vừa ghi chép, một tập giấy A4 dày 63 trang đã được Hàn Phong ghi chép xuống trước mặt. Section order 7: Paragraph: Đây là tình báo m...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 388.docx; chapter_title=Chương 388: Chiến tranh tới gần; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=54 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
