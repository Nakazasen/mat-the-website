"use client";

import Link from "next/link";
import {
    BookMarked,
    ChevronLeft,
    GraduationCap,
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
} from "react";

import { useLocale } from "@/context/LocaleContext";
import { useTheme } from "@/context/ThemeContext";
import { getReaderLearningStats, type ReaderLearningStatsResponse } from "@/lib/reader-learning";

const DESKTOP_COLLAPSED_STORAGE_KEY = "reader-study-dock-collapsed-v1";
const DESKTOP_FLOATING_BUTTON_STORAGE_KEY = "reader-study-dock-button-position-v1";
const DESKTOP_PANEL_LAYOUT_EVENT = "reader-study-dock-layout";
const DESKTOP_PANEL_MIN_WIDTH = 248;
const DESKTOP_PANEL_MAX_WIDTH = 360;
const DESKTOP_PANEL_MARGIN = 16;
const DESKTOP_BUTTON_SIZE = 56;
const MOBILE_PANEL_EVENT = "reader-learning-mobile-panel";
const AUDIO_LAYOUT_EVENT = "reader-audio-layout";

interface FloatingPosition {
    x: number;
    y: number;
}

interface DesktopButtonDragState {
    offsetX: number;
    offsetY: number;
    startX: number;
    startY: number;
}

function getDefaultDesktopButtonPosition(): FloatingPosition {
    if (typeof window === "undefined") {
        return { x: DESKTOP_PANEL_MARGIN, y: 0 };
    }

    return {
        x: DESKTOP_PANEL_MARGIN,
        y: Math.max(DESKTOP_PANEL_MARGIN, window.innerHeight - DESKTOP_BUTTON_SIZE - 32),
    };
}

