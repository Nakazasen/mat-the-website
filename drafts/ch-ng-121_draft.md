# Draft Knowledge: Chương 121

- source_id: ingest-035d09ec69a1e9d4
- raw_file: raw/Chương 121.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Nghe thấy thông báo này của Hàn Phong, những tiểu đội trưởng ngồi đây không có một chút hưng phấn, trái lại là một cảm giác nặng nề ngập tràn sầu lo. Section order 8: Paragraph: Hai tiểu đội trưởng mới tấn thăng này cũng không phải hắn tuỳ ý bổ nhiệm. Ngay từ 3 ngày trước hắn đã lên kế hoạch cho việc này rồi. Chiến tranh cần quân, cũng cần tướng. Cần người hi sinh, cũng cần người nêu gương hi sinh. Section order 11: Paragraph: Tin tức xấu đã công bố xong xuôi, Hàn...

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
- Con
- Section
- Heading
- Paragraph
- Nghe
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
- explain Chương 121
- summarize Chương 121
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 121.docx Chapter title: Chương 121: Con đường trải sẵn Section count: 93 Section order 1: Heading: Chương 121: Con đường trải sẵn Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: - Chiến tranh, tới gần rồi. Section order 4: Paragraph: Nghe thấy thông báo này của Hàn Phong, những tiểu đội trưởng ngồi đây không có một chút hưng phấn, trái lại là một cảm giác nặng nề ngập tràn sầu lo. Section order 5: Paragraph: Chỉ một đầu P2 đã khiến toàn trấn thiếu chút bị nó diệt sạch, nếu là một binh đoàn 3 vạn quân thây ma, ít nhất cũng có vài đầu quái vật khủng bố như vậy. Section order 6: Paragraph: Đến lúc đó, làm sao chống lại đây… Section order 7: Paragraph: Hàn Phong liếc mắt một vòng, nhìn tới Đào Đại Tư và Hứa Dương. Section order 8: Paragraph: Hai tiểu đội trưởng mới tấn thăng này cũng không phải hắn tuỳ ý bổ nhiệm. Ngay từ 3 ngày trước hắn đã lên kế hoạch cho việc này rồi. Chiến tranh cần quân, cũng cần tướng. Cần người hi sinh, cũng cần người nêu gương hi sinh. Section order 9: Paragraph: Họ được bổ nhiệm chính là để chuẩn bị cho cuộc chiến với thây ma sắp tới đây. Bằng không thì lý nào Hàn Phong chịu để một nam nhân thân chính phủ, một nữ nhân cơ bắp to não nhỏ đứng ra nắm quyền chứ. Section order 10: Paragraph: Có thực lực vượt trội thì bước lên mà cống hiến đi thôi. Section order 11: Paragraph: Tin tức xấu đã công bố xong xuôi, Hàn Phong mới chậm rãi công bố tin tức tốt: Section order 12: Paragraph: - Mọi người không cần quá bi quan. Chúng ta đối diện thi đàn cũng không nhất thiết phải dùng gậy đập, đao chém, thân cận thân chiến đấu....

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 121.docx; chapter_title=Chương 121: Con đường trải sẵn; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=92 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
