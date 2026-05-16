# Draft Knowledge: Chương 235

- source_id: ingest-ac5840569d8e4b85
- raw_file: raw/Chương 235.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 11: Paragraph: Hàn Phong dẫn đầu xoay người bước đi. Gã người chó do dự một chút, sau đó há cái mồm đầy răng nhọn hút mặt trăng trên cao vào bụng, thân thể dần trở về hình dạng bốn chân. Nó nhún chân một cái rồi đuổi theo sau lưng Hàn Phong, thái độ vẫn còn tương đối cảnh giác. Section order 56: Paragraph: Hàn Phong nhìn trúng con chó ngu này không chỉ bởi năng lực chiến đấu mà còn bởi tính cách khôn ngoan và ít bài xích nhân loại. Quan trọng nhất, nó chịu đàm phán, chịu trò chu...

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
- Trong
- Sao

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
- explain Chương 235
- summarize Chương 235
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 235.docx Chapter title: Chương 235: Thoả thuận Section count: 109 Section order 1: Heading: Chương 235: Thoả thuận Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Đúng là tham ăn như chó, dụ được con chó này cũng không phải quá mức khó khăn. Hàn Phong đạt được mục đích thì lập tức ra lệnh cho đội ngũ xung quanh: Section order 4: Paragraph: - Tất cả thu lại địch ý cùng vũ trang, truyền lệnh của tôi thông báo cho toàn bộ người sống sót tạm lánh vào nhà, cũng không được dâng lên địch ý với con chó này. Section order 5: Paragraph: Nhạc Sơn đội trưởng đội trị an nghe lệnh thì lập tức đáp lại: Section order 6: Paragraph: - Tuân lệnh! Section order 7: Paragraph: Hắn bắt đầu chỉ đạo đội viên tại cổng trấn tạm thu lại súng trung liên trên tháp canh, cũng cho vài đội viên chạy vào trong trấn ra hiệu di tản đám người sống sót tạm lánh vào nhà. Section order 8: Paragraph: Hàn Phong bày ra một thái độ thiện chí xoè tay cười sủa: Section order 9: Paragraph: - Gâu gâu. Section order 10: Paragraph: “Đại hắc cẩu, chúng ta đi thôi. Gâu.” Section order 11: Paragraph: Hàn Phong dẫn đầu xoay người bước đi. Gã người chó do dự một chút, sau đó há cái mồm đầy răng nhọn hút mặt trăng trên cao vào bụng, thân thể dần trở về hình dạng bốn chân. Nó nhún chân một cái rồi đuổi theo sau lưng Hàn Phong, thái độ vẫn còn tương đối cảnh giác. Section order 12: Paragraph: Liên tục duy trì hình dạng của nhân loại cũng làm nó tiêu hao không nhỏ. Section order 13: Paragraph: Trong trấn, người sống sót vẫn còn chưa có di tản toàn bộ, thậm chí bởi vì đang diễn ra việc phân...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 235.docx; chapter_title=Chương 235: Thoả thuận; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=108 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
