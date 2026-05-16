# Draft Knowledge: Chương 407

- source_id: ingest-2cf9ac9ef99b11d9
- raw_file: raw/Chương 407.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 17: Paragraph: Kích động chiến tranh nổ ra, hắn đã thất bại. Hắn công khai giết hai người kia trước mặt cư dân Liễu Lâm, vậy mà lại bị Hàn Phong hồi sinh, đồng thời còn chĩa ngược mũi dùi về phía Tam Giang, đoạt mất đại nghĩa vừa mới thành hình. Section order 20: Paragraph: Giết Hà Tam. Cũng chưa hoàn thành. Tuy nhiên đây chỉ là việc nhỏ, giết thằng kia vào lúc nào cũng được, nhưng giết vào lúc này thì rất dễ gây kinh động đám cao tầng trấn Hi Vọng, việc tiếp theo sẽ khó làm hơn...

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
- Phong
- Hi
- Tam

### Modules
- none

### Errors
- 407

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
- explain Chương 407
- summarize Chương 407
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 407.docx Chapter title: Chương 407 Section count: 52 Section order 1: Heading: Chương 407 Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong nằm trên giường ngủ rất ngon, khuôn mặt còn hiện lên vô tận an tường, hẳn là đang mơ một giấc mơ rất đẹp. Ánh trăng ngoài cửa sổ chiếu xuống thân thể hắn còn hiện lên một màu bạc trắng lóng lánh, cảnh tượng này thật giống như một vị bạch mã hoàng tử ngủ quên trong rừng vậy. Section order 4: Paragraph: Nếu hiện tại mà có nàng công chúa xinh đẹp nào lỡ chân lạc đường tìm tới, chắc chắn nàng ta sẽ không nhịn được mà lao lên rồi hôn một miếng để đánh thức chàng hoàng tử đẹp trai đang nằm kia, sau đó cả hai sẽ cùng với nhau sống hạnh phúc đến cuối đời. Section order 5: Paragraph: Chẳng qua nhan sắc của Hàn Phong chỉ tương đương với một thằng chăn ngựa, dù có trăng bạc tuyệt đẹp gánh bớt một phần, hắn cũng chỉ tương đương với một thằng chăn liền lúc 10 con ngựa, làm gì đủ tuổi ngoi lên được tầm bạch mã hoàng tử. Hơn nữa cũng chẳng có nàng công chúa quái nào lại lang thang vào cái tầm giờ nửa đêm này ngoài đường mà mò được tới phòng hắn, hôn hít lại càng không, ai mà biết thằng chăn ngựa nằm kia có thường xuyên đánh răng trước khi đi ngủ hay không chứ. Section order 6: Paragraph: Bất quá không sao, chỉ cần ngươi là thủ lĩnh một thế lực thì tất có người sẽ ngày nhớ đêm mong, công chúa có thể không tới, nhưng sát thủ thì có đấy. Section order 7: Paragraph: 12h45p đêm, một cái bóng dáng đen kịt với con mắt trắng ởn lạnh lẽo "chảy" từ trên mái nhà xuống dưới, ngự ở bên ngoài cửa sổ, cái bóng đen nà...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 407.docx; chapter_title=Chương 407; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=51 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
