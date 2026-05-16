# Draft Knowledge: Chương 364

- source_id: ingest-cbd4d8f530c66bd1
- raw_file: raw/Chương 364.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Một bát cơm đầy nữa đã được mang tới cho Hàn Phong, đồng thời Lam Nhu Thuỷ cũng đã tỉnh giấc, nàng ta ngồi xuống một chiếc ghế bên cạnh Hàn Phong rồi bắt đầu giảng giải chi tiết nội dung cơ bản của bộ luật mới được lập lên. Section order 7: Paragraph: Phi phàm giả không được phép sử dụng năng lực phi phàm trong phạm vi khu sinh hoạt chung nhằm đe doạ hay gây phương hại tới người khác, nếu bị tố cáo hoặc bị phát hiện sẽ bị phạt xxx điểm chiến công. Phần này không có...

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
- An
- Section
- Heading
- Paragraph
- Phong
- Lam Nhu

### Modules
- none

### Errors
- 500

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
- explain Chương 364
- summarize Chương 364
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 364.docx Chapter title: Chương 364: An tường Section count: 59 Section order 1: Heading: Chương 364: An tường Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Một bát cơm đầy nữa đã được mang tới cho Hàn Phong, đồng thời Lam Nhu Thuỷ cũng đã tỉnh giấc, nàng ta ngồi xuống một chiếc ghế bên cạnh Hàn Phong rồi bắt đầu giảng giải chi tiết nội dung cơ bản của bộ luật mới được lập lên. Section order 4: Paragraph: Bộ luật chia làm hai phần, phần áp dụng cho tất cả mọi người và phần bổ sung cho riêng phi phàm giả. Section order 5: Paragraph: Vẫn là các nguyên tắc tương tự xã hội trước tận thế, có điều hình phạt đã được thay đổi đề phù hợp hơn, chủ yếu sẽ tác động thằng vào túi tiền của mỗi người. Ví dụ như xả rác bừa bãi phạt một ngày công cơ bản, gây rối trật tự công cộng phạt ba ngày công, trộm cắp sẽ bị phạt bảy ngày công, hành vi làm tổn hại sức khoẻ, danh dự, nhân phẩm người khác cũng bị phạt rất nặng, từ 15 ngày công cho tới cả “tuỳ ý để bị hại xử lý”… Section order 6: Paragraph: Nhân lực hậu tận thế quá thiếu thốn, nếu vi phạm pháp luật mà lại nhốt người khác lại thì chẳng khác nào tự chặt tay. Chi bằng bắt đối tượng nai lưng ra làm việc để trả giá cho hành vi vi phạm sẽ tối ưu hơn nhiều. Section order 7: Paragraph: Phi phàm giả không được phép sử dụng năng lực phi phàm trong phạm vi khu sinh hoạt chung nhằm đe doạ hay gây phương hại tới người khác, nếu bị tố cáo hoặc bị phát hiện sẽ bị phạt xxx điểm chiến công. Phần này không có số liệu cụ thể, chính là muốn để Hàn Phong tự mình quyết định phạt bao nhiêu. Section order 8: Paragraph:...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 364.docx; chapter_title=Chương 364: An tường; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=58 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
