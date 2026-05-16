# Draft Knowledge: Chương 81

- source_id: ingest-8ddc1d909775d518
- raw_file: raw/Chương 81.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 81: Công bằng Section order 7: Paragraph: Châu Lam vẫn không hề muốn buông tha, ánh mắt thanh thuần của nàng ta nhìn thẳng Quan Bình, lạnh lùng hỏi: Section order 14: Paragraph: - Vậy thì không biết liệu căn cứ chính phủ bên phía huyện Tam Giang sẽ cử bao nhiêu người tới cứu chúng tôi?

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
- Quan

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
- explain Chương 81
- summarize Chương 81
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 81.docx Chapter title: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 81: Công bằng Section count: 118 Section order 1: Heading: Mạt Thế - Sinh Hoá Nguy Cơ - Chương 81: Công bằng Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Lời này vừa ra, không khí trở nên có chút lắng lại. Section order 4: Paragraph: Quan Bình trên đầu đổ mồ hôi lạnh, khoé mắt cũng có chút co giật. Section order 5: Paragraph: Hắn nuốt khan một ngụm nước bọt, chậm rãi nói: Section order 6: Paragraph: - Chúng tôi muốn trước tiên tìm hiểu tình huống, sau đó sẽ cử thêm quân số tăng cường đến. Section order 7: Paragraph: Châu Lam vẫn không hề muốn buông tha, ánh mắt thanh thuần của nàng ta nhìn thẳng Quan Bình, lạnh lùng hỏi: Section order 8: Paragraph: - Và kết quả của quyết định đó làm một căn cứ gần trăm người bị thây ma tàn sát? Im lặng, hoàn toàn im lặng. Section order 9: Paragraph: Những người ở đây tuy cũng có người ngu, nhưng không có người nào đần cả. Đoạn hội thoại vừa rồi, bọn họ có thể tưởng tượng ra chính phủ cũng không mạnh như lời kể. Section order 10: Paragraph: Thậm chí chính phủ cũng không phải rất quan tâm tới mấy căn cứ người sống sót như vậy. Section order 11: Paragraph: Quan Bình nắm chặt tay, sau đó kiên trì đáp lại: Section order 12: Paragraph: - Có rất nhiều căn cứ người sống sót cầu cứu, chúng tôi không thể tập trung ứng cứu toàn bộ, buộc phải phân tán ra… Section order 13: Paragraph: Châu Lam là diễn viên, mấy cái vụ dồn ép tâm lý này tiếp xúc rất thường xuyên, lúc này tiếp tục lên tiếng truy vấn: Section order 14: Paragraph: - Vậy thì không biết liệ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 81.docx; chapter_title=Mạt Thế - Sinh Hoá Nguy Cơ - Chương 81: Công bằng; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=117 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
