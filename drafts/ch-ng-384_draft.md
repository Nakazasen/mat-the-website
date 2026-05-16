# Draft Knowledge: Chương 384

- source_id: ingest-1f29be5cd3ee6b4c
- raw_file: raw/Chương 384.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Nhận được lệnh của hắn, Hương Vẫn Tình cúi đầu dạ một tiếng xoay người tiến vào đảo bếp, mà Xuân Hoa Xuân Thu cũng đồng thời cùng với nàng ta bắt tay chuẩn bị “đại tiệc”. Section order 4: Paragraph: Hàn Phong nhanh chóng thay ra trang phục chiến đấu rồi bước vào phòng tắm, sau khi hoàn thành thư giãn 15 phút, hắn trở ra ngoài rồi lại tiếp tục ngồi xuống bàn làm việc cạnh cửa sổ. Lam Nhu Thuỷ sớm sắp xếp xong tài liệu về bộ luật mới được sửa đổi bổ sung, nàng ta bắt...

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
- Hoa
- Thu
- Phong

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
- explain Chương 384
- summarize Chương 384
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 384.docx Chapter title: Chương 384: Hoàn thành bộ luật Section count: 51 Section order 1: Heading: Chương 384: Hoàn thành bộ luật Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Nhận được lệnh của hắn, Hương Vẫn Tình cúi đầu dạ một tiếng xoay người tiến vào đảo bếp, mà Xuân Hoa Xuân Thu cũng đồng thời cùng với nàng ta bắt tay chuẩn bị “đại tiệc”. Section order 4: Paragraph: Hàn Phong nhanh chóng thay ra trang phục chiến đấu rồi bước vào phòng tắm, sau khi hoàn thành thư giãn 15 phút, hắn trở ra ngoài rồi lại tiếp tục ngồi xuống bàn làm việc cạnh cửa sổ. Lam Nhu Thuỷ sớm sắp xếp xong tài liệu về bộ luật mới được sửa đổi bổ sung, nàng ta bắt đầu lần lượt giải thích vài điểm quan trọng cho Hàn Phong biết. Section order 5: Paragraph: Nội dung tổng thể vẫn duy trì phương thức phạt mạnh vào túi tiền như cũ, hiện tại được bổ sung thêm bằng việc đi sâu vào chi tiết của từng hành vi nhỏ, cùng với việc thành lập đội chấp pháp và phòng tư pháp để tiến hành xét xử. Section order 6: Paragraph: Ví dụ như hành vi gây rối trật tự công cộng sẽ chia ra 3 mức độ nhỏ một cách cụ thể. Mức 1 là hành vi gây rối bằng cách dùng tiếng động gây ồn ào, gây mất trật tự, hô hào cổ vũ quá khích… Hành vi này sẽ bị nhắc nhở và phạt hành chính từ 1-6 cống hiến, tương đương 2 đến 12 lạng gạo. Section order 7: Paragraph: Mức 2 là hành vi gây rối tương tự như mức 1 nhưng lại có sự tổ chức, cụ thể chính là tụ tập đông người, từ 3 người trở lên, gây cản trở hoạt động của cá nhân hoặc tập thể, gây kích động quần chúng... Mức phạt từ 6-24 cống hiến, tương đương nửa ngày lư...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 384.docx; chapter_title=Chương 384: Hoàn thành bộ luật; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=50 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
