"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { BookMarked, ChevronLeft, Loader2, RefreshCcw, Search, Sparkles } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";
import {
    getReaderLearningStats,
    getSavedReaderVocab,
    reviewSavedReaderVocab,
    type ReaderLearningStatsResponse,
    type ReaderReviewResponse,
    type ReaderSavedVocabItem,
} from "@/lib/reader-learning";
import type { Locale } from "@/lib/i18n/config";

const LOCALE_OPTIONS: Array<{ value: "" | Locale; label: string }> = [
    { value: "", label: "Tất cả" },
    { value: "en", label: "English" },
    { value: "ja", label: "日本語" },
    { value: "zh-CN", label: "中文" },
];

const REVIEW_BUTTONS: Array<{ grade: number; label: string; hint: string }> = [
    { grade: 0, label: "Quên", hint: "Ôn lại ngay" },
    { grade: 1, label: "Khó", hint: "Lặp lại sớm" },
    { grade: 2, label: "Ổn", hint: "Nhớ tạm ổn" },
    { grade: 3, label: "Nhớ rõ", hint: "Đẩy lịch xa hơn" },
];

type ReviewMap = Record<string, ReaderReviewResponse>;
type SortKey = "newest" | "oldest" | "due" | "term";

function formatReviewSummary(review?: ReaderReviewResponse | null): string | null {
    if (!review) return null;
    const nextReview = review.next_review_at
        ? new Date(review.next_review_at).toLocaleString("vi-VN")
        : "ngay bây giờ";
    return `Đã ôn ${review.review_count} lần. Lần tới: ${nextReview}.`;
}

function isDueForReview(item: ReaderSavedVocabItem): boolean {
    if (item.due_for_review) return true;
    if (!item.next_review_at) return false;
    return new Date(item.next_review_at).getTime() <= Date.now();
}

