import Image from "next/image";
import Link from "next/link";
import { AlertTriangle, BookOpen, ChevronRight, Skull, Zap } from "lucide-react";

import ContinueButton from "@/components/ContinueButton";
import HeroBackground from "@/components/HeroBackground";
import {
    getHomepageSettings,
    getLatestChapters,
    getNovelSettings,
    type Chapter,
    type HomepageSettings,
    type NovelSettings,
} from "@/lib/api";
import { LOCALE_LANG, withLocalePath } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/dictionaries";
import { getCurrentLocale } from "@/lib/i18n/server";

export const dynamic = "force-dynamic";
export const revalidate = 300;

function splitNovelTitle(title: string) {
    const parts = title.split("-").map((item) => item.trim()).filter(Boolean);
    if (parts.length < 2) {
        return {
            primary: title,
            secondary: "",
        };
    }

    return {
        primary: parts[0],
        secondary: parts.slice(1).join(" - "),
    };
}

export default async function HomePage() {
    const locale = await getCurrentLocale();
    const dictionary = getDictionary(locale);

    let latestChapters: Chapter[] = [];
    let novel: NovelSettings = {
        title: "Mạt Thế - Sinh Hóa Nguy Cơ",
        author: "Hàn Phong",
        description: "Virus biến thể đã xóa sổ nền văn minh. Giữa thế giới tràn ngập zombie và dị biến, con người chỉ còn lại bản năng sinh tồn.",
        cover_url: "/hero-bg.png",
        status: "Đang cập nhật",
        genres: ["Mạt Thế", "Zombie"],
        total_chapters: 0,
        max_chapter: 0,
        total_views: 0,
        total_likes: 0,
        ai_model_name: "gemini-3.1-flash-lite-preview",
    };

    let homeSettings: HomepageSettings = {
        warning_title: "CẢNH BÁO KHU VỰC CẤM",
        warning_subtitle: "BIOSAFETY LEVEL 4 • RESTRICTED ACCESS",
        warning_headline: "TRẬN ĐỊA SINH TỬ",
        warning_description: "Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...",
        features_title: "ĐIỂM NỔI BẬT",
        features_json: [
            { icon: "☣", title: "Zombie & Dị Biến", desc: "Nhiều chủng zombie với cơ chế săn mồi và năng lực riêng." },
            { icon: "⚔", title: "Chiến Thuật Sinh Tồn", desc: "Thu thập tài nguyên, nâng cấp căn cứ và đối đầu theo nhịp truyện." },
            { icon: "🧪", title: "Khoa Học Hậu Tận Thế", desc: "Virus, cải tạo cơ thể và vũ khí sinh học vận hành xuyên suốt truyện." },
            { icon: "❤", title: "Quan Hệ Con Người", desc: "Sinh tồn không chỉ là chiến đấu, mà còn là lựa chọn giữa tin tưởng và phản bội." },
        ],
    };

    try {
        const [chaptersData, settingsData, homeData] = await Promise.all([
            getLatestChapters(12, locale),
            getNovelSettings(locale),
            getHomepageSettings(locale),
        ]);
        latestChapters = chaptersData;
        novel = settingsData;
        homeSettings = homeData;
    } catch {
        // Fall back to local defaults when APIs are unavailable.
    }

    const localizedChapterListPath = withLocalePath(locale, "/chapters");
    const localizedFirstChapterPath = withLocalePath(locale, "/chapters/1");
    const { primary, secondary } = splitNovelTitle(novel.title);

    return (
        <div className="min-h-screen bg-ash-dark">
            <section className="relative flex min-h-[90vh] items-end overflow-hidden">
                <HeroBackground 
                    images={[
                        "/themes/theme-1.png", 
                        "/themes/theme-2.png", 
                        "/themes/theme-3.png", 
                        "/themes/theme-4.png", 
                        "/themes/theme-5.png"
                    ]}
                    fallbackImage={novel.cover_url || "/hero-bg.png"}
                    title={novel.title}
                />

                <div
                    className="pointer-events-none absolute inset-0"
                    style={{
                        background:
                            "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(57,255,20,0.008) 3px, rgba(57,255,20,0.008) 4px)",
                    }}
                />

                <div className="relative z-10 mx-auto w-full max-w-7xl px-6 pb-20">
                    <div className="max-w-3xl">
                        <div className="mb-6 flex flex-wrap items-center gap-2">
                            <div className="inline-flex items-center gap-2 rounded border border-blood-red-DEFAULT/40 bg-blood-red-DEFAULT/10 px-3 py-1.5">
                                <Skull size={12} className="text-blood-red-bright" />
                                <span className="font-mono text-xs uppercase tracking-widest text-blood-red-bright">
                                    {novel.status} • {novel.max_chapter || "?"} {dictionary.home.chapters}
                                </span>
                            </div>
                            <div className="inline-flex items-center gap-2 rounded border border-toxic-green-DEFAULT/40 bg-toxic-green-DEFAULT/5 px-3 py-1.5">
                                <span className="font-mono text-[10px] uppercase tracking-widest text-ash-400">
                                    {dictionary.home.author}:
                                </span>
                                <span className="font-biohazard text-sm uppercase tracking-widest text-toxic-green-bright">
                                    {novel.author}
                                </span>
                            </div>
                        </div>

                        <h1 className="mb-2 block font-biohazard text-6xl leading-none text-toxic-glow animate-flicker sm:text-7xl md:text-8xl lg:text-9xl">
                            {primary}
                        </h1>
                        {secondary ? (
                            <h2 className="mb-8 font-biohazard text-2xl tracking-[0.15em] text-ash-200 sm:text-3xl md:text-4xl">
                                {secondary}
                            </h2>
                        ) : null}

                        <div className="mb-8 flex items-center gap-4">
                            <div className="h-px flex-1 bg-gradient-to-r from-toxic-green-DEFAULT/50 to-transparent" />
                            <span className="font-mono text-sm tracking-widest text-toxic-green-DEFAULT">BIO-SCAN</span>
                            <div className="h-px w-16 bg-toxic-green-DEFAULT/30" />
                        </div>

                        <div
                            className="rich-text-home mb-8 max-w-2xl font-reading text-base leading-relaxed text-ash-100 sm:text-lg"
                            dangerouslySetInnerHTML={{ __html: novel.description }}
                        />

                        {homeSettings.is_fallback && locale !== "vi" ? (
                            <div className="mb-6 inline-flex items-center rounded border border-toxic-green-DEFAULT/20 bg-toxic-green-DEFAULT/5 px-3 py-1 font-mono text-[11px] tracking-widest text-toxic-green-DEFAULT">
                                {dictionary.common.fallbackVietnamese}
                            </div>
                        ) : null}

                        <div className="flex flex-wrap gap-4">
                            <Link href={localizedFirstChapterPath} className="btn-fixed-blood flex items-center gap-2 px-6 py-3 text-base">
                                <BookOpen size={16} />
                                <span>{dictionary.home.readFirst}</span>
                            </Link>
                            <ContinueButton fixedDark />
                            <Link href={localizedChapterListPath} className="btn-fixed-dark flex items-center gap-2 px-6 py-3 text-base">
                                <span>{dictionary.home.viewContents}</span>
                                <ChevronRight size={14} />
                            </Link>
                        </div>

                        <div className="mt-10 flex flex-wrap gap-6">
                            {[
                                { label: dictionary.home.chapters, value: `${novel.max_chapter || "?"}` },
                                { label: dictionary.home.author, value: novel.author },
                                { label: dictionary.home.genres, value: novel.genres.join(" • ") },
                                { label: dictionary.home.status, value: novel.status },
                            ].map(({ label, value }) => (
                                <div key={label} className="text-center">
                                    <div className="font-biohazard text-xl text-toxic-green-DEFAULT">{value}</div>
                                    <div className="font-mono text-xs uppercase tracking-widest text-ash-500">{label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            <section className="px-6 py-20">
                <div className="mx-auto max-w-7xl">
                    <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
                        <div className="card-biohazard hazard-corner relative rounded-lg p-8">
                            <div className="mb-6 flex items-start gap-3">
                                <AlertTriangle size={20} className="mt-1 shrink-0 text-toxic-green-DEFAULT" />
                                <div>
                                    <div className="mb-1 font-biohazard text-sm tracking-widest text-toxic-green-DEFAULT">
                                        {homeSettings.warning_title}
                                    </div>
                                    <div className="font-mono text-xs tracking-wider text-ash-500">
                                        {homeSettings.warning_subtitle}
                                    </div>
                                </div>
                            </div>
                            <h2 className="mb-6 font-biohazard text-4xl leading-tight tracking-wide text-worn-white">
                                {homeSettings.warning_headline}
                            </h2>
                            <div
                                className="rich-text-home mb-6 whitespace-pre-line font-reading text-sm leading-relaxed text-ash-100"
                                dangerouslySetInnerHTML={{ __html: homeSettings.warning_description }}
                            />
                        </div>

                        <div className="space-y-4">
                            <h3 className="mb-6 font-biohazard text-2xl tracking-widest text-ash-200">
                                {homeSettings.features_title}
                            </h3>
                            {homeSettings.features_json.map((feature, index) => (
                                <div
                                    key={`${feature.title}-${index}`}
                                    className="chapter-item flex gap-4 rounded border border-ash-800 bg-ash-900/50 p-4 transition-colors hover:border-toxic-green-DEFAULT/30"
                                >
                                    <span className="shrink-0 text-2xl">{feature.icon}</span>
                                    <div>
                                        <div className="mb-1 font-biohazard text-sm tracking-wider text-ash-200">
                                            {feature.title}
                                        </div>
                                        <div className="text-xs leading-relaxed text-ash-300">{feature.desc}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            <section className="bg-ash-900/30 px-6 py-16">
                <div className="mx-auto max-w-7xl">
                    <div className="mb-10 flex items-center justify-between">
                        <div>
                            <div className="mb-2 font-mono text-xs tracking-[0.3em] text-toxic-green-DEFAULT">
                                {dictionary.home.latestUpdated}
                            </div>
                            <h2 className="font-biohazard text-3xl tracking-wide text-worn-white">
                                {dictionary.home.latest}
                            </h2>
                        </div>
                        <Link
                            href={localizedChapterListPath}
                            className="flex items-center gap-2 font-mono text-sm text-ash-400 transition-colors hover:text-toxic-green-DEFAULT"
                        >
                            {dictionary.home.seeAll}
                            <ChevronRight size={14} />
                        </Link>
                    </div>

                    {latestChapters.length > 0 ? (
                        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                            {latestChapters.map((chapter, index) => (
                                <Link
                                    key={chapter.id}
                                    href={withLocalePath(locale, `/chapters/${chapter.chapter_number}`)}
                                    className="card-biohazard hazard-corner chapter-item group relative cursor-pointer rounded p-4"
                                    style={{ animationDelay: `${index * 0.05}s` }}
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="min-w-0 flex-1">
                                            <div className="chapter-badge mb-1">
                                                {dictionary.reader.chapter} {chapter.chapter_number}
                                            </div>
                                            <div className="line-clamp-2 text-base leading-tight tracking-wide text-ash-200 transition-colors group-hover:text-toxic-green-DEFAULT font-biohazard">
                                                {chapter.title}
                                            </div>
                                        </div>
                                        <ChevronRight
                                            size={14}
                                            className="mt-1 shrink-0 text-ash-600 transition-colors group-hover:text-toxic-green-DEFAULT"
                                        />
                                    </div>
                                    <div className="mt-3 font-mono text-[10px] text-ash-600">
                                        {new Date(chapter.created_at).toLocaleDateString(LOCALE_LANG[locale])}
                                    </div>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                            {Array.from({ length: 12 }).map((_, index) => (
                                <div key={index} className="card-biohazard rounded p-4 animate-pulse">
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="flex-1">
                                            <div className="mb-2 h-3 w-20 rounded bg-ash-800" />
                                            <div className="mb-1 h-4 w-full rounded bg-ash-800" />
                                            <div className="h-4 w-3/4 rounded bg-ash-800" />
                                        </div>
                                    </div>
                                    <div className="mt-3 h-3 w-24 rounded bg-ash-800" />
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="mt-12 flex flex-col items-center gap-4 text-center">
                        <ContinueButton fixedDark />
                        <Link href={localizedFirstChapterPath} className="btn-fixed-blood inline-flex items-center gap-2 px-8 py-3 text-base">
                            <Zap size={16} />
                            <span>{dictionary.home.startNow}</span>
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}
