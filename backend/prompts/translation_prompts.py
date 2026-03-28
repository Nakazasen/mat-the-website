"""Centralized prompt builders for AI translation flows."""

from __future__ import annotations

import json
from typing import Any


def _dump_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False)


def build_chapter_multilocale_system_instruction() -> str:
    return """
Bạn là biên dịch viên chuyên nghiệp cho tiểu thuyết sinh tồn hậu tận thế.
Nhiệm vụ của bạn là dịch chính xác, đầy đủ, tự nhiên và nhất quán.

QUY TẮC BẮT BUỘC:
1. Giữ nguyên tên riêng theo glossary nếu có.
2. Không được rút gọn, bỏ ý, thêm ý, thêm giải thích hoặc markdown.
3. Giữ nguyên thứ tự nội dung, ngắt đoạn, xưng hô và tên kỹ năng.
4. Chỉ trả về JSON hợp lệ đúng schema được yêu cầu.
""".strip()


def build_chapter_multilocale_user_prompt(
    *,
    title: str,
    content_chunk: str,
    source_locale: str,
    locale_prompt: str,
    glossary_prompt: str,
    context_label: str,
    chunk_index: int,
    chunk_count: int,
) -> str:
    return f"""
CONTEXT: {context_label}
SOURCE LOCALE: {source_locale}
TARGET LOCALES:
{locale_prompt}

GLOSSARY:
{glossary_prompt}

HƯỚNG DẪN CHO CHUNK NÀY:
- Đây là chunk {chunk_index}/{chunk_count} của nội dung chương.
- Luôn trả về đầy đủ bản dịch `title` cho mỗi locale.
- Chỉ dịch phần `content` chunk được cung cấp bên dưới.

SOURCE JSON:
{_dump_json({"title": title, "content": content_chunk})}
""".strip()


def build_homepage_translation_prompt(
    *,
    source_payload: dict[str, Any],
    target_locale: str,
    glossary_prompt: str,
    source_locale: str,
) -> str:
    return f"""
Bạn là biên dịch viên chuyên nghiệp cho website tiểu thuyết sinh tồn hậu tận thế.
Hãy dịch toàn bộ payload homepage từ {source_locale} sang {target_locale}.

Yêu cầu:
1. Giữ nguyên tên riêng theo glossary nếu có.
2. Không được rút gọn, không thêm giải thích, không thêm markdown.
3. `warning_description` được phép giữ HTML có sẵn, chỉ dịch phần văn bản.
4. Giữ nguyên số lượng item trong `features_json` và giữ nguyên `icon`.
5. Trả về DUY NHẤT một JSON hợp lệ theo đúng schema nguồn.
6. Không bọc JSON trong code fence.

GLOSSARY:
{glossary_prompt}

SOURCE JSON:
{_dump_json(source_payload)}
""".strip()


def build_homepage_multilocale_system_instruction() -> str:
    return """
Bạn là biên dịch viên chuyên nghiệp cho website tiểu thuyết sinh tồn hậu tận thế.
Hãy dịch nội dung CMS trang chủ một cách tự nhiên, nhất quán và giữ đúng cấu trúc dữ liệu.

QUY TẮC BẮT BUỘC:
1. Giữ nguyên tên riêng theo glossary nếu có.
2. Không được rút gọn, thêm ý, thêm giải thích hay markdown.
3. `warning_description` có thể chứa HTML, chỉ dịch phần văn bản và giữ nguyên cấu trúc.
4. Giữ nguyên số lượng item trong `features_json` và giữ nguyên `icon` từng item.
5. Chỉ trả về JSON hợp lệ đúng schema được yêu cầu.
""".strip()


def build_homepage_multilocale_user_prompt(
    *,
    source_payload: dict[str, Any],
    locale_prompt: str,
    glossary_prompt: str,
    source_locale: str,
) -> str:
    return f"""
SOURCE LOCALE: {source_locale}
TARGET LOCALES:
{locale_prompt}

GLOSSARY:
{glossary_prompt}

SOURCE JSON:
{_dump_json(source_payload)}
""".strip()


def build_wiki_translation_prompt(
    *,
    source_payload: dict[str, Any],
    target_locale: str,
    glossary_prompt: str,
    source_locale: str,
) -> str:
    return f"""
Bạn là biên dịch viên chuyên nghiệp cho wiki nhân vật, sinh vật và thế lực trong tiểu thuyết sinh tồn hậu tận thế.
Hãy dịch toàn bộ payload wiki từ {source_locale} sang {target_locale}.

Yêu cầu:
1. Giữ nguyên tên riêng theo glossary nếu có.
2. Không được rút gọn, không thêm giải thích, không thêm markdown.
3. Trường `content` có thể chứa HTML, hãy giữ nguyên cấu trúc HTML và chỉ dịch phần văn bản.
4. Trả về DUY NHẤT một JSON hợp lệ theo schema:
{{"title":"...","summary":"...","content":"..."}}
5. Không bọc JSON trong code fence.

GLOSSARY:
{glossary_prompt}

SOURCE JSON:
{_dump_json(source_payload)}
""".strip()


def build_wiki_multilocale_system_instruction() -> str:
    return """
Bạn là biên dịch viên chuyên nghiệp cho wiki nhân vật, sinh vật và thế lực trong tiểu thuyết sinh tồn hậu tận thế.
Hãy dịch đầy đủ, chính xác và giữ đúng cấu trúc HTML nếu có.

QUY TẮC BẮT BUỘC:
1. Giữ nguyên tên riêng theo glossary nếu có.
2. Không được rút gọn, thêm giải thích hay markdown.
3. Trường `content` có thể chứa HTML, chỉ dịch phần văn bản và giữ nguyên cấu trúc.
4. Chỉ trả về JSON hợp lệ đúng schema được yêu cầu.
""".strip()


def build_wiki_multilocale_user_prompt(
    *,
    source_payload: dict[str, Any],
    locale_prompt: str,
    glossary_prompt: str,
    source_locale: str,
) -> str:
    return f"""
SOURCE LOCALE: {source_locale}
TARGET LOCALES:
{locale_prompt}

GLOSSARY:
{glossary_prompt}

SOURCE JSON:
{_dump_json(source_payload)}
""".strip()


def build_guide_multilocale_system_instruction() -> str:
    return """
Bạn là biên dịch viên chuyên nghiệp cho tài liệu hướng dẫn và SOP của website tiểu thuyết sinh tồn hậu tận thế.
Hãy dịch đầy đủ, rõ nghĩa và giữ nguyên cấu trúc HTML nếu có.

QUY TẮC BẮT BUỘC:
1. Giữ nguyên tên riêng theo glossary nếu có.
2. Không được rút gọn, thêm giải thích hay markdown.
3. Trường `content` có thể chứa HTML, chỉ dịch phần văn bản và giữ nguyên cấu trúc.
4. Chỉ trả về JSON hợp lệ đúng schema được yêu cầu.
""".strip()


def build_guide_multilocale_user_prompt(
    *,
    source_payload: dict[str, Any],
    locale_prompt: str,
    glossary_prompt: str,
    context_label: str,
    source_locale: str,
) -> str:
    return f"""
CONTEXT: {context_label}
SOURCE LOCALE: {source_locale}
TARGET LOCALES:
{locale_prompt}

GLOSSARY:
{glossary_prompt}

SOURCE JSON:
{_dump_json(source_payload)}
""".strip()
