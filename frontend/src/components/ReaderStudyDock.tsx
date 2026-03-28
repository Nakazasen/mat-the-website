"use client";

import Link from "next/link";
import {
    BookMarked,
    GraduationCap,
    GripHorizontal,
    Languages,
    Loader2,
    Quote,
    RefreshCcw,
    Search,
    Sparkles,
    X,
} from "lucide-react";
import {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
    type KeyboardEvent as ReactKeyboardEvent,
    type MouseEvent as ReactMouseEvent,
    type PointerEvent as ReactPointerEvent,
} from "react";

import { useLocale } from "@/context/LocaleContext";
import { getReaderLearningStats, type ReaderLearningStatsResponse } from "@/lib/reader-learning";

const DESKTOP_PANEL_STORAGE_KEY = "reader-study-dock-position-v1";
const DESKTOP_DEFAULT_POSITION = { top: 132, left: 16 };
const DESKTOP_PANEL_WIDTH = 392;
const DESKTOP_PANEL_MARGIN = 16;
const MOBILE_PANEL_EVENT = "reader-learning-mobile-panel";
const AUDIO_LAYOUT_EVENT = "reader-audio-layout";

function StudyLinks({ onNavigate }: { onNavigate?: () => void }) {
    const { localizePath } = useLocale();

    return (
        <div className="grid grid-cols-1 gap-2 p-3">
            <Link
                href={localizePath("/saved-vocab")}
                onClick={onNavigate}
                className="inline-flex items-center gap-2 rounded-xl border border-cyan-900/30 px-3 py-2 text-sm text-gray-200 hover:border-cyan-500/40 hover:text-cyan-200"
            >
                <BookMarked size={14} />
                Từ đã lưu
            </Link>
            <Link
                href={localizePath("/saved-sentences")}
                onClick={onNavigate}
                className="inline-flex items-center gap-2 rounded-xl border border-cyan-900/30 px-3 py-2 text-sm text-gray-200 hover:border-cyan-500/40 hover:text-cyan-200"
            >
                <Quote size={14} />
                Câu đã lưu
            </Link>
            <Link
                href={localizePath("/saved-vocab")}
                onClick={onNavigate}
                className="inline-flex items-center gap-2 rounded-xl border border-cyan-900/30 px-3 py-2 text-sm text-gray-200 hover:border-cyan-500/40 hover:text-cyan-200"
            >
                <RefreshCcw size={14} />
                Ôn tập nhanh
            </Link>
        </div>
    );
}

function LookupTips() {
    return (
        <div className="border-b border-cyan-900/20 px-4 py-3">
            <div className="flex items-center gap-2 text-cyan-300">
                <Sparkles size={14} />
                <span className="text-[11px] font-mono uppercase tracking-[0.24em]">Cách tra nhanh</span>
            </div>
            <div className="mt-3 space-y-2 text-xs leading-5 text-gray-300">
                <div>
                    1. Bôi đen từ hoặc cụm ngắn rồi bấm <span className="font-medium text-cyan-200">Tra nhanh</span>.
                </div>
                <div>2. Click đúp vào một từ ngắn để mở tra từ ngay.</div>
                <div>
                    3. Sau khi đã chọn chữ, nhấn <span className="font-mono text-cyan-200">Alt+L</span> để tra từ, hoặc bấm <span className="font-medium text-emerald-200">Gốc VI đang chọn</span> / <span className="font-mono text-emerald-200">Alt+V</span> để đối chiếu bản gốc.
                </div>
            </div>
        </div>
    );
}

function triggerLookupFromSelection() {
    window.dispatchEvent(new CustomEvent("reader-open-lookup-from-selection"));
}

function triggerSourceReferenceFromSelection() {
    window.dispatchEvent(new CustomEvent("reader-open-source-reference-from-selection"));
}

