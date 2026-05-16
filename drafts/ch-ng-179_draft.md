# Draft Knowledge: Chương 179

- source_id: ingest-0f3f4fbd1375900d
- raw_file: raw/Chương 179.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Hàn Phong ngồi trên một chiếc xe jeep nhìn đoàn quân dũng mãnh tiến về phía trước. Trong số này có người là sinh viên, có người là công nhân, có người là nông dân, có người là nhân viên văn phòng, cũng có người vô công rồi nghề đầu đường xó chợ. Bọn họ hiện tại đều có chung mục đích: đánh hạ thi triều, giải phóng trung tâm huyện Liễu Lâm, cứu sống mấy trăm người sống sót đang mắc kẹt. Section order 51: Paragraph: Theo sau sự cổ động của Hàn Phong, tinh thần của đám...

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
- Section
- Heading
- Paragraph
- Phong
- Trong
- Xe

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
- explain Chương 179
- summarize Chương 179
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 179.docx Chapter title: Chương 179: Có sợ chết không? Section count: 65 Section order 1: Heading: Chương 179: Có sợ chết không? Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Từng hàng dài đội viên dựa theo sự sắp xếp phân công từ trước bắt đầu tiến về phía ba đường nhánh. Chiến trường chỉ cách điểm tập kết hành quân hơn 1 cây số, bởi vậy tất cả mọi người đều là cuốc bộ. Những chiếc xe jeep cơ động cao đa phần là chở đạn, lựu đạn, súng máy hạng nặng, súng phóng lựu, quân tư trang tiếp tế và hậu cần quân y như băng gạc và thuốc sát trùng. Section order 4: Paragraph: Hàn Phong ngồi trên một chiếc xe jeep nhìn đoàn quân dũng mãnh tiến về phía trước. Trong số này có người là sinh viên, có người là công nhân, có người là nông dân, có người là nhân viên văn phòng, cũng có người vô công rồi nghề đầu đường xó chợ. Bọn họ hiện tại đều có chung mục đích: đánh hạ thi triều, giải phóng trung tâm huyện Liễu Lâm, cứu sống mấy trăm người sống sót đang mắc kẹt. Section order 5: Paragraph: Mục tiêu kia một nửa là thật, một nửa chính là do Hàn Phong vẽ ra. Section order 6: Paragraph: Làm gì có cái thứ gọi là cứ điểm người sống sót chứ. Section order 7: Paragraph: Mỗi cuộc chiến đều cần có ý nghĩa của nó. Chỉ cần có ý nghĩa, người tham chiến sẽ có động lực, có quyết tâm, có cố gắng. Nếu không thể tìm ra ý nghĩa đủ lớn, vậy tốt nhất vắt óc mà bịa ra, để cho mọi người nhìn thấy mục tiêu và hi vọng, nỗ lực truy cầu nó. Section order 8: Paragraph: Tới khi đạt mục đích, tìm một cái cớ đủ tốt đẹp, sau đó đưa ra thành quả thay thế tương đương để lấp ɭϊếʍƈ là...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 179.docx; chapter_title=Chương 179: Có sợ chết không?; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=64 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
