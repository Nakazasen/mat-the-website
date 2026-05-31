"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bookmark, ChevronLeft, ChevronRight, Facebook, Home, List, Share2 } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";
import { useTheme } from "@/context/ThemeContext";
import { annotateCharacterNames } from "@/lib/character-highlights";
import { renderRichKaraoke } from "@/lib/karaoke";
import { sanitizeHtmlClient } from "@/lib/sanitize-html";
import { useChapterMeta } from "@/hooks/useChapterMeta";

import AudioPlayer from "./AudioPlayer";
import ChapterBgmPlayer from "./ChapterBgmPlayer";
import CommentSection from "./CommentSection";
import DonateSection from "./DonateSection";
import LikeButton from "./LikeButton";
import OraclePanel from "./OraclePanel";
import ReaderQuickLookup from "./ReaderQuickLookup";
import ReaderSentenceMode from "./ReaderSentenceMode";
import ReaderSettingsPanel from "./ReaderSettingsPanel";
import ReaderStudyDock from "./ReaderStudyDock";
import SystemHUD from "./SystemHUD";

interface ReadingClientProps {
    chapterId: number;
    chapterNumber: number;
    chapterTitle: string;
    content: string;
    prevId: number | null;
    nextId: number | null;
    totalChapters: number;
    resolvedLocale?: string;
    isFallback?: boolean;
    bgmUrl?: string | null;
    bgmTitle?: string | null;
}

interface WikiCharacterEntry {
    title?: string;
    tags?: string[];
}

const DESKTOP_STUDY_DOCK_LAYOUT_EVENT = "reader-study-dock-layout";

function shouldIgnoreNavigationHotkeys(target: EventTarget | null): boolean {
    if (!(target instanceof HTMLElement)) return false;
    return Boolean(target.closest('input, textarea, select, button, a, [contenteditable="true"]'));
}

