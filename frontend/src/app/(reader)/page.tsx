import Image from "next/image";
import Link from "next/link";
import { BookOpen, ChevronRight, AlertTriangle, Skull, Zap } from "lucide-react";
import { getLatestChapters, getNovelSettings, getHomepageSettings, formatChapterTitle, type Chapter, type NovelSettings, type HomepageSettings } from "@/lib/api";
import ContinueButton from "@/components/ContinueButton";

export const dynamic = "force-dynamic";
export const revalidate = 300; // ISR every 5 minutes

export default async function HomePage() {
    let latestChapters: Chapter[] = [];
    let novel: NovelSettings = {
        title: "Mạt Thế - Sinh Hoá Nguy Cơ",
        author: "Hà Phong",
        description: "Virus biến thể đã xóa sổ nền văn minh. Giữa thế giới tràn ngập zombie và những kẻ biến dị khát máu...",
        cover_url: "/hero-bg.png",
        status: "Đang cập nhật",
        genres: ["Mạt Thế", "Zombie"],
        total_chapters: 813,
        max_chapter: 813,
        total_views: 0,
        total_likes: 0
    };

    let homeSettings: HomepageSettings = {
        warning_title: 'CẢNH BÁO KHU VỰC CẤM',
        warning_subtitle: 'BIOSAFETY LEVEL 4 · RESTRICTED ACCESS',
        warning_headline: 'TRẬN ĐỊA SINH TỬ',
        warning_description: 'Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...',
        features_title: 'ĐIỂM NỔI BẬT',
        features_json: [
            { icon: "🧟", title: "Zombie & Dị Biến", desc: "Nhiều loại zombie với khả năng đặc biệt, từ đơn giản đến cực kỳ nguy hiểm" },
            { icon: "⚔️", title: "Chiến Thuật & Sinh Tồn", desc: "Xây dựng căn cứ, thu thập tài nguyên, chiến đấu có chiến lược" },
            { icon: "🔬", title: "Khoa Học Viễn Tưởng", desc: "Nghiên cứu virus, nâng cấp cơ thể, vũ khí sinh học trong thế giới tàn lụi" },
            { icon: "❤️", title: "Tình Cảm & Con Người", desc: "Tình đồng đội, tình yêu và những quyết định đau lòng giữa sự tàn bạo" }
        ]
    };

    try {
        const [chaptersData, settingsData, homeData] = await Promise.all([
            getLatestChapters(12),
            getNovelSettings(),
            getHomepageSettings()
        ]);
        latestChapters = chaptersData;
        novel = settingsData;
        homeSettings = homeData;
    } catch {
        // use defaults if API fails
    }

    return (
        <div className="min-h-screen bg-ash-dark">
            {/* === HERO SECTION === */}
            <section className="relative min-h-[90vh] flex items-end overflow-hidden">
                {/* Background image */}
                <div className="absolute inset-0">
                    <Image
                        src={novel.cover_url || "/hero-bg.png"}
                        alt={novel.title}
                        fill
                        priority
                        className="object-cover object-center"
                    />
                    {/* Multi-layer overlay */}
                    <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-ash-950/60 to-ash-950" />
                    <div className="absolute inset-0 bg-gradient-to-r from-ash-950/80 via-transparent to-ash-950/50" />
                    {/* Toxic green vignette bottom */}
                    <div className="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-ash-dark to-transparent" />
                </div>

                {/* Scanline animation overlay */}
                <div
                    className="absolute inset-0 pointer-events-none"
                    style={{
                        background:
                            "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(57,255,20,0.008) 3px, rgba(57,255,20,0.008) 4px)",
                    }}
                />

                {/* Content */}
                <div className="relative z-10 max-w-7xl mx-auto px-6 pb-20 w-full">
                    <div className="max-w-3xl">
                        {/* Status badge */}
                        <div className="flex flex-wrap items-center gap-2 mb-6">
                            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded border border-blood-red-DEFAULT/40 bg-blood-red-DEFAULT/10">
                                <Skull size={12} className="text-blood-red-bright" />
                                <span className="font-mono text-xs text-blood-red-bright tracking-widest uppercase">
                                    {novel.status} · {novel.max_chapter || 813} chương
                                </span>
                            </div>
                            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded border border-toxic-green-DEFAULT/40 bg-toxic-green-DEFAULT/5">
                                <span className="font-mono text-[10px] text-ash-400 tracking-widest uppercase">TÁC GIẢ:</span>
                                <span className="font-biohazard text-sm text-toxic-green-bright tracking-widest uppercase">
                                    {novel.author}
                                </span>
                            </div>
                        </div>

                        {/* Title */}
                        <h1 className="font-biohazard text-6xl sm:text-7xl md:text-8xl lg:text-9xl leading-none mb-2 animate-flicker">
                            <span className="text-toxic-glow block">{novel.title.split('-')[0].trim()}</span>
                        </h1>
                        <h2 className="font-biohazard text-2xl sm:text-3xl md:text-4xl text-ash-200 tracking-[0.15em] mb-8">
                            {novel.title.split('-')[1]?.trim() || ""}
                        </h2>

                        {/* Divider */}
                        <div className="flex items-center gap-4 mb-8">
                            <div className="flex-1 h-px bg-gradient-to-r from-toxic-green-DEFAULT/50 to-transparent" />
                            <span className="text-toxic-green-DEFAULT text-sm font-mono tracking-widest">
                                ☣
                            </span>
                            <div className="w-16 h-px bg-toxic-green-DEFAULT/30" />
                        </div>

                        {/* Description */}
                        <div
                            className="text-ash-100 text-base sm:text-lg leading-relaxed max-w-2xl mb-8 font-reading rich-text-home"
                            dangerouslySetInnerHTML={{ __html: novel.description }}
                        />

                        {/* CTA Buttons */}
                        <div className="flex flex-wrap gap-4">
                            <Link href="/chapters/1" className="btn-fixed-blood flex items-center gap-2 text-base py-3 px-6">
                                <BookOpen size={16} />
                                <span>ĐỌC TỪ ĐẦU</span>
                            </Link>
                            {/* Continue reading button (client-side only logic) */}
                            <ContinueButton fixedDark />
                            <Link href="/chapters" className="btn-fixed-dark flex items-center gap-2 text-base py-3 px-6">
                                <span>XEM MỤC LỤC</span>
                                <ChevronRight size={14} />
                            </Link>
                        </div>

                        {/* Quick stats */}
                        <div className="flex flex-wrap gap-6 mt-10">
                            {[
                                { label: "Chương", value: `${novel.total_chapters || 813}+` },
                                { label: "Tác giả", value: novel.author },
                                { label: "Thể loại", value: novel.genres.join(" · ") },
                                { label: "Tình trạng", value: novel.status },
                            ].map(({ label, value }) => (
                                <div key={label} className="text-center">
                                    <div className="font-biohazard text-xl text-toxic-green-DEFAULT">
                                        {value}
                                    </div>
                                    <div className="text-xs text-ash-500 font-mono tracking-widest uppercase">
                                        {label}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* === SYNOPSIS === */}
            <section className="py-20 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        {/* Left: Warning card */}
                        <div className="card-biohazard rounded-lg p-8 relative hazard-corner">
                            <div className="flex items-start gap-3 mb-6">
                                <AlertTriangle size={20} className="text-toxic-green-DEFAULT mt-1 shrink-0" />
                                <div>
                                    <div className="font-biohazard text-toxic-green-DEFAULT tracking-widest text-sm mb-1">
                                        {homeSettings.warning_title}
                                    </div>
                                    <div className="font-mono text-xs text-ash-500 tracking-wider">
                                        {homeSettings.warning_subtitle}
                                    </div>
                                </div>
                            </div>
                            <h2 className="font-biohazard text-4xl text-worn-white mb-6 tracking-wide leading-tight">
                                {homeSettings.warning_headline.split(' ').slice(0, -1).join(' ')}<br />
                                <span className="text-blood-glow">{homeSettings.warning_headline.split(' ').slice(-2).join(' ')}</span>
                            </h2>
                            <div
                                className="font-reading text-ash-100 text-sm leading-relaxed mb-6 whitespace-pre-line rich-text-home"
                                dangerouslySetInnerHTML={{ __html: homeSettings.warning_description }}
                            />
                        </div>

                        {/* Right: Feature list */}
                        <div className="space-y-4">
                            <h3 className="font-biohazard text-2xl text-ash-200 tracking-widest mb-6">
                                {homeSettings.features_title}
                            </h3>
                            {homeSettings.features_json.map((f, i) => (
                                <div
                                    key={i}
                                    className="flex gap-4 p-4 rounded border border-ash-800 hover:border-toxic-green-DEFAULT/30 transition-colors bg-ash-900/50 chapter-item"
                                >
                                    <span className="text-2xl shrink-0">{f.icon}</span>
                                    <div>
                                        <div className="font-biohazard text-ash-200 tracking-wider text-sm mb-1">
                                            {f.title}
                                        </div>
                                        <div className="text-ash-300 text-xs leading-relaxed">
                                            {f.desc}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* === LATEST CHAPTERS === */}
            <section className="py-16 px-6 bg-ash-900/30">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-between mb-10">
                        <div>
                            <div className="font-mono text-xs text-toxic-green-DEFAULT tracking-[0.3em] mb-2">
                                ☣ CẬP NHẬT MỚI NHẤT
                            </div>
                            <h2 className="font-biohazard text-3xl text-worn-white tracking-wide">
                                CHƯƠNG MỚI ĐÃ ĐĂNG
                            </h2>
                        </div>
                        <Link
                            href="/chapters"
                            className="flex items-center gap-2 text-sm font-mono text-ash-400 hover:text-toxic-green-DEFAULT transition-colors"
                        >
                            XEM TẤT CẢ
                            <ChevronRight size={14} />
                        </Link>
                    </div>

                    {latestChapters.length > 0 ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                            {latestChapters.map((chapter, i) => (
                                <Link
                                    key={chapter.id}
                                    href={`/chapters/${chapter.chapter_number}`}
                                    className="card-biohazard rounded p-4 group cursor-pointer relative hazard-corner chapter-item"
                                    style={{ animationDelay: `${i * 0.05}s` }}
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="flex-1 min-w-0">
                                            <div className="chapter-badge mb-1">
                                                CHƯƠNG {chapter.chapter_number}
                                            </div>
                                            <div className="font-biohazard text-ash-200 tracking-wide text-base leading-tight group-hover:text-toxic-green-DEFAULT transition-colors line-clamp-2">
                                                {chapter.title}
                                            </div>
                                        </div>
                                        <ChevronRight
                                            size={14}
                                            className="text-ash-600 group-hover:text-toxic-green-DEFAULT shrink-0 mt-1 transition-colors"
                                        />
                                    </div>
                                    <div className="mt-3 text-ash-600 text-[10px] font-mono">
                                        {new Date(chapter.created_at).toLocaleDateString("vi-VN")}
                                    </div>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        /* Skeleton / placeholder if API not available */
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                            {Array.from({ length: 12 }).map((_, i) => (
                                <div
                                    key={i}
                                    className="card-biohazard rounded p-4 animate-pulse"
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="flex-1">
                                            <div className="h-3 bg-ash-800 rounded w-20 mb-2" />
                                            <div className="h-4 bg-ash-800 rounded w-full mb-1" />
                                            <div className="h-4 bg-ash-800 rounded w-3/4" />
                                        </div>
                                    </div>
                                    <div className="mt-3 h-3 bg-ash-800 rounded w-24" />
                                </div>
                            ))}
                        </div>
                    )}

                    {/* CTA */}
                    <div className="text-center mt-12 flex flex-col items-center gap-4">
                        <ContinueButton fixedDark />
                        <Link href="/chapters/1" className="btn-fixed-blood inline-flex items-center gap-2 text-base py-3 px-8">
                            <Zap size={16} />
                            <span>BẮT ĐẦU ĐỌC NGAY</span>
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}
