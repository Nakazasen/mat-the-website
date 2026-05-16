# Draft Knowledge: Chương 328

- source_id: ingest-b22afa3c2d5893d7
- raw_file: raw/Chương 328.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Sau khi Liễu Huyên rời đi, trong phòng họp chỉ còn lại hai người, Hàn Phong lúc này mới bình tĩnh hỏi người bên cạnh: Section order 27: Paragraph: - Đã tuyển chọn ra được hơn chục người, đặc biệt là nhóm tàn quân Tam Giang có vài người rất phù hợp. Từ ngày mai, đệ sẽ chính thức cùng với họ tập luyện. Section order 29: Paragraph: - Ngày mai đệ qua Tam Giang hỗ trợ bên kia “sản xuất” đạn pháo diệt quỷ cần phải cẩn thận, kế hoạch cụ thể là…

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
- Sau
- Phong
- Hi

### Modules
- none

### Errors
- 500 m

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
- explain Chương 328
- summarize Chương 328
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 328.docx Chapter title: Chương 328: Lỗi của người đứng đầu Section count: 62 Section order 1: Heading: Chương 328: Lỗi của người đứng đầu Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Sau khi Liễu Huyên rời đi, trong phòng họp chỉ còn lại hai người, Hàn Phong lúc này mới bình tĩnh hỏi người bên cạnh: Section order 4: Paragraph: - Đệ thấy sao, nên xử lý thế nào? Section order 5: Paragraph: Ngô Soái hàm răng cắn chặt vào nhau, trên khuôn mặt hiện lên vô số biểu cảm phức tạp. Có khó tin, có tức giận, có hoang mang, có kinh ngạc không hiểu, có tự trách, có hối hận. Hắn không thể ngờ rằng bên ngoài trấn Hi Vọng thể hiện một bộ mặt tân sinh tràn đầy sức sống, vậy mà bên trong lại có nhiều như vậy khúc mắt khuất tất, nhiều như vậy bất mãn cùng âm thầm xấu xa… Section order 6: Paragraph: Những suy nghĩ điên cuồng hiện lên trong não hắn như thể vô số con sâu đang bò lổm ngồi rồi thi nhau cắn xé đục khoét, lại thải ra chất độc thần kinh hạng nặng, để cho trong lòng hắn tràn ngập một cảm giác đau khổ cùng bất lực. Một lúc sau, hắn mới khàn giọng đáp lại: Section order 7: Paragraph: - Đại ca… Đệ… Đệ không biết… Section order 8: Paragraph: Hàn Phong không quá bất ngờ vì câu trả lời của đối phương. Ngô Soái chung quy cũng chỉ là một thằng nhóc 18 tuổi với tâm hồn chính nghĩa, 18 năm chỉ ăn học trên ghế nhà trường, tất nhiên không có bao nhiêu trải nghiệm thực tế, không bao giờ gặp phải trùng kích, tất nhiên sẽ hoang mang khi trực tiếp phải đối diện những mặt tối này. Section order 9: Paragraph: Hơn nữa những điều xấu xa hắc ám này lại xuất phát...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 328.docx; chapter_title=Chương 328: Lỗi của người đứng đầu; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=61 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
