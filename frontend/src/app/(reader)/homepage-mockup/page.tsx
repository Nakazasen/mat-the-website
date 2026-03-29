import Link from "next/link";
import { ArrowRight, BookOpen, Flame, Shield, Zap } from "lucide-react";

import HeroBackground from "@/components/HeroBackground";
import HomepageHeroVideo from "@/components/HomepageHeroVideo";
import { withLocalePath } from "@/lib/i18n/config";
import { getCurrentLocale } from "@/lib/i18n/server";

export const dynamic = "force-dynamic";

const featureCards = [
    {
        icon: Shield,
        label: "Survival",
        title: "Nhịp đọc gọn",
        description: "Màn đầu chỉ giữ đúng thông tin cần thiết: hook, CTA, video và vài chỉ số cốt lõi.",
    },
    {
        icon: Zap,
        label: "Progression",
        title: "Visual làm trung tâm",
        description: "Một hero asset mạnh kéo mood toàn trang, thay cho nhiều panel mô tả đè lên nhau.",
    },
    {
        icon: Flame,
        label: "World",
        title: "Chất mạt thế rõ hơn",
        description: "Tông tối, lạnh, căng thẳng; nhấn bằng xanh độc và đỏ cảnh báo, không phô trương quá tay.",
    },
];

const chapterCards = [
    {
        number: "CH.001",
        title: "Ngày thế giới lệch trục",
        meta: "Khởi đầu",
    },
    {
        number: "CH.124",
        title: "Không còn đường lùi",
        meta: "Leo cấp",
    },
    {
        number: "CH.312",
        title: "Vùng an toàn rạn nứt",
        meta: "Mở rộng",
    },
    {
        number: "CH.817",
        title: "Chiến tuyến mới",
        meta: "Hiện tại",
    },
];

