# Draft Knowledge: Chương 361

- source_id: ingest-2a154ba494e8ced6
- raw_file: raw/Chương 361.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Hai người Hà Tam, Triệu Nhược Pháp được đội viên công tác dẫn đường vào cuộc họp, đi cùng với họ còn có cả Hoàng Khải, phó trưởng phòng thông tin liên lạc. Section order 5: Paragraph: Sau khi khách sáo sơ qua một chút, Hoàng Khải từ trong cặp đen lấy ra một vài tờ A4 đưa lên bên trên, Hàn Phong sau khi tiếp nhận rồi đọc qua thì âm thầm gật đầu. Hà Tam vẫn rất được việc, những yêu cầu cơ bản mà hắn giao chỉ tiêu, tên kia đều hoàn thành trong hạn mức cho phép. Sectio...

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
- Hai
- Tam
- Thanh

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
- explain Chương 361
- summarize Chương 361
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 361.docx Chapter title: Chương 361: Kích động mâu thuẫn Section count: 71 Section order 1: Heading: Chương 361: Kích động mâu thuẫn Section order 2: Paragraph: 11–13 minutes Section order 3: Paragraph: Hai người Hà Tam, Triệu Nhược Pháp được đội viên công tác dẫn đường vào cuộc họp, đi cùng với họ còn có cả Hoàng Khải, phó trưởng phòng thông tin liên lạc. Section order 4: Paragraph: Lạc Thanh Thuỷ trước đó rảnh rỗi bồi hồi ở bên này nghịch ngợm thuyền bè, hiện tại chiến sự Diệu Liên diễn ra cao trào, nàng ta rốt cuộc cũng không thể thoát thân được nữa, đã hoàn toàn ở lại bên kia tham gia chiến đấu rồi. Section order 5: Paragraph: Sau khi khách sáo sơ qua một chút, Hoàng Khải từ trong cặp đen lấy ra một vài tờ A4 đưa lên bên trên, Hàn Phong sau khi tiếp nhận rồi đọc qua thì âm thầm gật đầu. Hà Tam vẫn rất được việc, những yêu cầu cơ bản mà hắn giao chỉ tiêu, tên kia đều hoàn thành trong hạn mức cho phép. Section order 6: Paragraph: Trên tay hắn là bản ghi nhớ hợp tác chung, dưới nguyên tắc đồng thuận và bình đẳng về mặt lợi ích, hai bên sẽ có mối quan hệ ngang hàng. Thế nhưng về mặt tính chính thống thì vẫn phải từ bỏ sử dụng tên gọi trấn Hi Vọng, đây là giới hạn cuối cùng không thể thay đổi. Section order 7: Paragraph: Chính quyền huyện Tam Giang sẽ không yêu cầu giải giáp vũ khí bên phía Liễu Lâm này nữa, bù lại, Hàn Phong phải cử quân qua hỗ trợ bọn họ giải quyết thi đàn tại Diệu Liên, mà cụ thể ở đây là Ngô Soái sẽ phải đứng ra gia trì năng lực đạn pháo giúp họ. Section order 8: Paragraph: Ngoài ra, trấn Hi Vọng phải ra tay tiêu diệt thi đàn hơn 2 vạn...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 361.docx; chapter_title=Chương 361: Kích động mâu thuẫn; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=70 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
