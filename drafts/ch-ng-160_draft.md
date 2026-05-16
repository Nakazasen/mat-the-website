# Draft Knowledge: Chương 160

- source_id: ingest-3fde5f517e804a76
- raw_file: raw/Chương 160.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 28: Paragraph: Sau khi thăm ớt xong, Hàn Phong tiến thẳng tới phòng họp trung tâm. Section order 34: Paragraph: Trải qua một ngày chiến đấu cường độ cao, tất cả những người ngồi ở đây đã hoàn toàn tin phục Hàn Phong. Nam nhân này chẳng những vô cùng mạnh mẽ mà còn luôn chiến đấu ở tuyến đầu. Chẳng những vậy, tất cả quyết sách của hắn đều vô cùng chính xác và kịp thời. Section order 39: Paragraph: Ngay cả Quan Bình, Lý Võ Lạc hai cái quân nhân chuyên nghiệp này cũng phải âm thầm...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Trong
- Hi

### Modules
- none

### Errors
- 463 ng

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
- explain Chương 160
- summarize Chương 160
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 160.docx Chapter title: Chương 160: Thống kê trước cuộc chiến. Section count: 79 Section order 1: Heading: Chương 160: Thống kê trước cuộc chiến. Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong rời đi phòng quân y, đáy lòng không có nửa điểm gợn sóng. Section order 4: Paragraph: Trong mắt hắn đại khái có hai dạng người: người có tác dụng, và người không có tác dụng. Section order 5: Paragraph: Nếu không chiến đấu, vậy âm thầm tiếp nhận các loại thử nghiệm đi. Bản thân hắn khi bắt đầu xây dựng trấn Hi Vọng, ngay từ lúc ban sơ đã xác định một điểm: không nuôi phế vật. Section order 6: Paragraph: Ngươi nói sao? Họ đã cống hiến sức lực, cống hiến tương lai, đã bị thương, bị tàn phế, họ phải được nghỉ ngơi ư? Section order 7: Paragraph: Hừ! Làm gì có chuyện dễ thế. Cống hiến đó chưa đủ, mãi mãi chưa đủ. Trừ khi ch.ết rồi, trừ khi thế giới trở lại như cũ, hoặc trừ khi Hàn Phong có thực lực của chúa tể toàn năng, vậy may ra hắn mới dung túng cho người vô tác dụng. Section order 8: Paragraph: Nếu người bị thương an ổn tại hậu phương tiếp nhận trị liệu, vậy thì ai muốn đứng ở tuyến đầu chiến đấu đây, những người lành lặn vẫn đang cống hiến liệu có tiếp tục cố gắng mà cống hiến hết sức không? Thương binh ở hậu phương vẫn coi như còn được an toàn, nhưng chiến binh tuyến đầu thì thời khắc đều phải tiếp nhận nguy hiểm ch.ết đi. Section order 9: Paragraph: Nằm một chỗ thì làm ra các cống hiến theo kiểu nằm một chỗ, bởi vì người khác đứng ở tuyến đầu vẫn đang có đóng góp lớn hơn ngươi. Họ chưa cụt tay gãy chân, nhưng họ sắp rồi, thậm chí...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 160.docx; chapter_title=Chương 160: Thống kê trước cuộc chiến.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=78 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
