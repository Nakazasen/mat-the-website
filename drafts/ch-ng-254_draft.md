# Draft Knowledge: Chương 254

- source_id: ingest-1b878a8382035e5b
- raw_file: raw/Chương 254.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 8: Paragraph: Thời điểm Tường Vi nói ra câu này, Hàn Phong trong không khỏi xuất hiện cảm giác hưng phấn. Cái thiếu nữ Đường Hạ Dao này thật sự đúng là quý nhân của hắn mà. Section order 55: Paragraph: - Anh… Anh dám… Section order 60: Paragraph: Trong xe quả nhiên lâm vào im lặng kéo dài, không khí cũng có chút ngượng ngùng cùng lúng túng. Hàn Phong khoé miệng cười lạnh, ả này đã bị hắn làm mềm rồi.

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
- Vi
- Hi

### Modules
- none

### Errors
- 5000

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
- explain Chương 254
- summarize Chương 254
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 254.docx Chapter title: Chương 254: Cò kè mặc cả Section count: 96 Section order 1: Heading: Chương 254: Cò kè mặc cả Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hàn Phong hơi nhướng mày một cái, hắn tâm tư xoay chuyển cực nhanh, trong đầu nghĩ một câu nói: Section order 4: Paragraph: “Tường Vi, trấn Hi Vọng chỉ còn dư lại 7000 viên đạn, không thể đem ra chuộc người nào cả. Chúng tôi còn phải phòng thủ tự vệ, không thể rải đạn làm chuyện vô ích.” Section order 5: Paragraph: Tường Vi tất nhiên đọc được suy nghĩ này, nàng ta vẫn khẳng định nói nhỏ: Section order 6: Paragraph: - Nàng rất xinh đẹp, anh không thấy thương tiếc sao? Hãy cứu tất cả các nàng đi… Không cần lo lắng. Section order 7: Paragraph: “Thành công!” Section order 8: Paragraph: Thời điểm Tường Vi nói ra câu này, Hàn Phong trong không khỏi xuất hiện cảm giác hưng phấn. Cái thiếu nữ Đường Hạ Dao này thật sự đúng là quý nhân của hắn mà. Section order 9: Paragraph: Đè nén cảm giác trong lòng xuống, hắn quay qua nói với Đổng Thành: Section order 10: Paragraph: - Nữ tử này, 2000 viên đạn. Section order 11: Paragraph: Đổng Thành nghe cái giá này thiếu chút đã chửi ra thành tiếng. 2000 viên? Có bấy nhiêu mà cũng đòi đổi? Hắn lập tức nhấn tay xuống bàn rồi nói: Section order 12: Paragraph: - Ít nhất phải một vạn. 9 trinh nữ này là hàng tặng kèm, tôi đồng ý để lại cho anh giá 5000, tổng cộng 1,5 vạn viên đạn cho cả 10 người. Section order 13: Paragraph: Hàn Phong lắc lắc đầu đáp: Section order 14: Paragraph: - Đổng huynh đệ, các nàng dù sao cũng chỉ là nữ nhân, so với tì nữ c...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 254.docx; chapter_title=Chương 254: Cò kè mặc cả; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=95 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
