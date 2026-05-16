# Draft Knowledge: Chương 127

- source_id: ingest-b8528431a76002d7
- raw_file: raw/Chương 127.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 7: Paragraph: Hàn Phong thản nhiên nhìn Quan Bình, người kia không khỏi cười khổ, sau đó trả lời thay: Section order 9: Paragraph: Hắn kể ra chi tiết tất cả sự việc từ khi hắn bại trận tại cầu Lệ Giang bỏ chạy cho tới tiếp xúc trấn Hi Vọng, nghe tin chính phủ ở đây bị thổ phỉ giết hại, sau đó Hàn Phong đứng ra tiêu diệt thổ phỉ, giải phóng cứ điểm này. Section order 12: Paragraph: Quan Bình là nhân viên chính phủ, lời của hắn là có trọng lượng nhất, đáng tin tưởng nhất, mang tín...

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
- Phong
- Hi
- Quan

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
- explain Chương 127
- summarize Chương 127
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 127.docx Chapter title: Chương 127: Nói dối không chớp mắt Section count: 86 Section order 1: Heading: Chương 127: Nói dối không chớp mắt Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Lý Võ Lạc bờ môi mấp máy mấy lần cũng không thể thốt ra câu nào. Lý do này của Hàn Phong, ai có thể phản bác đây, ai có thể trách cứ đây. Section order 4: Paragraph: Một vị thủ lĩnh liều mạng cướp đoạt vũ khí để bảo vệ hàng trăm người khỏi nguy hiểm, để bảo vệ đồng đội bên cạnh khỏi ch.ết chóc. Đây là việc làm của anh hùng, nào phải việc mà một thổ phỉ có thể làm. Section order 5: Paragraph: Một quân nhân sau lưng hắn trầm mặc một lát rồi hỏi: Section order 6: Paragraph: - Vậy tại sao anh không tham gia chính phủ hoặc quân đội mà lại chiếm núi làm vua? Tôi chưa nghe danh từ trấn Hi Vọng bao giờ. Section order 7: Paragraph: Hàn Phong thản nhiên nhìn Quan Bình, người kia không khỏi cười khổ, sau đó trả lời thay: Section order 8: Paragraph: - Tôi là nhân viên chính phủ, nhưng cũng được Hàn Phong cứu mạng… Section order 9: Paragraph: Hắn kể ra chi tiết tất cả sự việc từ khi hắn bại trận tại cầu Lệ Giang bỏ chạy cho tới tiếp xúc trấn Hi Vọng, nghe tin chính phủ ở đây bị thổ phỉ giết hại, sau đó Hàn Phong đứng ra tiêu diệt thổ phỉ, giải phóng cứ điểm này. Section order 10: Paragraph: Hắn do dự một chút vẫn là nhất nhất kể ra những thành tựu của Hàn Phong khi điều hành trấn Hi Vọng, bao gồm cả việc chăm chỉ tổ chức tấn công thây ma, chế độ đãi ngộ, sắp xếp công việc, quản lý trật tự trị an, thu thập vật tư, giải cứu người sống sót, xây thành luỹ chặn thây m...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 127.docx; chapter_title=Chương 127: Nói dối không chớp mắt; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=85 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
