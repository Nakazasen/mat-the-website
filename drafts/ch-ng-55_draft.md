# Draft Knowledge: Chương 55

- source_id: ingest-66d1f7800974a7c2
- raw_file: raw/Chương 55.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 55: Quyết định chuyển nhà Section order 6: Paragraph: Nam nhân có chút khắc khổ tên Từ Thôi, là đại diện những nam nhân còn sống sót, nữ nhân trung niên tên Tạ Hàm Hương, đại diện cho những người sống sót nữ giới, nữ nhân trẻ tuổi rất xinh đẹp còn lại tên Kiều Ti Vân, là tổng quản hậu cung của Tam Lang trại. Section order 7: Paragraph: Hàn Phong ngồi nghe bọn họ báo cáo xong, trong lòng không khỏi chửi mắng đám người Tam Lang một l...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- lang
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Trong

### Modules
- none

### Errors
- 400 ng

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
- explain Chương 55
- summarize Chương 55
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 55.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 55: Quyết định chuyển nhà Section count: 96 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 55: Quyết định chuyển nhà Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Trong phòng khách lúc trước, máu cùng mảnh vụn thi thể đã được tẩy rửa sạch sẽ. Section order 4: Paragraph: Hàn Phong ngồi trên ghế sofa, nhìn vào ba nam hai nữ trước mặt. Section order 5: Paragraph: Hai nam trong đó hắn có thể coi như quen thuộc, chính là Nhạc Sơn và Lục Đại Nguyên. Ba người còn lại chính là đại diện người sống sót. Section order 6: Paragraph: Nam nhân có chút khắc khổ tên Từ Thôi, là đại diện những nam nhân còn sống sót, nữ nhân trung niên tên Tạ Hàm Hương, đại diện cho những người sống sót nữ giới, nữ nhân trẻ tuổi rất xinh đẹp còn lại tên Kiều Ti Vân, là tổng quản hậu cung của Tam Lang trại. Section order 7: Paragraph: Hàn Phong ngồi nghe bọn họ báo cáo xong, trong lòng không khỏi chửi mắng đám người Tam Lang một lần nữa. Section order 8: Paragraph: Đám người này tiếp quản trại tập trung vào 2 ngày trước thì tịch thu tất cả lương thực của mọi người. Bọn chúng ngoài ăn chơi phè phỡn và hϊế͙p͙ đáp người khác thì không làm gì nữa cả. Section order 9: Paragraph: Lương thực trước đó đám Liêu cục trưởng, Nhạc phó trưởng khổ cực dò tìm, bọn chúng đã ăn hết một góc, còn không chịu xuất quân tìm thêm vật tư, chỉ chăm chăm vào dò xét kho súng đạn. Section order 10: Paragraph: Hiện tại khu tập trung này chỉ còn khoảng hơn 1 tấn đồ ăn các loại, chỉ sợ không chèo chống nổi vài ngày. Section...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 55.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 55: Quyết định chuyển nhà; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=95 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
