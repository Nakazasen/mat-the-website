import pytest

from backend import main


@pytest.mark.asyncio
async def test_translate_chapter_payloads_retries_failed_large_chunk_by_splitting(monkeypatch):
    monkeypatch.setattr(main, "TRANSLATION_CHUNK_RETRY_MIN_CHARS", 40)
    monkeypatch.setattr(main, "TRANSLATION_CHUNK_RETRY_FANOUT", 2)
    monkeypatch.setattr(main, "build_glossary_prompt", lambda: "")
    calls = []
    source = "Doan mot rat dai de kich hoat retry.\n\nDoan hai cung du dai de tach nho."

    async def fake_generate_structured_translation_payload(**kwargs):
        calls.append(kwargs["user_prompt"])
        if len(calls) == 1:
            raise ValueError("context too large")
        return {
            "en": {
                "title": "Translated title",
                "content": f"translated-part-{len(calls) - 1}",
            }
        }

    monkeypatch.setattr(main, "generate_structured_translation_payload", fake_generate_structured_translation_payload)

    result = await main.translate_chapter_payloads_with_ai(
        title="Tieu de",
        content=source,
        source_locale="vi",
        target_locales=["en"],
        context_label="retry-test",
    )

    assert len(calls) >= 3
    assert result["en"]["title"] == "Translated title"
    assert "translated-part-1" in result["en"]["content"]
    assert "translated-part-2" in result["en"]["content"]
    assert result["en"]["sentence_alignment"]["chunk_count"] >= 2
