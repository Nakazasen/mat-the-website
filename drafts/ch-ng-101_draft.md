# Draft Knowledge: Chương 101

- source_id: ingest-478d0ac19dfbc5bd
- raw_file: raw/Chương 101.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 101: Việc làm dơ bẩn. Section order 6: Paragraph: Hàn Phong nói với Xuân Hoa Xuân Thu: Section order 12: Paragraph: - Nga, cái giọng điệu thật sự là dịu dàng. Ai dạy anh vậy? Hàn Phong khoé miệng co giật, thiếu chút đã chửi ra thành tiếng.

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
- Hai

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
- explain Chương 101
- summarize Chương 101
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 101.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 101: Việc làm dơ bẩn. Section count: 121 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 101: Việc làm dơ bẩn. Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hai huynh đệ bàn bạc tác chiến thêm một lúc lâu mới chia tay. Section order 4: Paragraph: Hàn Phong xoay người quay về phòng, ngoài cửa đã sớm có một người đang chờ đợi từ trước. Section order 5: Paragraph: Không phải Liễu Huyên thì còn ai. Section order 6: Paragraph: Hàn Phong nói với Xuân Hoa Xuân Thu: Section order 7: Paragraph: - Chuẩn bị hai bình trà. Section order 8: Paragraph: - Dạ… Section order 9: Paragraph: Chờ hai nữ hầu rời đi, Hàn Phong mời mở cửa phòng chìa tay thân sĩ nói: Section order 10: Paragraph: - Liễu tiểu thư, mời vào. Section order 11: Paragraph: Liễu Huyên liếc xéo Hàn Phong, cười trêu tức: Section order 12: Paragraph: - Nga, cái giọng điệu thật sự là dịu dàng. Ai dạy anh vậy? Hàn Phong khoé miệng co giật, thiếu chút đã chửi ra thành tiếng. Section order 13: Paragraph: Trấn Hi Vọng có hai người cực kỳ khó đối phó, cả hai đều là nữ nhân, mà Liễu Huyên chính là một trong số đó. Section order 14: Paragraph: Hắn nặn ra một vẻ mặt méo mó nói: Section order 15: Paragraph: - ɖâʍ phụ, cút vào trong đi. Section order 16: Paragraph: Hàn Phong vừa nói xong đã bị đối phương tung một cước đá trúng ống đồng, để cho hắn đau tới chảy cả nước mắt. Section order 17: Paragraph: - Hừ, đồ tr.a nam. Lần sau anh còn dám dùng giọng điệu đó với tôi, tôi sẽ sút vào chỗ khác. Section order 18: Paragraph: L...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 101.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 101: Việc làm dơ bẩn.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=120 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
