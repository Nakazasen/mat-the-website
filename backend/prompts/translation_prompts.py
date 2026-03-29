"""Centralized prompt builders for AI translation flows."""

from __future__ import annotations

import json
from typing import Any


def _dump_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False)


def build_chapter_multilocale_system_instruction() -> str:
    return """
You are a senior literary translator for serialized web novels.
Your job is to translate each chapter chunk faithfully, naturally, and completely.

Mandatory rules:
1. Preserve plot facts, names, skills, glossary terms, and tone.
2. Do not summarize, omit, add information, add explanations, or add markdown.
3. Preserve content order, paragraph order, and scene progression.
4. Preserve the paragraph count of the source chunk.
5. Keep sentence coverage close to the source; do not collapse many source sentences into one short summary sentence.
6. Do not leave untranslated Vietnamese text in the output except glossary-approved proper nouns.
7. Return valid JSON only, matching the requested schema exactly.
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

CHUNK INSTRUCTIONS:
- This is chunk {chunk_index}/{chunk_count} of one chapter.
- Always return a translated `title` for every target locale.
- Translate the provided `content` chunk completely.
- Preserve the source paragraph count.
- Keep sentence coverage close to the source and do not compress multiple source sentences into a short summary.
- Verify that no untranslated Vietnamese sentence remains in the output.

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
You are a professional translator for a post-apocalyptic web novel website.
Translate the entire homepage payload from {source_locale} to {target_locale}.

Requirements:
1. Preserve glossary-approved proper nouns.
2. Do not shorten, add explanations, or add markdown.
3. `warning_description` may contain HTML; translate only the text and preserve the HTML structure.
4. Preserve the number of items in `features_json` and keep each item's `icon`.
5. Return valid JSON only, matching the requested schema exactly.

GLOSSARY:
{glossary_prompt}

SOURCE JSON:
{_dump_json(source_payload)}
""".strip()


def build_homepage_multilocale_system_instruction() -> str:
    return """
You are a professional translator for a post-apocalyptic web novel website.
Translate CMS homepage content naturally while preserving structure.

Mandatory rules:
1. Preserve glossary-approved proper nouns.
2. Do not shorten, add information, add explanations, or add markdown.
3. `warning_description` may contain HTML; translate only the text and preserve the HTML structure.
4. Preserve the number of items in `features_json` and keep each item's `icon`.
5. Return valid JSON only, matching the requested schema exactly.
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
You are a professional translator for a character and lore wiki in a post-apocalyptic web novel.
Translate the entire wiki payload from {source_locale} to {target_locale}.

Requirements:
1. Preserve glossary-approved proper nouns.
2. Do not shorten, add explanations, or add markdown.
3. `content` may contain HTML; translate only the text and preserve the HTML structure.
4. Return valid JSON only, matching this schema:
{{"title":"...","summary":"...","content":"..."}}

GLOSSARY:
{glossary_prompt}

SOURCE JSON:
{_dump_json(source_payload)}
""".strip()


def build_wiki_multilocale_system_instruction() -> str:
    return """
You are a professional translator for a character and lore wiki in a post-apocalyptic web novel.
Translate clearly and preserve HTML structure where present.

Mandatory rules:
1. Preserve glossary-approved proper nouns.
2. Do not shorten, add information, add explanations, or add markdown.
3. `content` may contain HTML; translate only the text and preserve the HTML structure.
4. Return valid JSON only, matching the requested schema exactly.
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
You are a professional translator for website guides and SOP documents in a post-apocalyptic web novel project.
Translate clearly while preserving HTML structure where present.

Mandatory rules:
1. Preserve glossary-approved proper nouns.
2. Do not shorten, add information, add explanations, or add markdown.
3. `content` may contain HTML; translate only the text and preserve the HTML structure.
4. Return valid JSON only, matching the requested schema exactly.
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


def build_chapter_refine_system_instruction() -> str:
    return """
You are a senior literary translation editor for serialized web novels.
Your job is to improve an existing chapter translation using the Vietnamese source text as ground truth.

Rules:
1. Preserve meaning, plot facts, names, skills, and glossary terms.
2. Improve fluency, naturalness, and readability for the target locale.
3. Do not add new information, summaries, markdown, or explanations.
4. Keep paragraph order and scene progression intact.
5. Preserve the source paragraph count exactly unless the source is malformed.
6. Translate every source sentence; do not collapse many source sentences into a short summary.
7. Remove leftover Vietnamese text unless it is a glossary-approved proper noun.
8. Return valid JSON only, matching the requested schema exactly.
""".strip()


def build_chapter_refine_user_prompt(
    *,
    source_title: str,
    source_content_chunk: str,
    current_title: str,
    current_content_chunk: str,
    source_locale: str,
    target_locale: str,
    glossary_prompt: str,
    context_label: str,
    chunk_index: int,
    chunk_count: int,
) -> str:
    return f"""
CONTEXT: {context_label}
SOURCE LOCALE: {source_locale}
TARGET LOCALE: {target_locale}
CHUNK: {chunk_index}/{chunk_count}

TASK:
Improve the existing translation chunk. Use the source text as the authority and the current translation as editable draft text.
Preserve names and glossary consistency. Keep the same paragraph order and the same paragraph count as the source chunk.
Stay close to the source sentence coverage and do not summarize.
Do not leave untranslated Vietnamese sentences behind.

GLOSSARY:
{glossary_prompt}

SOURCE JSON:
{_dump_json({"title": source_title, "content": source_content_chunk})}

CURRENT TRANSLATION JSON:
{_dump_json({"title": current_title, "content": current_content_chunk})}
""".strip()
