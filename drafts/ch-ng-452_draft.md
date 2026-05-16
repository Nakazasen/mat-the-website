# Draft Knowledge: Chương 452

- source_id: ingest-1caad00edfd24e6e
- raw_file: raw/Chương 452.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Thấy Lưu Giang lâm vào trong do dự, Hàn Phong khẽ gõ gõ tay xuống bàn rồi chậm rãi nói: Section order 8: Paragraph: Hàn Phong lại quan sát Lưu Giang thêm mấy giây rồi mới chỉ vào cái ghế phía dưới bình tĩnh nói: Section order 16: Paragraph: - Anh có biết tại sao bản thân bị phạt không? Lưu Giang nắm tay lại, một lúc lâu sau, hắn mới cứng rắn đáp lại:

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- giang
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Trung
- Section
- Heading
- Paragraph
- Giang
- Phong

### Modules
- none

### Errors
- 452
- 452: Trung th

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
- explain Chương 452
- summarize Chương 452
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 452.docx Chapter title: Chương 452: Trung thành Section count: 85 Section order 1: Heading: Chương 452: Trung thành Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Thấy Lưu Giang lâm vào trong do dự, Hàn Phong khẽ gõ gõ tay xuống bàn rồi chậm rãi nói: Section order 4: Paragraph: - Tổ chức phạt anh 1000 cống hiến. Anh có chấp nhận không? Section order 5: Paragraph: Lưu Giang bàn tay đang nắm chặt chợt buông ra. 1000 cống hiến sao... Cái giá này bằng toàn bộ số chiến công hắn đang tích luỹ được, nhưng hắn vẫn hoàn toàn chấp nhận, dù nó sẽ khiến hắn mất đi cơ hội tranh đoạt kỹ năng tam giai. Section order 6: Paragraph: Ít nhất, về mặt ý nghĩa nào đó, hắn đã đền bù cho sai lầm của mình... Section order 7: Paragraph: - Thủ lĩnh. Tôi chấp nhận. Section order 8: Paragraph: Hàn Phong lại quan sát Lưu Giang thêm mấy giây rồi mới chỉ vào cái ghế phía dưới bình tĩnh nói: Section order 9: Paragraph: - Ngồi đi. Section order 10: Paragraph: Lưu Giang máy móc ngồi xuống ghế, một cái băng nô theo đó trống rỗng xuất hiện trong phòng, vật này bước tới cạnh bàn của thủ lĩnh rồi đem tới cho hắn một tờ giấy A4. Section order 11: Paragraph: "Phòng lưu trữ Đặc Huấn..." Section order 12: Paragraph: Lưu Giang bắt đầu chăm chú đọc tài liệu trong tay, nội dung bên trên làm lòng hắn càng thêm rối bời. Section order 13: Paragraph: Theo nghiên cứu từ phòng này, một thây ma F2 level 25, nếu không kịp khống chế trong 1-3 giây tại thời điểm trước khi nó tiếp cận, vậy thì nó có thể gây ra thương vong cho cả một tiểu đội trong 10 giây tiếp theo. Section order 14: Par...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 452.docx; chapter_title=Chương 452: Trung thành; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=84 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
