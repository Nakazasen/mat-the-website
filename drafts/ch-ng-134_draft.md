# Draft Knowledge: Chương 134

- source_id: ingest-716acf28fba65f54
- raw_file: raw/Chương 134.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Hàn Phong tuỳ ý lướt mắt nhìn một vòng, sau đó trông thấy hai người Lý Hạ Vân, Cao Trác đang ngồi trước máy tính. Section order 7: Paragraph: Hai người Lý, Cao này tất nhiên biết sử dụng máy tính lẫn làm số liệu, Phương Tường để cho bọn họ làm mấy công việc văn phòng này cũng xem như nhàn hạ an toàn. Section order 15: Paragraph: Sau khi hai bên trao đổi với nhau khoảng 20 phút, bàn giao vài công việc sau màn, Hàn Phong mới đứng lên rời đi. Mà cả Phương Tường cũng đ...

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
- Cao
- Hai

### Modules
- none

### Errors
- 531
- 4320
- 500 c

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
- explain Chương 134
- summarize Chương 134
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 134.docx Chapter title: Chương 134: Ám Kỳ Sát Section count: 87 Section order 1: Heading: Chương 134: Ám Kỳ Sát Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Thấy Hàn Phong bước vào, mấy người trong phòng đều giật thót vội vã đứng lên cúi chào. Section order 4: Paragraph: Hàn Phong tuỳ ý lướt mắt nhìn một vòng, sau đó trông thấy hai người Lý Hạ Vân, Cao Trác đang ngồi trước máy tính. Section order 5: Paragraph: Mạng viễn thông không biết vì lý do gì mà bị đứt đoạn, thế nhưng máy tính bình thường vẫn có thể sử dụng. Mấy tác vụ offline như word, excel vẫn dùng được thoải mái, mấy cái máy tính này được đào bới ra từ nhà dân, hiện nay được sử dụng chính để quản lý số liệu cho tiện lợi và chính xác. Section order 6: Paragraph: Bên cạnh còn có cả máy in, chỉ là hiện tại cần dùng tiết kiệm, cần thiết mới in 1 bản sau đó chép tay qua các bản khác. Cũng không biết khi nào thì tìm thấy mực in mới a. Section order 7: Paragraph: Hai người Lý, Cao này tất nhiên biết sử dụng máy tính lẫn làm số liệu, Phương Tường để cho bọn họ làm mấy công việc văn phòng này cũng xem như nhàn hạ an toàn. Section order 8: Paragraph: Phương Tường thấy Hàn Phong tới thì nở một nụ cười khổ. Gần đây thay đổi mức quy đổi chiến công, các số liệu cũ đều phải lật lên làm lại hết, lão mỗi ngày chỉ được ngủ 7 tiếng, cả ngày đều ghi chép báo cáo sau đó xoa dịu các bên, phân phối vật tư đến cho cả trấn, còn vất vả hơn cả làm giám đốc kiếp trước. Section order 9: Paragraph: Cơ bản kiếp trước chỉ đi lừa về rồi chia nhau ăn, nào có làm thật ăn thật như hiện tại. Section order...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 134.docx; chapter_title=Chương 134: Ám Kỳ Sát; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=86 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
