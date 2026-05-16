# Draft Knowledge: Chương 365

- source_id: ingest-318840b5313b94f7
- raw_file: raw/Chương 365.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 20: Paragraph: Sự lạnh lùng cùng vô cảm của Hàn Phong thực ra rất lớn, thế nhưng khi đứng trước nỗ lực bào mòn của cả nghìn người, hắn đã không giữ được bản tâm “đứng ngoài cuộc” nữa, đã dần trở nên nhỏ bé, đã không còn là Hàn Phong của những ngày đầu nữa. Section order 23: Paragraph: Hàn Phong chậm rãi thu ánh mắt dưới sân lại rồi chuyển tầm nhìn về phương bắc. Đó là địa điểm của trấn Vân Minh, nơi đang tồn tại 2 vạn thây ma, cùng với hơn 10 vạn thây ma tới từ huyện Long Dương...

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
- Hi
- Thanh

### Modules
- none

### Errors
- 500 ng

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
- explain Chương 365
- summarize Chương 365
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 365.docx Chapter title: Chương 365 Section count: 43 Section order 1: Heading: Chương 365 Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Giấc mộng vừa mới trôi qua ngoài cửa sổ thực sự vô cùng đơn sơ mộc mạc, đồng thời cũng tràn đầy hình ảnh nhàm chán của thế giới trước đây, thế nhưng ngược lại nó cũng mang tới cho Hàn Phong cảm giác vô cùng an tường bình lặng. Dường như sau 19 ngày tận thế, đêm qua là đêm duy nhất mà hắn cảm nhận được một giấc ngủ trọn vẹn. Section order 4: Paragraph: Chưa bao giờ hắn cảm giác thoải mái như lúc này. Section order 5: Paragraph: “Có đôi khi chỉ là việc ngủ trong căn phòng oi bức chật hẹp, nghe thấy tiếng báo thức quen thuộc, ăn một cái bánh đã ăn cả nghìn lần, tán dóc vài câu với người thân bên cạnh, lao đầu vào công việc để thiêu đốt tuổi trẻ, lầu bầu chửi sếp nhưng vẫn nỗ lực hàng giờ lại hàng giờ. Bấy nhiêu đó cũng đủ quý giá để bảo vệ, để trân trọng, để khắc ghi… Tự hỏi bản thân, liệu bao lâu nữa mới được trở về những ngày xưa cũ…” Section order 6: Paragraph: Hàn Phong đem chiếc chăn trên ngực để qua một bên rồi bước từng bước tới sát cửa sổ. Ánh mắt nửa mơ hồ nửa hốt hoảng của hắn theo đó hướng xuống sân rộng. Từ vị trí này có thể bao quát toàn bộ khung cảnh mấy trăm mét xung quanh, từng dãy nhà, từng góc tường, từng khu vực vòng trong vòng ngoài, toàn bộ trấn Hi Vọng đều hiện lên dưới một màu hôn ám. Section order 7: Paragraph: Cư dân từ Xuân Lê là nhóm người vô cùng chăm chỉ. Dù mới chỉ 5 giờ sáng nhưng sớm đã có một nhóm lớn người sớm vác theo cuốc xẻng mà lũ lượt kéo ra khỏi cổng trấn. Bọn...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 365.docx; chapter_title=Chương 365; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=42 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
