# Draft Knowledge: Chương 201

- source_id: ingest-b93139acc3b2f3e2
- raw_file: raw/Chương 201.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Con chó đen nhìn chằm chằm lá ớt trên tay Hàn Phong, khoé miệng lại tứa ra chút ít nước bọt. Vật kia tuy không bằng cái viên đen kịt, nhưng cũng rất tốt. Section order 7: Paragraph: Hàn Phong mỉm cười, hắn dùng ngón tay chỉ về phía đại lộ Thanh Hà xa xa rồi sủa một tràng: Section order 10: Paragraph: Người chó nghe Hàn Phong nói tới, ánh mắt liếc qua đại lộ Thanh Hà, sau khi nhìn thấy một rừng thây ma đông nghịt rậm rạp, cùng với xa xa là đám thây ma tiến hoá vô cù...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- nhanh

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Con
- Phong
- Thanh

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
- explain Chương 201
- summarize Chương 201
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 201.docx Chapter title: Chương 201: Đàm phán Section count: 80 Section order 1: Heading: Chương 201: Đàm phán Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Con chó đen nhìn chằm chằm lá ớt trên tay Hàn Phong, khoé miệng lại tứa ra chút ít nước bọt. Vật kia tuy không bằng cái viên đen kịt, nhưng cũng rất tốt. Section order 4: Paragraph: Nó thực sự vô cùng thèm khát, bởi vậy lúc này mở miệng sủa nhỏ: Section order 5: Paragraph: - Gâu gâu hú… Section order 6: Paragraph: “Nhân loại, ngươi muốn đàm phán gì? Gâu!” Section order 7: Paragraph: Hàn Phong mỉm cười, hắn dùng ngón tay chỉ về phía đại lộ Thanh Hà xa xa rồi sủa một tràng: Section order 8: Paragraph: - Gâu gâu… Section order 9: Paragraph: “Là thế này, chúng ta đang định tiêu diệt đám quái vật bên kia. Bất quá chúng nó khá mạnh, ngươi có muốn hợp tác hay không? Nếu thành công, đến lúc đó sẽ chia cho ngươi vài viên tinh thạch ma dược, à, là cái viên đen kịt ngươi vừa ăn đó. Gâu!” Section order 10: Paragraph: Người chó nghe Hàn Phong nói tới, ánh mắt liếc qua đại lộ Thanh Hà, sau khi nhìn thấy một rừng thây ma đông nghịt rậm rạp, cùng với xa xa là đám thây ma tiến hoá vô cùng khủng bố, nó không khỏi rùng mình sợ hãi, lông đen trên người dựng hết cả lên. Section order 11: Paragraph: Đây là khác biệt của thây ma bình thường và sinh vật dị biến. Thây ma rất ngu xuẩn, chỉ biết lao lên chịu ch.ết. Sinh vật dị biến thì có trí tuệ, có cảm xúc, có tư duy, biết sợ hãi. Nó không thông minh bằng con người, nhưng sẽ thông minh hơn dã thú thông thường, càng thông minh hơn xa thây ma. Section ord...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 201.docx; chapter_title=Chương 201: Đàm phán; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=79 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
