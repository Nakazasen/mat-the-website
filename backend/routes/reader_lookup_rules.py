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


def _build_rule(
    *,
    term: str,
    normalized_term: str,
    locale: str,
    reading: str | None,
    meaning_vi: str | None,
    pos: str | None,
    notes: str | None,
) -> RuleBasedLookup:
    return {
        "term": term,
        "normalized_term": normalized_term,
        "locale": locale,
        "reading": reading,
        "meaning_vi": meaning_vi,
        "pos": pos,
        "notes": notes,
        "source": "rule_based",
    }


EN_EXACT_RULES: dict[str, dict[str, str | None]] = {
    "make sure": {
        "reading": "/meik ʃʊr/",
        "meaning_vi": "đảm bảo, chắc chắn",
        "pos": "verb phrase / collocation",
        "notes": "Cụm này nhấn mạnh việc xác nhận hoặc bảo đảm điều gì đó xảy ra đúng như mong muốn.",
    },
    "pay attention": {
        "reading": "/pei əˈten.ʃən/",
        "meaning_vi": "chú ý",
        "pos": "verb phrase / collocation",
        "notes": "Thường dùng để yêu cầu tập trung vào một chi tiết, hành động hoặc lời nói quan trọng.",
    },
    "take care": {
        "reading": "/teik ker/",
        "meaning_vi": "cẩn thận; chăm sóc",
        "pos": "verb phrase / collocation",
        "notes": "Tùy ngữ cảnh có thể là lời nhắc giữ gìn hoặc hành động chăm sóc ai đó.",
    },
    "give up": {
        "reading": "/ɡɪv ʌp/",
        "meaning_vi": "bỏ cuộc; từ bỏ",
        "pos": "phrasal verb",
        "notes": "Nghĩa của cả cụm quan trọng hơn từng từ riêng lẻ, nên cần nhớ như một đơn vị.",
    },
    "look for": {
        "reading": "/lʊk fɔr/",
        "meaning_vi": "tìm kiếm",
        "pos": "phrasal verb",
        "notes": "Chỉ hành động chủ động đi tìm người, vật hoặc thông tin.",
    },
    "find out": {
        "reading": "/faind aut/",
        "meaning_vi": "phát hiện ra; tìm ra",
        "pos": "phrasal verb",
        "notes": "Thường dùng khi biết được một thông tin sau khi điều tra, quan sát hoặc tình cờ nhận ra.",
    },
    "carry on": {
        "reading": "/ˈkæri ɑn/",
        "meaning_vi": "tiếp tục",
        "pos": "phrasal verb",
        "notes": "Chỉ việc tiếp tục một hành động hoặc tiến trình đang diễn ra.",
    },
    "wake up": {
        "reading": "/weik ʌp/",
        "meaning_vi": "thức dậy; tỉnh ra",
        "pos": "phrasal verb",
        "notes": "Có thể dùng theo nghĩa đen là thức dậy, hoặc nghĩa bóng là bừng tỉnh nhận ra sự thật.",
    },
    "salary": {
        "reading": "/ˈsæl.ər.i/",
        "meaning_vi": "lương",
        "pos": "noun",
        "notes": "Thường chỉ khoản lương cố định nhận theo tháng hoặc chu kỳ.",
    },
    "monthly salary": {
        "reading": "/ˈmʌnθ.li ˈsæl.ər.i/",
        "meaning_vi": "lương tháng",
        "pos": "noun phrase",
        "notes": "Cụm này nhấn mạnh mức lương tính theo tháng.",
    },
    "honest": {
        "reading": "/ˈɑː.nɪst/",
        "meaning_vi": "thành thật; trung thực",
        "pos": "adjective",
        "notes": "Chỉ phẩm chất không gian dối, đáng tin và thẳng thắn.",
    },
    "company": {
        "reading": "/ˈkʌm.pə.ni/",
        "meaning_vi": "công ty",
        "pos": "noun",
        "notes": "Danh từ chỉ doanh nghiệp hoặc tổ chức kinh doanh.",
    },
    "contract": {
        "reading": "/ˈkɑn.trækt/",
        "meaning_vi": "hợp đồng",
        "pos": "noun",
        "notes": "Thường là thỏa thuận chính thức hoặc có giá trị pháp lý.",
    },
    "income": {
        "reading": "/ˈɪn.kʌm/",
        "meaning_vi": "thu nhập",
        "pos": "noun",
        "notes": "Chỉ số tiền kiếm được từ công việc hoặc nguồn thu khác.",
    },
    "ability": {
        "reading": "/əˈbɪl.ə.ti/",
        "meaning_vi": "năng lực; khả năng",
        "pos": "noun",
        "notes": "Chỉ khả năng hoàn thành một việc hoặc trình độ vốn có.",
    },
    "profit": {
        "reading": "/ˈprɑː.fɪt/",
        "meaning_vi": "lợi nhuận; lợi ích",
        "pos": "noun",
        "notes": "Trong truyện kinh doanh thường nghiêng về lợi nhuận hoặc lợi ích thu được.",
    },
    "cover up": {
        "reading": "/ˈkʌv.ər ʌp/",
        "meaning_vi": "che đậy; bưng bít",
        "pos": "phrasal verb",
        "notes": "Chỉ việc cố tình giấu đi sự thật hoặc hậu quả xấu.",
    },
    "clean up someone else's mess": {
        "reading": "/kliːn ʌp ˈsʌm.wʌn elz mes/",
        "meaning_vi": "dọn hậu quả do người khác gây ra",
        "pos": "idiom / expression",
        "notes": "Cụm này mang sắc thái phải gánh trách nhiệm hoặc sửa sai thay cho người khác.",
    },
}

