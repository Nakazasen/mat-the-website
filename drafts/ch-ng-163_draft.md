# Draft Knowledge: Chương 163

- source_id: ingest-9f6d73d0b0777fdc
- raw_file: raw/Chương 163.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 10: Paragraph: - Sau này anh sẽ không ngăn cản người khác quyết định tương lai của mình chứ? Ví dụ như, ngăn ai đó trở về bên chính phủ? Hàn Phong cười lớn đáp lại: Section order 39: Paragraph: - Xuân Hoa, Xuân Thu. Section order 40: Paragraph: Hai cái tì nữ cả ngày không được gặp Hàn Phong lúc này vội vã mở cửa bước vào.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- trang

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Trang
- Section
- Heading
- Paragraph
- Phong
- Vi

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
- explain Chương 163
- summarize Chương 163
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 163.docx Chapter title: Chương 163: Trang bị level 4 thứ hai. Section count: 110 Section order 1: Heading: Chương 163: Trang bị level 4 thứ hai. Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Lời nói của Hàn Phong để cho Tường Vi hoàn toàn im lặng. Section order 4: Paragraph: Một người muốn theo đuổi lực lượng, muốn đạt được tự do, tự cường, tự chủ thì có gì sai? Chẳng những thế, người đó còn hỗ trợ những người khác cũng đạt được lực lượng, đạt được sức đề kháng với tận thế nghiệt ngã, vậy càng không thể sai. Section order 5: Paragraph: Nàng rốt cuộc hiểu tại sao Hàn Phong lại thoải mái thú nhận việc hắn đang kích động lòng người. Bởi vì nàng biết, kể cả hắn không kích động, tương lai cái chân tướng mà hắn nói cũng sẽ có người từ từ nhận ra mà thôi. Section order 6: Paragraph: Hắn chỉ đang thúc đẩy quá trình này diễn ra sớm hơn, khiến cho mọi người sớm bước ra một bước quyết đoán kia mà thôi. Section order 7: Paragraph: Vấn đề không nằm ở đúng - sai, vấn đề nằm ở quan điểm trái ngược. Chính phủ muốn mọi người tiếp nhận bảo hộ, tất cả chung tay hợp sức xây dựng lại trật tự. Mà Hàn Phong thì muốn độc lập đứng trên đôi chân của mình, không muốn phụ thuộc ai cả. Section order 8: Paragraph: Kết quả của hai hành động này đều là mang tới cuộc sống tốt đẹp hơn cho người dưới trướng. Thế nhưng… Section order 9: Paragraph: Tường Vi cũng không có vạch trần điều gì, cả hai người sớm đã ngầm hiểu rõ nhiều vấn đề, không nhất thiết lại khơi gợi rồi tranh luận. Nàng chỉ chậm rãi hỏi lại: Section order 10: Paragraph: - Sau này anh sẽ không ngăn cản...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 163.docx; chapter_title=Chương 163: Trang bị level 4 thứ hai.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=109 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
