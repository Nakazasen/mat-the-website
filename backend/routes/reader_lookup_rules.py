from __future__ import annotations

import re
from typing import Optional, TypedDict


class RuleBasedLookup(TypedDict):
    term: str
    normalized_term: str
    locale: str
    reading: str | None
    meaning_vi: str | None
    pos: str | None
    notes: str | None
    source: str


EN_EXACT_RULES: dict[str, RuleBasedLookup] = {
    "make sure": {
        "term": "make sure",
        "normalized_term": "make sure",
        "locale": "en",
        "reading": "/meɪk ʃʊr/",
        "meaning_vi": "đảm bảo, chắc chắn",
        "pos": "verb phrase / collocation",
        "notes": "Cụm này thường dùng để nhấn mạnh việc phải xác nhận hoặc bảo đảm điều gì đó.",
        "source": "rule_based",
    },
    "pay attention": {
        "term": "pay attention",
        "normalized_term": "pay attention",
        "locale": "en",
        "reading": "/peɪ əˈten.ʃən/",
        "meaning_vi": "chú ý",
        "pos": "verb phrase / collocation",
        "notes": "Cụm quen thuộc, thường đi với to để nói chú ý vào điều gì đó.",
        "source": "rule_based",
    },
    "take care": {
        "term": "take care",
        "normalized_term": "take care",
        "locale": "en",
        "reading": "/teɪk keər/",
        "meaning_vi": "cẩn thận; chăm sóc",
        "pos": "verb phrase / collocation",
        "notes": "Nghĩa chính phụ thuộc ngữ cảnh: có thể là tự giữ gìn hoặc chăm sóc người khác.",
        "source": "rule_based",
    },
    "give up": {
        "term": "give up",
        "normalized_term": "give up",
        "locale": "en",
        "reading": "/ɡɪv ʌp/",
        "meaning_vi": "bỏ cuộc; từ bỏ",
        "pos": "phrasal verb",
        "notes": "Đây là phrasal verb nên nghĩa của cả cụm quan trọng hơn từng từ riêng lẻ.",
        "source": "rule_based",
    },
    "look for": {
        "term": "look for",
        "normalized_term": "look for",
        "locale": "en",
        "reading": "/lʊk fɔːr/",
        "meaning_vi": "tìm kiếm",
        "pos": "phrasal verb",
        "notes": "Cụm này mang nghĩa chủ động đi tìm một người hoặc vật.",
        "source": "rule_based",
    },
    "find out": {
        "term": "find out",
        "normalized_term": "find out",
        "locale": "en",
        "reading": "/faɪnd aʊt/",
        "meaning_vi": "phát hiện ra; tìm ra",
        "pos": "phrasal verb",
        "notes": "Thường dùng khi biết ra thông tin sau khi tìm hiểu hoặc tình cờ phát hiện.",
        "source": "rule_based",
    },
    "carry on": {
        "term": "carry on",
        "normalized_term": "carry on",
        "locale": "en",
        "reading": "/ˈkær.i ɒn/",
        "meaning_vi": "tiếp tục",
        "pos": "phrasal verb",
        "notes": "Cụm này thường mang nghĩa tiếp tục một việc đang làm.",
        "source": "rule_based",
    },
    "wake up": {
        "term": "wake up",
        "normalized_term": "wake up",
        "locale": "en",
        "reading": "/weɪk ʌp/",
        "meaning_vi": "thức dậy; làm tỉnh ra",
        "pos": "phrasal verb",
        "notes": "Có thể dùng theo nghĩa đen là thức dậy hoặc nghĩa bóng là tỉnh ngộ.",
        "source": "rule_based",
    },
    "salary": {
        "term": "salary",
        "normalized_term": "salary",
        "locale": "en",
        "reading": "/ˈsæl.ər.i/",
        "meaning_vi": "lương",
        "pos": "noun",
        "notes": "Thường chỉ khoản lương cố định nhận theo tháng hoặc chu kỳ.",
        "source": "rule_based",
    },
    "honest": {
        "term": "honest",
        "normalized_term": "honest",
        "locale": "en",
        "reading": "/ˈɒn.ɪst/",
        "meaning_vi": "thành thật; trung thực",
        "pos": "adjective",
        "notes": "Chỉ phẩm chất không gian dối hoặc thẳng thắn.",
        "source": "rule_based",
    },
}

EN_LEMMA_RULES = {
    "looked for": "look for",
    "looking for": "look for",
    "made sure": "make sure",
    "making sure": "make sure",
    "gave up": "give up",
    "giving up": "give up",
    "found out": "find out",
    "finding out": "find out",
    "carried on": "carry on",
    "carrying on": "carry on",
    "woke up": "wake up",
    "waking up": "wake up",
}

