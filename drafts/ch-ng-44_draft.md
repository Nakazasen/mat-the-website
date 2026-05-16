# Draft Knowledge: Chương 44

- source_id: ingest-2066724ffa495cae
- raw_file: raw/Chương 44.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 44: Vũ khí tới tay Section order 8: Paragraph: Hàn Phong bĩu môi, thật sự là quỷ nghèo. Một con mèo level 12 lại chỉ rớt ra một sách kỹ năng nhị giai. Aizz, nhớ ngày đầu tiên hắn và Ngô Soái đánh bại F1, kia trực tiếp rơi ra kỹ năng tam giai. Section order 12: Paragraph: Hắn đang suy nghĩ nghiêm túc về việc có nên ra ngoài chiến đấu hay tiếp tục ở nhà nấu cơm cùng Mộ Thi Thi.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- minh

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
- explain Chương 44
- summarize Chương 44
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 44.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 44: Vũ khí tới tay Section count: 92 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 44: Vũ khí tới tay Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: “24 exp, lượng kinh nghiệm gấp đôi bình thường. Thật tốt…” Section order 4: Paragraph: Hàn Phong lẳng lặng cảm nhận điểm kinh nghiệm tăng lên, nhìn tới bên cạnh xác của mèo biến dị có một cuốn sách, một thẻ kỹ năng, một viên tinh thạch màu đỏ rớt ra. Section order 5: Paragraph: Hắn lập tức nhặt lên xem xét: Section order 6: Paragraph: “Đinh! Sách kỹ năng chủ động nhị giai: Độc Lực! Kỹ năng miêu tả: thả độc lực vào trong công kích vật lý, độc lực có thể tạo ra hiệu quả trúng độc liên tục. Kỹ năng kích hoạt: 3 trí lực. Kỹ năng duy trì: 15 giây. Không có thời gian làm lạnh.” Section order 7: Paragraph: “Đinh! 24 exp!” Section order 8: Paragraph: Hàn Phong bĩu môi, thật sự là quỷ nghèo. Một con mèo level 12 lại chỉ rớt ra một sách kỹ năng nhị giai. Aizz, nhớ ngày đầu tiên hắn và Ngô Soái đánh bại F1, kia trực tiếp rơi ra kỹ năng tam giai. Section order 9: Paragraph: Nhưng cái kỹ năng này cũng có điểm thú vị. Bất quá, hắn không cần lắm. Section order 10: Paragraph: Bỏ qua vấn đề này, Hàn Phong ném tất cả cho Liễu Huyên để nàng ta bảo quản, về sau lại chia chác. Thẻ vật phẩm kia, hắn không dám tự tay mở, sợ sẽ lại là một đôi ủng gia tốc. Section order 11: Paragraph: Tiêu Minh bây giờ mới hoàn hồn, cảm giác dưới háng có chút ẩm ướt, hắn trong lòng vạn phần sợ hãi củng xấu hổ. Chẳng lẽ ra ngoài chiến đấu nguy hiểm tới vậ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 44.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 44: Vũ khí tới tay; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=91 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
