# Draft Knowledge: Chương 244

- source_id: ingest-e3f7c0fd57d87106
- raw_file: raw/Chương 244.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Trong bồn tắm đầy nước, hai cái thân ảnh vẫn tiếp tục như vậy dây dưa qua lại, nam căn cùng huyệt hoa từ đầu tới cuối đều dính liền tại một chỗ. Tường Vi hàm răng cắn mạnh trên vai Hàn Phong một cái rồi mắng: Section order 4: Paragraph: - Anh… Anh bắn hết vào trong như vậy… Ức… Tôi có thể có bầu hay không? Section order 23: Paragraph: - Anh… Anh hỗn đản…

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
- Trong
- Vi
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
- explain Chương 244
- summarize Chương 244
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 244.docx Chapter title: Chương 244: Đạo bất đồng, tương bất vi mưu Section count: 78 Section order 1: Heading: Chương 244: Đạo bất đồng, tương bất vi mưu Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Trong bồn tắm đầy nước, hai cái thân ảnh vẫn tiếp tục như vậy dây dưa qua lại, nam căn cùng huyệt hoa từ đầu tới cuối đều dính liền tại một chỗ. Tường Vi hàm răng cắn mạnh trên vai Hàn Phong một cái rồi mắng: Section order 4: Paragraph: - Anh… Anh bắn hết vào trong như vậy… Ức… Tôi có thể có bầu hay không? Section order 5: Paragraph: Vừa rồi Hàn Phong đem toàn bộ dương dịch đều bắn vào trong, cái này để cho nàng vô cùng hoang mang. Hơn nữa hắn bắn xong còn tiếp tục lôi nàng vào nhà tắm giày vò, giống như vĩnh viễn không thoả mãn. Nàng còn chưa có sẵn sàng làm mẹ, nhất là trong hoàn cảnh tận thế này. Section order 6: Paragraph: Hàn Phong nhướng mày, hắn lập tức truy hỏi: Section order 7: Paragraph: - Cô hành kinh vào ngày nào? Tường Vi khuôn mặt đỏ lên, tại sao Hàn Phong lại hỏi cái vấn đề nhạy cảm này. Nàng ta ngập ngừng một chút vẫn là thành thật nói: Section order 8: Paragraph: - Ngày 16 hàng tháng là bắt đầu. Section order 9: Paragraph: Hàn Phong lẩm bẩm tính toán, ngày 16 hàng tháng là bắt đầu, hiện tại là ngày 13… Section order 10: Paragraph: Hắn khoé miệng nhếch lên cười nhạt: Section order 11: Paragraph: - Hiện tại tôi có bắn vào bên trong 5 lít nữa thì cô cũng không có bầu được. Section order 12: Paragraph: - T-Tại sao? Section order 13: Paragraph: Hàn Phong đè ngửa nàng ta ra thành bồn tắm, lại há miệng gặm trên bộ ngực cự đạ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 244.docx; chapter_title=Chương 244: Đạo bất đồng, tương bất vi mưu; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=77 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
