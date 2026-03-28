'use client';

import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from 'react';
import { BookText, BrainCircuit, Loader2, Quote, Search, Square, Volume2, X } from 'lucide-react';

import type { Locale } from '@/lib/i18n/config';
import {
    getReaderGrammarHints,
    getReaderSentenceInsight,
    requestReaderSentenceTts,
    saveReaderSentence,
    type ReaderGrammarHint,
    type ReaderGrammarHintsResponse,
    type ReaderSentenceInsightResponse,
} from '@/lib/reader-learning';
import { findSentenceFromPoint, shouldIgnoreSelectionTarget } from '@/lib/reader-selection';

interface ReaderSentenceModeProps {
    chapterId?: number;
    chapterProgress: number;
    containerRef: RefObject<HTMLElement | null>;
    sourceLocale: Locale;
}

const MOBILE_PANEL_EVENT = 'reader-learning-mobile-panel';

interface CachedSentenceAnalysis {
    insight: ReaderSentenceInsightResponse | null;
    grammar: ReaderGrammarHintsResponse | null;
}

function getInsightSourceLabel(source?: string | null): string {
    if (source === 'cache') return 'Cache';
    if (source === 'rule_based') return 'Rule-based';
    if (source === 'ai') return 'AI';
    return 'Unknown';
}

function getHintCategoryLabel(category: ReaderGrammarHint['category']): string {
    switch (category) {
        case 'phrasal_verb':
            return 'Phrasal verb';
        case 'idiom':
            return 'Idiom';
        case 'collocation':
            return 'Collocation';
        case 'conjugation':
            return 'Chia động từ';
        case 'aspect':
            return 'Thể / Aspect';
        case 'tone':
            return 'Sắc thái';
        case 'structure':
            return 'Cấu trúc';
        default:
            return 'Ngữ pháp';
    }
}

