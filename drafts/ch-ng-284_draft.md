# Draft Knowledge: Chương 284

- source_id: ingest-f8c86271339a197a
- raw_file: raw/Chương 284.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Hàn Phong nhìn nàng ta mà nội tâm không nhịn được bốc lên một ngọn tà hoả. Sau khi phát sinh quan hệ thân mật cùng cái nữ nhân này, hắn rốt cuộc nhận ra bản thân giống như đã bị nghiện, mỗi khi tiếp cận gần đối phương liền phải rất vất vả mới có thể khống chế cảm xúc. Section order 12: Paragraph: Hai người rất nhanh liền chia nhau chủ khách ngồi xuống, Tường Vi thong thả rót cho đối phương một ly nước, mà Hàn Phong cũng nhanh chóng búng tay tạo ra mấy viên đá lạnh,...

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
- Phong
- Vi
- Sau

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
- explain Chương 284
- summarize Chương 284
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 284.docx Chapter title: Chương 284: Bàn công chuyện Section count: 65 Section order 1: Heading: Chương 284: Bàn công chuyện Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Đưa tay gõ cửa phòng hai tiếng, Hàn Phong lui lại một bước rồi bình tĩnh chờ đợi. Một phút sau, Tường Vi trong trang phục chỉnh chu đã xuất hiện rồi mở cửa, nàng ta ánh mắt trong suốt nhìn người bên ngoài, sau đó lại ngay lập tức thu lại ánh mắt rồi bối rối hỏi: Section order 4: Paragraph: - Có… Có chuyện gì vậy? Section order 5: Paragraph: Hàn Phong nhìn nàng ta mà nội tâm không nhịn được bốc lên một ngọn tà hoả. Sau khi phát sinh quan hệ thân mật cùng cái nữ nhân này, hắn rốt cuộc nhận ra bản thân giống như đã bị nghiện, mỗi khi tiếp cận gần đối phương liền phải rất vất vả mới có thể khống chế cảm xúc. Section order 6: Paragraph: Bất quá làm gì cũng phải từ từ, nhất là đối với Tường Vi, khi chưa bước qua được cửa phòng của nàng ta thì vẫn phải biểu hiện ra thật thân sĩ. Hắn giả bộ dùng giọng điệu nghiêm chỉnh rồi chính khí lẫm nhiên nói: Section order 7: Paragraph: - Tôi muốn bàn bạc với cô một chút về tình hình của những nữ nhân vừa được giải cứu. Section order 8: Paragraph: Tường Vi nghe những lời này, nội tâm hồi hộp rốt bình tĩnh lại, sau đó là xuất hiện đôi chút hụt hẫng không rõ. Vừa rồi, cái khối màu sắc đỏ rực cuồn cuộn trong thể tâm trí của Hàn Phong, đó là cái gì biểu hiện a… Nhưng lý do này của hắn vẫn khiến cho nàng cảm thấy tương đối hài lòng, hắn tuy là thủ lĩnh nhưng vẫn không có như vậy tuỳ tiện bỏ qua những việc đau lòng mà đám người nhỏ bé tầng...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 284.docx; chapter_title=Chương 284: Bàn công chuyện; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=64 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
