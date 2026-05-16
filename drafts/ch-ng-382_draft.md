# Draft Knowledge: Chương 382

- source_id: ingest-64bc4166b702fb5e
- raw_file: raw/Chương 382.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Trong số này có phiếu xuất thực phẩm cho thành viên Dao Găm. Có phiếu xuất lượng lớn sữa cho bà bầu, thương binh, trẻ em dưới 6 tuổi. Có phiếu xuất lương khô và xúc xích ăn liền dự phòng trong chiến đấu cho đội viên cả 16 tiểu đội. Phiếu xuất nước tăng lực và điện giải bổ sung cho đội xây dựng tường thành. Phiếu xuất vật tư đền bù cho thân nhân của liệt sĩ, cho những người còn hôn mê chưa tỉnh… Section order 8: Paragraph: Tám tờ phiếu xuất kho này chủ yếu là muốn v...

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
- Section
- Heading
- Paragraph
- Phong
- Trong
- Dao

### Modules
- none

### Errors
- 500 l

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
- explain Chương 382
- summarize Chương 382
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 382.docx Chapter title: Chương 382: Báo cáo công việc (2) Section count: 55 Section order 1: Heading: Chương 382: Báo cáo công việc (2) Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Chửi bới phát tiết một hồi, Hàn Phong cuối cùng vẫn là đọc sơ qua một lượt rồi nhắm mắt ký bừa cả tám phiếu xuất kho. Section order 4: Paragraph: Trong số này có phiếu xuất thực phẩm cho thành viên Dao Găm. Có phiếu xuất lượng lớn sữa cho bà bầu, thương binh, trẻ em dưới 6 tuổi. Có phiếu xuất lương khô và xúc xích ăn liền dự phòng trong chiến đấu cho đội viên cả 16 tiểu đội. Phiếu xuất nước tăng lực và điện giải bổ sung cho đội xây dựng tường thành. Phiếu xuất vật tư đền bù cho thân nhân của liệt sĩ, cho những người còn hôn mê chưa tỉnh… Section order 5: Paragraph: Tất cả đều quan trọng, đều phải ký duyệt ngay. Section order 6: Paragraph: Thật ra Phương Tường đã làm rất tốt rồi, công việc của lão là nhiều sự tình vặt vãnh phức tạp nhất nhưng chưa từng xuất hiện hỗn loạn qua, lão chính là người ít gây ra sự phiền toái cho hắn nhất rồi. Section order 7: Paragraph: Lo cái ăn cái mặc cho hơn 1000 người dưới sự “cai trị tàn bạo” của Hàn Phong là không hề dễ dàng, những chỉ tiêu khắc nghiệt liên tiếp được hắn giáng xuống nhằm hạn chế tiêu hao cho kho vật tư và áp đặt sự nghèo khổ lên cư dân trấn Hi Vọng, lão phải gồng mình ứng phó cả trên cả dưới vô cùng vất vả, vậy nhưng đơn từ khiếu nại nhận về chẳng có bao nhiêu Section order 8: Paragraph: Tám tờ phiếu xuất kho này chủ yếu là muốn vòi thêm tài nguyên ngoài định mức, ngoài chỉ tiêu, vòi thêm tài nguyên cho...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 382.docx; chapter_title=Chương 382: Báo cáo công việc (2); ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=54 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
