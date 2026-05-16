# Draft Knowledge: Chương 82

- source_id: ingest-e4709e757879ba1b
- raw_file: raw/Chương 82.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 82: Tình báo Section order 31: Paragraph: Lúc này Xuân Hoa cùng Xuân Thu gõ cửa tiến vào, mỗi người đều đem theo một bình trà và mấy cái tách. Section order 44: Paragraph: Chu Vấn thích tỏ ra yếu đuối nhu mì khi ở trên giường… Hàn Phong đọc tới đây, trong đầu toàn bộ là dấu hỏi chấm.

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
- explain Chương 82
- summarize Chương 82
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 82.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 82: Tình báo Section count: 125 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 82: Tình báo Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Hàn Phong tức tới thiếu chút chửi thề. Section order 4: Paragraph: Đồ đãng phụ này có vẻ chưa nhận được giáo huấn đầy đủ. Section order 5: Paragraph: Thấy Hàn Phong ánh mắt tràn đầy nguy hiểm nhìn mình, Liễu Huyên hừ lạnh nói: Section order 6: Paragraph: - Nếu anh dám làm gì tôi, tôi sẽ kể cho cả cái trấn này biết. Section order 7: Paragraph: Hàn Phong lại tiêu tốn 1 tinh thần nữa, lần này là để phá tan suy nghĩ tức giận đang sinh ra. Section order 8: Paragraph: Đồ khốn Liễu Huyên này rất hiểu giới hạn trong lòng hắn. Nàng ta biết bản thân sẽ không thể bị trừng phạt vì mấy cái chuyện cỏn con này, vậy nên trực tiếp lấy thanh danh của hắn ra đe doạ. Section order 9: Paragraph: Hắn nghiến răng nghiến lợi nói: Section order 10: Paragraph: - Xem như cô lợi hại. Section order 11: Paragraph: Liễu Huyên cười khoái chí: Section order 12: Paragraph: - Nếu anh chịu thua ngay từ đầu, tôi cũng đâu có thèm làm khó. Ai bảo anh thích hơn thua cơ. Section order 13: Paragraph: Hàn Phong quyết định không đối đáp nữa, chỉ tiến lại gần ghế dựa ngồi xuống, sau đó hô lớn: Section order 14: Paragraph: - Nói nhà bếp chuẩn bị hai bình trà, một trà xoài, một trà gì rẻ tiền chút. Section order 15: Paragraph: Bên ngoài lập tức có thanh âm mềm mại đáp lại: Section order 16: Paragraph: - Dạ! Section order 17: Paragraph: Liễu Huyên cũng không có tiếp tục...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 82.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 82: Tình báo; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=124 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
