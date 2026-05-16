# Draft Knowledge: Chương 122

- source_id: ingest-b7bae53955d83760
- raw_file: raw/Chương 122.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: 17 người này gồm Hàn Phong, Ngô Soái, Châu Lam, Đào Đại Tư, ba đội viên cấp 5, ba đội viên cấp 6, bốn đội viên khoẻ mạnh thuộc tiểu đội hậu cần, một bác sĩ. Section order 4: Paragraph: Cuối cùng là người quan trọng nhất, Tường Vi. Ngoài ra, nhân viên chính phủ huyện Tam Giang, người phi phàm cấp 5 Quan Bình cũng đột nhiên được chiêu mộ vào đội ngũ. Section order 5: Paragraph: Đoàn xe băng băng tiến về phía trước. Dẫn đầu là chiếc xe bọc thép cùng một khẩu súng đại...

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
- Phong Section
- Section
- Heading
- Paragraph
- Phong
- Lam

### Modules
- none

### Errors
- 500 m

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
- explain Chương 122
- summarize Chương 122
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 122.docx Chapter title: Chương 122: Thực lực của Hàn Phong Section count: 88 Section order 1: Heading: Chương 122: Thực lực của Hàn Phong Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: 17 người này gồm Hàn Phong, Ngô Soái, Châu Lam, Đào Đại Tư, ba đội viên cấp 5, ba đội viên cấp 6, bốn đội viên khoẻ mạnh thuộc tiểu đội hậu cần, một bác sĩ. Section order 4: Paragraph: Cuối cùng là người quan trọng nhất, Tường Vi. Ngoài ra, nhân viên chính phủ huyện Tam Giang, người phi phàm cấp 5 Quan Bình cũng đột nhiên được chiêu mộ vào đội ngũ. Section order 5: Paragraph: Đoàn xe băng băng tiến về phía trước. Dẫn đầu là chiếc xe bọc thép cùng một khẩu súng đại liên 12ly7 luôn luôn sẵn sàng xả đạn, phía sau gồm 2 xe jeep chở quân, 2 xe tải cỡ lớn nhằm chở súng đạn, cuối cùng là một chiếc xe bán tải Ford Raptor đi đoạn hậu. Section order 6: Paragraph: Ngô Soái chính là làm nhiệm vụ chặn đoạn hậu, Hàn Phong và Tường Vi thì ngồi trên xe bọc thép làm nhiệm vụ dẫn đường. Section order 7: Paragraph: Bởi vì nguyên nhân phi lễ tối qua, ngày hôm nay cả Tường Vi lẫn Hàn Phong đều chưa nói với nhau nửa lời. Hàn Phong đối với việc này thì rất vui mừng, hắn ngồi ở ghế phụ hai chân gác lên đầu xe, còn thật thảnh thơi từ balo lấy ra một bản sách kỹ năng đã lâu chưa đụng đến. Section order 8: Paragraph: Kỹ năng nhị giai, thiết huyết ca. Section order 9: Paragraph: Đây là một cái kỹ năng dạng buff quần thể cực kỳ lợi hại. Từ khi đánh quái rớt được cái kỹ năng này, hắn vẫn luôn truy tìm người phù hợp để sử dụng, thế nhưng đến giờ vẫn chưa tìm được. Section order 10...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 122.docx; chapter_title=Chương 122: Thực lực của Hàn Phong; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=87 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
