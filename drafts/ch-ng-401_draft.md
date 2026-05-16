# Draft Knowledge: Chương 401

- source_id: ingest-1787e5f12f2800e6
- raw_file: raw/Chương 401.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Theo diễn giải của hai người trước mặt, dung dịch trắng sữa có hiệu quả gia tăng chống chịu vô cùng mạnh mẽ. Đoàn Thanh được cộng vĩnh viễn 3 chống chịu, hiện tại khi uống vào 100ml, cậu ta vẫn tiếp tục được nhận thêm 10 chống chịu tạm thời, chưa có dấu hiệu đạt tới giới hạn cuối cùng. Section order 10: Paragraph: Nhận được phiếu lương thực trắng và phiếu chiến công 200 điểm từ chỗ Hàn Phong, Đoàn Thanh vô cùng vui mừng nhét nó vào sâu trong túi quần, trong khi Âu...

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
- Theo
- Thanh
- Trong

### Modules
- none

### Errors
- 401
- 401:

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
- explain Chương 401
- summarize Chương 401
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 401.docx Chapter title: Chương 401: Đúng người, đúng thời điểm Section count: 67 Section order 1: Heading: Chương 401: Đúng người, đúng thời điểm Section order 2: Paragraph: 11–13 minutes Section order 3: Paragraph: Theo diễn giải của hai người trước mặt, dung dịch trắng sữa có hiệu quả gia tăng chống chịu vô cùng mạnh mẽ. Đoàn Thanh được cộng vĩnh viễn 3 chống chịu, hiện tại khi uống vào 100ml, cậu ta vẫn tiếp tục được nhận thêm 10 chống chịu tạm thời, chưa có dấu hiệu đạt tới giới hạn cuối cùng. Section order 4: Paragraph: Đây là một tin tức vô cùng tốt, tin tốt hơn là sau hơn 2 ngày sử dụng thì thứ này đã được xác nhận an toàn, không gây ra bất kỳ dấu hiệu nguy hại nào cả. Section order 5: Paragraph: Điểm trừ lớn nhất có lẽ là hao nước. Uống vào dung dịch trắng sữa này sẽ mang tới cho người sử dụng cảm giác tương đối khát, cần phải uống lượng nước gấp 3 tới 4 lần để trung hoà. Trong một cuộc chiến 12 tiếng, nếu binh lính uống 1,2 lít dung dịch trắng sữa thì cần phải uống thêm hơn 3 lít nước để giải toả mới có thể cân bằng lại. Section order 6: Paragraph: Vấn đề này nếu có thể đảm bảo công tác hậu cần bằng 3 xe bồn chở nước ngay phía sau chiến trường thì sẽ được giải quyết. Section order 7: Paragraph: - Tốt, hai người làm rất tốt! Section order 8: Paragraph: Hàn Phong thật sự hài lòng với kết quả này. Hắn sẽ công bố một phần nhỏ kết quả nghiên cứu ngay trong hôm nay với bên ngoài, từ đó làm tiền đề cho việc công khai sản xuất số lượng lớn loại dung dịch này. Section order 9: Paragraph: Trận chiến quy mô lớn trong tương lai, toàn bộ quân đội của trấn Hi...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 401.docx; chapter_title=Chương 401: Đúng người, đúng thời điểm; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=66 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
