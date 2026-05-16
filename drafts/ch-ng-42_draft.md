# Draft Knowledge: Chương 42

- source_id: ingest-3f0513348fc68117
- raw_file: raw/Chương 42.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 42: Kịch chiến thể sức mạnh. Section order 5: Paragraph: Hắn nói câu sau là dành riêng cho Chu Vấn, để thiếu niên này không có phát rồ vận dụng kỹ năng hao tốn thể lực làm gì cả. Cứ đánh bình thường, chờ đợi hắn và Hàn Phong kết thúc chiến đấu bên kia, vậy là hợp lý nhất. Section order 6: Paragraph: Chu Vấn trong đội ngũ đặc biệt hâm mộ hai người Hàn Phong, Ngô Soái, đối với sự phân phó của đối phương không có một chút dị nghị nào.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- tinh

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Chu

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
- explain Chương 42
- summarize Chương 42
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 42.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 42: Kịch chiến thể sức mạnh. Section count: 84 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 42: Kịch chiến thể sức mạnh. Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Ngô Soái phía sau cũng đã nhận ra sự bất thường của thây ma cao lớn đang đứng cách xa hơn 40 mét phía trước, hắn trầm giọng nói: Section order 4: Paragraph: - Các người thanh lý thây ma xung quanh, đừng để chúng nó cào phá ô tô, vây kín đường lui của chúng ta… Cũng đừng tiêu tốn quá nhiều thể lực, phía sau còn có nhiệm vụ đang chờ. Section order 5: Paragraph: Hắn nói câu sau là dành riêng cho Chu Vấn, để thiếu niên này không có phát rồ vận dụng kỹ năng hao tốn thể lực làm gì cả. Cứ đánh bình thường, chờ đợi hắn và Hàn Phong kết thúc chiến đấu bên kia, vậy là hợp lý nhất. Section order 6: Paragraph: Chu Vấn trong đội ngũ đặc biệt hâm mộ hai người Hàn Phong, Ngô Soái, đối với sự phân phó của đối phương không có một chút dị nghị nào. Section order 7: Paragraph: Ngô Soái sau khi chạy lên tụ họp cùng Hàn Phong, nghiêm túc nói: Section order 8: Paragraph: - Một con thây ma thật lớn, không biết so với thể thôn phệ kia thì thế nào đây? Hàn Phong nheo mắt nói: Section order 9: Paragraph: - Khẳng định sức lực rất lớn, đồng thời da dày thịt béo. Tốt nhất ta và đệ không nên dây dưa quá lâu với nó… Thế này đi, ta sẽ vận dụng lấy tĩnh chế động, làm choáng nó, đệ tìm cách chém đầu nó từ phía sau, hoặc ít nhất đục thủng một lỗ trên đầu nó. Nếu không được, dụ nó chạy khỏi nơi này. Section order 10: Paragraph:...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 42.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 42: Kịch chiến thể sức mạnh.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=83 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
