"use client";

import Link from "next/link";

import { useLocale } from "@/context/LocaleContext";
import { useNovel } from "@/context/NovelContext";

export default function Footer() {
    const { novel } = useNovel();
    const { dictionary, localizePath } = useLocale();

    const novelInfo = novel || {
        author: "Han Phong",
        status: "Updating",
        genres: ["Apocalypse", "Zombie"],
        max_chapter: 0,
        total_chapters: 0,
    };

    return (
        <footer className="bg-ash-950 border-t border-ash-800 mt-20">
            <div className="hazard-divider mx-8 mb-0" />

            <div className="max-w-7xl mx-auto px-6 py-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <span className="text-2xl text-toxic-green-DEFAULT">☣</span>
                            <div>
                                <div className="font-biohazard text-lg text-toxic-green-DEFAULT tracking-widest">
                                    {dictionary.footer.heading}
                                </div>
                                <div className="font-mono text-[9px] text-ash-500 tracking-[0.3em] uppercase">
                                    {dictionary.header.archive}
                                </div>
                            </div>
                        </div>
                        <p className="text-ash-400 text-sm leading-relaxed font-reading">
                            {dictionary.footer.blurb}
                        </p>
                    </div>

                    <div>
                        <h3 className="font-biohazard text-sm tracking-widest text-ash-300 mb-4 uppercase">
                            {dictionary.footer.links}
                        </h3>
                        <ul className="space-y-2">
                            {[
                                { href: "/", label: dictionary.common.home },
                                { href: "/chapters", label: dictionary.common.chapters },
                                { href: "/chapters/1", label: dictionary.footer.firstChapter },
                                { href: `/chapters/${novelInfo.max_chapter || 1}`, label: dictionary.footer.latest },
                            ].map(({ href, label }) => (
                                <li key={href}>
                                    <Link
                                        href={localizePath(href)}
                                        className="text-ash-400 hover:text-toxic-green-DEFAULT text-sm transition-colors flex items-center gap-2 group"
                                    >
                                        <span className="text-toxic-green-DEFAULT/30 group-hover:text-toxic-green-DEFAULT transition-colors">
                                            •
                                        </span>
                                        {label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-biohazard text-sm tracking-widest text-ash-300 mb-4 uppercase">
                            {dictionary.footer.stats}
                        </h3>
                        <div className="space-y-3">
                            {[
                                { label: dictionary.footer.author, value: novelInfo.author },
                                { label: dictionary.footer.status, value: novelInfo.status },
                                { label: dictionary.footer.genres, value: novelInfo.genres.join(" · ") },
                                { label: dictionary.footer.chapters, value: `${novelInfo.max_chapter || "?"}` },
                            ].map(({ label, value }) => (
                                <div key={label} className="flex justify-between text-sm gap-4">
                                    <span className="text-ash-500">{label}</span>
                                    <span className="text-ash-300 text-right">{value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="mt-10 pt-6 border-t border-ash-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-ash-600 text-xs font-mono">
                        © 2026 MAT THE · {dictionary.footer.allRightsReserved}
                    </p>
                    <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-toxic-green-DEFAULT animate-pulse" />
                        <span className="text-xs font-mono text-ash-500">{dictionary.common.online}</span>
                    </div>
                </div>
            </div>
        </footer>
    );
}
