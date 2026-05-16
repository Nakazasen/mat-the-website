# Draft Knowledge: Chương 128

- source_id: ingest-ed75baa98846564b
- raw_file: raw/Chương 128.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 13: Paragraph: Haha, nếu ngay ngày đầu tiên Hàn Phong vớ được kỹ năng tam giai này, hắn hẳn sẽ ch.ết chắc. Khi đó là buổi chiều, hắn chưa có cơ hội tắm trăng mà triệu hồi bản thân đâu. Section order 16: Paragraph: Đám kỹ năng nhị giai còn lại cũng đều là do hai người Hàn Phong, Ngô Soái đánh rớt cả, những người khác hầu hết là râu ria hô hào phụ hoạ. Hàn Phong thò tay bốc lên một bản kỹ năng chủ động nhị giai từ con chó biến dị level 15. Section order 18: Paragraph: Sau khi kỹ n...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- giai

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Sau
- Khi
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
- explain Chương 128
- summarize Chương 128
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 128.docx Chapter title: Chương 128: Được cả người cả vật. Section count: 75 Section order 1: Heading: Chương 128: Được cả người cả vật. Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Ảnh Chiếu Ánh Trăng này tương đối đặc biệt, đây là một kỹ năng cần điều kiện mới có thể kích hoạt. Section order 4: Paragraph: Sau khi học tập kỹ năng, mỗi tối người sở hữu đều phải tắm trong ánh trăng để “sạc” lại thời gian hồi cho kỹ năng. Tắm trong ánh trăng bao lâu, thời gian duy trì của ảnh chiếu sẽ kéo dài được một phần mười khoảng thời gian đó. Section order 5: Paragraph: Ví dụ tắm ánh trăng được 1 tiếng, vậy thì thời gian ảnh chiếu tồn tại kéo dài được sáu phút. Section order 6: Paragraph: Khi có thời gian tích luỹ, người nắm giữ có thể triệu hồi một ảnh chiếu của bản thân ngay tại thời điểm tắm trăng đó. Chỉ số ảnh chiếu ngang bằng chỉ số cơ bản khi không đeo trang bị, không trong trạng thái bộc phá, không nhận buff hay debuff từ các nguồn khác. Section order 7: Paragraph: Ảnh chiếu có thể sử dụng 1 kỹ năng dưới tam giai, khi sử dụng kỹ năng, thời gian tồn tại sẽ bị giảm đi 10 lần. Tức là ảnh chiếu tồn tại 6 phút, nếu sử dụng kỹ năng phá tâm linh, hoặc sử dụng xuyên thấu, nó sẽ chỉ duy trì được 36 giây. Tất nhiên nếu không sử dụng kỹ năng, chỉ đấm tay bo, thời gian duy trì sẽ không bị hao hụt. Section order 8: Paragraph: Điểm làm Hàn Phong quyết tâm lựa chọn chính là ảnh chiếu có tư duy độc lập, còn có thể tâm ý tương thông với chính chủ, cái này thực sự là quá lỗi đi. Tất nhiên khi sử dụng tâm ý tương thông được tính là kích hoạt kỹ năng, thờ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 128.docx; chapter_title=Chương 128: Được cả người cả vật.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=74 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
