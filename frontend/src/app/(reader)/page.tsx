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
    const isEastAsianLocale = locale === "ja" || locale === "zh-CN";
    const isEnglishLocale = locale === "en";

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

    const heroTitleClassName = isEastAsianLocale
        ? "homepage-hero-title font-biohazard text-[4.1rem] leading-[0.96] animate-flicker sm:text-[5.4rem] md:text-[6.4rem] lg:text-[6.7rem] xl:text-[7.2rem]"
        : isEnglishLocale
          ? "homepage-hero-title font-biohazard text-5xl leading-[0.94] animate-flicker sm:text-[5.8rem] md:text-[6.6rem] lg:text-[6.8rem] xl:text-[7.2rem]"
          : "homepage-hero-title font-biohazard text-5xl leading-[0.92] animate-flicker sm:text-7xl md:text-8xl lg:text-[7rem] xl:text-[7.6rem]";

    const heroSubtitleClassName = isEastAsianLocale
        ? "mt-2 font-biohazard text-lg tracking-[0.06em] text-ash-200 sm:mt-3 sm:text-[1.7rem] md:text-[2rem]"
        : isEnglishLocale
          ? "mt-2 font-biohazard text-xl tracking-[0.1em] text-ash-200 sm:mt-3 sm:text-[1.9rem] md:text-[2.35rem]"
          : "mt-2 font-biohazard text-xl tracking-[0.12em] text-ash-200 sm:mt-3 sm:text-3xl sm:tracking-[0.15em] md:text-4xl";

    const chapterCardTitleClassName = isEastAsianLocale
        ? "mt-3 line-clamp-3 font-biohazard text-[1.22rem] leading-[1.1] tracking-[0.03em] text-worn-white sm:mt-4 sm:text-[1.75rem] sm:leading-[1.08]"
        : isEnglishLocale
          ? "mt-3 line-clamp-3 font-biohazard text-[1.28rem] leading-[1.08] tracking-[0.035em] text-worn-white sm:mt-4 sm:text-[1.9rem] sm:leading-[1.06]"
          : "mt-3 line-clamp-3 font-biohazard text-[1.3rem] leading-[1.06] tracking-[0.04em] text-worn-white sm:mt-4 sm:text-[1.95rem] sm:leading-[1.04]";

    const heroTextWrapClassName = isEastAsianLocale
        ? "max-w-[34rem] lg:max-w-[31rem] xl:max-w-[33rem]"
        : isEnglishLocale
          ? "max-w-[40rem] lg:max-w-[35rem] xl:max-w-[37rem]"
          : "max-w-[42rem] lg:max-w-[38rem] xl:max-w-[40rem]";

    const heroTitleWidthClassName = isEastAsianLocale
        ? "max-w-[8.5ch]"
        : isEnglishLocale
          ? "max-w-[10.5ch]"
          : "max-w-[11.5ch]";

    const heroSubtitleWidthClassName = isEastAsianLocale
        ? "max-w-[16ch]"
        : isEnglishLocale
          ? "max-w-[18ch]"
          : "max-w-[20ch]";

    const heroDescriptionClassName = isEastAsianLocale
        ? "rich-text-home mt-6 max-w-[33rem] font-reading text-[15px] leading-[1.85] text-ash-100 sm:mt-8 sm:text-[1.02rem] sm:leading-[1.95]"
        : isEnglishLocale
          ? "rich-text-home mt-6 max-w-[36rem] font-reading text-[15px] leading-[1.9] text-ash-100 sm:mt-8 sm:text-lg sm:leading-[2.05]"
          : "rich-text-home mt-6 max-w-[38rem] font-reading text-[15px] leading-[1.92] text-ash-100 sm:mt-8 sm:text-lg sm:leading-[2.08]";

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

                <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(57,255,20,0.05),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(139,0,0,0.12),transparent_26%),linear-gradient(180deg,rgba(0,0,0,0.48),rgba(0,0,0,0.82))]" />
                <div className="pointer-events-none absolute inset-0 [box-shadow:inset_0_0_160px_rgba(0,0,0,0.34)] sm:[box-shadow:inset_0_0_220px_rgba(0,0,0,0.38)]" />
                <div
                    className="pointer-events-none absolute inset-0"
                    style={{
                        background:
                            "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(57,255,20,0.008) 3px, rgba(57,255,20,0.008) 4px)",
                    }}
                />

                <div className="relative z-10 mx-auto max-w-7xl px-5 py-10 sm:px-6 sm:py-14 lg:py-24">
                    <div className="grid items-center gap-8 lg:grid-cols-[minmax(0,0.9fr)_minmax(540px,1.1fr)] lg:gap-[3.6rem] xl:grid-cols-[minmax(0,0.88fr)_minmax(620px,1.12fr)] xl:gap-[4.1rem]">
                        <div className={`homepage-copy-block max-w-3xl ${heroTextWrapClassName}`}>
                            <div className="mb-4 flex flex-wrap gap-2.5 sm:mb-5 sm:gap-3">
                                <div className="inline-flex items-center gap-2 rounded-full border border-blood-red-DEFAULT/35 bg-blood-red-DEFAULT/10 px-3 py-1.5 sm:px-4 sm:py-2">
                                    <Skull size={12} className="text-blood-red-bright" />
                                    <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-blood-red-bright sm:text-[11px] sm:tracking-[0.28em]">
                                        {novel.status} / {novel.max_chapter || "?"} {dictionary.home.chapters}
                                    </span>
                                </div>
                                <div className="inline-flex items-center gap-2 rounded-full border border-toxic-green-DEFAULT/25 bg-black/35 px-3 py-1.5 sm:px-4 sm:py-2">
                                    <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-ash-400 sm:text-[11px] sm:tracking-[0.28em]">{dictionary.home.author}</span>
                                    <span className="font-biohazard text-xs uppercase tracking-[0.14em] text-toxic-green-bright sm:text-sm sm:tracking-[0.18em]">{novel.author}</span>
                                </div>
                            </div>

                            <h1 className={`${heroTitleClassName} ${heroTitleWidthClassName}`}>
                                {primary}
                            </h1>
                            {secondary ? (
                                <h2 className={`${heroSubtitleClassName} ${heroSubtitleWidthClassName}`}>{secondary}</h2>
                            ) : null}

                            <div className="mt-6 flex items-center gap-3 sm:mt-8 sm:gap-4">
                                <div className="h-px flex-1 bg-gradient-to-r from-toxic-green-DEFAULT/50 to-transparent" />
                                <span className="font-mono text-[11px] uppercase tracking-[0.24em] text-toxic-green-DEFAULT sm:text-sm sm:tracking-[0.32em]">Bio-Scan</span>
                                <div className="h-px w-10 bg-toxic-green-DEFAULT/30 sm:w-16" />
                            </div>

                            <div
                                className={heroDescriptionClassName}
                                dangerouslySetInnerHTML={{ __html: novel.description }}
                            />

                            {homeSettings.is_fallback && locale !== "vi" ? (
                                <div className="mt-4 inline-flex items-center rounded-full border border-toxic-green-DEFAULT/20 bg-toxic-green-DEFAULT/5 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.22em] text-toxic-green-DEFAULT sm:mt-5 sm:px-4 sm:py-2 sm:text-[11px] sm:tracking-[0.28em]">
                                    {dictionary.common.fallbackVietnamese}
                                </div>
                            ) : null}

                            <div className="mt-7 grid gap-3 sm:hidden">
                                <Link href={localizedFirstChapterPath} className="btn-fixed-blood inline-flex w-full items-center justify-center gap-2 px-5 py-3 text-sm">
                                    <BookOpen size={16} />
                                    <span>{dictionary.home.readFirst}</span>
                                </Link>
                                <ContinueButton
                                    fixedDark
                                    fallbackPath="/chapters"
                                    fallbackLabel={dictionary.home.viewContents}
                                    className="!w-full !justify-center !border-white/12 !bg-black/30 !text-ash-200/80 hover:!border-white/18 hover:!bg-black/52 hover:!text-white"
                                />
                            </div>

                            <div className="mt-7 hidden flex-wrap gap-3 sm:mt-8 sm:flex sm:gap-4">
                                <Link href={localizedFirstChapterPath} className="btn-fixed-blood inline-flex items-center gap-2 px-5 py-3 text-sm sm:px-6 sm:text-base">
                                    <BookOpen size={16} />
                                    <span>{dictionary.home.readFirst}</span>
                                </Link>
                                <ContinueButton
                                    fixedDark
                                    className="!border-white/12 !bg-black/30 !text-ash-200/80 hover:!border-white/18 hover:!bg-black/52 hover:!text-white"
                                />
                                <Link
                                    href={localizedChapterListPath}
                                    className="btn-fixed-dark inline-flex items-center gap-2 px-5 py-3 text-sm !border-white/12 !bg-black/30 !text-ash-200/80 hover:!border-white/18 hover:!bg-black/52 hover:!text-white sm:px-6 sm:text-base"
                                >
                                    <span>{dictionary.home.viewContents}</span>
                                    <ChevronRight size={14} />
                                </Link>
                            </div>

                            <div className="mt-7 grid grid-cols-2 gap-3 sm:mt-10 xl:grid-cols-[minmax(0,0.72fr)_minmax(0,1.18fr)_minmax(0,1.08fr)_minmax(0,0.94fr)]">
                                {heroStats.map(({ label, value }) => (
                                    <div key={label} className="rounded-[22px] border border-white/8 bg-black/38 p-3.5 backdrop-blur-md sm:p-4">
                                        <div className="font-mono text-[10px] uppercase tracking-[0.24em] text-ash-500">{label}</div>
                                        <div className="mt-2 break-words font-biohazard text-xl leading-tight text-toxic-green-DEFAULT sm:text-[1.9rem]">{value}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="homepage-video-shell lg:pl-4 xl:pl-7">
                            <HomepageHeroVideo
                                title={novel.author}
                                src="/media/han-phong-mystical-explosion.mp4"
                                poster="/media/han-phong-mystical-explosion-poster.jpg"
                            />
                        </div>
                    </div>
                </div>
            </section>

            <section className="homepage-section-soft px-5 py-12 sm:px-6 sm:py-16 lg:py-[5.8rem]">
                <div className="mx-auto max-w-7xl">
                    <div className="grid gap-7 lg:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)] lg:gap-8">
                        <div className="relative overflow-hidden rounded-[28px] border border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.02),rgba(0,0,0,0.34))] p-5 shadow-[0_26px_84px_rgba(0,0,0,0.3)] backdrop-blur-md sm:p-7">
                            <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-toxic-green-DEFAULT/20 to-transparent" />

                            <div className="mb-5 flex items-start gap-3 sm:mb-6">
                                <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-toxic-green-DEFAULT/20 bg-black/45 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
                                    <AlertTriangle size={18} className="text-toxic-green-DEFAULT" />
                                </div>
                                <div>
                                    <div className="font-mono text-[11px] uppercase tracking-[0.32em] text-toxic-green-DEFAULT">{homeSettings.warning_title}</div>
                                    <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.26em] text-ash-500">
                                        {homeSettings.warning_subtitle}
                                    </div>
                                </div>
                            </div>

                            <h2 className="font-biohazard text-[1.9rem] tracking-[0.04em] text-worn-white sm:text-4xl">{homeSettings.warning_headline}</h2>
                            <div
                                className="rich-text-home mt-5 max-w-[42rem] font-reading text-sm leading-[1.95] text-ash-200 sm:mt-6 sm:text-base sm:leading-[2]"
                                dangerouslySetInnerHTML={{ __html: homeSettings.warning_description }}
                            />
                        </div>

                        <div>
                            <div className="mb-5 flex items-center gap-3 sm:mb-6">
                                <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-toxic-green-DEFAULT/20 bg-black/45 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
                                    <Shield size={18} className="text-toxic-green-DEFAULT" />
                                </div>
                                <div className="font-mono text-[11px] uppercase tracking-[0.32em] text-toxic-green-DEFAULT">{homeSettings.features_title}</div>
                            </div>

                            <div className="grid gap-4 md:grid-cols-2">
                                {homeSettings.features_json.map((feature, index) => (
                                    <div
                                        key={`${feature.title}-${index}`}
                                        className="group relative overflow-hidden rounded-[24px] border border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.02),rgba(0,0,0,0.28))] p-4 backdrop-blur-md transition duration-300 hover:-translate-y-0.5 hover:border-white/14 hover:bg-[linear-gradient(180deg,rgba(255,255,255,0.035),rgba(0,0,0,0.36))] sm:p-5"
                                    >
                                        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 transition duration-300 group-hover:opacity-100" />
                                        <div className="flex items-start gap-4">
                                            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-toxic-green-DEFAULT/15 bg-black/46 text-xl shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
                                                {feature.icon}
                                            </div>
                                            <div>
                                                <div className="font-mono text-[10px] uppercase tracking-[0.24em] text-ash-500">Feature {String(index + 1).padStart(2, "0")}</div>
                                                <div className="mt-2 font-biohazard text-xl tracking-[0.06em] text-worn-white">{feature.title}</div>
                                                <div className="mt-2 text-sm leading-[1.9] text-ash-300">{feature.desc}</div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section className="homepage-section-soft border-y border-white/6 bg-black/24 px-5 py-12 sm:px-6 sm:py-16 lg:py-[5.9rem]">
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
                        <div className="homepage-chapter-rail -mx-5 flex snap-x snap-mandatory gap-3 overflow-x-auto px-5 pb-2 md:mx-0 md:grid md:gap-4 md:overflow-visible md:px-0 md:pb-0 md:[grid-template-columns:repeat(2,minmax(0,1fr))] xl:[grid-template-columns:repeat(4,minmax(0,1fr))]">
                            {latestChapters.map((chapter, index) => (
                                <Link
                                    key={chapter.id}
                                    href={withLocalePath(locale, `/chapters/${chapter.chapter_number}`)}
                                    className="homepage-chapter-card group relative min-w-[82vw] snap-start overflow-hidden rounded-[24px] border border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.02),rgba(0,0,0,0.26))] p-3.5 backdrop-blur-md transition duration-300 hover:-translate-y-0.5 hover:border-white/14 hover:bg-[linear-gradient(180deg,rgba(255,255,255,0.035),rgba(0,0,0,0.34))] hover:shadow-[0_22px_55px_rgba(0,0,0,0.28)] sm:min-w-[27rem] sm:rounded-[26px] sm:p-5 md:min-w-0"
                                    style={{ animationDelay: `${index * 0.05}s` }}
                                >
                                    <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(140deg,rgba(57,255,20,0.04),transparent_28%,transparent_72%,rgba(255,255,255,0.03))] opacity-70 transition-opacity duration-300 group-hover:opacity-100" />
                                    <div className="relative z-10 flex items-start justify-between gap-3">
                                        <div className="rounded-full border border-white/10 bg-black/28 px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.2em] text-toxic-green-DEFAULT sm:px-3 sm:text-[10px] sm:tracking-[0.24em]">
                                            {dictionary.reader.chapter} {chapter.chapter_number}
                                        </div>
                                        <div className="rounded-full border border-white/8 bg-black/22 px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.12em] text-ash-500 sm:px-3 sm:text-[10px] sm:tracking-[0.18em]">
                                            {new Date(chapter.created_at).toLocaleDateString(LOCALE_LANG[locale])}
                                        </div>
                                    </div>
                                    <div className="relative z-10 mt-4 sm:mt-5">
                                        <div className={chapterCardTitleClassName}>{chapter.title}</div>
                                    </div>
                                    <div className="relative z-10 mt-5 flex items-center justify-between gap-3 border-t border-white/8 pt-3.5 sm:mt-6 sm:pt-4">
                                        <div className="font-mono text-[9px] uppercase tracking-[0.16em] text-ash-500 sm:text-[10px] sm:tracking-[0.2em]">
                                            {dictionary.home.latestUpdated}
                                        </div>
                                        <ChevronRight size={14} className="shrink-0 text-ash-500 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:text-white" />
                                    </div>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <div className="homepage-chapter-rail -mx-5 flex gap-3 overflow-x-auto px-5 pb-2 md:mx-0 md:grid md:gap-4 md:overflow-visible md:px-0 md:pb-0 md:[grid-template-columns:repeat(2,minmax(0,1fr))] xl:[grid-template-columns:repeat(4,minmax(0,1fr))]">
                            {Array.from({ length: 8 }).map((_, index) => (
                                <div key={index} className="min-w-[82vw] rounded-[22px] border border-white/8 bg-black/30 p-3.5 backdrop-blur-md animate-pulse sm:min-w-[27rem] sm:rounded-[24px] sm:p-5 md:min-w-0">
                                    <div className="h-3 w-20 rounded bg-ash-800" />
                                    <div className="mt-3 h-5 w-full rounded bg-ash-800 sm:mt-4 sm:h-6" />
                                    <div className="mt-2 h-6 w-3/4 rounded bg-ash-800" />
                                    <div className="mt-5 h-3 w-24 rounded bg-ash-800 sm:mt-6" />
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="mt-10 flex flex-col items-center gap-4 text-center sm:mt-12">
                        <ContinueButton
                            fixedDark
                            className="!border-white/12 !bg-black/30 !text-ash-200/80 hover:!border-white/18 hover:!bg-black/52 hover:!text-white"
                        />
                        <Link href={localizedFirstChapterPath} className="btn-fixed-blood inline-flex items-center gap-2 px-7 py-3 text-sm sm:px-8 sm:text-base">
                            <Zap size={16} />
                            <span>{dictionary.home.startNow}</span>
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}
