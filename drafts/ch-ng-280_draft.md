# Draft Knowledge: Chương 280

- source_id: ingest-227aa82afc92c870
- raw_file: raw/Chương 280.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Dù sao đối với một đội ngũ chuyên đánh nhau vào sinh ra tử, sống đời phóng túng, cách chiến thắng bằng mưu hèn kế bẩn của Hàn Phong là chưa đủ thuyết phục, chưa làm cho đối phương phải chịu thua. Trong trường hợp này, càng nói nhiều chỉ càng thu về nhiều bất mãn. Section order 9: Paragraph: Hàn Phong xoay người bước ra ngoài. Hắn đã căn dặn Nhạc Sơn, Sử Thắng, Lưu Giang nhìn chằm chằm nơi này, bên ngoài có 30 đội viên thay nhau canh chừng, bên trong có Hà Tam, Uông...

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
- Hi

### Modules
- none

### Errors
- 500 d

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
- explain Chương 280
- summarize Chương 280
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 280.docx Chapter title: Chương 280: Kiến tạo môi trường sống Section count: 53 Section order 1: Heading: Chương 280: Kiến tạo môi trường sống Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Đối với đám tàn binh thôn Xuân Lê này, Hàn Phong không muốn tiếp xúc hay giao thiệp bằng lời nói quá nhiều. Trên thực tế, cái nhìn của người sống sót bình thường đối với hắn có thể coi như “đấng cứu thế”, nhưng với đám người này thì không, họ chỉ coi hắn là kẻ thắng trận mà thôi, sẽ không dâng lên cảm kích hay nhiệt liệt đón chào, thậm chí một bộ phận không nhỏ còn đang ngầm bất mãn. Section order 4: Paragraph: Dù sao đối với một đội ngũ chuyên đánh nhau vào sinh ra tử, sống đời phóng túng, cách chiến thắng bằng mưu hèn kế bẩn của Hàn Phong là chưa đủ thuyết phục, chưa làm cho đối phương phải chịu thua. Trong trường hợp này, càng nói nhiều chỉ càng thu về nhiều bất mãn. Section order 5: Paragraph: Hắn sẽ dùng cách trực tiếp và cứng rắn hơn để quản lý. Section order 6: Paragraph: - Được rồi, anh tiếp tục ổn định tình hình, cho người quan sát và canh chừng thật kỹ bọn họ, tìm ra những mầm mống phản loạn tiềm tàng… 30 phút nữa, hãy trở lại tổng bộ trấn Hi Vọng. Section order 7: Paragraph: Hà Tam vội vã cúi người đáp: Section order 8: Paragraph: - Tuân lệnh thủ lĩnh. Section order 9: Paragraph: Hàn Phong xoay người bước ra ngoài. Hắn đã căn dặn Nhạc Sơn, Sử Thắng, Lưu Giang nhìn chằm chằm nơi này, bên ngoài có 30 đội viên thay nhau canh chừng, bên trong có Hà Tam, Uông Hùng trấn giữ. Đã bị tịch thu hết vũ khí, cũng đứt nguồn tiếp tế, bọn này sẽ chẳng...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 280.docx; chapter_title=Chương 280: Kiến tạo môi trường sống; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=52 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