function LookupActionButtons({
    showSourceReference,
    onAfterTrigger,
}: {
    showSourceReference: boolean;
    onAfterTrigger?: () => void;
}) {
    const handleMouseDown = useCallback((event: ReactMouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        triggerLookupFromSelection();
        onAfterTrigger?.();
    }, [onAfterTrigger]);

    const handleTouchStart = useCallback(() => {
        triggerLookupFromSelection();
        onAfterTrigger?.();
    }, [onAfterTrigger]);

    const handleKeyDown = useCallback((event: ReactKeyboardEvent<HTMLButtonElement>) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            triggerLookupFromSelection();
            onAfterTrigger?.();
        }
    }, [onAfterTrigger]);

    const handleSourceMouseDown = useCallback((event: ReactMouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        triggerSourceReferenceFromSelection();
        onAfterTrigger?.();
    }, [onAfterTrigger]);

    const handleSourceTouchStart = useCallback(() => {
        triggerSourceReferenceFromSelection();
        onAfterTrigger?.();
    }, [onAfterTrigger]);

    const handleSourceKeyDown = useCallback((event: ReactKeyboardEvent<HTMLButtonElement>) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            triggerSourceReferenceFromSelection();
            onAfterTrigger?.();
        }
    }, [onAfterTrigger]);

    return (
        <div className="mx-3 mt-3 grid grid-cols-1 gap-2">
            {showSourceReference && (
                <button
                    type="button"
                    onMouseDown={handleSourceMouseDown}
                    onTouchStart={handleSourceTouchStart}
                    onKeyDown={handleSourceKeyDown}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200 hover:border-emerald-400 hover:bg-emerald-500/15"
                >
                    <BookMarked size={14} />
                    Gốc VI đang chọn
                </button>
            )}
            <button
                type="button"
                onMouseDown={handleMouseDown}
                onTouchStart={handleTouchStart}
                onKeyDown={handleKeyDown}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-cyan-500/40 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-200 hover:border-cyan-400 hover:bg-cyan-500/15"
            >
                <Search size={14} />
                Tra từ đang chọn
            </button>
        </div>
    );
}

function StudyStats({
    loading,
    error,
    stats,
}: {
    loading: boolean;
    error: string | null;
    stats: ReaderLearningStatsResponse | null;
}) {
    if (loading) {
        return (
            <div className="flex items-center gap-2 text-xs text-ash-400">
                <Loader2 size={12} className="animate-spin" />
                Đang tải thống kê...
            </div>
        );
    }

    if (error) {
        return <div className="text-xs leading-5 text-amber-300">{error}</div>;
    }

    if (!stats) {
        return <div className="text-xs leading-5 text-ash-400">Chưa có dữ liệu học tập.</div>;
    }

    return (
        <div className="grid grid-cols-3 gap-2 text-center">
            <div className="rounded-xl border border-cyan-900/20 bg-black/20 px-2 py-2">
                <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-ash-500">Từ</div>
                <div className="mt-1 text-lg font-semibold text-white">{stats.saved_vocab_count}</div>
            </div>
            <div className="rounded-xl border border-cyan-900/20 bg-black/20 px-2 py-2">
                <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-ash-500">Câu</div>
                <div className="mt-1 text-lg font-semibold text-white">{stats.saved_sentence_count}</div>
            </div>
            <div className="rounded-xl border border-cyan-900/20 bg-black/20 px-2 py-2">
                <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-ash-500">Đến hạn</div>
                <div className="mt-1 text-lg font-semibold text-toxic-green-DEFAULT">{stats.review_due_count}</div>
            </div>
        </div>
    );
}

