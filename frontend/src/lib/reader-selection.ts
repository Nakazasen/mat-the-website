"use client";

import type { Locale } from "@/lib/i18n/config";

const SENTENCE_BOUNDARY_REGEX = /[.!?。！？\n]/;
const BLOCK_SELECTOR = "p, li, blockquote, dd, dt, h1, h2, h3, h4, h5, h6, [data-karaoke-index], div";

export function normalizeSelectionText(text: string, maxLength = 120): string {
    return text.replace(/\s+/g, " ").trim().slice(0, maxLength);
}

export function normalizeContextText(text: string): string {
    return text.replace(/\s+/g, " ").trim();
}

export function buildExternalDictionaryUrl(locale: Locale, selectedText: string): string | null {
    const query = encodeURIComponent(selectedText.trim());
    if (!query) return null;
    if (locale === "ja") return `https://jotoba.de/search/0/${query}`;
    if (locale === "zh-CN") {
        return `https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb=${query}`;
    }
    if (locale === "en") return `https://dictionary.cambridge.org/dictionary/english/${query}`;
    return null;
}

export function shouldIgnoreSelectionTarget(target: EventTarget | null): boolean {
    if (!(target instanceof HTMLElement)) return false;
    return Boolean(target.closest("button, a, input, textarea, select, [contenteditable='true']"));
}

export function extractSentenceFromText(text: string, selectedText: string): string {
    const normalizedText = normalizeContextText(text);
    const normalizedSelectedText = normalizeSelectionText(selectedText);

    if (!normalizedText) return normalizedSelectedText;
    if (!normalizedSelectedText) return normalizedText.slice(0, 320);

    const index = normalizedText.indexOf(normalizedSelectedText);
    if (index === -1) {
        return normalizedText.slice(0, 320);
    }

    let start = index;
    while (start > 0 && !SENTENCE_BOUNDARY_REGEX.test(normalizedText[start - 1])) {
        start -= 1;
    }

    let end = index + normalizedSelectedText.length;
    while (end < normalizedText.length && !SENTENCE_BOUNDARY_REGEX.test(normalizedText[end])) {
        end += 1;
    }

    const sentence = normalizedText.slice(start, Math.min(end + 1, normalizedText.length)).trim();
    return sentence || normalizedSelectedText;
}

export function findSelectionSentence(anchorElement: HTMLElement | null, selectedText: string): string {
    const candidates = [
        anchorElement?.closest("p, li, blockquote, dd, dt, h1, h2, h3, h4, h5, h6"),
        anchorElement?.closest("[data-karaoke-index]"),
        anchorElement?.closest("div"),
        anchorElement,
    ].filter(Boolean) as HTMLElement[];

    for (const candidate of candidates) {
        const sentence = extractSentenceFromText(candidate.innerText || candidate.textContent || "", selectedText);
        if (sentence) return sentence;
    }

    return selectedText;
}

function getBlockElementFromTarget(container: HTMLElement, target: EventTarget | null): HTMLElement | null {
    if (!(target instanceof HTMLElement)) return null;
    const block = target.closest(BLOCK_SELECTOR) as HTMLElement | null;
    if (block && container.contains(block)) return block;
    return container.contains(target) ? target : null;
}

function getTextOffsetWithinElement(element: HTMLElement, clientX: number, clientY: number): number | null {
    const documentAny = document as Document & {
        caretPositionFromPoint?: (x: number, y: number) => { offsetNode: Node; offset: number } | null;
        caretRangeFromPoint?: (x: number, y: number) => Range | null;
    };

    let offsetNode: Node | null = null;
    let offset = 0;

    const caretPosition = documentAny.caretPositionFromPoint?.(clientX, clientY);
    if (caretPosition) {
        offsetNode = caretPosition.offsetNode;
        offset = caretPosition.offset;
    } else {
        const caretRange = documentAny.caretRangeFromPoint?.(clientX, clientY);
        if (caretRange) {
            offsetNode = caretRange.startContainer;
            offset = caretRange.startOffset;
        }
    }

    if (!offsetNode || !element.contains(offsetNode)) {
        return null;
    }

    const range = document.createRange();
    range.setStart(element, 0);
    range.setEnd(offsetNode, offset);
    return range.toString().length;
}

export function extractSentenceAtOffset(text: string, offset: number): string {
    const rawText = text || "";
    if (!rawText.trim()) return "";

    const safeOffset = Math.max(0, Math.min(offset, rawText.length));
    let start = safeOffset;
    while (start > 0 && !SENTENCE_BOUNDARY_REGEX.test(rawText[start - 1])) {
        start -= 1;
    }

    let end = safeOffset;
    while (end < rawText.length && !SENTENCE_BOUNDARY_REGEX.test(rawText[end])) {
        end += 1;
    }

    const sentence = normalizeContextText(rawText.slice(start, Math.min(end + 1, rawText.length)));
    if (sentence) return sentence;

    return normalizeContextText(rawText).slice(0, 320);
}

export function findSentenceFromPoint(
    container: HTMLElement,
    target: EventTarget | null,
    clientX: number,
    clientY: number,
): string {
    const block = getBlockElementFromTarget(container, target);
    if (!block) return "";

    const blockText = block.innerText || block.textContent || "";
    const fallback = normalizeContextText(blockText).slice(0, 320);
    if (!fallback) return "";

    const offset = getTextOffsetWithinElement(block, clientX, clientY);
    if (offset === null) return fallback;

    return extractSentenceAtOffset(blockText, offset);
}
