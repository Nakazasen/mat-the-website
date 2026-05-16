# Draft Knowledge: Chương 192

- source_id: ingest-81287fb48e3a3b97
- raw_file: raw/Chương 192.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Nếu bọn họ có đủ thể lực, trí lực, có thể tiếp tục đánh chém thi đàn cấp 8, cấp 9 bên dưới, diễn biến này cũng có thể chấp nhận được. Nhưng ngoài Hàn Phong và Chu Vấn, đám người còn lại không thể đánh dài lâu, lại thử vài lần nữa, bọn họ sẽ hao hết tiềm năng tích trữ, buộc phải rút lui. Section order 6: Paragraph: Thi đàn đã có đề phòng, cũng không dễ lừa lần 2 như vậy. Bọn nó không bị tách ra, điều này ép buộc Hàn Phong buộc phải đối đầu trực diện với 2 thây ma ti...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- level

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- F2
- Phong
- Chu

### Modules
- none

### Errors
- 400 m

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
- explain Chương 192
- summarize Chương 192
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 192.docx Chapter title: Chương 192: Tự mình doạ mình. Section count: 68 Section order 1: Heading: Chương 192: Tự mình doạ mình. Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Bọn họ đánh cũng đánh rồi, thu thập chiến quả cũng thu thập rồi, chạy cũng đã chạy luôn, thế nhưng trung tâm thi đàn vẫn không cử ra bất cứ thây ma tiến hoá nào chạy ra xử lý vụ việc, không trung cũng không vang lên tiếng dê kêu nào cả. Section order 4: Paragraph: Hắn muốn đột kích chính là muốn thử phản ứng thi đàn, đồng thời dụ dỗ F2 level 20 chui ra hòng xử đẹp nó. Nhưng kết quả nhận lại là thi đàn không phản ứng, F2 không dị động, phép thử đã thất bại. Section order 5: Paragraph: Nếu bọn họ có đủ thể lực, trí lực, có thể tiếp tục đánh chém thi đàn cấp 8, cấp 9 bên dưới, diễn biến này cũng có thể chấp nhận được. Nhưng ngoài Hàn Phong và Chu Vấn, đám người còn lại không thể đánh dài lâu, lại thử vài lần nữa, bọn họ sẽ hao hết tiềm năng tích trữ, buộc phải rút lui. Section order 6: Paragraph: Thi đàn đã có đề phòng, cũng không dễ lừa lần 2 như vậy. Bọn nó không bị tách ra, điều này ép buộc Hàn Phong buộc phải đối đầu trực diện với 2 thây ma tiến hoá kia cùng một lúc. Section order 7: Paragraph: Một con một lượt thì thật dễ làm, có khi không cần tiêu hao đạn chống tăng, 2 con cùng lúc, lại còn một đám vây quanh, nguy hiểm sẽ nâng cao. Section order 8: Paragraph: Không cẩn thận để F2 phản kích thì sẽ có người phải đổ máu. Section order 9: Paragraph: - Có khi tên khốn sau màn kia đang trực chờ bản thân chạy tới, hao hết tiềm năng rồi mới bất ngờ hét một tiếng cho...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 192.docx; chapter_title=Chương 192: Tự mình doạ mình.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=67 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
