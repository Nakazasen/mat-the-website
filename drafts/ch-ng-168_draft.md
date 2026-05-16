# Draft Knowledge: Chương 168

- source_id: ingest-56c941823fd55bcc
- raw_file: raw/Chương 168.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 8: Paragraph: Qua mấy phút chờ đợi, Trần Diệu Âm rốt cuộc từ phía xa xa chạy tới hậu tuyến. Chờ nàng ta mang báo cáo trình lên xong, Hàn Phong mới phất tay nói: Section order 13: Paragraph: Hàn Phong nhướng mày, sau đó gật đầu nói với Quan Bình: Section order 18: Paragraph: Sau khi nhìn Quan Bình rời đi, Hàn Phong trầm giọng nói:

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- quan

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Quang
- Phong
- Ba

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
- explain Chương 168
- summarize Chương 168
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 168.docx Chapter title: Chương 168: Tách đàn (1) Section count: 99 Section order 1: Heading: Chương 168: Tách đàn (1) Section order 2: Paragraph: 11–13 minutes Section order 3: Paragraph: Ngồi trên tán cây ngô đồng, Trần Diệu Âm chỉ cảm thấy vòng phòng hộ từ kỹ năng nhị giai Quang Giáp hơi run rẩy một chút, sau đó là từ từ bình tĩnh lại. Section order 4: Paragraph: Nàng ta chờ đợi hơn 10 phút đồng hồ mới lấy ra giấy bút rồi ghi chép chi tiết, sau đó cẩn thận từng li từng tí chui xuống, dựa theo lối đi nhỏ xíu không có dịch keo dính nhớp mà thoát khỏi tán cây, leo lên xe jeep cơ động cao, băng băng chạy về hậu tuyến. Section order 5: Paragraph: Tại hậu tuyến, Hàn Phong lấy ra ống nhòm chăm chú quan sát, sau khi xác nhận cả hai con thể tốc độ level 14 và level 18 đều thoát kiếp thì cũng có chút tiếc nuối. Section order 6: Paragraph: Ba con quái vật thể tốc độ này khoảng cách cách xa nhau, hứng chịu thương tổn từ vụ nổ không giống nhau. F1 level 18 sau khi lột một lớp da thì cũng thành công thoát nạn, về phần F1 level 14, nó cách quá xa, chỉ bị cháy xém nhè nhẹ. Section order 7: Paragraph: Thi đàn đã thành công bị hấp dẫn. 5 đầu thể sức mạnh, 3 đầu thể tốc độ cùng 1 con thể phòng hộ được cử ra canh giữ liên tục, tiến hành phòng hộ khu vực ngoại biên mà không trở về trung tâm nữa. Section order 8: Paragraph: Qua mấy phút chờ đợi, Trần Diệu Âm rốt cuộc từ phía xa xa chạy tới hậu tuyến. Chờ nàng ta mang báo cáo trình lên xong, Hàn Phong mới phất tay nói: Section order 9: Paragraph: - Cô cùng với Quan Bình trở về trước đi. Section order 10: Paragraph: Nữ nhân n...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 168.docx; chapter_title=Chương 168: Tách đàn (1); ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=98 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
