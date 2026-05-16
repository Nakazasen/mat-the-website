# Draft Knowledge: Chương 202

- source_id: ingest-c2a4e47078fe68b4
- raw_file: raw/Chương 202.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 11: Paragraph: Nếu coi chiến công của tất cả những người trong doanh trướng là 100%, vậy thì Hàn Phong chiếm tới 55% điểm chiến công, Ngô Soái là 15%, Chu Vấn 7%, Tường Vi 5%, Châu Lam 4% hơn chục người còn lại chiếm 14%. Đó là về mặt số liệu, trên thực tế, nếu không có Hàn Phong dẫn dắt áp trận, thiết lập bố cục, sẽ chẳng có chiến công nào ở đây cả. Section order 12: Paragraph: Hơn chục tiểu đội trưởng và tiểu đội trưởng dự bị đều là hai mặt nhìn nhau, sau đó tiếp tục nở nụ cườ...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- giai
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Theo
- Quang

### Modules
- none

### Errors
- 400 exp c

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
- explain Chương 202
- summarize Chương 202
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 202.docx Chapter title: Chương 202: Phân chia chiến lợi phẩm. Section count: 68 Section order 1: Heading: Chương 202: Phân chia chiến lợi phẩm. Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Một buổi sáng xuất ra 12 bản kỹ năng tam giai, đó là còn chưa kể tới một bản Thần Tốc đã được Hàn Phong học tập lúc trước. Chiến tranh quả thật sẽ đồng nghĩa với huỷ diệt, nhưng cũng song hành với tăng trưởng phát triển, đây chính là ví dụ trực quan nhất. Section order 4: Paragraph: “Đinh! Kỹ năng bị động tam giai: Cuốn Theo Chiều Gió. Kỹ năng thuộc tính: di chuyển thuận chiều gió sẽ nhận được điểm nhanh nhẹn gia trì ngẫu nhiên từ 50% - 100% tốc độ gió, di chuyển ngược chiều gió sẽ nhận được nhanh nhẹn gia trì từ 10 - 30% tốc độ gió. Kỹ năng không thể học tập trùng lặp, có thể cường hoá cùng tiến giai.” Section order 5: Paragraph: “Đinh! Kỹ năng chủ động tam giai: Quang Giáp. Kỹ năng thuộc tính: kích phát một quang giáp hư ảo ngăn chặn công kích đánh tới. Kỹ năng tiêu hao: mỗi 3 giây tiêu hao 2 thể lực, 1 trí lực. Uy lực kỹ năng phụ thuộc chỉ số thể lực, trí lực. Kỹ năng có thể cường hoá cùng tiến giai.” Section order 6: Paragraph: “Đinh! Kỹ năng chủ động tam giai: Tấn Công Điểm Yếu! Kỹ năng thuộc tính: mỗi công kích trúng đích sẽ phá vỡ 1% điểm thể lực, 1% điểm phục hồi, 1% điểm chống chịu mục tiêu trong 5 giây. Khi cộng dồn đủ 100% phá vỡ, đòn đánh tiếp theo sẽ đạt hiệu quả chí mạng (Hiệu ứng chí mạng không vượt quá 5 cấp độ). Kỹ năng kích hoạt: mỗi 5 giây tiêu hao 6 thể lực. có thể kích hoạt liên tục. Kỹ năng không thể học tập trùng lặp, có...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 202.docx; chapter_title=Chương 202: Phân chia chiến lợi phẩm.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=67 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
