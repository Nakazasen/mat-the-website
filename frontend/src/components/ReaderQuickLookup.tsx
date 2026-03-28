'use client';

import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from 'react';
import {
    BookOpenText,
    BookmarkPlus,
    ExternalLink,
    Loader2,
    Maximize2,
    Minimize2,
    Quote,
    Repeat,
    Search,
    Square,
    Volume2,
    X,
} from 'lucide-react';

import { useLocale } from '@/context/LocaleContext';
import type { Locale } from '@/lib/i18n/config';
import {
    getReaderSourceReference,
    lookupReaderTerm,
    requestReaderSentenceTts,
    saveReaderSentence,
    saveReaderVocab,
    type ReaderLookupResponse,
    type ReaderSourceReferenceResponse,
} from '@/lib/reader-learning';
import {
    buildExternalDictionaryUrl,
    findSelectionSentence,
    normalizeSelectionText,
    shouldIgnoreSelectionTarget,
} from '@/lib/reader-selection';

interface ReaderQuickLookupProps {
    chapterId?: number;
    chapterProgress: number;
    containerRef: RefObject<HTMLElement | null>;
    sourceLocale: Locale;
}

const MOBILE_PANEL_EVENT = 'reader-learning-mobile-panel';
const AUDIO_LAYOUT_EVENT = 'reader-audio-layout';
const SOURCE_REFERENCE_EVENT = 'reader-open-source-reference-from-selection';

function getLookupSourceLabel(source?: string | null): string {
    if (source === 'cache') return 'Cache';
    if (source === 'rule_based') return 'Rule-based';
    if (source === 'ai') return 'AI';
    return 'Unknown';
}

function getReadingLabel(locale: Locale): string {
    if (locale === 'ja') return 'Furigana';
    if (locale === 'zh-CN') return 'Pinyin';
    if (locale === 'en') return 'Pronunciation';
    return 'Cách đọc';
}

function renderReadingBlock(locale: Locale, result: ReaderLookupResponse) {
    if (!result.reading) return null;

    if (locale === 'ja') {
        return (
            <div className="mt-3 rounded-xl border border-cyan-900/30 bg-black/20 px-3 py-3">
                <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-cyan-300">Furigana</div>
                <div className="mt-2">
                    <ruby className="text-2xl font-semibold text-white ruby-align-center">
                        {result.term}
                        <rt className="pb-1 text-sm font-normal tracking-[0.08em] text-cyan-300">{result.reading}</rt>
                    </ruby>
                </div>
            </div>
        );
    }

    if (locale === 'zh-CN') {
        return (
            <div className="mt-3 rounded-xl border border-cyan-900/30 bg-black/20 px-3 py-3">
                <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-cyan-300">Pinyin</div>
                <div className="mt-2 text-xs tracking-[0.16em] text-cyan-200">{result.reading}</div>
                <div className="mt-1 text-2xl font-semibold text-white">{result.term}</div>
            </div>
        );
    }

    return (
        <div className="mt-3 rounded-xl border border-cyan-900/30 bg-black/20 px-3 py-3">
            <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-cyan-300">
                {getReadingLabel(locale)}
            </div>
            <div className="mt-2 text-lg font-semibold text-white">{result.reading}</div>
        </div>
    );
}

function shouldAutoLookupSelection(text: string): boolean {
    const normalized = normalizeSelectionText(text, 48);
    if (!normalized) return false;
    const wordCount = normalized.split(/\s+/).filter(Boolean).length;
    return normalized.length <= 32 && wordCount <= 2;
}

function shouldPrioritizeSourceReference(locale: Locale, text: string): boolean {
    if (locale === 'vi') return false;
    const normalized = normalizeSelectionText(text, 240);
    if (!normalized) return false;
    const wordCount = normalized.split(/\s+/).filter(Boolean).length;
    return normalized.length >= 24 || wordCount >= 5;
}

function getSourceReferenceModeLabel(mode?: 'sentence' | 'paragraph'): string {
    return mode === 'sentence' ? 'Đang đối chiếu theo câu' : 'Đang đối chiếu theo đoạn';
}

function getSourceReferenceConfidenceLabel(confidence?: 'high' | 'medium' | 'low'): string {
    if (confidence === 'high') return 'HIGH';
    if (confidence === 'medium') return 'MEDIUM';
    return 'LOW';
}

