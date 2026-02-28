import Link from "next/link";
import { ChevronRight, BookOpen, Search } from "lucide-react";
import { getChapters } from "@/lib/api";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Mục Lục",
    description: "Danh sách toàn bộ 813+ chương truyện Mạt Thế Sinh Hoá Nguy Cơ",
};

export const revalidate = 300;

interface Props {
    searchParams: { page?: string };
}

export default async function ChaptersPage({
    searchParams,
}: {
    searchParams: Promise<{ page?: string }>;
}) {
    const resolvedSearchParams = await searchParams;
    const page = Math.max(1, parseInt(resolvedSearchParams.page || "1", 10));
    const LIMIT = 60;

    let data: {
        chapters: any[];
        total: number;
        page: number;
        total_pages: number;
        max_chapter: number;
    } = { chapters: [], total: 0, page: 1, total_pages: 1, max_chapter: 0 };
    try {
        data = await getChapters(page, LIMIT);
    } catch {
        // API not available, show empty
    }

    const { chapters, total, total_pages, max_chapter } = data;

    return (
        <div className="min-h-screen bg-ash-dark py-12 px-4 sm:px-6">
            <div className="max-w-6xl mx-auto">
                {/* === HEADER === */}
                <div className="mb-10">
                    <div className="font-mono text-xs text-toxic-green-DEFAULT tracking-[0.3em] mb-2">
                        ☣ DANH SÁCH CHƯƠNG
                    </div>
                    <h1 className="font-biohazard text-5xl sm:text-6xl text-worn-white tracking-wide mb-4">
                        MỤC LỤC
                    </h1>
                    <div className="flex flex-wrap items-center gap-4">
                        <div className="flex items-center gap-2 text-ash-400 text-sm font-mono">
                            <BookOpen size={14} />
                            <span>
                                Tổng cộng{" "}
                                <span className="text-toxic-green-DEFAULT font-bold">{max_chapter || total || "813+"}</span>{" "}
                                chương
                            </span>
                        </div>
                        <div className="hazard-divider flex-1 max-w-xs" />
                    </div>
                </div>

                {/* === QUICK JUMP BOX === */}
                <div className="card-biohazard rounded-lg p-4 mb-8 flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                    <div className="flex items-center gap-2 text-ash-400 text-sm shrink-0">
                        <Search size={14} />
                        <span className="font-mono">NHẢY ĐẾN CHƯƠNG</span>
                    </div>
                    <div className="flex gap-3 flex-wrap">
                        {[1, 100, 200, 400, 600, 800].map((n) => (
                            <Link
                                key={n}
                                href={`/chapters/${n}`}
                                className="px-3 py-1 text-xs font-mono border border-ash-700 text-ash-400 hover:border-toxic-green-DEFAULT/50 hover:text-toxic-green-DEFAULT transition-colors rounded"
                            >
                                CH.{n}
                            </Link>
                        ))}
                    </div>
                </div>

                {/* === CHAPTER GRID === */}
                {chapters.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                        {chapters.map((chapter, i) => (
                            <Link
                                key={chapter.id}
                                href={`/chapters/${chapter.chapter_number}`}
                                className="card-biohazard rounded p-3 group flex items-center gap-3 chapter-item relative hazard-corner"
                            >
                                {/* Chapter number */}
                                <div className="shrink-0 w-12 text-right">
                                    <span className="font-mono text-xs text-ash-600 chapter-number transition-colors">
                                        {String(chapter.chapter_number).padStart(3, "0")}
                                    </span>
                                </div>
                                {/* Divider */}
                                <div className="w-px h-8 bg-ash-800 group-hover:bg-toxic-green-DEFAULT/30 transition-colors shrink-0" />
                                {/* Title */}
                                <div className="flex-1 min-w-0">
                                    <div className="text-ash-300 text-sm font-reading leading-tight group-hover:text-worn-white transition-colors line-clamp-2">
                                        {chapter.title}
                                    </div>
                                </div>
                                <ChevronRight
                                    size={12}
                                    className="text-ash-700 group-hover:text-toxic-green-DEFAULT shrink-0 transition-colors"
                                />
                            </Link>
                        ))}
                    </div>
                ) : (
                    /* Skeleton loading */
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                        {Array.from({ length: 60 }).map((_, i) => (
                            <div
                                key={i}
                                className="card-biohazard rounded p-3 animate-pulse flex items-center gap-3"
                            >
                                <div className="w-12 h-3 bg-ash-800 rounded" />
                                <div className="w-px h-8 bg-ash-800" />
                                <div className="flex-1">
                                    <div className="h-3 bg-ash-800 rounded w-full mb-1" />
                                    <div className="h-3 bg-ash-800 rounded w-2/3" />
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* === PAGINATION === */}
                {total_pages > 1 && (
                    <div className="mt-10 flex items-center justify-center gap-2 flex-wrap">
                        {page > 1 && (
                            <Link
                                href={`/chapters?page=${page - 1}`}
                                className="btn-toxic text-sm py-2 px-4"
                            >
                                <span>← TRANG TRƯỚC</span>
                            </Link>
                        )}

                        {/* Page numbers */}
                        <div className="flex gap-1">
                            {Array.from({ length: Math.min(total_pages, 9) }, (_, i) => {
                                let p: number;
                                if (total_pages <= 9) {
                                    p = i + 1;
                                } else if (page <= 5) {
                                    p = i + 1;
                                } else if (page >= total_pages - 4) {
                                    p = total_pages - 8 + i;
                                } else {
                                    p = page - 4 + i;
                                }
                                return (
                                    <Link
                                        key={p}
                                        href={`/chapters?page=${p}`}
                                        className={`w-10 h-10 flex items-center justify-center font-mono text-sm rounded transition-all ${p === page
                                            ? "bg-toxic-green-DEFAULT text-black font-bold"
                                            : "border border-ash-800 text-ash-400 hover:border-toxic-green-DEFAULT/40 hover:text-toxic-green-DEFAULT"
                                            }`}
                                    >
                                        {p}
                                    </Link>
                                );
                            })}
                        </div>

                        {page < total_pages && (
                            <Link
                                href={`/chapters?page=${page + 1}`}
                                className="btn-toxic text-sm py-2 px-4"
                            >
                                <span>TRANG SAU →</span>
                            </Link>
                        )}
                    </div>
                )}

                {/* Info line */}
                <div className="text-center mt-6 font-mono text-xs text-ash-600">
                    TRANG {page} / {total_pages || 1} · {LIMIT} CHƯƠNG MỖI TRANG
                </div>
            </div>
        </div>
    );
}
