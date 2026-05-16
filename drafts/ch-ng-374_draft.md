# Draft Knowledge: Chương 374

- source_id: ingest-2f215947d5d9fedc
- raw_file: raw/Chương 374.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Hàn Phong thực hiện theo các bước tuần tự được dạy từ việc nạp đạn, chỉnh ống ngắm, đo khoảng cách, tính tốc độ gió, tính toán độ lệch, tính toán lực hút trái đất, dự đoán chuyển động mục tiêu… Sau 5 phút, hắn đã ngắm chuẩn một thây ma level 3 phía xa xa, sẵn sàng hạ gục mục tiêu chỉ với một viên đạn. Section order 5: Paragraph: Hàn Phong khuôn mặt âm trầm nhìn khẩu súng ngắm AWM trong tay, đội bảo dưỡng súng đạn chắc chắn phải bị trừ lương, khẩu súng ngu này hỏng...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- level
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Sau
- AWM

### Modules
- none

### Errors
- 500 m
- 4000 th

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
- explain Chương 374
- summarize Chương 374
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 374.docx Chapter title: Chương 374: Tàn sát (1) Section count: 54 Section order 1: Heading: Chương 374: Tàn sát (1) Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong thực hiện theo các bước tuần tự được dạy từ việc nạp đạn, chỉnh ống ngắm, đo khoảng cách, tính tốc độ gió, tính toán độ lệch, tính toán lực hút trái đất, dự đoán chuyển động mục tiêu… Sau 5 phút, hắn đã ngắm chuẩn một thây ma level 3 phía xa xa, sẵn sàng hạ gục mục tiêu chỉ với một viên đạn. Section order 4: Paragraph: Bất quá, sự thật tàn khốc thường xảy đến vào lúc người ta kỳ vọng nhất. Sau khi bắn khoảng 8 viên đạn liên tục, hắn không bắn trúng bất kỳ viên nào cả. Section order 5: Paragraph: Hàn Phong khuôn mặt âm trầm nhìn khẩu súng ngắm AWM trong tay, đội bảo dưỡng súng đạn chắc chắn phải bị trừ lương, khẩu súng ngu này hỏng rồi mà vẫn cung cấp ra tiền tuyến, quả thật là không thể chấp nhận nổi. Section order 6: Paragraph: - Aizzzz… Nếu có đội ngũ bắn tỉa 100 người, mỗi người đều là thần xạ thủ đứng sau xạ kích, vậy thì thi đàn 2 vạn sẽ bị giải quyết sau nửa giờ đồng hồ… Section order 7: Paragraph: Bắn súng ngắm là một công việc không hề đơn giản. Trong dưới một giây, người ta phải tính toán hàng trăm phép tính khác nhau từ rất nhiều dữ kiện khác nhau, đảm bảo việc đạn bắn đúng hướng và chuẩn xác. Khoảng cách càng xa, các yếu tố tác động lên viên đạn càng lớn, tỉ lệ trượt đích càng lớn. Section order 8: Paragraph: Đơn cử như việc bắn vào đầu của Thể Sức Mạnh level 20 trở lên là vô cùng khó khăn, bởi vì loại quái vật này luôn có hào quang trọng lực lớn lao...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 374.docx; chapter_title=Chương 374: Tàn sát (1); ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=53 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
