# Draft Knowledge: Chương 275

- source_id: ingest-6895dea1b7bc4902
- raw_file: raw/Chương 275.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 34: Paragraph: - Kia… Kia không phải là Chương Tham, một trong ngũ tướng sao, là tứ đại tướng. Section order 63: Paragraph: Sau khi nhìn tất cả mọi việc đã được chuẩn bị xong, Hàn Phong mới nhìn một vòng đáp tất cả những ánh mắt bên dưới rồi bình tĩnh giới thiệu: Section order 64: Paragraph: - Xin chào mọi người. Tôi là Hàn Phong, là một nhân viên văn phòng, cũng là một người may mắn sống sót giữa tận thế khốc liệt này.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.59
- signals: mom, minutes

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
- Hoa Section
- Hi
- Huhuhu

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
- explain Chương 275
- summarize Chương 275
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 275.docx Chapter title: Chương 275: Tất cả đã được tự do Section count: 75 Section order 1: Heading: Chương 275: Tất cả đã được tự do Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Chiến trường tiền tuyến, giao lộ Vạn Hoa Section order 4: Paragraph: Âm thanh sợ hãi van xin, âm thanh than khóc rên rỉ, âm thanh chửi bới mắng nhiếc, âm thanh lạnh lùng ra lệnh, âm thanh ôn hoà trấn an, tất cả hoà trộn lại thành một bản giao hưởng xen lẫn giữa đau khổ và tuyệt vọng. Dưới ánh nắng chiều dần tắt, toàn bộ cư dân tại thôn Xuân Lê đã được tập trung đầy đủ. Section order 5: Paragraph: Lý Võ Lạc, Sử Thắng, Lục Đại Nguyên chia ra đứng tại ba góc làm nhiệm vụ điều phối cư dân và tuyên truyền trị an, đội viên trấn Hi Vọng cũng đang tích cực làm việc hết công suất nhằm hết sức trấn an đám người sống sót, ngăn không cho bọn họ diễn tiến theo hướng loạn lạc: Section order 6: Paragraph: - Mọi người hết sức bình tĩnh. Không nên hoảng loạn. Không nên phản ứng quá mức. Tất cả đều ổn định. Section order 7: Paragraph: - Toàn bộ cao tầng thôn Xuân Lê đã bị giải quyết triệt để, mọi người sẽ được an toàn tuyệt đối. Section order 8: Paragraph: - Trưởng quan, làm ơn tha cho chúng tôi, chúng tôi sẽ nghe lời mà, đừng bắt chúng tôi đứng tại đây…. Section order 9: Paragraph: - Trưởng quan, chúng tôi không có ý định phản kháng mà, chúng tôi sẽ an ổn, sẽ không đòi thêm thức ăn nữa mà… Section order 10: Paragraph: - Đừng mà, Đổng đại nhân sẽ giết tôi mất… Section order 11: Paragraph: - Huhuhu… Section order 12: Paragraph: - Trưởng quan, tên khốn kiếp kia đã ch.ết thậ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 275.docx; chapter_title=Chương 275: Tất cả đã được tự do; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=74 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
