"use client";

import Link from "next/link";
import { BookMarked, GraduationCap, Languages, Loader2, Quote, RefreshCcw, Sparkles, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { useLocale } from "@/context/LocaleContext";
import { getReaderLearningStats, type ReaderLearningStatsResponse } from "@/lib/reader-learning";

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
                <div>1. Bôi đen từ hoặc cụm ngắn rồi bấm <span className="font-medium text-cyan-200">Tra nhanh</span>.</div>
                <div>2. Click đúp vào một từ ngắn để mở tra từ ngay.</div>
                <div>3. Sau khi đã chọn chữ, nhấn <span className="font-mono text-cyan-200">Alt+L</span>.</div>
            </div>
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
    const [stats, setStats] = useState<ReaderLearningStatsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [mobileOpen, setMobileOpen] = useState(false);
    const [audioActive, setAudioActive] = useState(false);

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

        window.addEventListener("reader-audio-state", handleAudioState as EventListener);
        return () => window.removeEventListener("reader-audio-state", handleAudioState as EventListener);
    }, []);

    const desktopBottom = useMemo(() => (audioActive ? 226 : 96), [audioActive]);
    const mobileBottom = useMemo(() => (audioActive ? 174 : 88), [audioActive]);

    return (
        <>
            <div className="fixed left-4 z-[58] hidden md:block" style={{ bottom: `${desktopBottom}px` }}>
                <div className="overflow-hidden rounded-2xl border border-cyan-900/30 bg-[#071018]/90 shadow-[0_18px_50px_rgba(0,0,0,0.38)] backdrop-blur">
                    <div className="border-b border-cyan-900/30 px-4 py-3">
                        <div className="flex items-center gap-2 text-cyan-300">
                            <Languages size={14} />
                            <span className="text-[11px] font-mono uppercase tracking-[0.28em]">Learning</span>
                        </div>
                        <p className="mt-2 max-w-[240px] text-xs leading-5 text-gray-400">
                            Tra từ, lưu câu và ôn lại ngay trong lúc đọc. Khu này sẽ là nền cho grammar hints
                            và SRS ở bước sau.
                        </p>
                    </div>

                    <div className="border-b border-cyan-900/20 px-4 py-3">
                        <StudyStats loading={loading} error={error} stats={stats} />
                    </div>

                    <LookupTips />
                    <StudyLinks />
                </div>
            </div>

            <div className="fixed left-4 z-[58] md:hidden" style={{ bottom: `${mobileBottom}px` }}>
                <button
                    type="button"
                    onClick={() => setMobileOpen(true)}
                    className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-[#071018]/95 px-4 py-3 text-sm text-cyan-200 shadow-[0_10px_30px_rgba(0,0,0,0.38)] backdrop-blur"
                >
                    <GraduationCap size={16} />
                    Learning
                </button>
            </div>

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
                            <StudyLinks onNavigate={() => setMobileOpen(false)} />
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