EN_ALIAS_RULES = {
    "made sure": "make sure",
    "making sure": "make sure",
    "paid attention": "pay attention",
    "paying attention": "pay attention",
    "took care": "take care",
    "taking care": "take care",
    "gave up": "give up",
    "giving up": "give up",
    "looked for": "look for",
    "looking for": "look for",
    "found out": "find out",
    "finding out": "find out",
    "carried on": "carry on",
    "carrying on": "carry on",
    "woke up": "wake up",
    "waking up": "wake up",
    "companies": "company",
    "contracts": "contract",
    "profits": "profit",
    "salaries": "salary",
    "incomes": "income",
    "abilities": "ability",
    "covered up": "cover up",
    "covering up": "cover up",
}

JA_EXACT_RULES: dict[str, dict[str, str | None]] = {
    "誠実": {
        "reading": "せいじつ",
        "meaning_vi": "chân thành; thành thật; nghiêm túc",
        "pos": "na-adj / noun",
        "notes": "Thường dùng để nói về tính cách đáng tin, cư xử nghiêm túc và không giả dối.",
    },
    "仕事": {
        "reading": "しごと",
        "meaning_vi": "công việc",
        "pos": "noun",
        "notes": "Có thể chỉ việc làm, nhiệm vụ hoặc nghề nghiệp tùy ngữ cảnh.",
    },
    "会社": {
        "reading": "かいしゃ",
        "meaning_vi": "công ty",
        "pos": "noun",
        "notes": "Danh từ chỉ công ty hoặc doanh nghiệp.",
    },
    "社長": {
        "reading": "しゃちょう",
        "meaning_vi": "giám đốc; chủ tịch công ty",
        "pos": "noun",
        "notes": "Chỉ người đứng đầu công ty. Trong truyện thường là boss trực tiếp.",
    },
    "給料": {
        "reading": "きゅうりょう",
        "meaning_vi": "tiền lương",
        "pos": "noun",
        "notes": "Khoản tiền nhận được từ công việc.",
    },
    "月給": {
        "reading": "げっきゅう",
        "meaning_vi": "lương tháng",
        "pos": "noun",
        "notes": "Chỉ mức lương tính theo tháng.",
    },
    "利益": {
        "reading": "りえき",
        "meaning_vi": "lợi ích; lợi nhuận",
        "pos": "noun",
        "notes": "Tùy ngữ cảnh có thể là lợi ích chung hoặc lợi nhuận kinh doanh.",
    },
    "能力": {
        "reading": "のうりょく",
        "meaning_vi": "năng lực",
        "pos": "noun",
        "notes": "Chỉ khả năng hoặc trình độ làm việc.",
    },
    "収入": {
        "reading": "しゅうにゅう",
        "meaning_vi": "thu nhập",
        "pos": "noun",
        "notes": "Tổng số tiền kiếm được từ công việc hoặc nguồn khác.",
    },
    "待遇": {
        "reading": "たいぐう",
        "meaning_vi": "đãi ngộ; đối xử",
        "pos": "noun",
        "notes": "Thường nói về mức đãi ngộ, cách đối xử hoặc điều kiện nhận được.",
    },
    "不満": {
        "reading": "ふまん",
        "meaning_vi": "bất mãn; không hài lòng",
        "pos": "noun",
        "notes": "Chỉ cảm giác khó chịu, không thỏa mãn với tình hình hiện tại.",
    },
    "契約": {
        "reading": "けいやく",
        "meaning_vi": "hợp đồng",
        "pos": "noun",
        "notes": "Thỏa thuận chính thức, thường có ràng buộc rõ ràng.",
    },
    "尻拭い": {
        "reading": "しりぬぐい",
        "meaning_vi": "dọn hậu quả cho người khác",
        "pos": "noun",
        "notes": "Mang sắc thái phải gánh hậu quả hoặc sửa sai do người khác gây ra.",
    },
    "隠蔽工作": {
        "reading": "いんぺいこうさく",
        "meaning_vi": "che giấu; thao túng bưng bít",
        "pos": "noun",
        "notes": "Chỉ việc có chủ đích che đậy sự thật hoặc xóa dấu vết.",
    },
    "詐欺会社": {
        "reading": "さぎがいしゃ",
        "meaning_vi": "công ty lừa đảo",
        "pos": "noun",
        "notes": "Ghép của 詐欺 và 会社, chỉ một công ty mang bản chất lừa đảo.",
    },
    "愚か者": {
        "reading": "おろかもの",
        "meaning_vi": "kẻ ngu ngốc",
        "pos": "noun",
        "notes": "Cách gọi mang sắc thái miệt thị hoặc khinh thường.",
    },
}

