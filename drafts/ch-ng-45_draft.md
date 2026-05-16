# Draft Knowledge: Chương 45

- source_id: ingest-0b3ffeb8580d1910
- raw_file: raw/Chương 45.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 45: Doạ tè ra quần Section order 6: Paragraph: Tường Vi cũng không có trao súng cho hai người Lý Hạ Vân, Cao Trác. Bản thân nàng giữ khẩu M17, về phần D.E, nàng đưa cho nữ tử còn lại trong 4 người, Trần Diệu Âm. Section order 7: Paragraph: Hai người Lý Hạ Vân, Cao Trác nuốt khan nước bọt. Bọn hắn tham gia câu lạc bộ này, tất nhiên đều biết bắn súng, càng biết rằng súng ống là thực lực. Nhưng vừa rồi thương lượng với Hàn Phong, bọn...

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
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Phong

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
- explain Chương 45
- summarize Chương 45
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 45.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 45: Doạ tè ra quần Section count: 75 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 45: Doạ tè ra quần Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Tiếp sau đó là công cuộc di dời vũ khí ra khỏi hầm. Đối với việc này, Ngô Soái gần như là sướng tới phát cuồng, bỏ ra 200% sức lực đem tất cả súng ống nhanh chóng vác ra bên ngoài. Section order 4: Paragraph: Hàn Phong nhìn số vũ khí được bê lên trên, cả người không khỏi thở dài một hơi. Section order 5: Paragraph: Hắn dựa theo ước định, trao cho Tường Vi một khẩu súng lục M17, một khẩu D.E và tổng cộng 40 viên đạn. Section order 6: Paragraph: Tường Vi cũng không có trao súng cho hai người Lý Hạ Vân, Cao Trác. Bản thân nàng giữ khẩu M17, về phần D.E, nàng đưa cho nữ tử còn lại trong 4 người, Trần Diệu Âm. Section order 7: Paragraph: Hai người Lý Hạ Vân, Cao Trác nuốt khan nước bọt. Bọn hắn tham gia câu lạc bộ này, tất nhiên đều biết bắn súng, càng biết rằng súng ống là thực lực. Nhưng vừa rồi thương lượng với Hàn Phong, bọn họ không có đạt được một khẩu nào. Section order 8: Paragraph: Cao Trác âm thầm nghiến răng nói: Section order 9: Paragraph: - Hạ Vân, cậu không thấy cái tên Hàn Phong kia rất quá đáng sao? Hắn thậm chí không thèm nghe chúng ta thuyết phục? Lý Hạ Vân cũng đành bất lực, hắn trầm mặc hồi lâu, nhàn nhạt nói: Section order 10: Paragraph: - Chúng ta hiện tại cần nhất là sống sót, sau đó liên lạc với chính phủ, liên lạc với các mối quan hệ của mình. Cao Trác, cậu nghĩ lung tung thì được, nhưng chớ c...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 45.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 45: Doạ tè ra quần; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=74 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
