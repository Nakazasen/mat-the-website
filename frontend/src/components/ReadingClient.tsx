"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Settings, Home, List, Sun, Moon, Coffee, Share2, Facebook } from "lucide-react";
import { useTheme } from "@/context/ThemeContext";
import AudioPlayer from "./AudioPlayer";
import CommentSection from "./CommentSection";
import { splitIntoChunks } from "@/lib/tts-utils";

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
    const { theme, setTheme, fontSize, setFontSize, fontFamily, setFontFamily } = useTheme();
    const [showSettings, setShowSettings] = useState(false);
    const [readingProgress, setReadingProgress] = useState(0);
    const [activeChunkIndex, setActiveChunkIndex] = useState<number | null>(null);
    const contentRef = useRef<HTMLDivElement>(null);
    const activeChunkRef = useRef<HTMLSpanElement>(null);

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

    // Analytics: Report view after a delay
    useEffect(() => {
        const { reportView } = require("@/lib/api");
        const timer = setTimeout(() => {
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

    // History: Mark last read chapter
    useEffect(() => {
        localStorage.setItem('lastReadChapter', chapterNumber.toString());
        localStorage.setItem('lastReadTitle', chapterTitle);
        localStorage.setItem('lastReadAt', new Date().toISOString());
    }, [chapterNumber, chapterTitle]);

    return (
        <div className={`min-h-screen bg-reader-bg text-reader-text transition-colors duration-300 ${fontFamily === 'serif' ? 'font-serif' : 'font-sans'}`}>
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

                    {/* Right: Settings */}
                    <button
                        onClick={() => setShowSettings(!showSettings)}
                        className="p-2 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors"
                        title="Cài đặt đọc"
                    >
                        <Settings size={15} />
                    </button>
                </div>

                {/* Settings panel */}
                {showSettings && (
                    <div className="border-t border-ash-800/60 bg-ash-950/95 px-4 py-4">
                        <div className="max-w-4xl mx-auto flex flex-col gap-6">
                            <div className="flex flex-wrap gap-8 items-center justify-center sm:justify-start">
                                {/* Font family */}
                                <div className="flex items-center gap-3">
                                    <span className="text-ash-400 text-xs font-mono">FONT</span>
                                    <div className="flex bg-ash-900/50 p-1 rounded border border-ash-800">
                                        <button
                                            onClick={() => setFontFamily('sans')}
                                            className={`px-3 py-1.5 text-[10px] font-mono tracking-widest rounded transition-all ${fontFamily === 'sans' ? "bg-ash-700 text-toxic-green-DEFAULT" : "text-ash-500 hover:text-ash-300"}`}
                                        >
                                            SANS
                                        </button>
                                        <button
                                            onClick={() => setFontFamily('serif')}
                                            className={`px-3 py-1.5 text-[10px] font-mono tracking-widest rounded transition-all ${fontFamily === 'serif' ? "bg-ash-700 text-toxic-green-DEFAULT" : "text-ash-500 hover:text-ash-300"}`}
                                        >
                                            SERIF
                                        </button>
                                    </div>
                                </div>

                                {/* Font size */}
                                <div className="flex items-center gap-3">
                                    <span className="text-ash-400 text-xs font-mono">CỠ CHỮ</span>
                                    <button
                                        onClick={() => setFontSize(Math.max(14, fontSize - 2))}
                                        className="w-7 h-7 border border-ash-700 text-ash-300 hover:border-toxic-green-DEFAULT hover:text-toxic-green-DEFAULT transition-colors rounded text-sm"
                                    >
                                        A-
                                    </button>
                                    <span className="text-toxic-green-DEFAULT font-mono text-sm w-6 text-center">
                                        {fontSize}
                                    </span>
                                    <button
                                        onClick={() => setFontSize(Math.min(28, fontSize + 2))}
                                        className="w-7 h-7 border border-ash-700 text-ash-300 hover:border-toxic-green-DEFAULT hover:text-toxic-green-DEFAULT transition-colors rounded text-sm"
                                    >
                                        A+
                                    </button>
                                </div>

                                {/* Theme */}
                                <div className="flex items-center gap-3">
                                    <span className="text-ash-400 text-xs font-mono">NỀN</span>
                                    <div className="flex bg-ash-900/50 p-1 rounded border border-ash-800">
                                        {[
                                            { id: 'dark', icon: Moon, label: 'TỐI' },
                                            { id: 'light', icon: Sun, label: 'SÁNG' },
                                            { id: 'sepia', icon: Coffee, label: 'VÀNG' }
                                        ].map((t) => (
                                            <button
                                                key={t.id}
                                                onClick={() => setTheme(t.id as any)}
                                                className={`flex items-center gap-2 px-3 py-1.5 text-[10px] font-mono tracking-widest rounded transition-all ${theme === t.id
                                                    ? "bg-toxic-green-DEFAULT text-black"
                                                    : "text-ash-500 hover:text-ash-200"
                                                    }`}
                                            >
                                                <t.icon size={12} />
                                                <span className="hidden xs:inline">{t.label}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Progress info */}
                            <div className="text-ash-500 text-[10px] font-mono text-center sm:text-right">
                                {Math.round(readingProgress)}% đã đọc
                            </div>
                        </div>
                    </div>
                )}
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
                                className="flex items-center gap-1 px-4 py-2 border border-ash-800 rounded-full text-ash-400 hover:border-toxic-green-DEFAULT hover:text-toxic-green-DEFAULT transition-all font-mono text-xs group"
                            >
                                <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
                                TRƯỚC
                            </Link>
                        ) : (
                            <span className="px-4 py-2 border border-ash-900 rounded-full text-ash-800 font-mono text-xs cursor-not-allowed">ĐẦU</span>
                        )}

                        <Link
                            href="/chapters"
                            className="w-10 h-10 flex items-center justify-center border border-ash-800 rounded-full text-ash-400 hover:border-toxic-green-DEFAULT hover:text-toxic-green-DEFAULT transition-all"
                            title="Mục lục"
                        >
                            <List size={16} />
                        </Link>

                        {nextId ? (
                            <Link
                                href={`/chapters/${nextId}`}
                                className="flex items-center gap-1 px-4 py-2 border border-ash-800 rounded-full text-ash-400 hover:border-blood-red-bright hover:text-blood-red-bright transition-all font-mono text-xs group"
                            >
                                TIẾP
                                <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                            </Link>
                        ) : (
                            <span className="px-4 py-2 border border-ash-900 rounded-full text-ash-800 font-mono text-xs cursor-not-allowed">HẾT</span>
                        )}
                    </div>

                    <div className="hazard-divider mt-8" />
                </div>

                {/* Reading content */}
                <div
                    ref={contentRef}
                    className="reading-container !bg-transparent !text-inherit"
                    style={{ fontSize: `${fontSize}px`, whiteSpace: "pre-wrap", lineHeight: 1.8 }}
                >
                    {chunks.map((chunk, index) => (
                        <span
                            key={index}
                            ref={activeChunkIndex === index ? activeChunkRef : null}
                            className={`transition-all duration-300 rounded-sm ${activeChunkIndex === index
                                ? theme === 'dark'
                                    ? "bg-toxic-green-DEFAULT/40 text-white shadow-[0_0_25px_rgba(0,255,159,0.4)] ring-1 ring-toxic-green-DEFAULT/50 scale-[1.02] inline-block"
                                    : "bg-toxic-green-DEFAULT/50 text-black ring-1 ring-toxic-green-DEFAULT/60 scale-[1.02] inline-block"
                                : "opacity-100"
                                }`}
                        >
                            {chunk}
                        </span>
                    ))}
                </div>

                {/* === SOCIAL SHARE === */}
                <div className="mt-12 mb-8 flex flex-col items-center">
                    <div className="text-[10px] font-mono text-ash-600 mb-4 tracking-[0.4em]">CHIA SẺ TRUYỆN</div>
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
                            className="flex-1 flex items-center justify-center gap-2 py-4 border border-ash-700 rounded text-ash-300 hover:border-toxic-green-DEFAULT/50 hover:text-toxic-green-DEFAULT transition-all font-biohazard tracking-wider text-sm sm:text-base group"
                        >
                            <ChevronLeft
                                size={18}
                                className="group-hover:-translate-x-1 transition-transform"
                            />
                            <span>CHƯƠNG TRƯỚC</span>
                        </Link>
                    ) : (
                        <div className="flex-1 flex items-center justify-center py-4 border border-ash-800/50 rounded text-ash-700 font-biohazard tracking-wider text-sm cursor-not-allowed">
                            ĐÂY LÀ ĐẦU TRUYỆN
                        </div>
                    )}

                    {nextId ? (
                        <Link
                            href={`/chapters/${nextId}`}
                            className="flex-1 flex items-center justify-center gap-2 py-4 bg-blood-red-DEFAULT border border-blood-red-bright/30 rounded text-white hover:bg-blood-red-bright hover:shadow-[0_0_20px_rgba(139,0,0,0.5)] transition-all font-biohazard tracking-wider text-sm sm:text-base group"
                        >
                            <span>CHƯƠNG TIẾP</span>
                            <ChevronRight
                                size={18}
                                className="group-hover:translate-x-1 transition-transform"
                            />
                        </Link>
                    ) : (
                        <div className="flex-1 flex items-center justify-center py-4 border border-ash-800/50 rounded text-ash-700 font-biohazard tracking-wider text-sm cursor-not-allowed">
                            HẾT TRUYỆN (TẠM THỜI)
                        </div>
                    )}
                </div>

                {/* === COMMENTS === */}
                <CommentSection chapterNumber={chapterNumber} />

                {/* Quick nav */}
                <div className="flex items-center justify-center gap-4 mt-12 pb-10">
                    <Link
                        href="/"
                        className="text-ash-500 hover:text-toxic-green-DEFAULT text-xs font-mono transition-colors flex items-center gap-1"
                    >
                        <Home size={12} /> TRANG CHỦ
                    </Link>
                    <span className="text-ash-700">·</span>
                    <Link
                        href="/chapters"
                        className="text-ash-500 hover:text-toxic-green-DEFAULT text-xs font-mono transition-colors flex items-center gap-1"
                    >
                        <List size={12} /> MỤC LỤC
                    </Link>
                    {nextId && (
                        <>
                            <span className="text-ash-700">·</span>
                            <Link
                                href={`/chapters/${nextId}`}
                                className="text-ash-500 hover:text-blood-red-bright text-xs font-mono transition-colors flex items-center gap-1"
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

                <div className="relative grid grid-cols-4 items-center h-16">
                    <Link
                        href="/"
                        className="flex flex-col items-center justify-center gap-1 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors"
                    >
                        <Home size={18} />
                        <span className="text-[10px] font-mono">CHỦ</span>
                    </Link>

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

                    <button
                        onClick={() => setShowSettings(!showSettings)}
                        className="flex flex-col items-center justify-center gap-1 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors border-l border-ash-800/40"
                    >
                        <Settings size={18} />
                        <span className="text-[10px] font-mono">SET</span>
                    </button>
                </div>
            </div>

            {/* Bottom spacer for mobile nav */}
            <div className="h-20 md:h-0" />
        </div>
    );
}
