import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Tag, Calendar, BookOpen, Star } from "lucide-react";
import { getWikiEntry, getWikiEntries, WIKI_CATEGORIES } from "@/lib/api";
import FactionOrgChart from "@/components/FactionOrgChart";
import WikiSettingsWrapper from "@/components/WikiSettingsWrapper";

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

export const dynamic = "force-dynamic";

export default async function WikiDetailPage({ params }: { params: Promise<{ slug: string }> }) {
    const { slug } = await params;

    let entry;
    try {
        entry = await getWikiEntry(slug);
    } catch {
        notFound();
    }

    if (!entry) notFound();

    const categoryIcon = entry.category ? (CATEGORY_ICONS[entry.category] || "📖") : "📖";
    const formattedDate = entry.created_at 
        ? new Date(entry.created_at).toLocaleDateString("vi-VN", {
            year: "numeric",
            month: "long",
            day: "numeric",
        })
        : "N/A";

    return (
        <WikiSettingsWrapper>
            <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
            {/* Back button */}
            <div className="mb-8">
                <Link
                    href="/wiki"
                    className="inline-flex items-center gap-2 text-xs font-mono text-reader-muted hover:text-reader-accent transition-colors group"
                >
                    <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
                    QUAY LẠI CẨM NANG
                </Link>
            </div>

            {/* Hero image */}
            {entry.image_url && (
                <div className="relative w-full h-64 sm:h-80 rounded-xl overflow-hidden mb-8 border border-reader-border shadow-lg">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                        src={entry.image_url}
                        alt={entry.title}
                        className="w-full h-full object-cover"
                    />
                    {/* Theme-aware gradient overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-reader-bg via-reader-bg/40 to-transparent" />

                    {/* Category badge over image */}
                    <div className="absolute bottom-4 left-4">
                        <span className="text-xs font-mono text-reader-accent bg-reader-bg/80 border border-reader-border px-3 py-1 rounded-full backdrop-blur-sm">
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
                        <span className="text-xs font-mono text-reader-accent bg-reader-accent/10 border border-reader-accent/30 px-2 py-1 rounded">
                            {categoryIcon} {entry.category}
                        </span>
                    </div>
                )}

                {/* Title */}
                <h1 className="font-biohazard text-3xl sm:text-4xl text-reader-text tracking-wide mb-4 leading-tight flex items-center gap-3">
                    {entry.title}
                    {entry.is_main_character && (
                        <span className="bg-yellow-500 text-black px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 shadow-[0_0_10px_rgba(234,179,8,0.3)] shrink-0">
                            <Star size={10} fill="currentColor" /> CHÍNH
                        </span>
                    )}
                </h1>

                {/* Meta info */}
                <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-reader-muted">
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
                    <div className="mt-6 pl-4 border-l-2 border-reader-accent/50">
                        <div
                            className="text-reader-muted font-reading text-base leading-relaxed italic rich-text-content"
                            dangerouslySetInnerHTML={{ __html: entry.summary }}
                        />
                    </div>
                )}
            </div>

            {/* Divider */}
            <div className="flex items-center gap-3 mb-8">
                <div className="flex-1 h-px bg-reader-border" />
                <span className="text-reader-muted text-xs font-mono opacity-40">☣</span>
                <div className="flex-1 h-px bg-reader-border" />
            </div>

            {/* Content */}
            {entry.content ? (
                <article
                    className="prose prose-invert prose-sm sm:prose-base max-w-none
                        prose-headings:font-biohazard prose-headings:text-reader-text
                        prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg
                        prose-p:text-reader-text prose-p:leading-relaxed prose-p:font-reading
                        prose-a:text-reader-accent prose-a:no-underline hover:prose-a:underline
                        prose-strong:text-reader-text prose-strong:font-bold
                        prose-em:text-reader-text/80
                        prose-ul:text-reader-text prose-ol:text-reader-text
                        prose-li:marker:text-reader-accent
                        prose-hr:border-reader-border
                        prose-blockquote:border-reader-accent prose-blockquote:text-reader-muted
                        prose-code:text-reader-accent prose-code:bg-reader-accent/10 prose-code:px-1 prose-code:rounded
                        prose-pre:bg-reader-bg/40 prose-pre:border prose-pre:border-reader-border"
                    dangerouslySetInnerHTML={{ __html: entry.content }}
                />
            ) : (
                <div className="text-center py-16 border border-dashed border-reader-border rounded-lg">
                    <p className="text-reader-muted font-mono text-sm">Dữ liệu đang được biên soạn...</p>
                    <p className="text-reader-muted/40 font-mono text-xs mt-2">☣ Classified - Pending Clearance</p>
                </div>
            )}

            {/* Tags */}
            {entry.tags && entry.tags.length > 0 && (
                <div className="mt-10 pt-6 border-t border-reader-border">
                    <div className="flex items-center gap-2 flex-wrap">
                        <Tag size={12} className="text-reader-muted" />
                        {entry.tags.map((tag) => (
                            <Link
                                key={tag}
                                href={`/wiki?search=${encodeURIComponent(tag)}`}
                                className="text-xs font-mono text-reader-muted hover:text-reader-accent bg-reader-bg border border-reader-border hover:border-reader-accent/40 px-2.5 py-1 rounded transition-all"
                            >
                                {tag}
                            </Link>
                        ))}
                    </div>
                </div>
            )}

            {/* Faction Org Chart (only for category "Thế lực") */}
            {entry.category === "Thế lực" && (
                <FactionOrgChart slug={entry.slug} />
            )}

            {/* Related categories */}
            <div className="mt-10 p-5 bg-reader-bg/40 border border-reader-border rounded-xl backdrop-blur-sm">
                <p className="text-xs font-mono text-reader-muted mb-3 tracking-wider">KHÁM PHÁ THÊM</p>
                <div className="flex flex-wrap gap-2">
                    <Link
                        href="/wiki"
                        className="text-xs font-mono text-reader-muted hover:text-reader-text bg-reader-bg border border-reader-border hover:border-reader-accent px-3 py-1.5 rounded transition-all"
                    >
                        📋 Tất cả
                    </Link>
                    {WIKI_CATEGORIES.map((cat) => (
                        <Link
                            key={cat}
                            href={`/wiki?cat=${encodeURIComponent(cat)}`}
                            className={`text-xs font-mono px-3 py-1.5 rounded transition-all border ${cat === entry.category
                                ? "text-reader-accent bg-reader-accent/10 border-reader-accent/30"
                                : "text-reader-muted hover:text-reader-text bg-reader-bg border-reader-border hover:border-reader-accent"
                                }`}
                        >
                            {CATEGORY_ICONS[cat]} {cat}
                        </Link>
                    ))}
                </div>
            </div>
        </main>
    </WikiSettingsWrapper>
);
}
