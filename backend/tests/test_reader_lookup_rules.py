from backend.routes.reader_lookup_rules import build_rule_based_lookup


def test_build_rule_based_lookup_returns_english_phrasal_verb():
    payload = build_rule_based_lookup("en", "make sure")

    assert payload is not None
    assert payload["meaning_vi"] == "đảm bảo, chắc chắn"
    assert payload["reading"] == "/meik ʃʊr/"
    assert payload["source"] == "rule_based"


def test_build_rule_based_lookup_normalizes_english_alias():
    payload = build_rule_based_lookup("en", "made sure")

    assert payload is not None
    assert payload["normalized_term"] == "make sure"
    assert payload["meaning_vi"] == "đảm bảo, chắc chắn"


def test_build_rule_based_lookup_returns_japanese_reading():
    payload = build_rule_based_lookup("ja", "誠実")

    assert payload is not None
    assert payload["reading"] == "せいじつ"
    assert payload["meaning_vi"] == "chân thành; thành thật; nghiêm túc"


def test_build_rule_based_lookup_strips_japanese_suffix():
    payload = build_rule_based_lookup("ja", "誠実に")

    assert payload is not None
    assert payload["normalized_term"] == "誠実"
    assert payload["reading"] == "せいじつ"


def test_build_rule_based_lookup_returns_chinese_pinyin():
    payload = build_rule_based_lookup("zh-CN", "牛乳")

    assert payload is not None
    assert payload["reading"] == "niú rǔ"
    assert payload["meaning_vi"] == "sữa bò"


def test_build_rule_based_lookup_composes_chinese_reading_from_characters():
    payload = build_rule_based_lookup("zh-CN", "老板")

    assert payload is not None
    assert payload["reading"] == "lǎo bǎn"
    assert payload["meaning_vi"] == "ông chủ; sếp"


def test_build_rule_based_lookup_uses_kana_fallback_for_reading_only():
    payload = build_rule_based_lookup("ja", "しかし")

    assert payload is not None
    assert payload["reading"] == "しかし"
    assert payload["meaning_vi"] == "nhưng; tuy nhiên"


def test_build_rule_based_lookup_lemmatizes_english_plural():
    payload = build_rule_based_lookup("en", "contracts")

    assert payload is not None
    assert payload["normalized_term"] == "contract"
    assert payload["meaning_vi"] == "hợp đồng"


def test_build_rule_based_lookup_segments_known_chinese_phrase():
    payload = build_rule_based_lookup("zh-CN", "公司工资")

    assert payload is not None
    assert payload["pos"] == "phrase"
    assert payload["reading"] == "gōng sī gōng zī"
