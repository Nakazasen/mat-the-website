'use client';

import { useCallback, useEffect, useMemo, useState, type RefObject } from 'react';
import { BookOpenText, BookmarkPlus, ExternalLink, Loader2, Quote, Search, X } from 'lucide-react';

import { useLocale } from '@/context/LocaleContext';
import type { Locale } from '@/lib/i18n/config';
import {
    lookupReaderTerm,
    saveReaderSentence,
    saveReaderVocab,
    type ReaderLookupResponse,
} from '@/lib/reader-learning';

interface ReaderQuickLookupProps {
    chapterId?: number;
    chapterProgress: number;
    containerRef: RefObject<HTMLElement | null>;
    sourceLocale: Locale;
}

function normalizeSelectionText(text: string): string {
    return text.replace(/\s+/g, ' ').trim().slice(0, 120);
}

function normalizeContextText(text: string): string {
    return text.replace(/\s+/g, ' ').trim();
}

function buildExternalDictionaryUrl(locale: Locale, selectedText: string): string | null {
    const query = encodeURIComponent(selectedText.trim());
    if (!query) return null;
    if (locale === 'ja') return `https://jotoba.de/search/0/${query}`;
    if (locale === 'zh-CN') return `https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb=${query}`;
    if (locale === 'en') return `https://dictionary.cambridge.org/dictionary/english/${query}`;
    return null;
}

function shouldIgnoreSelectionTarget(target: EventTarget | null): boolean {
    if (!(target instanceof HTMLElement)) return false;
    return Boolean(target.closest('button, a, input, textarea, select, [contenteditable="true"]'));
}

function extractSentenceFromText(text: string, selectedText: string): string {
    const normalizedText = normalizeContextText(text);
    const normalizedSelectedText = normalizeSelectionText(selectedText);

    if (!normalizedText) return normalizedSelectedText;
    if (!normalizedSelectedText) return normalizedText.slice(0, 320);

    const index = normalizedText.indexOf(normalizedSelectedText);
    if (index === -1) {
        return normalizedText.slice(0, 320);
    }

    const punctuation = /[.!?。！？]/;
    let start = index;
    while (start > 0 && !punctuation.test(normalizedText[start - 1])) {
        start -= 1;
    }

    let end = index + normalizedSelectedText.length;
    while (end < normalizedText.length && !punctuation.test(normalizedText[end])) {
        end += 1;
    }

    const sentence = normalizedText.slice(start, Math.min(end + 1, normalizedText.length)).trim();
    return sentence || normalizedSelectedText;
}

function findSelectionSentence(anchorElement: HTMLElement | null, selectedText: string): string {
    const candidates = [
        anchorElement?.closest('p, li, blockquote, dd, dt, h1, h2, h3, h4, h5, h6'),
        anchorElement?.closest('[data-karaoke-index]'),
        anchorElement?.closest('div'),
        anchorElement,
    ].filter(Boolean) as HTMLElement[];

    for (const candidate of candidates) {
        const sentence = extractSentenceFromText(candidate.innerText || candidate.textContent || '', selectedText);
        if (sentence) return sentence;
    }

    return selectedText;
}

