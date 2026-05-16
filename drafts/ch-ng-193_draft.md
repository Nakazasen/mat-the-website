# Draft Knowledge: Chương 193

- source_id: ingest-2ea44927158127c1
- raw_file: raw/Chương 193.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 8: Paragraph: Sau khi đã xác nhận xong, Hàn Phong giơ tay lên làm một cái thủ thế với đám người đối diện. Section order 12: Paragraph: Đây không chỉ là thời cơ cho Thanh Liễu, đây còn là thời cơ cho Thanh Lâm, Thanh Hà. Section order 15: Paragraph: Dựa vào sự hỗn loạn của thi đàn dưới chân, đám người Chu Vấn rất nhanh tiếp cận tới khu vực P2 và F2 đang đứng mà không bị phát hiện, sau đó Chu Vấn trực tiếp xách theo Lý Võ Lạc vượt qua khu vực này, tiến về phía sau bọn chúng 100 mét.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- thanh
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Sau
- IQ
- F2

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
- explain Chương 193
- summarize Chương 193
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 193.docx Chapter title: Chương 193: Thời cơ Section count: 77 Section order 1: Heading: Chương 193: Thời cơ Section order 2: Paragraph: 9–11 minutes Section order 3: Paragraph: Hắn đặt cược kẻ sau màn đang gặp phải vấn đề nhất định. Sau khi dùng hai lần kỹ năng công kích tinh thần dạng quần thể, nó đã gặp vấn đề, khoảng thời gian này sẽ không thể bảo hộ lũ lâu la dưới trướng, buộc phải để mặc quân lính muốn làm gì thì làm. Section order 4: Paragraph: Hắn đặt cược IQ của kẻ sau màn không đủ cao, từ đầu tới cuối đều bị động đối kháng, để hắn dắt mũi theo kế hoạch chứ không có lừa trong lừa nào ở đây. Section order 5: Paragraph: Hắn còn đặt cược việc F2 level 20 kia sẽ chạy trốn ra phía sau, nơi quang đãng trống trải hơn để thoái lui, và chỉ chạy ra phía sau mà thôi. Section order 6: Paragraph: Và hắn cược thắng, thắng toàn bộ. Section order 7: Paragraph: Hai viên đạn bới ra ba nghi vấn, lại hoá thành một liều thuốc an thần, để hắn tự tin hơn rất nhiều, cái giá chờ đợi này tương đối xứng đáng. Section order 8: Paragraph: Sau khi đã xác nhận xong, Hàn Phong giơ tay lên làm một cái thủ thế với đám người đối diện. Section order 9: Paragraph: Chu Vấn lập tức hiểu ý, dẫn theo đội viên bắt đầu tiếp cận gần hơn. Section order 10: Paragraph: Pằng! Viên đạn diệt quỷ thứ ba được bắn ra, không trung vẽ lên một vệt đen kịt hắc hoả, vút một tiếng nối liền giữa nòng súng và khiên chắn huyết sắc. Section order 11: Paragraph: Mỗi viên đạn được bắn ra, không chỉ đám thây ma tại trung tâm thi đàn bị doạ sợ, đám thây ma cấp cao lúc nhúc đứng xung quanh cũng bị doạ cho chấn ki...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 193.docx; chapter_title=Chương 193: Thời cơ; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=76 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
