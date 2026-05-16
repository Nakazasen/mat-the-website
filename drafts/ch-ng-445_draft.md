# Draft Knowledge: Chương 445

- source_id: ingest-f9c307c35df63b3a
- raw_file: raw/Chương 445.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Tiết Xuyên, Tần Nam, Hồ Du, Lưu Cầu, Đàm Quang, Hạ Ái Linh, Mạc Bội San... Đây đều là những tân thủ lĩnh tương lai, là những người tiếp theo bước lên vũ đài phi phàm, cùng nhau xây đắp lên sự vững mạnh của trấn Hi Vọng, đem tổ chức này ngày một vươn cao, ngày một toả bóng rộng, đủ sức để che phủ và bảo vệ cho hàng nghìn người. Section order 6: Paragraph: Đây là miếng mồi ngon mà bất kỳ ai đều không thể cưỡng lại. Nếu có thể số hoá thành số liệu để so sánh, vậy thì...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- level

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Hi
- Nam
- Du

### Modules
- none

### Errors
- 445
- 445: L

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
- explain Chương 445
- summarize Chương 445
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 445.docx Chapter title: Chương 445: Lợi và ích Section count: 39 Section order 1: Heading: Chương 445: Lợi và ích Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Cây muốn vươn cao cần có gốc rễ đủ mạnh, nhưng cây muốn toả bóng rộng cũng cần phải có cành lá xum xuê. Biển muốn mặn cần nhiều sông hợp sức, nhưng sông muốn chảy cũng cần suối nhỏ góp nguồn. Trấn Hi Vọng có thượng tầng chắc chắn, đại nghĩa vững mạnh, nhưng điều quan trọng nhất chính là cần có cả hạ tầng mỗi ngày một nỗ lực cố gắng, cần có nguồn máu mới bổ sung liên tục, xây dựng tổ chức theo cả chiều dọc lẫn chiều ngang. Chỉ có không ngừng tiến lên mới có thể thoát khỏi tận thế u ám tăm tối này, một khi dừng lại, chính là vĩnh viễn bị bỏ lại phía sau, vĩnh viễn biến thành máu thịt cho thây ma và cho cả kẻ khác xơi tái. Section order 4: Paragraph: Tiết Xuyên, Tần Nam, Hồ Du, Lưu Cầu, Đàm Quang, Hạ Ái Linh, Mạc Bội San... Đây đều là những tân thủ lĩnh tương lai, là những người tiếp theo bước lên vũ đài phi phàm, cùng nhau xây đắp lên sự vững mạnh của trấn Hi Vọng, đem tổ chức này ngày một vươn cao, ngày một toả bóng rộng, đủ sức để che phủ và bảo vệ cho hàng nghìn người. Section order 5: Paragraph: Hàn Phong để cho người bên dưới tung ra tin tức rằng sau chiến dịch trấn Thiết Thạch sẽ cơ cấu lại tổ chức quân đội thành một tiểu đoàn hợp nhất, ít nhất sẽ có thêm 5 biên chế tiểu đội trưởng, cái này đã khiến cho nhiệt huyết của tất cả mọi người đều bị đốt đến sôi sục, ai nấy đều ra sức thể hiện bản thân, bằng mọi cách đoạt lấy danh ngạch dẫn đầu bảng chiến công. Section order 6:...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 445.docx; chapter_title=Chương 445: Lợi và ích; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=38 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
