# Draft Knowledge: Chương 415

- source_id: ingest-61b80f18da028508
- raw_file: raw/Chương 415.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 4: Paragraph: Trấn Hi Vọng chưa hoàn toàn có được sự thống nhất này. Mặc dù mọi người đều dâng lên phẫn nộ với chính quyền Tam Giang, thế nhưng nó mới chỉ là phẫn nộ lướt qua khoảnh khắc, chưa đụng tới lợi ích của ai, chưa tới mức tức giận tột cùng, chưa chạm tới ngòi nổ cần thiết để khởi đầu "chiến tranh". Section order 7: Paragraph: Chiếm đại nghĩa rồi mới hành động là cách làm đúng, nhưng chỉ phù hợp khi có những bên khác đứng ngoài quan sát. Ví dụ A và B đánh nhau, C và D đứ...

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
- Section
- Heading
- Paragraph
- Hi
- Tam Giang
- A

### Modules
- none

### Errors
- 415

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
- explain Chương 415
- summarize Chương 415
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 415.docx Chapter title: Chương 415 Section count: 57 Section order 1: Heading: Chương 415 Section order 2: Paragraph: 10–12 minutes Section order 3: Paragraph: Hoà bình, không chỉ cần làm cho địch yếu ta mạnh, còn cần làm cho ta đã mạnh lại càng mạnh, mạnh từ vật chất đến ý thức, phải kết nối quan điểm trên dưới một lòng, thống nhất lý tưởng trong cả cao tầng lẫn hạ tầng, có như vậy thì sức mạnh mới phát huy được tối đa. Section order 4: Paragraph: Trấn Hi Vọng chưa hoàn toàn có được sự thống nhất này. Mặc dù mọi người đều dâng lên phẫn nộ với chính quyền Tam Giang, thế nhưng nó mới chỉ là phẫn nộ lướt qua khoảnh khắc, chưa đụng tới lợi ích của ai, chưa tới mức tức giận tột cùng, chưa chạm tới ngòi nổ cần thiết để khởi đầu "chiến tranh". Section order 5: Paragraph: Không có chiến tranh, làm sao có được hoà bình đích thực. Nếu tiếp tục quá trình đàm phán và chơi chiêu, đó chính là hành động để cho địch nhân phát huy thế mạnh, tự khiến bản thân phơi bày điểm yếu của mình, không bao giờ trấn Hi Vọng thắng nổi một cuộc đấu trí khi đối phương nắm danh nghĩa của chính quyền trong tay. Section order 6: Paragraph: Ngô Soái là một trong ba người đứng đầu, hiện tại lại có tư tưởng trước tiên chơi trò tuyên truyền truyền thông, công kích tư tưởng, vận động hành lang trước, sau đó mới tiến hành phản kích trả đũa sau, đây không phải tư tưởng sai lầm, nhưng nó không phù hợp. Section order 7: Paragraph: Chiếm đại nghĩa rồi mới hành động là cách làm đúng, nhưng chỉ phù hợp khi có những bên khác đứng ngoài quan sát. Ví dụ A và B đánh nhau, C và D đứng ngoài quan sát, khi...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 415.docx; chapter_title=Chương 415; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=56 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
