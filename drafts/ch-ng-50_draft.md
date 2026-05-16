# Draft Knowledge: Chương 50

- source_id: ingest-e7670a1f00b64d71
- raw_file: raw/Chương 50.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 50: Tình thế bắt buộc Section order 5: Paragraph: Hàn Phong tiếp lấy một khẩu AK74 đeo vào bên hông, dù sao đây cũng là loại súng hắn được huấn luyện qua, ít nhất còn biết cách dùng. Section order 7: Paragraph: - Trong số các người, người nào bắn súng tốt nhất? Cao Trác lập tức lên tiếng:

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- lang

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
- explain Chương 50
- summarize Chương 50
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 50.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 50: Tình thế bắt buộc Section count: 90 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 50: Tình thế bắt buộc Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Ngô Soái nghe lời của Hàn Phong cũng không nhịn được ngưng trọng. Hắn ngay lập tức từ mái nhà nhảy xuống, sau đó cùng với Hứa Dương lái xe chạy ngược về căn cứ. Section order 4: Paragraph: Mấy phút sau, hắn đã trở lại cùng đầy đủ súng ống đạn dược. Section order 5: Paragraph: Hàn Phong tiếp lấy một khẩu AK74 đeo vào bên hông, dù sao đây cũng là loại súng hắn được huấn luyện qua, ít nhất còn biết cách dùng. Section order 6: Paragraph: Hắn xoay người hỏi Tường Vi: Section order 7: Paragraph: - Trong số các người, người nào bắn súng tốt nhất? Cao Trác lập tức lên tiếng: Section order 8: Paragraph: - Tôi, là tôi… Section order 9: Paragraph: Tường Vi không thèm để ý hắn, khẳng định nói: Section order 10: Paragraph: - Là Trần Diệu Âm. Section order 11: Paragraph: Hàn Phong nhìn thoáng qua Trần Diệu Âm một chút, nữ tử này khuôn mặt tương đối bình thường, nàng ta dù biết nguy hiểm đang cận kề nhưng ánh mắt vẫn tương đối bình thản lạnh lùng. Section order 12: Paragraph: Hàn Phong ném khẩu M4 carbine cho nàng ta, sau đó lại ném nốt khẩu AK74 cho Tiêu Minh, trầm giọng nói: Section order 13: Paragraph: - Một lát đi sứ, anh biểu hiện cho tốt, chớ có lộ ra sự sợ hãi. Section order 14: Paragraph: Tiêu Minh vốn vẫn còn đang ngẩn người chợt run tay tiếp nhận khẩu súng, nuốt một ngụm nước bọt nghi hoặc hỏi: Section order 15...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 50.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 50: Tình thế bắt buộc; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=89 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
