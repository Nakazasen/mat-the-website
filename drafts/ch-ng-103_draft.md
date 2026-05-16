# Draft Knowledge: Chương 103

- source_id: ingest-2118cbc38bf8657b
- raw_file: raw/Chương 103.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 103: Tấn cấp 11 Section order 9: Paragraph: Không phải Xuân Hoa cùng Xuân Thu thì còn ai. Section order 11: Paragraph: Xuân Hoa lập tức ném tờ giấy xuống bàn, sau đó vội vã đưa mắt nhìn Hàn Phong.

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
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Phong

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
- explain Chương 103
- summarize Chương 103
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 103.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 103: Tấn cấp 11 Section count: 128 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 103: Tấn cấp 11 Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Nhưng đó cũng chỉ là suy đoán cá nhân của Hàn Phong. Thể linh hồn, thể tâm trí, thể tiềm thức, nghe có vẻ rất não tàn. Ừm, là não bộ… Tốt hơn hết, hắn nên hỏi thử ba cái vị bác sĩ trong trấn Hi Vọng trước khi suy đoán tiếp. Section order 4: Paragraph: Còn hiện tại, hắn cần test thử lần cuối. Section order 5: Paragraph: - Xuân Hoa, cô cầm thử tờ giấy đi. Section order 6: Paragraph: Xuân Hoa có chút tò mò cầm lên tờ giấy, lật qua lật lại xem xét. Section order 7: Paragraph: 10 giây sau, trên giấy xuất hiện một cái hình ảnh vô cùng khiến người ta thổn thức. Section order 8: Paragraph: Hai cái nữ tử trần như nhộng đang cuộn thành một đoàn mơn trớn lẫn nhau, người thì thành thục nõn nà, người thì nhu mì e ấp. Section order 9: Paragraph: Không phải Xuân Hoa cùng Xuân Thu thì còn ai. Section order 10: Paragraph: - Á… Section order 11: Paragraph: Xuân Hoa lập tức ném tờ giấy xuống bàn, sau đó vội vã đưa mắt nhìn Hàn Phong. Section order 12: Paragraph: Cũng may, chủ nhân đang bận uống trà. Section order 13: Paragraph: Hàn Phong làm bộ không để ý mà hỏi: Section order 14: Paragraph: - Hửm, sao thế? Xuân Hoa khuôn mặt đỏ bừng, lắp bắp nói: Section order 15: Paragraph: - Nga… Nó rất nóng, ta đã trượt tay… Chủ nhân… Section order 16: Paragraph: Hàn Phong trong lòng mặc niệm cho nàng ta, nữ nhân này bị doạ sợ rồi. Section order 1...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 103.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 103: Tấn cấp 11; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=127 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
