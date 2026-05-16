# Draft Knowledge: Chương 309

- source_id: ingest-8dc70ae6f3d54c12
- raw_file: raw/Chương 309.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 6: Paragraph: - Hoàng trưởng phòng, cái này tuyệt đối không phải là hối lộ. Tôi là một công dân gương mẫu, sau có thể làm ra hành vi hối lộ chứ. Cái này là tôi muốn nhờ anh gửi tới chính quyền huyên Tam Giang, nó thể hiện thái độ của chúng tôi đối với chính phủ, chính là tài nguyên nhân lực chất lượng cao chắc chắn sẽ cung cấp cho các vị, chỉ là tạm thời còn kẹt thi đàn nên chưa tới kịp, sẽ có một phần tới trước… Section order 9: Paragraph: Một khi hắn mất vị trí này thì đồng ng...

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
- Tam Giang
- Hi

### Modules
- none

### Errors
- 500 exp

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
- explain Chương 309
- summarize Chương 309
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 309.docx Chapter title: Chương 309 Section count: 82 Section order 1: Heading: Chương 309 Section order 2: Paragraph: 11–13 minutes Section order 3: Paragraph: Hoàng Khải nhìn đống tinh thạch exp dày đặc trước mặt mà lâm vào chấn kinh, hắn ngay lập tức mãnh liệt từ chối: Section order 4: Paragraph: - Hàn thủ lĩnh, việc hối lộ này là không được phép… Section order 5: Paragraph: Hàn Phong xua tay cắt ngang lời của hắn rồi bình tĩnh nói: Section order 6: Paragraph: - Hoàng trưởng phòng, cái này tuyệt đối không phải là hối lộ. Tôi là một công dân gương mẫu, sau có thể làm ra hành vi hối lộ chứ. Cái này là tôi muốn nhờ anh gửi tới chính quyền huyên Tam Giang, nó thể hiện thái độ của chúng tôi đối với chính phủ, chính là tài nguyên nhân lực chất lượng cao chắc chắn sẽ cung cấp cho các vị, chỉ là tạm thời còn kẹt thi đàn nên chưa tới kịp, sẽ có một phần tới trước… Section order 7: Paragraph: Hoàng Khải nghe lời này, sự kháng cự trong nội tâm mới dần dần an ổn lại, sau đó là một ngọn lửa nóng nháy mắt bùng lên dưới đáy lòng. Chỗ này phải tương đương 500 exp, tức là có thể trợ giúp hắn nhảy vọt một mạch lên 2 cấp độ, chạm tới cấp 7. Section order 8: Paragraph: Đãi ngộ phi phàm hiện tại của hắn là 50 exp một ngày, nếu chỉ dựa vào con số này, hắn cần 10 ngày mới có thể đạt được số lượng trước mặt. 10 ngày sao, chưa biết chừng đã có người khác thay thế vị trí của hắn rồi, trưởng phòng thông tin liên lạc Hạ Quân đang tìm cách đẩy hắn xuống, đưa người của ông ta lên kia… Section order 9: Paragraph: Một khi hắn mất vị trí này thì đồng nghĩa với việc mất luôn đãi ngộ cấ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 309.docx; chapter_title=Chương 309; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=81 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
