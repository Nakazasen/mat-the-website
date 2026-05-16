# Draft Knowledge: Chương 381

- source_id: ingest-2ed90b2afe737712
- raw_file: raw/Chương 381.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 10: Paragraph: Chưa bao giờ trấn Hi Vọng mạnh mẽ như lúc này. Những người phía dưới đều có cấp độ thấp nhất đạt tới level 13, ngang với Hàn Phong thời điểm bắt đầu diễn ra trận chiến tại ba đại lộ. Bọn họ có 16 tiểu đội trưởng, 2 phó đội trưởng, và chính bản thân Hàn Phong. Nếu một lần nữa đối diện thi đàn 7 vạn tại Xuân Lê, không cần pháo 2a28 trên bọc thép BMP-1 yểm trợ thì bọn họ vẫn có khả năng chiến thắng như thường. Section order 22: Paragraph: Đây là tin xấu, nhưng cũng c...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- trong
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Trong
- Phong
- Hi

### Modules
- none

### Errors
- 5000 exp
- 437 cu

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
- explain Chương 381
- summarize Chương 381
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 381.docx Chapter title: Chương 381 Section count: 72 Section order 1: Heading: Chương 381 Section order 2: Paragraph: 10–13 minutes Section order 3: Paragraph: Trong phòng họp, không khí trao đổi cũng đang tương đối nhộn nhịp. Section order 4: Paragraph: Lần đầu tiên những tiểu đội trưởng này tự mình tách ra hoạt động trong cả một ngày dài, tất nhiên sẽ có nhiều chuyện để nói, nhiều trải nghiệm để chia sẻ, nhiều tâm đắc để bàn luận. Section order 5: Paragraph: Cùng tác chiến một chỗ với Hàn Phong sẽ tương đối “an toàn”, nhưng tác chiến độc lập sẽ cho bọn họ cảm giác bản thân giống với một tiểu đội trưởng hơn, tự đưa ra quyết sách rồi tự giải quyết khó khăn sẽ hưng phấn hơn, có cảm giác làm chủ hơn, cũng là cơ hội để họ xây dựng và bồi dưỡng thế lực của riêng mình. Section order 6: Paragraph: Thấy Hàn Phong bước vào, hai mươi mấy người trong phòng đều dừng lại trao đổi rồi đồng loạt đứng lên cúi chào. Section order 7: Paragraph: - Thủ lĩnh. Section order 8: Paragraph: - Thủ lĩnh. Section order 9: Paragraph: Hàn Phong bước từng bước tiến về phía ghế chủ vị rồi ngồi xuống. Hắn lần lượt đáp lại ánh mắt của từng người một, có hưng phấn, có kỳ vọng, có hồi hộp, có cuồng nhiệt, có kính sợ… Muôn vàn trạng thái cảm xúc phức tạp đều được hắn thu lại, trong lòng không khỏi dâng lên vô tận cảm khái. Section order 10: Paragraph: Chưa bao giờ trấn Hi Vọng mạnh mẽ như lúc này. Những người phía dưới đều có cấp độ thấp nhất đạt tới level 13, ngang với Hàn Phong thời điểm bắt đầu diễn ra trận chiến tại ba đại lộ. Bọn họ có 16 tiểu đội trưởng, 2 phó đội trưởng, và chính bả...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 381.docx; chapter_title=Chương 381; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=71 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
