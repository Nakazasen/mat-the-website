from backend.routes.reader_lookup_rules import build_rule_based_lookup


def test_build_rule_based_lookup_returns_english_phrasal_verb():
    payload = build_rule_based_lookup("en", "make sure")

    assert payload is not None
    assert payload["meaning_vi"] == "đảm bảo, chắc chắn"
    assert payload["reading"] == "/meɪk ʃʊr/"
    assert payload["source"] == "rule_based"


def test_build_rule_based_lookup_returns_japanese_reading():
    payload = build_rule_based_lookup("ja", "誠実")

    assert payload is not None
    assert payload["reading"] == "せいじつ"
    assert payload["meaning_vi"] == "chân thành; thành thật"


def test_build_rule_based_lookup_returns_chinese_pinyin():
    payload = build_rule_based_lookup("zh-CN", "牛乳")

    assert payload is not None
    assert payload["reading"] == "niú rǔ"
    assert payload["meaning_vi"] == "sữa bò"


def test_build_rule_based_lookup_uses_kana_fallback_for_reading_only():
    payload = build_rule_based_lookup("ja", "しかし")

    assert payload is not None
    assert payload["reading"] == "しかし"
    assert payload["meaning_vi"] == "nhưng; tuy nhiên"
