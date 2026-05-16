# Draft Knowledge: Chương 100

- source_id: ingest-f4325a1c755556b1
- raw_file: raw/Chương 100.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 100: Thảo luận kế hoạch tác chiến Section order 8: Paragraph: Thật ra công tác 20 cống hiến mỗi ngày đã là công tác rất tuyệt rồi. Hai người Cao Trác làm việc ngày có 8, 9 tiếng, chủ yếu là ngồi viết, soạn số liệu, chỉnh sửa hồ sơ, chẳng có gì vất vả. So với đào đất hay tìm kiếm vật tư vẫn còn nhàn chán, đừng so chiến sĩ trực chiến thanh lý thây ma chịu đủ nguy hiểm. Phương Tường dù có muốn nâng đỡ thêm, lão cũng không có lý do để...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- nguy

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Cao

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
- explain Chương 100
- summarize Chương 100
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 100.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 100: Thảo luận kế hoạch tác chiến Section count: 110 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 100: Thảo luận kế hoạch tác chiến Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Cao Trác túng quẫn gãi đầu, sau đó thở dài thườn thượt: Section order 4: Paragraph: - Aizzz… Section order 5: Paragraph: Hắn không than vãn thêm nữa. Section order 6: Paragraph: Hắn trước tận thế là công tử ca hàng thật giá thật, xung quanh người có bao nhiêu là nữ nhân vây quanh cơ chứ. Nếu không có nữ nhân hầu hạ một ngày, hắn sẽ cảm giác bản thân không đủ quý tộc trong một ngày. Section order 7: Paragraph: Rốt cuộc cũng là công việc hiện tại không đủ chi tiêu a… Section order 8: Paragraph: Thật ra công tác 20 cống hiến mỗi ngày đã là công tác rất tuyệt rồi. Hai người Cao Trác làm việc ngày có 8, 9 tiếng, chủ yếu là ngồi viết, soạn số liệu, chỉnh sửa hồ sơ, chẳng có gì vất vả. So với đào đất hay tìm kiếm vật tư vẫn còn nhàn chán, đừng so chiến sĩ trực chiến thanh lý thây ma chịu đủ nguy hiểm. Phương Tường dù có muốn nâng đỡ thêm, lão cũng không có lý do để nâng thêm. Section order 9: Paragraph: Một lúc sau, sau khi nhận được cháo, Cao Trác vẫn là thở dài than thở: Section order 10: Paragraph: - Cũng coi như ngon. Bất quá, sao lại ít như vậy a… Section order 11: Paragraph: Xung quanh hắn chẳng ai chê ít cả, ngay cả Lý Hạ Vân cũng là rất nghiêm chỉnh dùng thìa xúc hết vụn cá còn sót lại trong bát. Section order 12: Paragraph: Hắn sớm quen với lời than vãn của đồng bạn rồi. Section...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 100.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 100: Thảo luận kế hoạch tác chiến; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=109 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
