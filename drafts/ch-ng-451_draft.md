# Draft Knowledge: Chương 451

- source_id: ingest-3451975b911206a4
- raw_file: raw/Chương 451.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Tam Giai Huyết Luyện Thuật cứ như vậy được quy cho Hàn Phong, Ngô Soái đẩy bản kỹ năng này tới ghế chủ vị, sau đó lại tiếp tục giơ một bản kỹ năng khác lên cao giọng nói: Section order 4: Paragraph: - Tam giai, Long Lân. Section order 8: Paragraph: "Kha Thành có một kỹ năng Long Trảo Thủ, là phần thưởng sống sót được hệ thống trao tặng ngay từ ngày đầu tiên, nó cũng đang dừng ở tam giai +4 rồi... Kỹ năng này có lẽ có chung nguồn gốc, hẳn là phù hợp với hắn ta."

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- giai
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Tam Giai
- Phong
- Tam

### Modules
- none

### Errors
- 451
- 451: C

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
- explain Chương 451
- summarize Chương 451
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 451.docx Chapter title: Chương 451: Công bằng Section count: 59 Section order 1: Heading: Chương 451: Công bằng Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Tam Giai Huyết Luyện Thuật cứ như vậy được quy cho Hàn Phong, Ngô Soái đẩy bản kỹ năng này tới ghế chủ vị, sau đó lại tiếp tục giơ một bản kỹ năng khác lên cao giọng nói: Section order 4: Paragraph: - Tam giai, Long Lân. Section order 5: Paragraph: Kỹ năng này vừa ra, Hàn Phong lại một lần nữa phải nhướng mày. Section order 6: Paragraph: Long Lân? Vảy rồng, da rồng? Liên quan gì tới thây ma không? Tại sao lại rơi ra kỹ năng này? Section order 7: Paragraph: "Kỹ năng này rơi ra bất quy tắc, không phải năng lực thây ma, cũng không giống với việc sẽ chống lại cụ thể một loại thây ma nào. Chứng tỏ tỉ lệ rơi kỹ năng cũng khá giống với tỉ lệ rút thẻ vật phẩm, sẽ có xác xuất nhỏ bé nhất định xuất hiện "nổ hũ" ra sản phẩm khác biệt với bình thường." Section order 8: Paragraph: "Kha Thành có một kỹ năng Long Trảo Thủ, là phần thưởng sống sót được hệ thống trao tặng ngay từ ngày đầu tiên, nó cũng đang dừng ở tam giai +4 rồi... Kỹ năng này có lẽ có chung nguồn gốc, hẳn là phù hợp với hắn ta." Section order 9: Paragraph: Long Lân là một kỹ năng tự động hệ phòng thủ, có thể phóng xuất một tầng lân giáp tiến hành tự động phòng ngự những công kích giáng tới, nghe qua thật sự đủ bảo hiểm. Bất quá nó không đem lại quá nhiều hứng thú cho các tiểu đội trưởng phía dưới, sau 1 phút, nó lại được sung công quỹ. Section order 10: Paragraph: Cũng phải thôi, chẳng ai muốn mạo hiểm dùng cống hiến quý gi...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 451.docx; chapter_title=Chương 451: Công bằng; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=58 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
