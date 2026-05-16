# Draft Knowledge: Chương 142

- source_id: ingest-ae2840cc7ff53a61
- raw_file: raw/Chương 142.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Hàn Phong nhướng mày, hắn nhẹ nhàng đẩy Xuân Hoa từ trong ngực ra, sau đó tiến tới nhấc cây gậy đen nhánh lên. Section order 7: Paragraph: Sau Thanh Phong Đao level 3, đây là vũ khí level 3 tiếp theo mà hắn mở được. Section order 15: Paragraph: Xuân Thu thường thường sẽ may mắn hơn Xuân Hoa nhiều, thẻ vật phẩm trong tay nàng ta rất hay mở ra mấy thứ linh tinh kỳ quái. Nhưng Xuân Hoa lại hay mở ra vũ khí quốc dân trảm mã đao hơn, thích hợp trang bị cho đội viên. Nói...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- level

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Hoa
- Sau Thanh Phong

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
- explain Chương 142
- summarize Chương 142
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 142.docx Chapter title: Chương 142: Kế hoạch tác chiến Section count: 120 Section order 1: Heading: Chương 142: Kế hoạch tác chiến Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong nhướng mày, hắn nhẹ nhàng đẩy Xuân Hoa từ trong ngực ra, sau đó tiến tới nhấc cây gậy đen nhánh lên. Section order 4: Paragraph: Với 28 điểm sức mạnh, hắn rất dễ dàng cầm lên trang bị này. Section order 5: Paragraph: “Đinh! Hắc Thiết Côn level 3. Thuộc tính +5 sức mạnh, +3 nhanh nhẹn. Là vũ khí có sức công phá mạnh mẽ.” Section order 6: Paragraph: Nhìn côn sắt trong tay, tâm trạng hắn không khỏi xuất hiện vui mừng. Section order 7: Paragraph: Sau Thanh Phong Đao level 3, đây là vũ khí level 3 tiếp theo mà hắn mở được. Section order 8: Paragraph: Bất quá, vật này không quá phù hợp cho hắn sử dụng. Nó khá nặng, phải tới 30kg, lại cộng chỉ số sức mạnh nhiều hơn nhanh nhẹn, hắn cầm không vừa tay chút nào. Section order 9: Paragraph: - Cái này chắc sẽ phù hợp với Tiểu Im Lặng. Section order 10: Paragraph: Hắn tự ước lượng một chút sau đó mỉm cười nói: Section order 11: Paragraph: - Tôi rất hài lòng. Section order 12: Paragraph: Xuân Hoa thấy chủ nhân không trách mắng vì nàng đục thủng sàn nhà thì vui mừng, sau đó nàng lần lượt mở nốt hai thẻ vật phẩm còn lại. Section order 13: Paragraph: Một đôi giày phản lực level 3, một chiếc nhẫn nhanh nhẹn level 2. Section order 14: Paragraph: Tất cả đều là đồ tốt. Section order 15: Paragraph: Xuân Thu thường thường sẽ may mắn hơn Xuân Hoa nhiều, thẻ vật phẩm trong tay nàng ta rất hay mở ra mấy thứ linh tinh kỳ quá...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 142.docx; chapter_title=Chương 142: Kế hoạch tác chiến; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=119 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