export default function ReaderStudyDock() {
    const { locale } = useLocale();
    const desktopPanelRef = useRef<HTMLDivElement | null>(null);
    const draggingPointerIdRef = useRef<number | null>(null);
    const [stats, setStats] = useState<ReaderLearningStatsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [mobileOpen, setMobileOpen] = useState(false);
    const [audioActive, setAudioActive] = useState(false);
    const [audioPanelHeight, setAudioPanelHeight] = useState(0);
    const [isDesktop, setIsDesktop] = useState(false);
    const [dragging, setDragging] = useState(false);
    const [desktopPosition, setDesktopPosition] = useState(DESKTOP_DEFAULT_POSITION);
    const [mobileReaderPanelActive, setMobileReaderPanelActive] = useState(false);

    useEffect(() => {
        let mounted = true;
        setLoading(true);
        setError(null);

        getReaderLearningStats()
            .then((payload) => {
                if (!mounted) return;
                setStats(payload);
            })
            .catch((err: unknown) => {
                if (!mounted) return;
                setStats(null);
                setError((err as Error)?.message || "Không tải được thống kê học tập.");
            })
            .finally(() => {
                if (mounted) setLoading(false);
            });

        return () => {
            mounted = false;
        };
    }, []);

    useEffect(() => {
        const handleAudioState = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean }>).detail;
            setAudioActive(Boolean(detail?.active));
        };

        const handleAudioLayout = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean; height?: number }>).detail;
            setAudioPanelHeight(detail?.active ? Math.max(0, detail?.height || 0) : 0);
        };

        window.addEventListener("reader-audio-state", handleAudioState as EventListener);
        window.addEventListener(AUDIO_LAYOUT_EVENT, handleAudioLayout as EventListener);
        return () => {
            window.removeEventListener("reader-audio-state", handleAudioState as EventListener);
            window.removeEventListener(AUDIO_LAYOUT_EVENT, handleAudioLayout as EventListener);
        };
    }, []);

    useEffect(() => {
        const updateViewport = () => setIsDesktop(window.innerWidth >= 768);
        updateViewport();
        window.addEventListener("resize", updateViewport);
        return () => window.removeEventListener("resize", updateViewport);
    }, []);

    useEffect(() => {
        const handleMobilePanelEvent = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean; kind?: string }>).detail;
            setMobileReaderPanelActive(Boolean(detail?.active));
            if (detail?.active) {
                setMobileOpen(false);
            }
        };

        window.addEventListener(MOBILE_PANEL_EVENT, handleMobilePanelEvent as EventListener);
        return () => window.removeEventListener(MOBILE_PANEL_EVENT, handleMobilePanelEvent as EventListener);
    }, []);

    const mobileBottom = useMemo(() => {
        if (!audioActive) return 88;
        return Math.max(88, audioPanelHeight + 116);
    }, [audioActive, audioPanelHeight]);

    const mobileLearningButtonBottom = useMemo(() => {
        if (!audioActive) return mobileBottom;
        return Math.max(104, audioPanelHeight + 106);
    }, [audioActive, audioPanelHeight, mobileBottom]);

    const getDesktopMinTop = useCallback(() => {
        if (typeof window === "undefined") return DESKTOP_DEFAULT_POSITION.top;
        const header = document.querySelector("header");
        if (!(header instanceof HTMLElement)) {
            return DESKTOP_DEFAULT_POSITION.top;
        }
        const headerBottom = header.getBoundingClientRect().bottom;
        return Math.max(DESKTOP_DEFAULT_POSITION.top, Math.ceil(headerBottom + 12));
    }, []);

    const clampDesktopPosition = useCallback((position: { top: number; left: number }) => {
        if (typeof window === "undefined") return position;
        const panelHeight = desktopPanelRef.current?.offsetHeight ?? 620;
        const maxLeft = Math.max(DESKTOP_PANEL_MARGIN, window.innerWidth - DESKTOP_PANEL_WIDTH - DESKTOP_PANEL_MARGIN);
        const minTop = getDesktopMinTop();
        const maxTop = Math.max(minTop, window.innerHeight - panelHeight - DESKTOP_PANEL_MARGIN);
        return {
            left: Math.min(Math.max(DESKTOP_PANEL_MARGIN, position.left), maxLeft),
            top: Math.min(Math.max(minTop, position.top), maxTop),
        };
    }, [getDesktopMinTop]);

    useEffect(() => {
        if (!isDesktop) return;
        try {
            const raw = window.localStorage.getItem(DESKTOP_PANEL_STORAGE_KEY);
            if (!raw) return;
            const parsed = JSON.parse(raw) as { top?: number; left?: number };
            if (typeof parsed.top === "number" && typeof parsed.left === "number") {
                setDesktopPosition(clampDesktopPosition({ top: parsed.top, left: parsed.left }));
            }
        } catch {
            // ignore storage errors
        }
    }, [clampDesktopPosition, isDesktop]);

    useEffect(() => {
        if (!isDesktop) return;
        setDesktopPosition((prev) => clampDesktopPosition(prev));
    }, [clampDesktopPosition, isDesktop]);

    const persistDesktopPosition = useCallback((position: { top: number; left: number }) => {
        try {
            window.localStorage.setItem(DESKTOP_PANEL_STORAGE_KEY, JSON.stringify(position));
        } catch {
            // ignore storage errors
        }
    }, []);

    const handleDesktopDragStart = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
        if (!isDesktop) return;
        event.preventDefault();
        draggingPointerIdRef.current = event.pointerId;
        event.currentTarget.setPointerCapture(event.pointerId);
        const startX = event.clientX;
        const startY = event.clientY;
        const origin = desktopPosition;

        setDragging(true);

        const handleMove = (moveEvent: PointerEvent) => {
            if (draggingPointerIdRef.current !== null && moveEvent.pointerId !== draggingPointerIdRef.current) {
                return;
            }
            const next = clampDesktopPosition({
                left: origin.left + (moveEvent.clientX - startX),
                top: origin.top + (moveEvent.clientY - startY),
            });
            setDesktopPosition(next);
        };

        const handleUp = () => {
            setDragging(false);
            draggingPointerIdRef.current = null;
            window.removeEventListener("pointermove", handleMove);
            window.removeEventListener("pointerup", handleUp);
        };

        window.addEventListener("pointermove", handleMove);
        window.addEventListener("pointerup", handleUp);
    }, [clampDesktopPosition, desktopPosition, isDesktop]);

    useEffect(() => {
        if (!isDesktop) return;
        persistDesktopPosition(desktopPosition);
    }, [desktopPosition, isDesktop, persistDesktopPosition]);

    return (
        <>
            <div
                ref={desktopPanelRef}
                className="fixed z-[58] hidden md:block"
                style={{ top: `${desktopPosition.top}px`, left: `${desktopPosition.left}px`, width: `${DESKTOP_PANEL_WIDTH}px` }}
            >
                <div className="overflow-hidden rounded-2xl border border-cyan-900/30 bg-[#071018]/90 shadow-[0_18px_50px_rgba(0,0,0,0.38)] backdrop-blur">
                    <div
                        className={`border-b border-cyan-900/30 px-4 py-3 select-none touch-none ${dragging ? "cursor-grabbing" : "cursor-grab"}`}
                        onPointerDown={handleDesktopDragStart}
                    >
                        <div className="flex items-center justify-between gap-3">
                            <div className="flex items-center gap-2 text-cyan-300">
                                <Languages size={14} />
                                <span className="text-[11px] font-mono uppercase tracking-[0.28em]">Learning</span>
                            </div>
                            <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-[0.2em] text-ash-500">
                                <GripHorizontal size={14} />
                                Kéo để di chuyển
                            </div>
                        </div>
                        <p className="mt-2 max-w-[260px] text-xs leading-5 text-gray-400">
                            Tra từ, lưu câu và ôn lại ngay trong lúc đọc. Khu này sẽ là nền cho grammar hints
                            và SRS ở bước sau.
                        </p>
                    </div>

                    <div className="border-b border-cyan-900/20 px-4 py-3">
                        <StudyStats loading={loading} error={error} stats={stats} />
                    </div>

                    <LookupTips />
                    <LookupActionButtons showSourceReference={locale !== "vi"} />
                    <StudyLinks />
                </div>
            </div>

            {!mobileReaderPanelActive && (
                <div
                    className={`fixed z-[58] md:hidden ${audioActive ? "right-4" : "left-4"}`}
                    style={{ bottom: `${mobileLearningButtonBottom}px` }}
                >
                    <button
                        type="button"
                        onClick={() => setMobileOpen(true)}
                        className={`inline-flex items-center rounded-full border border-cyan-500/30 bg-[#071018]/95 text-cyan-200 shadow-[0_10px_30px_rgba(0,0,0,0.38)] backdrop-blur ${
                            audioActive ? "gap-1.5 px-3 py-2 text-xs" : "gap-2 px-4 py-3 text-sm"
                        }`}
                    >
                        <GraduationCap size={audioActive ? 14 : 16} />
                        <span className={audioActive ? "font-mono uppercase tracking-[0.2em]" : ""}>Learning</span>
                    </button>
                </div>
            )}

            {mobileOpen && (
                <div className="fixed inset-0 z-[70] md:hidden">
                    <button
                        type="button"
                        aria-label="Đóng Learning"
                        onClick={() => setMobileOpen(false)}
                        className="absolute inset-0 bg-black/60"
                    />

                    <div
                        className="absolute left-0 right-0 rounded-t-3xl border-t border-cyan-900/40 bg-[#071018]/98 shadow-[0_-20px_60px_rgba(0,0,0,0.55)]"
                        style={{ bottom: `${mobileBottom - 12}px` }}
                    >
                        <div className="flex items-center gap-2 border-b border-cyan-900/30 px-4 py-4">
                            <Languages size={16} className="text-cyan-300" />
                            <div className="flex-1">
                                <div className="text-sm font-semibold text-cyan-200">Learning</div>
                                <div className="text-xs text-gray-400">
                                    Tra nhanh, lưu lại và ôn tập ngay trên điện thoại.
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={() => setMobileOpen(false)}
                                className="rounded-full border border-gray-800 p-2 text-gray-400 hover:border-cyan-500/40 hover:text-cyan-200"
                            >
                                <X size={14} />
                            </button>
                        </div>

                        <div className="max-h-[60vh] overflow-y-auto">
                            <div className="border-b border-cyan-900/20 px-4 py-4">
                                <StudyStats loading={loading} error={error} stats={stats} />
                            </div>
                            <LookupTips />
                            <LookupActionButtons
                                showSourceReference={locale !== "vi"}
                                onAfterTrigger={() => setMobileOpen(false)}
                            />
                            <StudyLinks onNavigate={() => setMobileOpen(false)} />
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
