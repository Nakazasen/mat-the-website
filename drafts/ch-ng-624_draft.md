# Draft Knowledge: Chương 624

- source_id: ingest-6bc8e22ecd933dd5
- raw_file: raw/Chương 624.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: operations_report

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 624: Bóc lột thuộc hạ Section order 20: Paragraph: Hai chỉ tiêu KPIs này... Thật sự là sức nặng khủng bố mà... Section order 53: Paragraph: Nghe được những lời này, các tiểu đội trưởng trong phòng họp tuy vẫn còn rất nhiều áp lực, thế nhưng rốt cuộc cũng có một chút điểm dựa, đã cảm thấy KPIs khả thi hơn đôi chút.

## Document Purpose
- purpose: operations_report
- confidence: 0.47
- signals: kpi

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
- explain Chương 624
- summarize Chương 624
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 624.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 624: Bóc lột thuộc hạ Section count: 159 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 624: Bóc lột thuộc hạ Section order 2: Paragraph: 18-23 phút Section order 3: Paragraph: Quyết định của Hàn Phong giao một phần ba lượng binh lực dự bị cho Hồ Du khiến cho tất cả mọi người đều âm thầm chấn động. Section order 4: Paragraph: Phải biết rằng sau trận chiến ngày hôm qua thì hầu hết tất cả đội viên dự bị đều đã thăng tiến rất nhiều, thăng tiến cả về mặt sức mạnh lẫn kinh nghiệm, cả tâm lý và tinh thần, những người này đều đã đủ điều kiện tấn thăng đội viên chính thức. Bọn họ những tiểu đội trưởng này còn đang mong chờ được chia chác nhóm phi phàm giả ưu tú mới nổi này để bổ xung tiêu hao đây, bất quá hiện tại trực tiếp bị "bắt mất" một phần ba, không ai là không cảm thấy đau lòng. Section order 5: Paragraph: Đội ngũ mạnh, đông thành viên, tất nhiên hiệu quả chiến đấu sẽ lớn, chiến công nhận về cũng nhiều, tài nguyên theo đó cũng nhận được nhiều hơn, cả thực lực cá nhân và quyền lực trong tổ chức đều sẽ càng được đẩy lên một bước mới. Section order 6: Paragraph: Chỉ còn 2/3 quân lực dự bị, lại phải chia cho 19 tiểu đội, mỗi đội sẽ được thêm bao nhiêu đây, không bao nhiêu cả... Section order 7: Paragraph: Nhưng mà đau lòng thì cũng phải chịu thôi, ai dám đứng ra thắc mắc đây, hay có thể nói là, ai dám tuyên bố bản thân sẽ từ chức khi làm không tốt đây? Section order 8: Paragraph: Bọn họ nhìn về phía Hồ Du, tất cả đều cảm tưởng như đã nhìn thấy được hình bóng của một vị đại đội trưởng t...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 624.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 624: Bóc lột thuộc hạ; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=158 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
