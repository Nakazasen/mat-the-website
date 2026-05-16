# Draft Knowledge: Chương 419

- source_id: ingest-1e6a79a0a6a34b0f
- raw_file: raw/Chương 419.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Lệnh triệu tập do chính phủ căn cứ Tam Giang phát ra không phải là chưa có tiền lệ, trước đó căn cứ Tam Giang đã từng "mời" các phi phàm giả Liễu Lâm qua bên kia để tiếp nhận "đào tạo tư tưởng", nhưng không nêu trừng phạt đính kèm. Section order 4: Paragraph: Khi đó Hàn Phong đã ra lệnh cho Liễu Huyên tuyên truyền kiểu bóp méo và bôi đen công văn chỉ đạo đó, biến thành bắt buộc triệu tập, ai không tuân thủ thì sau này sẽ phải chịu đựng hình phạt thích đáng. Ân, tất...

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
- Section
- Heading
- Paragraph
- Tam Giang
- Khi
- Phong

### Modules
- none

### Errors
- 419
- 419: Quy

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
- explain Chương 419
- summarize Chương 419
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 419.docx Chapter title: Chương 419: Quyết chiến Section count: 79 Section order 1: Heading: Chương 419: Quyết chiến Section order 2: Paragraph: 11–14 minutes Section order 3: Paragraph: Lệnh triệu tập do chính phủ căn cứ Tam Giang phát ra không phải là chưa có tiền lệ, trước đó căn cứ Tam Giang đã từng "mời" các phi phàm giả Liễu Lâm qua bên kia để tiếp nhận "đào tạo tư tưởng", nhưng không nêu trừng phạt đính kèm. Section order 4: Paragraph: Khi đó Hàn Phong đã ra lệnh cho Liễu Huyên tuyên truyền kiểu bóp méo và bôi đen công văn chỉ đạo đó, biến thành bắt buộc triệu tập, ai không tuân thủ thì sau này sẽ phải chịu đựng hình phạt thích đáng. Ân, tất nhiên là nó cũng gây ra phẫn nộ nhất định, nhưng vì không có hình phạt, sự việc kia dần lắng xuống. Section order 5: Paragraph: Lệnh triệu tập lần này sử dụng ngữ điệu khắc nghiệt và thúc ép sát sao về mặt thời gian, thậm chí đã nêu rõ trừng phạt đính kèm, điều này đã triệt để chọc giận tất cả mọi người. Tất cả ức chế kìm nén trong quá khứ đã hoàn toàn bộc phát ra ngoài, thái độ tiêu cực xuất hiện tràn lan trong phòng họp. Section order 6: Paragraph: - Chó ch.ết. Chính lũ khốn này mới là bọn làm ra hành động khủng bố nhằm vào dân thường, hiện tại nhận được bằng chứng thì liền đổ tội qua cho chúng ta. Section order 7: Paragraph: - Mặt dày vô sỉ, không biết xấu hổ, bọn này có tư cách gì mà triệu tập, lý do bịa ra mà cũng viết bừa thành công văn chỉ đạo được. Section order 8: Paragraph: - Dơ bẩn, thái độ trịch thượng không chịu nổi, chúng ta gửi công hàm phản đối bọn họ tiếp tục can thiệp nội bộ, bọn họ liền bắt c...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 419.docx; chapter_title=Chương 419: Quyết chiến; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=78 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
