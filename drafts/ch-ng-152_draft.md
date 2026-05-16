# Draft Knowledge: Chương 152

- source_id: ingest-df006fea3a9f4c84
- raw_file: raw/Chương 152.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Sau khi rời đi phòng nuôi ớt, Hàn Phong tới thẳng khu huấn luyện tân binh. Section order 39: Paragraph: - Qua đại lộ Thanh Hà, đây là đại lộ đông thây ma nhất. Section order 40: Paragraph: Drone lại è è è bay qua đại lộ Thanh Hà, chỉ 7 phút sau, Lý Võ Lạc thao tác drone bay thấp xuống, sau đó hắn chỉ một cái thân ảnh trên màn hình rồi hỏi:

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- phong
- thao

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- F2
- Section
- Heading
- Paragraph
- Phong
- Sau

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
- explain Chương 152
- summarize Chương 152
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 152.docx Chapter title: Chương 152: Ám sát F2 (1) Section count: 113 Section order 1: Heading: Chương 152: Ám sát F2 (1) Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Đám y bác sĩ tại phòng vật tư đã lấy hơn 150 cân lương thực các loại rồi chia nhau, Hàn Phong khẳng định họ sẽ không còn cản trở gì quá kịch liệt nữa. Section order 4: Paragraph: Có khi vì chiến sự nguy nan, ngay ngày mai thôi là việc điều tr.a thử nghiệm kia của hắn sẽ có kết quả rồi. Section order 5: Paragraph: Sau khi rời đi phòng nuôi ớt, Hàn Phong tới thẳng khu huấn luyện tân binh. Section order 6: Paragraph: Trần Diệu Âm vẫn đang miệt mài gấp rút chỉ đạo các đội viên tiếp nhận huấn luyện cơ sở, thấy Hàn Phong bước tới, nàng ta ra hiệu cho một trợ giảng dưới trướng tiếp tục quản lý sau đó mới bước tới gần nghiêm người chào: Section order 7: Paragraph: - Đại đội trưởng. Section order 8: Paragraph: Hàn Phong gật đầu, nhanh chóng nói: Section order 9: Paragraph: - Tôi cần sự trợ giúp của cô. Section order 10: Paragraph: Sau khi trao đổi sơ qua một chút, cả hai nhanh chóng bước về phía sân trước. Section order 11: Paragraph: Nơi này đang có một chiếc xe bọc thép chờ sẵn. Section order 12: Paragraph: Ngô Soái và Lý Võ Lạc đã ngồi sẵn trên xe, sau khi hai người Hàn Phong tới, một binh lính bắt đầu khởi động xe, chiếc xe bọc thép lăn bánh chạy ra khỏi căn cứ. Section order 13: Paragraph: Ngồi trên xe, mấy người bắt đầu tranh thủ ăn bữa trưa. Section order 14: Paragraph: Bọn họ bây giờ mới có thời gian ăn bữa trưa. Cả bốn người đều đang gặm bánh mỳ được nhồi đầy các thể...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 152.docx; chapter_title=Chương 152: Ám sát F2 (1); ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=112 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
