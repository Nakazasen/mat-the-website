# Draft Knowledge: Chương 324

- source_id: ingest-eca80c503af7301a
- raw_file: raw/Chương 324.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 6: Paragraph: Kim Nguyệt Huyễn là thiếu nữ vừa tròn 17 tuổi, nàng ta khởi đầu tận thế đánh ch.ết 5 thây ma, thành công sống sót và thăng cấp, được ban thưởng kỹ năng tam giai Thanh Xuân. Dù là kỹ năng tam giai nhưng nó lại không đem đến bất kỳ năng lực chiến đấu nào cả, cuối cùng khiến nàng ta lưu lạc thành tỳ nữ của Đổng Thành. Lúc này bàn tay nàng ta bốc lên hào quang đỏ máu rồi ném nó vào binh lính dưới đất, lập tức hồi phục cho người này 50% chỉ số thể lực, trí lực, đồng thờ...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- level
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Vi
- Phong
- Kim

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
- explain Chương 324
- summarize Chương 324
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 324.docx Chapter title: Chương 324 Section count: 55 Section order 1: Heading: Chương 324 Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: “Thật ra tôi chính là cái đầu thể thao túng đã tấn công đồng đội của anh đây.” Bởi vì không có Tường Vi bên cạnh, Hàn Phong rất tuỳ tiện mà nghĩ thầm một câu trong lòng, hắn lúc này chỉ vào vị quân nhân đang bị thương nặng nhất rồi nói: Section order 4: Paragraph: - Kim Nguyệt Huyễn, Thường Vân, hỗ trợ vị quân nhân này. Section order 5: Paragraph: - Tuân lệnh! Section order 6: Paragraph: Kim Nguyệt Huyễn là thiếu nữ vừa tròn 17 tuổi, nàng ta khởi đầu tận thế đánh ch.ết 5 thây ma, thành công sống sót và thăng cấp, được ban thưởng kỹ năng tam giai Thanh Xuân. Dù là kỹ năng tam giai nhưng nó lại không đem đến bất kỳ năng lực chiến đấu nào cả, cuối cùng khiến nàng ta lưu lạc thành tỳ nữ của Đổng Thành. Lúc này bàn tay nàng ta bốc lên hào quang đỏ máu rồi ném nó vào binh lính dưới đất, lập tức hồi phục cho người này 50% chỉ số thể lực, trí lực, đồng thời xoá bỏ hiệu ứng ác mộng. Section order 7: Paragraph: Thường Vân cả cấp độ cả thực lực còn yếu hơn Kim Nguyệt Huyễn. Hắn mặc dù có kỹ năng chữa thương Huyền Hồ Tế Thế tam giai nhưng lại là nam nhân, mà nam nhân thì làm gì có chuyện được “sủng ái”, cái kết là cho tới khi Hàn Phong giải phóng Xuân Lê, hắn vẫn bồi hồi ở level 5. Lúc này hắn ngưng tụ hào quang lục nhạt ném tới, lập tức chữa khỏi 50% thương thế trên người thương binh này, để cho người dưới đất ọc ra một ngụm máu tươi rồi lờ mờ tỉnh lại. Section order 8: Paragraph: Binh lính này mở mắt nhìn q...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 324.docx; chapter_title=Chương 324; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=54 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
