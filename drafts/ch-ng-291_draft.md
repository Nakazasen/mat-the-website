# Draft Knowledge: Chương 291

- source_id: ingest-6d181fff54427395
- raw_file: raw/Chương 291.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Chương 291: Người từ huyện Tam Giang tới Section order 5: Paragraph: Thật ra điều này khó trách Quan Bình. Thời điểm hai bên liên lạc, đúng là Hàn Phong chỉ nhận được trang thiết bị từ trung tâm huấn luyện chó nghiệp vụ, nhưng sau đó hắn vẫn tiến hành bít chặn thông tin, độc đoán bộ đàm radio liên lạc, hai bên có đào móc được tình báo gì gì thì cũng không thể thông báo cho nhau. Section order 6: Paragraph: Lạc Thanh Thuỷ thì không có quá nhiều bận tâm. Nàng lười nghĩ...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- giang
- trong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Tam Giang
- Section
- Heading
- Paragraph
- Quan
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
- explain Chương 291
- summarize Chương 291
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 291.docx Chapter title: Chương 291: Người từ huyện Tam Giang tới Section count: 66 Section order 1: Heading: Chương 291: Người từ huyện Tam Giang tới Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Nhiệm vụ thứ nhất của nam tử kính gọng vàng trong lần dẫn quân qua Liễu Lâm chính là thu về súng ống đạn dược, đặc biệt là đạn dược, bọn họ cần thêm đạn để đối phó với thi đàn tại chiến trường Diệu Liên. Hiện tại không có đạn, nhiệm vụ này coi như hỏng rồi. Section order 4: Paragraph: Hắn lại thêm một lần nữa cảm giác tình báo của Quan Bình kia quá mức ngu xuẩn. Không phải gã nói lũ thổ phỉ kia chỉ nhận được trang bị từ khu huấn luyện chó nghiệp vụ sao, tại sao hiện tại lại thành đã lấy cả trang thiết bị tại đây từ lâu rồi? Section order 5: Paragraph: Thật ra điều này khó trách Quan Bình. Thời điểm hai bên liên lạc, đúng là Hàn Phong chỉ nhận được trang thiết bị từ trung tâm huấn luyện chó nghiệp vụ, nhưng sau đó hắn vẫn tiến hành bít chặn thông tin, độc đoán bộ đàm radio liên lạc, hai bên có đào móc được tình báo gì gì thì cũng không thể thông báo cho nhau. Section order 6: Paragraph: Lạc Thanh Thuỷ thì không có quá nhiều bận tâm. Nàng lười nghĩ về súng ống đạn dược, nàng chỉ quan tâm tới 5 chiếc thuyền đang đỗ dưới bến cảng, đó chính là mục tiêu mà nàng vô cùng mong muốn. Bất quá chúng nó đều đã thuộc sở hữu của vị tên là Hàn Phong Hàn thủ lĩnh kia, làm sao để đối phương chịu nhả ra bây giờ? Section order 7: Paragraph: Đối phương dường như không biết sử dụng thuyền, mấy chiếc thuyền từ đầu tới cuối đều neo đậu, không có vai trò quá lớn đ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 291.docx; chapter_title=Chương 291: Người từ huyện Tam Giang tới; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=65 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