export default function ReaderSentenceMode({
    chapterId,
    chapterProgress,
    containerRef,
    sourceLocale,
}: ReaderSentenceModeProps) {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const cacheRef = useRef<Map<string, CachedSentenceAnalysis>>(new Map());
    const suppressMobilePanelBroadcastRef = useRef(false);

    const [sentenceText, setSentenceText] = useState('');
    const [toolbarPosition, setToolbarPosition] = useState<{ top: number; left: number } | null>(null);
    const [panelOpen, setPanelOpen] = useState(false);
    const [insight, setInsight] = useState<ReaderSentenceInsightResponse | null>(null);
    const [grammarHints, setGrammarHints] = useState<ReaderGrammarHintsResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [grammarLoading, setGrammarLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [saveLoading, setSaveLoading] = useState(false);
    const [saveMessage, setSaveMessage] = useState<string | null>(null);
    const [audioLoading, setAudioLoading] = useState(false);
    const [audioError, setAudioError] = useState<string | null>(null);
    const [audioPlaying, setAudioPlaying] = useState(false);
    const [audioActive, setAudioActive] = useState(false);
    const [isDesktop, setIsDesktop] = useState(false);

    const canPlayAudio = useMemo(
        () => sentenceText.trim().length > 0 && sentenceText.trim().length <= 200,
        [sentenceText],
    );

    const panelBottom = useMemo(() => {
        if (audioActive) return isDesktop ? 226 : 196;
        return isDesktop ? 96 : 88;
    }, [audioActive, isDesktop]);

    const panelTop = useMemo(() => (isDesktop ? 92 : 80), [isDesktop]);

    const stopAudio = useCallback(() => {
        if (!audioRef.current) return;
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        setAudioPlaying(false);
    }, []);

    const resetAnalysisState = useCallback(() => {
        setInsight(null);
        setGrammarHints(null);
        setError(null);
        setSaveMessage(null);
        setAudioError(null);
        stopAudio();
    }, [stopAudio]);

    const handleSentencePick = useCallback((sentence: string, clientX: number, clientY: number) => {
        const normalizedSentence = sentence.trim();
        if (!normalizedSentence) return;

        setSentenceText((previous) => {
            if (previous !== normalizedSentence) {
                resetAnalysisState();
                setPanelOpen(false);
            }
            return normalizedSentence;
        });

        setToolbarPosition({
            top: Math.max(16, clientY + window.scrollY - 48),
            left: Math.max(48, clientX + window.scrollX),
        });
    }, [resetAnalysisState]);

    const runSentenceAnalysis = useCallback(async () => {
        const normalizedSentence = sentenceText.trim();
        if (!normalizedSentence || loading) return;

        setToolbarPosition(null);
        setPanelOpen(true);
        setError(null);
        setSaveMessage(null);
        setAudioError(null);
        stopAudio();

        const cached = cacheRef.current.get(normalizedSentence);
        if (cached) {
            setInsight(cached.insight);
            setGrammarHints(cached.grammar);
            return;
        }

        setLoading(true);
        setGrammarLoading(true);
        setInsight(null);
        setGrammarHints(null);

        try {
            const insightPayload = await getReaderSentenceInsight({
                locale: sourceLocale,
                sentence_text: normalizedSentence,
                chapter_id: chapterId,
            });
            setInsight(insightPayload);

            let grammarPayload: ReaderGrammarHintsResponse | null = null;
            try {
                grammarPayload = await getReaderGrammarHints({
                    locale: sourceLocale,
                    sentence_text: normalizedSentence,
                    chapter_id: chapterId,
                });
                setGrammarHints(grammarPayload);
            } catch {
                grammarPayload = {
                    sentence_text: normalizedSentence,
                    locale: sourceLocale,
                    hints: [],
                    source: 'rule_based',
                };
                setGrammarHints(grammarPayload);
            }

            cacheRef.current.set(normalizedSentence, {
                insight: insightPayload,
                grammar: grammarPayload,
            });
        } catch (err: unknown) {
            setError((err as Error)?.message || 'Không phân tích được câu này.');
        } finally {
            setLoading(false);
            setGrammarLoading(false);
        }
    }, [chapterId, loading, sentenceText, sourceLocale, stopAudio]);

    const handleSaveSentence = useCallback(async () => {
        if (!sentenceText || saveLoading) return;

        setSaveLoading(true);
        setSaveMessage(null);
        setError(null);

        try {
            await saveReaderSentence({
                locale: sourceLocale,
                sentence_text: sentenceText,
                meaning_vi: insight?.meaning_vi || undefined,
                note: `Lưu từ sentence mode ở chương ${chapterProgress}.`,
                chapter_id: chapterId,
            });
            setSaveMessage('Đã lưu câu vào kho học tập.');
        } catch (err: unknown) {
            setError((err as Error)?.message || 'Không lưu được câu này.');
        } finally {
            setSaveLoading(false);
        }
    }, [chapterId, chapterProgress, insight?.meaning_vi, saveLoading, sentenceText, sourceLocale]);

    const handlePlay = useCallback(async (speed: number) => {
        if (!sentenceText || audioLoading) return;
        if (sentenceText.length > 200) {
            setAudioError('Câu này quá dài cho audio nhanh. Hãy chọn cụm ngắn hơn.');
            return;
        }

        setAudioLoading(true);
        setAudioError(null);

        try {
            const payload = await requestReaderSentenceTts({
                locale: sourceLocale,
                sentence_text: sentenceText,
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
        } catch (err: unknown) {
            setAudioError((err as Error)?.message || 'Không phát được audio câu.');
            setAudioPlaying(false);
        } finally {
            setAudioLoading(false);
        }
    }, [audioLoading, chapterId, sentenceText, sourceLocale]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return undefined;

        const handleEnded = () => setAudioPlaying(false);
        const handlePause = () => setAudioPlaying(false);
        const handlePlay = () => setAudioPlaying(true);

        audio.addEventListener('ended', handleEnded);
        audio.addEventListener('pause', handlePause);
        audio.addEventListener('play', handlePlay);

        return () => {
            audio.removeEventListener('ended', handleEnded);
            audio.removeEventListener('pause', handlePause);
            audio.removeEventListener('play', handlePlay);
        };
    }, []);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return undefined;

        const handleClick = (event: MouseEvent) => {
            if (shouldIgnoreSelectionTarget(event.target)) return;
            const selectionText = window.getSelection()?.toString().trim();
            if (selectionText) return;

            const sentence = findSentenceFromPoint(container, event.target, event.clientX, event.clientY);
            if (!sentence || sentence.length < 2) return;

            handleSentencePick(sentence, event.clientX, event.clientY);
        };

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setToolbarPosition(null);
                setPanelOpen(false);
                stopAudio();
            }
        };

        container.addEventListener('click', handleClick);
        window.addEventListener('keydown', handleKeyDown);

        return () => {
            container.removeEventListener('click', handleClick);
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [containerRef, handleSentencePick, stopAudio]);

    useEffect(() => {
        const handleAudioState = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean }>).detail;
            setAudioActive(Boolean(detail?.active));
        };

        const updateViewport = () => setIsDesktop(window.innerWidth >= 768);

        updateViewport();
        window.addEventListener('resize', updateViewport);
        window.addEventListener('reader-audio-state', handleAudioState as EventListener);
        return () => {
            window.removeEventListener('resize', updateViewport);
            window.removeEventListener('reader-audio-state', handleAudioState as EventListener);
        };
    }, []);

    useEffect(() => {
        if (isDesktop) return undefined;

        const handleMobilePanelEvent = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean; kind?: string }>).detail;
            if (!detail?.active || detail.kind === 'sentence') return;
            suppressMobilePanelBroadcastRef.current = true;
            setToolbarPosition(null);
            setPanelOpen(false);
            stopAudio();
        };

        window.addEventListener(MOBILE_PANEL_EVENT, handleMobilePanelEvent as EventListener);
        return () => window.removeEventListener(MOBILE_PANEL_EVENT, handleMobilePanelEvent as EventListener);
    }, [isDesktop, stopAudio]);

    useEffect(() => {
        if (isDesktop) return;
        if (!panelOpen && suppressMobilePanelBroadcastRef.current) {
            suppressMobilePanelBroadcastRef.current = false;
            return;
        }

        window.dispatchEvent(new CustomEvent(MOBILE_PANEL_EVENT, {
            detail: {
                active: panelOpen,
                kind: 'sentence',
            },
        }));
    }, [isDesktop, panelOpen]);

    return (
        <>
            <audio ref={audioRef} preload="none" className="hidden" />

            {toolbarPosition && sentenceText && !panelOpen && (
                <div
                    className="fixed z-[65] -translate-x-1/2"
                    style={{ top: `${toolbarPosition.top}px`, left: `${toolbarPosition.left}px` }}
                >
                    <button
                        type="button"
                        onClick={() => void runSentenceAnalysis()}
                        className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-ash-950/95 px-3 py-2 text-[11px] font-mono text-emerald-300 shadow-[0_8px_30px_rgba(0,0,0,0.45)] backdrop-blur hover:border-emerald-400 hover:text-emerald-200"
                    >
                        <BrainCircuit size={12} />
                        Phân tích câu
                    </button>
                </div>
            )}

            {panelOpen && (
                <div
                    className="fixed inset-x-4 z-[63] md:left-auto md:right-6 md:w-[430px]"
                    style={{ top: `${panelTop}px`, bottom: `${panelBottom}px` }}
                >
                    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-emerald-900/40 bg-[#0a1012]/95 shadow-[0_18px_60px_rgba(0,0,0,0.45)] backdrop-blur">
                        <div className="flex items-center gap-2 border-b border-emerald-900/30 px-4 py-3">
                            <BookText size={15} className="text-emerald-300" />
                            <div className="min-w-0 flex-1">
                                <div className="text-[11px] font-mono uppercase tracking-[0.25em] text-emerald-300">
                                    Sentence Mode
                                </div>
                                <div className="truncate text-[10px] text-gray-500">
                                    Chỉ phân tích khi bạn bấm nút, không tự đốt token mỗi lần chạm.
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={() => {
                                    setPanelOpen(false);
                                    setToolbarPosition(null);
                                    stopAudio();
                                }}
                                className="rounded-full border border-gray-800 p-2 text-gray-400 hover:border-emerald-500/40 hover:text-emerald-200"
                                title="Đóng"
                            >
                                <X size={14} />
                            </button>
                        </div>

                        <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
                            <div className="rounded-xl border border-gray-800 bg-black/20 px-3 py-3">
                                <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-gray-500">
                                    Câu đang học
                                </div>
                                <div className="mt-2 text-sm leading-7 text-reader-text">
                                    {sentenceText}
                                </div>
                            </div>

                            {loading && (
                                <div className="flex items-center gap-2 rounded-xl border border-emerald-900/30 bg-emerald-950/10 px-3 py-3 text-sm text-emerald-200">
                                    <Loader2 size={14} className="animate-spin" />
                                    Đang phân tích nghĩa ngắn của câu...
                                </div>
                            )}

                            {!loading && error && (
                                <div className="rounded-xl border border-red-900/40 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                                    {error}
                                </div>
                            )}

                            {!loading && !error && insight && (
                                <div className="rounded-xl border border-emerald-900/30 bg-emerald-950/10 px-3 py-3 text-sm text-gray-100">
                                    <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-emerald-400">
                                        Nguồn nghĩa: {getInsightSourceLabel(insight.source)}
                                    </div>

                                    <div className="mt-3 whitespace-pre-wrap leading-7 text-gray-100">
                                        {insight.meaning_vi || 'Chưa có diễn giải ngắn cho câu này.'}
                                    </div>

                                    {insight.notes && (
                                        <div className="mt-3 rounded-lg border border-ash-800 bg-black/20 px-3 py-3 text-xs leading-6 text-ash-300">
                                            {insight.notes}
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="rounded-xl border border-cyan-900/30 bg-cyan-950/10 px-3 py-3">
                                <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-[0.2em] text-cyan-300">
                                    <BrainCircuit size={12} />
                                    Grammar Hints
                                    <span className="ml-auto text-ash-500">
                                        {grammarHints ? getInsightSourceLabel(grammarHints.source) : '...'}
                                    </span>
                                </div>

                                {grammarLoading && (
                                    <div className="mt-3 flex items-center gap-2 text-sm text-cyan-200">
                                        <Loader2 size={14} className="animate-spin" />
                                        Đang tìm grammar hints...
                                    </div>
                                )}

                                {!grammarLoading && grammarHints?.hints?.length ? (
                                    <div className="mt-3 space-y-2">
                                        {grammarHints.hints.map((hint, index) => (
                                            <div
                                                key={`${hint.category}-${index}-${hint.title}`}
                                                className="rounded-lg border border-cyan-900/20 bg-black/20 px-3 py-3"
                                            >
                                                <div className="flex flex-wrap items-center gap-2">
                                                    <span className="text-sm font-semibold text-white">{hint.title}</span>
                                                    <span className="rounded-full border border-cyan-700/30 px-2 py-1 text-[10px] font-mono uppercase tracking-[0.15em] text-cyan-200">
                                                        {getHintCategoryLabel(hint.category)}
                                                    </span>
                                                </div>
                                                <div className="mt-2 text-xs leading-6 text-ash-300">
                                                    {hint.explanation_vi}
                                                </div>
                                                {hint.example_fragment && (
                                                    <div className="mt-2 rounded-lg border border-ash-800 bg-ash-950/70 px-3 py-2 text-xs leading-6 text-ash-400">
                                                        {hint.example_fragment}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    !grammarLoading && (
                                        <div className="mt-3 text-xs leading-6 text-ash-400">
                                            Chưa thấy điểm ngữ pháp nổi bật trong câu này.
                                        </div>
                                    )
                                )}
                            </div>

                            {audioError && (
                                <div className="rounded-xl border border-red-900/40 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                                    {audioError}
                                </div>
                            )}

                            {saveMessage && (
                                <div className="rounded-xl border border-green-900/40 bg-green-950/20 px-3 py-3 text-sm text-green-200">
                                    {saveMessage}
                                </div>
                            )}
                        </div>

                        <div className="border-t border-emerald-900/20 px-4 py-4">
                            <div className="flex flex-wrap gap-2">
                                <button
                                    type="button"
                                    onClick={() => handlePlay(1)}
                                    disabled={!canPlayAudio || audioLoading}
                                    className="inline-flex items-center gap-2 rounded-lg border border-sky-700/40 px-3 py-2 text-[11px] font-mono text-sky-300 hover:bg-sky-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {audioLoading ? <Loader2 size={12} className="animate-spin" /> : <Volume2 size={12} />}
                                    Nghe 1x
                                </button>

                                <button
                                    type="button"
                                    onClick={() => handlePlay(0.75)}
                                    disabled={!canPlayAudio || audioLoading}
                                    className="inline-flex items-center gap-2 rounded-lg border border-sky-700/40 px-3 py-2 text-[11px] font-mono text-sky-300 hover:bg-sky-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {audioLoading ? <Loader2 size={12} className="animate-spin" /> : <Volume2 size={12} />}
                                    Nghe 0.75x
                                </button>

                                <button
                                    type="button"
                                    onClick={stopAudio}
                                    disabled={!audioPlaying}
                                    className="inline-flex items-center gap-2 rounded-lg border border-rose-700/40 px-3 py-2 text-[11px] font-mono text-rose-300 hover:bg-rose-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    <Square size={12} />
                                    Dừng
                                </button>

                                <button
                                    type="button"
                                    onClick={handleSaveSentence}
                                    disabled={!sentenceText || saveLoading}
                                    className="inline-flex items-center gap-2 rounded-lg border border-amber-700/40 px-3 py-2 text-[11px] font-mono text-amber-300 hover:bg-amber-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {saveLoading ? <Loader2 size={12} className="animate-spin" /> : <Quote size={12} />}
                                    Lưu câu
                                </button>

                                <button
                                    type="button"
                                    onClick={() => {
                                        setPanelOpen(false);
                                        setToolbarPosition(null);
                                    }}
                                    className="ml-auto inline-flex items-center gap-2 rounded-lg border border-gray-800 px-3 py-2 text-[11px] font-mono text-gray-300 hover:border-emerald-500/30 hover:text-emerald-200"
                                >
                                    <Search size={12} />
                                    Chọn câu khác
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
