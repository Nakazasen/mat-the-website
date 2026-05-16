# Draft Knowledge: Chương 238

- source_id: ingest-0a1fe97e7290d73e
- raw_file: raw/Chương 238.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 5: Paragraph: Hắn đưa tay che miệng ngáp một tiếng rồi tuỳ tiện nói với hai người Xuân Hoa, Xuân Thu: Section order 9: Paragraph: Nữ tử đầu tiên là Liễu Huyên, rất quen mắt, hầu như ngày nào cũng gặp. Nữ tử thứ hai tương đối quen mắt, chính là cái Lam Nhu Thuỷ buổi chiều vừa tới, được Hà Tam dâng lên như “lễ vật”. Người còn lại Hàn Phong sắp sửa quên luôn tới nơi, chính là Hương Vẫn Tình có gương mặt xinh đẹp nhưng ánh mắt luôn luôn buồn thảm, người được hắn đổi lấy khi lần đầu...

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
- Hoa
- Thu

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
- explain Chương 238
- summarize Chương 238
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 238.docx Chapter title: Chương 238: Háo sắc hay táo bón. Section count: 80 Section order 1: Heading: Chương 238: Háo sắc hay táo bón. Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Hàn Phong cứ nghĩ đã giải quyết hết mọi việc quan trọng, hiện tại mới nhớ ra vẫn còn một cái phiền phức to đùng nữa chưa đụng tới, lại còn đang chờ sẵn trong phòng. Section order 4: Paragraph: Từ bao giờ lệnh cấm xâm nhập lại bị để ngoài tai như vậy? Section order 5: Paragraph: Hắn đưa tay che miệng ngáp một tiếng rồi tuỳ tiện nói với hai người Xuân Hoa, Xuân Thu: Section order 6: Paragraph: - Chuẩn bị cho tôi hai bình trà. Section order 7: Paragraph: - Dạ ~ Section order 8: Paragraph: Hàn Phong đưa tay mở cửa phòng bước vào, trong phòng vậy mà có sẵn tới ba người. Section order 9: Paragraph: Nữ tử đầu tiên là Liễu Huyên, rất quen mắt, hầu như ngày nào cũng gặp. Nữ tử thứ hai tương đối quen mắt, chính là cái Lam Nhu Thuỷ buổi chiều vừa tới, được Hà Tam dâng lên như “lễ vật”. Người còn lại Hàn Phong sắp sửa quên luôn tới nơi, chính là Hương Vẫn Tình có gương mặt xinh đẹp nhưng ánh mắt luôn luôn buồn thảm, người được hắn đổi lấy khi lần đầu tiên tiếp xúc thôn Xuân Lê. Section order 10: Paragraph: Trong căn phòng không phải rất lớn, ba người này đang trò chyện cùng nhau, thái độ tương đối hoà hợp cởi mở, thậm chí có chút vui vẻ giống như rất tâm đầu ý hợp. Section order 11: Paragraph: Hàn Phong không khỏi nghệt mặt ra rồi kêu ầm lên: Section order 12: Paragraph: - Các cô đang làm trò gì vậy? Section order 13: Paragraph: Thấy người tới là Hàn Phong, cả ba ngư...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 238.docx; chapter_title=Chương 238: Háo sắc hay táo bón.; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=79 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