JA_KANA_RULES: dict[str, dict[str, str | None]] = {
    "しかし": {
        "reading": "しかし",
        "meaning_vi": "nhưng; tuy nhiên",
        "pos": "conjunction",
        "notes": "Liên từ chuyển ý, dùng để đối lập với mệnh đề trước.",
    },
    "もし": {
        "reading": "もし",
        "meaning_vi": "nếu",
        "pos": "adverb",
        "notes": "Thường đi kèm cấu trúc giả định như もし〜なら hoặc もし〜たら.",
    },
    "だから": {
        "reading": "だから",
        "meaning_vi": "vì vậy; cho nên",
        "pos": "conjunction",
        "notes": "Chỉ quan hệ nguyên nhân và kết quả trong lời nói thường ngày.",
    },
    "ちゃんと": {
        "reading": "ちゃんと",
        "meaning_vi": "đàng hoàng; tử tế; đúng chuẩn",
        "pos": "adverb",
        "notes": "Nhấn mạnh việc làm gì đó nghiêm túc, đầy đủ hoặc đúng cách.",
    },
}

JA_TRAILING_SUFFIXES = (
    "でした",
    "ます",
    "ました",
    "ない",
    "たい",
    "には",
    "では",
    "から",
    "まで",
    "より",
    "だけ",
    "ほど",
    "くらい",
    "ぐらい",
    "です",
    "だった",
    "だ",
    "に",
    "は",
    "が",
    "を",
    "へ",
    "で",
    "と",
    "も",
    "の",
    "ね",
    "よ",
    "な",
    "か",
)

