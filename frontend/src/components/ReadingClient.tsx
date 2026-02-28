"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Settings, Home, List } from "lucide-react";

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
    const [fontSize, setFontSize] = useState(18);
    const [showSettings, setShowSettings] = useState(false);
    const [readingProgress, setReadingProgress] = useState(0);
    const [theme, setTheme] = useState<"dark" | "sepia">("dark");
    const contentRef = useRef<HTMLDivElement>(null);

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

    const themeStyles =
        theme === "sepia"
            ? { background: "#2c2318", color: "#d4b896" }
            : { background: "#161616", color: "#d4d0c8" };

    // Split content into paragraphs
    const paragraphs = content
        .split(/\n+/)
        .filter((p) => p.trim().length > 0);

    return (
        <div className="min-h-screen" style={themeStyles}>
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
                    <div className="border-t border-ash-800/60 bg-ash-950/95 px-4 py-3">
                        <div className="max-w-4xl mx-auto flex flex-wrap gap-6 items-center">
                            {/* Font size */}
                            <div className="flex items-center gap-3">
                                <span className="text-ash-400 text-xs font-mono">CỠ CHỮ</span>
                                <button
                                    onClick={() => setFontSize((s) => Math.max(14, s - 2))}
                                    className="w-7 h-7 border border-ash-700 text-ash-300 hover:border-toxic-green-DEFAULT hover:text-toxic-green-DEFAULT transition-colors rounded text-sm"
                                >
                                    A-
                                </button>
                                <span className="text-toxic-green-DEFAULT font-mono text-sm w-6 text-center">
                                    {fontSize}
                                </span>
                                <button
                                    onClick={() => setFontSize((s) => Math.min(28, s + 2))}
                                    className="w-7 h-7 border border-ash-700 text-ash-300 hover:border-toxic-green-DEFAULT hover:text-toxic-green-DEFAULT transition-colors rounded text-sm"
                                >
                                    A+
                                </button>
                            </div>

                            {/* Theme */}
                            <div className="flex items-center gap-3">
                                <span className="text-ash-400 text-xs font-mono">NỀN</span>
                                {(["dark", "sepia"] as const).map((t) => (
                                    <button
                                        key={t}
                                        onClick={() => setTheme(t)}
                                        className={`px-3 py-1 text-xs font-mono rounded border transition-colors ${theme === t
                                            ? "border-toxic-green-DEFAULT text-toxic-green-DEFAULT bg-toxic-green-DEFAULT/10"
                                            : "border-ash-700 text-ash-400 hover:border-ash-500"
                                            }`}
                                    >
                                        {t === "dark" ? "TỐI" : "NGỦ"}
                                    </button>
                                ))}
                            </div>

                            {/* Progress */}
                            <div className="text-ash-500 text-xs font-mono ml-auto">
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
                    <h1 className="font-biohazard text-3xl sm:text-4xl text-worn-white tracking-wide leading-tight">
                        {chapterTitle}
                    </h1>

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
                    className="reading-container"
                    style={{ fontSize: `${fontSize}px`, whiteSpace: "pre-wrap", lineHeight: 1.8 }}
                >
                    {content}
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

                {/* Quick nav */}
                <div className="flex items-center justify-center gap-4 mt-6">
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
