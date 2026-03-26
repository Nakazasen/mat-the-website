"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Zap } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";

export default function ContinueButton({ fixedDark }: { fixedDark?: boolean }) {
    const { dictionary, localizePath } = useLocale();
    const [history, setHistory] = useState<{ chapter: string; title: string } | null>(null);

    useEffect(() => {
        const chapter = localStorage.getItem("lastReadChapter");
        const title = localStorage.getItem("lastReadTitle");
        if (chapter && title) {
            setHistory({ chapter, title });
        }
    }, []);

    if (!history) return null;

    return (
        <Link
            href={localizePath(`/chapters/${history.chapter}`)}
            className={`${fixedDark ? "btn-fixed-dark" : "btn-toxic"} flex items-center gap-2 px-6 py-3 text-base animate-pulse-slow`}
        >
            <Zap size={16} fill="currentColor" />
            <span className="max-w-[200px] truncate sm:max-w-none">
                {dictionary.reader.continueReading} CH.{history.chapter}
            </span>
        </Link>
    );
}
