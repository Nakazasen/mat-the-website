# Draft Knowledge: Chương 400

- source_id: ingest-315cfbc2ce46be45
- raw_file: raw/Chương 400.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Khi Hàn Phong tới bến thuyền loại biên bên bờ sông Lệ Giang, Lạc Thanh Thuỷ đúng là đang ở tại nơi này nghịch nước. Section order 7: Paragraph: Hàn Phong nhìn vẻ mệt mỏi chật vật của Lạc Thanh Thuỷ mà không nhịn được ác độc thầm nghĩ một chút. Dù sao cũng là người Tam Giang, tình báo nói nữ nhân này không có ý đồ tấn công trấn Hi Vọng nhưng ai mà biết nàng ta có đột nhiên dở chứng hay không. Nàng ta vô cùng có động cơ đó chứ, đó chính là mấy cái thuyền ở đây này. S...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- thuy
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Khi
- Phong
- Giang

### Modules
- none

### Errors
- 400
- 400: Ngu

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
- explain Chương 400
- summarize Chương 400
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 400.docx Chapter title: Chương 400: Nguỵ tạo Section count: 102 Section order 1: Heading: Chương 400: Nguỵ tạo Section order 2: Paragraph: 13–17 minutes Section order 3: Paragraph: Khi Hàn Phong tới bến thuyền loại biên bên bờ sông Lệ Giang, Lạc Thanh Thuỷ đúng là đang ở tại nơi này nghịch nước. Section order 4: Paragraph: Ân, hay chính xác hơn là nghịch thuyền, nàng ta đang thao túng dòng nước phía dưới mạn thuyền để tạo động lực gián tiếp thao túng những con thuyền này. Không biết nàng ta đã vác thêm 2 cái cano nhỏ từ đâu tới, hợp với 5 chiếc thuyền có sẵn tại bến phà này, tổ hợp lại thành một đội thuyền 7 chiếc. Section order 5: Paragraph: Từng chiếc chạy ngang chạy dọc trên mặt nước giống như đang tập luyện chiến trận gì đó, khi thì hợp lại, khi thì tách ra, khi thì vòng quanh nhau vây kín một chiếc ở giữa, khi thì đan xéo vẫy vùng như thể cá vược leo thác... Nói chung nhìn cái khuôn mặt lấm tấm mồ hôi kia là đủ biết nghịch ngợm ba cái thứ đồ quỷ này vô cùng tốn sức. Section order 6: Paragraph: "Có nên giáng cho một đòn thật mạnh, nhân cơ hội này giết quách ả này đi không nhỉ... Hay chí ít là bắt trói lại, kiếm tí điều kiện đàm phán với bên kia..." Section order 7: Paragraph: Hàn Phong nhìn vẻ mệt mỏi chật vật của Lạc Thanh Thuỷ mà không nhịn được ác độc thầm nghĩ một chút. Dù sao cũng là người Tam Giang, tình báo nói nữ nhân này không có ý đồ tấn công trấn Hi Vọng nhưng ai mà biết nàng ta có đột nhiên dở chứng hay không. Nàng ta vô cùng có động cơ đó chứ, đó chính là mấy cái thuyền ở đây này. Section order 8: Paragraph: Vừa rảnh tay là chạy qua nghị...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 400.docx; chapter_title=Chương 400: Nguỵ tạo; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=101 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
