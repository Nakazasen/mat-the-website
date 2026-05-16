# Draft Knowledge: Chương 326

- source_id: ingest-b2b312a32135f385
- raw_file: raw/Chương 326.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Hai nhiệm vụ mà cao tầng căn cứ huyện Tam Giang giao cho Hoàng Khải, một là chiêu mộ phi phàm giả, hai là thu hồi trang thiết bị quân sự, tại sao lại đều thất bại cả rồi. Section order 4: Paragraph: Chiếc xe bọc thép BMP-1 tại bến thuyền kia, bọn họ đã dùng cả ngày để sửa chữa lắp ráp, kết quả phát hiện nó thiếu vài cái linh kiện cực kỳ quan trọng, không có thì không thể di chuyển được. Hiện tại tới cả 1 chiếc BMP-1, 2 chiếc BTR-60 cùng 4 chiếc BTR-152 sờ sờ ra đó...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- trang

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Thay
- Section
- Heading
- Paragraph
- Hai
- Tam Giang

### Modules
- none

### Errors
- 500 qu

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
- explain Chương 326
- summarize Chương 326
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 326.docx Chapter title: Chương 326: Thay đổi thái độ Section count: 60 Section order 1: Heading: Chương 326: Thay đổi thái độ Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hai nhiệm vụ mà cao tầng căn cứ huyện Tam Giang giao cho Hoàng Khải, một là chiêu mộ phi phàm giả, hai là thu hồi trang thiết bị quân sự, tại sao lại đều thất bại cả rồi. Section order 4: Paragraph: Chiếc xe bọc thép BMP-1 tại bến thuyền kia, bọn họ đã dùng cả ngày để sửa chữa lắp ráp, kết quả phát hiện nó thiếu vài cái linh kiện cực kỳ quan trọng, không có thì không thể di chuyển được. Hiện tại tới cả 1 chiếc BMP-1, 2 chiếc BTR-60 cùng 4 chiếc BTR-152 sờ sờ ra đó cũng thất lạc nốt, vậy thì lấy đâu ra tài nguyên mà báo cáo đây? Section order 5: Paragraph: Hắn lúc này vội vã hỏi lại Vương Tốn: Section order 6: Paragraph: - Vương thiếu uý, rốt cuộc mọi chuyện là sao? Vương Tốn lắc đầu thở dài, cuối cùng đem tình hình chiến trận đáp lại chi tiết từng chút một. Section order 7: Paragraph: Cuối ngày giao chiến, Hàn Phong muốn toàn lực công phá ngọn đồi thây ma nên đã ra lệnh cho tất cả bọc thép tấn công tới sào huyệt địch nhân, kết quả là dính phải một đòn đau của thủ lĩnh thi đàn, lái xe đều bị đánh ngất cả. Thây ma bao vây quá dày đặc, bọn họ buộc phải bỏ xe chạy lấy người, cuối cùng khiến tất cả bọc thép đều đã trực tiếp bị kẹt lại. Section order 8: Paragraph: Hàn Phong để cho Ngô Soái ở lại tìm cách giải cứu phương tiện, bản thân thì dẫn theo binh lính dưới trướng trở về trước. Đám người Vương Tốn tất nhiên không thể đơn độc ở lại tiền tuyến chờ đợi, đó chẳng khá...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 326.docx; chapter_title=Chương 326: Thay đổi thái độ; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=59 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
