# Draft Knowledge: Chương 85

- source_id: ingest-09aba3f5b0878f5a
- raw_file: raw/Chương 85.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 85: Tử sĩ Section order 18: Paragraph: Cầu Lệ Giang là một trong ba cây cầu kết nối hai huyện Liễu Lâm và Tam Giang. Nếu không muốn đi qua cầu này, vậy phải đi tiếp 6 cây số nữa mới tới cầu Dương Lê. Section order 24: Paragraph: - Triệu Tứ, Long Hưu, hai người phụ trách đảm bảo an toàn xung quanh, cố gắng đừng dùng súng. Lê Tam Ba, cậu canh chừng súng máy, có vấn đề lập tức yểm trợ.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- level
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
- explain Chương 85
- summarize Chương 85
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 85.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 85: Tử sĩ Section count: 99 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 85: Tử sĩ Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Quả nhiên giống hệt miêu tả của biểu huynh Hàn Phong, thây ma ở khu vực này đều biểu hiện ra trạng thái kỳ dị, bọn chúng đều đang quay mặt về một hướng. Section order 4: Paragraph: Hướng đó chính là phía đường dẫn tới ký túc xá cảnh sát cơ động, trung tâm huyện Liễu Lâm. Section order 5: Paragraph: Cũng may, bọn họ chạy tới phía bắc, càng lúc càng xa trung tâm huyện. Mà theo Ngô Soái chăm chú quan sát, tình trạng ngẩn người kỳ dị này đang giảm dần, đầu tiên là cả những thây ma level 5, level 6 cũng ngẩn người, hiện tại chỉ còn lại thây ma level 1, hơn nữa càng ngày tình trạng này càng giảm. Section order 6: Paragraph: Có xe bọc thép mở đường, thây ma hầu như không thể ngăn cảm nổi đoàn xe. Chỉ có số ít đoạn tắc bởi thây ma kẹt cứng, Ngô Soái trực tiếp nhảy xuống tàn sát một trận, đoàn xe lại khởi hành không dừng. Section order 7: Paragraph: Hắn không khỏi dâng lên thắc mắc với Quan Bình: Section order 8: Paragraph: - Đoạn đường này tương đối nguy hiểm, tại sao các anh lại chạy thoát được vậy? Quan Bình cắn chặt răng nói: Section order 9: Paragraph: - Chúng tôi vốn hình thành một đoàn 4 xe chạy trốn, cũng có súng máy 7.62mm áp trận. Chẳng qua 3 xe còn lại đã bị thây ma tầng tầng lớp lớp bao vây, không biết thất lạc đi đâu mất, tôi chạy cuối vậy mà may mắn thoát nạn… Section order 10: Paragraph: Ngô Soái gật đầu, không hỏi thêm nữa...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 85.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 85: Tử sĩ; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=98 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