function getSourceReferenceConfidenceClass(confidence?: 'high' | 'medium' | 'low'): string {
    if (confidence === 'high') {
        return 'border-emerald-500/50 bg-emerald-500/10 text-emerald-200';
    }
    if (confidence === 'medium') {
        return 'border-amber-500/50 bg-amber-500/10 text-amber-200';
    }
    return 'border-red-500/50 bg-red-500/10 text-red-200';
}

function buildDiffHighlightSegments(leftText?: string | null, rightText?: string | null) {
    const left = leftText || '';
    const right = rightText || '';

    let prefix = 0;
    while (prefix < left.length && prefix < right.length && left[prefix] === right[prefix]) {
        prefix += 1;
    }

    let leftSuffix = left.length - 1;
    let rightSuffix = right.length - 1;
    while (leftSuffix >= prefix && rightSuffix >= prefix && left[leftSuffix] === right[rightSuffix]) {
        leftSuffix -= 1;
        rightSuffix -= 1;
    }

    const makeSegments = (value: string, suffixIndex: number) => ({
        before: value.slice(0, prefix),
        changed: value.slice(prefix, suffixIndex + 1),
        after: value.slice(suffixIndex + 1),
    });

    return {
        left: makeSegments(left, leftSuffix),
        right: makeSegments(right, rightSuffix),
        hasDiff: prefix < left.length || prefix < right.length,
    };
}

