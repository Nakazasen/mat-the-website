# Draft Knowledge: Chương 40

- source_id: ingest-5d120302d347b0d7
- raw_file: raw/Chương 40.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 40: Giải quyết mâu thuẫn Section order 5: Paragraph: Hàn Phong thì thảnh thơi, nhưng tất cả những người còn lại thì không được như vậy. Cho tới sáng nay, hầu như bọn họ đều đã biết về tranh đấu giữa Liễu Huyên, Châu Lam, đều hiểu rằng sự việc này có thể dẫn tới phản ứng dây chuyền mà nếu không ngăn chặn, nó sẽ dẫn tới chia rẽ sâu sắc của đội ngũ. Section order 7: Paragraph: Mấy người Hứa Dương, Tiêu Minh, Mộ Thi Thi đương nhiên đứn...

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
- explain Chương 40
- summarize Chương 40
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 40.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 40: Giải quyết mâu thuẫn Section count: 63 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 40: Giải quyết mâu thuẫn Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Sáng hôm sau, Hàn Phong nghỉ ngơi đầy đủ, tinh thần thoải mái, thể lực cùng trí lực đều hồi phục đầy cây. Hắn đang nhàn nhã thưởng thức bữa sáng với bánh bột rán cùng với xúc xích và trứng chiên thịt, còn có thêm một bát canh măng để uống cho đỡ nghẹn, có thể nói là cực kỳ ngon miệng. Section order 4: Paragraph: Kể từ khi thu thập hết vật tư từ một cửa hàng tiện lợi, bữa ăn của bọn họ đã đầy đủ và bớt nhàm chán hơn rất nhiều. Cũng phải nói tới tài nấu ăn của hai cô bạn gái của Ngô Soái thực sự rất đỉnh cấp. Section order 5: Paragraph: Hàn Phong thì thảnh thơi, nhưng tất cả những người còn lại thì không được như vậy. Cho tới sáng nay, hầu như bọn họ đều đã biết về tranh đấu giữa Liễu Huyên, Châu Lam, đều hiểu rằng sự việc này có thể dẫn tới phản ứng dây chuyền mà nếu không ngăn chặn, nó sẽ dẫn tới chia rẽ sâu sắc của đội ngũ. Section order 6: Paragraph: Tất cả đều được định đoạt bởi quyết định của Hàn Phong. Section order 7: Paragraph: Mấy người Hứa Dương, Tiêu Minh, Mộ Thi Thi đương nhiên đứng về phía Châu Lam, còn Liễu Huyên cũng có Chu Vấn, Phương Tường ủng hộ. Về phía Mã Mộng Đình, nàng ta quả thật rất khôn khéo khi sớm rời xa vòng xoáy tranh đấu, dù kết quả thế nào, nàng vẫn có thể giữ được mối quan hệ tốt đẹp với cả hai bên. Section order 8: Paragraph: Đây là tranh đấu của tầng lớp có sức chiến đ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 40.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 40: Giải quyết mâu thuẫn; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=62 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
