# Draft Knowledge: Chương 450

- source_id: ingest-d98df1577b88518a
- raw_file: raw/Chương 450.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: meeting_minutes

## Business Summary
Section order 3: Paragraph: Đem việc của đám người Tam Giang ném ra sau đầu, Hàn Phong nhét bộ đàm vào túi đựng bên hông sau đó thong thả quay trở lại phòng họp trung tâm. Section order 15: Paragraph: Thật ra kỹ năng Thao Túng Hoả Diễm và kỹ năng Hoả Đao có rất nhiều khác biệt. Hay nói rộng ra, các kỹ năng thao túng rất khác với các kỹ năng công kích thuần tuý, ngay cả Thao Túng Hàn Băng của Hàn Phong cũng vậy. Section order 16: Paragraph: Thao Túng Hoả Diễm, người sử dụng sẽ linh hoạt hơn, c...

## Document Purpose
- purpose: meeting_minutes
- confidence: 0.47
- signals: minutes

## Key Topics
- section
- order
- paragraph
- giai
- phong

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Heading
- Paragraph
- Tam Giang
- Phong
- F2

### Modules
- none

### Errors
- 450
- 450: Chi

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
- explain Chương 450
- summarize Chương 450
- what is section
- what is order
- what is paragraph

## Extracted Source Text
Filename: Chương 450.docx Chapter title: Chương 450: Chiến công Section count: 113 Section order 1: Heading: Chương 450: Chiến công Section order 2: Paragraph: 18–22 minutes Section order 3: Paragraph: Đem việc của đám người Tam Giang ném ra sau đầu, Hàn Phong nhét bộ đàm vào túi đựng bên hông sau đó thong thả quay trở lại phòng họp trung tâm. Section order 4: Paragraph: Nơi này đang diễn ra tiết mục tranh đoạt quyền phân phối vật tư vô cùng khốc liệt. Section order 5: Paragraph: - Bản kỹ năng Hoả Đao tam giai này phải là của tiểu đội 7 chúng tôi, là do chúng tôi đánh rớt cơ mà. Section order 6: Paragraph: - Thế sao được, công lớn nhất là nhờ có đội viên tiểu đội 8 thi triển sa lầy, thành công giữ chân quái vật, các vị mới có cơ hội chém giết, làm sao có chuyện một mình độc chiếm a. Section order 7: Paragraph: - Triệu Tứ, nói vậy thì đội 9 của tôi cũng có công, nên nhớ thây ma F2 đó bị giết trên chiến hào số 9. Theo quy định, chúng tôi có công gây áp lực toàn thể. Section order 8: Paragraph: Âm thanh tranh luận càng lúc càng sôi nổi giữa Đào Đại Tư, Triệu Tứ và Sử Thắng. Ai cũng đều tỏ ra tương đối gấp gáp, muốn nhanh chóng đoạt quyền sở hữu kỹ năng Hoả Đao tam giai vào tay. Section order 9: Paragraph: Kỹ năng này phải nói là cực mạnh. Cho tới hôm nay mới có người đem nó thăng giai từ nhị giai lên tam giai, Hoả Đao liền phát ra hào quang chói lọi khiến cho bất kỳ ai cũng đều thèm muốn. Section order 10: Paragraph: Ở trạng thái cơ bản, một lượt kích hoạt của nó có thể triệu hồi 10 lưỡi đao lửa, những đao lửa này mang theo thuộc tính thiêu đốt liên tục, một khi cháy là sẽ...

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 450.docx; chapter_title=Chương 450: Chiến công; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.78; evidence=1 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=112 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
