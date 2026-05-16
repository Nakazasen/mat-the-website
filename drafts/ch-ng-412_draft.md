# Draft Knowledge: Chương 412

- source_id: ingest-838de6b2d99455da
- raw_file: raw/Chương 412.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Chu Vấn tiếp nhận hai món vật phẩm mà Hàn Phong đưa qua, ánh mắt theo đó xuất hiện hàn quang vô cùng lạnh lùng. Section order 6: Paragraph: Hàn Phong sau khi bàn giao xong vật phẩm và chi tiết quá trình thực hiện cho Chu Vấn thì quay qua con chó đen bên cạnh sủa nói: Section order 14: Paragraph: Lúc này nó thò bàn tay to phạc đầy lông lá ra tóm lấy cổ Chu Vấn rồi nhún chân phóng thẳng về một phương hướng bên hông trấn Hi Vọng. Hai con mắt sáng quắc như hai đốm lửa...

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
- Chu
- Phong
- Hi

### Modules
- none

### Errors
- 412
- 500ml n
- 400 v

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
- explain Chương 412
- summarize Chương 412
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 412.docx Chapter title: Chương 412 Section count: 70 Section order 1: Heading: Chương 412 Section order 2: Paragraph: 12–15 minutes Section order 3: Paragraph: Chu Vấn tiếp nhận hai món vật phẩm mà Hàn Phong đưa qua, ánh mắt theo đó xuất hiện hàn quang vô cùng lạnh lùng. Section order 4: Paragraph: Cậu ta vốn là một tên lưu manh đầu đường xó chợ vô pháp vô thiên điển hình, nhìn thấy đám người chính phủ luôn giao rảng đạo lý cái gì mà chính nghĩa, chính quy, dân chủ, nhân quyền, nghe câu nào ngứa tai câu đó, hầu như chỉ muốn ném cho chó ăn. Hiện tại lại thấy được hành vi u ám tàn độc trong bóng tối của chính phủ thì lại càng không nhịn được, tất nhiên là muốn tự mình xả ra một ngụm ác khí. Section order 5: Paragraph: Giờ thì tốt rồi, thủ lĩnh chẳng những cho phép cậu ta thực hiện trả thù mà còn trực tiếp tham gia đồng hành hùa theo, đây chính là thiên đại hảo sự. Section order 6: Paragraph: Hàn Phong sau khi bàn giao xong vật phẩm và chi tiết quá trình thực hiện cho Chu Vấn thì quay qua con chó đen bên cạnh sủa nói: Section order 7: Paragraph: - Gâu gâu. Section order 8: Paragraph: "Đại Hắc Cẩu, ngươi phải đảm bảo an toàn cho thằng nhóc này. Gâu." Section order 9: Paragraph: Đại Hắc Cẩu ngáp một tiếng rồi nhe răng sủa lại: Section order 10: Paragraph: "Nhân loại, ta đã biết, gâu!" Section order 11: Paragraph: Nó nói xong liền không chút do dự gồng người co cứng cơ thể rồi dần đứng thẳng bằng hai chân, chiếc sừng xoắn ốc trên đầu phát ra ánh trăng bạc trắng, khoảnh khắc liền biến thành cong vút như lưỡi liềm, xương cốt cùng cơ bắp trên thân thể càng thêm m...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 412.docx; chapter_title=Chương 412; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=69 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
