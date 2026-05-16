# Draft Knowledge: Chương 135

- source_id: ingest-1a991362a2dae63d
- raw_file: raw/Chương 135.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 15: Paragraph: Sau khi nhìn Chu Vấn hoàn thành học tập kỹ năng, mọi người bắt đầu phân chia lợi ích còn lại. Section order 16: Paragraph: Chu Vấn coi như đã hao sạch cống hiến, bởi vậy những kỹ năng nhị giai và nhất giai còn lại đã bớt đi một đối thủ lớn, 4 bản kỹ năng nhị giai lần lượt được Kha Thành, Hứa Dương, Mã Mộng đình thu lấy. Section order 17: Paragraph: Lục Đại Nguyên là tàn quân Tam Lang hội, lúc này hắn có lần đầu tiên sở hữu kỹ năng nhị giai cho mình, kỹ năng Bạo Ch...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- giai

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Tin
- Section
- Heading
- Paragraph
- Kha
- Chu

### Modules
- none

### Errors
- 500 m

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
- explain Chương 135
- summarize Chương 135
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 135.docx Chapter title: Chương 135: Tin tốt, tin xấu Section count: 107 Section order 1: Heading: Chương 135: Tin tốt, tin xấu Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Kha Thành im lặng một lát rồi nói: Section order 4: Paragraph: - Tôi bỏ lượt. Section order 5: Paragraph: Hắn tự nhận bản thân đóng góp không bằng Chu Vấn trong việc tiêu diệt con quái vật nhanh nhẹn kia. Section order 6: Paragraph: Người kia gần như góp cả cái mạng nhỏ vào, mà cậu ta cũng là người trực tiếp kết liễu. Section order 7: Paragraph: Kha Thành còn vậy Mã Mộng Đình, Hứa Dương cũng đều lần lượt biểu đạt: Section order 8: Paragraph: - Tôi bỏ lượt. Section order 9: Paragraph: Chu Vấn vai trái băng bó, trong mắt xuất hiện hào quang cảm kích và hưng phấn. Cậu ta cầm kỹ năng tam giai này lên rồi trầm giọng nói: Section order 10: Paragraph: - Đại đội trưởng, phó đại đội trưởng, các vị tiểu đội trưởng. Tôi Chu Vấn xin thề, tôi sẽ dùng kỹ năng này để bảo vệ tất cả những gì của chúng ta! Section order 11: Paragraph: Khoảnh khắc này, Chu Vấn giống như đột nhiên trưởng thành. Section order 12: Paragraph: Lý Võ Lạc ngồi ở một bên, hắn dù không hiểu lắm một kỹ năng tam giai sẽ có bao nhiêu ý nghĩa, thế nhưng chỉ từ thái độ của mọi người là có thể biết được vật kia vô cùng quý giá. Section order 13: Paragraph: Hàn Phong lại sẵn sàng nhượng ra thứ quý giá như vậy cho đội viên. Section order 14: Paragraph: “Hắn là một thủ lĩnh vô cùng hợp cách…” Section order 15: Paragraph: Sau khi nhìn Chu Vấn hoàn thành học tập kỹ năng, mọi người bắt đầu phân chia lợi ích còn lại....

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 135.docx; chapter_title=Chương 135: Tin tốt, tin xấu; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=106 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
