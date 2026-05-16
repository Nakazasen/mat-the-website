# Draft Knowledge: Chương 380

- source_id: ingest-37fe7adb24074a4d
- raw_file: raw/Chương 380.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Hàn Phong đã uỷ nhiệm toàn bộ trách nhiệm cho Liễu Huyên và Lam Nhu Thuỷ, tất nhiên sẽ không tham gia vào những công việc này, hiện tại đã vậy, sau này cũng vậy, hắn không nhìn quá trình nữa mà chỉ muốn nhìn kết quả. Section order 5: Paragraph: Đây không phải biểu hiện của dân chủ, đây là biểu hiện của lười. Lười giao tiếp đôi co cùng đám Tam Giang, lười cùng nhân viên tầng thấp như bọn họ tranh cãi, chẳng có tác dụng quái gì cả mà chỉ càng lộ ra điểm yếu của bản t...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- level

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Lam Nhu
- Tam Giang

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
- explain Chương 380
- summarize Chương 380
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 380.docx Chapter title: Chương 380 Section count: 63 Section order 1: Heading: Chương 380 Section order 2: Paragraph: 11–14 minutes Section order 3: Paragraph: Đám người Phó Tế Tường không còn lựa chọn nào khác, cuối cùng chỉ có thể cùng nhân viên công tác rời đi. Section order 4: Paragraph: Hàn Phong đã uỷ nhiệm toàn bộ trách nhiệm cho Liễu Huyên và Lam Nhu Thuỷ, tất nhiên sẽ không tham gia vào những công việc này, hiện tại đã vậy, sau này cũng vậy, hắn không nhìn quá trình nữa mà chỉ muốn nhìn kết quả. Section order 5: Paragraph: Đây không phải biểu hiện của dân chủ, đây là biểu hiện của lười. Lười giao tiếp đôi co cùng đám Tam Giang, lười cùng nhân viên tầng thấp như bọn họ tranh cãi, chẳng có tác dụng quái gì cả mà chỉ càng lộ ra điểm yếu của bản thân mà thôi. Section order 6: Paragraph: Tốt nhất là cho hai người phụ nữ đi cãi nhau với đám này, để xem xem họ có thắng nổi nữ nhân không. Section order 7: Paragraph: Hàn Phong xách theo vali tiến tới phòng quân y. Sau cuộc chiến vừa rồi có 28 người cả đội viên cả thường dân bị thương, nặng nhẹ đủ cả, hắn ở chỗ này đứng ra tuyên dương cổ vũ, động viên tinh thần, thưởng nóng một số lượng điểm cống hiến nhất định, hứa hẹn với thân nhân liệt sĩ, đồng thời cam kết đảm bảo quyền lợi cho tất cả mọi người. Section order 8: Paragraph: Xem như làm tròn chức trách của một vị thủ lĩnh. Section order 9: Paragraph: Sau khi hoàn thành xong công việc này, Hàn Phong lại tiến tới một khu nhà thấp tầng sát bên cạnh khu quân y, đây là khu điều trị chấn thương tâm lý, hay nói chính xác hơn là khu bệnh tâm thần. Bệnh nhân nơi...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 380.docx; chapter_title=Chương 380; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=62 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
