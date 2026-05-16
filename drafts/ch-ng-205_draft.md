# Draft Knowledge: Chương 205

- source_id: ingest-108436b09c901fd6
- raw_file: raw/Chương 205.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 6: Paragraph: Bang! Bang! Bang! Section order 28: Paragraph: Tường Vi ngồi bên cạnh nghe được tiếng than khóc cùng đau đớn của nhân loại xung quanh, lại nghe thấy mệnh lệnh của Hàn Phong, nàng đột nhiên cảm thấy vô cùng do dự… Nếu bắn tiếp, đối phương lại giáng xuống công kích kinh khủng như vừa rồi thì sao đây. Có Hàn Phong bảo vệ, nàng hẳn sẽ an toàn, nhưng còn những người khác… Section order 47: Paragraph: Khu vực trung tâm, đám P2, F2, P1, F1 bắt đầu run rẩy dừng lại động tá...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- quang

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Giao
- Section
- Heading
- Paragraph
- Bang
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
- explain Chương 205
- summarize Chương 205
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 205.docx Chapter title: Chương 205: Giao phong Section count: 84 Section order 1: Heading: Chương 205: Giao phong Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Âm thanh như tiếng trẻ con kêu khóc hoà lẫn với tiếng dê đực vào mùa động dục khoảnh khắc liền vang lên bên tai tất cả mọi người tại trận địa số 5. Section order 4: Paragraph: Một luồng công kích tinh thần khổng lồ giống như thác lũ thực chất hoá từ trên cao giáng xuống, không khí xung quanh cũng bị chấn cho run rẩy trùng động, cùng với đó là cảm xúc máu tanh phẫn nộ và tức giận hận thù tràn ngập bốn phương tám hướng. Section order 5: Paragraph: Sóng tinh thần hàng ngàn hàng vạn lớp trùng trùng điệp điệp lan toả, bắt đầu từ đám tiểu đội trưởng đứng trên cao điểm rồi xung kích tới nhóm đội viên, sau đó xung kích tới đám thường dân. Section order 6: Paragraph: Bang! Bang! Bang! Section order 7: Paragraph: Những tâm khiên năng lượng hư ảo liên tiếp run rẩy rồi bang bang vỡ vụn như bong bóng xà phòng. Có người ôm đầu cắn răng thở dốc, có người hoảng sợ co giật khóc lóc, có người chống tay xuống đất nôn mửa ra mật xanh mật vàng, có người đau đớn liên tục giật tóc của mình, vài người còn lập tức thất khiếu chảy máu lăn ra ngất xỉu tại chỗ. Section order 8: Paragraph: Sóng tinh thần trùng động kéo dài tới 3 giây mới chấm dứt, sau đó là âm thanh nhân loại than khóc vang trời. Section order 9: Paragraph: - Huhuhu, đừng giết tôi. Section order 10: Paragraph: - Đau… Đau quá… Section order 11: Paragraph: - Mau tránh ra, cứu… Section order 12: Paragraph: - Thây ma, có thây ma… Section or...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 205.docx; chapter_title=Chương 205: Giao phong; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=83 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
