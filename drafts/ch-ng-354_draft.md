# Draft Knowledge: Chương 354

- source_id: ingest-9aac5be112437dd2
- raw_file: raw/Chương 354.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 8: Paragraph: Ngô Soái quả nhiên sợ tới mức im bặt, mà hai người Hà Tam, Triệu Nhược Pháp cũng theo đó im thít rồi đồng loạt cúi đầu xuống. Nói đùa, đây chính là phu nhân thủ lĩnh, có xinh đẹp cách mấy mà bọn họ dám lằng nhằng ngó nghiêng thì chưa cần Hàn Phong ra tay, Ngô phó đại đội sẽ ra tay trảm trước. Section order 9: Paragraph: Những đội viên Tam Giang xung quanh khi nghe cái từ “chị dâu” này thì đều hiện lên vẻ mặt không thể tin nổi, cái gì cơ, thằng ranh con với khuôn mặ...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- theo
- nghe

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Ngay
- Vi
- Im

### Modules
- none

### Errors
- 400 m

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
- explain Chương 354
- summarize Chương 354
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 354.docx Chapter title: Chương 354: Chị dâu Section count: 60 Section order 1: Heading: Chương 354: Chị dâu Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Ngô Soái trăm ngàn vạn lần cũng không nghĩ tới địa điểm mà bản thân tham gia tác chiến lại do người quen trực tiếp lãnh đạo, hơn nữa lại còn là người rất quen, rất “đáng sợ”. Nữ nhân xinh đẹp tới ngạt thở trước mặt chính là người có thể đọc thấu được suy nghĩ của người khác, là người từng khiến đại ca hắn ăn không ngon ngủ không yên. Section order 4: Paragraph: Ngay cả hắn dù không trực tiếp bị nhằm vào, thế nhưng mỗi lần tiếp xúc gần với đối phương cũng phải liên tục niệm phật hòng che giấu suy nghĩ, đúng là mệt mỏi còn hơn cả đánh trận hay canh chừng khi vụng trộm ân ái. Section order 5: Paragraph: Tường Vi khi nhìn thấy Ngô Soái cũng dâng lên kinh ngạc không nhỏ, thật không hiểu tại sao đối phương lại xuất hiện ở chỗ này. Nàng mới tấn thăng phó đoàn trưởng được hơn một ngày, nhân mạch chưa rộng, rất nhiều thông tin chưa kịp cập nhật, bởi vậy theo thói quen muốn trực tiếp đọc luôn những điều mình muốn biết. Section order 6: Paragraph: Bất quá cái tên nhóc này vừa lên là đã chủ động cầu xin nàng đừng dùng đọc tâm thuật đối với hắn, bởi vậy nàng vừa rồi mới chỉ thoáng muốn thi triển liền dừng lại. Hơn nữa hắn còn gọi nàng là chị dâu, cái này để cho Tường Vi không khỏi dâng lên bối rối cùng ngượng ngùng, lúc này không khỏi tức giận mở miệng trách mắng: Section order 7: Paragraph: - Im miệng! Section order 8: Paragraph: Ngô Soái quả nhiên sợ tới mức im bặt, mà hai người Hà Tam, Tri...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 354.docx; chapter_title=Chương 354: Chị dâu; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=59 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
