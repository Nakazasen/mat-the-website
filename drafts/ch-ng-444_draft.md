# Draft Knowledge: Chương 444

- source_id: ingest-9feac35cc132b679
- raw_file: raw/Chương 444.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 6: Paragraph: Một câu này của Hàn Phong lúc trước tưởng chừng như không có mấy giá trị, dù sao Tam Giang cũng chẳng thiếu thốn tới mức cần dựa vào một căn cứ nghìn người, thế nhưng hiện lại bên kia lại là một trong những lối thoát cho vấn đề nan giải hiện tại. Section order 8: Paragraph: Bạc Thanh là chính khách, thứ ông ta giỏi nhất là mặt dày vô địch, kể cả lúc trước Hàn Phong có tuyên bố tuyệt giao thì ông ta vẫn có thể nở một nụ cười chân thành để vác mặt qua mượn súng được....

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- level

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Thanh
- Phong
- Hi

### Modules
- none

### Errors
- 444
- 444: H

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
- explain Chương 444
- summarize Chương 444
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 444.docx Chapter title: Chương 444: Hạt giống Section count: 65 Section order 1: Heading: Chương 444: Hạt giống Section order 2: Paragraph: 12–15 minutes Section order 3: Paragraph: Câu hỏi của Bạc Thanh về việc đào đâu ra súng diệt quỷ level 4, rất nhiều người biết đáp án, Section order 4: Paragraph: nhưng không có ai đứng ra trả lời cả. Section order 5: Paragraph: "... tôi Hàn Phong lấy danh nghĩa thủ lĩnh trấn Hi Vọng tuyên bố, kể từ hôm nay, hai bờ đông tây sông Lệ, ân đoạn nghĩa tuyệt..." Section order 6: Paragraph: Một câu này của Hàn Phong lúc trước tưởng chừng như không có mấy giá trị, dù sao Tam Giang cũng chẳng thiếu thốn tới mức cần dựa vào một căn cứ nghìn người, thế nhưng hiện lại bên kia lại là một trong những lối thoát cho vấn đề nan giải hiện tại. Section order 7: Paragraph: Ân, là chỉ một trong những thôi. Section order 8: Paragraph: Bạc Thanh là chính khách, thứ ông ta giỏi nhất là mặt dày vô địch, kể cả lúc trước Hàn Phong có tuyên bố tuyệt giao thì ông ta vẫn có thể nở một nụ cười chân thành để vác mặt qua mượn súng được. Chẳng qua không tới đường cùng thì ông ta tất nhiên sẽ không nhờ tới người ngoài, điều đó sẽ làm hạ thấp uy tín của người đứng đầu, lúc này ông ta quay qua Cổ Nguyên hỏi: Section order 9: Paragraph: - Cổ đoàn trưởng, theo trinh sát thì huyện Hương Đường có tới hai thi đàn, một thi đàn còn lại đã đi đâu rồi? Thật ra ông ta đã sớm biết, hỏi ra chỉ là cho đúng quy trình mà thôi. Section order 10: Paragraph: Cổ Nguyên chỉ lên tấm bản đồ trên bàn nói: Section order 11: Paragraph: - Một thi đàn 7 vạn trước đó quanh quẩn ở...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 444.docx; chapter_title=Chương 444: Hạt giống; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=64 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
