# Draft Knowledge: Chương 123

- source_id: ingest-4f0cda09fc98f00d
- raw_file: raw/Chương 123.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 40: Paragraph: Sau đó hắn lại nói với Tường Vi và Quan Bình: Section order 50: Paragraph: Sau khi bàn bạc sơ lược kế hoạch, Hàn Phong cùng Ngô Soái, Châu Lam, Đào Đại Tư trước tiên xâm nhập dò xét, những người khác ở lại bên ngoài canh chừng. Section order 56: Paragraph: Trung tâm khu huấn luyện có một tổ hợp kiến trúc lớn cao 4 tầng giống như ký túc xá, Hàn Phong vừa nhìn tới sân rộng trong kiến trúc, hai mắt chợt toả sáng.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- trung

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Vi
- Phong
- Sau

### Modules
- none

### Errors
- 500 m
- 531

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
- explain Chương 123
- summarize Chương 123
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 123.docx Chapter title: Chương 123: Chó biến dị Section count: 103 Section order 1: Heading: Chương 123: Chó biến dị Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Nơi bọn họ đang dừng lại là một cái ngã ba đường, Tường Vi cẩn thận phân biệt khung cảnh tan hoang, sau đó chỉ tay về bên trái nói: Section order 4: Paragraph: - Đường đó, đi tiếp 1 cây số nữa lại nói. Section order 5: Paragraph: Lái xe lập tức dựa theo lời nàng ta chạy tới, Hàn Phong cẩn thận quan sát xung quanh, lông mày không khỏi nhíu chặt. Section order 6: Paragraph: Thây ma đâu? Section order 7: Paragraph: Tại sao nơi này không có thây ma? Thậm chí xác ch.ết thây ma cũng chỉ rải rác. Đây là trạng huống quỷ dị gì? Section order 8: Paragraph: “ch.ết tiệt! Cứ mỗi lần gặp quỷ dị là một lần đau đầu…” Section order 9: Paragraph: Hàn Phong không khỏi cắn răng mắng thầm, hắn đang nghĩ tới trạng huống quỷ dị tại trung tâm huyện Liễu Lâm. Section order 10: Paragraph: Bởi vì không có thây ma, đoạn đường 1 cây số rất dễ dàng vượt qua. Cộng thêm việc nơi này đã cách rất xa trung tâm, tiến về phía mấy nhà xưởng, thế nên đường thông hè thoáng, bọn họ còn không cần nhảy xuống dọn dẹp kẹt xe. Section order 11: Paragraph: Sau khi đi hết 1 cây số, Tường Vi mới chỉ vào con đường mòn bên cạnh một cổ thụ rồi nói: Section order 12: Paragraph: - Đi thẳng đường này một cây số nữa sẽ tới một trại huấn luyện chó nghiệp vụ, đó chính là mục tiêu của chúng ta. Section order 13: Paragraph: Hàn Phong vừa đề cao cảnh giác xung quanh, vừa trầm giọng ra lệnh cho lái xe: Section order 14: Paragraph:...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 123.docx; chapter_title=Chương 123: Chó biến dị; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=102 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
