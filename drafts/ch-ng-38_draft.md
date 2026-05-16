# Draft Knowledge: Chương 38

- source_id: ingest-c273030953565c88
- raw_file: raw/Chương 38.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 38: Rắc rối tìm tới cửa Section order 21: Paragraph: - Tiểu Phong Phong, đệ nghe rồi! Section order 31: Paragraph: Qua loa giao tế mấy câu khách sáo, Hàn Phong lên phòng, thay tạm một bộ đồ sau đó xuống tầng. Hắn cũng không dở người tới mức chui vào phòng tắm để đám người phía dưới phải chờ thêm.

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
- explain Chương 38
- summarize Chương 38
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 38.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 38: Rắc rối tìm tới cửa Section count: 89 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 38: Rắc rối tìm tới cửa Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Hàn Phong từ balo sau lưng lấy ra một đôi ủng gia tốc cho nàng ta rồi nói: Section order 4: Paragraph: - Tốt, đây là phần thưởng. Section order 5: Paragraph: Đào Đại Tư cầm đôi ủng, có chút tham lam xoa xoa, sau đó chậm rãi nói: Section order 6: Paragraph: - Ông chủ Hàn, có thể đổi ủng này bằng trảm mã đao hay không? Section order 7: Paragraph: Đào Đại Tư luôn miệng gọi Hàn Phong là ông chủ Hàn, chính là do hắn đã cho nàng ta thuê trảm mã đao, đồng thời đồng ý bảo hộ nàng ta thăng cấp. Section order 8: Paragraph: Nàng ta trước tận thế chỉ là một người làm thuê tạp vụ chăn ngựa trong gia đình giàu có, cứ ai quản lý nàng ta, vậy nàng ta liền gọi là ông chủ. Hàn Phong vừa “ứng lương”, vừa “bao ăn bao ở”, chẳng khác nào ông chủ cả. Section order 9: Paragraph: Hàn Phong lắc đầu cười: Section order 10: Paragraph: - Đao này giá trị cao hơn ủng gia tốc. Section order 11: Paragraph: Đào Đại Tư ngẫm nghĩ, tính toán, sau đó nói: Section order 12: Paragraph: - Vậy tôi chấp nhận làm thuê cho ông chủ Hàn 10 năm. Section order 13: Paragraph: Hàn Phong thiếu chút đã phun nước đang uống ra ngoài. 10 năm? Nãi tử này tự muốn ký hợp đồng nô lệ à? Section order 14: Paragraph: Hắn tất nhiên không phải người “tốt” mà đi giải thích cho nàng ta. Thấy lợi, ngu gì không đồng ý. Section order 15: Paragraph: - Ân, cũng được, vậy tr...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 38.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 38: Rắc rối tìm tới cửa; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=88 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
