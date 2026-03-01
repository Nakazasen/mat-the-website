import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Tag, Calendar, BookOpen } from "lucide-react";
import { getWikiEntry, getWikiEntries, WIKI_CATEGORIES } from "@/lib/api";

const CATEGORY_ICONS: Record<string, string> = {
    "Nhân vật": "👤",
    "Sinh vật": "🧟",
    "Thế lực": "⚔️",
    "Vật phẩm": "🗡️",
    "Địa điểm": "📍",
};

// Pre-generate known slugs for static generation
export async function generateStaticParams() {
    try {
        const entries = await getWikiEntries();
        return entries.map((e) => ({ slug: e.slug }));
    } catch {
        return [];
    }
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
    const { slug } = await params;
    try {
        const entry = await getWikiEntry(slug);
        return {
            title: `${entry.title} | Cẩm Nang Mạt Thế`,
            description: entry.summary || `Thông tin về ${entry.title} trong thế giới Mạt Thế.`,
        };
    } catch {
        return { title: "Không tìm thấy | Cẩm Nang Mạt Thế" };
    }
}

export default async function WikiDetailPage({ params }: { params: Promise<{ slug: string }> }) {
    const { slug } = await params;

    let entry;
    try {
        entry = await getWikiEntry(slug);
    } catch {
        notFound();
    }

    const categoryIcon = CATEGORY_ICONS[entry.category] || "📖";
    const formattedDate = new Date(entry.created_at).toLocaleDateString("vi-VN", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });

    return (
        <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
            {/* Back button */}
            <div className="mb-8">
                <Link
                    href="/wiki"
                    className="inline-flex items-center gap-2 text-xs font-mono text-gray-600 hover:text-green-500 transition-colors group"
                >
                    <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
                    QUAY LẠI CẨM NANG
                </Link>
            </div>

            {/* Hero image */}
            {entry.image_url && (
                <div className="relative w-full h-64 sm:h-80 rounded-xl overflow-hidden mb-8 border border-gray-800">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                        src={entry.image_url}
                        alt={entry.title}
                        className="w-full h-full object-cover"
                    />
                    {/* Dark gradient overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/40 to-transparent" />

                    {/* Category badge over image */}
                    <div className="absolute bottom-4 left-4">
                        <span className="text-xs font-mono text-green-400 bg-green-950/80 border border-green-800 px-3 py-1 rounded-full backdrop-blur-sm">
                            {categoryIcon} {entry.category}
                        </span>
                    </div>
                </div>
            )}

            {/* Header */}
            <div className="mb-8">
                {/* Category badge (when no image) */}
                {!entry.image_url && (
                    <div className="flex items-center gap-2 mb-4">
                        <span className="text-xs font-mono text-green-600 bg-green-950/40 border border-green-900 px-2 py-1 rounded">
                            {categoryIcon} {entry.category}
                        </span>
                    </div>
                )}

                {/* Title */}
                <h1 className="font-biohazard text-3xl sm:text-4xl text-worn-white tracking-wide mb-4 leading-tight">
                    {entry.title}
                </h1>

                {/* Meta info */}
                <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-gray-600">
                    <span className="flex items-center gap-1.5">
                        <Calendar size={12} />
                        {formattedDate}
                    </span>
                    <span className="flex items-center gap-1.5">
                        <BookOpen size={12} />
                        Cẩm Nang Mạt Thế
                    </span>
                </div>

                {/* Summary / Lead text */}
                {entry.summary && (
                    <div className="mt-6 pl-4 border-l-2 border-green-800">
                        <p className="text-ash-400 font-reading text-base leading-relaxed italic">
                            {entry.summary}
                        </p>
                    </div>
                )}
            </div>

            {/* Divider */}
            <div className="flex items-center gap-3 mb-8">
                <div className="flex-1 h-px bg-gray-800" />
                <span className="text-green-900 text-xs font-mono">☣</span>
                <div className="flex-1 h-px bg-gray-800" />
            </div>

            {/* Content */}
            {entry.content ? (
                <article
                    className="prose prose-invert prose-sm sm:prose-base max-w-none
                        prose-headings:font-biohazard prose-headings:text-worn-white
                        prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg
                        prose-p:text-ash-400 prose-p:leading-relaxed prose-p:font-reading
                        prose-a:text-green-500 prose-a:no-underline hover:prose-a:underline
                        prose-strong:text-ash-200 prose-strong:font-semibold
                        prose-em:text-ash-500
                        prose-ul:text-ash-400 prose-ol:text-ash-400
                        prose-li:marker:text-green-700
                        prose-hr:border-gray-800
                        prose-blockquote:border-green-800 prose-blockquote:text-ash-500
                        prose-code:text-green-400 prose-code:bg-green-950/30 prose-code:px-1 prose-code:rounded
                        prose-pre:bg-[#111] prose-pre:border prose-pre:border-gray-800"
                    dangerouslySetInnerHTML={{ __html: entry.content }}
                />
            ) : (
                <div className="text-center py-16 border border-dashed border-gray-800 rounded-lg">
                    <p className="text-gray-600 font-mono text-sm">Dữ liệu đang được biên soạn...</p>
                    <p className="text-gray-800 font-mono text-xs mt-2">☣ Classified - Pending Clearance</p>
                </div>
            )}

            {/* Tags */}
            {entry.tags && entry.tags.length > 0 && (
                <div className="mt-10 pt-6 border-t border-gray-800">
                    <div className="flex items-center gap-2 flex-wrap">
                        <Tag size={12} className="text-gray-700" />
                        {entry.tags.map((tag) => (
                            <Link
                                key={tag}
                                href={`/wiki?search=${encodeURIComponent(tag)}`}
                                className="text-xs font-mono text-gray-600 hover:text-green-500 bg-gray-900 hover:bg-green-950/30 border border-gray-800 hover:border-green-900 px-2.5 py-1 rounded transition-all"
                            >
                                {tag}
                            </Link>
                        ))}
                    </div>
                </div>
            )}

            {/* Related categories */}
            <div className="mt-10 p-5 bg-[#0d0d0d] border border-gray-800 rounded-xl">
                <p className="text-xs font-mono text-gray-700 mb-3 tracking-wider">KHÁM PHÁ THÊM</p>
                <div className="flex flex-wrap gap-2">
                    <Link
                        href="/wiki"
                        className="text-xs font-mono text-gray-600 hover:text-gray-300 bg-gray-900 border border-gray-800 hover:border-gray-700 px-3 py-1.5 rounded transition-all"
                    >
                        📋 Tất cả
                    </Link>
                    {WIKI_CATEGORIES.map((cat) => (
                        <Link
                            key={cat}
                            href={`/wiki?cat=${encodeURIComponent(cat)}`}
                            className={`text-xs font-mono px-3 py-1.5 rounded transition-all border ${cat === entry.category
                                    ? "text-green-400 bg-green-950/40 border-green-900"
                                    : "text-gray-600 hover:text-gray-300 bg-gray-900 border-gray-800 hover:border-gray-700"
                                }`}
                        >
                            {CATEGORY_ICONS[cat]} {cat}
                        </Link>
                    ))}
                </div>
            </div>
        </main>
    );
}
