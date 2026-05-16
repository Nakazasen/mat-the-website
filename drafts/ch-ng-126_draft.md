# Draft Knowledge: Chương 126

- source_id: ingest-9909a71da6ac2dba
- raw_file: raw/Chương 126.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Hàn Phong bước vào nhìn từng dãy súng AK74 trên vách tường mà vô cùng vui mừng. Nơi này có ít nhất 100 khẩu AK74 phiên bản cải tiến, ngoài ra còn có quân phục chiến đấu, lưỡi lê, xẻng quân dụng các loại. Section order 19: Paragraph: Ở trong một căn phòng, 10 khẩu đại liên RPD 7.62mm đang được các đội viên vận chuyển ra ngoài, ngoài ra còn có 4 khẩu súng chống tăng RPG-7 to như cổ chân người trưởng thành. Section order 37: Paragraph: Vật này gọi là Drone, tên thông...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- quan

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Phong
- Trong
- Ba

### Modules
- none

### Errors
- 531 c
- 531 n

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
- explain Chương 126
- summarize Chương 126
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 126.docx Chapter title: Chương 126: Hàn thủ lĩnh của chúng tôi Section count: 110 Section order 1: Heading: Chương 126: Hàn thủ lĩnh của chúng tôi Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong dâng lên tinh thần, lập tức xoay người chạy về bên kia. Section order 4: Paragraph: Trong một nhà kho, hai cái xác thây ma đã bị chém ch.ết nằm đó. Ba đội viên đang liên tiếp lôi các thùng chứa bằng sắt ra giữa phòng. Section order 5: Paragraph: Hàn Phong bước vào nhìn từng dãy súng AK74 trên vách tường mà vô cùng vui mừng. Nơi này có ít nhất 100 khẩu AK74 phiên bản cải tiến, ngoài ra còn có quân phục chiến đấu, lưỡi lê, xẻng quân dụng các loại. Section order 6: Paragraph: Từng thùng sắt được mở ra, bên trong là hàng dài các viên đạn 7.62mm sắp xếp chỉnh tề. Mỗi thùng có tới 2000 viên, mà nơi này có tới mười mấy thùng. Section order 7: Paragraph: - Tốt, tốt, haha. Từ Thôi, cho người vận chuyển hết số quân trang này ra ngoài. Section order 8: Paragraph: - Tuân lệnh. Section order 9: Paragraph: Từ Thôi bắt đầu cho đội viên tiến vào, đem súng đạn vận chuyển ra ngoài xếp lên xe tải. Section order 10: Paragraph: Dù nơi này nhiều súng đạn, nhưng Hàn Phong vẫn chưa được thoả mãn khẩu vị, hắn vung tay kêu lên: Section order 11: Paragraph: - Tiếp tục tìm kiếm cho tôi. Section order 12: Paragraph: Hắn quay lại toà nhà chỉ huy trung tâm, chỉ đạo đội viên dưới trướng bắt đầu thu hết mớ tài liệu lại. Section order 13: Paragraph: Đây đều là tài liệu huấn luyện binh lính giai đoạn tân binh, huấn luyện chó nghiệp vụ, huấn luyện kỹ chiến thuật phối...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 126.docx; chapter_title=Chương 126: Hàn thủ lĩnh của chúng tôi; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=109 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
