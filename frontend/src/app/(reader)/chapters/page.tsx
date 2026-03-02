import Link from "next/link";
import { ChevronRight, BookOpen, Search } from "lucide-react";
import { getChapters, getNovelSettings, type Chapter } from "@/lib/api";
import type { Metadata } from "next";
import ChapterJump from "@/components/ChapterJump";

export async function generateMetadata(): Promise<Metadata> {
    try {
        const novel = await getNovelSettings();
        return {
            title: "Mục Lục",
            description: `Danh sách toàn bộ ${novel.total_chapters}+ chương truyện ${novel.title}. Cập nhật mới nhất.`,
        };
    } catch {
        return {
            title: "Mục Lục",
            description: "Danh sách toàn bộ chương truyện Mạt Thế Sinh Hoá Nguy Cơ",
        };
    }
}

export const dynamic = "force-dynamic";
export const revalidate = 300;

interface Props {
    searchParams: Promise<{ page?: string; search?: string; tab?: string }>;
}

export default async function ChaptersPage({
    searchParams,
}: Props) {
    const resolvedSearchParams = await searchParams;
    const page = Math.max(1, parseInt(resolvedSearchParams.page || "1", 10));
    const search = resolvedSearchParams.search || "";
    const tab = resolvedSearchParams.tab === "side" ? "side" : "main";
    const isSideStory = tab === "side" ? "true" : "false";
    const LIMIT = 60;

    let data: {
        chapters: Chapter[];
        total: number;
        page: number;
        total_pages: number;
        max_chapter: number;
    } = { chapters: [], total: 0, page: 1, total_pages: 1, max_chapter: 0 };
    try {
        // Update api client call if I add search param to it, or just use fetch here
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(
            `${API_BASE_URL}/api/chapters?page=${page}&limit=${LIMIT}&search=${encodeURIComponent(search)}&is_side_story=${isSideStory}`,
            { cache: "no-store" }
        );
        if (res.ok) data = await res.json();
    } catch {
        // API not available
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
                        {search ? "KẾT QUẢ" : "MỤC LỤC"}
                    </h1>
                    {search && (
                        <div className="mb-6 flex items-center gap-2 text-toxic-green-DEFAULT font-mono text-sm group">
                            <span className="opacity-50 tracking-tighter">{" >>> "}</span>
                            TÌM KIẾM: <span className="bg-toxic-green-DEFAULT/20 px-2 py-0.5 rounded border border-toxic-green-DEFAULT/30">{search.toUpperCase()}</span>
                            <Link href="/chapters" className="ml-4 text-ash-500 hover:text-ash-300 underline decoration-ash-800 text-xs">
                                XÓA TÌM KIẾM
                            </Link>
                        </div>
                    )}
                    <div className="flex flex-wrap items-center gap-4">
                        <div className="flex items-center gap-2 text-ash-400 text-sm font-mono">
                            <BookOpen size={14} />
                            <span>
                                Tổng cộng{" "}
                                <span className="text-toxic-green-DEFAULT font-bold">{max_chapter || total || "813"}</span>{" "}
                                chương
                                <span className="ml-2 text-[10px] text-toxic-green-DEFAULT/40 border border-toxic-green-DEFAULT/20 px-1 rounded animate-pulse">
                                    LIVE
                                </span>
                            </span>
                        </div>
                        <div className="hazard-divider flex-1 max-w-xs" />
                    </div>
                </div>

                {/* === TABS === */}
                <div className="flex border-b border-ash-800 mb-8 rounded-t overflow-hidden">
                    <Link
                        href={`/chapters?tab=main${search ? `&search=${encodeURIComponent(search)}` : ''}`}
                        className={`flex-1 text-center py-3 sm:py-4 font-mono text-sm tracking-widest transition-all ${tab === 'main'
                            ? 'text-toxic-green-DEFAULT border-b-2 border-toxic-green-DEFAULT bg-toxic-green-DEFAULT/5'
                            : 'text-ash-500 hover:text-ash-300 hover:bg-ash-900/50'
                            }`}
                    >
                        MẠCH TRUYỆN CHÍNH
                    </Link>
                    <div className="w-px bg-ash-800 shrink-0" />
                    <Link
                        href={`/chapters?tab=side${search ? `&search=${encodeURIComponent(search)}` : ''}`}
                        className={`flex-1 text-center py-3 sm:py-4 font-mono text-sm tracking-widest transition-all ${tab === 'side'
                            ? 'text-toxic-green-DEFAULT border-b-2 border-toxic-green-DEFAULT bg-toxic-green-DEFAULT/5'
                            : 'text-ash-500 hover:text-ash-300 hover:bg-ash-900/50'
                            }`}
                    >
                        NGOẠI TRUYỆN & HỒ SƠ 📜
                    </Link>
                </div>

                {/* === QUICK JUMP BOX === */}
                <div className="card-biohazard rounded-lg p-4 mb-8 flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                    <ChapterJump />
                    <div className="flex gap-3 flex-wrap">
                        {[1, 100, 200, 400, 600, 800].filter(n => n <= (max_chapter || 2000)).map((n) => (
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
                                        {tab === 'side' && <span className="text-xs mr-2 relative -top-0.5">📜</span>}
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
                ) : search ? (
                    <div className="text-center py-20 card-biohazard rounded-lg border-dashed border-ash-800">
                        <div className="text-ash-500 font-mono text-sm mb-2">KHÔNG TÌM THẤY KẾT QUẢ</div>
                        <div className="text-ash-700 text-xs text-balance">Dữ liệu không tồn tại trong khu vực quét.</div>
                    </div>
                ) : tab === 'side' ? (
                    <div className="text-center py-20 card-biohazard rounded-lg border-dashed border-ash-800">
                        <div className="text-ash-500 font-mono text-sm mb-2">CHƯA CÓ NGOẠI TRUYỆN</div>
                        <div className="text-ash-700 text-xs text-balance">Hồ sơ bổ sung chưa được nạp vào hệ thống.</div>
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
                                href={`/chapters?page=${page - 1}&tab=${tab}${search ? `&search=${encodeURIComponent(search)}` : ''}`}
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
                                        href={`/chapters?page=${p}&tab=${tab}${search ? `&search=${encodeURIComponent(search)}` : ''}`}
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
                                href={`/chapters?page=${page + 1}&tab=${tab}${search ? `&search=${encodeURIComponent(search)}` : ''}`}
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
