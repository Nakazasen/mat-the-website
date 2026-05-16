# Draft Knowledge: Chương 330

- source_id: ingest-f3b0fe2cec7bd421
- raw_file: raw/Chương 330.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 8: Paragraph: Suy nghĩ vừa rồi chỉ khẽ lướt qua, âm thanh từ bộ đàm vẫn tiếp tục vang vọng. Lượng thông tin trong này không phải rất nhiều, chủ yếu là thông báo về tình trạng của những người đã chuyển qua Tam Giang, có ai gặp khó khăn, có ai đang nỗ lực vươn lên, có ai được trọng dụng, có ai từ bỏ việc chiến đấu, cũng thông báo việc người nọ đã thành công tấn thăng tiểu đội trưởng bên đó, cùng với việc cảm tạ Hàn Phong đã tin tưởng. Section order 10: Paragraph: Thông tin quan tr...

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
- Suy
- Tam Giang

### Modules
- none

### Errors
- 5000 exp r
- 5732/10

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
- explain Chương 330
- summarize Chương 330
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 330.docx Chapter title: Chương 330 Section count: 60 Section order 1: Heading: Chương 330 Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Thời điểm ghi chép bảng nguyện vọng lúc trước, Hàn Phong đã thu được ba lá phiếu đặc biệt. Một lá phiếu đánh dấu cả hai ô rời đi và ở lại, một lá phiếu có một tích lớn tại ô rời đi, hai tích nhỏ tại ô ở lại, lá phiếu cuối cùng thì có ghi chú “Tôi rất muốn ở lại”. Section order 4: Paragraph: Hắn đã thử đặt cược vào may mắn, chọn một trong ba lá phiếu này để trao bộ đàm nhằm giữ liên lạc, hiện tại rốt cuộc đã có kết quả. Section order 5: Paragraph: Người tiếp nhận cái danh “gián điệp” này có lẽ không phải người trung thành nhất, càng không phải người mà hắn có thể nắm thóp. Sự lựa chọn của hắn ngoài việc đến từ mối quan hệ tương đối tốt đẹp với đối phương thì còn nằm ở chỗ đối phương đủ tiềm lực để vươn lên. Section order 6: Paragraph: Hàn Phong sẽ không chọn người có vị trí quan trọng như vậy dựa theo cảm tính, hắn lựa chọn theo lợi ích tối đa. Một là có tất cả, hai là không gì cả, thà rằng đặt cược vào việc có một gián điệp đủ năng lực còn hơn lựa chọn một người đủ trung thành nhưng không gian phát triển hạn chế. Section order 7: Paragraph: Mối quan hệ xây dựng dựa trên sự tin tưởng lỏng lẻo không có ràng buộc này, có đôi khi còn hiệu quả và vững chắc hơn cả mong đợi. Đối phương đang làm việc dựa trên tâm lý tình nguyện trả ơn, vậy thì tỉ lệ bị cắn ngược của hắn là rất thấp, đồng thời áp lực tâm lý “phản bội chính phủ” mà đối phương đang phải gánh chịu cũng sẽ không quá bị đè nén. Section order 8:...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 330.docx; chapter_title=Chương 330; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=59 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
