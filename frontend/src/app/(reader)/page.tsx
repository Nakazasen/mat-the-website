import Link from "next/link";
import { AlertTriangle, BookOpen, ChevronRight, Shield, Skull, Zap } from "lucide-react";

import ContinueButton from "@/components/ContinueButton";
import HeroBackground from "@/components/HeroBackground";
import HomepageHeroVideo from "@/components/HomepageHeroVideo";
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
    const parts = title
        .split("-")
        .map((item) => item.trim())
        .filter(Boolean);

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
        author: "Hàn Nhược Tuyết",
        description:
            "Một thế giới sụp đổ bởi virus, nơi con người phải vùng vẫy để giữ lại từng tia trật tự cuối cùng giữa zombie và dị biến.",
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
        warning_title: "KHU VỰC CẤM",
        warning_subtitle: "BIOSAFETY LEVEL 4 / RESTRICTED ACCESS",
        warning_headline: "TRẬT TỰ CŨ ĐÃ SỤP ĐỔ",
        warning_description:
            "Thế giới cũ đã vỡ vụn. Những gì còn lại là sinh tồn, tiến hóa và những cuộc va chạm không thể tránh khỏi.",
        features_title: "ĐIỂM NỔI BẬT",
        features_json: [
            { icon: "☣", title: "Zombie & Dị biến", desc: "Sinh vật nguy hiểm, hành vi khó đoán và áp lực luôn tăng dần theo từng chặng truyện." },
            { icon: "⚔", title: "Sinh tồn chiến thuật", desc: "Mỗi quyết định, mỗi món tài nguyên và mỗi lần đối đầu đều có giá của nó." },
            { icon: "🧬", title: "Hệ thống tiến hóa", desc: "Nhân vật mạnh lên từng bước, nhưng thế giới cũng trở nên tàn nhẫn hơn theo cùng nhịp đó." },
            { icon: "☠", title: "Quan hệ con người", desc: "Niềm tin, phản bội và áp lực đạo đức là một phần cốt lõi của bầu không khí mạt thế." },
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
        // Keep local fallback defaults when APIs are unavailable.
    }

    const localizedChapterListPath = withLocalePath(locale, "/chapters");
    const localizedFirstChapterPath = withLocalePath(locale, "/chapters/1");
    const { primary, secondary } = splitNovelTitle(novel.title);

    const heroStats = [
        { label: dictionary.home.chapters, value: `${novel.max_chapter || "?"}` },
        { label: dictionary.home.author, value: novel.author },
        { label: dictionary.home.genres, value: novel.genres.join(" • ") },
        { label: dictionary.home.status, value: novel.status },
    ];

    return (
        <div className="min-h-screen bg-ash-dark text-worn-white">
            <section className="relative overflow-hidden border-b border-toxic-green-DEFAULT/10">
                <HeroBackground
                    images={[
                        "/themes/theme-1.png",
                        "/themes/theme-2.png",
                        "/themes/theme-3.png",
                        "/themes/theme-4.png",
                        "/themes/theme-5.png",
                    ]}
                    fallbackImage={novel.cover_url || "/hero-bg.png"}
                    title={novel.title}
                />

                <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(57,255,20,0.08),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(139,0,0,0.18),transparent_28%),linear-gradient(180deg,rgba(0,0,0,0.38),rgba(0,0,0,0.72))]" />
                <div
                    className="pointer-events-none absolute inset-0"
                    style={{
                        background:
                            "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(57,255,20,0.008) 3px, rgba(57,255,20,0.008) 4px)",
                    }}
                />

                <div className="relative z-10 mx-auto max-w-7xl px-6 py-14 sm:py-18 lg:py-24">
                    <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,0.95fr)_minmax(460px,1.05fr)]">
                        <div className="max-w-3xl">
                            <div className="mb-5 flex flex-wrap gap-3">
                                <div className="inline-flex items-center gap-2 rounded-full border border-blood-red-DEFAULT/35 bg-blood-red-DEFAULT/10 px-4 py-2">
                                    <Skull size={12} className="text-blood-red-bright" />
                                    <span className="font-mono text-[11px] uppercase tracking-[0.28em] text-blood-red-bright">
                                        {novel.status} / {novel.max_chapter || "?"} {dictionary.home.chapters}
                                    </span>
                                </div>
                                <div className="inline-flex items-center gap-2 rounded-full border border-toxic-green-DEFAULT/25 bg-black/35 px-4 py-2">
                                    <span className="font-mono text-[11px] uppercase tracking-[0.28em] text-ash-400">{dictionary.home.author}</span>
                                    <span className="font-biohazard text-sm uppercase tracking-[0.18em] text-toxic-green-bright">{novel.author}</span>
                                </div>
                            </div>

                            <h1 className="font-biohazard text-6xl leading-none text-toxic-glow animate-flicker sm:text-7xl md:text-8xl lg:text-[6.5rem]">
                                {primary}
                            </h1>
                            {secondary ? (
                                <h2 className="mt-3 font-biohazard text-2xl tracking-[0.15em] text-ash-200 sm:text-3xl md:text-4xl">{secondary}</h2>
                            ) : null}

                            <div className="mt-8 flex items-center gap-4">
                                <div className="h-px flex-1 bg-gradient-to-r from-toxic-green-DEFAULT/50 to-transparent" />
                                <span className="font-mono text-sm uppercase tracking-[0.32em] text-toxic-green-DEFAULT">Bio-Scan</span>
                                <div className="h-px w-16 bg-toxic-green-DEFAULT/30" />
                            </div>

                            <div
                                className="rich-text-home mt-8 max-w-2xl font-reading text-base leading-8 text-ash-100 sm:text-lg"
                                dangerouslySetInnerHTML={{ __html: novel.description }}
                            />

                            {homeSettings.is_fallback && locale !== "vi" ? (
                                <div className="mt-5 inline-flex items-center rounded-full border border-toxic-green-DEFAULT/20 bg-toxic-green-DEFAULT/5 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-toxic-green-DEFAULT">
                                    {dictionary.common.fallbackVietnamese}
                                </div>
                            ) : null}

                            <div className="mt-8 flex flex-wrap gap-4">
                                <Link href={localizedFirstChapterPath} className="btn-fixed-blood inline-flex items-center gap-2 px-6 py-3 text-base">
                                    <BookOpen size={16} />
                                    <span>{dictionary.home.readFirst}</span>
                                </Link>
                                <ContinueButton fixedDark />
                                <Link href={localizedChapterListPath} className="btn-fixed-dark inline-flex items-center gap-2 px-6 py-3 text-base">
                                    <span>{dictionary.home.viewContents}</span>
                                    <ChevronRight size={14} />
                                </Link>
                            </div>

                            <div className="mt-10 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                                {heroStats.map(({ label, value }) => (
                                    <div key={label} className="rounded-2xl border border-white/10 bg-black/30 p-4 backdrop-blur">
                                        <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ash-500">{label}</div>
                                        <div className="mt-2 line-clamp-2 font-biohazard text-2xl leading-tight text-toxic-green-DEFAULT">{value}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="lg:pl-6">
                            <HomepageHeroVideo
                                title={novel.author}
                                src="/media/han-phong-mystical-explosion.mp4"
                                poster="/media/han-phong-mystical-explosion-poster.jpg"
                            />
                        </div>
                    </div>
                </div>
            </section>

            <section className="px-6 py-14 sm:py-16 lg:py-20">
                <div className="mx-auto max-w-7xl">
                    <div className="grid gap-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
                        <div className="rounded-[28px] border border-white/10 bg-black/30 p-7 backdrop-blur">
                            <div className="mb-5 flex items-start gap-3">
                                <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-toxic-green-DEFAULT/20 bg-toxic-green-DEFAULT/10">
                                    <AlertTriangle size={18} className="text-toxic-green-DEFAULT" />
                                </div>
                                <div>
                                    <div className="font-mono text-[11px] uppercase tracking-[0.32em] text-toxic-green-DEFAULT">{homeSettings.warning_title}</div>
                                    <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.26em] text-ash-500">
                                        {homeSettings.warning_subtitle}
                                    </div>
                                </div>
                            </div>

                            <h2 className="font-biohazard text-3xl tracking-[0.06em] text-worn-white sm:text-4xl">{homeSettings.warning_headline}</h2>
                            <div
                                className="rich-text-home mt-5 font-reading text-sm leading-7 text-ash-200 sm:text-base"
                                dangerouslySetInnerHTML={{ __html: homeSettings.warning_description }}
                            />
                        </div>

                        <div>
                            <div className="mb-5 flex items-center gap-3">
                                <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-toxic-green-DEFAULT/20 bg-toxic-green-DEFAULT/10">
                                    <Shield size={18} className="text-toxic-green-DEFAULT" />
                                </div>
                                <div>
                                    <div className="font-mono text-[11px] uppercase tracking-[0.32em] text-toxic-green-DEFAULT">
                                        {homeSettings.features_title}
                                    </div>
                                    <div className="mt-1 font-reading text-sm text-ash-400">Giữ nguyên nội dung thật, chỉ đổi bố cục cho sạch và dễ nhìn hơn.</div>
                                </div>
                            </div>

                            <div className="grid gap-4 md:grid-cols-2">
                                {homeSettings.features_json.map((feature, index) => (
                                    <div
                                        key={`${feature.title}-${index}`}
                                        className="rounded-[24px] border border-white/10 bg-black/25 p-5 backdrop-blur transition hover:border-toxic-green-DEFAULT/30 hover:bg-black/35"
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-toxic-green-DEFAULT/15 bg-toxic-green-DEFAULT/8 text-xl">
                                                {feature.icon}
                                            </div>
                                            <div>
                                                <div className="font-biohazard text-xl tracking-[0.06em] text-worn-white">{feature.title}</div>
                                                <div className="mt-2 text-sm leading-7 text-ash-300">{feature.desc}</div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section className="border-y border-white/6 bg-black/20 px-6 py-14 sm:py-16">
                <div className="mx-auto max-w-7xl">
                    <div className="mb-8 flex items-end justify-between gap-4">
                        <div>
                            <div className="font-mono text-[11px] uppercase tracking-[0.34em] text-toxic-green-DEFAULT">{dictionary.home.latestUpdated}</div>
                            <h2 className="mt-3 font-biohazard text-3xl tracking-[0.06em] text-worn-white sm:text-4xl">{dictionary.home.latest}</h2>
                        </div>
                        <Link
                            href={localizedChapterListPath}
                            className="font-mono text-sm uppercase tracking-[0.22em] text-ash-400 transition hover:text-toxic-green-DEFAULT"
                        >
                            {dictionary.home.seeAll}
                        </Link>
                    </div>

                    {latestChapters.length > 0 ? (
                        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                            {latestChapters.map((chapter, index) => (
                                <Link
                                    key={chapter.id}
                                    href={withLocalePath(locale, `/chapters/${chapter.chapter_number}`)}
                                    className="rounded-[24px] border border-white/10 bg-black/30 p-5 backdrop-blur transition hover:border-toxic-green-DEFAULT/30 hover:bg-black/40"
                                    style={{ animationDelay: `${index * 0.05}s` }}
                                >
                                    <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-toxic-green-DEFAULT">
                                        {dictionary.reader.chapter} {chapter.chapter_number}
                                    </div>
                                    <div className="mt-3 line-clamp-2 font-biohazard text-2xl leading-tight tracking-[0.05em] text-worn-white">{chapter.title}</div>
                                    <div className="mt-5 flex items-center justify-between gap-3">
                                        <div className="font-mono text-[10px] uppercase tracking-[0.24em] text-ash-500">
                                            {new Date(chapter.created_at).toLocaleDateString(LOCALE_LANG[locale])}
                                        </div>
                                        <ChevronRight size={14} className="shrink-0 text-ash-500" />
                                    </div>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                            {Array.from({ length: 8 }).map((_, index) => (
                                <div key={index} className="rounded-[24px] border border-white/10 bg-black/25 p-5 backdrop-blur animate-pulse">
                                    <div className="h-3 w-20 rounded bg-ash-800" />
                                    <div className="mt-4 h-6 w-full rounded bg-ash-800" />
                                    <div className="mt-2 h-6 w-3/4 rounded bg-ash-800" />
                                    <div className="mt-6 h-3 w-24 rounded bg-ash-800" />
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