export default function ReaderQuickLookup({
    chapterId,
    chapterProgress,
    containerRef,
    sourceLocale,
}: ReaderQuickLookupProps) {
    const { dictionary } = useLocale();
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const panelRef = useRef<HTMLDivElement | null>(null);
    const toolbarRef = useRef<HTMLDivElement | null>(null);
    const suppressMobilePanelBroadcastRef = useRef(false);

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
    const [audioLoading, setAudioLoading] = useState(false);
    const [audioError, setAudioError] = useState<string | null>(null);
    const [audioPlaying, setAudioPlaying] = useState(false);
    const [audioActive, setAudioActive] = useState(false);
    const [audioPanelHeight, setAudioPanelHeight] = useState(0);
    const [isDesktop, setIsDesktop] = useState(false);
    const [showGuide, setShowGuide] = useState(false);
    const [sourceReferenceLoading, setSourceReferenceLoading] = useState(false);
    const [sourceReferenceError, setSourceReferenceError] = useState<string | null>(null);
    const [sourceReference, setSourceReference] = useState<ReaderSourceReferenceResponse | null>(null);
    const [sourceReferenceSwapOrder, setSourceReferenceSwapOrder] = useState(false);
    const [panelExpanded, setPanelExpanded] = useState(false);

    const externalDictionaryUrl = useMemo(() => {
        if (lookupResult?.external_links?.[0]?.url) return lookupResult.external_links[0].url;
        return buildExternalDictionaryUrl(sourceLocale, selectedText);
    }, [lookupResult, selectedText, sourceLocale]);

    const panelBottom = useMemo(() => {
        if (audioActive) return isDesktop ? 226 : Math.max(196, audioPanelHeight + 28);
        return isDesktop ? 96 : 88;
    }, [audioActive, audioPanelHeight, isDesktop]);

    const panelTop = useMemo(() => (isDesktop ? 92 : 80), [isDesktop]);
    const desktopPanelWidth = useMemo(() => {
        if (!isDesktop) return undefined;
        return panelExpanded ? 'min(920px, calc(100vw - 3rem))' : '480px';
    }, [isDesktop, panelExpanded]);
    const preferSourceReference = useMemo(
        () => shouldPrioritizeSourceReference(sourceLocale, selectedText),
        [selectedText, sourceLocale],
    );
    const sourceReferenceDiff = useMemo(
        () => buildDiffHighlightSegments(sourceReference?.translated_excerpt, sourceReference?.source_excerpt),
        [sourceReference],
    );

    const hideToolbar = useCallback(() => {
        setToolbarPosition(null);
    }, []);

    const clearBrowserSelection = useCallback(() => {
        const selection = window.getSelection();
        selection?.removeAllRanges();
    }, []);

    const stopSentenceAudio = useCallback(() => {
        if (!audioRef.current) return;
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        setAudioPlaying(false);
    }, []);

    const resetLookupState = useCallback(() => {
        setLookupResult(null);
        setLookupError(null);
        setSaveMessage(null);
        setSaveError(null);
        setAudioError(null);
        setSourceReference(null);
        setSourceReferenceError(null);
        stopSentenceAudio();
    }, [stopSentenceAudio]);

    const closeLookupPanel = useCallback(() => {
        hideToolbar();
        setPanelOpen(false);
        setSelectedText('');
        setSelectedSentence('');
        setLastLookupKey('');
        resetLookupState();
        clearBrowserSelection();
    }, [clearBrowserSelection, hideToolbar, resetLookupState]);

    const showSelectionRequiredError = useCallback(() => {
        setPanelOpen(true);
        hideToolbar();
        setLookupLoading(false);
        setLookupResult(null);
        setLookupError('Hãy bôi đen một từ hoặc cụm trước khi tra.');
        setSaveMessage(null);
        setSaveError(null);
        setAudioError(null);
    }, [hideToolbar]);

    const showSourceReferenceSelectionError = useCallback(() => {
        setPanelOpen(true);
        hideToolbar();
        setSourceReference(null);
        setSourceReferenceLoading(false);
        setSourceReferenceError('Hãy bôi đen một câu hoặc đoạn trước khi mở Gốc VI.');
        setLookupError(null);
        setSaveMessage(null);
        setSaveError(null);
        setAudioError(null);
        if (isDesktop) {
            setPanelExpanded(true);
        }
    }, [hideToolbar, isDesktop]);

    const captureCurrentSelection = useCallback(() => {
        const container = containerRef.current;
        if (!container) return null;

        const selection = window.getSelection();
        if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
            return null;
        }

        const range = selection.getRangeAt(0);
        const anchorNode = range.commonAncestorContainer;
        const anchorElement = anchorNode.nodeType === Node.ELEMENT_NODE
            ? (anchorNode as HTMLElement)
            : anchorNode.parentElement;

        if (!anchorElement || !container.contains(anchorElement)) {
            return null;
        }

        const normalizedText = normalizeSelectionText(selection.toString());
        if (!normalizedText) {
            return null;
        }

        const rect = range.getBoundingClientRect();
        if (!rect.width && !rect.height) {
            return null;
        }

        return {
            normalizedText,
            sentence: findSelectionSentence(anchorElement, normalizedText),
            rect,
        };
    }, [containerRef]);

    const runLookup = useCallback(async (textOverride?: string, sentenceOverride?: string) => {
        const query = normalizeSelectionText(textOverride || selectedText);
        const contextSentence = sentenceOverride ?? selectedSentence;
        if (!query || lookupLoading) return;

        const lookupKey = `${sourceLocale}:${query}:${contextSentence}`;
        if (lookupKey === lastLookupKey && (lookupResult || lookupError)) {
            setPanelOpen(true);
            hideToolbar();
            return;
        }

        setPanelOpen(true);
        hideToolbar();
        setLookupLoading(true);
        setLookupError(null);
        setLookupResult(null);
        setSaveMessage(null);
        setSaveError(null);
        setAudioError(null);
        setLastLookupKey(lookupKey);

        try {
            const payload = await lookupReaderTerm({
                locale: sourceLocale,
                term: query,
                context_sentence: contextSentence || undefined,
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
        hideToolbar,
        lastLookupKey,
        lookupError,
        lookupLoading,
        lookupResult,
        selectedSentence,
        selectedText,
        sourceLocale,
    ]);

    const readCurrentSelection = useCallback((triggerLookup = false) => {
        const snapshot = captureCurrentSelection();
        if (!snapshot) {
            hideToolbar();
            return;
        }
        const { normalizedText, sentence, rect } = snapshot;

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
        if (triggerLookup && shouldAutoLookupSelection(normalizedText)) {
            window.setTimeout(() => {
                void runLookup(normalizedText, sentence);
            }, 0);
        }
    }, [captureCurrentSelection, hideToolbar, resetLookupState, runLookup]);

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
                notes: lookupResult?.notes || `Lưu khi đọc chương ${chapterProgress}.`,
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
    }, [chapterId, chapterProgress, lookupResult, saveVocabLoading, selectedSentence, selectedText, sourceLocale]);

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
    }, [chapterId, chapterProgress, lookupResult, saveSentenceLoading, selectedSentence, selectedText, sourceLocale]);

    const handlePlaySentence = useCallback(async (speed: number) => {
        if (!selectedSentence || audioLoading) return;

        setAudioLoading(true);
        setAudioError(null);

        try {
            const sentenceForAudio = selectedSentence.trim();
            if (sentenceForAudio.length > 200) {
                throw new Error('Câu này quá dài cho audio nhanh. Hãy chọn cụm ngắn hơn.');
            }

            const payload = await requestReaderSentenceTts({
                locale: sourceLocale,
                sentence_text: sentenceForAudio,
                speed,
                chapter_id: chapterId,
            });

            if (!payload.audio_url) {
                throw new Error(payload.detail || 'Không tạo được audio câu.');
            }

            const audio = audioRef.current;
            if (!audio) {
                throw new Error('Trình phát audio chưa sẵn sàng.');
            }

            if (audio.src !== payload.audio_url) {
                audio.src = payload.audio_url;
            }
            audio.currentTime = 0;
            await audio.play();
            setAudioPlaying(true);
        } catch (error: unknown) {
            setAudioError((error as Error)?.message || 'Không phát được audio câu.');
            setAudioPlaying(false);
        } finally {
            setAudioLoading(false);
        }
    }, [audioLoading, chapterId, selectedSentence, sourceLocale]);

    const handleLoadSourceReference = useCallback(async (textOverride?: string, sentenceOverride?: string) => {
        const sourceText = normalizeSelectionText(textOverride || selectedText);
        const sourceSentence = sentenceOverride ?? selectedSentence;
        if (sourceLocale === 'vi' || !chapterId || !sourceText || sourceReferenceLoading) return;

        setSourceReferenceLoading(true);
        setSourceReferenceError(null);
        try {
            const payload = await getReaderSourceReference({
                locale: sourceLocale,
                selected_text: sourceText,
                context_sentence: sourceSentence || undefined,
                chapter_id: chapterId,
            });
            setSourceReference(payload);
        } catch (error: unknown) {
            setSourceReferenceError((error as Error)?.message || 'Không tìm được đoạn gốc tiếng Việt tương ứng.');
        } finally {
            setSourceReferenceLoading(false);
        }
    }, [chapterId, selectedSentence, selectedText, sourceLocale, sourceReferenceLoading]);

    const openSourceReferencePanel = useCallback(() => {
        if (!selectedText || !chapterId || sourceLocale === 'vi') return;
        setPanelOpen(true);
        hideToolbar();
        if (isDesktop) {
            setPanelExpanded(true);
        }
        setLookupError(null);
        setSaveMessage(null);
        setSaveError(null);
        setAudioError(null);
        void handleLoadSourceReference(selectedText, selectedSentence);
    }, [chapterId, handleLoadSourceReference, hideToolbar, isDesktop, selectedText, sourceLocale]);

    const renderDiffText = useCallback(
        (value: { before: string; changed: string; after: string }, tone: 'cyan' | 'emerald') => (
            <div className="mt-2 whitespace-pre-wrap text-sm leading-7">
                <span>{value.before}</span>
                {value.changed && (
                    <mark
                        className={tone === 'cyan'
                            ? 'rounded bg-cyan-500/15 px-0.5 text-cyan-100'
                            : 'rounded bg-emerald-500/15 px-0.5 text-emerald-50'}
                    >
                        {value.changed}
                    </mark>
                )}
                <span>{value.after}</span>
            </div>
        ),
        [],
    );

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return undefined;

        const handleEnded = () => setAudioPlaying(false);
        const handlePause = () => setAudioPlaying(false);
        const handlePlay = () => setAudioPlaying(true);
        const handleError = () => {
            setAudioPlaying(false);
            setAudioError('Audio câu không tải được. Hãy thử lại.');
        };

        audio.addEventListener('ended', handleEnded);
        audio.addEventListener('pause', handlePause);
        audio.addEventListener('play', handlePlay);
        audio.addEventListener('error', handleError);

        return () => {
            audio.removeEventListener('ended', handleEnded);
            audio.removeEventListener('pause', handlePause);
            audio.removeEventListener('play', handlePlay);
            audio.removeEventListener('error', handleError);
        };
    }, []);

    useEffect(() => {
        const handlePointerUp = (event: MouseEvent | TouchEvent) => {
            if (shouldIgnoreSelectionTarget(event.target)) return;
            const triggerLookup = event instanceof MouseEvent && event.detail >= 2;
            window.setTimeout(() => readCurrentSelection(triggerLookup), 0);
        };

        const handleKeyUp = () => {
            window.setTimeout(() => readCurrentSelection(false), 0);
        };

        const handleScroll = () => {
            if (!panelOpen) hideToolbar();
        };

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                closeLookupPanel();
                return;
            }

            if (event.altKey && event.key.toLowerCase() === 'l' && !shouldIgnoreSelectionTarget(event.target)) {
                event.preventDefault();
                runLookup();
            }

            if (event.altKey && event.key.toLowerCase() === 'v' && !shouldIgnoreSelectionTarget(event.target)) {
                event.preventDefault();
                openSourceReferencePanel();
            }
        };

        const handlePointerDown = (event: MouseEvent | TouchEvent) => {
            if (!panelOpen) return;
            const target = event.target as Node | null;
            if (!target) return;
            if (panelRef.current?.contains(target)) return;
            if (toolbarRef.current?.contains(target)) return;
            closeLookupPanel();
        };

        const handleLookupRequest = () => {
            const snapshot = captureCurrentSelection();
            if (!snapshot) {
                if (selectedText) {
                    void runLookup(selectedText, selectedSentence);
                    return;
                }
                showSelectionRequiredError();
                return;
            }

            const { normalizedText, sentence, rect } = snapshot;
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
            window.setTimeout(() => {
                void runLookup(normalizedText, sentence);
            }, 0);
        };

        const handleSourceReferenceRequest = () => {
            const snapshot = captureCurrentSelection();
            if (!snapshot) {
                if (selectedText) {
                    openSourceReferencePanel();
                    return;
                }
                showSourceReferenceSelectionError();
                return;
            }

            const { normalizedText, sentence, rect } = snapshot;
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
            window.setTimeout(() => {
                setPanelOpen(true);
                hideToolbar();
                if (isDesktop) {
                    setPanelExpanded(true);
                }
                void handleLoadSourceReference(normalizedText, sentence);
            }, 0);
        };

        document.addEventListener('mouseup', handlePointerUp);
        document.addEventListener('touchend', handlePointerUp);
        document.addEventListener('mousedown', handlePointerDown);
        document.addEventListener('touchstart', handlePointerDown, { passive: true });
        document.addEventListener('keyup', handleKeyUp);
        window.addEventListener('scroll', handleScroll, { passive: true });
        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('reader-open-lookup-from-selection', handleLookupRequest as EventListener);
        window.addEventListener(SOURCE_REFERENCE_EVENT, handleSourceReferenceRequest as EventListener);

        return () => {
            document.removeEventListener('mouseup', handlePointerUp);
            document.removeEventListener('touchend', handlePointerUp);
            document.removeEventListener('mousedown', handlePointerDown);
            document.removeEventListener('touchstart', handlePointerDown);
            document.removeEventListener('keyup', handleKeyUp);
            window.removeEventListener('scroll', handleScroll);
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('reader-open-lookup-from-selection', handleLookupRequest as EventListener);
            window.removeEventListener(SOURCE_REFERENCE_EVENT, handleSourceReferenceRequest as EventListener);
        };
    }, [
        captureCurrentSelection,
        closeLookupPanel,
        handleLoadSourceReference,
        hideToolbar,
        isDesktop,
        openSourceReferencePanel,
        panelOpen,
        readCurrentSelection,
        resetLookupState,
        runLookup,
        selectedSentence,
        selectedText,
        showSelectionRequiredError,
        showSourceReferenceSelectionError,
    ]);

    useEffect(() => {
        const handleAudioState = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean }>).detail;
            setAudioActive(Boolean(detail?.active));
        };

        const handleAudioLayout = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean; height?: number }>).detail;
            setAudioPanelHeight(detail?.active ? Math.max(0, detail?.height || 0) : 0);
        };

        const updateViewport = () => setIsDesktop(window.innerWidth >= 768);

        updateViewport();
        window.addEventListener('resize', updateViewport);
        window.addEventListener('reader-audio-state', handleAudioState as EventListener);
        window.addEventListener(AUDIO_LAYOUT_EVENT, handleAudioLayout as EventListener);
        return () => {
            window.removeEventListener('resize', updateViewport);
            window.removeEventListener('reader-audio-state', handleAudioState as EventListener);
            window.removeEventListener(AUDIO_LAYOUT_EVENT, handleAudioLayout as EventListener);
        };
    }, []);

    useEffect(() => {
        if (isDesktop) return undefined;

        const handleMobilePanelEvent = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean; kind?: string }>).detail;
            if (!detail?.active || detail.kind === 'lookup') return;
            suppressMobilePanelBroadcastRef.current = true;
            hideToolbar();
            setPanelOpen(false);
        };

        window.addEventListener(MOBILE_PANEL_EVENT, handleMobilePanelEvent as EventListener);
        return () => window.removeEventListener(MOBILE_PANEL_EVENT, handleMobilePanelEvent as EventListener);
    }, [hideToolbar, isDesktop]);

    useEffect(() => {
        if (isDesktop) return;
        if (!panelOpen && suppressMobilePanelBroadcastRef.current) {
            suppressMobilePanelBroadcastRef.current = false;
            return;
        }

        window.dispatchEvent(new CustomEvent(MOBILE_PANEL_EVENT, {
            detail: {
                active: panelOpen,
                kind: 'lookup',
            },
        }));
    }, [isDesktop, panelOpen]);

    useEffect(() => {
        try {
            const seen = window.localStorage.getItem('reader-lookup-guide-v1');
            if (!seen) {
                setShowGuide(true);
            }
        } catch {
            setShowGuide(true);
        }
    }, []);

    const dismissGuide = useCallback(() => {
        setShowGuide(false);
        try {
            window.localStorage.setItem('reader-lookup-guide-v1', 'seen');
        } catch {
            // ignore localStorage failures
        }
    }, []);

    return (
        <>
            <audio ref={audioRef} preload="none" className="hidden" />

            {showGuide && !panelOpen && (
                <div className="fixed right-4 top-20 z-[63] max-w-[320px] md:right-6">
                    <div className="rounded-2xl border border-cyan-900/40 bg-[#081019]/95 p-4 shadow-[0_18px_60px_rgba(0,0,0,0.45)] backdrop-blur">
                        <div className="flex items-start gap-3">
                            <div className="min-w-0 flex-1">
                                <div className="text-[11px] font-mono uppercase tracking-[0.24em] text-cyan-300">
                                    Tra từ nhanh
                                </div>
                                <div className="mt-2 space-y-2 text-xs leading-5 text-gray-300">
                                    <div>Bôi đen từ hoặc cụm ngắn rồi bấm <span className="font-medium text-cyan-200">Tra nhanh</span>.</div>
                                    <div>Click đúp vào một từ ngắn để tra ngay.</div>
                                    <div>Hoặc nhấn <span className="font-mono text-cyan-200">Alt+L</span> sau khi đã chọn chữ.</div>
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={dismissGuide}
                                className="rounded-full border border-gray-800 p-2 text-gray-400 hover:border-cyan-500/40 hover:text-cyan-200"
                                aria-label="Đóng hướng dẫn tra từ"
                            >
                                <X size={14} />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {toolbarPosition && selectedText && (
                <div
                    ref={toolbarRef}
                    className="fixed z-[65] -translate-x-1/2"
                    style={{ top: `${toolbarPosition.top}px`, left: `${toolbarPosition.left}px` }}
                >
                    <div className="flex flex-wrap items-center justify-center gap-2 rounded-full border border-gray-800/70 bg-ash-950/95 px-2 py-2 shadow-[0_8px_30px_rgba(0,0,0,0.45)] backdrop-blur">
                        {sourceLocale !== 'vi' && preferSourceReference && (
                            <button
                                type="button"
                                onClick={openSourceReferencePanel}
                                className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-950/30 px-3 py-2 text-[11px] font-mono text-emerald-300 hover:border-emerald-400 hover:text-emerald-200"
                            >
                                <BookOpenText size={12} />
                                Gốc VI
                            </button>
                        )}
                        <button
                            type="button"
                            onClick={() => runLookup()}
                            className="inline-flex items-center gap-2 rounded-full border border-cyan-500/40 bg-ash-950/95 px-3 py-2 text-[11px] font-mono text-cyan-300 hover:border-cyan-400 hover:text-cyan-200"
                        >
                            <Search size={12} />
                            {dictionary.lookup.action}
                        </button>
                        {sourceLocale !== 'vi' && !preferSourceReference && (
                            <button
                                type="button"
                                onClick={openSourceReferencePanel}
                                className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-950/30 px-3 py-2 text-[11px] font-mono text-emerald-300 hover:border-emerald-400 hover:text-emerald-200"
                            >
                                <BookOpenText size={12} />
                                Gốc VI
                            </button>
                        )}
                    </div>
                </div>
            )}

            {panelOpen && (
                <div
                    ref={panelRef}
                    className="fixed inset-x-4 z-[64] md:left-6 md:right-auto"
                    style={{ top: `${panelTop}px`, bottom: `${panelBottom}px`, width: desktopPanelWidth }}
                >
                    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-cyan-900/40 bg-[#090d12]/95 shadow-[0_18px_60px_rgba(0,0,0,0.45)] backdrop-blur">
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
                            {isDesktop && (
                                <button
                                    type="button"
                                    onClick={() => setPanelExpanded((prev) => !prev)}
                                    className="rounded-full border border-gray-800 p-2 text-gray-400 hover:border-cyan-500/40 hover:text-cyan-200"
                                    title={panelExpanded ? 'Thu gọn panel đối chiếu' : 'Mở rộng panel đối chiếu'}
                                >
                                    {panelExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
                                </button>
                            )}
                            <button
                                type="button"
                                onClick={closeLookupPanel}
                                className="rounded-full border border-gray-800 p-2 text-gray-400 hover:border-cyan-500/40 hover:text-cyan-200"
                                title={dictionary.lookup.close}
                            >
                                <X size={14} />
                            </button>
                        </div>

                        {panelOpen && (
                            <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
                                <div className="rounded-xl border border-gray-800 bg-black/20 px-3 py-2">
                                    <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-gray-500">
                                        {dictionary.lookup.selected}
                                    </div>
                                    <div className="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-reader-text">
                                        {selectedText || dictionary.lookup.empty}
                                    </div>
                                    {selectedSentence && (
                                        <div className="mt-3 rounded-lg border border-ash-800 bg-ash-950/70 px-3 py-3 text-sm leading-7 text-ash-300">
                                            {selectedSentence}
                                        </div>
                                    )}
                                    <div className="mt-3 text-[10px] text-ash-500">
                                        Click đúp vào từ ngắn để tra ngay, hoặc dùng <span className="font-mono text-cyan-300">Alt+L</span> / <span className="font-mono text-emerald-300">Alt+V</span>.
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

                                {!lookupLoading && !lookupError && lookupResult && (
                                    <div className="rounded-xl border border-cyan-900/30 bg-cyan-950/10 px-3 py-3 text-sm text-gray-100">
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span className="text-base font-semibold text-white">{lookupResult.term}</span>
                                            {lookupResult.pos && (
                                                <span className="rounded-full border border-ash-700 px-2 py-1 text-[11px] font-mono text-ash-300">
                                                    {lookupResult.pos}
                                                </span>
                                            )}
                                        </div>

                                        {renderReadingBlock(sourceLocale, lookupResult)}

                                        <div className="mt-3 whitespace-pre-wrap leading-7 text-gray-100">
                                            {lookupResult.meaning_vi || 'Chưa có nghĩa ngắn cho mục này.'}
                                        </div>

                                        {lookupResult.notes && (
                                            <div className="mt-3 rounded-lg border border-ash-800 bg-black/20 px-3 py-3 text-xs leading-6 text-ash-300">
                                                {lookupResult.notes}
                                            </div>
                                        )}

                                        <div className="mt-3 text-[10px] font-mono uppercase tracking-[0.2em] text-cyan-400">
                                            Nguồn: {getLookupSourceLabel(lookupResult.source)}
                                        </div>
                                    </div>
                                )}

                                {audioError && (
                                    <div className="rounded-xl border border-red-900/40 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                                        {audioError}
                                    </div>
                                )}

                                {sourceReferenceError && (
                                    <div className="rounded-xl border border-red-900/40 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                                        {sourceReferenceError}
                                    </div>
                                )}

                                {sourceReference && (
                                    <div className="rounded-xl border border-emerald-900/40 bg-emerald-950/15 px-3 py-3 text-sm text-emerald-50">
                                        <div className="flex flex-wrap items-center justify-between gap-2">
                                            <div className="flex flex-wrap items-center gap-2">
                                                <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-emerald-300">
                                                    Đối chiếu bản gốc tiếng Việt
                                                </div>
                                                <button
                                                    type="button"
                                                    onClick={() => setSourceReferenceSwapOrder((prev) => !prev)}
                                                    className="inline-flex items-center gap-1 rounded-full border border-emerald-700/40 px-2 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-emerald-200 hover:bg-emerald-500/10"
                                                >
                                                    <Repeat size={10} />
                                                    Đảo vị trí
                                                </button>
                                            </div>
                                            <div className="rounded-full border border-emerald-700/40 px-2 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-emerald-200">
                                                {getSourceReferenceModeLabel(sourceReference.match_mode)}
                                            </div>
                                            <div
                                                className={`rounded-full border px-2 py-1 text-[10px] font-mono uppercase tracking-[0.16em] ${getSourceReferenceConfidenceClass(sourceReference.confidence)}`}
                                            >
                                                Confidence {getSourceReferenceConfidenceLabel(sourceReference.confidence)}
                                            </div>
                                        </div>
                                        <div className={`mt-3 grid gap-3 ${isDesktop && panelExpanded ? 'md:grid-cols-2' : 'grid-cols-1'}`}>
                                            {(sourceReferenceSwapOrder ? [
                                                {
                                                    key: 'source',
                                                    title: 'Bản gốc VI',
                                                    tone: 'emerald' as const,
                                                    content: sourceReference.source_excerpt,
                                                    segments: sourceReferenceDiff.right,
                                                },
                                                {
                                                    key: 'translation',
                                                    title: 'Bản dịch hiện tại',
                                                    tone: 'cyan' as const,
                                                    content: sourceReference.translated_excerpt,
                                                    segments: sourceReferenceDiff.left,
                                                },
                                            ] : [
                                                {
                                                    key: 'translation',
                                                    title: 'Bản dịch hiện tại',
                                                    tone: 'cyan' as const,
                                                    content: sourceReference.translated_excerpt,
                                                    segments: sourceReferenceDiff.left,
                                                },
                                                {
                                                    key: 'source',
                                                    title: 'Bản gốc VI',
                                                    tone: 'emerald' as const,
                                                    content: sourceReference.source_excerpt,
                                                    segments: sourceReferenceDiff.right,
                                                },
                                            ]).map((card) => card.content ? (
                                                <div
                                                    key={card.key}
                                                    className={`rounded-lg border px-3 py-3 ${
                                                        card.tone === 'cyan'
                                                            ? 'border-ash-800 bg-black/20'
                                                            : 'border-emerald-900/30 bg-black/20'
                                                    }`}
                                                >
                                                    <div className={`text-[10px] font-mono uppercase tracking-[0.18em] ${
                                                        card.tone === 'cyan' ? 'text-cyan-300' : 'text-emerald-300'
                                                    }`}>
                                                        {card.title}
                                                    </div>
                                                    {sourceReferenceDiff.hasDiff
                                                        ? renderDiffText(card.segments, card.tone)
                                                        : (
                                                            <div className={`mt-2 whitespace-pre-wrap text-sm leading-7 ${
                                                                card.tone === 'cyan' ? 'text-ash-300' : 'text-emerald-50'
                                                            }`}>
                                                                {card.content}
                                                            </div>
                                                        )}
                                                </div>
                                            ) : null)}
                                        </div>
                                        {typeof sourceReference.paragraph_index === 'number' && (
                                            <div className="mt-3 text-[10px] font-mono uppercase tracking-[0.2em] text-emerald-400">
                                                Đoạn #{sourceReference.paragraph_index + 1}
                                            </div>
                                        )}
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
                            </div>
                        )}

                        {panelOpen && (
                            <div className="border-t border-cyan-900/20 px-4 py-4">
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

                                    {sourceLocale !== 'vi' && (
                                        <button
                                            type="button"
                                            onClick={openSourceReferencePanel}
                                            disabled={!selectedText || !chapterId || sourceReferenceLoading}
                                            className="inline-flex items-center gap-2 rounded-lg border border-emerald-700/40 px-3 py-2 text-[11px] font-mono text-emerald-300 hover:bg-emerald-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                        >
                                            {sourceReferenceLoading ? <Loader2 size={12} className="animate-spin" /> : <BookOpenText size={12} />}
                                            Gốc VI
                                        </button>
                                    )}

                                    <button
                                        type="button"
                                        onClick={() => handlePlaySentence(1)}
                                        disabled={!selectedSentence || audioLoading}
                                        className="inline-flex items-center gap-2 rounded-lg border border-sky-700/40 px-3 py-2 text-[11px] font-mono text-sky-300 hover:bg-sky-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                        {audioLoading ? <Loader2 size={12} className="animate-spin" /> : <Volume2 size={12} />}
                                        Nghe 1x
                                    </button>

                                    <button
                                        type="button"
                                        onClick={() => handlePlaySentence(0.75)}
                                        disabled={!selectedSentence || audioLoading}
                                        className="inline-flex items-center gap-2 rounded-lg border border-sky-700/40 px-3 py-2 text-[11px] font-mono text-sky-300 hover:bg-sky-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                        {audioLoading ? <Loader2 size={12} className="animate-spin" /> : <Volume2 size={12} />}
                                        Nghe 0.75x
                                    </button>

                                    <button
                                        type="button"
                                        onClick={stopSentenceAudio}
                                        disabled={!audioPlaying}
                                        className="inline-flex items-center gap-2 rounded-lg border border-rose-700/40 px-3 py-2 text-[11px] font-mono text-rose-300 hover:bg-rose-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                        <Square size={12} />
                                        Dừng audio
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
                                    <div className="mt-2 text-[10px] text-emerald-300/80">
                                        Bôi đen đoạn dài rồi bấm <span className="font-mono text-emerald-300">Gốc VI</span> để đối chiếu trực tiếp, không cần tra AI trước.
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}