function clampDesktopButtonPosition(position: FloatingPosition): FloatingPosition {
    if (typeof window === "undefined") return position;

    return {
        x: Math.min(
            Math.max(position.x, DESKTOP_PANEL_MARGIN),
            window.innerWidth - DESKTOP_BUTTON_SIZE - DESKTOP_PANEL_MARGIN,
        ),
        y: Math.min(
            Math.max(position.y, DESKTOP_PANEL_MARGIN),
            window.innerHeight - DESKTOP_BUTTON_SIZE - DESKTOP_PANEL_MARGIN,
        ),
    };
}

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
                    3. Sau khi chọn chữ, nhấn <span className="font-mono text-cyan-200">Alt+L</span> để tra từ, hoặc bấm <span className="font-medium text-emerald-200">Gốc VI đồng chữ</span> / <span className="font-mono text-emerald-200">Alt+V</span> để đối chiếu bản gốc.
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
                    Gốc VI đồng chữ
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
    const { isLearningEnabled } = useTheme();
    const desktopButtonRef = useRef<HTMLButtonElement | null>(null);
    const desktopButtonMovedRef = useRef(false);
    const [stats, setStats] = useState<ReaderLearningStatsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [mobileOpen, setMobileOpen] = useState(false);
    const [audioActive, setAudioActive] = useState(false);
    const [audioPanelHeight, setAudioPanelHeight] = useState(0);
    const [isDesktop, setIsDesktop] = useState(false);
    const [viewportWidth, setViewportWidth] = useState(0);
    const [viewportHeight, setViewportHeight] = useState(0);
    const [desktopCollapsed, setDesktopCollapsed] = useState(false);
    const [desktopButtonPosition, setDesktopButtonPosition] = useState<FloatingPosition>({
        x: DESKTOP_PANEL_MARGIN,
        y: 0,
    });
    const [desktopButtonHasCustomPosition, setDesktopButtonHasCustomPosition] = useState(false);
    const [desktopButtonDragState, setDesktopButtonDragState] = useState<DesktopButtonDragState | null>(null);
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
        const updateViewport = () => {
            const width = window.innerWidth;
            const height = window.innerHeight;
            const desktop = width >= 960;

            setViewportWidth(width);
            setViewportHeight(height);
            setIsDesktop(desktop);
            setDesktopButtonPosition((previous) => (
                desktopButtonHasCustomPosition
                    ? clampDesktopButtonPosition(previous)
                    : getDefaultDesktopButtonPosition()
            ));
        };

        updateViewport();
        window.addEventListener("resize", updateViewport);
        return () => window.removeEventListener("resize", updateViewport);
    }, [desktopButtonHasCustomPosition]);

    useEffect(() => {
        if (isDesktop) {
            setMobileOpen(false);
        }
    }, [isDesktop]);

    useEffect(() => {
        try {
            const collapsedRaw = window.localStorage.getItem(DESKTOP_COLLAPSED_STORAGE_KEY);
            if (collapsedRaw !== null) {
                setDesktopCollapsed(collapsedRaw === "true");
            }

            const buttonRaw = window.localStorage.getItem(DESKTOP_FLOATING_BUTTON_STORAGE_KEY);
            if (!buttonRaw) return;

            const parsed = JSON.parse(buttonRaw) as { x?: number; y?: number };
            if (typeof parsed.x === "number" && typeof parsed.y === "number") {
                setDesktopButtonPosition(clampDesktopButtonPosition({ x: parsed.x, y: parsed.y }));
                setDesktopButtonHasCustomPosition(true);
            }
        } catch {
            // ignore storage errors
        }
    }, []);

    useEffect(() => {
        try {
            window.localStorage.setItem(DESKTOP_COLLAPSED_STORAGE_KEY, String(desktopCollapsed));
        } catch {
            // ignore storage errors
        }
    }, [desktopCollapsed]);

    useEffect(() => {
        if (!desktopButtonHasCustomPosition) return;

        try {
            window.localStorage.setItem(
                DESKTOP_FLOATING_BUTTON_STORAGE_KEY,
                JSON.stringify(desktopButtonPosition),
            );
        } catch {
            // ignore storage errors
        }
    }, [desktopButtonHasCustomPosition, desktopButtonPosition]);

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

    useEffect(() => {
        if (!desktopButtonDragState) return;

        const handlePointerMove = (event: PointerEvent) => {
            if (
                Math.abs(event.clientX - desktopButtonDragState.startX) > 3
                || Math.abs(event.clientY - desktopButtonDragState.startY) > 3
            ) {
                desktopButtonMovedRef.current = true;
            }

            setDesktopButtonPosition(clampDesktopButtonPosition({
                x: event.clientX - desktopButtonDragState.offsetX,
                y: event.clientY - desktopButtonDragState.offsetY,
            }));
        };

        const handlePointerUp = () => {
            setDesktopButtonDragState(null);
            if (desktopButtonMovedRef.current) {
                setDesktopButtonHasCustomPosition(true);
            }
        };

        window.addEventListener("pointermove", handlePointerMove);
        window.addEventListener("pointerup", handlePointerUp);
        return () => {
            window.removeEventListener("pointermove", handlePointerMove);
            window.removeEventListener("pointerup", handlePointerUp);
        };
    }, [desktopButtonDragState]);

    const mobileBottom = useMemo(() => {
        if (!audioActive) return 88;
        return Math.max(88, audioPanelHeight + 116);
    }, [audioActive, audioPanelHeight]);

    const mobileLearningButtonBottom = useMemo(() => {
        if (!audioActive) return mobileBottom;
        return Math.max(104, audioPanelHeight + 106);
    }, [audioActive, audioPanelHeight, mobileBottom]);

    const desktopPanelWidth = useMemo(() => {
        if (!isDesktop) return DESKTOP_PANEL_MAX_WIDTH;
        return Math.min(
            DESKTOP_PANEL_MAX_WIDTH,
            Math.max(DESKTOP_PANEL_MIN_WIDTH, Math.round(viewportWidth * 0.26)),
        );
    }, [isDesktop, viewportWidth]);

    const desktopPanelTop = useMemo(() => {
        if (!isDesktop || typeof window === "undefined") return 88;

        const header = document.querySelector("header");
        if (!(header instanceof HTMLElement)) {
            return 88;
        }

        return Math.max(88, Math.ceil(header.getBoundingClientRect().bottom + 12));
    }, [isDesktop, viewportHeight, viewportWidth]);

    const desktopPanelMaxHeight = useMemo(() => {
        if (!isDesktop) return 0;
        return Math.max(360, viewportHeight - desktopPanelTop - DESKTOP_PANEL_MARGIN);
    }, [desktopPanelTop, isDesktop, viewportHeight]);

    useEffect(() => {
        const detail = {
            open: isDesktop && !desktopCollapsed,
            offset: isDesktop && !desktopCollapsed ? desktopPanelWidth + 40 : 0,
        };

        window.dispatchEvent(new CustomEvent(DESKTOP_PANEL_LAYOUT_EVENT, { detail }));
        return () => {
            window.dispatchEvent(new CustomEvent(DESKTOP_PANEL_LAYOUT_EVENT, {
                detail: { open: false, offset: 0 },
            }));
        };
    }, [desktopCollapsed, desktopPanelWidth, isDesktop]);

    if (!isLearningEnabled) return null;

    return (
        <>
            {isDesktop && !desktopCollapsed && (
                <div
                    className="fixed z-[58]"
                    style={{
                        top: `${desktopPanelTop}px`,
                        left: `${DESKTOP_PANEL_MARGIN}px`,
                        width: `${desktopPanelWidth}px`,
                    }}
                >
                    <div
                        className="flex flex-col overflow-hidden rounded-2xl border border-cyan-900/30 bg-[#071018]/90 shadow-[0_18px_50px_rgba(0,0,0,0.38)] backdrop-blur"
                        style={{ maxHeight: `${desktopPanelMaxHeight}px` }}
                    >
                        <div className="border-b border-cyan-900/30 px-4 py-3">
                            <div className="flex items-start justify-between gap-3">
                                <div className="min-w-0">
                                    <div className="flex items-center gap-2 text-cyan-300">
                                        <Languages size={14} />
                                        <span className="text-[11px] font-mono uppercase tracking-[0.28em]">Learning</span>
                                    </div>
                                    <p className="mt-2 text-xs leading-5 text-gray-400">
                                        Tra từ, lưu câu và ôn lại ngay trong lúc đọc. Panel này luôn nằm trong vùng an toàn,
                                        không đè lên nội dung truyện.
                                    </p>
                                </div>
                                <button
                                    type="button"
                                    aria-label="Thu gọn Learning"
                                    onClick={() => setDesktopCollapsed(true)}
                                    className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-cyan-900/30 text-gray-400 hover:border-cyan-500/40 hover:text-cyan-200"
                                >
                                    <ChevronLeft size={16} />
                                </button>
                            </div>
                        </div>

                        <div className="overflow-y-auto">
                            <div className="border-b border-cyan-900/20 px-4 py-3">
                                <StudyStats loading={loading} error={error} stats={stats} />
                            </div>
                            <LookupTips />
                            <LookupActionButtons showSourceReference={locale !== "vi"} />
                            <StudyLinks />
                        </div>
                    </div>
                </div>
            )}

            {isDesktop && desktopCollapsed && (
                <button
                    ref={desktopButtonRef}
                    type="button"
                    onClick={() => {
                        if (desktopButtonMovedRef.current) {
                            desktopButtonMovedRef.current = false;
                            return;
                        }
                        setDesktopCollapsed(false);
                    }}
                    onPointerDown={(event) => {
                        if (!desktopButtonRef.current) return;
                        const rect = desktopButtonRef.current.getBoundingClientRect();
                        desktopButtonMovedRef.current = false;
                        setDesktopButtonDragState({
                            offsetX: event.clientX - rect.left,
                            offsetY: event.clientY - rect.top,
                            startX: event.clientX,
                            startY: event.clientY,
                        });
                    }}
                    className="fixed z-[58] inline-flex touch-none items-center gap-2 rounded-full border border-cyan-500/30 bg-[#071018]/95 px-4 py-3 text-sm text-cyan-200 shadow-[0_10px_30px_rgba(0,0,0,0.38)] backdrop-blur"
                    style={{
                        left: `${desktopButtonPosition.x}px`,
                        top: `${desktopButtonPosition.y}px`,
                    }}
                >
                    <GraduationCap size={16} />
                    <span className="font-medium">Learning</span>
                </button>
            )}

            {!isDesktop && !mobileReaderPanelActive && (
                <div
                    className={`fixed z-[58] ${audioActive ? "right-4" : "left-4"}`}
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

            {!isDesktop && mobileOpen && (
                <div className="fixed inset-0 z-[70]">
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
