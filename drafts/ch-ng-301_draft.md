# Draft Knowledge: Chương 301

- source_id: ingest-7282665da548804d
- raw_file: raw/Chương 301.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 18: Paragraph: - Phi… Phi phàm giả! Section order 26: Paragraph: Tại huyện Tam Giang, phi phàm giả là những người đứng trên đỉnh kim tự tháp. Phi phàm giả sở hữu các kỹ năng thao túng nguyên tố, các kỹ năng công kích tầm xa càng là tinh anh, kia biểu hiện cho việc họ có thể đóng góp rất lớn cho đội ngũ. Section order 27: Paragraph: Mà thủ hộ giả là những người sở hữu kỹ năng quang giáp, hoặc kỹ năng thao túng đại địa, kỹ năng dạng phòng ngự nói chung, đây càng là tinh anh trong...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- ngay

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Nam
- Vi
- Xin

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
- explain Chương 301
- summarize Chương 301
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 301.docx Chapter title: Chương 301: Rất nhanh thôi Section count: 65 Section order 1: Heading: Chương 301: Rất nhanh thôi Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: - Còn chần chờ cái gì, cởi hết quần áo ra cho chúng tôi kiểm tr.a ngay. Cô muốn chống người thi hành công vụ, chống lại pháp luật sao? Section order 4: Paragraph: Nam nhân viên béo mập ánh mắt hau háu vừa quát lạnh vừa nhìn chằm chằm vào thân thể Tường Vi, tưởng như chắc chắn một giây sau đây cái nữ nhân xinh đẹp này sẽ phải khuất phục trước ɖâʍ uy của gã. Mà nhân viên công tác mặc đồng phục cảnh sát bên cạnh cũng là treo biểu cảm tương tự, thậm chí bàn tay sớm đã chạm tới thắt lưng tại đai quần, sẵn sàng làm cái việc mà ai cũng biết là gì. Section order 5: Paragraph: Tường Vi khuôn mặt dần dần xuất hiện vẻ lạnh lùng, nàng nheo mắt nhìn nhân viên béo mập, lại nhìn qua gã cảnh sát đứng bên cạnh, sau đó mới thong thả cất lời: Section order 6: Paragraph: - Lệnh khám người này do ai ban bố, tại sao tôi không thấy trên bảng quy tắc, tại sao không có nữ nhân viên công tác làm nhiệm vụ khám xét cho người sống sót là nữ? Section order 7: Paragraph: Nam nhân viên béo mập thoáng khựng lại, cái này, lệnh khám người đúng là không có ghi trong quy tắc, nhưng mệnh lệnh cấp trên cũng không cấm việc khám người, đây không phải ngầm hiểu sao? Còn nữa, gã lòng mang ý đồ xấu, sao có thể gọi nữ nhân viên công tác tới chứ? Gã lúc này lập tức quát lên: Section order 8: Paragraph: - Đừng có lằng nhằng, tôi làm việc theo quy tắc, cô cảm thấy không đúng, cảm thấy muốn khiếu nại thì viết đơn m...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 301.docx; chapter_title=Chương 301: Rất nhanh thôi; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=64 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
