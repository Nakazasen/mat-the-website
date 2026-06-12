import os
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone

def read_chapter_text_file(path: str) -> str:
    """Reads contents of raw chapter file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_chapter_file(path: str) -> Dict[str, Any]:
    """Parses filename and content into structured chapter dictionary."""
    filename = os.path.basename(path)
    # Match pattern chapter_XXXX.txt (case-insensitive)
    match = re.search(r'chapter_(\d+)\.txt', filename, re.IGNORECASE)
    if not match:
        raise ValueError(f"Filename does not match contract convention: {filename}")
    
    chapter_number = int(match.group(1))
    raw_text = read_chapter_text_file(path)
    
    lines = raw_text.splitlines()
    if not lines:
        return {
            "chapter_number": chapter_number,
            "title": "",
            "content": "",
            "source_path": os.path.abspath(path),
            "char_count": 0
        }
        
    title = lines[0].strip()
    content = "\n".join(lines[1:]).strip()
    
    return {
        "chapter_number": chapter_number,
        "title": title,
        "content": content,
        "source_path": os.path.abspath(path),
        "char_count": len(content)
    }

def load_new_chapters_from_folder(folder: str) -> List[Dict[str, Any]]:
    """Scans folder and returns parsed chapters sorted by chapter_number."""
    if not os.path.exists(folder):
        return []
        
    chapters = []
    for entry in os.scandir(folder):
        if entry.is_file() and entry.name.lower().startswith("chapter_") and entry.name.lower().endswith(".txt"):
            try:
                parsed = parse_chapter_file(entry.path)
                chapters.append(parsed)
            except Exception:
                # If a file is malformed, we still include it with errors in the main validation flow
                pass
    return sorted(chapters, key=lambda x: x["chapter_number"])

def validate_new_chapter_source(chapter: Dict[str, Any], current_last_chapter: int, strict: bool = True) -> Dict[str, Any]:
    """Validates chapter fields against ingestion contract requirements."""
    errors = []
    warnings = []
    
    chapter_num = chapter.get("chapter_number")
    title = chapter.get("title", "").strip()
    content = chapter.get("content", "").strip()
    
    # Rule 1: Check empty content
    if not content:
        errors.append("Chapter content is completely empty.")
    elif len(content) < 50:
        warnings.append(f"Chapter content is unusually short ({len(content)} characters).")
        
    # Rule 2: Check empty title
    if not title:
        errors.append("Chapter title is empty.")
    else:
        # Check if title chapter number matches the file chapter number
        title_num_match = re.search(r'(?:chương|chapter|chg|c\.?)\s*(\d+)', title, re.IGNORECASE)
        if title_num_match:
            title_num = int(title_num_match.group(1))
            if title_num != chapter_num:
                errors.append(f"Title chapter number ({title_num}) mismatch with file chapter number ({chapter_num}).")
                
    # Rule 3: Check bounds relative to historical data
    if chapter_num is not None:
        if chapter_num <= current_last_chapter:
            errors.append(f"Chapter number ({chapter_num}) is <= current last chapter ({current_last_chapter}). Overwriting historical data is blocked.")
            
    is_valid = len(errors) == 0
    return {
        "chapter_number": chapter_num,
        "title": title,
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings
    }

def build_new_chapter_manifest(chapters: List[Dict[str, Any]], current_last_chapter: int, strict: bool = True) -> Dict[str, Any]:
    """Compiles list of parsed chapters, runs validations, checks gaps and returns complete manifest report."""
    if not chapters:
        return {
            "status": "NO_SOURCE_FILES_FOUND",
            "ok": True,
            "write_required": False,
            "chapters_count": 0,
            "new_chapters": [],
            "validation_results": {},
            "gaps": [],
            "errors": []
        }
        
    validation_results = {}
    new_chapters = []
    errors = []
    
    all_numbers = [c["chapter_number"] for c in chapters]
    
    # Check duplicate chapter numbers in files
    seen = set()
    duplicates = set()
    for num in all_numbers:
        if num in seen:
            duplicates.add(num)
        seen.add(num)
        
    for ch in chapters:
        ch_num = ch["chapter_number"]
        val = validate_new_chapter_source(ch, current_last_chapter, strict=strict)
        
        # Add duplicate error if applicable
        if ch_num in duplicates:
            val["is_valid"] = False
            val["errors"].append(f"Duplicate chapter file found for chapter {ch_num}.")
            
        validation_results[str(ch_num)] = val
        if val["is_valid"]:
            new_chapters.append({
                "chapter_number": ch_num,
                "title": ch["title"],
                "char_count": ch["char_count"],
                "source_path": ch["source_path"]
            })
        else:
            errors.append(f"Chapter {ch_num} validation failed: {'; '.join(val['errors'])}")
            
    # Check sequence gaps starting from current_last_chapter + 1
    expected_next = current_last_chapter + 1
    gaps = []
    
    if all_numbers:
        # Check gap between current_last_chapter and first new chapter
        first_new = all_numbers[0]
        if first_new > expected_next:
            for missing in range(expected_next, first_new):
                gaps.append(missing)
                
        # Check gaps between new chapters
        for i in range(len(all_numbers) - 1):
            curr_num = all_numbers[i]
            next_num = all_numbers[i+1]
            if next_num > curr_num + 1:
                for missing in range(curr_num + 1, next_num):
                    gaps.append(missing)
                    
    if gaps:
        gap_msg = f"Sequence gaps detected. Missing chapters: {gaps}"
        if strict:
            errors.append(gap_msg)
            
    # Manifest status
    ok = len(errors) == 0
    status = "VALIDATION_PASSED" if ok else "VALIDATION_FAILED"
    
    return {
        "status": status,
        "ok": ok,
        "write_required": False,
        "chapters_count": len(chapters),
        "new_chapters": new_chapters,
        "validation_results": validation_results,
        "gaps": gaps,
        "errors": errors,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def normalize_chapter_title(text: str) -> str:
    """Normalizes the chapter title by removing HTML and extra spaces."""
    if not text:
        return ""
    cleaned = re.sub(r'<[^>]*>', '', text)
    return " ".join(cleaned.strip().split())

def validate_new_chapter_payload(
    chapter_number: int,
    title: str,
    content: str,
    current_last_chapter: int,
    strict: bool = True
) -> Dict[str, Any]:
    """Validates raw payload fields for a staging chapter submission."""
    errors = []
    warnings = []

    from backend.rag.chunking import strip_html_to_text, normalize_story_text

    clean_title = normalize_chapter_title(title)

    # Strip HTML and normalize content
    clean_content_text = strip_html_to_text(content)
    clean_content = normalize_story_text(clean_content_text)

    # 1. Content check
    if not clean_content:
        errors.append("Chapter content is completely empty.")
    elif len(clean_content) < 50:
        errors.append(f"Chapter content is unusually short ({len(clean_content)} characters).")

    # Check if original content had forbidden HTML tags or scripts
    has_script_or_handler = (
        re.search(r'(?is)<script\b[^>]*>', content) or
        re.search(r'(?i)href\s*=\s*[\'"]?\s*javascript:', content) or
        re.search(r'(?i)<[^>]*\bon[a-zA-Z]+\s*=[^>]*>', content)
    )
    
    from backend.security_utils import ALLOWED_HTML_TAGS
    # Find all tag names (e.g. <p>, </p>, <br/>, <img ...>)
    found_tags = re.findall(r'</?([a-zA-Z1-6]+)(?:\s|/|>)', content)
    has_forbidden_tag = any(t.lower() not in ALLOWED_HTML_TAGS for t in found_tags)

    if has_script_or_handler or has_forbidden_tag:
        errors.append("HTML tags or script elements are detected and forbidden.")


    # 2. Title check
    if not clean_title:
        errors.append("Chapter title is empty.")
    else:
        # Check if title chapter number matches
        title_num_match = re.search(r'(?:chương|chapter|chg|c\.?)\s*(\d+)', clean_title, re.IGNORECASE)
        if title_num_match:
            title_num = int(title_num_match.group(1))
            if title_num != chapter_number:
                errors.append(f"Title chapter number ({title_num}) mismatch with chapter number ({chapter_number}).")
        else:
            warnings.append("Chapter title does not explicitly contain a chapter number (e.g. 'Chương XXX').")

    # 3. Chapter number checks
    if chapter_number <= current_last_chapter:
        errors.append(f"Chapter number ({chapter_number}) is <= current last chapter ({current_last_chapter}). Overwriting historical data is blocked.")

    # 4. Strict sequence gap checks
    if strict and chapter_number > current_last_chapter + 1:
        errors.append(f"Sequence gap detected: chapter {chapter_number} is submitted but next expected is {current_last_chapter + 1}.")

    is_valid = len(errors) == 0
    return {
        "chapter_number": chapter_number,
        "title": clean_title,
        "content": clean_content,
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings
    }
