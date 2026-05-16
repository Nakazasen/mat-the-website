# Draft Knowledge: Chương 422

- source_id: ingest-0249080454c82dda
- raw_file: raw/Chương 422.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Sau âm thanh báo động tấn công đi kèm với lời buộc tội không thể chân thật hơn của Hàn Phong, tình hình vốn đã căng thẳng tại hai bờ đông tây sông Lệ đã triệt để bị kích phát tới sôi trào, giống như tấm sắt nung bị hắt vào một cốc nước lạnh, tất cả đều bùng nổ rồi hoàn toàn bộc phát. Section order 13: Paragraph: Cả nghìn viên đạn được xả ra chỉ trong vài chục giây. Với trình độ xạ kích ngu xuẩn của đội viên trấn Hi Vọng, tới cái bóng của binh lính Tam Giang còn khô...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- thanh

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Sau
- Phong
- Chu

### Modules
- none

### Errors
- 422
- 422:

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
- explain Chương 422
- summarize Chương 422
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 422.docx Chapter title: Chương 422: Đánh qua đánh lại Section count: 66 Section order 1: Heading: Chương 422: Đánh qua đánh lại Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Sau âm thanh báo động tấn công đi kèm với lời buộc tội không thể chân thật hơn của Hàn Phong, tình hình vốn đã căng thẳng tại hai bờ đông tây sông Lệ đã triệt để bị kích phát tới sôi trào, giống như tấm sắt nung bị hắt vào một cốc nước lạnh, tất cả đều bùng nổ rồi hoàn toàn bộc phát. Section order 4: Paragraph: Hơn một nghìn binh sĩ ở cả hai đầu cầu đều bị doạ cho giật nảy mình, mặc kệ ai đang làm gì, tất cả đều vội vã ôm đầu rồi cúi xuống, người nào nhạy bén hơn thì nhảy vào công sự che chắn, người nào bình tĩnh hơn thì rút ống nhòm ra quan sát, người nào vững tâm lý hơn thì hô hào bình tĩnh, mà những người hoảng loạn nhất thì cầm súng lên điên cuồng bắn phá lung tung. Section order 5: Paragraph: Pằng pằng pằng... Section order 6: Paragraph: Chỉ trong phút chốc, vũng nước tĩnh lặng lúc trước đã bị khuấy tới đục ngầu, sông ngầm cuộn sóng. Section order 7: Paragraph: Trận địa Liễu Lâm, Sử Thắng cắn chặt hàm răng tức giận hô to triển khai chiến thuật phòng ngự, hàng loạt tiểu đội trưởng cũng cấp tốc chỉ đạo đội viên nhanh chóng núp sau lô cốt, ẩn sau tường bao, chui xuống hầm hào, trong khi Chu Vấn cầm đầu thành phần hiếu chiến thì rút thanh phong đao gào ầm lên: Section order 8: Paragraph: - Giết! Giết sạch lũ xâm lược! Section order 9: Paragraph: Hắn nói xong liền không chút do dự cầm lên khẩu AK47 bên cạnh mà nã liên tục về phía bờ đông. Section order 10: Par...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 422.docx; chapter_title=Chương 422: Đánh qua đánh lại; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=65 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
