# Draft Knowledge: Chương 234

- source_id: ingest-8de75c284c57bb17
- raw_file: raw/Chương 234.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Việc này coi như đã xong, bố trí của số 15 tới đây đã trọn vẹn, kế tới là bố trí của số 85. Chỉ cần hoàn thành kế hoạch này, lực lượng trấn Hi Vọng sẽ nhảy vọt, thậm chí đủ sức đương đầu với căn cứ huyện Tam Giang cũng không chừng. Section order 15: Paragraph: Phương Tường vẫn quen gọi thẳng tên của Hàn Phong, không có thay đổi cách gọi thành Hàn đại đội trưởng hay Hàn thủ lĩnh. Hàn Phong đối với vấn đề này không những không phản đối mà còn âm thầm cảm thấy may mắn...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- tinh

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Hi
- Tam Giang

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
- explain Chương 234
- summarize Chương 234
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 234.docx Chapter title: Chương 234: Gặp lại Đại Hắc Cẩu Section count: 79 Section order 1: Heading: Chương 234: Gặp lại Đại Hắc Cẩu Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Hàn Phong từ trước tới nay làm người xảo quyệt nham hiểm, chỉ có chuyện đi lừa người khác kiếm lợi, làm gì có chuyện để người khác dễ dàng chiếm lợi của mình. Nếu không lột một lớp da của đối phương, đánh phế một chi lực lượng của đối phương, hắn sao có thể an tâm cho nổi. Section order 4: Paragraph: Việc này coi như đã xong, bố trí của số 15 tới đây đã trọn vẹn, kế tới là bố trí của số 85. Chỉ cần hoàn thành kế hoạch này, lực lượng trấn Hi Vọng sẽ nhảy vọt, thậm chí đủ sức đương đầu với căn cứ huyện Tam Giang cũng không chừng. Section order 5: Paragraph: Tất cả mấu chốt đều nằm trên người cái nữ nhân Tường Vi kia. Chỉ cần từ nay tới chiều mai trót lọt lừa được nàng ta, hắn sẽ thêm một bước nữa củng cố được năng lực của bản thân. Section order 6: Paragraph: Bất quá, trước hết phải chiêu an con chó ngu ngoài kia đã. Hàn Phong thu hết tài liệu trên bàn bỏ vào balo, sau đó đi thẳng tới khu nuôi cấy ớt biến dị. Nơi này luôn được canh giữ 24/24 bởi ít nhất 3 phi phàm giả cấp 9 cùng 15 đội viên khác chia thành 3 tiểu tổ trị an, số lượng súng đạn cũng được trang bị rất đầy đủ, có thể sẵn sàng phát hiện ra bất kỳ kẻ nào có ý đồ rình mò bén mảng tới. Section order 7: Paragraph: Hàn Phong đi thẳng vào trong phòng, nhìn tới cây ớt rất lớn được trồng trong bồn chứa giữa nhà. Section order 8: Paragraph: Cây ớt biến dị cao tới 60cm, đường kinh thân đã lớn bằng cổ tay, cà...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 234.docx; chapter_title=Chương 234: Gặp lại Đại Hắc Cẩu; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=78 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
