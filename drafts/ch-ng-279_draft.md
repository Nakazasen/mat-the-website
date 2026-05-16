# Draft Knowledge: Chương 279

- source_id: ingest-fd0416a1a3d30e6c
- raw_file: raw/Chương 279.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 25: Paragraph: Đó cũng là lý do hắn sắp xếp bọn họ ở đây, tách rời với cư dân trấn Hi Vọng. Một mặt là muốn ngăn đám người này tiếp cận được thông tin, tìm cách bỏ chạy qua Tam Giang, một mặt là hắn muốn gia tăng hơn nữa lực ảnh hưởng của bản thân lên họ rồi mới tiến hành trộn dân lại, từ đó pha loãng sự bất mãn có thể đang âm ỉ trong lòng tổ chức. Section order 29: Paragraph: Nghe những lời này của Hàn Phong, cư dân thôn Xuân Lê lại một lần nữa được trấn an, đồng thời trong lòn...

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
- Hi
- Nghe

### Modules
- none

### Errors
- 500 m
- 500 ng

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
- explain Chương 279
- summarize Chương 279
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 279.docx Chapter title: Chương 279: Trấn an Section count: 55 Section order 1: Heading: Chương 279: Trấn an Section order 2: Paragraph: 9–12 minutes Section order 3: Paragraph: Nếu để Hàn Phong biết những suy nghĩ trong đầu Triệu Nhược Pháp hiện tại, hắn khẳng định sẽ đỏ mặt rồi cắn răng vì xấu hổ. Section order 4: Paragraph: Hắn đánh chủ ý lên nữ tử kia là mang mục đích muốn tìm kiếm một cái vật thí nghiệm sát chiêu hợp tiêu chuẩn nhất. “Tự nguyện” không sợ hãi, rất có tính liên tục, từ đầu tới cuối không thay đổi suy nghĩ, còn có, ừm, không phản kháng… Cái này thật sự là có điểm thất đức, bất quá, mục đích chân chính tất nhiên là bao gồm cả việc chữa trị cho đối phương. Section order 5: Paragraph: “Được rồi, vì “nhân loại”…” Section order 6: Paragraph: 5 phút sau, Hàn Phong đã ngồi trên ô tô lên đường trở về trấn Hi Vọng. Section order 7: Paragraph: Cùng xe với hắn còn có thêm một cái nữ tử từ đầu tới cuối đều im lặng như tờ. Nghe Triệu Nhược Pháp nói, thi thoảng nàng ta sẽ phát điên, trạng thái tương đối tồi tệ. Section order 8: Paragraph: - Haizzz… Section order 9: Paragraph: Hàn Phong vừa nhìn nàng ta thì không khỏi âm thầm thở dài, hắn rốt cuộc biết tại sao Đổng Thành lại chơi đùa nàng ta tới mức phát điên. Section order 10: Paragraph: Nữ tử này quá đẹp. Section order 11: Paragraph: Thiếu nữ Triệu Băng Vũ vừa tròn 18 tuổi, vóc dáng thân hình không phải quá nổi bật, nhưng khuôn mặt thực sự giống như một búp bê thiên sứ. Mỗi đường nét đều vô cùng mềm mại thanh thuần, nhất là đôi mắt đen nhánh sâu thẳm kia, thật giống như cả bầu trời sao đang nhẹ nhàn...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 279.docx; chapter_title=Chương 279: Trấn an; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=54 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
