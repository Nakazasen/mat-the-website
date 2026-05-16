# Draft Knowledge: Chương 83

- source_id: ingest-038e9babb7a15197
- raw_file: raw/Chương 83.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 83: Diễm phúc không tệ Section order 15: Paragraph: - Hàn Phong, ngày mai anh sẽ đi thăm dò con đường an toàn dẫn tới huyện Tam Giang chứ? Section order 27: Paragraph: - Hơn nữa, tôi là người rất có nguyên tắc. Sau khi đánh hạ siêu thị Thanh Hà, tôi mới tính tới chuyện toàn lực tìm kiếm.

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
- explain Chương 83
- summarize Chương 83
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 83.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 83: Diễm phúc không tệ Section count: 120 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 83: Diễm phúc không tệ Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Đây là lần thứ hai Hàn Phong nghe thấy câu này. Hắn vẫn chẳng hiểu gì cả, chỉ có thể tuỳ tiện đáp lại: Section order 4: Paragraph: - Cô nhìn cũng diễm phúc không tệ. Section order 5: Paragraph: Thấy Tường Vi tức giận nhìn mình, Hàn Phong khuôn mặt đều nghệt ra. Section order 6: Paragraph: Chẳng lẽ lại sai ở đâu rồi? À đúng, còn cần phải rót nước. Section order 7: Paragraph: Hắn rót cho Tường Vi một ly trà xoài, còn chu đáo thêm vào đó mấy cục đá, sau đó đẩy tới phía đối phương cười nói: Section order 8: Paragraph: - Đây, mời cô dùng trà, tuyệt đối thân sĩ nhé. Section order 9: Paragraph: Tường Vi cắn môi nhìn Hàn Phong, sau đó lại nhìn ly trà xoài, mắng nhẹ một câu: Section order 10: Paragraph: - Lưu manh! Section order 11: Paragraph: - …!!! Section order 12: Paragraph: “ch.ết tiệt! Thế này không được, thế kia cũng không được. Ả này còn khó đối phó hơn Liễu Huyên!” Section order 13: Paragraph: Hắn chỉ có thể chửi thầm trong lòng, tự bưng ly trà đen lên uống một ngụm. Aizz, nếu hắn cũng uống trà xoài, có khi lại bị đánh giá chủ uống tranh đồ của khách, nghe thêm một câu chửi mắng nữa. Section order 14: Paragraph: Tường Vi thấy Hàn Phong không giải thích, cũng không có dây dưa ở chủ đề này nữa, hiểu rằng nam nhân này thực sự là một tên đầu đất rồi. Nàng nhẹ bưng tách trà xoài lên uống một ngụm sau đó nói:...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 83.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 83: Diễm phúc không tệ; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=119 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
