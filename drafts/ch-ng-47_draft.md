# Draft Knowledge: Chương 47

- source_id: ingest-872112cd4844c521
- raw_file: raw/Chương 47.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 47: Cấp 8 Section order 8: Paragraph: Hàn Phong nhảy vào đàn thây ma, Thanh Phong Đao chém xéo, chém bay đầu một thây ma level 5. Section order 12: Paragraph: Hao ít, hồi nhiều, Hàn Phong nếu toàn lực chém giết không nghỉ ngơi thì trong một tiếng cũng hao hết 6, 7 thể lực mà thôi. Nếu vừa đánh vừa nghỉ, có lẽ chỉ hao hết 3, 4 điểm.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- nhanh

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Thi

### Modules
- none

### Errors
- 450 exp l

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
- explain Chương 47
- summarize Chương 47
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 47.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 47: Cấp 8 Section count: 91 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 47: Cấp 8 Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Tất nhiên phòng ngự của bọn họ không phải vô địch. Thi triển phòng ngự tiêu hao thể lực, trí lực cực lớn, cản mỗi viên đạn đều để bọn họ tiêu hao tài nguyên. Nếu có vài người cầm súng vây công, bọn họ sẽ bị mài ch.ết sau vài phút. Bất quá, có thể phòng ngự súng đạn, kia đã là tồn tại phi nhân loại rồi. Section order 4: Paragraph: Hàn Phong nạp lại đạn cho D.E, đeo nó bên hông, sau đó rút thanh phong đao, nhảy vào đám thây ma nói: Section order 5: Paragraph: - Cô gắng cho tới bữa trưa, chúng ta phải thanh lý thêm 50 mét nữa! Section order 6: Paragraph: Nhóm người xung quanh cũng bốc lên khí thế ngút trời: Section order 7: Paragraph: - Chúng ta lên! Section order 8: Paragraph: Hàn Phong nhảy vào đàn thây ma, Thanh Phong Đao chém xéo, chém bay đầu một thây ma level 5. Section order 9: Paragraph: Tuy rằng không rơi ra thứ đồ gì cả, nhưng hắn ngược lại tương đối hài lòng với thực lực của bản thân. Nếu là ngày đầu tiên khi đối diện một thây ma thế này, hắn phải dựa vào mưu mẹo cùng mồi nhử là Phương Tường, Liễu Huyên mới có thể đánh lén nó, còn tiêu tốn mất hai thể lực. Mà bây giờ thây ma dạng này trước mặt hắn không khác nào kiến hôi, chém mười con mới hao 1 thể lực. Section order 10: Paragraph: Sức mạnh, tốc độ cao khiến việc chém giết ít tiêu hao hơn, mà thể lực, hồi phục cao khiến thể lực duy trì bền bỉ hơn, tốc đồ hồi phục lại cũng...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 47.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 47: Cấp 8; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=90 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
