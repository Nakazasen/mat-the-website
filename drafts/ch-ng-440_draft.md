# Draft Knowledge: Chương 440

- source_id: ingest-77263cbf5daeab2c
- raw_file: raw/Chương 440.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 10: Paragraph: Tin xấu nhất là thi đàn này có 1 thây ma Shield-2 level 29, 2 thây ma S2 level 28, 1 thây ma S2 level 27, 3 thây ma S2 level 25... Hiện tại Hàn Phong vẫn chưa có cách nào vừa hiệu quả lại vừa tiết kiệm để làm thịt mấy con lợn mồm rộng này ngoài việc nã đạn chống tăng liên tiếp không ngừng nghỉ, mài dần năng lực của chúng nó. Section order 11: Paragraph: Hắn vừa chôm được tám phần mười kho đạn của Tam Giang, chỉ riêng đạn chống tăng loại hình PG-7V và PG-9V mà trấn...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- level
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Thao
- Hi

### Modules
- none

### Errors
- 440
- 440: Chi

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
- explain Chương 440
- summarize Chương 440
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 440.docx Chapter title: Chương 440: Chiến tranh bất đối xứng Section count: 43 Section order 1: Heading: Chương 440: Chiến tranh bất đối xứng Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Thây ma đầu tiên bước vào rãnh hào sâu số 4, sau đó là thây ma thứ hai, thứ ba, thứ mười, sau đó là hàng trăm thây ma thi nhau tiến vào khu vực 10 luồng chiến hào này, khởi đầu cho cuộc giao tranh đầu tiên giữa thi đàn 7 vạn và gần 600 nhân loại. Section order 4: Paragraph: Đứng ở xa xa khoảng cách 1 cây số quan sát tình hình chiến trường, Hàn Phong đem ống nhòm soi xét kỹ lưỡng từng đợt thây ma xâm nhập trận địa, muốn từ tình hình toàn thể để xem thử trình độ biến đổi của ngày thứ 22 tận thế. Đây là lần đầu tiên hắn tiếp xúc một thi đàn có chỉ huy kể từ khi tinh thạch an toàn được phân phát, nhân loại đã thăng tiến mạnh mẽ, còn thây ma thì sao? Section order 5: Paragraph: Cũng còn may, gần tám phần thi đàn vẫn đang duy trì ở cấp độ 1, chúng nó dường như không được nâng cấp toàn diện từ trên xuống dưới. Xét về mặt hạ tầng, thi đàn này có sức mạnh ngang ngửa với thi đàn tại Xuân Lê. Section order 6: Paragraph: Có điều thành phần thượng tầng của thi đàn tại đây lại cao cấp hơn hẳn thi đàn Xuân Lê, cấp độ cao nhất của thây ma Thiết Thạch là level 29, tức là Thể Thao Túng ở đây có thể đạt cấp 28 hoặc cấp 29. Số lượng thây ma cấp cao cũng vô cùng đông đúc, với thống kê gần chính xác là 118 thây ma trên level 20, tương đương việc cứ hai đội viên chính thức phải đối phó một thây ma tiến hoá mạnh mẽ, một con số vô cùng khủng bố, cái này đã gấp đôi năng l...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 440.docx; chapter_title=Chương 440: Chiến tranh bất đối xứng; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=42 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
