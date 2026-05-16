# Draft Knowledge: Chương 329

- source_id: ingest-44dc3e893207dacc
- raw_file: raw/Chương 329.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Một người một chó vẫn có nhiệm vụ ở Tam Giang như cũ. Mặc dù kế hoạch của Hàn Phong không còn là giết ch.ết tất cả nhân viên công tác vòng ngoài đang đồn trú tại các trục đường chính nữa, thế nhưng hắn vẫn phải tự mình thu thập tình báo bên kia, đồng thời cũng không ngại gây áp lực lên thi đàn khiến cho đám người kia không thể phân tâm đối phó với trấn Hi Vọng. Section order 4: Paragraph: Đặc biệt là thi đàn ngay tại phía bên kia cầu Liễu Hà, hắn muốn một lần nữa d...

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
- Tam Giang
- Phong
- Hi

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
- explain Chương 329
- summarize Chương 329
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 329.docx Chapter title: Chương 329 Section count: 70 Section order 1: Heading: Chương 329 Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Một người một chó vẫn có nhiệm vụ ở Tam Giang như cũ. Mặc dù kế hoạch của Hàn Phong không còn là giết ch.ết tất cả nhân viên công tác vòng ngoài đang đồn trú tại các trục đường chính nữa, thế nhưng hắn vẫn phải tự mình thu thập tình báo bên kia, đồng thời cũng không ngại gây áp lực lên thi đàn khiến cho đám người kia không thể phân tâm đối phó với trấn Hi Vọng. Section order 4: Paragraph: Đặc biệt là thi đàn ngay tại phía bên kia cầu Liễu Hà, hắn muốn một lần nữa dẫn dụ chúng nó bít chặn con đường thông thương giữa hai bên, khiến chính quyền Tam Giang có muốn dẫn quân qua bên này cũng sẽ không đơn giản thích đánh là đánh. Section order 5: Paragraph: Chạy được một đoạn, phân thân Ảnh Chiếu mới nghi hoặc sủa to: Section order 6: Paragraph: - Gâu gâu… Section order 7: Paragraph: “Đại Hắc Cẩu, ngươi cứ như vậy rời đi mà không sợ lũ chuột kia cắn phá bảo bối sao? Gâu!” Section order 8: Paragraph: Trong bóng đêm, hai con mắt Đại Hắc Cẩu phát ra hai luồng ánh sáng xanh lục lập loè đáng sợ, nó nhe răng nhếch miệng ngửa cổ hú lên một tràng dài tràn ngập kiêu ngạo: Section order 9: Paragraph: - Húuuuuu… Section order 10: Paragraph: “Ta vừa đánh dấu lãnh thổ tại bốn xung quanh, hiện tại những con chuột nhắt kia chỉ cần ngửi thấy mùi đã sợ ch.ết khiếp, làm sao dám bén mảng tới gần. Gâu!” Section order 11: Paragraph: Trấn Hi Vọng, Hàn Phong sau khi một lần nữa căn dặn đám đội viên tăng cường công tác tuần tr.a...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 329.docx; chapter_title=Chương 329; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=69 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
