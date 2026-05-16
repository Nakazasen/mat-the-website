# Draft Knowledge: Chương 41

- source_id: ingest-2e7c3bc9b97b49c8
- raw_file: raw/Chương 41.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 41: Tìm kiếm súng đạn Section order 23: Paragraph: - Đồn cảnh sát Thanh Hà nằm gần siêu thị Thanh Hà, cách chúng ta khoảng 4km, về phần doanh trại quân đội, này cách đây gần mười cây số cơ. Section order 42: Paragraph: Tiêu Minh gốc rễ rất to, nhưng so với Hứa Dương cũng chỉ là một tên quan nhị đại bình thường. Hứa Dương mới thực sự là gốc rễ chắc chắn. Hứa thiếu đã tôn sùng Hàn Phong, người kia tuyệt đối không phải tầm thường.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- minh
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Sinh
- Nguy
- Section
- Heading
- Paragraph
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
- explain Chương 41
- summarize Chương 41
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 41.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 41: Tìm kiếm súng đạn Section count: 87 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 41: Tìm kiếm súng đạn Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Hàn Phong thấy mọi người đồng ý thì hài lòng gật đầu, tiếp tục nói: Section order 4: Paragraph: - Bản thân tôi trong chuyện này cũng có một phần lỗi. Là do tôi không nhanh chóng hoả giải, để mâu thuẫn tăng cao, khiến mối quan hệ đoàn đội có sự chia rẽ. Tôi sẽ tự phạt bản thân, hiến ra một sách kỹ năng bị động tăng cường thể lực. Section order 5: Paragraph: - Tài nguyên trong công quỹ phân chia dựa trên đóng góp. Người đóng góp nhiều sẽ có quyền chọn trước, người đóng góp ít hơn, vui lòng chọn sau. Section order 6: Paragraph: Mọi người trong đội nhóm nghe vậy không khỏi ngẩn ngơ, âm thầm cảm thán hp thật biết cách làm người. Section order 7: Paragraph: Nếu như vậy thì sẽ giảm bớt tranh cãi tới mức tối đa. Dù sao, nếu ngươi không phục, vậy đóng góp nhiều hơn đi, giết nhiều thây ma hơn đi. Cách này thật ra công bằng cho cả người yếu lẫn người mạnh. Người mạnh không thể độc chiếm, người yếu vẫn có cơ hội mạnh lên. Section order 8: Paragraph: Mà hp ngược lại thì cười nhạt. Hắn đây là hành động bỏ con săn sắt, bắt con cá rô mà thôi. Section order 9: Paragraph: Sau này khi đội ngũ mạnh lên, tài nguyên thu về càng nhiều, sự mạnh mẽ của hắn không còn là tính duy nhất như hiện tại nữa. Tới lúc đó thì dựa vào cống hiến, hắn vẫn có thể được quyền ưu tiên chọn lựa tài nguyên cần thiết phù hợp cho mình mà không cần lải n...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 41.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 41: Tìm kiếm súng đạn; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=86 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
