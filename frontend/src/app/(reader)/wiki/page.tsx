import { Suspense } from "react";
import { BookOpen, Filter, Star } from "lucide-react";
import Link from "next/link";
import { getWikiEntries, WikiEntry, WIKI_CATEGORIES } from "@/lib/api";
import WikiSettingsWrapper from "@/components/WikiSettingsWrapper";

export const metadata = {
    title: "Cẩm Nang Mạt Thế | Bách Khoa Toàn Thư",
    description: "Tra cứu Nhân vật, Sinh vật, Thế lực và Vật phẩm trong thế giới Mạt Thế☣️",
};

const CATEGORY_ICONS: Record<string, string> = {
    "Nhân vật": "👤", "Sinh vật": "🧟", "Thế lực": "⚔️", "Vật phẩm": "🗡️", "Địa điểm": "📍"
};

function WikiCard({ entry }: { entry: WikiEntry }) {
    return (
        <Link href={`/wiki/${entry.slug}`}
            className={`group bg-reader-bg border rounded-xl overflow-hidden transition-all duration-300 hover:shadow-[0_0_20px_rgba(0,255,159,0.05)]
                ${entry.is_main_character ? "border-yellow-900/50 shadow-[0_0_15px_rgba(234,179,8,0.03)] hover:border-yellow-600" : "border-reader-border hover:border-reader-accent"}`}>
            {entry.image_url && (
                <div className="relative overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={entry.image_url} alt={entry.title}
                        className="w-full h-40 object-cover group-hover:scale-105 transition-transform duration-500" />
                    {entry.is_main_character && (
                        <div className="absolute top-2 right-2 bg-yellow-500 text-black px-1.5 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 shadow-lg z-10">
                            <Star size={10} fill="currentColor" /> CHÍNH
                        </div>
                    )}
                </div>
            )}
            {!entry.image_url && (
                <div className={`w-full h-40 flex items-center justify-center text-4xl border-b relative
                    ${entry.is_main_character ? "bg-yellow-950/20 border-yellow-900/40" : "bg-reader-bg border-reader-border"}`}>
                    {CATEGORY_ICONS[entry.category] || "📖"}
                    {entry.is_main_character && (
                        <div className="absolute top-2 right-2 bg-yellow-500 text-black px-1.5 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 shadow-lg z-10">
                            <Star size={10} fill="currentColor" /> CHÍNH
                        </div>
                    )}
                </div>
            )}
            <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs font-mono px-2 py-0.5 rounded border
                        ${entry.is_main_character ? "text-yellow-500 bg-yellow-950/40 border-yellow-900/60" : "text-green-600 bg-green-950/40 border-green-900"}`}>
                        {CATEGORY_ICONS[entry.category]} {entry.category}
                    </span>
                </div>
                <h3 className={`font-mono text-sm font-semibold transition-colors
                    ${entry.is_main_character ? "text-yellow-500 group-hover:text-yellow-400" : "text-reader-text group-hover:text-reader-accent"}`}>
                    {entry.title}
                </h3>
                {entry.summary && <p className="text-xs text-reader-muted font-reading mt-2 leading-relaxed line-clamp-2">{entry.summary}</p>}
                {entry.tags && entry.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                        {entry.tags.slice(0, 3).map(tag => (
                            <span key={tag} className="text-[10px] font-mono text-reader-muted bg-reader-bg/40 border border-reader-border px-1.5 py-0.5 rounded">{tag}</span>
                        ))}
                    </div>
                )}
            </div>
        </Link>
    );
}

async function WikiGrid({ category }: { category?: string }) {
    let entries: WikiEntry[] = [];
    try {
        entries = await getWikiEntries(category);
    } catch {
        return <p className="col-span-3 text-center text-gray-700 font-mono py-20">Không kết nối được với server. Vui lòng thử lại.</p>;
    }

    if (entries.length === 0) {
        return (
            <div className="col-span-3 text-center py-20 border border-dashed border-reader-border rounded-lg">
                <p className="text-reader-muted font-mono text-sm">Chưa có dữ liệu trong mục này.</p>
                <p className="text-reader-muted/60 font-mono text-xs mt-2">Các thông tin đang được biên soạn...</p>
            </div>
        );
    }

    return (
        <>
            {entries.map(entry => <WikiCard key={entry.id} entry={entry} />)}
        </>
    );
}

export default async function WikiPage({ searchParams }: { searchParams: Promise<{ cat?: string }> }) {
    const { cat } = await searchParams;
    const activeCategory = WIKI_CATEGORIES.includes(cat as typeof WIKI_CATEGORIES[number]) ? cat : undefined;

    return (
        <WikiSettingsWrapper>
            <main className="max-w-7xl mx-auto px-6 py-10">
                {/* Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 mb-4 px-4 py-1.5 border border-reader-accent/50 bg-reader-accent/10 rounded-full">
                        <BookOpen size={14} className="text-reader-accent" />
                        <span className="text-xs font-mono text-reader-accent tracking-widest uppercase">CLASSIFIED DATABASE</span>
                    </div>
                    <h1 className="font-biohazard text-4xl text-reader-text tracking-wide mb-2 uppercase">CẨM NANG MẠT THẾ</h1>
                    <p className="text-reader-muted text-sm font-reading italic">Dữ liệu tình báo về mọi thực thể trong thế giới Mạt Thế ☣️</p>
                </div>

                <div className="flex gap-8">
                    {/* Sidebar */}
                    <aside className="w-48 flex-shrink-0">
                        <div className="sticky top-24 bg-reader-bg/40 border border-reader-border rounded-xl p-4 backdrop-blur-sm shadow-xl">
                            <div className="flex items-center gap-2 mb-4 text-xs font-mono text-reader-muted">
                                <Filter size={12} /> PHÂN LOẠI
                            </div>
                            <ul className="space-y-1">
                                <li>
                                    <Link href="/wiki" className={`flex items-center gap-2 px-3 py-2 rounded text-xs font-mono transition-colors
                                    ${!activeCategory ? "bg-reader-accent/20 text-reader-accent border border-reader-accent/40 shadow-[0_0_10px_rgba(57,255,20,0.1)]" : "text-reader-muted hover:text-reader-text"}`}>
                                        📋 Tất cả
                                    </Link>
                                </li>
                                {WIKI_CATEGORIES.map(cat => (
                                    <li key={cat}>
                                        <Link href={`/wiki?cat=${encodeURIComponent(cat)}`}
                                            className={`flex items-center gap-2 px-3 py-2 rounded text-xs font-mono transition-colors
                                            ${activeCategory === cat ? "bg-reader-accent/20 text-reader-accent border border-reader-accent/40 shadow-[0_0_10px_rgba(57,255,20,0.1)]" : "text-reader-muted hover:text-reader-text"}`}>
                                            {CATEGORY_ICONS[cat]} {cat}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </aside>

                    {/* Main grid */}
                    <div className="flex-1">
                        {activeCategory && (
                            <div className="mb-6 flex items-center gap-2">
                                <span className="text-xs font-mono text-reader-muted">Đang lọc:</span>
                                <span className="text-xs font-mono text-reader-accent bg-reader-accent/10 border border-reader-accent/30 px-2 py-0.5 rounded">
                                    {CATEGORY_ICONS[activeCategory]} {activeCategory}
                                </span>
                                <Link href="/wiki" className="text-xs font-mono text-reader-muted hover:text-reader-text transition-colors ml-2">✕ Bỏ lọc</Link>
                            </div>
                        )}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            <Suspense fallback={
                                <>
                                    {[...Array(6)].map((_, i) => (
                                        <div key={i} className="h-64 bg-reader-bg border border-reader-border rounded-xl animate-pulse" />
                                    ))}
                                </>
                            }>
                                <WikiGrid category={activeCategory} />
                            </Suspense>
                        </div>
                    </div>
                </div>
            </main>
        </WikiSettingsWrapper>
    );
}