JA_EXACT_RULES: dict[str, RuleBasedLookup] = {
    "誠実": {
        "term": "誠実",
        "normalized_term": "誠実",
        "locale": "ja",
        "reading": "せいじつ",
        "meaning_vi": "chân thành; thành thật",
        "pos": "na-adj / noun",
        "notes": "Thường dùng để nói về tính cách nghiêm túc, đáng tin hoặc tử tế.",
        "source": "rule_based",
    },
    "仕事": {
        "term": "仕事",
        "normalized_term": "仕事",
        "locale": "ja",
        "reading": "しごと",
        "meaning_vi": "công việc",
        "pos": "noun",
        "notes": "Có thể chỉ việc làm, nhiệm vụ hoặc nghề nghiệp tùy ngữ cảnh.",
        "source": "rule_based",
    },
    "会社": {
        "term": "会社",
        "normalized_term": "会社",
        "locale": "ja",
        "reading": "かいしゃ",
        "meaning_vi": "công ty",
        "pos": "noun",
        "notes": "Thường chỉ doanh nghiệp hoặc công ty nói chung.",
        "source": "rule_based",
    },
    "社長": {
        "term": "社長",
        "normalized_term": "社長",
        "locale": "ja",
        "reading": "しゃちょう",
        "meaning_vi": "giám đốc; chủ tịch công ty",
        "pos": "noun",
        "notes": "Chỉ người đứng đầu công ty.",
        "source": "rule_based",
    },
    "給料": {
        "term": "給料",
        "normalized_term": "給料",
        "locale": "ja",
        "reading": "きゅうりょう",
        "meaning_vi": "tiền lương",
        "pos": "noun",
        "notes": "Khoản tiền nhận được từ công việc.",
        "source": "rule_based",
    },
    "月給": {
        "term": "月給",
        "normalized_term": "月給",
        "locale": "ja",
        "reading": "げっきゅう",
        "meaning_vi": "lương tháng",
        "pos": "noun",
        "notes": "Chỉ mức lương cố định theo tháng.",
        "source": "rule_based",
    },
    "利益": {
        "term": "利益",
        "normalized_term": "利益",
        "locale": "ja",
        "reading": "りえき",
        "meaning_vi": "lợi ích; lợi nhuận",
        "pos": "noun",
        "notes": "Tùy ngữ cảnh có thể là lợi ích chung hoặc lợi nhuận kinh doanh.",
        "source": "rule_based",
    },
    "能力": {
        "term": "能力",
        "normalized_term": "能力",
        "locale": "ja",
        "reading": "のうりょく",
        "meaning_vi": "năng lực",
        "pos": "noun",
        "notes": "Chỉ khả năng hoặc trình độ làm việc.",
        "source": "rule_based",
    },
    "収入": {
        "term": "収入",
        "normalized_term": "収入",
        "locale": "ja",
        "reading": "しゅうにゅう",
        "meaning_vi": "thu nhập",
        "pos": "noun",
        "notes": "Tổng tiền kiếm được từ công việc hoặc nguồn khác.",
        "source": "rule_based",
    },
    "待遇": {
        "term": "待遇",
        "normalized_term": "待遇",
        "locale": "ja",
        "reading": "たいぐう",
        "meaning_vi": "đãi ngộ; đối xử",
        "pos": "noun",
        "notes": "Thường nói về mức đãi ngộ, điều kiện hoặc cách đối xử.",
        "source": "rule_based",
    },
    "不満": {
        "term": "不満",
        "normalized_term": "不満",
        "locale": "ja",
        "reading": "ふまん",
        "meaning_vi": "bất mãn; không hài lòng",
        "pos": "noun",
        "notes": "Chỉ cảm giác không vừa ý hoặc khó chịu.",
        "source": "rule_based",
    },
    "契約": {
        "term": "契約",
        "normalized_term": "契約",
        "locale": "ja",
        "reading": "けいやく",
        "meaning_vi": "hợp đồng",
        "pos": "noun",
        "notes": "Thỏa thuận mang tính chính thức hoặc pháp lý.",
        "source": "rule_based",
    },
    "尻拭い": {
        "term": "尻拭い",
        "normalized_term": "尻拭い",
        "locale": "ja",
        "reading": "しりぬぐい",
        "meaning_vi": "dọn hậu quả cho người khác",
        "pos": "noun",
        "notes": "Thường mang sắc thái phải gánh hậu quả hoặc sửa sai do người khác gây ra.",
        "source": "rule_based",
    },
    "隠蔽工作": {
        "term": "隠蔽工作",
        "normalized_term": "隠蔽工作",
        "locale": "ja",
        "reading": "いんぺいこうさく",
        "meaning_vi": "che giấu; thao tác bưng bít",
        "pos": "noun",
        "notes": "Cụm này chỉ việc cố tình che đậy sự thật hoặc xóa dấu vết.",
        "source": "rule_based",
    },
}

JA_KANA_RULES: dict[str, RuleBasedLookup] = {
    "しかし": {
        "term": "しかし",
        "normalized_term": "しかし",
        "locale": "ja",
        "reading": "しかし",
        "meaning_vi": "nhưng; tuy nhiên",
        "pos": "conjunction",
        "notes": "Liên từ chuyển ý, thường dùng để đối lập với câu trước.",
        "source": "rule_based",
    },
    "もし": {
        "term": "もし",
        "normalized_term": "もし",
        "locale": "ja",
        "reading": "もし",
        "meaning_vi": "nếu",
        "pos": "adverb",
        "notes": "Thường đi với mẫu giả định như 〜なら, 〜たら, 〜ば.",
        "source": "rule_based",
    },
}