export default function ReadingClient({
    chapterId,
    chapterNumber,
    chapterTitle,
    content,
    prevId,
    nextId,
    totalChapters,
    resolvedLocale,
    isFallback = false,
    bgmUrl,
    bgmTitle,
}: ReadingClientProps) {
    const backendUrl = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
    const { theme, fontSize, fontFamily } = useTheme();
    const { locale, dictionary, localizePath } = useLocale();
    const router = useRouter();

    const [readingProgress, setReadingProgress] = useState(0);
    const [activeChunkIndex, setActiveChunkIndex] = useState<number | null>(null);
    const [activeVoice, setActiveVoice] = useState('google');
    const [characterNames, setCharacterNames] = useState<string[]>([]);
    const [isMounted, setIsMounted] = useState(false);
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [isBookmarkLoading, setIsBookmarkLoading] = useState(false);
    const [desktopStudyDockOffset, setDesktopStudyDockOffset] = useState(0);

    const contentRef = useRef<HTMLDivElement>(null);
    const activeChunkRef = useRef<HTMLElement | null>(null);
    const chapterMeta = useChapterMeta(content, chapterNumber);

    useEffect(() => {
        setIsMounted(true);
        if (typeof window !== 'undefined') {
            const savedVoice = window.localStorage.getItem('reader-audio-voice-v1') || 'google';
            setActiveVoice(savedVoice);
        }
    }, []);

    useEffect(() => {
        const handleStudyDockLayout = (event: Event) => {
            const detail = (event as CustomEvent<{ open?: boolean; offset?: number }>).detail;
            setDesktopStudyDockOffset(detail?.open ? Math.max(0, detail?.offset || 0) : 0);
        };

        window.addEventListener(DESKTOP_STUDY_DOCK_LAYOUT_EVENT, handleStudyDockLayout as EventListener);
        return () => window.removeEventListener(DESKTOP_STUDY_DOCK_LAYOUT_EVENT, handleStudyDockLayout as EventListener);
    }, []);

    const sanitizedContent = useMemo(() => sanitizeHtmlClient(content), [content]);
    const highlightedContent = useMemo(
        () => annotateCharacterNames(sanitizedContent, characterNames),
        [characterNames, sanitizedContent],
    );

    const karaokeNodes = useMemo(() => {
        if (!isMounted) return null;
        // If activeVoice is an Edge voice, completely disable visual karaoke highlighting
        const highlightIndex = activeVoice === 'google' ? activeChunkIndex : null;
        return renderRichKaraoke(
            highlightedContent,
            highlightIndex,
            theme,
            chapterNumber,
            (idx: number, el: HTMLElement | null) => {
                if (highlightIndex === idx && el) {
                    activeChunkRef.current = el;
                }
            },
        ).nodes;
    }, [activeChunkIndex, activeVoice, chapterNumber, highlightedContent, isMounted, theme]);

    useEffect(() => {
        fetch("/api/user/bookmarks")
            .then((res) => (res.ok ? res.json() : []))
            .then((data) => {
                if (Array.isArray(data)) {
                    setIsBookmarked(data.some((item: { chapter_id?: number }) => item.chapter_id === chapterId));
                }
            })
            .catch(() => {});
    }, [chapterId]);

    const toggleBookmark = async () => {
        if (isBookmarkLoading) return;
        setIsBookmarkLoading(true);
        try {
            if (isBookmarked) {
                await fetch(`/api/user/bookmarks?chapter_id=${chapterId}`, { method: "DELETE" });
                setIsBookmarked(false);
            } else {
                const response = await fetch("/api/user/bookmarks", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ chapter_id: chapterId }),
                });
                if (response.ok) setIsBookmarked(true);
            }
        } finally {
            setIsBookmarkLoading(false);
        }
    };

    useEffect(() => {
        let isActive = true;

        const extractAliases = (entries: WikiCharacterEntry[]): string[] => entries
            .flatMap((entry) => [
                entry?.title?.trim(),
                ...(Array.isArray(entry?.tags) ? entry.tags : []),
            ])
            .map((value) => value?.trim())
            .filter((value): value is string => Boolean(value && value.length >= 2));

        const fetchCharacterNames = async () => {
            try {
                const params = new URLSearchParams({
                    category: "Nhân vật",
                    limit: "200",
                    locale,
                });
                const response = await fetch(`${backendUrl}/api/wiki?${params.toString()}`, { cache: "force-cache" });
                if (!response.ok) return;

                const payload = await response.json();
                const entries = Array.isArray(payload?.entries) ? payload.entries : [];
                const names = entries
                    .map((entry: { title?: string }) => entry?.title?.trim())
                    .filter((value: string | undefined): value is string => Boolean(value && value.length >= 2));

                if (isActive) {
                    setCharacterNames((previous) => (previous.length > names.length ? previous : names));
                }
            } catch {
                if (isActive) {
                    setCharacterNames((previous) => previous);
                }
            }
        };

        fetchCharacterNames();
        return () => {
            isActive = false;
        };
    }, [backendUrl, locale]);

    useEffect(() => {
        let isActive = true;

        const extractAliases = (entries: WikiCharacterEntry[]): string[] => entries
            .flatMap((entry) => [
                entry?.title?.trim(),
                ...(Array.isArray(entry?.tags) ? entry.tags : []),
            ])
            .map((value) => value?.trim())
            .filter((value): value is string => Boolean(value && value.length >= 2));

        const fetchCharacterAliases = async () => {
            try {
                const baseParams = new URLSearchParams({
                    category: "Nhân vật",
                    limit: "200",
                });
                const localeParams = new URLSearchParams(baseParams);
                localeParams.set("locale", locale);

                const requests = [
                    fetch(`${backendUrl}/api/wiki?${localeParams.toString()}`, { cache: "force-cache" }),
                ];

                if (locale !== "vi") {
                    const viParams = new URLSearchParams(baseParams);
                    viParams.set("locale", "vi");
                    requests.push(fetch(`${backendUrl}/api/wiki?${viParams.toString()}`, { cache: "force-cache" }));
                }

                const responses = await Promise.all(requests);
                const payloads = await Promise.all(
                    responses.map(async (response) => (response.ok ? response.json() : null)),
                );
                const aliases = Array.from(
                    new Set(
                        payloads.flatMap((payload) => {
                            const entries = Array.isArray(payload?.entries) ? payload.entries as WikiCharacterEntry[] : [];
                            return extractAliases(entries);
                        }),
                    ),
                );

                if (isActive && aliases.length > 0) {
                    setCharacterNames(aliases);
                }
            } catch {
                // Keep the basic scan list if the richer alias load fails.
            }
        };

        fetchCharacterAliases();
        return () => {
            isActive = false;
        };
    }, [backendUrl, locale]);

    useEffect(() => {
        if (activeChunkIndex !== null && activeChunkRef.current) {
            activeChunkRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    }, [activeChunkIndex]);

    useEffect(() => {
        const handleScroll = () => {
            const element = document.documentElement;
            const scrollTop = element.scrollTop || document.body.scrollTop;
            const scrollHeight = element.scrollHeight - element.clientHeight;
            const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
            setReadingProgress(Math.min(100, progress));
        };
        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    useEffect(() => {
        const timer = setTimeout(async () => {
            const { reportView } = await import("@/lib/api");
            reportView(chapterNumber);
        }, 15000);
        return () => clearTimeout(timer);
    }, [chapterNumber]);

    useEffect(() => {
        const handleKey = (event: KeyboardEvent) => {
            if (shouldIgnoreNavigationHotkeys(event.target) || event.altKey || event.ctrlKey || event.metaKey) {
                return;
            }
            if (event.key === "ArrowLeft" && prevId) {
                router.push(localizePath(`/chapters/${prevId}`));
            } else if (event.key === "ArrowRight" && nextId) {
                router.push(localizePath(`/chapters/${nextId}`));
            }
        };
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [localizePath, nextId, prevId]);

    useEffect(() => {
        const targetChapter = nextId ? nextId.toString() : chapterNumber.toString();
        localStorage.setItem("lastReadChapter", targetChapter);
        localStorage.setItem("lastReadTitle", chapterTitle);
        localStorage.setItem("lastReadAt", new Date().toISOString());

        // Dispatch custom event to notify other components (e.g. Header)
        window.dispatchEvent(new Event("chapter-read-updated"));

        const timer = setTimeout(() => {
            try {
                const historyRaw = localStorage.getItem("readingHistory");
                let history = historyRaw ? JSON.parse(historyRaw) : [];
                if (!Array.isArray(history)) history = [];

                const safeHistory = history.map(String);
                const currentId = String(chapterId);
                if (!safeHistory.includes(currentId)) {
                    safeHistory.push(currentId);
                    localStorage.setItem("readingHistory", JSON.stringify(safeHistory));
                }

                fetch("/api/user/read-progress", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        chapterId,
                        locale,
                        newExpAmount: 10,
                    }),
                }).catch(() => {});
            } catch {
                // ignore
            }
        }, 5000);

        return () => clearTimeout(timer);
    }, [chapterId, chapterNumber, chapterTitle, locale]);

    return (
        <div suppressHydrationWarning className={`min-h-screen bg-reader-bg text-reader-text transition-colors duration-300 ${fontFamily === "serif" ? "font-serif" : "font-sans"}`}>
            {isMounted && (
                <SystemHUD
                    chapterNumber={chapterNumber}
                    totalChapters={totalChapters}
                    readingProgress={readingProgress}
                    dangerLevel={chapterMeta.dangerLevel}
                    dangerLabel={chapterMeta.dangerLabel}
                    dangerColor={chapterMeta.dangerColor}
                    characterStatus={chapterMeta.characterStatus}
                    keywords={chapterMeta.keywords}
                />
            )}
            {isMounted && <OraclePanel chapterProgress={chapterNumber} />}
            {isMounted && <ReaderStudyDock />}

            <div className="reading-progress" style={{ width: `${readingProgress}%` }} />

            <div className="sticky top-0 z-40 border-b border-ash-800/60 backdrop-blur-md bg-ash-950/90">
                <div className="max-w-4xl mx-auto px-4 h-12 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-1">
                        <Link href={localizePath("/")} className="p-2 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors" title={dictionary.common.home}>
                            <Home size={15} />
                        </Link>
                        <Link href={localizePath("/chapters")} className="p-2 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors" title={dictionary.reader.toc}>
                            <List size={15} />
                        </Link>
                    </div>

                    <div className="text-center flex-1 overflow-hidden">
                        <div className="font-mono text-xs text-toxic-green-DEFAULT truncate">
                            {dictionary.reader.chapter} {chapterNumber}
                        </div>
                        <div className="text-ash-400 text-[10px] truncate hidden sm:block">{chapterTitle}</div>
                    </div>

                    <div className="flex items-center gap-1">
                        <button
                            onClick={toggleBookmark}
                            disabled={isBookmarkLoading}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all border ${
                                isBookmarked
                                    ? "bg-toxic-green-DEFAULT/10 border-toxic-green-DEFAULT/40 text-toxic-green-DEFAULT shadow-[0_0_15px_rgba(57,255,20,0.2)]"
                                    : "bg-ash-900/40 border-ash-800/60 text-ash-500 hover:border-toxic-green-DEFAULT/40 hover:text-toxic-green-DEFAULT"
                            }`}
                            title={isBookmarked ? dictionary.reader.saved : dictionary.reader.save}
                        >
                            <Bookmark size={14} fill={isBookmarked ? "currentColor" : "none"} className={isBookmarkLoading ? "animate-pulse" : ""} />
                            <span className="text-[10px] font-mono tracking-widest hidden xs:inline">
                                {isBookmarked ? dictionary.reader.saved : dictionary.reader.save}
                            </span>
                        </button>
                    </div>
                </div>

                <ReaderSettingsPanel showReadingProgress={true} readingProgress={readingProgress} className="fixed bottom-10 right-10 z-[60]" />
            </div>

            <div
                className="mx-auto max-w-[1280px] transition-[padding] duration-300"
                style={{ paddingLeft: desktopStudyDockOffset > 0 ? `${desktopStudyDockOffset}px` : undefined }}
            >
                <div className="max-w-[800px] mx-auto px-6 sm:px-10 py-10">
                <div className="mb-10 text-center">
                    <div className="font-mono text-xs text-toxic-green-DEFAULT tracking-[0.3em] mb-3">
                        {dictionary.reader.chapter.toUpperCase()} {chapterNumber} / {totalChapters}
                    </div>
                    <h1 className="font-biohazard text-3xl sm:text-4xl text-reader-text tracking-wide leading-tight">
                        {chapterTitle}
                    </h1>

                    {isFallback && resolvedLocale === "vi" && (
                        <div className="mt-3 inline-flex items-center rounded-full border border-toxic-green-DEFAULT/30 bg-toxic-green-DEFAULT/10 px-3 py-1 text-[11px] font-mono text-toxic-green-DEFAULT">
                            {dictionary.reader.quickFallback}
                        </div>
                    )}

                    <AudioPlayer
                        content={content}
                        chapterTitle={chapterTitle}
                        chapterNumber={chapterNumber}
                        prevId={prevId}
                        nextId={nextId}
                        onIndexChange={setActiveChunkIndex}
                        onVoiceChange={setActiveVoice}
                        locale={(resolvedLocale as any) || locale}
                        resolvedContent={content}
                    />

                    <ChapterBgmPlayer
                        chapterNumber={chapterNumber}
                        locale={(resolvedLocale as any) || locale}
                        bgmUrl={bgmUrl}
                        bgmTitle={bgmTitle}
                    />

                    <div className="flex items-center justify-center gap-4 mt-8">
                        {prevId ? (
                            <Link href={localizePath(`/chapters/${prevId}`)} className="flex items-center gap-1 px-4 py-2 border border-reader-border rounded-full text-reader-muted hover:border-reader-accent hover:text-reader-accent transition-all font-mono text-xs group">
                                <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
                                {dictionary.reader.previous}
                            </Link>
                        ) : (
                            <span className={`px-4 py-2 border border-reader-border rounded-full text-reader-muted font-mono text-xs cursor-not-allowed ${theme === "dark" ? "opacity-30" : "opacity-60 font-bold"}`}>{dictionary.reader.start}</span>
                        )}

                        <Link href={localizePath("/chapters")} className="w-10 h-10 flex items-center justify-center border border-reader-border rounded-full text-reader-muted hover:border-reader-accent hover:text-reader-accent transition-all" title={dictionary.reader.toc}>
                            <List size={16} />
                        </Link>

                        {nextId ? (
                            <Link href={localizePath(`/chapters/${nextId}`)} className="flex items-center gap-1 px-4 py-2 border border-reader-border rounded-full text-reader-muted hover:border-blood-red-bright hover:text-blood-red-bright transition-all font-mono text-xs group">
                                {dictionary.reader.next}
                                <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                            </Link>
                        ) : (
                            <span className={`px-4 py-2 border border-reader-border rounded-full text-reader-muted font-mono text-xs cursor-not-allowed ${theme === "dark" ? "opacity-30" : "opacity-60 font-bold"}`}>{dictionary.reader.end}</span>
                        )}
                    </div>

                    <div className="hazard-divider mt-8" />
                </div>

                <div ref={contentRef} className="reading-container !bg-transparent !text-inherit prose max-w-none" style={{ fontSize: `${fontSize}px`, lineHeight: 1.8 }}>
                    {!isMounted ? <div dangerouslySetInnerHTML={{ __html: highlightedContent }} /> : karaokeNodes}
                </div>

                {isMounted && (
                    <ReaderQuickLookup
                        chapterId={chapterId}
                        chapterProgress={chapterNumber}
                        containerRef={contentRef}
                        sourceLocale={(resolvedLocale as any) || locale}
                    />
                )}

                {isMounted && (
                    <ReaderSentenceMode
                        chapterId={chapterId}
                        chapterProgress={chapterNumber}
                        containerRef={contentRef}
                        sourceLocale={(resolvedLocale as any) || locale}
                    />
                )}

                <div className="mt-12 mb-8 flex flex-col items-center">
                    <div className="text-[10px] font-mono text-reader-muted mb-4 tracking-[0.4em]">{dictionary.reader.shareStory.toUpperCase()}</div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => {
                                const url = window.location.href;
                                window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, "_blank");
                            }}
                            className="flex items-center gap-2 px-6 py-2 bg-[#1877F2] text-white rounded text-xs font-mono hover:brightness-110 transition-all uppercase tracking-wider"
                        >
                            <Facebook size={14} fill="currentColor" />
                            Facebook
                        </button>
                        <button
                            onClick={() => {
                                const url = window.location.href;
                                window.open(`https://chat.zalo.me/?url=${encodeURIComponent(url)}`, "_blank");
                            }}
                            className="flex items-center gap-2 px-6 py-2 bg-[#0068FF] text-white rounded text-xs font-mono hover:brightness-110 transition-all uppercase tracking-wider"
                        >
                            <Share2 size={14} />
                            Zalo
                        </button>
                    </div>
                </div>

                <div className="hazard-divider my-12" />

                <div className="flex gap-3">
                    {prevId ? (
                        <Link href={localizePath(`/chapters/${prevId}`)} className="flex-1 flex items-center justify-center gap-2 py-4 border border-reader-border rounded text-reader-muted hover:border-reader-accent/50 hover:text-reader-accent transition-all font-biohazard tracking-wider text-sm sm:text-base group">
                            <ChevronLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
                            <span>{dictionary.reader.previousChapter}</span>
                        </Link>
                    ) : (
                        <div className={`flex-1 flex items-center justify-center py-4 border border-reader-border rounded text-reader-muted font-biohazard tracking-wider text-sm cursor-not-allowed ${theme === "dark" ? "opacity-30" : "opacity-60"}`}>
                            {dictionary.reader.start}
                        </div>
                    )}

                    {nextId ? (
                        <Link href={localizePath(`/chapters/${nextId}`)} className="flex-1 flex items-center justify-center gap-2 py-4 bg-blood-red border border-blood-red-bright/30 rounded text-white hover:bg-blood-red-bright hover:shadow-[0_0_20px_rgba(139,0,0,0.5)] transition-all font-biohazard tracking-wider text-sm sm:text-base group">
                            <span>{dictionary.reader.nextChapter}</span>
                            <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
                        </Link>
                    ) : (
                        <div className={`flex-1 flex items-center justify-center py-4 border border-reader-border rounded text-reader-muted font-biohazard tracking-wider text-sm cursor-not-allowed ${theme === "dark" ? "opacity-30" : "opacity-60"}`}>
                            {dictionary.reader.end}
                        </div>
                    )}
                </div>

                <div className="flex justify-center py-8 border-t border-reader-border mt-8">
                    <div className="flex flex-col items-center gap-3">
                        <p className="text-xs font-mono text-reader-muted">{dictionary.reader.leaveALike}</p>
                        <LikeButton chapterId={chapterId} chapterNumber={chapterNumber} />
                    </div>
                </div>

                <DonateSection chapterNumber={chapterNumber} />
                <CommentSection chapterNumber={chapterNumber} />

                <div className="flex items-center justify-center gap-4 mt-12 pb-10">
                    <Link href={localizePath("/")} className="text-reader-muted hover:text-reader-accent text-xs font-mono transition-colors flex items-center gap-1">
                        <Home size={12} /> {dictionary.common.home}
                    </Link>
                    <span className="text-reader-border">·</span>
                    <Link href={localizePath("/chapters")} className="text-reader-muted hover:text-reader-accent text-xs font-mono transition-colors flex items-center gap-1">
                        <List size={12} /> {dictionary.reader.toc}
                    </Link>
                    {nextId && (
                        <>
                            <span className="text-reader-border">·</span>
                            <Link href={localizePath(`/chapters/${nextId}`)} className="text-reader-muted hover:text-blood-red-bright text-xs font-mono transition-colors flex items-center gap-1">
                                {dictionary.reader.next} <ChevronRight size={12} />
                            </Link>
                        </>
                    )}
                </div>
            </div>

            </div>

            <div className="fixed bottom-0 left-0 right-0 z-50 md:hidden pb-safe">
                <div className="absolute inset-0 bg-ash-950/80 backdrop-blur-lg border-t border-ash-800/50 shadow-[0_-10px_30px_rgba(0,0,0,0.5)]" />

                <div className="relative grid grid-cols-5 items-center h-16">
                    <Link href={localizePath("/")} className="flex flex-col items-center justify-center gap-1 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors">
                        <Home size={18} />
                        <span className="text-[10px] font-mono">{dictionary.common.home}</span>
                    </Link>

                    <button
                        onClick={toggleBookmark}
                        disabled={isBookmarkLoading}
                        className={`flex flex-col items-center justify-center gap-1 transition-colors border-l border-ash-800/40 ${isBookmarked ? "text-toxic-green-DEFAULT" : "text-ash-500"}`}
                    >
                        <Bookmark size={18} fill={isBookmarked ? "currentColor" : "none"} className={isBookmarkLoading ? "animate-pulse" : ""} />
                        <span className="text-[10px] font-mono">{isBookmarked ? dictionary.reader.saved : dictionary.reader.save}</span>
                    </button>

                    {prevId ? (
                        <Link href={localizePath(`/chapters/${prevId}`)} className="col-span-1 flex flex-col items-center justify-center gap-1 text-ash-300 hover:text-toxic-green-DEFAULT transition-colors border-l border-ash-800/40">
                            <ChevronLeft size={20} />
                            <span className="text-[10px] font-mono">{dictionary.reader.previous}</span>
                        </Link>
                    ) : (
                        <div className="flex flex-col items-center justify-center gap-1 text-ash-800 border-l border-ash-800/40">
                            <ChevronLeft size={20} />
                            <span className="text-[10px] font-mono">{dictionary.reader.start}</span>
                        </div>
                    )}

                    {nextId ? (
                        <Link href={localizePath(`/chapters/${nextId}`)} className="col-span-1 flex flex-col items-center justify-center gap-1 text-white bg-blood-red-DEFAULT h-full transition-colors border-l border-ash-800/40">
                            <ChevronRight size={20} />
                            <span className="text-[10px] font-mono">{dictionary.reader.next}</span>
                        </Link>
                    ) : (
                        <div className="flex flex-col items-center justify-center gap-1 text-ash-700 border-l border-ash-800/40">
                            <ChevronRight size={20} />
                            <span className="text-[10px] font-mono">{dictionary.reader.end}</span>
                        </div>
                    )}

                    <ReaderSettingsPanel showReadingProgress={false} className="flex flex-col items-center justify-center gap-1 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors border-l border-ash-800/40" />
                </div>
            </div>

            <div className="h-20 md:h-0" />
        </div>
    );
}
