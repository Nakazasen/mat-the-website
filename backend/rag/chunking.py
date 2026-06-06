"""
RAG Chunking Module
Provides text cleanup, normalization, token estimation, and chunking functions.
"""

import hashlib
import html as html_lib
import re

def strip_html_to_text(html: str) -> str:
    """Removes HTML tags, including <script> and <style> sections, and unescapes entities."""
    if not html:
        return ""
    
    # 1. Remove script/style tags and contents
    text = re.sub(r"(?is)<script\b[^>]*>.*?</script>", "", html)
    text = re.sub(r"(?is)<style\b[^>]*>.*?</style>", "", text)
    
    # 2. Convert common block level breaks to newlines
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = re.sub(r"(?i)</div\s*>", "\n\n", text)
    text = re.sub(r"(?i)</td>", " \t ", text)
    text = re.sub(r"(?i)</tr>", "\n", text)
    
    # 3. Strip all other tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # 4. Decode HTML entities
    text = html_lib.unescape(text)
    
    return text.strip()

def normalize_story_text(text: str) -> str:
    """Standardizes newlines and spaces, removing double spacing while preserving paragraphs."""
    if not text:
        return ""
        
    # Standardize line endings
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Collapse multiple consecutive newlines to double newlines (paragraph boundary)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    
    # Clean whitespace line by line to preserve newlines but collapse spacing
    lines = []
    for line in normalized.split("\n"):
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)
        
    result = "\n".join(lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()

def estimate_token_count(text: str) -> int:
    """Estimates token count of a given text string based on character and word averages."""
    if not text:
        return 0
    # Average character length of 1 token in Vietnamese/English is ~3.8 characters
    # Alternatively, 1 token is ~1.25 syllables (words in space-split list)
    char_estimate = len(text) / 3.8
    word_estimate = len(text.split()) * 1.25
    return max(1, int((char_estimate + word_estimate) / 2))

def chunk_text(text: str, max_chars: int = 3500, overlap_chars: int = 450) -> list[str]:
    """
    Splits text into chunks of at most max_chars, trying to align with paragraphs or sentences.
    Ensures overlap_chars of overlap between consecutive chunks.
    """
    if not text:
        return []
        
    if overlap_chars >= max_chars:
        overlap_chars = max_chars // 2
        
    # Split text into paragraphs first
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]
            
    chunks = []
    current_chunk_parts = []
    current_len = 0
    
    for para in paragraphs:
        # If a single paragraph exceeds max_chars, split it by sentence
        if len(para) > max_chars:
            # Flush current chunk
            if current_chunk_parts:
                chunks.append("\n\n".join(current_chunk_parts))
                current_chunk_parts = []
                current_len = 0
                
            # Split paragraph into sentences
            sentence_ends = r"(?<=[.!?。！？])\s+"
            sentences = re.split(sentence_ends, para)
            
            sub_chunk_parts = []
            sub_len = 0
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(sentence) > max_chars:
                    # Flush whatever sub chunk we have
                    if sub_chunk_parts:
                        chunks.append(" ".join(sub_chunk_parts))
                        sub_chunk_parts = []
                        sub_len = 0
                        
                    # Split by hard character count
                    start = 0
                    while start < len(sentence):
                        end = min(start + max_chars, len(sentence))
                        chunks.append(sentence[start:end])
                        start += max_chars - overlap_chars
                else:
                    if sub_len + len(sentence) + (1 if sub_chunk_parts else 0) > max_chars:
                        # Flush sub-chunk
                        chunks.append(" ".join(sub_chunk_parts))
                        
                        # Generate overlap from previous sentences
                        overlap_parts = []
                        overlap_len = 0
                        for s in reversed(sub_chunk_parts):
                            if overlap_len + len(s) + (1 if overlap_parts else 0) <= overlap_chars:
                                overlap_parts.insert(0, s)
                                overlap_len += len(s) + 1
                            else:
                                break
                        sub_chunk_parts = overlap_parts + [sentence]
                        sub_len = sum(len(s) for s in sub_chunk_parts) + len(sub_chunk_parts) - 1
                    else:
                        sub_chunk_parts.append(sentence)
                        sub_len += len(sentence) + (1 if len(sub_chunk_parts) > 1 else 0)
                        
            if sub_chunk_parts:
                current_chunk_parts = sub_chunk_parts
                current_len = sub_len
        else:
            # Normal paragraph chunking
            if current_len + len(para) + (2 if current_chunk_parts else 0) > max_chars:
                # Flush current chunk
                chunks.append("\n\n".join(current_chunk_parts))
                
                # Generate overlap from previous paragraphs
                overlap_parts = []
                overlap_len = 0
                for p in reversed(current_chunk_parts):
                    if overlap_len + len(p) + (2 if overlap_parts else 0) <= overlap_chars:
                        overlap_parts.insert(0, p)
                        overlap_len += len(p) + 2
                    else:
                        break
                
                current_chunk_parts = overlap_parts + [para]
                current_len = sum(len(p) for p in current_chunk_parts) + (len(current_chunk_parts) - 1) * 2
            else:
                current_chunk_parts.append(para)
                current_len += len(para) + (2 if len(current_chunk_parts) > 1 else 0)
                
    if current_chunk_parts:
        chunks.append("\n\n".join(current_chunk_parts))
        
    return [c.strip() for c in chunks if c.strip()]

def stable_content_hash(text: str) -> str:
    """Returns a stable SHA-256 hash of the input text."""
    if not text:
        return hashlib.sha256(b"").hexdigest()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
