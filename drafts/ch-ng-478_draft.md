# Draft Knowledge: Chương 478

- source_id: ingest-eeb98622c04495c5
- raw_file: raw/Chương 478.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Sau hiệu lệnh quen thuộc của Hàn Phong, cuộc họp đầu tiên sau kỳ nghỉ của cao tầng trấn Hi Vọng chính thức diễn ra. Section order 13: Paragraph: Hai vị trí này không nằm ngoài dự đoán của mọi người, đó là điều tất nhiên rồi. Hai người Hàn Phong, Ngô Soái chẳng những là người thành lập lên trấn Hi Vọng, họ còn là hai người có thực lực cao nhất, chiến công nhiều nhất, thâm niên dài lâu nhất, và cũng tích luỹ uy vọng đầy đủ nhất, không ai có thể thắc mắc được. Section...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Hi
- Section
- Heading
- Paragraph
- Sau
- Phong

### Modules
- none

### Errors
- 478
- 478: Ti
- 500 chi
- 531 c

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
- explain Chương 478
- summarize Chương 478
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 478.docx Chapter title: Chương 478: Tiểu đoàn Hi Vọng Section count: 104 Section order 1: Heading: Chương 478: Tiểu đoàn Hi Vọng Section order 2: Paragraph: 11–14 minutes Section order 3: Paragraph: Sau hiệu lệnh quen thuộc của Hàn Phong, cuộc họp đầu tiên sau kỳ nghỉ của cao tầng trấn Hi Vọng chính thức diễn ra. Section order 4: Paragraph: Các tiểu đội trưởng đều đồng loạt nghiêm túc hẳn lên, ai nấy tinh thần tập trung cao độ, tâm trạng có thể nói là vô cùng hồi hộp. Nhóm người cũ thì hi vọng được thăng chức, thăng lương, nhóm người mới thì mong chờ nhận được quyết định bổ nhiệm, đến ngay cả Ngô Soái cũng khẽ nắm chặt bàn tay. Trên cơ bản, hắn dù đã biết trước kết quả, thế nhưng đối với môi trường quân ngũ vẫn có rất nhiều chấp niệm. Section order 5: Paragraph: - Dựa theo tình hình thực tế, tôi quyết định tổ chức lại nhân sự cho quân đội của chúng ta. Toàn bộ đội viên sẽ được tập trung biên chế lại thành một tiểu đoàn duy nhất. Section order 6: Paragraph: Âm thanh trầm khàn của Hàn Phong vang lên, đám người phía dưới lại càng tập trung lớn hơn. Một tiểu đoàn sao, tiểu đoàn trưởng thì khỏi nói rồi, vị trí đó ai cũng sẽ rõ là người nào đảm nhiệm, thế nhưng những chức danh còn lại bên dưới mới đáng để lưu tâm a. Section order 7: Paragraph: Hàn Phong lúc này tiếp tục phất tay, hai đội viên đội hậu cần theo đó bắt đầu tiến lên phân phát tài liệu. Section order 8: Paragraph: Sau khi tài liệu được phân phát xong, một đội viên đội hậu cần khác cầm lên tờ A4 bắt đầu đọc to rõ ràng: Section order 9: Paragraph: - Tiểu đoàn Hi Vọng. Section order 10: Paragraph: - S...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 478.docx; chapter_title=Chương 478: Tiểu đoàn Hi Vọng; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=103 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
