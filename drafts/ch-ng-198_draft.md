# Draft Knowledge: Chương 198

- source_id: ingest-10f95e82dc4a42b5
- raw_file: raw/Chương 198.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 71: Paragraph: Ban đầu cậu ta còn tưởng Hàn Phong chướng mắt mấy kỹ năng này. Nhưng đây mới thật là dụng ý của đại đội trưởng sao… Section order 76: Paragraph: Nghe được thanh âm thê lương này, Hàn Phong ánh mắt không co rụt lại. Section order 3: Paragraph: Hàn Phong đưa ra vấn đề này, đồng thời bên cạnh Lý Võ Lạc cũng xoay màn hình máy tính lại cho tất cả mọi người cùng xem xét

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
- Thanh
- Vi

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
- explain Chương 198
- summarize Chương 198
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 198.docx Chapter title: Chương 198: Kẻ sau màn lộ diện. Section count: 77 Section order 1: Heading: Chương 198: Kẻ sau màn lộ diện. Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Hàn Phong đưa ra vấn đề này, đồng thời bên cạnh Lý Võ Lạc cũng xoay màn hình máy tính lại cho tất cả mọi người cùng xem xét Section order 4: Paragraph: Trên màn hình là hình ảnh cao tầng thi đàn tại đại lộ Thanh Hà. Bọn chúng đang ở tại vị trí giữa trận địa số 2, ước chừng 30 phút nữa sẽ bắt đầu bước vào trận địa số 3. Section order 5: Paragraph: Mấy chục đầu thây ma tiến hoá lúc nhúc đứng, con nào con nấy hiện lên vẻ hung dữ khát máu, ánh mắt đỏ quạch còn bốc lên thái độ điên cuồng vô cùng kinh tởm. Chẳng những thế khi bọn chúng tụ tập với nhau còn đem đến cho người ta cảm giác áp bách ngộp thở, dù đang cách 1 cái màn hình cũng đủ khiến cho người ta cảm thấy rùng mình. Section order 6: Paragraph: 17 thây ma tiến hoá trên level 20, hơn 50 thây ma tiến hoá trên level 10, nếu không có súng chống tăng và đại liên 12ly7 áp trận, không đời nào nhân loại có thể chống cự lại. Section order 7: Paragraph: Hàn Phong chỉ vào màn hình rồi nói: Section order 8: Paragraph: - Đây là chủ lực thi đàn, thế nhưng không có bất kỳ thây ma nào lạ mặt. Những dạng thây ma tiến hoá như thể tốc độ, thể sức mạnh, thể phòng hộ, chúng ta đều đã từng đối đầu qua, nhưng không có bất kỳ thây ma nào từng biểu hiện ra việc có thể khống chế thây ma khác, cũng không có năng lực công kích tinh thần. Section order 9: Paragraph: - Mọi người nói xem thây ma có thể khống chế thây ma khác đang trố...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 198.docx; chapter_title=Chương 198: Kẻ sau màn lộ diện.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=76 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