ZH_EXACT_RULES: dict[str, RuleBasedLookup] = {
    "牛乳": {
        "term": "牛乳",
        "normalized_term": "牛乳",
        "locale": "zh-CN",
        "reading": "niú rǔ",
        "meaning_vi": "sữa bò",
        "pos": "noun",
        "notes": "Danh từ chỉ sữa bò.",
        "source": "rule_based",
    },
    "公司": {
        "term": "公司",
        "normalized_term": "公司",
        "locale": "zh-CN",
        "reading": "gōng sī",
        "meaning_vi": "công ty",
        "pos": "noun",
        "notes": "Thường chỉ doanh nghiệp hoặc công ty.",
        "source": "rule_based",
    },
    "工资": {
        "term": "工资",
        "normalized_term": "工资",
        "locale": "zh-CN",
        "reading": "gōng zī",
        "meaning_vi": "tiền lương",
        "pos": "noun",
        "notes": "Khoản tiền nhận được từ công việc.",
        "source": "rule_based",
    },
    "收入": {
        "term": "收入",
        "normalized_term": "收入",
        "locale": "zh-CN",
        "reading": "shōu rù",
        "meaning_vi": "thu nhập",
        "pos": "noun",
        "notes": "Tổng khoản tiền kiếm được hoặc thu về.",
        "source": "rule_based",
    },
    "能力": {
        "term": "能力",
        "normalized_term": "能力",
        "locale": "zh-CN",
        "reading": "néng lì",
        "meaning_vi": "năng lực",
        "pos": "noun",
        "notes": "Chỉ khả năng làm việc hoặc trình độ.",
        "source": "rule_based",
    },
    "合同": {
        "term": "合同",
        "normalized_term": "合同",
        "locale": "zh-CN",
        "reading": "hé tong",
        "meaning_vi": "hợp đồng",
        "pos": "noun",
        "notes": "Thỏa thuận chính thức, thường có tính pháp lý.",
        "source": "rule_based",
    },
    "但是": {
        "term": "但是",
        "normalized_term": "但是",
        "locale": "zh-CN",
        "reading": "dàn shì",
        "meaning_vi": "nhưng; tuy nhiên",
        "pos": "conjunction",
        "notes": "Liên từ chuyển ý đối lập.",
        "source": "rule_based",
    },
    "如果": {
        "term": "如果",
        "normalized_term": "如果",
        "locale": "zh-CN",
        "reading": "rú guǒ",
        "meaning_vi": "nếu",
        "pos": "conjunction",
        "notes": "Mở đầu mệnh đề giả định hoặc điều kiện.",
        "source": "rule_based",
    },
}


def _normalize_english_term(term: str) -> str:
    lowered = re.sub(r"[^\w\s'-]", " ", term.lower())
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return EN_LEMMA_RULES.get(lowered, lowered)


def _is_kana_only(term: str) -> bool:
    return bool(term) and all(
        ("\u3040" <= char <= "\u309f") or ("\u30a0" <= char <= "\u30ff") or char in {"ー", "・"}
        for char in term
    )


def _build_kana_fallback(term: str) -> Optional[RuleBasedLookup]:
    normalized = term.strip()
    if not _is_kana_only(normalized):
        return None
    return {
        "term": normalized,
        "normalized_term": normalized,
        "locale": "ja",
        "reading": normalized,
        "meaning_vi": None,
        "pos": "kana",
        "notes": "Cụm này đang viết hoàn toàn bằng kana nên có thể dùng trực tiếp làm cách đọc.",
        "source": "rule_based",
    }


def _build_english_rule(term: str) -> Optional[RuleBasedLookup]:
    normalized = _normalize_english_term(term)
    rule = EN_EXACT_RULES.get(normalized)
    if rule:
        return {**rule, "term": term, "normalized_term": normalized}
    return None


def _build_japanese_rule(term: str) -> Optional[RuleBasedLookup]:
    normalized = term.strip()
    for table in (JA_EXACT_RULES, JA_KANA_RULES):
        rule = table.get(normalized)
        if rule:
            return {**rule, "term": term, "normalized_term": normalized}
    return _build_kana_fallback(normalized)


def _build_chinese_rule(term: str) -> Optional[RuleBasedLookup]:
    normalized = term.strip()
    rule = ZH_EXACT_RULES.get(normalized)
    if rule:
        return {**rule, "term": term, "normalized_term": normalized}
    return None


def build_rule_based_lookup(locale: str, term: str, context_sentence: str | None = None) -> Optional[RuleBasedLookup]:
    del context_sentence
    if locale == "en":
        return _build_english_rule(term)
    if locale == "ja":
        return _build_japanese_rule(term)
    if locale == "zh-CN":
        return _build_chinese_rule(term)
    return None
