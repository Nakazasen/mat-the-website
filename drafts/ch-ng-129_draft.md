# Draft Knowledge: Chương 129

- source_id: ingest-5f4107ec5b4b8b8e
- raw_file: raw/Chương 129.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 7: Paragraph: Bên này, đám người Hàn Phong cũng lục tục nhảy xuống xe. Hàn Phong nhìn lướt qua người tới, hai chiếc xe jeep với 8 đại hán mang theo súng trường, đây là đội hình cực mạnh. Section order 9: Paragraph: Hai bên tới cách nhau 3 mét thì dừng lại, Hàn Phong nhìn đối phương mỉm cười nói: Section order 10: Paragraph: - Xin chào, tôi là Hàn Phong, thủ lĩnh đoàn xe. Chẳng hay vì sao các vị chặn đường chúng tôi? Đại hán râu rậm nhìn phe Hàn Phong, bên này có Ngô Soái, Châu L...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- theo

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Hai
- Xin

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
- explain Chương 129
- summarize Chương 129
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 129.docx Chapter title: Chương 129: Thôn Xuân Lê Section count: 105 Section order 1: Heading: Chương 129: Thôn Xuân Lê Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Hàn Phong nhướng mày, sau khi nghĩ tới cái gì đó, hắn mỉm cười ra lệnh: Section order 4: Paragraph: - Dừng xe đi. Section order 5: Paragraph: Đội viên lái xe đựa theo lời hắn bấm còi nháy đèn ra hiệu cho phía sau, sau đó cả đoàn xe chậm rãi ngừng lại. Section order 6: Paragraph: Nhìn ba chiếc xe bọc thép to lớn như ba con quái thú trước mặt, đại hán cao lớn râu rậm không khỏi có chút nuốt nước bọt. Nhưng nghĩ tới đại ca mạnh mẽ vô song, gã cũng dâng lên tinh thần, từ trên xe bọc thép nhảy xuống. Section order 7: Paragraph: Bên này, đám người Hàn Phong cũng lục tục nhảy xuống xe. Hàn Phong nhìn lướt qua người tới, hai chiếc xe jeep với 8 đại hán mang theo súng trường, đây là đội hình cực mạnh. Section order 8: Paragraph: Những người này đều mang theo trảm mã đao hoặc gậy bóng chày, hẳn đều là người phi phàm. Đại hán râu rậm tay phải còn đeo kín 5 chiếc nhẫn, chứng minh thực lực của gã là vô cùng mạnh mẽ. Section order 9: Paragraph: Hai bên tới cách nhau 3 mét thì dừng lại, Hàn Phong nhìn đối phương mỉm cười nói: Section order 10: Paragraph: - Xin chào, tôi là Hàn Phong, thủ lĩnh đoàn xe. Chẳng hay vì sao các vị chặn đường chúng tôi? Đại hán râu rậm nhìn phe Hàn Phong, bên này có Ngô Soái, Châu Lam, Đào Đại Tư đều toả ra khí chất thiện chiến, lại còn có hai quân nhân mặc quân phục, chứng tỏ là đội hình chính quy lão luyện. Section order 11: Paragraph: Khi nhìn tới Thanh...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 129.docx; chapter_title=Chương 129: Thôn Xuân Lê; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=104 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
