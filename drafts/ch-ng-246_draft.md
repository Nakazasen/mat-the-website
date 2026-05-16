# Draft Knowledge: Chương 246

- source_id: ingest-24e6d0379636fee0
- raw_file: raw/Chương 246.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Sau khi buông ra lời nói chứa đầy sự thương tổn và tuyệt tình kia, xuyên qua hình ảnh phản chiếu từ chiếc gương trên tường, Hàn Phong có thể nhìn thấy được sự run rẩy cùng thê lương thoáng xuất hiện trong đôi mắt Tường Vi. Bất quá hắn vẫn như cũ tiếp tục lạnh nhạt nói: Section order 5: Paragraph: - Tôi cần sự trợ giúp của cô tại chiến trường thôn Xuân Lê, ít nhất là tìm cho ra vị trí của đầu lĩnh thi đàn. Bởi vậy sau bữa sáng, hãy chuẩn bị quân tư trang sẵn sàng lê...

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
- Sau
- Phong
- Vi

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
- explain Chương 246
- summarize Chương 246
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 246.docx Chapter title: Chương 246: Thẳng hướng Xuân Lê Section count: 59 Section order 1: Heading: Chương 246: Thẳng hướng Xuân Lê Section order 2: Paragraph: 9–11 minutes Section order 3: Paragraph: Sau khi buông ra lời nói chứa đầy sự thương tổn và tuyệt tình kia, xuyên qua hình ảnh phản chiếu từ chiếc gương trên tường, Hàn Phong có thể nhìn thấy được sự run rẩy cùng thê lương thoáng xuất hiện trong đôi mắt Tường Vi. Bất quá hắn vẫn như cũ tiếp tục lạnh nhạt nói: Section order 4: Paragraph: - Trang bị tứ giai Áo Khoác Phòng Hộ có thể tuỳ biến thành mọi hình dạng kích thước, tôi đã để sẵn nó trên bàn rồi, cô có thể sử dụng mà không cần lo lắng vấn đề y phục bị xé rách, chỉ cần động niệm hình ảnh trong đầu là được. Section order 5: Paragraph: - Tôi cần sự trợ giúp của cô tại chiến trường thôn Xuân Lê, ít nhất là tìm cho ra vị trí của đầu lĩnh thi đàn. Bởi vậy sau bữa sáng, hãy chuẩn bị quân tư trang sẵn sàng lên đường. Không lâu đâu, có lẽ chỉ cần buổi sáng thôi, trước khi đội ngũ huyện Tam Giang tới, tôi sẽ tự mình đưa cô trở về trấn Hi Vọng. Section order 6: Paragraph: Tường Vi cắn chặt đôi môi đỏ mọng, trong lòng nàng còn có một vạn lời muốn nói ra, thế nhưng tất cả đều đã nghẹn ứ ở cổ. Section order 7: Paragraph: - Tôi… Tôi biết rồi… Section order 8: Paragraph: Nàng nói xong liền nhanh chóng hoàn thành vệ sinh cá nhân sau đó cất bước ra ngoài. Section order 9: Paragraph: Hàn Phong nheo mắt nhìn đối phương mấy giây. Hắn thong thả từ trong bồn tắm đứng lên, xả ra vòi hoa sen nước lạnh, sau đó vừa đánh răng vừa tuỳ tiện tắm qua một lượt, muốn đem hết t...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 246.docx; chapter_title=Chương 246: Thẳng hướng Xuân Lê; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=58 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
