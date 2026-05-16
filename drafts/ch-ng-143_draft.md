# Draft Knowledge: Chương 143

- source_id: ingest-ef23d95fd3ed59f1
- raw_file: raw/Chương 143.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Sau khi định ra kế hoạch cơ bản, Hàn Phong mới vung tay lên nói: Section order 7: Paragraph: Theo mệnh lệnh của Hàn Phong phát ra, ánh mắt của những người trong phòng đều bốc lên hoả quang hừng hực. Section order 19: Paragraph: Ngoài thông báo bổ nhiệm hai tân tiểu đội trưởng Quan Bình, Lý Võ Lạc, thông cáo này còn có thêm việc Hàn Phong dẫn quân đi thu phục được trang bị của một tiểu đoàn, sau đó là thông báo chiến dịch tấn công về phía trung tâm huyện Liễu Lâm.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Sau
- Phong
- Ba

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
- explain Chương 143
- summarize Chương 143
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 143.docx Chapter title: Chương 143: Triển khai tấn công Section count: 95 Section order 1: Heading: Chương 143: Triển khai tấn công Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Sau khi định ra kế hoạch cơ bản, Hàn Phong mới vung tay lên nói: Section order 4: Paragraph: - Mọi người. Tận thế hàng lâm, chúng ta có muốn tránh cũng không tránh nổi. Bởi vì duy trì hi vọng sinh tồn cho tất cả chúng ta, chiến dịch lần này, chỉ cho phép thành công, không được phép thất bại. Section order 5: Paragraph: - Ba người đứng đầu bảng chiến công trong ba ngày tiếp theo sẽ được ban thưởng một quả ớt biến dị! Section order 6: Paragraph: - Rõ! Section order 7: Paragraph: Theo mệnh lệnh của Hàn Phong phát ra, ánh mắt của những người trong phòng đều bốc lên hoả quang hừng hực. Section order 8: Paragraph: Bọn họ đã không còn yếu nhược như những ngày đầu tiên nữa. Hiện tại tiểu đội trưởng thấp nhất cũng cấp 7, cao nhất tiếp cận cấp 8, người nào cũng có kỹ năng nhị giai, thậm chí là vài kỹ năng nhị giai kết hợp. Section order 9: Paragraph: Đã đến lúc bọn họ trả thù đám thây ma đáng ch.ết kia. Section order 10: Paragraph: Phần thưởng ớt biến dị lại càng khiến bọn họ bị kích thích. Kia chính là vật phẩm có thể khiến người ta đột nhiên mạnh lên! Section order 11: Paragraph: 10 phút sau, hơn 80 đội viên trong trang phục quân đội chính quy đã tập trung trong sân rộng. Section order 12: Paragraph: Bởi vì đánh hạ được một khu huấn luyện, hiện tại đội viên nào cũng đều được trang bị tới tận răng. Mỗi người đều có quân phục rằn ri xanh lục, lưng đeo súng AK74 nâng...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 143.docx; chapter_title=Chương 143: Triển khai tấn công; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=94 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
