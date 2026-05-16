# Draft Knowledge: Chương 180

- source_id: ingest-87984ab315ebef46
- raw_file: raw/Chương 180.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 7: Paragraph: Châu Lam bị Hàn Phong mắng thì không khỏi ngượng ngùng đỏ mặt. Nàng ta tiếp nhận tấm áo khoác trong suốt, bàn tay chợt khựng lại mất mấy giây, sau đó khuôn mặt nở một nụ cười càng thêm tươi tắn: Section order 14: Paragraph: Những người này lần lượt là Lưu Giang, Triệu Tứ, Long Hưu, Lê Tam Ba. Lưu Giang là tàn quân của Tam Lang hội, về sau đầu nhập dưới trướng Châu Lam, ba người còn lại là những đội viên vô cùng kỳ cựu, từng tham gia hành động dò xét cầu Lệ Giang cù...

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
- Lam
- Phong
- Giang

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
- explain Chương 180
- summarize Chương 180
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 180.docx Chapter title: Chương 180: Chúng ta là bạn! Section count: 74 Section order 1: Heading: Chương 180: Chúng ta là bạn! Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Châu Lam nghe được câu hỏi này thì hơi ngẩn ra, nàng ta nhanh chóng nở một nụ cười thật tươi rồi đáp lại: Section order 4: Paragraph: - Đại đội trưởng, ai cũng sẽ sợ ch.ết, nhưng ch.ết thế nào lại càng khiến người ta quan tâm hơn. Tôi hi vọng mình có thể định đoạt số phận của bản thân, có thể tự quyết định cái ch.ết cho mình, có thể mỉm cười hài lòng vì đã nỗ lực hết sức. Section order 5: Paragraph: Hàn Phong nhướng mày, hắn từ trong ngực móc ra một tấm áo khoác trong suốt ném cho nàng ta rồi nói: Section order 6: Paragraph: - Bớt đạo lý lại. Trước khi đánh hạ chủ lực thây ma trên đại lộ này, tôi chưa cho cô ch.ết. Section order 7: Paragraph: Châu Lam bị Hàn Phong mắng thì không khỏi ngượng ngùng đỏ mặt. Nàng ta tiếp nhận tấm áo khoác trong suốt, bàn tay chợt khựng lại mất mấy giây, sau đó khuôn mặt nở một nụ cười càng thêm tươi tắn: Section order 8: Paragraph: - Ân, tôi đã biết. Đại đội trưởng, cảm ơn anh. Section order 9: Paragraph: Hàn Phong híp mắt nhìn về phía xa xa thi đàn rồi lạnh nhạt nói: Section order 10: Paragraph: - Một lát nữa sẽ có một, hoặc hai thây ma tiến hoá chạy về phía này. Nhiệm vụ của cô là gắng sức ngăn cản ít nhất một con, tốt nhất ngăn cản cả hai, tuyệt đối không cho chúng nó tàn sát đội viên, rõ chưa? Section order 11: Paragraph: Châu Lam khuôn mặt hiện lên nét kiên định gật mạnh đầu nói: Section order 12: Paragraph: - Tôi đảm bảo sẽ ho...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 180.docx; chapter_title=Chương 180: Chúng ta là bạn!; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=73 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
