# Draft Knowledge: Chương 138

- source_id: ingest-284f3fb7fd21eb60
- raw_file: raw/Chương 138.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 18: Paragraph: Hàn Phong rút Thanh Phong đao từ bên hông ra chém một đao, ổ khoá nhỏ nhắn không chịu được cự lực đã bị chém vỡ. Section order 21: Paragraph: Đây là một chiếc bộ đàm radio, có thể dùng để liên lạc với huyện Tam Giang bên kia. Section order 25: Paragraph: “Đây là trung tâm cứu hộ cứu nạn huyện Tam Giang. Tôi là Bạc Thanh. Liêu cục trưởng, Nhạc phó cục trưởng, hãy liên lạc lại khi nhận được tín hiệu.”

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
- Thu
- Hi
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
- explain Chương 138
- summarize Chương 138
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 138.docx Chapter title: Chương 138: Câu Section count: 113 Section order 1: Heading: Chương 138: Câu Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Xuân Thu vừa đi ra từ phòng tắm, sau khi nghe thấy thảm trạng tại thôn Xuân Lê thì không khỏi khóc thút thít. Nàng cũng biết tận thế tàn khốc, thậm chí ngay tại trấn Hi Vọng cũng vẫn tàn khốc như thường, nhiều nữ nhân yếu đuối không được nhận vào đội đào đất đã phải bán thân lấy miếng ăn. Section order 4: Paragraph: Thế nhưng tới tình trạng làm đồ chơi cho người khác tuỳ tiện chà đạp, nàng vẫn không thể tưởng tượng nổi. Section order 5: Paragraph: Hàn Phong tuỳ tiện phất phất tay nói: Section order 6: Paragraph: - Được rồi, thông tin của cô khiến tôi rất hài lòng. Thế này đi, tôi cho cô 100 cống hiến coi như tiền phòng thân. Về phần công việc sau này thế nào, Xuân Thu, cô dắt nàng ta đi tìm Liễu tiểu thư. Section order 7: Paragraph: Xuân Thu lau nước mắt, nhu thuận đáp lời: Section order 8: Paragraph: - Dạ, chủ nhân. Section order 9: Paragraph: Nàng hiện tại không còn một chút bài xích với mấy nữ nhân tới từ thôn Xuân Lê, trái lại đã tràn ngập đồng cảm cùng thương tiếc. Section order 10: Paragraph: Chờ cho hai nữ nhân rồng rắn kéo nhau ra ngoài, Hàn Phong mới đứng lên đi tới bên cạnh giường ngủ, sau đó từ tốn ngồi xuống. Section order 11: Paragraph: Hắn thò tay xuống gầm giường tìm kiếm một hồi, sau đó từ bên dưới móc lên một cái hộp sắt màu đen. Section order 12: Paragraph: Bên ngoài hộp, móc khoá vẫn nguyên vẹn, giống như chưa từng bị người mở ra. Section order 13: Paragraph: Hàn Phon...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 138.docx; chapter_title=Chương 138: Câu; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=112 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
