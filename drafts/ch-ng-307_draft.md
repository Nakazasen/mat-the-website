# Draft Knowledge: Chương 307

- source_id: ingest-ee889258425e6aab
- raw_file: raw/Chương 307.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Nghe được cái tin tức này, Hàn Phong trong lòng không khỏi hiện lên suy tư, bên kia có quyết định nhanh như vậy? Bọn họ đang vội vàng điều gì à? Section order 4: Paragraph: Theo dự tính của hắn, chính quyền huyện Tam Giang hẳn là sẽ tới vào buổi sáng ngày mai mới đúng. Nếu đã rơi vào thời điểm hiện tại thì phải là đang dẫn binh tới đánh một trận tơi bời rồi, nhân viên công tác sẽ không có thái độ tương đối bình tĩnh như vậy… Section order 13: Paragraph: Hắn không n...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- level

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Nghe
- Phong
- Theo

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
- explain Chương 307
- summarize Chương 307
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 307.docx Chapter title: Chương 307: Vội vàng Section count: 73 Section order 1: Heading: Chương 307: Vội vàng Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Nghe được cái tin tức này, Hàn Phong trong lòng không khỏi hiện lên suy tư, bên kia có quyết định nhanh như vậy? Bọn họ đang vội vàng điều gì à? Section order 4: Paragraph: Theo dự tính của hắn, chính quyền huyện Tam Giang hẳn là sẽ tới vào buổi sáng ngày mai mới đúng. Nếu đã rơi vào thời điểm hiện tại thì phải là đang dẫn binh tới đánh một trận tơi bời rồi, nhân viên công tác sẽ không có thái độ tương đối bình tĩnh như vậy… Section order 5: Paragraph: Hiện tại cũng đã 6 giờ rồi, chỉ khoảng hơn nửa tiếng nữa là trời sẽ tối. Hàn Phong vốn không định chiến đấu trong điều kiện bất lợi như vậy, nhưng nhóm người bên kia đã tới, hắn không ngại làm ra vài cử động trái với lẽ thường. Section order 6: Paragraph: - Toàn quân lui lại một cây số, tiến hành thong thả tiêu diệt thây ma bình thường, huấn luyện tác chiến trong môi trường đêm tối! Section order 7: Paragraph: Nghe lệnh của hắn, toàn quân đều hô vang đáp lại: Section order 8: Paragraph: - Tuân lệnh! Section order 9: Paragraph: Đoàn xe nối đuôi nhau lui về phía sau 1 cây số rồi bắt đầu tiến hành bố trí công sự, ngăn cản thây ma xâm nhập từ nhiều hướng. Người căng đèn chiếu sáng, người căng lưới vải chặn đường, người thì bắt đầu rút trảm mã đao tiến hành săn lùng thây ma xung quanh. Section order 10: Paragraph: “Lợi thế” của việc đóng quân xung quanh khu vực có tồn tại Thể Thao Túng chính là không có thây ma loại hình tiến hoá tồn...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 307.docx; chapter_title=Chương 307: Vội vàng; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=72 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
