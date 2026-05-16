# Draft Knowledge: Chương 28

- source_id: ingest-0f91a2b44f7a0929
- raw_file: raw/Chương 28.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 28: Họp bàn chiến thuật. Section order 3: Paragraph: Nghe thấy Hàn Phong nói vậy, Chu Vấn rốt cuộc bình tĩnh lại. Hắn từ chỗ Hứa Dương cũng biết rằng cả ngày hôm nay đám người Hàn Phong đã liên tục chiến đấu cường độ cao, hiện tại vô cùng mệt mỏi, cần phải nghỉ ngơi dưỡng sức. Section order 5: Paragraph: Sau khi Chu Vấn dẫn đầu biểu đạt, mấy người còn lại cũng lần lượt nêu ý kiến.

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
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Nghe

### Modules
- none

### Errors
- 500 exp
- 500 c

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
- explain Chương 28
- summarize Chương 28
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 28.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 28: Họp bàn chiến thuật. Section count: 79 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 28: Họp bàn chiến thuật. Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Nghe thấy Hàn Phong nói vậy, Chu Vấn rốt cuộc bình tĩnh lại. Hắn từ chỗ Hứa Dương cũng biết rằng cả ngày hôm nay đám người Hàn Phong đã liên tục chiến đấu cường độ cao, hiện tại vô cùng mệt mỏi, cần phải nghỉ ngơi dưỡng sức. Section order 4: Paragraph: Mà buổi tối bên ngoài quả thật cũng rất nguy hiểm, hắn dù có gan to bằng trời cũng không dám tự mình xuất chiến. Section order 5: Paragraph: Sau khi Chu Vấn dẫn đầu biểu đạt, mấy người còn lại cũng lần lượt nêu ý kiến. Section order 6: Paragraph: Tiêu Minh, Mộ Thi Thi do dự hồi lâu, cuối cùng chọn cách ở lại căn cứ, làm các công việc tạp vụ. Section order 7: Paragraph: Trung niên nam tử Đường Hiếu rõ ràng rất sốt ruột. Hắn hôm qua đi tới khu đô thị này chơi, hiện tại người nhà vẫn còn ở trung tâm thành phố, hai bên đã mất liên lạc, mà có muốn trở về cũng không được. Section order 8: Paragraph: Nữ tử mặt rỗ Đào Đại Tư trực tiếp biểu đạt quyết tâm cao độ. Nàng ta rất có tư thái nam nhân vỗ ngực bịch bịch, nói bất kỳ lúc nào cũng sẵn sàng làm việc. Section order 9: Paragraph: Hàn Phong để cho bọn họ thoải mái bày tỏ thái độ xong xuôi, lúc này mới chậm rãi hỏi: Section order 10: Paragraph: - Vậy là trong số các vị, có người vẫn còn gậy bóng chày, có người đã thất lạc mất? Tiêu Minh cùng Mộ Thi Thi, cẩn thận nhớ lại, đồng thanh nói: Section order 11: Paragr...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 28.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 28: Họp bàn chiến thuật.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=78 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
