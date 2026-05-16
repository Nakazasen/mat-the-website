# Draft Knowledge: Chương 86

- source_id: ingest-65dc77bff26934d1
- raw_file: raw/Chương 86.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 86: Nhiệm vụ tiếp theo Section order 18: Paragraph: Hàn Phong lẩm bẩm suy tư. Thi đàn 10.000 con có tổ chức sao? Vậy thì bọn nó sẽ tụ họp lại… Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 86: Nhiệm vụ tiếp theo

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
- Phong

### Modules
- none

### Errors
- 500 nh

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
- explain Chương 86
- summarize Chương 86
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 86.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 86: Nhiệm vụ tiếp theo Section count: 103 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 86: Nhiệm vụ tiếp theo Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Âm thanh hệ thống tuy lạnh lùng nhưng lại khiến cho Hàn Phong thở phào. Cũng may, cũng may, vẫn còn nhận được nhiệm vụ. Section order 4: Paragraph: Lựa chọn đầu tiên tăng lên 3 cấp, tất nhiên đủ sức hấp dẫn, thuộc về dạng không làm mà vẫn có ăn. Nhưng 3 cấp độ đối với Hàn Phong hiện tại không phải quá khó, thông thường 1 ngày gắng sức có thể tăng một cấp, cùng lắm là 2 ngày. Section order 5: Paragraph: Lựa chọn thứ hai, Hàn Phong trực tiếp bỏ qua. Nói đùa, hắn hiện tại đã tương đối đủ đầy năng lực, trang bị cũng không quá cần thiết phải bổ sung. Nhất là lựa chọn mang tính ngẫu nhiên như vậy, hắn càng không muốn cân nhắc chút nào. Section order 6: Paragraph: Bởi vậy Hàn Phong trong lòng mặc niệm: Section order 7: Paragraph: - Lựa chọn tiếp nhận nhiệm vụ. Section order 8: Paragraph: “Đinh! Xác nhận nhiệm vụ sơ cấp: Đứng vững gót chân. Nhiệm vụ miêu tả: Cứu sống và tập hợp 500 nhân loại trong vùng an toàn. Đánh tan hai đợt tấn công có tổ chức của thi đàn quy mô ít nhất 1 vạn. Thời gian thực hiện: 360 giờ.” Section order 9: Paragraph: “Nhiệm vụ hoàn thành nhận ban thưởng: một sách kỹ năng tứ giai; một thẻ trang bị level 4; một tinh thạch an toàn.” Section order 10: Paragraph: “Nhiệm vụ thất bại: Giáng trừ 3 cấp.” Section order 11: Paragraph: Xác nhận xong nhiệm vụ, Hàn Phong bắt được hai cái tình báo quan tr...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 86.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 86: Nhiệm vụ tiếp theo; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=102 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