export default function ReaderQuickLookup({
    chapterId,
    chapterProgress,
    containerRef,
    sourceLocale,
}: ReaderQuickLookupProps) {
    const { dictionary } = useLocale();
    const [selectedText, setSelectedText] = useState('');
    const [selectedSentence, setSelectedSentence] = useState('');
    const [toolbarPosition, setToolbarPosition] = useState<{ top: number; left: number } | null>(null);
    const [panelOpen, setPanelOpen] = useState(false);
    const [lookupResult, setLookupResult] = useState<ReaderLookupResponse | null>(null);
    const [lookupError, setLookupError] = useState<string | null>(null);
    const [lookupLoading, setLookupLoading] = useState(false);
    const [lastLookupKey, setLastLookupKey] = useState('');
    const [saveVocabLoading, setSaveVocabLoading] = useState(false);
    const [saveSentenceLoading, setSaveSentenceLoading] = useState(false);
    const [saveMessage, setSaveMessage] = useState<string | null>(null);
    const [saveError, setSaveError] = useState<string | null>(null);

    const externalDictionaryUrl = useMemo(() => {
        if (lookupResult?.external_links?.[0]?.url) return lookupResult.external_links[0].url;
        return buildExternalDictionaryUrl(sourceLocale, selectedText);
    }, [lookupResult, selectedText, sourceLocale]);

    const hideToolbar = useCallback(() => {
        setToolbarPosition(null);
    }, []);

    const resetLookupState = useCallback(() => {
        setLookupResult(null);
        setLookupError(null);
        setSaveMessage(null);
        setSaveError(null);
    }, []);

    const readCurrentSelection = useCallback(() => {
        const container = containerRef.current;
        if (!container) {
            hideToolbar();
            return;
        }

        const selection = window.getSelection();
        if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
            hideToolbar();
            return;
        }

        const range = selection.getRangeAt(0);
        const anchorNode = range.commonAncestorContainer;
        const anchorElement = anchorNode.nodeType === Node.ELEMENT_NODE
            ? (anchorNode as HTMLElement)
            : anchorNode.parentElement;

        if (!anchorElement || !container.contains(anchorElement)) {
            hideToolbar();
            return;
        }

        const normalizedText = normalizeSelectionText(selection.toString());
        if (!normalizedText) {
            hideToolbar();
            return;
        }

        const rect = range.getBoundingClientRect();
        if (!rect.width && !rect.height) {
            hideToolbar();
            return;
        }

        const sentence = findSelectionSentence(anchorElement, normalizedText);

        setSelectedText((prev) => {
            if (prev !== normalizedText) {
                resetLookupState();
            }
            return normalizedText;
        });
        setSelectedSentence(sentence);
        setToolbarPosition({
            top: Math.max(12, rect.top + window.scrollY - 52),
            left: rect.left + window.scrollX + rect.width / 2,
        });
    }, [containerRef, hideToolbar, resetLookupState]);

    const runLookup = useCallback(async (textOverride?: string) => {
        const query = normalizeSelectionText(textOverride || selectedText);
        if (!query || lookupLoading) return;

        const lookupKey = `${sourceLocale}:${query}:${selectedSentence}`;
        if (lookupKey === lastLookupKey && (lookupResult || lookupError)) {
            setPanelOpen(true);
            return;
        }

        setPanelOpen(true);
        setLookupLoading(true);
        setLookupError(null);
        setLookupResult(null);
        setSaveMessage(null);
        setSaveError(null);
        setLastLookupKey(lookupKey);

        try {
            const payload = await lookupReaderTerm({
                locale: sourceLocale,
                term: query,
                context_sentence: selectedSentence || undefined,
                chapter_id: chapterId,
            });
            setLookupResult(payload);
        } catch (error: unknown) {
            setLookupError((error as Error)?.message || dictionary.lookup.failed);
        } finally {
            setLookupLoading(false);
        }
    }, [
        chapterId,
        dictionary.lookup.failed,
        lastLookupKey,
        lookupError,
        lookupLoading,
        lookupResult,
        selectedSentence,
        selectedText,
        sourceLocale,
    ]);

    const handleSaveVocab = useCallback(async () => {
        if (!selectedText || saveVocabLoading) return;

        setSaveVocabLoading(true);
        setSaveMessage(null);
        setSaveError(null);

        try {
            await saveReaderVocab({
                locale: sourceLocale,
                term: selectedText,
                normalized_term: lookupResult?.normalized_term,
                reading: lookupResult?.reading || undefined,
                meaning_vi: lookupResult?.meaning_vi || undefined,
                pos: lookupResult?.pos || undefined,
                notes: lookupResult?.notes || `Lưu khi đang đọc tới chương ${chapterProgress}.`,
                context_sentence: selectedSentence || undefined,
                chapter_id: chapterId,
                source: lookupResult?.source || 'manual',
            });
            setSaveMessage('Đã lưu từ vào kho học tập.');
        } catch (error: unknown) {
            setSaveError((error as Error)?.message || 'Không lưu được từ đã chọn.');
        } finally {
            setSaveVocabLoading(false);
        }
    }, [chapterId, lookupResult, saveVocabLoading, selectedSentence, selectedText, sourceLocale]);

    const handleSaveSentence = useCallback(async () => {
        if (!selectedSentence || saveSentenceLoading) return;

        setSaveSentenceLoading(true);
        setSaveMessage(null);
        setSaveError(null);

        try {
            await saveReaderSentence({
                locale: sourceLocale,
                sentence_text: selectedSentence,
                meaning_vi: lookupResult?.meaning_vi || undefined,
                note: selectedText
                    ? `Từ được tra trong câu: ${selectedText}. Chương đọc: ${chapterProgress}.`
                    : `Chương đọc: ${chapterProgress}.`,
                chapter_id: chapterId,
            });
            setSaveMessage('Đã lưu câu vào kho học tập.');
        } catch (error: unknown) {
            setSaveError((error as Error)?.message || 'Không lưu được câu hiện tại.');
        } finally {
            setSaveSentenceLoading(false);
        }
    }, [chapterId, lookupResult, saveSentenceLoading, selectedSentence, selectedText, sourceLocale]);

    useEffect(() => {
        const handlePointerUp = (event: MouseEvent | TouchEvent) => {
            if (shouldIgnoreSelectionTarget(event.target)) return;
            window.setTimeout(readCurrentSelection, 0);
        };

        const handleKeyUp = () => {
            window.setTimeout(readCurrentSelection, 0);
        };

        const handleScroll = () => {
            if (!panelOpen) hideToolbar();
        };

        const handleEscape = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                hideToolbar();
                setPanelOpen(false);
            }
        };

        document.addEventListener('mouseup', handlePointerUp);
        document.addEventListener('touchend', handlePointerUp);
        document.addEventListener('keyup', handleKeyUp);
        window.addEventListener('scroll', handleScroll, { passive: true });
        window.addEventListener('keydown', handleEscape);

        return () => {
            document.removeEventListener('mouseup', handlePointerUp);
            document.removeEventListener('touchend', handlePointerUp);
            document.removeEventListener('keyup', handleKeyUp);
            window.removeEventListener('scroll', handleScroll);
            window.removeEventListener('keydown', handleEscape);
        };
    }, [hideToolbar, panelOpen, readCurrentSelection]);

    return (
        <>
            {toolbarPosition && selectedText && (
                <div
                    className="fixed z-[65] -translate-x-1/2"
                    style={{ top: `${toolbarPosition.top}px`, left: `${toolbarPosition.left}px` }}
                >
                    <button
                        type="button"
                        onClick={() => runLookup()}
                        className="inline-flex items-center gap-2 rounded-full border border-cyan-500/40 bg-ash-950/95 px-3 py-2 text-[11px] font-mono text-cyan-300 shadow-[0_8px_30px_rgba(0,0,0,0.45)] backdrop-blur hover:border-cyan-400 hover:text-cyan-200"
                    >
                        <Search size={12} />
                        {dictionary.lookup.action}
                    </button>
                </div>
            )}

            {(panelOpen || selectedText) && (
                <div className="fixed bottom-24 left-4 right-4 z-[64] md:left-6 md:right-auto md:w-[380px]">
                    <div className="overflow-hidden rounded-2xl border border-cyan-900/40 bg-[#090d12]/95 shadow-[0_18px_60px_rgba(0,0,0,0.45)] backdrop-blur">
                        <div className="flex items-center gap-2 border-b border-cyan-900/30 px-4 py-3">
                            <BookOpenText size={15} className="text-cyan-300" />
                            <div className="min-w-0 flex-1">
                                <div className="text-[11px] font-mono uppercase tracking-[0.25em] text-cyan-300">
                                    {dictionary.lookup.title}
                                </div>
                                <div className="truncate text-[10px] text-gray-500">
                                    {selectedText || dictionary.lookup.hint}
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={() => setPanelOpen((prev) => !prev)}
                                className="rounded-full border border-gray-800 p-2 text-gray-400 hover:border-cyan-500/40 hover:text-cyan-200"
                                title={panelOpen ? dictionary.lookup.close : dictionary.lookup.action}
                            >
                                {panelOpen ? <X size={14} /> : <Search size={14} />}
                            </button>
                        </div>

                        {panelOpen && (
                            <div className="space-y-3 px-4 py-4">
                                <div className="rounded-xl border border-gray-800 bg-black/20 px-3 py-2">
                                    <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-gray-500">
                                        {dictionary.lookup.selected}
                                    </div>
                                    <div className="mt-1 break-words text-sm text-reader-text">
                                        {selectedText || dictionary.lookup.empty}
                                    </div>
                                    {selectedSentence && (
                                        <div className="mt-3 rounded-lg border border-ash-800 bg-ash-950/70 px-3 py-2 text-xs leading-6 text-ash-400">
                                            {selectedSentence}
                                        </div>
                                    )}
                                </div>

                                {lookupLoading && (
                                    <div className="flex items-center gap-2 rounded-xl border border-cyan-900/30 bg-cyan-950/10 px-3 py-3 text-sm text-cyan-200">
                                        <Loader2 size={14} className="animate-spin" />
                                        {dictionary.lookup.loading}
                                    </div>
                                )}

                                {!lookupLoading && lookupError && (
                                    <div className="rounded-xl border border-red-900/40 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                                        {lookupError}
                                    </div>
                                )}

                                {!lookupLoading && !lookupError && lookupResult && (
                                    <div className="rounded-xl border border-cyan-900/30 bg-cyan-950/10 px-3 py-3 text-sm text-gray-100">
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span className="text-base font-semibold text-white">{lookupResult.term}</span>
                                            {lookupResult.reading && (
                                                <span className="rounded-full border border-cyan-700/40 px-2 py-1 text-[11px] font-mono text-cyan-200">
                                                    {lookupResult.reading}
                                                </span>
                                            )}
                                            {lookupResult.pos && (
                                                <span className="rounded-full border border-ash-700 px-2 py-1 text-[11px] font-mono text-ash-300">
                                                    {lookupResult.pos}
                                                </span>
                                            )}
                                        </div>

                                        <div className="mt-3 whitespace-pre-wrap leading-7 text-gray-100">
                                            {lookupResult.meaning_vi || 'Đang ở chế độ scaffold: contract lookup đã có, bước tiếp theo sẽ nối rule-based và AI giải nghĩa ngữ cảnh.'}
                                        </div>

                                        {lookupResult.notes && (
                                            <div className="mt-3 rounded-lg border border-ash-800 bg-black/20 px-3 py-3 text-xs leading-6 text-ash-300">
                                                {lookupResult.notes}
                                            </div>
                                        )}

                                        <div className="mt-3 text-[10px] font-mono uppercase tracking-[0.2em] text-cyan-400">
                                            Source: {lookupResult.source}
                                        </div>
                                    </div>
                                )}

                                {saveMessage && (
                                    <div className="rounded-xl border border-green-900/40 bg-green-950/20 px-3 py-3 text-sm text-green-200">
                                        {saveMessage}
                                    </div>
                                )}

                                {saveError && (
                                    <div className="rounded-xl border border-red-900/40 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                                        {saveError}
                                    </div>
                                )}

                                <div className="flex flex-wrap gap-2">
                                    <button
                                        type="button"
                                        onClick={() => runLookup()}
                                        disabled={!selectedText || lookupLoading}
                                        className="inline-flex items-center gap-2 rounded-lg border border-cyan-700/40 px-3 py-2 text-[11px] font-mono text-cyan-300 hover:bg-cyan-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                        <Search size={12} />
                                        {dictionary.lookup.action}
                                    </button>

                                    <button
                                        type="button"
                                        onClick={handleSaveVocab}
                                        disabled={!selectedText || saveVocabLoading}
                                        className="inline-flex items-center gap-2 rounded-lg border border-emerald-700/40 px-3 py-2 text-[11px] font-mono text-emerald-300 hover:bg-emerald-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                        {saveVocabLoading ? <Loader2 size={12} className="animate-spin" /> : <BookmarkPlus size={12} />}
                                        Lưu từ
                                    </button>

                                    <button
                                        type="button"
                                        onClick={handleSaveSentence}
                                        disabled={!selectedSentence || saveSentenceLoading}
                                        className="inline-flex items-center gap-2 rounded-lg border border-amber-700/40 px-3 py-2 text-[11px] font-mono text-amber-300 hover:bg-amber-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                        {saveSentenceLoading ? <Loader2 size={12} className="animate-spin" /> : <Quote size={12} />}
                                        Lưu câu
                                    </button>

                                    {externalDictionaryUrl && (
                                        <a
                                            href={externalDictionaryUrl}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="inline-flex items-center gap-2 rounded-lg border border-gray-800 px-3 py-2 text-[11px] font-mono text-gray-300 hover:border-cyan-500/30 hover:text-cyan-200"
                                        >
                                            <ExternalLink size={12} />
                                            {dictionary.lookup.external}
                                        </a>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}
