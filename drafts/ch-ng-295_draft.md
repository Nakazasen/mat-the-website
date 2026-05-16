# Draft Knowledge: Chương 295

- source_id: ingest-9c76cebcacdc3f99
- raw_file: raw/Chương 295.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Hai người Hàn Phong, Hoàng Khải cứ như vậy bàn luận về nội dung văn bản tiếp theo sẽ ký kết, kia chính là một cái văn bản thể hiện sự phụ thuộc của trấn Hi Vọng vào huyện Tam Giang, trên danh nghĩa sẽ là chi nhánh của chính phủ huyện Tam Giang tại huyện Liễu Lâm, với người quản lý là Hàn Phong, chính phủ sẽ cử tới một đội ngũ phụ trách hỗ trợ và giám sát, định hướng cách làm của trấn Hi Vọng. Section order 7: Paragraph: Tiệc chiêu đãi theo kiểu buffet đã diễn ra đư...

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
- Section
- Heading
- Paragraph
- Hai
- Phong
- Hi

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
- explain Chương 295
- summarize Chương 295
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 295.docx Chapter title: Chương 295: Giờ phút chia ly Section count: 69 Section order 1: Heading: Chương 295: Giờ phút chia ly Section order 2: Paragraph: 9–11 minutes Section order 3: Paragraph: Hai người Hàn Phong, Hoàng Khải cứ như vậy bàn luận về nội dung văn bản tiếp theo sẽ ký kết, kia chính là một cái văn bản thể hiện sự phụ thuộc của trấn Hi Vọng vào huyện Tam Giang, trên danh nghĩa sẽ là chi nhánh của chính phủ huyện Tam Giang tại huyện Liễu Lâm, với người quản lý là Hàn Phong, chính phủ sẽ cử tới một đội ngũ phụ trách hỗ trợ và giám sát, định hướng cách làm của trấn Hi Vọng. Section order 4: Paragraph: Hoàng Khải trong mắt bùng lên sự hưng phấn khó thể cưỡng nổi, đây chính là cơ hội của hắn. Chỉ cần có thể tranh thủ được cái vị trí giám sát viên tại trấn Hi Vọng này, vậy thì hắn sẽ thoát ly được sự kìm hãm của thượng cấp, dần dần xây dựng lên thế lực của riêng mình, còn đạt được tài nguyên khó có thể tưởng tượng nổi. Section order 5: Paragraph: Bên cạnh bọn họ, Lạc Thanh Thuỷ từ đầu tới cuối vẫn luôn giữ vẻ mặt nhàm chán tẻ nhạt, nàng hiện tại chỉ mong mau mau hoàn thành nhiệm vụ bên trên giao xuống, sau đó tới bến tàu kia thực hiện dự định cá nhân. Về phần cái gì công văn, chỉ đạo, ký kết, nàng hoàn toàn không quan tâm, càng không có ý định tham gia vào. Section order 6: Paragraph: Bọn họ bước tới nhà ăn cũng là lúc hoàn thành những nhận định chung về nội dung cơ bản, nội dung chi tiết tất nhiên sẽ được bàn bạc sau. Section order 7: Paragraph: Tiệc chiêu đãi theo kiểu buffet đã diễn ra được một khoảng thời gian, không chỉ có các tiểu đội trưởng...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 295.docx; chapter_title=Chương 295: Giờ phút chia ly; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=68 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
