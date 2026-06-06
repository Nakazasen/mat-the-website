"""
RAG Context Builder Module
Transforms hybrid lexical retrieval results into formatted context blocks with structured citations.
"""

def build_citation(result: dict) -> str:
    """Builds a human-readable citation string from a retrieval result dictionary."""
    chapter_number = result.get("chapter_number")
    chapter_title = (result.get("chapter_title") or "").strip()
    chunk_index = result.get("chunk_index")

    parts = []
    if chapter_number is not None:
        parts.append(f"Chương {chapter_number}")
    if chapter_title:
        parts.append(chapter_title)

    citation = " - ".join(parts)
    if chunk_index is not None:
        if citation:
            citation += f" | chunk {chunk_index}"
        else:
            citation = f"chunk {chunk_index}"

    return citation

def trim_context_text(text: str, max_chars: int = 1200) -> str:
    """Trims text to at most max_chars, appending '...' if it is truncated without returning empty string."""
    if not text:
        return ""
    trimmed = text.strip()
    if not trimmed:
        return ""
    if len(trimmed) <= max_chars:
        return trimmed
    if max_chars <= 3:
        return trimmed[:max_chars]
    return trimmed[:max_chars - 3].rstrip() + "..."

def build_rag_context_block(
    results: list[dict],
    max_chunks: int = 5,
    max_chars_per_chunk: int = 1200,
    max_total_chars: int = 6000
) -> dict:
    """
    Builds a unified RAG context block with formatted citations from hybrid lexical search results.
    """
    if not results:
        return {
            "context_text": "",
            "citations": [],
            "chunks_used": 0,
            "total_chars": 0,
            "source": "story_chunks_hybrid_context"
        }

    blocks = []
    citations = []
    current_total_chars = 0

    for r in results[:max_chunks]:
        chapter_number = r.get("chapter_number")
        chapter_title = (r.get("chapter_title") or "").strip()
        chunk_index = r.get("chunk_index")
        content_hash = r.get("content_hash")

        content = r.get("content_plain") or r.get("content") or ""
        trimmed = trim_context_text(content, max_chars_per_chunk)

        block = f"[CHƯƠNG {chapter_number} - {chapter_title} | chunk {chunk_index}]\n{trimmed}"

        potential_separator = "\n\n" if blocks else ""
        potential_len = len(potential_separator) + len(block)

        if current_total_chars + potential_len <= max_total_chars:
            blocks.append(block)
            current_total_chars += potential_len
            citations.append({
                "chapter_number": chapter_number,
                "chapter_title": r.get("chapter_title"),
                "chunk_index": chunk_index,
                "content_hash": content_hash,
                "source": "story_chunks"
            })
        else:
            break

    context_text = "\n\n".join(blocks)

    return {
        "context_text": context_text,
        "citations": citations,
        "chunks_used": len(blocks),
        "total_chars": len(context_text),
        "source": "story_chunks_hybrid_context"
    }