export default async function HomepageMockupPage() {
    const locale = await getCurrentLocale();
    const firstChapterPath = withLocalePath(locale, "/chapters/1");
    const chapterListPath = withLocalePath(locale, "/chapters");

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
                    fallbackImage="/hero-bg.png"
                    title="Homepage Mockup"
                />

                <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(57,255,20,0.08),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(139,0,0,0.18),transparent_28%),linear-gradient(180deg,rgba(0,0,0,0.38),rgba(0,0,0,0.72))]" />

                <div className="relative z-10 mx-auto max-w-7xl px-6 py-14 sm:py-18 lg:py-24">
                    <div className="mb-8 inline-flex items-center rounded-full border border-white/10 bg-black/35 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.32em] text-ash-300 backdrop-blur">
                        Preview route / không ảnh hưởng homepage hiện tại
                    </div>

                    <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,0.95fr)_minmax(480px,1.05fr)]">
                        <div className="max-w-2xl">
                            <div className="mb-4 flex flex-wrap gap-3">
                                <div className="rounded-full border border-blood-red-DEFAULT/35 bg-blood-red-DEFAULT/12 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-blood-red-bright">
                                    817 chương
                                </div>
                                <div className="rounded-full border border-toxic-green-DEFAULT/20 bg-black/30 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-toxic-green-bright">
                                    cinematic dystopia
                                </div>
                            </div>

                            <h1 className="font-biohazard text-6xl leading-none text-toxic-glow sm:text-7xl lg:text-[6.5rem]">
                                Mạt Thế
                            </h1>

                            <p className="mt-6 max-w-xl font-reading text-base leading-8 text-ash-100 sm:text-lg">
                                Hướng làm mới nên đi theo kiểu gọn, lạnh và có trọng tâm: ít chữ hơn, video mạnh hơn, CTA rõ hơn, toàn bộ
                                hero nhìn giống landing page cao cấp chứ không giống dashboard chắp vá.
                            </p>

                            <div className="mt-8 flex flex-wrap gap-4">
                                <Link href={firstChapterPath} className="btn-fixed-blood inline-flex items-center gap-2 px-6 py-3 text-base">
                                    <BookOpen size={16} />
                                    Đọc từ đầu
                                </Link>
                                <Link href={chapterListPath} className="btn-fixed-dark inline-flex items-center gap-2 px-6 py-3 text-base">
                                    Xem danh sách chương
                                    <ArrowRight size={16} />
                                </Link>
                            </div>

                            <div className="mt-10 grid gap-3 sm:grid-cols-3">
                                <div className="rounded-2xl border border-white/10 bg-black/30 p-4 backdrop-blur">
                                    <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ash-500">Hero</div>
                                    <div className="mt-2 font-biohazard text-2xl text-toxic-green-DEFAULT">1 video</div>
                                </div>
                                <div className="rounded-2xl border border-white/10 bg-black/30 p-4 backdrop-blur">
                                    <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ash-500">Tone</div>
                                    <div className="mt-2 font-biohazard text-2xl text-toxic-green-DEFAULT">ít chữ</div>
                                </div>
                                <div className="rounded-2xl border border-white/10 bg-black/30 p-4 backdrop-blur">
                                    <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ash-500">Mood</div>
                                    <div className="mt-2 font-biohazard text-2xl text-toxic-green-DEFAULT">premium</div>
                                </div>
                            </div>
                        </div>

                        <div className="lg:pl-6">
                            <HomepageHeroVideo
                                title="Hàn Phong"
                                src="/media/han-phong-mystical-explosion.mp4"
                                poster="/media/han-phong-mystical-explosion-poster.jpg"
                            />
                        </div>
                    </div>
                </div>
            </section>

            <section className="px-6 py-14 sm:py-16">
                <div className="mx-auto max-w-7xl">
                    <div className="mb-8 flex items-end justify-between gap-4">
                        <div>
                            <div className="font-mono text-[11px] uppercase tracking-[0.34em] text-toxic-green-DEFAULT">Direction</div>
                            <h2 className="mt-3 font-biohazard text-3xl tracking-[0.06em] text-worn-white sm:text-4xl">
                                Ít panel hơn, đúng nhịp hơn
                            </h2>
                        </div>
                        <div className="hidden max-w-md font-reading text-sm leading-7 text-ash-400 lg:block">
                            Không nhồi lore ở màn đầu. Hero chỉ cần tạo mood, kéo người đọc vào truyện và dẫn sang chương đầu.
                        </div>
                    </div>

                    <div className="grid gap-4 lg:grid-cols-3">
                        {featureCards.map((card) => (
                            <div
                                key={card.title}
                                className="rounded-[24px] border border-white/10 bg-black/25 p-6 backdrop-blur transition hover:border-toxic-green-DEFAULT/30 hover:bg-black/35"
                            >
                                <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-toxic-green-DEFAULT/20 bg-toxic-green-DEFAULT/10">
                                    <card.icon size={20} className="text-toxic-green-DEFAULT" />
                                </div>
                                <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-toxic-green-DEFAULT">{card.label}</div>
                                <div className="mt-3 font-biohazard text-2xl tracking-[0.06em] text-worn-white">{card.title}</div>
                                <div className="mt-3 font-reading text-sm leading-7 text-ash-300">{card.description}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <section className="border-y border-white/6 bg-black/20 px-6 py-14 sm:py-16">
                <div className="mx-auto max-w-7xl">
                    <div className="mb-8 flex items-end justify-between gap-4">
                        <div>
                            <div className="font-mono text-[11px] uppercase tracking-[0.34em] text-toxic-green-DEFAULT">Latest Flow</div>
                            <h2 className="mt-3 font-biohazard text-3xl tracking-[0.06em] text-worn-white sm:text-4xl">
                                Chapter card nên sạch và căng
                            </h2>
                        </div>
                        <Link href={chapterListPath} className="font-mono text-sm uppercase tracking-[0.22em] text-ash-400 transition hover:text-toxic-green-DEFAULT">
                            xem tất cả
                        </Link>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                        {chapterCards.map((chapter) => (
                            <div
                                key={chapter.number}
                                className="rounded-[24px] border border-white/10 bg-black/30 p-5 backdrop-blur transition hover:border-toxic-green-DEFAULT/30 hover:bg-black/40"
                            >
                                <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-toxic-green-DEFAULT">{chapter.number}</div>
                                <div className="mt-3 font-biohazard text-2xl leading-tight tracking-[0.05em] text-worn-white">{chapter.title}</div>
                                <div className="mt-5 inline-flex rounded-full border border-white/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.28em] text-ash-400">
                                    {chapter.meta}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>
        </div>
    );
}
