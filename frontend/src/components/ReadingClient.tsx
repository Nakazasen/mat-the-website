"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Home, List, Share2, Facebook, Bookmark } from "lucide-react";
import { useTheme } from "@/context/ThemeContext";
import ReaderSettingsPanel from "./ReaderSettingsPanel";
import AudioPlayer from "./AudioPlayer";
import CommentSection from "./CommentSection";
import LikeButton from "./LikeButton";
import DonateSection from "./DonateSection";
import { splitIntoChunks } from "@/lib/tts-utils";
import { renderRichKaraoke } from "@/lib/karaoke";

interface ReadingClientProps {
    chapterId: number;
    chapterNumber: number;
    chapterTitle: string;
    content: string;
    prevId: number | null;
    nextId: number | null;
    totalChapters: number;
}

export default function ReadingClient({
    chapterId,
    chapterNumber,
    chapterTitle,
    content,
    prevId,
    nextId,
    totalChapters,
}: ReadingClientProps) {
    const { theme, fontSize, fontFamily } = useTheme();
    const [readingProgress, setReadingProgress] = useState(0);
    const [activeChunkIndex, setActiveChunkIndex] = useState<number | null>(null);
    const contentRef = useRef<HTMLDivElement>(null);
    const activeChunkRef = useRef<HTMLSpanElement>(null);

    const [isMounted, setIsMounted] = useState(false);
    useEffect(() => {
        setIsMounted(true);
    }, []);

    const karaokeNodes = useMemo(() => {
        if (!isMounted) return null;
        return renderRichKaraoke(content, activeChunkIndex, theme, (idx: number, el: HTMLElement | null) => {
            if (activeChunkIndex === idx && el) {
                activeChunkRef.current = el;
            }
        }).nodes;
    }, [content, activeChunkIndex, theme, isMounted]);

    // Bookmarks state
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [isBookmarkLoading, setIsBookmarkLoading] = useState(false);

    // Load bookmark status on mount
    useEffect(() => {
        fetch('/api/user/bookmarks').then(res => {
            if (res.ok) return res.json();
            return [];
        }).then(data => {
            if (Array.isArray(data)) {
                setIsBookmarked(data.some((b: any) => b.chapter_id === chapterId));
            }
        }).catch(() => { });
    }, [chapterId]);

    const toggleBookmark = async () => {
        if (isBookmarkLoading) return;
        setIsBookmarkLoading(true);
        try {
            if (isBookmarked) {
                await fetch(`/api/user/bookmarks?chapter_id=${chapterId}`, { method: 'DELETE' });
                setIsBookmarked(false);
            } else {
                const res = await fetch('/api/user/bookmarks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ chapter_id: chapterId })
                });
                if (res.ok) setIsBookmarked(true);
            }
        } catch { }
        setIsBookmarkLoading(false);
    };

    // Split content into chunks for Karaoke
    const chunks = splitIntoChunks(content);

    // Auto-scroll to active chunk
    useEffect(() => {
        if (activeChunkIndex !== null && activeChunkRef.current) {
            activeChunkRef.current.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }, [activeChunkIndex]);

    // Reading progress bar
    useEffect(() => {
        const handleScroll = () => {
            const el = document.documentElement;
            const scrollTop = el.scrollTop || document.body.scrollTop;
            const scrollHeight = el.scrollHeight - el.clientHeight;
            const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
            setReadingProgress(Math.min(100, progress));
        };
        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    // Analytics: Report view after a delay (with localStorage anti-spam)
    useEffect(() => {
        const timer = setTimeout(async () => {
            const { reportView } = await import("@/lib/api");
            reportView(chapterNumber);
        }, 15000); // Report after 15 seconds of reading
        return () => clearTimeout(timer);
    }, [chapterNumber]);

    // Keyboard navigation
    useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            if (e.key === "ArrowLeft" && prevId) {
                window.location.href = `/chapters/${prevId}`;
            } else if (e.key === "ArrowRight" && nextId) {
                window.location.href = `/chapters/${nextId}`;
            }
        };
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [prevId, nextId]);

    // History: Mark last read chapter & Sync reading progress
    useEffect(() => {
        // Last read pointer
        localStorage.setItem('lastReadChapter', chapterNumber.toString());
        localStorage.setItem('lastReadTitle', chapterTitle);
        localStorage.setItem('lastReadAt', new Date().toISOString());

        // Wait 5 seconds before syncing to ensure they are actually on the page
        const timer = setTimeout(() => {
            try {
                // Array of read chapter IDs for stats/EXP calculation
                const historyRaw = localStorage.getItem("readingHistory");
                let history = historyRaw ? JSON.parse(historyRaw) : [];
                if (!Array.isArray(history)) history = [];

                // Convert all to string for safe comparison
                const safeHistory = history.map(String);
                const currentIdStr = String(chapterId);

                let isNewRead = false;
                if (!safeHistory.includes(currentIdStr)) {
                    safeHistory.push(currentIdStr);
                    localStorage.setItem("readingHistory", JSON.stringify(safeHistory));
                    isNewRead = true;
                }

                // Sync to backend
                fetch('/api/user/read-progress', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chaptersReadCount: safeHistory.length,
                        newExpAmount: isNewRead ? 10 : 0
                    })
                }).catch(err => console.error("Failed to sync reading progress", err));
            } catch (error) {
                console.error("Error updating reading history", error);
            }
        }, 5000);

        return () => clearTimeout(timer);
    }, [chapterId, chapterNumber, chapterTitle]);

    return (
        <div suppressHydrationWarning className={`min-h-screen bg-reader-bg text-reader-text transition-colors duration-300 ${fontFamily === 'serif' ? 'font-serif' : 'font-sans'}`}>
            {/* Progress bar */}
            <div
                className="reading-progress"
                style={{ width: `${readingProgress}%` }}
            />

            {/* === TOP NAV BAR === */}
            <div className="sticky top-0 z-40 border-b border-ash-800/60 backdrop-blur-md bg-ash-950/90">
                <div className="max-w-4xl mx-auto px-4 h-12 flex items-center justify-between gap-4">
                    {/* Left: Home + Chapters */}
                    <div className="flex items-center gap-1">
                        <Link
                            href="/"
                            className="p-2 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors"
                            title="Trang chủ"
                        >
                            <Home size={15} />
                        </Link>
                        <Link
                            href="/chapters"
                            className="p-2 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors"
                            title="Mục lục"
                        >
                            <List size={15} />
                        </Link>
                    </div>

                    {/* Center: Chapter info */}
                    <div className="text-center flex-1 overflow-hidden">
                        <div className="font-mono text-xs text-toxic-green-DEFAULT truncate">
                            Chương {chapterNumber}
                        </div>
                        <div className="text-ash-400 text-[10px] truncate hidden sm:block">
                            {chapterTitle}
                        </div>
                    </div>

                    {/* Right: Actions & Settings */}
                    <div className="flex items-center gap-1">
                        <button
                            onClick={toggleBookmark}
                            disabled={isBookmarkLoading}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all border ${isBookmarked
                                ? 'bg-toxic-green-DEFAULT/10 border-toxic-green-DEFAULT/40 text-toxic-green-DEFAULT shadow-[0_0_15px_rgba(57,255,20,0.2)]'
                                : 'bg-ash-900/40 border-ash-800/60 text-ash-500 hover:border-toxic-green-DEFAULT/40 hover:text-toxic-green-DEFAULT'
                                }`}
                            title={isBookmarked ? "Bỏ lưu khỏi Tủ sách" : "Lưu vào Tủ sách"}
                        >
                            <Bookmark size={14} fill={isBookmarked ? "currentColor" : "none"} className={isBookmarkLoading ? "animate-pulse" : ""} />
                            <span className="text-[10px] font-mono tracking-widest hidden xs:inline">
                                {isBookmarked ? "ĐÃ LƯU" : "LƯU TRANG"}
                            </span>
                        </button>
                    </div>
                </div>

                <ReaderSettingsPanel
                    showReadingProgress={true}
                    readingProgress={readingProgress}
                    className="fixed bottom-10 right-10 z-[60]"
                />
            </div>

            {/* === MAIN CONTENT === */}
            <div className="max-w-[800px] mx-auto px-6 sm:px-10 py-10">
                {/* Chapter title */}
                <div className="mb-10 text-center">
                    <div className="font-mono text-xs text-toxic-green-DEFAULT tracking-[0.3em] mb-3">
                        CHƯƠNG {chapterNumber} / {totalChapters}
                    </div>
                    <h1 className="font-biohazard text-3xl sm:text-4xl text-reader-text tracking-wide leading-tight">
                        {chapterTitle}
                    </h1>

                    {/* Audio Player */}
                    <AudioPlayer
                        content={content}
                        chapterTitle={chapterTitle}
                        chapterNumber={chapterNumber}
                        prevId={prevId}
                        nextId={nextId}
                        onIndexChange={setActiveChunkIndex}
                    />

                    {/* Top Navigation Buttons */}
                    <div className="flex items-center justify-center gap-4 mt-8">
                        {prevId ? (
                            <Link
                                href={`/chapters/${prevId}`}
                                className="flex items-center gap-1 px-4 py-2 border border-reader-border rounded-full text-reader-muted hover:border-reader-accent hover:text-reader-accent transition-all font-mono text-xs group"
                            >
                                <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
                                TRƯỚC
                            </Link>
                        ) : (
                            <span className={`px-4 py-2 border border-reader-border rounded-full text-reader-muted font-mono text-xs cursor-not-allowed ${theme === 'dark' ? 'opacity-30' : 'opacity-60 font-bold'}`}>ĐẦU</span>
                        )}

                        <Link
                            href="/chapters"
                            className="w-10 h-10 flex items-center justify-center border border-reader-border rounded-full text-reader-muted hover:border-reader-accent hover:text-reader-accent transition-all"
                            title="Mục lục"
                        >
                            <List size={16} />
                        </Link>

                        {nextId ? (
                            <Link
                                href={`/chapters/${nextId}`}
                                className="flex items-center gap-1 px-4 py-2 border border-reader-border rounded-full text-reader-muted hover:border-blood-red-bright hover:text-blood-red-bright transition-all font-mono text-xs group"
                            >
                                TIẾP
                                <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                            </Link>
                        ) : (
                            <span className={`px-4 py-2 border border-reader-border rounded-full text-reader-muted font-mono text-xs cursor-not-allowed ${theme === 'dark' ? 'opacity-30' : 'opacity-60 font-bold'}`}>HẾT</span>
                        )}
                    </div>

                    <div className="hazard-divider mt-8" />
                </div>

                {/* Reading content */}
                <div
                    ref={contentRef}
                    className="reading-container !bg-transparent !text-inherit prose max-w-none"
                    style={{ fontSize: `${fontSize}px`, lineHeight: 1.8 }}
                >
                    {!isMounted ? (
                        <div dangerouslySetInnerHTML={{ __html: content }} />
                    ) : (
                        karaokeNodes
                    )}
                </div>

                {/* === SOCIAL SHARE === */}
                <div className="mt-12 mb-8 flex flex-col items-center">
                    <div className="text-[10px] font-mono text-reader-muted mb-4 tracking-[0.4em]">CHIA SẺ TRUYỆN</div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => {
                                const url = window.location.href;
                                window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
                            }}
                            className="flex items-center gap-2 px-6 py-2 bg-[#1877F2] text-white rounded text-xs font-mono hover:brightness-110 transition-all uppercase tracking-wider"
                        >
                            <Facebook size={14} fill="currentColor" />
                            Facebook
                        </button>
                        <button
                            onClick={() => {
                                const url = window.location.href;
                                window.open(`https://chat.zalo.me/?url=${encodeURIComponent(url)}`, '_blank');
                            }}
                            className="flex items-center gap-2 px-6 py-2 bg-[#0068FF] text-white rounded text-xs font-mono hover:brightness-110 transition-all uppercase tracking-wider"
                        >
                            <Share2 size={14} />
                            Zalo
                        </button>
                    </div>
                </div>

                {/* Bottom divider */}
                <div className="hazard-divider my-12" />

                {/* === CHAPTER NAVIGATION (BOTTOM) === */}
                <div className="flex gap-3">
                    {prevId ? (
                        <Link
                            href={`/chapters/${prevId}`}
                            className="flex-1 flex items-center justify-center gap-2 py-4 border border-reader-border rounded text-reader-muted hover:border-reader-accent/50 hover:text-reader-accent transition-all font-biohazard tracking-wider text-sm sm:text-base group"
                        >
                            <ChevronLeft
                                size={18}
                                className="group-hover:-translate-x-1 transition-transform"
                            />
                            <span>CHƯƠNG TRƯỚC</span>
                        </Link>
                    ) : (
                        <div className={`flex-1 flex items-center justify-center py-4 border border-reader-border rounded text-reader-muted font-biohazard tracking-wider text-sm cursor-not-allowed ${theme === 'dark' ? 'opacity-30' : 'opacity-60'}`}>
                            ĐÂY LÀ ĐẦU TRUYỆN
                        </div>
                    )}

                    {nextId ? (
                        <Link
                            href={`/chapters/${nextId}`}
                            className="flex-1 flex items-center justify-center gap-2 py-4 bg-blood-red border border-blood-red-bright/30 rounded text-white hover:bg-blood-red-bright hover:shadow-[0_0_20px_rgba(139,0,0,0.5)] transition-all font-biohazard tracking-wider text-sm sm:text-base group"
                        >
                            <span>CHƯƠNG TIẾP</span>
                            <ChevronRight
                                size={18}
                                className="group-hover:translate-x-1 transition-transform"
                            />
                        </Link>
                    ) : (
                        <div className={`flex-1 flex items-center justify-center py-4 border border-reader-border rounded text-reader-muted font-biohazard tracking-wider text-sm cursor-not-allowed ${theme === 'dark' ? 'opacity-30' : 'opacity-60'}`}>
                            HẾT TRUYỆN (TẠM THỜI)
                        </div>
                    )}
                </div>

                {/* === LIKE BUTTON === */}
                <div className="flex justify-center py-8 border-t border-reader-border mt-8">
                    <div className="flex flex-col items-center gap-3">
                        <p className="text-xs font-mono text-reader-muted">Chương hay? Để lại một trái tim nhé! ☣️</p>
                        <LikeButton chapterNumber={chapterNumber} />
                    </div>
                </div>

                {/* === DONATE === */}
                <DonateSection chapterNumber={chapterNumber} />

                {/* === COMMENTS === */}
                <CommentSection chapterNumber={chapterNumber} />

                {/* Quick nav */}
                <div className="flex items-center justify-center gap-4 mt-12 pb-10">
                    <Link
                        href="/"
                        className="text-reader-muted hover:text-reader-accent text-xs font-mono transition-colors flex items-center gap-1"
                    >
                        <Home size={12} /> TRANG CHỦ
                    </Link>
                    <span className="text-reader-border">·</span>
                    <Link
                        href="/chapters"
                        className="text-reader-muted hover:text-reader-accent text-xs font-mono transition-colors flex items-center gap-1"
                    >
                        <List size={12} /> MỤC LỤC
                    </Link>
                    {nextId && (
                        <>
                            <span className="text-reader-border">·</span>
                            <Link
                                href={`/chapters/${nextId}`}
                                className="text-reader-muted hover:text-blood-red-bright text-xs font-mono transition-colors flex items-center gap-1"
                            >
                                TIẾP <ChevronRight size={12} />
                            </Link>
                        </>
                    )}
                </div>
            </div>

            {/* === MOBILE STICKY BOTTOM NAV XỊN === */}
            <div className="fixed bottom-0 left-0 right-0 z-50 md:hidden pb-safe">
                {/* Visual Glassmorphism background */}
                <div className="absolute inset-0 bg-ash-950/80 backdrop-blur-lg border-t border-ash-800/50 shadow-[0_-10px_30px_rgba(0,0,0,0.5)]" />

                <div className="relative grid grid-cols-5 items-center h-16">
                    <Link
                        href="/"
                        className="flex flex-col items-center justify-center gap-1 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors"
                    >
                        <Home size={18} />
                        <span className="text-[10px] font-mono">CHỦ</span>
                    </Link>

                    <button
                        onClick={toggleBookmark}
                        disabled={isBookmarkLoading}
                        className={`flex flex-col items-center justify-center gap-1 transition-colors border-l border-ash-800/40 ${isBookmarked ? 'text-toxic-green-DEFAULT' : 'text-ash-500'
                            }`}
                    >
                        <Bookmark size={18} fill={isBookmarked ? "currentColor" : "none"} className={isBookmarkLoading ? "animate-pulse" : ""} />
                        <span className="text-[10px] font-mono">{isBookmarked ? "ĐÃ LƯU" : "LƯU"}</span>
                    </button>

                    {prevId ? (
                        <Link
                            href={`/chapters/${prevId}`}
                            className="col-span-1 flex flex-col items-center justify-center gap-1 text-ash-300 hover:text-toxic-green-DEFAULT transition-colors border-l border-ash-800/40"
                        >
                            <ChevronLeft size={20} />
                            <span className="text-[10px] font-mono">TRƯỚC</span>
                        </Link>
                    ) : (
                        <div className="flex flex-col items-center justify-center gap-1 text-ash-800 border-l border-ash-800/40">
                            <ChevronLeft size={20} />
                            <span className="text-[10px] font-mono">ĐẦU</span>
                        </div>
                    )}

                    {nextId ? (
                        <Link
                            href={`/chapters/${nextId}`}
                            className="col-span-1 flex flex-col items-center justify-center gap-1 text-white bg-blood-red-DEFAULT h-full transition-colors border-l border-ash-800/40"
                        >
                            <ChevronRight size={20} />
                            <span className="text-[10px] font-mono">TIẾP</span>
                        </Link>
                    ) : (
                        <div className="flex flex-col items-center justify-center gap-1 text-ash-700 border-l border-ash-800/40">
                            <ChevronRight size={20} />
                            <span className="text-[10px] font-mono">HẾT</span>
                        </div>
                    )}

                    <ReaderSettingsPanel
                        showReadingProgress={false}
                        className="flex flex-col items-center justify-center gap-1 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors border-l border-ash-800/40"
                    />
                </div>
            </div>

            {/* Bottom spacer for mobile nav */}
            <div className="h-20 md:h-0" />
        </div>
    );
}
