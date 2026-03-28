"use client";

import Link from "next/link";
import { BookMarked, Languages, Quote } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";

export default function ReaderStudyDock() {
    const { localizePath } = useLocale();

    return (
        <div className="fixed bottom-24 left-4 z-[58] hidden md:block">
            <div className="overflow-hidden rounded-2xl border border-cyan-900/30 bg-[#071018]/90 shadow-[0_18px_50px_rgba(0,0,0,0.38)] backdrop-blur">
                <div className="border-b border-cyan-900/30 px-4 py-3">
                    <div className="flex items-center gap-2 text-cyan-300">
                        <Languages size={14} />
                        <span className="text-[11px] font-mono uppercase tracking-[0.28em]">
                            Learning
                        </span>
                    </div>
                    <p className="mt-2 max-w-[220px] text-xs leading-5 text-gray-400">
                        Bộ khung học tiếng đã sẵn sàng: tra từ, lưu từ và lưu câu sẽ được nối dần vào reader.
                    </p>
                </div>

                <div className="grid grid-cols-1 gap-2 p-3">
                    <Link
                        href={localizePath("/saved-vocab")}
                        className="inline-flex items-center gap-2 rounded-xl border border-cyan-900/30 px-3 py-2 text-sm text-gray-200 hover:border-cyan-500/40 hover:text-cyan-200"
                    >
                        <BookMarked size={14} />
                        Từ đã lưu
                    </Link>
                    <Link
                        href={localizePath("/saved-sentences")}
                        className="inline-flex items-center gap-2 rounded-xl border border-cyan-900/30 px-3 py-2 text-sm text-gray-200 hover:border-cyan-500/40 hover:text-cyan-200"
                    >
                        <Quote size={14} />
                        Câu đã lưu
                    </Link>
                </div>
            </div>
        </div>
    );
}
