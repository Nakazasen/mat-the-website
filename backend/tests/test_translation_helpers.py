import backend.main as main


def test_build_target_translation_locales_filters_duplicates_and_vi():
    locales = main.build_target_translation_locales(["vi", "en", "EN", "zh-cn", "ja", "ja"])

    assert locales == ["en", "zh-CN", "ja"]


def test_chunk_translation_source_text_preserves_all_content():
    source = ("Doan 1.\n\n" + ("abc " * 1200) + "\n\nDoan 2.\n\n" + ("xyz " * 1200)).strip()

    chunks = main.chunk_translation_source_text(source, max_chars=1200)

    assert len(chunks) > 1
    assert "".join(chunks).replace("\n", "").replace(" ", "") == source.replace("\n", "").replace(" ", "")


def test_parse_multilocale_translation_payload_reads_nested_translations():
    payload = """
    {
      "translations": {
        "en": { "title": "Hello", "content": "World" },
        "zh-CN": { "title": "你好", "content": "世界" },
        "ja": { "title": "こんにちは", "content": "世界" }
      }
    }
    """

    parsed = main.parse_multilocale_translation_payload(payload, ["en", "zh-CN", "ja"], ["title", "content"])

    assert parsed["en"]["title"] == "Hello"
    assert parsed["zh-CN"]["content"] == "世界"
    assert parsed["ja"]["title"] == "こんにちは"


def test_build_guide_translation_slug_uses_locale_suffix():
    assert main.build_guide_translation_slug("reader-guide", "zh-cn") == "reader-guide__zh-CN"
