# Draft Knowledge: Chương 80

- source_id: ingest-03842b3a15199aef
- raw_file: raw/Chương 80.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 80: Dân chủ Section order 11: Paragraph: Quan Bình cũng là ánh mắt lấp loé, muốn chờ đợi cách mà Hàn Phong phán định. Section order 63: Paragraph: Vững chắc đến mức nào ư? Theo Quan Bình, chính phủ sẽ không có tiếng nói tại tổ chức này.

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- quan
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
- explain Chương 80
- summarize Chương 80
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 80.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 80: Dân chủ Section count: 90 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 80: Dân chủ Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong tuỳ ý ngồi đó, để mặc cho các đội viên tranh cướp tài nguyên. Tất nhiên hắn cũng có giới hạn, chỉ cần âm lượng của ai đó gay gắt một chút, hắn sẽ lập tức ra tay định đoạt. Section order 4: Paragraph: Mà lời nói của hắn hầu như không có bất kỳ ai phản bác. Section order 5: Paragraph: Tiếp theo tới báo cáo công tác của từng tiểu đội một. Trần Diệu Âm đã chờ từ lâu, nhanh chóng đứng lên nói: Section order 6: Paragraph: - Tôi muốn tăng khẩu phần ăn của đội viên đội dự bị. Không được ăn no, họ sẽ không được huấn luyện tốt, tới khi ra chiến trường cũng không phát huy được bao nhiêu tác dụng, tôi cũng không thể đồng ý cho họ xuất chiến. Section order 7: Paragraph: Đây là vấn đề rất quan trọng. Đội viên đội dự bị là nguồn máu mới cho mỗi một tiểu đội, nếu không có đội viên mới, bọn họ sẽ thu nạp được ít chiến công hơn. Section order 8: Paragraph: Mà kết quả của đứng bét liên tiếp trong bảng xếp hạng chiến công chính là tiểu đội bị giải tán, thành viên bị phân vào các tiểu đội khác. Section order 9: Paragraph: Ai mà muốn điều này cơ chứ. Section order 10: Paragraph: Nhưng tài nguyên phân phối đâu phải chỉ nói có liền có. Đội viên đội dự bị có hơn 30 người, tăng thêm bao nhiêu đều là con số khó nói. Ở đây quyền quyết định chỉ thuộc về một người, các tiểu đội trưởng đều đồng loạt hướng ánh mắt lên phía vị trí chủ vị. Section o...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 80.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 80: Dân chủ; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=89 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
