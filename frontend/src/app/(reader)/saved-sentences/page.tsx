"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, Loader2, Quote, RefreshCcw } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";
import {
    getReaderLearningStats,
    getSavedReaderSentences,
    type ReaderLearningStatsResponse,
    type ReaderSavedSentenceItem,
} from "@/lib/reader-learning";
import type { Locale } from "@/lib/i18n/config";

const LOCALE_OPTIONS: Array<{ value: "" | Locale; label: string }> = [
    { value: "", label: "Tất cả" },
    { value: "en", label: "English" },
    { value: "ja", label: "日本語" },
    { value: "zh-CN", label: "中文" },
];

export default function SavedSentencesPage() {
    const { localizePath, locale } = useLocale();
    const [items, setItems] = useState<ReaderSavedSentenceItem[]>([]);
    const [stats, setStats] = useState<ReaderLearningStatsResponse | null>(null);
    const [filterLocale, setFilterLocale] = useState<"" | Locale>(locale === "vi" ? "" : locale);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadPage = useCallback(async (showRefreshing = false) => {
        if (showRefreshing) setRefreshing(true);
        else setLoading(true);
        setError(null);

        try {
            const [sentencesPayload, statsPayload] = await Promise.all([
                getSavedReaderSentences({ locale: filterLocale || undefined, page: 1, limit: 100 }),
                getReaderLearningStats(),
            ]);
            setItems(sentencesPayload.items);
            setStats(statsPayload);
        } catch (err: unknown) {
            setError((err as Error)?.message || "Không tải được danh sách câu đã lưu.");
            setItems([]);
            setStats(null);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [filterLocale]);

    useEffect(() => {
        void loadPage(false);
    }, [loadPage]);

    return (
        <div className="min-h-screen bg-black text-white">
            <div className="mx-auto max-w-5xl px-4 py-10">
                <Link
                    href={localizePath("/profile")}
                    className="inline-flex items-center gap-2 text-sm text-ash-400 hover:text-toxic-green-DEFAULT"
                >
                    <ChevronLeft size={16} />
                    Quay lại hồ sơ
                </Link>

                <div className="mt-6 rounded-3xl border border-ash-800 bg-ash-950/80 p-6 shadow-2xl">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                        <div>
                            <div className="flex items-center gap-3 text-cyan-300">
                                <Quote size={18} />
                                <span className="text-xs font-mono uppercase tracking-[0.3em]">Reader Learning</span>
                            </div>
                            <h1 className="mt-3 text-3xl font-biohazard tracking-wide">Câu đã lưu</h1>
                            <p className="mt-2 max-w-2xl text-sm leading-6 text-ash-400">
                                Trang này gom các câu anh đã lưu trong lúc đọc. Đây là nền cho sentence mode, replay theo câu
                                và grammar hints ở các bước tiếp theo.
                            </p>
                        </div>

                        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                            <label className="flex flex-col gap-2 text-sm text-ash-400">
                                <span>Ngôn ngữ</span>
                                <select
                                    value={filterLocale}
                                    onChange={(event) => setFilterLocale(event.target.value as "" | Locale)}
                                    className="rounded-xl border border-ash-700 bg-black px-3 py-2 text-white outline-none"
                                >
                                    {LOCALE_OPTIONS.map((option) => (
                                        <option key={option.label} value={option.value}>
                                            {option.label}
                                        </option>
                                    ))}
                                </select>
                            </label>

                            <button
                                type="button"
                                onClick={() => void loadPage(true)}
                                disabled={refreshing}
                                className="inline-flex items-center gap-2 rounded-xl border border-cyan-700/40 px-4 py-2 text-sm text-cyan-300 hover:bg-cyan-500/10 disabled:opacity-50"
                            >
                                {refreshing ? <Loader2 size={16} className="animate-spin" /> : <RefreshCcw size={16} />}
                                Làm mới
                            </button>
                        </div>
                    </div>

                    <div className="mt-6 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-2xl border border-ash-800 bg-black/20 px-4 py-4">
                            <div className="text-[10px] font-mono uppercase tracking-[0.24em] text-ash-500">Câu đã lưu</div>
                            <div className="mt-2 text-3xl font-semibold text-white">{stats?.saved_sentence_count ?? "..."}</div>
                        </div>
                        <div className="rounded-2xl border border-ash-800 bg-black/20 px-4 py-4">
                            <div className="text-[10px] font-mono uppercase tracking-[0.24em] text-ash-500">Từ đã lưu</div>
                            <div className="mt-2 text-3xl font-semibold text-white">{stats?.saved_vocab_count ?? "..."}</div>
                        </div>
                        <div className="rounded-2xl border border-ash-800 bg-black/20 px-4 py-4">
                            <div className="text-[10px] font-mono uppercase tracking-[0.24em] text-ash-500">Đến hạn ôn</div>
                            <div className="mt-2 text-3xl font-semibold text-toxic-green-DEFAULT">{stats?.review_due_count ?? "..."}</div>
                        </div>
                    </div>

                    <div className="mt-6">
                        {loading && (
                            <div className="flex items-center gap-2 rounded-2xl border border-ash-800 bg-black/30 px-4 py-4 text-sm text-ash-300">
                                <Loader2 size={16} className="animate-spin" />
                                Đang tải danh sách câu đã lưu...
                            </div>
                        )}

                        {!loading && error && (
                            <div className="rounded-2xl border border-red-900/40 bg-red-950/20 px-4 py-4 text-sm text-red-200">
                                {error}
                            </div>
                        )}

                        {!loading && !error && items.length === 0 && (
                            <div className="rounded-2xl border border-dashed border-ash-700 bg-black/20 px-4 py-8 text-center text-sm text-ash-500">
                                Chưa có câu nào được lưu cho bộ lọc hiện tại.
                            </div>
                        )}

                        {!loading && !error && items.length > 0 && (
                            <div className="space-y-4">
                                {items.map((item) => (
                                    <div key={item.id} className="rounded-2xl border border-ash-800 bg-black/25 px-4 py-4">
                                        <div className="flex flex-wrap items-start justify-between gap-3">
                                            <div className="text-xs font-mono uppercase tracking-[0.2em] text-cyan-300">
                                                {item.locale}
                                                {item.chapter_id ? ` · chương ${item.chapter_id}` : ""}
                                            </div>
                                            <div className="text-xs text-ash-500">
                                                {new Date(item.created_at).toLocaleString("vi-VN")}
                                            </div>
                                        </div>

                                        <div className="mt-3 text-base leading-8 text-white">
                                            {item.sentence_text}
                                        </div>

                                        {item.meaning_vi && (
                                            <div className="mt-3 rounded-xl border border-ash-800 bg-ash-950/80 px-3 py-3 text-sm text-ash-200">
                                                {item.meaning_vi}
                                            </div>
                                        )}

                                        {item.note && (
                                            <div className="mt-3 text-sm leading-6 text-ash-400">
                                                {item.note}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
