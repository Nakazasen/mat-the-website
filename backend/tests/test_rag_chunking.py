import pytest
import re
from backend.rag.chunking import (
    strip_html_to_text,
    normalize_story_text,
    estimate_token_count,
    chunk_text,
    stable_content_hash,
)

# Test 1: strip_html_to_text removes script/style tags and keeps text
def test_strip_html_to_text_removes_tags():
    html_input = """
    <html>
        <head>
            <style>body { color: red; }</style>
            <script>alert("hello");</script>
        </head>
        <body>
            <div class="content">
                <p>Hello World!</p>
                <br/>
                <p>Mạt thế sinh hóa nguy cơ &amp; RAG.</p>
            </div>
        </body>
    </html>
    """
    cleaned = strip_html_to_text(html_input)
    assert "body { color: red; }" not in cleaned
    assert "alert(" not in cleaned
    assert "Hello World!" in cleaned
    assert "Mạt thế sinh hóa nguy cơ & RAG." in cleaned
    assert "<p>" not in cleaned

# Test 2: normalize_story_text handles spacing and newlines properly
def test_normalize_story_text_handles_spacing():
    dirty_text = "\n\n\nHello   World!\r\nThis is\t\ta test.\n\n\n\nNew paragraph."
    normalized = normalize_story_text(dirty_text)
    assert normalized.startswith("Hello World!")
    assert "This is a test." in normalized
    # Paragraph boundary should be a double newline
    assert "test.\n\nNew paragraph." in normalized
    # No triple newlines
    assert "\n\n\n" not in normalized

# Test 3: chunk_text does not return empty chunks
def test_chunk_text_no_empty_chunks():
    chunks = chunk_text("   \n\n  \n\n   ")
    assert len(chunks) == 0

# Test 4: chunk_text preserves important content
def test_chunk_text_preserves_content():
    text = "Paragraph 1 is very important.\n\nParagraph 2 contains vital keys.\n\nParagraph 3 is the end."
    chunks = chunk_text(text, max_chars=100, overlap_chars=10)
    
    # Reconstruct plain text to ensure no words were dropped
    combined = " ".join(chunks)
    assert "Paragraph 1 is very important." in combined
    assert "Paragraph 2 contains vital keys." in combined
    assert "Paragraph 3 is the end." in combined

# Test 5: chunk_text has overlap when text is long
def test_chunk_text_has_overlap():
    p1 = "Diệp Phàm nhặt khẩu súng lục trên mặt đất và nạp đạn."
    p2 = "Con tang thi từ từ tiến lại gần anh với tiếng gầm dữ dội."
    p3 = "Anh ngắm thẳng vào đầu con tang thi và bóp cò."
    
    text = f"{p1}\n\n{p2}\n\n{p3}"
    
    # Set max_chars so it splits, but overlap_chars is large enough to copy previous paragraph
    max_chars = 120
    overlap_chars = 60
    
    chunks = chunk_text(text, max_chars=max_chars, overlap_chars=overlap_chars)
    assert len(chunks) >= 2
    
    # The second chunk should overlap and contain parts of the first chunk
    # Specifically, paragraph 2 is overlap-copied or sentence-based
    overlap_found = False
    for i in range(len(chunks) - 1):
        # Check if some words from chunk i are in chunk i+1
        last_sentence_of_first = chunks[i].split("\n\n")[-1]
        first_sentence_of_second = chunks[i+1].split("\n\n")[0]
        if last_sentence_of_first in chunks[i+1] or first_sentence_of_second in chunks[i]:
            overlap_found = True
            break
    assert overlap_found

# Test 6: stable_content_hash is stable for same input
def test_stable_content_hash_stability():
    text = "Mạt Thế Sinh Hóa Nguy Cơ"
    hash1 = stable_content_hash(text)
    hash2 = stable_content_hash(text)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex length

# Test 7: stable_content_hash changes when content changes
def test_stable_content_hash_changes():
    hash1 = stable_content_hash("content A")
    hash2 = stable_content_hash("content B")
    assert hash1 != hash2

# Test 8: dry-run helper does not write to DB
@pytest.mark.asyncio
async def test_dry_run_no_db_write(monkeypatch):
    class MockArgs:
        dry_run = True
        write = True
        max_chars = 3500
        overlap_chars = 450
        
    class MockSupabase:
        def table(self, name):
            raise RuntimeError("Database write should not be called in dry-run mode!")
            
    from backend.scripts.build_story_chunks import process_chapter
    
    # Even if write=True, dry_run=True should prevent any DB calls
    # Mock supabase client that throws error if table() is called
    mock_sb = MockSupabase()
    monkeypatch.setattr("backend.scripts.build_story_chunks.supabase", mock_sb)
    
    # Run process_chapter, it should not raise the database error because it simulates dry-run
    chunks_count = await process_chapter(
        chapter_num=1,
        title="Test Chapter",
        content_html="<p>Test content</p>",
        args=MockArgs()
    )
    assert chunks_count == 1  # Should process correctly but not call DB
