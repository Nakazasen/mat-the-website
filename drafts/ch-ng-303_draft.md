# Draft Knowledge: Chương 303

- source_id: ingest-d07919ec37c5332c
- raw_file: raw/Chương 303.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Sau khi hơn 70 đội viên đã leo lên xe, Hàn Phong mới phất tay rồi hô lên: Section order 15: Paragraph: Hà Tam ngồi bên cạnh Hàn Phong lúc này nhiệt tình giới thiệu: Section order 26: Paragraph: Chiếc BMP-1 đã đâm xuyên đàn lũ thây ma để đến giao lộ Vạn Hoa, đây cũng là địa điểm lúc trước bọn họ làm thịt hơn một vạn thây ma, nơi này cũng cách ngọn đồi mục tiêu 4 cây số, bước gần tới vùng nguy hiểm rồi.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- level

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Sau
- Phong
- A3

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
- explain Chương 303
- summarize Chương 303
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 303.docx Chapter title: Chương 303: Dò xét thi đàn Section count: 55 Section order 1: Heading: Chương 303: Dò xét thi đàn Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Sau khi hơn 70 đội viên đã leo lên xe, Hàn Phong mới phất tay rồi hô lên: Section order 4: Paragraph: - Xuất phát! Section order 5: Paragraph: Lần hành động này lấy việc thử nghiệm chiến thuật và thăm dò giới hạn chịu đựng của thi đàn là chính, tiêu diệt thây ma chỉ là phụ, quan trọng nhất là phải đảm bảo đi bao nhiêu trở về đủ bấy nhiêu. Bởi vậy thành phần đội viên vẫn chủ yếu là các đội viên có kỹ năng phòng ngự, khống chế, có thể làm ra tác dụng đánh chặn thi đàn để rút lui bất cứ lúc nào. Section order 6: Paragraph: Ngồi trên một chiếc xe jeep cơ động cao, Hàn Phong đang chăm chú nhìn qua màn hình máy tính quan sát toàn cảnh khu vực bên dưới. Nhờ có drone trinh sát, hắn có thể nắm rõ tình hình di động của thi đàn các nơi, chỗ nào đông đúc, chỗ nào tản mát, chỗ nào bị đột kích, lúc này hắn sau khi phân tích cẩn thận thì trầm giọng ra lệnh: Section order 7: Paragraph: - Thông báo cho đội 2 tách ra, tiến về đường A3, sẵn sàng bỏ chạy về đường A9 hoặc B27. Section order 8: Paragraph: - Rõ! Section order 9: Paragraph: Đội viên phụ trách thông tin lập tức giơ bộ đàm trong tay lên ngắn gọn nói: Section order 10: Paragraph: - Đội 2 nghe rõ, tiến về A3, rút lui về A9 hoặc B27. Xác nhận. Section order 11: Paragraph: - Xác nhận. Section order 12: Paragraph: Bên kia lập tức có âm thanh xác nhận trở lại, sau đó một xe bọc thép BTR-60 cùng 2 cỗ xe tải chờ quân lập tức tách ra...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 303.docx; chapter_title=Chương 303: Dò xét thi đàn; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=54 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