ZH_EXACT_RULES: dict[str, dict[str, str | None]] = {
    "牛乳": {
        "reading": "niú rǔ",
        "meaning_vi": "sữa bò",
        "pos": "noun",
        "notes": "Danh từ chỉ sữa bò.",
    },
    "公司": {
        "reading": "gōng sī",
        "meaning_vi": "công ty",
        "pos": "noun",
        "notes": "Danh từ chỉ công ty hoặc doanh nghiệp.",
    },
    "工资": {
        "reading": "gōng zī",
        "meaning_vi": "tiền lương",
        "pos": "noun",
        "notes": "Khoản lương nhận được từ công việc.",
    },
    "月薪": {
        "reading": "yuè xīn",
        "meaning_vi": "lương tháng",
        "pos": "noun",
        "notes": "Nhấn mạnh mức lương tính theo tháng.",
    },
    "收入": {
        "reading": "shōu rù",
        "meaning_vi": "thu nhập",
        "pos": "noun",
        "notes": "Chỉ tổng tiền kiếm được hoặc thu về.",
    },
    "能力": {
        "reading": "néng lì",
        "meaning_vi": "năng lực",
        "pos": "noun",
        "notes": "Chỉ khả năng làm việc hoặc năng lực cá nhân.",
    },
    "合同": {
        "reading": "hé tóng",
        "meaning_vi": "hợp đồng",
        "pos": "noun",
        "notes": "Thỏa thuận chính thức, thường có tính pháp lý.",
    },
    "利益": {
        "reading": "lì yì",
        "meaning_vi": "lợi ích; lợi nhuận",
        "pos": "noun",
        "notes": "Tùy ngữ cảnh có thể là lợi ích chung hoặc lợi nhuận kinh doanh.",
    },
    "诚实": {
        "reading": "chéng shí",
        "meaning_vi": "thành thật",
        "pos": "adjective",
        "notes": "Chỉ tính cách trung thực, không gian dối.",
    },
    "工作": {
        "reading": "gōng zuò",
        "meaning_vi": "công việc; làm việc",
        "pos": "noun / verb",
        "notes": "Có thể là danh từ chỉ công việc hoặc động từ chỉ hành động làm việc.",
    },
    "老板": {
        "reading": "lǎo bǎn",
        "meaning_vi": "ông chủ; sếp",
        "pos": "noun",
        "notes": "Trong văn cảnh công sở thường là sếp hoặc chủ doanh nghiệp.",
    },
    "待遇": {
        "reading": "dài yù",
        "meaning_vi": "đãi ngộ; đối xử",
        "pos": "noun",
        "notes": "Chỉ cách đối xử hoặc điều kiện đãi ngộ nhận được.",
    },
    "不满": {
        "reading": "bù mǎn",
        "meaning_vi": "bất mãn; không hài lòng",
        "pos": "adjective / verb",
        "notes": "Chỉ trạng thái không hài lòng hoặc bất bình.",
    },
    "但是": {
        "reading": "dàn shì",
        "meaning_vi": "nhưng; tuy nhiên",
        "pos": "conjunction",
        "notes": "Liên từ đối lập để chuyển ý trong câu.",
    },
    "如果": {
        "reading": "rú guǒ",
        "meaning_vi": "nếu",
        "pos": "conjunction",
        "notes": "Dùng để mở mệnh đề điều kiện hoặc giả định.",
    },
}

ZH_CHAR_PINYIN = {
    "牛": "niú",
    "乳": "rǔ",
    "公": "gōng",
    "司": "sī",
    "工": "gōng",
    "资": "zī",
    "月": "yuè",
    "薪": "xīn",
    "收": "shōu",
    "入": "rù",
    "能": "néng",
    "力": "lì",
    "合": "hé",
    "同": "tóng",
    "利": "lì",
    "益": "yì",
    "诚": "chéng",
    "实": "shí",
    "作": "zuò",
    "老": "lǎo",
    "板": "bǎn",
    "待": "dài",
    "遇": "yù",
    "不": "bù",
    "满": "mǎn",
    "但": "dàn",
    "是": "shì",
    "如": "rú",
    "果": "guǒ",
}

ZH_TRAILING_SUFFIXES = ("了", "的", "们", "嗎", "吗", "啊", "呀", "呢", "吧", "啦", "着", "過", "过")

SURROUNDING_PUNCTUATION = " \t\r\n.,!?;:'\"“”‘’()[]{}<>《》「」『』【】，。！？；：、"


def _strip_surrounding_punctuation(term: str) -> str:
    return term.strip(SURROUNDING_PUNCTUATION)


