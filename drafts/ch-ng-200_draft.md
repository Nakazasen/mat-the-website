# Draft Knowledge: Chương 200

- source_id: ingest-eb1618ae3f39ac4c
- raw_file: raw/Chương 200.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 20: Paragraph: Người chó cao hơn 3 mét đột nhiên hoảng hốt khựng lại, nó kinh ngạc đảo mắt dáo dác nhìn quanh. Sau khi nhìn thấy Hàn Phong đang đứng đó ngửa cổ hú dài, nó lập tức nhe răng sủa ầm lên: Section order 32: Paragraph: Hàn Phong khoé miệng co giật, hắn thật có xúc động huy động súng chống tăng tới cho nó một viên. Con chó này thù quá dai, đúng với thành ngữ chó cắn không nhả. Section order 43: Paragraph: Hàn Phong thấy chiến cuộc thật sự đã kết thúc thì thở phào một hơ...

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
- Section
- Heading
- Paragraph
- Phong
- Xin
- Chim

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
- explain Chương 200
- summarize Chương 200
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 200.docx Chapter title: Chương 200: Đại Hắc Cẩu Section count: 97 Section order 1: Heading: Chương 200: Đại Hắc Cẩu Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Thẻ tiến giai sơ cấp. Section order 4: Paragraph: Vật phẩm này có thể giúp kỹ năng trải qua 4 lượt cường hoá tiến giai lên nhị giai hoặc lên tam giai. Section order 5: Paragraph: Hàn Phong có một kỹ năng có thể ngay lập tức sử dụng thẻ tiến giai này. Trước đây hắn còn có chút coi thường nó, hiện tại rốt cuộc phải sử dụng. Section order 6: Paragraph: “Kỹ năng bị động nhất giai: Phiên Dịch Đa Năng. Nắm giữ hoàn chỉnh tất cả ngôn ngữ của nhân tộc thuần chủng. Kỹ năng không thể cường hoá, chỉ có thể tiến giai.” Section order 7: Paragraph: Hắn từng nghĩ không ai điên mà đem thẻ tiến giai quý giá ra dùng trên cái kỹ năng có phần gân gà này, thế nhưng hiện tại đã phải dùng, đã cần tới kỹ năng gân gà này trợ trận. Thẻ tiến giai dù hiếm có, nhưng đánh quái nhiều rớt nhiều, tới nay Hàn Phong đã có 5 tấm, dùng 1 tấm không vấn đề gì. Section order 8: Paragraph: Lúc này thẻ tiến giai sơ cấp hoá thành hào quang bao phủ, kỹ năng Phiên Dịch Đa Năng lập tức được thăng cấp. Section order 9: Paragraph: “Đinh! Xin mời lựa chọn ngôn ngữ thông hiểu.” Section order 10: Paragraph: Âm thanh hệ thống lạnh lùng vang lên, đồng thời bảng hệ thống xuất hiện 9 lựa chọn phát sáng có thể lựa chọn, mấy chục lựa chọn khác vẫn tối đen như mực, không thể xem xét, không thể lựa chọn. Section order 11: Paragraph: Chim, thú, côn trùng, bò sát, chân khớp, cá, lưỡng cư, thân mềm, giun. Section order 12: Paragraph:...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 200.docx; chapter_title=Chương 200: Đại Hắc Cẩu; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=96 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
