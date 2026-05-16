# Draft Knowledge: Chương 186

- source_id: ingest-1a90350064d069e8
- raw_file: raw/Chương 186.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 10: Paragraph: - Bao nhiêu người sẽ bảo vệ tôi? Hàn Phong liếc nhìn một vòng chiến trường rồi khẳng định nói: Section order 14: Paragraph: - Anh mà lại cho nhiều người bảo vệ tôi như vậy, khẳng định hành động lần này rất nguy hiểm. Chi bằng điều thêm vài khẩu đại liên với hai khẩu súng chống tăng tới yểm trợ được không? Section order 16: Paragraph: Hàn Phong nghiến răng nghiến lợi nhìn nàng ta không đáp, một lúc sau, hắn quay qua nói với Kha Thành:

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- level
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Vi
- Phong
- Bao

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
- explain Chương 186
- summarize Chương 186
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 186.docx Chapter title: Chương 186: Bản năng. Section count: 78 Section order 1: Heading: Chương 186: Bản năng. Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Rất nhanh Tường Vi đã được mời tới, cô ả này trải qua rất nhiều lần tập kích của kẻ sau màn, thế nhưng vẫn như cũ không có một điểm nhiệt huyết hay tinh nhuệ. Vừa mới xuất hiện, chưa cần Hàn Phong mở lời trước, nàng ta đã lập tức đưa ra yêu cầu: Section order 4: Paragraph: - Tôi muốn tăng số người bảo vệ bản thân lên. Section order 5: Paragraph: Hàn Phong khoé miệng co giật, thật có xúc động tóm cổ nàng ta ném vào giữa thi đàn. Section order 6: Paragraph: Nếu đội viên dưới trướng người nào cũng nhát ch.ết như nàng ta, vậy hắn sẽ giết sạch tất cả rồi bỏ chạy, khỏi có nhiệm vụ hệ thống cái gì nữa. Section order 7: Paragraph: Hắn cuối cùng vẫn là gắng gượng nhịn lại, lấy ra 5 viên đạn diệt quỷ đưa cho nàng ta rồi nhàn nhạt nói: Section order 8: Paragraph: - Tiếp theo quả thật sẽ phái người bảo vệ cô. Có điều, cô phải đảm bảo trong 30 giây bắn hết 5 viên đạn vào mục tiêu chỉ định. Section order 9: Paragraph: Tường Vi suy nghĩ một chút rồi dò hỏi: Section order 10: Paragraph: - Bao nhiêu người sẽ bảo vệ tôi? Hàn Phong liếc nhìn một vòng chiến trường rồi khẳng định nói: Section order 11: Paragraph: - Tất cả bọn họ. Section order 12: Paragraph: - …?! Section order 13: Paragraph: Tường Vi còn tưởng mình nghe lầm, thế nhưng sau khi nhìn thấy ánh mắt tương đối chân thật của Hàn Phong, nàng ta vẫn là chậm rãi nói: Section order 14: Paragraph: - Anh mà lại cho nhiều người bảo vệ tôi như v...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 186.docx; chapter_title=Chương 186: Bản năng.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=77 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
