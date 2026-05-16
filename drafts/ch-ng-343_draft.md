# Draft Knowledge: Chương 343

- source_id: ingest-01122f48ea814b83
- raw_file: raw/Chương 343.docx
- status: draft
- ingest_mode: local
- confidence: 0.17
- promotion_status: review_needed
- review_reason: low_confidence
- perception_version: enterprise_ingest_perception_v2
- document_type: text_document
- document_purpose: general_knowledge_source

## Business Summary
Section order 1: Paragraph: Trấn An Ca chương 343, Ấn Tích Tụ chương 349 Filename: Chương 343.docx Chapter title: Chương 343

## Document Purpose
- purpose: general_knowledge_source
- confidence: 0.35
- signals: none

## Key Topics
- section
- title
- paragraph
- order
- filename

## Extracted Knowledge Signals
### Entities
- Filename
- Chapter
- Section
- Paragraph
- An Ca

### Modules
- none

### Errors
- none

### Processes
- none

## Perception Pipeline
- document_type: text_document
- document_type_confidence: 0.78
- signals: docx_container, paragraphs
- native_structured: confidence=0.80
- ocr: confidence=0.00
- vision_layout: confidence=0.22
- document_classifier: confidence=0.78
- provider_semantic: confidence=0.00

## Provider Assistance
- used=False; status=skipped; selected=; fail_count=0; latency_ms=0; token_estimate=0

## Possible Queries
- explain Chương 343
- summarize Chương 343
- what is section
- what is title
- what is paragraph

## Extracted Source Text
Filename: Chương 343.docx Chapter title: Chương 343 Section count: 1 Section order 1: Paragraph: Trấn An Ca chương 343, Ấn Tích Tụ chương 349

## Provenance
Raw extraction trace kept separate from business summary.
- metadata: method=docx_core_metadata; confidence=0.72; evidence=filename=Chương 343.docx; chapter_title=Chương 343; ref=docProps/core.xml
- headings: method=docx_heading_parse; confidence=0.22; evidence=0 heading blocks; ref=word/document.xml#w:p
- text: method=docx_paragraph_parse; confidence=0.80; evidence=1 paragraph blocks; ref=word/document.xml#w:p
- lists: method=docx_list_parse; confidence=0.22; evidence=0 list items; ref=word/document.xml#w:numPr
- tables: method=docx_table_parse; confidence=0.22; evidence=0 table rows; ref=word/document.xml#w:tbl

## Trust Notice
This draft is not trusted wiki knowledge until explicitly approved or promoted by governed workflow.
