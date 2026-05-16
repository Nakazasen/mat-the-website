# Draft Knowledge: Chương 111

- source_id: ingest-4d400572774a03f0
- raw_file: raw/Chương 111.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 111: Chiến quả khổng lồ Section order 4: Paragraph: Lần săn giết này rốt cuộc bù đắp phần nào đó tiếc nuối của Hàn Phong. Trước đó bọn họ săn giết thể thôn phệ E2 level 22 chẳng thu được gì ngoài một phần tài liệu tinh hạch. Lần này Hàn Phong trực tiếp giết ch.ết quái vật, khiến cho nó rơi ra được trang bị hệ thống, lại còn rất phong phú và mạnh mẽ. Section order 9: Paragraph: “Đinh! Kỹ năng bị động tam giai: Can Trường! Kỹ năng th...

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
- explain Chương 111
- summarize Chương 111
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 111.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 111: Chiến quả khổng lồ Section count: 83 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 111: Chiến quả khổng lồ Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Ngô Soái ứng một tiếng, sau đó từ balo lấy ra rất nhiều vật phẩm trải trên bàn. Section order 4: Paragraph: Lần săn giết này rốt cuộc bù đắp phần nào đó tiếc nuối của Hàn Phong. Trước đó bọn họ săn giết thể thôn phệ E2 level 22 chẳng thu được gì ngoài một phần tài liệu tinh hạch. Lần này Hàn Phong trực tiếp giết ch.ết quái vật, khiến cho nó rơi ra được trang bị hệ thống, lại còn rất phong phú và mạnh mẽ. Section order 5: Paragraph: Các tiểu đội trưởng đều nhìn chằm chằm vào động tác của Ngô Soái, người kia mỗi khi lấy ra một món vật phẩm, bọn họ đều tiến thêm một bước kích động cùng trầm trồ. Section order 6: Paragraph: Từng món vật phẩm được truyền tay nhau xem xét, khiến cho ai nấy đều phải nuốt một ngụm nước miếng. Section order 7: Paragraph: Quá ngưu bức rồi. Section order 8: Paragraph: “Đinh. Kỹ năng bán chủ động tam giai: Pháo Không Khí. Kỹ năng thuộc tính: Đòn đánh dạng quyền, chưởng sẽ kích hoạt hiệu ứng pháo không khí, tạo ra kình lực tương đương 20% lực lượng nội tại. Kỹ năng gia tăng 10% tốc độ tiêu hao thể lực. Lưu ý: uy lực và phạm vi kình lực quyết định bởi chỉ số thể lực cùng cấp độ kỹ năng.” Section order 9: Paragraph: “Đinh! Kỹ năng bị động tam giai: Can Trường! Kỹ năng thuộc tính: +3 phục hồi, +3 chống chịu. Đồng thời nhận về nội tại Can Trường: Chia nhỏ và kéo dài gấp 30 lần thời gi...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 111.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 111: Chiến quả khổng lồ; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=82 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