export default function SavedVocabPage() {
    const { localizePath, locale } = useLocale();
    const [items, setItems] = useState<ReaderSavedVocabItem[]>([]);
    const [stats, setStats] = useState<ReaderLearningStatsResponse | null>(null);
    const [reviewMap, setReviewMap] = useState<ReviewMap>({});
    const [filterLocale, setFilterLocale] = useState<"" | Locale>(locale === "vi" ? "" : locale);
    const [searchQuery, setSearchQuery] = useState("");
    const [sortKey, setSortKey] = useState<SortKey>("due");
    const [dueOnly, setDueOnly] = useState(false);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [reviewLoadingId, setReviewLoadingId] = useState<string | null>(null);
    const [reviewMessage, setReviewMessage] = useState<string | null>(null);

    const loadPage = useCallback(async (showRefreshing = false) => {
        if (showRefreshing) setRefreshing(true);
        else setLoading(true);
        setError(null);

        try {
            const [vocabPayload, statsPayload] = await Promise.all([
                getSavedReaderVocab({ locale: filterLocale || undefined, page: 1, limit: 100 }),
                getReaderLearningStats(),
            ]);
            setItems(vocabPayload.items);
            setStats(statsPayload);
        } catch (err: unknown) {
            setError((err as Error)?.message || "Không tải được danh sách từ đã lưu.");
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

    const handleReview = useCallback(async (savedVocabId: string, grade: number) => {
        setReviewLoadingId(savedVocabId);
        setReviewMessage(null);
        setError(null);

        try {
            const payload = await reviewSavedReaderVocab({
                saved_vocab_id: savedVocabId,
                grade,
            });
            setReviewMap((prev) => ({ ...prev, [savedVocabId]: payload }));
            setItems((prev) =>
                prev.map((item) =>
                    item.id === savedVocabId
                        ? {
                              ...item,
                              review_count: payload.review_count,
                              next_review_at: payload.next_review_at ?? null,
                              interval_days: payload.interval_days,
                              ease: payload.ease,
                              due_for_review:
                                  !!payload.next_review_at &&
                                  new Date(payload.next_review_at).getTime() <= Date.now(),
                          }
                        : item,
                ),
            );
            setReviewMessage("Đã cập nhật lịch ôn cho từ vừa chọn.");
            const statsPayload = await getReaderLearningStats();
            setStats(statsPayload);
        } catch (err: unknown) {
            setError((err as Error)?.message || "Không cập nhật được lịch ôn.");
        } finally {
            setReviewLoadingId(null);
        }
    }, []);

    const visibleItems = useMemo(() => {
        const query = searchQuery.trim().toLowerCase();
        const filtered = items.filter((item) => {
            if (dueOnly && !isDueForReview(item)) {
                return false;
            }

            if (!query) return true;
            const haystack = [
                item.term,
                item.reading || "",
                item.meaning_vi || "",
                item.notes || "",
                item.context_sentence || "",
            ]
                .join(" ")
                .toLowerCase();
            return haystack.includes(query);
        });

        filtered.sort((left, right) => {
            if (sortKey === "oldest") {
                return new Date(left.created_at).getTime() - new Date(right.created_at).getTime();
            }
            if (sortKey === "term") {
                return left.term.localeCompare(right.term, "vi");
            }
            if (sortKey === "due") {
                const leftDue = isDueForReview(left);
                const rightDue = isDueForReview(right);
                if (leftDue !== rightDue) return leftDue ? -1 : 1;

                const leftNext = left.next_review_at ? new Date(left.next_review_at).getTime() : Number.MAX_SAFE_INTEGER;
                const rightNext = right.next_review_at ? new Date(right.next_review_at).getTime() : Number.MAX_SAFE_INTEGER;
                if (leftNext !== rightNext) return leftNext - rightNext;
            }
            return new Date(right.created_at).getTime() - new Date(left.created_at).getTime();
        });

        return filtered;
    }, [dueOnly, items, searchQuery, sortKey]);

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
                                <BookMarked size={18} />
                                <span className="text-xs font-mono uppercase tracking-[0.3em]">Reader Learning</span>
                            </div>
                            <h1 className="mt-3 text-3xl font-biohazard tracking-wide">Từ đã lưu</h1>
                            <p className="mt-2 max-w-2xl text-sm leading-6 text-ash-400">
                                Đây là kho từ vựng lấy trực tiếp từ lúc đọc truyện. Anh có thể lọc theo ngôn ngữ, xem ngữ cảnh,
                                rồi đánh giá nhanh để hệ thống chuẩn bị cho ôn tập SRS ở bước tiếp theo.
                            </p>
                        </div>

                        <div className="flex flex-col gap-3 lg:min-w-[420px]">
                            <label className="flex items-center gap-2 rounded-xl border border-ash-800 bg-black/20 px-3 py-2 text-sm text-ash-400">
                                <Search size={16} className="text-cyan-300" />
                                <input
                                    value={searchQuery}
                                    onChange={(event) => setSearchQuery(event.target.value)}
                                    placeholder="Tìm theo từ, nghĩa, ghi chú, ngữ cảnh..."
                                    className="w-full bg-transparent text-sm text-white outline-none placeholder:text-ash-500"
                                />
                            </label>

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

                            <label className="flex flex-col gap-2 text-sm text-ash-400">
                                <span>Sắp xếp</span>
                                <select
                                    value={sortKey}
                                    onChange={(event) => setSortKey(event.target.value as SortKey)}
                                    className="rounded-xl border border-ash-700 bg-black px-3 py-2 text-white outline-none"
                                >
                                    <option value="due">Đến hạn ôn trước</option>
                                    <option value="newest">Mới nhất</option>
                                    <option value="oldest">Cũ nhất</option>
                                    <option value="term">Theo tên từ</option>
                                </select>
                            </label>

                            <label className="inline-flex items-center gap-2 rounded-xl border border-ash-800 bg-black/20 px-3 py-2 text-sm text-ash-300">
                                <input
                                    type="checkbox"
                                    checked={dueOnly}
                                    onChange={(event) => setDueOnly(event.target.checked)}
                                    className="h-4 w-4 rounded border-ash-600 bg-transparent"
                                />
                                Chỉ hiện mục đến hạn ôn
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
                    </div>

                    <div className="mt-6 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-2xl border border-ash-800 bg-black/20 px-4 py-4">
                            <div className="text-[10px] font-mono uppercase tracking-[0.24em] text-ash-500">Tổng từ đã lưu</div>
                            <div className="mt-2 text-3xl font-semibold text-white">{stats?.saved_vocab_count ?? "..."}</div>
                        </div>
                        <div className="rounded-2xl border border-ash-800 bg-black/20 px-4 py-4">
                            <div className="text-[10px] font-mono uppercase tracking-[0.24em] text-ash-500">Câu đã lưu</div>
                            <div className="mt-2 text-3xl font-semibold text-white">{stats?.saved_sentence_count ?? "..."}</div>
                        </div>
                        <div className="rounded-2xl border border-ash-800 bg-black/20 px-4 py-4">
                            <div className="text-[10px] font-mono uppercase tracking-[0.24em] text-ash-500">Đến hạn ôn</div>
                            <div className="mt-2 text-3xl font-semibold text-toxic-green-DEFAULT">{stats?.review_due_count ?? "..."}</div>
                        </div>
                    </div>

                    {reviewMessage && (
                        <div className="mt-6 rounded-2xl border border-green-900/40 bg-green-950/20 px-4 py-4 text-sm text-green-200">
                            {reviewMessage}
                        </div>
                    )}

                    <div className="mt-6">
                        {loading && (
                            <div className="flex items-center gap-2 rounded-2xl border border-ash-800 bg-black/30 px-4 py-4 text-sm text-ash-300">
                                <Loader2 size={16} className="animate-spin" />
                                Đang tải danh sách từ đã lưu...
                            </div>
                        )}

                        {!loading && error && (
                            <div className="rounded-2xl border border-red-900/40 bg-red-950/20 px-4 py-4 text-sm text-red-200">
                                {error}
                            </div>
                        )}

                        {!loading && !error && visibleItems.length === 0 && (
                            <div className="rounded-2xl border border-dashed border-ash-700 bg-black/20 px-4 py-8 text-center text-sm text-ash-500">
                                Chưa có từ nào được lưu cho bộ lọc hiện tại.
                            </div>
                        )}

                        {!loading && !error && visibleItems.length > 0 && (
                            <div className="space-y-4">
                                {visibleItems.map((item) => {
                                    const review = reviewMap[item.id];
                                    return (
                                        <div key={item.id} className="rounded-2xl border border-ash-800 bg-black/25 px-4 py-4">
                                            <div className="flex flex-wrap items-start justify-between gap-3">
                                                <div>
                                                    <div className="text-lg font-semibold text-white">{item.term}</div>
                                                    <div className="mt-1 flex flex-wrap gap-2 text-xs font-mono uppercase tracking-[0.2em] text-cyan-300">
                                                        <span>{item.locale}</span>
                                                        {item.reading && <span>{item.reading}</span>}
                                                        {item.pos && <span>{item.pos}</span>}
                                                        {item.source && <span>{item.source}</span>}
                                                    </div>
                                                </div>
                                                <div className="text-xs text-ash-500">
                                                    {new Date(item.created_at).toLocaleString("vi-VN")}
                                                </div>
                                            </div>

                                            <div className="mt-3 text-sm leading-6 text-ash-200">
                                                {item.meaning_vi || "Chưa có nghĩa tiếng Việt được lưu cho mục này."}
                                            </div>

                                            <div className="mt-3 flex flex-wrap gap-2 text-xs">
                                                {isDueForReview(item) ? (
                                                    <span className="rounded-full border border-toxic-green-DEFAULT/30 bg-toxic-green-DEFAULT/10 px-2 py-1 text-toxic-green-DEFAULT">
                                                        Đến hạn ôn
                                                    </span>
                                                ) : (
                                                    <span className="rounded-full border border-ash-700 px-2 py-1 text-ash-400">
                                                        Chưa đến hạn ôn
                                                    </span>
                                                )}
                                                {item.next_review_at && (
                                                    <span className="rounded-full border border-cyan-900/30 px-2 py-1 text-cyan-200">
                                                        Ôn lại: {new Date(item.next_review_at).toLocaleString("vi-VN")}
                                                    </span>
                                                )}
                                                {!!item.review_count && (
                                                    <span className="rounded-full border border-ash-700 px-2 py-1 text-ash-400">
                                                        Đã ôn {item.review_count} lần
                                                    </span>
                                                )}
                                            </div>

                                            {item.notes && (
                                                <div className="mt-3 rounded-xl border border-ash-800 bg-ash-950/70 px-3 py-3 text-sm text-ash-300">
                                                    {item.notes}
                                                </div>
                                            )}

                                            {item.context_sentence && (
                                                <div className="mt-3 rounded-xl border border-ash-800 bg-black/20 px-3 py-3 text-sm italic text-ash-400">
                                                    {item.context_sentence}
                                                </div>
                                            )}

                                            <div className="mt-4 flex flex-wrap items-center gap-2">
                                                {REVIEW_BUTTONS.map((button) => (
                                                    <button
                                                        key={button.grade}
                                                        type="button"
                                                        onClick={() => void handleReview(item.id, button.grade)}
                                                        disabled={reviewLoadingId === item.id}
                                                        className="rounded-lg border border-cyan-900/30 px-3 py-2 text-xs text-cyan-200 hover:border-cyan-500/40 hover:bg-cyan-500/10 disabled:opacity-50"
                                                        title={button.hint}
                                                    >
                                                        {reviewLoadingId === item.id ? (
                                                            <span className="inline-flex items-center gap-2">
                                                                <Loader2 size={12} className="animate-spin" />
                                                                Đang lưu
                                                            </span>
                                                        ) : (
                                                            button.label
                                                        )}
                                                    </button>
                                                ))}
                                            </div>

                                            {review && (
                                                <div className="mt-3 inline-flex items-center gap-2 rounded-xl border border-toxic-green-DEFAULT/20 bg-toxic-green-DEFAULT/10 px-3 py-2 text-sm text-toxic-green-DEFAULT">
                                                    <Sparkles size={14} />
                                                    {formatReviewSummary(review)}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