def _normalize_english_term(term: str) -> str:
    lowered = term.lower().replace("’", "'")
    lowered = re.sub(r"[^\w\s'-]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return EN_ALIAS_RULES.get(lowered, lowered)


def _is_kana_only(term: str) -> bool:
    return bool(term) and all(
        ("\u3040" <= char <= "\u309f") or ("\u30a0" <= char <= "\u30ff") or char in {"ー", "・"}
        for char in term
    )


def _strip_japanese_suffix(term: str) -> str:
    normalized = _strip_surrounding_punctuation(term)
    for suffix in JA_TRAILING_SUFFIXES:
        if normalized.endswith(suffix) and len(normalized) > len(suffix):
            candidate = normalized[: -len(suffix)]
            if candidate in JA_EXACT_RULES or candidate in JA_KANA_RULES:
                return candidate
    return normalized


def _strip_chinese_suffix(term: str) -> str:
    normalized = _strip_surrounding_punctuation(term).replace(" ", "")
    for suffix in ZH_TRAILING_SUFFIXES:
        if normalized.endswith(suffix) and len(normalized) > len(suffix):
            candidate = normalized[: -len(suffix)]
            if candidate in ZH_EXACT_RULES:
                return candidate
    return normalized


def _build_english_rule(term: str) -> Optional[RuleBasedLookup]:
    normalized = _normalize_english_term(term)
    rule = EN_EXACT_RULES.get(normalized)
    if not rule:
        return None
    return _build_rule(
        term=term,
        normalized_term=normalized,
        locale="en",
        reading=rule.get("reading"),
        meaning_vi=rule.get("meaning_vi"),
        pos=rule.get("pos"),
        notes=rule.get("notes"),
    )


def _build_kana_fallback(term: str) -> Optional[RuleBasedLookup]:
    if not _is_kana_only(term):
        return None
    return _build_rule(
        term=term,
        normalized_term=term,
        locale="ja",
        reading=term,
        meaning_vi=None,
        pos="kana",
        notes="Từ này được viết hoàn toàn bằng kana, nên có thể dùng trực tiếp làm cách đọc.",
    )


def _build_japanese_rule(term: str) -> Optional[RuleBasedLookup]:
    normalized = _strip_japanese_suffix(term)
    for table in (JA_EXACT_RULES, JA_KANA_RULES):
        rule = table.get(normalized)
        if rule:
            return _build_rule(
                term=term,
                normalized_term=normalized,
                locale="ja",
                reading=rule.get("reading"),
                meaning_vi=rule.get("meaning_vi"),
                pos=rule.get("pos"),
                notes=rule.get("notes"),
            )
    return _build_kana_fallback(normalized)


def _build_chinese_character_fallback(term: str, normalized: str) -> Optional[RuleBasedLookup]:
    if not normalized:
        return None
    readings: list[str] = []
    for char in normalized:
        reading = ZH_CHAR_PINYIN.get(char)
        if not reading:
            return None
        readings.append(reading)
    return _build_rule(
        term=term,
        normalized_term=normalized,
        locale="zh-CN",
        reading=" ".join(readings),
        meaning_vi=None,
        pos="hanzi",
        notes="Đã ghép cách đọc theo từng chữ Hán. Nếu cần nghĩa chính xác theo ngữ cảnh thì mới gọi AI.",
    )


def _build_chinese_rule(term: str) -> Optional[RuleBasedLookup]:
    normalized = _strip_chinese_suffix(term)
    rule = ZH_EXACT_RULES.get(normalized)
    if rule:
        return _build_rule(
            term=term,
            normalized_term=normalized,
            locale="zh-CN",
            reading=rule.get("reading"),
            meaning_vi=rule.get("meaning_vi"),
            pos=rule.get("pos"),
            notes=rule.get("notes"),
        )
    return _build_chinese_character_fallback(term, normalized)


def build_rule_based_lookup(locale: str, term: str, context_sentence: str | None = None) -> Optional[RuleBasedLookup]:
    del context_sentence
    stripped = _strip_surrounding_punctuation(term)
    if not stripped:
        return None
    if locale == "en":
        return _build_english_rule(stripped)
    if locale == "ja":
        return _build_japanese_rule(stripped)
    if locale == "zh-CN":
        return _build_chinese_rule(stripped)
    return None
