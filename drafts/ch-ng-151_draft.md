# Draft Knowledge: Chương 151

- source_id: ingest-2e5beb0138dee1fd
- raw_file: raw/Chương 151.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 34: Paragraph: Sau khi hai bên ngồi xuống, Tường Vi bình tĩnh rót cho Hàn Phong một cốc nước. Section order 73: Paragraph: - Anh thật sự đáng tin sao? Hàn Phong vừa bước tới khu quân y vừa cười lạnh: Section order 74: Paragraph: - Thật sự đủ ngây thơ. Chờ cô hết giá trị lợi dụng, tôi sẽ đuổi cô về bên huyện Tam Giang, tới lúc đó khỏi có hứa hẹn gì nữa.

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
- Tin
- Section
- Heading
- Paragraph
- La
- Kia

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
- explain Chương 151
- summarize Chương 151
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 151.docx Chapter title: Chương 151: Tin hay không cũng phải dùng. Section count: 127 Section order 1: Heading: Chương 151: Tin hay không cũng phải dùng. Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Thôn Xuân Lê. Section order 4: Paragraph: Đổng Thành đi đi lại lại trong phòng họp trung tâm, tại sao đội nhóm ra ngoài lại không liên lạc lại. Section order 5: Paragraph: Đúng lúc này có một tên lâu la chạy vào báo cáo: Section order 6: Paragraph: - Báo. Có tin tức từ nhị đương gia. Section order 7: Paragraph: Đổng Thành hai mắt bốc lên tinh quang lập tức hỏi: Section order 8: Paragraph: - Tin gì? Section order 9: Paragraph: - Dạ bẩm đại đương gia, Nhị đương gia truyền tin về, phát hiện dấu vết của nhóm người La Sơn. Chẳng qua bọn họ đã ch.ết sạch… Section order 10: Paragraph: Đổng Thành hai mắt mở to vội hỏi lại: Section order 11: Paragraph: - Cái gì?! Section order 12: Paragraph: Hắn nghe tin này mà trong lòng trầm xuống. La Sơn ra ngoài cùng 10 tên đội viên, có súng ống đầy đủ, tại sao có thể ch.ết mà không kịp truyền tin chứ. Section order 13: Paragraph: Hắn vội vã chạy tới phòng thông tin, nơi này có một thiết bị thu nhận sóng khá lớn. Đại hán trực máy vừa thấy Đổng Thành thì đứng lên nói: Section order 14: Paragraph: - Đại đương gia, nhóm người nhị đương gia phát hiện một khu vực tụ tập rất đông thây ma… Section order 15: Paragraph: Đổng Thành nghe vậy vội nói: Section order 16: Paragraph: - Kết nối lại tín hiệu. Section order 17: Paragraph: Một lúc sau, Bành Lực bên kia đã kết nối tín hiệu thành công, hắn nhanh chóng thông báo:...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 151.docx; chapter_title=Chương 151: Tin hay không cũng phải dùng.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=126 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
