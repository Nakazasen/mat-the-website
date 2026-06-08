# New Chapter Source Intake Contract

This document defines the formal contract and validation schema for ingestion of new story chapters into the RAG system.

## Supported Input Formats

The intake pipeline scans the directory `backend/data/new_chapters/` for chapter source files.

### 1. File Naming Convention
Files must be named using the pattern:
```
chapter_<4_digit_number>.txt
```
Examples:
- `chapter_0830.txt`
- `chapter_0831.txt`

### 2. Content Structure
Each file must contain plain text formatted as follows:
- **First Line**: The exact chapter title (e.g. `Chương 830: Diệp Phàm thức tỉnh`).
- **Subsequent Lines**: The clean text body of the chapter. No HTML markup, script tags, or styling elements should be present.

### 3. Metadata Fields (Parsed & Built in Manifest)
Every verified chapter maps to the following payload schema:
- `chapter_number`: Integer parsed from the filename.
- `title`: String parsed from the first line of the file.
- `content`: Full text content of the chapter excluding the first line.
- `source_path`: Absolute or relative path of the source file.
- `char_count`: Length of content in characters.
- `imported_at`: ISO datetime string of the verification run.

---

## Validation & Safety Rules

To protect the integrity of the RAG database, the pipeline enforces the following validation constraints:

1. **Content Validity**: Chapter files must not be empty. Content must have at least 50 characters to prevent placeholder inputs.
2. **Title Pattern**: The first line must start with a valid chapter title pattern (e.g. `Chương \d+` or `Chapter \d+`) matching the chapter number.
3. **No Historical Overwrite**: The chapter number must be strictly greater than the current last chapter in the database (`current_last_chapter`, e.g. 829), unless explicit override options are passed.
4. **Sequence Gap Detection (Strict Mode)**: New chapters must form a continuous sequence starting exactly at `current_last_chapter + 1`. Gaps (e.g. trying to load chapter 831 without chapter 830) are rejected in strict mode.
5. **No Duplicates**: Duplicate chapter files within the intake folder are rejected.
6. **Bypass / Safety Boundaries**:
   - No automatic third-party web scrapers or crawler tools are executed.
   - No LLM calls or embedding generations are performed during validation.
   - No database writes or modifications to `wiki_entries` or `provisional_library` are allowed.
