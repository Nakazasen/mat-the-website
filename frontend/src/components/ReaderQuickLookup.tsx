'use client';

import { useCallback, useEffect, useMemo, useState, type RefObject } from 'react';
import { BookOpenText, ExternalLink, Loader2, Search, X } from 'lucide-react';

import { useLocale } from '@/context/LocaleContext';
import type { Locale } from '@/lib/i18n/config';

interface ReaderQuickLookupProps {
    chapterProgress: number;
    containerRef: RefObject<HTMLElement | null>;
    sourceLocale: Locale;
}

interface LookupResponse {
    answer?: string;
    error?: string;
}

function normalizeSelectionText(text: string): string {
    return text.replace(/\s+/g, ' ').trim().slice(0, 120);
}

function buildLookupPrompt(locale: Locale, selectedText: string): string {
    const languageLabel =
        locale === 'ja'
            ? 'tiếng Nhật'
            : locale === 'zh-CN'
                ? 'tiếng Trung giản thể'
                : locale === 'en'
                    ? 'tiếng Anh'
                    : 'tiếng Việt';

    return [
        `Bạn là trợ lý tra từ nhanh cho người Việt đang học ${languageLabel} qua truyện.`,
        `Từ hoặc cụm cần tra: "${selectedText}"`,
        `Yêu cầu trả lời thật ngắn gọn bằng tiếng Việt:`,
        `1. Nghĩa phù hợp nhất trong ngữ cảnh đọc truyện.`,
        `2. Nếu là tiếng Nhật hoặc tiếng Trung, thêm cách đọc Latin nếu suy ra được.`,
        `3. Nêu loại từ hoặc vai trò ngữ pháp nếu rõ.`,
        `4. Nếu đây có vẻ là tên riêng, nói rõ là tên riêng và không bịa nghĩa.`,
        `5. Trả lời tối đa 6 dòng, ưu tiên súc tích, dễ học nhanh.`,
    ].join('\n');
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

export default function ReaderQuickLookup({
    chapterProgress,
    containerRef,
    sourceLocale,
}: ReaderQuickLookupProps) {
    const { dictionary } = useLocale();
    const [selectedText, setSelectedText] = useState('');
    const [toolbarPosition, setToolbarPosition] = useState<{ top: number; left: number } | null>(null);
    const [panelOpen, setPanelOpen] = useState(false);
    const [lookupAnswer, setLookupAnswer] = useState('');
    const [lookupError, setLookupError] = useState<string | null>(null);
    const [lookupLoading, setLookupLoading] = useState(false);
    const [lastLookupKey, setLastLookupKey] = useState('');

    const externalDictionaryUrl = useMemo(
        () => buildExternalDictionaryUrl(sourceLocale, selectedText),
        [selectedText, sourceLocale],
    );

    const hideToolbar = useCallback(() => {
        setToolbarPosition(null);
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
        if (!normalizedText || normalizedText.length < 1) {
            hideToolbar();
            return;
        }

        const rect = range.getBoundingClientRect();
        if (!rect.width && !rect.height) {
            hideToolbar();
            return;
        }

        setSelectedText(normalizedText);
        setToolbarPosition({
            top: Math.max(12, rect.top + window.scrollY - 52),
            left: rect.left + window.scrollX + rect.width / 2,
        });
    }, [containerRef, hideToolbar]);

    const runLookup = useCallback(async (textOverride?: string) => {
        const query = normalizeSelectionText(textOverride || selectedText);
        if (!query || lookupLoading) return;

        const lookupKey = `${sourceLocale}:${query}`;
        if (lookupKey === lastLookupKey && (lookupAnswer || lookupError)) {
            setPanelOpen(true);
            return;
        }

        setPanelOpen(true);
        setLookupLoading(true);
        setLookupError(null);
        setLookupAnswer('');
        setLastLookupKey(lookupKey);

        try {
            const response = await fetch('/api/oracle/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: buildLookupPrompt(sourceLocale, query),
                    chapter_progress: chapterProgress,
                }),
            });
            const payload = await response.json().catch(() => ({})) as LookupResponse;
            if (!response.ok) {
                throw new Error(payload.error || dictionary.lookup.failed);
            }
            setLookupAnswer((payload.answer || '').trim() || dictionary.lookup.failed);
        } catch (error: unknown) {
            setLookupError((error as Error)?.message || dictionary.lookup.failed);
        } finally {
            setLookupLoading(false);
        }
    }, [
        chapterProgress,
        dictionary.lookup.failed,
        lastLookupKey,
        lookupAnswer,
        lookupError,
        lookupLoading,
        selectedText,
        sourceLocale,
    ]);

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
                <div className="fixed bottom-24 left-4 right-4 z-[64] md:left-6 md:right-auto md:w-[360px]">
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

                                {!lookupLoading && !lookupError && lookupAnswer && (
                                    <div className="rounded-xl border border-cyan-900/30 bg-cyan-950/10 px-3 py-3 text-sm leading-7 text-gray-100 whitespace-pre-wrap">
                                        {lookupAnswer}
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
