# Draft Knowledge: Chương 233

- source_id: ingest-c5f148ccc5598659
- raw_file: raw/Chương 233.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Ý định ban đầu của Đổng Thành là muốn “mượn” tới cả xe bọc thép để áp trận, nhưng xe bọc thép là đại sát khí, sao có thể dễ dàng mượn. Hà Tam hiến kế cho hắn, nói thôn Xuân Lê thay vì mượn xe bọc thép thì mượn binh, để cho Hàn Phong cử binh tới hỗ trợ, hắn ta vì lo an toàn cho thuộc hạ thì tất nhiên cũng sẽ phải điều động bọc thép đảm bảo. Từ đó bọn họ sẽ thiết lập chiến đấu xoay quanh chiếc bọc thép này, kiểu gì cũng sẽ dễ dàng lợi dụng uy năng của nó. Section ord...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- giang

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Phong Section
- Section
- Heading
- Paragraph
- Tam
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
- explain Chương 233
- summarize Chương 233
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 233.docx Chapter title: Chương 233: Món quà Thiện Duyên của Hàn Phong Section count: 67 Section order 1: Heading: Chương 233: Món quà Thiện Duyên của Hàn Phong Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Ý định ban đầu của Đổng Thành là muốn “mượn” tới cả xe bọc thép để áp trận, nhưng xe bọc thép là đại sát khí, sao có thể dễ dàng mượn. Hà Tam hiến kế cho hắn, nói thôn Xuân Lê thay vì mượn xe bọc thép thì mượn binh, để cho Hàn Phong cử binh tới hỗ trợ, hắn ta vì lo an toàn cho thuộc hạ thì tất nhiên cũng sẽ phải điều động bọc thép đảm bảo. Từ đó bọn họ sẽ thiết lập chiến đấu xoay quanh chiếc bọc thép này, kiểu gì cũng sẽ dễ dàng lợi dụng uy năng của nó. Section order 4: Paragraph: Đổng Thành nghe có lý, đồng ý không chút do dự. Section order 5: Paragraph: Tất nhiên ý kiến của Hà Tam tràn đầy tính nguy cơ, chẳng khác nào việc dẫn sói vào nhà, hay chặn hổ cửa trước rước beo cửa sau. Nhưng nếu hắn không “hiến kế”, không dẫn dắt theo chiều hướng dễ hành động hơn, hắn sẽ phải mượn bằng được xe bọc thép, đây là nhiệm vụ bất khả thi. Section order 6: Paragraph: Hiện tại Hàn Phong chủ động đề xuất, hắn cầu còn không được nữa là, bởi vậy lại tiếp tục nói: Section order 7: Paragraph: - Hàn thủ lĩnh, không biết khi nào có thể xuất quân hỗ trợ? Tình hình chiến đấu thực sự đang rất nguy cấp… Section order 8: Paragraph: Hàn Phong thản nhiên nói: Section order 9: Paragraph: - Chúng tôi hiện tại chưa tiện xuất quân, ngày mai sẽ tiến hành hỗ trợ các vị. Section order 10: Paragraph: Hà Tam nghe vậy không khỏi trong lòng nặng nề, hắn do dự một chú...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 233.docx; chapter_title=Chương 233: Món quà Thiện Duyên của Hàn Phong; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=66 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
