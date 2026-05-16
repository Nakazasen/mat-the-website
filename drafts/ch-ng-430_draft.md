# Draft Knowledge: Chương 430

- source_id: ingest-0ee392e8a1d35041
- raw_file: raw/Chương 430.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Tư liệu về Hàn Phong xem như tương đối đầy đủ, chuẩn bị của hắn cũng vì thế mà vô cùng đầy đủ. Bước vào trận này, bảy phần nhẫn phòng ngự các đòn công kích tâm linh của huyện Tam Giang đều đã được hắn mang trên người. Section order 11: Paragraph: Cổ Nguyên không khỏi đau đớn cắn răng lẩm bẩm mắng thầm, xu thế tấn công bị cứng rắn chặn đứng, buộc phải dừng lại tại chỗ giơ đao che chắn. Trong khi Hàn Phong đứng tại phía xa nhìn thấy đối thủ trúng chiêu thì không khỏi...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- nguy
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Phong
- Section
- Heading
- Paragraph
- Tam Giang
- Trong

### Modules
- none

### Errors
- 430
- 430: H

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
- explain Chương 430
- summarize Chương 430
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 430.docx Chapter title: Chương 430: Hàn Phong vs Cổ Nguyên (3) Section count: 54 Section order 1: Heading: Chương 430: Hàn Phong vs Cổ Nguyên (3) Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Đòn Hồn Áp đầu tiên phá tan một khoả nhẫn phòng ngự của Cổ Nguyên, Hàn Phong lại tiếp tục ra tay đánh tới đòn Hồn Áp thứ hai, tiếp tục giáng nát vòng phòng hộ bạch sắc này, ý định thật giống như muốn mài tới khi nào tiêu hao hết tích trữ của đối phương thì thôi. Section order 4: Paragraph: Cổ Nguyên ánh mắt lạnh lùng nhún chân phóng thẳng về phía địch thủ, một tay cầm đao chém xéo, một tay thò vào trong ngực móc ra hai khoả nhẫn tiếp theo đeo vào. Section order 5: Paragraph: Tư liệu về Hàn Phong xem như tương đối đầy đủ, chuẩn bị của hắn cũng vì thế mà vô cùng đầy đủ. Bước vào trận này, bảy phần nhẫn phòng ngự các đòn công kích tâm linh của huyện Tam Giang đều đã được hắn mang trên người. Section order 6: Paragraph: Muốn hao hết tích luỹ của hắn sao, có giỏi thì nện tới 12 đòn liên tiếp đi. Section order 7: Paragraph: Thế nhưng Cổ Nguyên vừa mới chạy được 50 mét, một luồng công kích vô hình vô sắc khủng bố khác loại đã ập thẳng vào mặt, hai khoả nhẫn vừa mới đeo trên tay không có nửa điểm phát huy tác dụng, trái lại hắn lỗ tai cảm giác lùng bùng đau đớn, trong ngực cũng không nhịn được buồn bực khó chịu, gân xanh trên trán chi chít nổi lên như những con mãng xà tím đen. Section order 8: Paragraph: - ... Section order 9: Paragraph: Một cỗ sóng âm như thác lũ cuồn cuộn từ phương hướng bên kia ập thẳng tới bên này, đánh cho hắn xây xẩm mặt mày,...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 430.docx; chapter_title=Chương 430: Hàn Phong vs Cổ Nguyên (3); ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=53 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
