import { Suspense } from "react";
import { BookOpen, Filter } from "lucide-react";
import Link from "next/link";
import { getWikiEntries, WikiEntry, WIKI_CATEGORIES } from "@/lib/api";

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
            className="group bg-[#111] border border-gray-800 rounded-xl overflow-hidden hover:border-green-900 transition-all duration-300 hover:shadow-[0_0_20px_rgba(0,255,159,0.05)]">
            {entry.image_url && (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={entry.image_url} alt={entry.title}
                    className="w-full h-40 object-cover group-hover:scale-105 transition-transform duration-500" />
            )}
            {!entry.image_url && (
                <div className="w-full h-40 bg-[#0d0d0d] flex items-center justify-center text-4xl border-b border-gray-800">
                    {CATEGORY_ICONS[entry.category] || "📖"}
                </div>
            )}
            <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-mono text-green-600 bg-green-950/40 border border-green-900 px-2 py-0.5 rounded">
                        {CATEGORY_ICONS[entry.category]} {entry.category}
                    </span>
                </div>
                <h3 className="font-mono text-gray-200 text-sm font-semibold group-hover:text-green-400 transition-colors">{entry.title}</h3>
                {entry.summary && <p className="text-xs text-gray-600 font-reading mt-2 leading-relaxed line-clamp-2">{entry.summary}</p>}
                {entry.tags && entry.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                        {entry.tags.slice(0, 3).map(tag => (
                            <span key={tag} className="text-[10px] font-mono text-gray-700 bg-gray-900 px-1.5 py-0.5 rounded">{tag}</span>
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
            <div className="col-span-3 text-center py-20 border border-dashed border-gray-800 rounded-lg">
                <p className="text-gray-600 font-mono text-sm">Chưa có dữ liệu trong mục này.</p>
                <p className="text-gray-800 font-mono text-xs mt-2">Các thông tin đang được biên soạn...</p>
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
        <main className="max-w-7xl mx-auto px-6 py-10">
            {/* Header */}
            <div className="text-center mb-10">
                <div className="inline-flex items-center gap-2 mb-4 px-4 py-1.5 border border-green-900/50 bg-green-950/20 rounded-full">
                    <BookOpen size={14} className="text-green-500" />
                    <span className="text-xs font-mono text-green-600 tracking-widest">CLASSIFIED DATABASE</span>
                </div>
                <h1 className="font-biohazard text-4xl text-worn-white tracking-wide mb-2">CẨM NANG MẠT THẾ</h1>
                <p className="text-ash-400 text-sm font-reading">Dữ liệu tình báo về mọi thực thể trong thế giới Mạt Thế ☣️</p>
            </div>

            <div className="flex gap-8">
                {/* Sidebar */}
                <aside className="w-48 flex-shrink-0">
                    <div className="sticky top-24 bg-[#0d0d0d] border border-gray-800 rounded-xl p-4">
                        <div className="flex items-center gap-2 mb-4 text-xs font-mono text-gray-600">
                            <Filter size={12} /> PHÂN LOẠI
                        </div>
                        <ul className="space-y-1">
                            <li>
                                <Link href="/wiki" className={`flex items-center gap-2 px-3 py-2 rounded text-xs font-mono transition-colors
                                    ${!activeCategory ? "bg-green-950/40 text-green-400 border border-green-900" : "text-gray-500 hover:text-gray-300"}`}>
                                    📋 Tất cả
                                </Link>
                            </li>
                            {WIKI_CATEGORIES.map(cat => (
                                <li key={cat}>
                                    <Link href={`/wiki?cat=${encodeURIComponent(cat)}`}
                                        className={`flex items-center gap-2 px-3 py-2 rounded text-xs font-mono transition-colors
                                            ${activeCategory === cat ? "bg-green-950/40 text-green-400 border border-green-900" : "text-gray-500 hover:text-gray-300"}`}>
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
                            <span className="text-xs font-mono text-gray-600">Đang lọc:</span>
                            <span className="text-xs font-mono text-green-500 bg-green-950/30 border border-green-900 px-2 py-0.5 rounded">
                                {CATEGORY_ICONS[activeCategory]} {activeCategory}
                            </span>
                            <Link href="/wiki" className="text-xs font-mono text-gray-700 hover:text-gray-500 transition-colors ml-2">✕ Bỏ lọc</Link>
                        </div>
                    )}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        <Suspense fallback={
                            <>
                                {[...Array(6)].map((_, i) => (
                                    <div key={i} className="h-64 bg-[#111] border border-gray-800 rounded-xl animate-pulse" />
                                ))}
                            </>
                        }>
                            <WikiGrid category={activeCategory} />
                        </Suspense>
                    </div>
                </div>
            </div>
        </main>
    );
}
