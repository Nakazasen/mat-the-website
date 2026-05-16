# Draft Knowledge: Chương 189

- source_id: ingest-15e1abf52cce62bf
- raw_file: raw/Chương 189.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Hàn Phong nhìn thái độ này của nàng ta, cũng xem như tương đối hài lòng. Chiến trường Thanh Lâm có một người thiên hướng phòng thủ an ổn như Kha Thành, một người thiên hướng tấn công dũng mãnh như Châu Lam, hai người hiệp đồng trấn thủ, vậy là đạt thành cân bằng nhất định. Section order 7: Paragraph: Châu Lam khuôn mặt hơi phiếm hồng, lời nói của Hàn Phong để nàng có chút suy nghĩ lung tung, nhưng rất nhanh đã gạt cảm giác kỳ quái qua một bên, tiến hành cởi bỏ Áo K...

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
- Thanh
- Kha

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
- explain Chương 189
- summarize Chương 189
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 189.docx Chapter title: Chương 189: Dò xét Áo Khoác Phòng Hộ. Section count: 81 Section order 1: Heading: Chương 189: Dò xét Áo Khoác Phòng Hộ. Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong nhìn thái độ này của nàng ta, cũng xem như tương đối hài lòng. Chiến trường Thanh Lâm có một người thiên hướng phòng thủ an ổn như Kha Thành, một người thiên hướng tấn công dũng mãnh như Châu Lam, hai người hiệp đồng trấn thủ, vậy là đạt thành cân bằng nhất định. Section order 4: Paragraph: Sự cân bằng này sẽ đem đến hiệu quả hắn muốn thấy. Section order 5: Paragraph: Hắn thản nhiên chìa tay ra nói: Section order 6: Paragraph: - Tốt, một lát nữa cô hãy trở lại tiền tuyến bảo hộ đội viên dưới trướng. Giờ thì cởi áo ra đi. Section order 7: Paragraph: Châu Lam khuôn mặt hơi phiếm hồng, lời nói của Hàn Phong để nàng có chút suy nghĩ lung tung, nhưng rất nhanh đã gạt cảm giác kỳ quái qua một bên, tiến hành cởi bỏ Áo Khoác Phòng Hộ level 4 ra. Section order 8: Paragraph: Hàn Phong cầm vật phẩm này trên tay, nó thoáng cái đã trở nên trong suốt không màu, hắn lập tức nhướng mày vì sự thay đổi kỳ lạ. Section order 9: Paragraph: 3 lượt sử dụng kỹ năng vẫn còn nguyên, chỉ là mỗi lượt sử dụng bị giảm mất 18 giây duy trì. Section order 10: Paragraph: Hắn kỳ quái hỏi Châu Lam: Section order 11: Paragraph: - Vừa rồi trang bị này làm sao kích hoạt? Section order 12: Paragraph: Châu Lam nhanh chóng đem toàn bộ quá trình diễn biến chiến đấu đều thuật lại cho Hàn Phong. Từ việc F2 điên cuồng tấn công nhưng đều bị hào quang vàng nhạt chặn lại, cảm giác đ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 189.docx; chapter_title=Chương 189: Dò xét Áo Khoác Phòng Hộ.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=80 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
