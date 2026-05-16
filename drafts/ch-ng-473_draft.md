# Draft Knowledge: Chương 473

- source_id: ingest-25f708fb9ba41624
- raw_file: raw/Chương 473.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 9: Paragraph: Hàn Phong sau khi cảnh cáo mấy người bên cạnh xong thì đưa mắt nhìn sông Lệ Giang một chút, sau đó hắn mới quay qua thiếu niên vẫn ngơ ngác đứng đó rồi hỏi: Section order 3: Paragraph: Hàn Phong gõ một gõ vào nhóm đầu não trấn Hi Vọng, chính là muốn thể hiện cho bọn họ thấy thái độ quyết tâm của bản thân trong những việc này. Hắn không chỉ cảnh báo cho bọn họ nhanh nhanh giải quyết vấn đề, đó còn là gửi đi thông điệp: đừng có cái gì cũng để tôi phải ra mặt, bằng kh...

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
- Hi
- Giang

### Modules
- none

### Errors
- 473
- 473: Ng
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
- explain Chương 473
- summarize Chương 473
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 473.docx Chapter title: Chương 473: Ngày nghỉ (9) Section count: 81 Section order 1: Heading: Chương 473: Ngày nghỉ (9) Section order 2: Paragraph: 14–18 minutes Section order 3: Paragraph: Hàn Phong gõ một gõ vào nhóm đầu não trấn Hi Vọng, chính là muốn thể hiện cho bọn họ thấy thái độ quyết tâm của bản thân trong những việc này. Hắn không chỉ cảnh báo cho bọn họ nhanh nhanh giải quyết vấn đề, đó còn là gửi đi thông điệp: đừng có cái gì cũng để tôi phải ra mặt, bằng không thì hậu quả khôn lường. Section order 4: Paragraph: Hắn đề bạt nhóm này lên làm cao tầng là muốn nhàn đầu, muốn họ giúp hắn quản lý cái trấn này, không phải để cho bọn họ hưởng thụ lương bổng, ăn chơi phè phỡn, công chuyện chưa kịp bàn bạc xong đã tót đi chơi. Section order 5: Paragraph: Hắn đề bạt bọn họ chỉ vì bọn họ là người nhà, người quen thuộc, có sự tin tưởng nhất định, có thể bớt đi sự lo lắng việc bị phản bội, đồng thời tin rằng họ sẽ nhanh chóng trưởng thành và phát triển. Section order 6: Paragraph: Nhưng nếu bọn này không làm được việc, haha... Section order 7: Paragraph: Vậy thì sớm một chút cút xuống làm dân thường, giống như một vị thường dân duy nhất trong đoàn, chỉ cần hát hò nhảy nhót, mặt xinh ngực to mông tròn đùi thon là đủ. Hoặc cút xuống làm cấp phó, để cho người có tài đứng lên chỉ đạo, chính mình đứng một bên làm chân xách đồ vác cá, culi chỉ đâu đánh đó, thế là được. Section order 8: Paragraph: Hắn mặc dù lập ra trấn Hi Vọng với mục đích hoàn thành nhiệm vụ, thế nhưng hiện tại nó đã vượt ra ngoài phạm vi "tài sản cá nhân" rồi, nó đã phần nào đó trở thành tài s...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 473.docx; chapter_title=Chương 473: Ngày nghỉ (9); ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=80 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
