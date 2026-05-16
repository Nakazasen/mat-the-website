# Draft Knowledge: Chương 178

- source_id: ingest-ef23c7247bf5e8f1
- raw_file: raw/Chương 178.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Nghe thấy âm điệu lạnh nhạt của Hàn Phong, những người ở đây đều mơ hồ bốc lên một hơi lãnh khí, sau đó đều đồng loạt rùng mình. Section order 6: Paragraph: Hàn Phong bình thường tương đối điệu thấp, cách làm người cũng vô cùng khép kín, cực kỳ ít khi giao lưu hay trao đổi chuyện riêng với người khác. Ngoài những lúc giao tiếp với Ngô Soái, mọi người gần như không thấy hắn cười đùa bao giờ, bởi vậy những tiểu đội trưởng đều dần dần dâng lên cảm giác Hàn Phong vô cù...

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
- Phong
- Nghe
- Hi

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
- explain Chương 178
- summarize Chương 178
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 178.docx Chapter title: Chương 178: Trước đại chiến (2) Section count: 68 Section order 1: Heading: Chương 178: Trước đại chiến (2) Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong dừng một chút rồi lại trầm giọng nói: Section order 4: Paragraph: - Các vị nên đốc thúc đội viên chấp hành cho nghiêm chỉnh, tốt nhất đừng để tôi phải tự mình ra tay. Section order 5: Paragraph: Nghe thấy âm điệu lạnh nhạt của Hàn Phong, những người ở đây đều mơ hồ bốc lên một hơi lãnh khí, sau đó đều đồng loạt rùng mình. Section order 6: Paragraph: Hàn Phong bình thường tương đối điệu thấp, cách làm người cũng vô cùng khép kín, cực kỳ ít khi giao lưu hay trao đổi chuyện riêng với người khác. Ngoài những lúc giao tiếp với Ngô Soái, mọi người gần như không thấy hắn cười đùa bao giờ, bởi vậy những tiểu đội trưởng đều dần dần dâng lên cảm giác Hàn Phong vô cùng xa cách, thậm chí có chút lãnh cảm lạnh lùng, vô cùng khó tiếp cận. Section order 7: Paragraph: Hàn Phong cũng chưa từng trực tiếp đặt ra luật lệ cụ thể nào nhằm vào việc quản lý đội viên, hắn gần như buông lỏng kỷ cương, toàn quyền uỷ thác cho tiểu đội trưởng chỉ huy thành viên dưới trướng, không có bất kỳ đụng tay đụng chân nào vào nội bộ của cá nhân đoàn đội. Section order 8: Paragraph: Nhưng cách hành xử như vậy không có nghĩa là hắn không có uy vọng. Trái lại, uy vọng của hắn càng lúc càng lớn. Càng không nhìn thấy rõ hắn thế nào, người khác càng thêm kính sợ. Section order 9: Paragraph: Đây chính là lần đầu tiên hắn ban hành thiết quân luật nhằm thẳng vào kỷ cương đội ngũ. Section order...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 178.docx; chapter_title=Chương 178: Trước đại chiến (2); ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=67 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
