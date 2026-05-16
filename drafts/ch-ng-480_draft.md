# Draft Knowledge: Chương 480

- source_id: ingest-6f6f6751c02724a5
- raw_file: raw/Chương 480.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 6: Paragraph: 27 người trải dài trong 9 tiểu đội, 3 phòng ban, trong đó đội viên thuộc tiểu đội của Kha Thành là chiếm số lượng đông đảo nhất với 5 người, chắc chắn là bọn này có lên kế hoạch tỉ mỉ với nhau thông qua Kha Mã, bằng không thì không thể có chuyện có số lượng đông đảo tập trung một chỗ như vậy được. Section order 23: Paragraph: Sau khi đạt thành 2 khoá an toàn tại hai hướng Xuân Lê và Thiết Thạch, mức độ uy hϊế͙p͙ đối với thây ma tạm thời được hạ giảm, Hàn Phong đã q...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- danh
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Haha
- Kha

### Modules
- none

### Errors
- 480
- 480: Ch
- 500 tr

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
- explain Chương 480
- summarize Chương 480
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 480.docx Chapter title: Chương 480: Chính danh Section count: 88 Section order 1: Heading: Chương 480: Chính danh Section order 2: Paragraph: 12–15 minutes Section order 3: Paragraph: Hàn Phong tuyên bố hình phạt đối với nhóm đội viên có hành vi tham ô tham nhũng xong, các tiểu đội trưởng tiếp tục nhận được danh sách đội viên vi phạm, đồng thời là bằng chứng xác thực đính kèm. Section order 4: Paragraph: Không công khai và tuyên truyền đối với toàn dân, nhưng người đứng đầu tất nhiên phải biết. Section order 5: Paragraph: Haha, biết để mà còn nộp phạt chứ. Section order 6: Paragraph: 27 người trải dài trong 9 tiểu đội, 3 phòng ban, trong đó đội viên thuộc tiểu đội của Kha Thành là chiếm số lượng đông đảo nhất với 5 người, chắc chắn là bọn này có lên kế hoạch tỉ mỉ với nhau thông qua Kha Mã, bằng không thì không thể có chuyện có số lượng đông đảo tập trung một chỗ như vậy được. Section order 7: Paragraph: Kha Thành nhìn danh sách trên tay mà trong lòng trầm xuống, thật sự là đủ mất mặt. Section order 8: Paragraph: Chưa nói tới tiền phạt liên đới mà hắn phải gánh chịu đối với vi phạm của cả 5 người này là 1200 chiến công, bằng nửa già gia sản của hắn, chỉ riêng việc vừa mới tấn thăng đại đội trưởng đã dính phải "phốt" này, uy tín của hắn đã xem như bị hạ giảm tới 18 tầng cấp bậc rồi. Section order 9: Paragraph: "Kha Mã..." Section order 10: Paragraph: Chưa bao giờ Kha Thành "hận" em trai mình tới vậy, hắn hiện tại có chút xúc động muốn phế luôn cái chức "phó tiểu đội trưởng" hão của thằng ranh kia. Section order 11: Paragraph: Các tiểu đội trưởng khác cũng...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 480.docx; chapter_title=Chương 480: Chính danh; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=87 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
