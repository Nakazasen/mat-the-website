# Draft Knowledge: Chương 31

- source_id: ingest-84c855568d7fabe5
- raw_file: raw/Chương 31.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 31: Vây giết thể thôn phệ (2) Section order 25: Paragraph: Đây là một cái téc nước 5000 lít, hay chính xác hơn, là một cái téc nước muối 5000 lít. Thanh sắt cố định bệ đỡ bị Hàn Phong đá gãy khiến vật này mất trọng tâm, nghiêng qua một bên mà đổ xuống. Section order 37: Paragraph: Hai người kia sớm đã ở trong trạng thái tập trung cao độ, vừa nghe Hàn Phong ra lệnh, một người thì ngưng tụ lôi cầu ném xuống E2, người khác thì thò tay...

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
- Sinh
- Nguy
- Section
- Heading
- Paragraph
- Trong

### Modules
- none

### Errors
- 5000 l

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
- explain Chương 31
- summarize Chương 31
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 31.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 31: Vây giết thể thôn phệ (2) Section count: 87 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 31: Vây giết thể thôn phệ (2) Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Trong tầm quan sát của E2, cái sinh vật bé nhỏ đáng ch.ết kia lại trốn thoát khỏi công kích của nó, sau đó sinh vật đó nhún người một cái, nhảy vào cái lỗ trên bức tường cao chắn ngang con đường này, thoáng cái biến mất. Section order 4: Paragraph: Vách tường kia sớm đã được chăng kín những sợi dây thừng. Section order 5: Paragraph: Thể thôn phệ ngửa đầu gào lên một tiếng dữ tợn, dưới chân lại nhún, phá tan nền gạch, phóng thẳng về phía bức tường. Nó muốn mạnh mẽ xông tới, đập nát cả bức tường này. Section order 6: Paragraph: Thế nhưng khoảnh khắc nó phóng tới, một thanh âm âm trầm quanh quẩn vang lên: Section order 7: Paragraph: - Đâm xuyên tinh thần! Section order 8: Paragraph: Chính là Hàn Phong đang đứng trên nóc nhà, bàn tay xoè ra năm ngón, lòng bàn tay hướng về phía E2 như thể một hành động phán quyết. Section order 9: Paragraph: Kỹ năng đâm xuyên tinh thần của nhẫn duy tâm! Section order 10: Paragraph: - Réckkk… Réc réc… Section order 11: Paragraph: Bị trúng chiêu khiến động tác của E2 đột nhiên khựng lại, tốc độ điên cuồng giảm mạnh, ngay cả thanh âm kêu gào cũng trở nên đứt quãng. Cả cơ thể nó xệt xệt lăn mấy vòng, nặng nề đập vào tường bao sân bóng. Section order 12: Paragraph: Nó chỉ khựng lại một, hai giây, tâm thần lập tức trở lại thanh tỉnh. Nó vừa muốn đứng lên, trên đỉnh đầu...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 31.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 31: Vây giết thể thôn phệ (2); ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=86 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
