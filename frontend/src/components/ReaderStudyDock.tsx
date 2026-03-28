"use client";

import Link from "next/link";
import { BookMarked, Languages, Loader2, Quote, RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";

import { useLocale } from "@/context/LocaleContext";
import { getReaderLearningStats, type ReaderLearningStatsResponse } from "@/lib/reader-learning";

export default function ReaderStudyDock() {
    const { localizePath } = useLocale();
    const [stats, setStats] = useState<ReaderLearningStatsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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

    return (
        <div className="fixed bottom-24 left-4 z-[58] hidden md:block">
            <div className="overflow-hidden rounded-2xl border border-cyan-900/30 bg-[#071018]/90 shadow-[0_18px_50px_rgba(0,0,0,0.38)] backdrop-blur">
                <div className="border-b border-cyan-900/30 px-4 py-3">
                    <div className="flex items-center gap-2 text-cyan-300">
                        <Languages size={14} />
                        <span className="text-[11px] font-mono uppercase tracking-[0.28em]">
                            Learning
                        </span>
                    </div>
                    <p className="mt-2 max-w-[240px] text-xs leading-5 text-gray-400">
                        Tra từ, lưu câu và ôn lại ngay trong lúc đọc. Kho học tập này là nền cho grammar hints và SRS ở bước sau.
                    </p>
                </div>

                <div className="border-b border-cyan-900/20 px-4 py-3">
                    {loading && (
                        <div className="flex items-center gap-2 text-xs text-ash-400">
                            <Loader2 size={12} className="animate-spin" />
                            Đang tải thống kê...
                        </div>
                    )}

                    {!loading && error && (
                        <div className="text-xs leading-5 text-amber-300">
                            {error}
                        </div>
                    )}

                    {!loading && !error && stats && (
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
                    )}
                </div>

                <div className="grid grid-cols-1 gap-2 p-3">
                    <Link
                        href={localizePath("/saved-vocab")}
                        className="inline-flex items-center gap-2 rounded-xl border border-cyan-900/30 px-3 py-2 text-sm text-gray-200 hover:border-cyan-500/40 hover:text-cyan-200"
                    >
                        <BookMarked size={14} />
                        Từ đã lưu
                    </Link>
                    <Link
                        href={localizePath("/saved-sentences")}
                        className="inline-flex items-center gap-2 rounded-xl border border-cyan-900/30 px-3 py-2 text-sm text-gray-200 hover:border-cyan-500/40 hover:text-cyan-200"
                    >
                        <Quote size={14} />
                        Câu đã lưu
                    </Link>
                    <Link
                        href={localizePath("/saved-vocab")}
                        className="inline-flex items-center gap-2 rounded-xl border border-cyan-900/30 px-3 py-2 text-sm text-gray-200 hover:border-cyan-500/40 hover:text-cyan-200"
                    >
                        <RefreshCcw size={14} />
                        Ôn tập nhanh
                    </Link>
                </div>
            </div>
        </div>
    );
}
