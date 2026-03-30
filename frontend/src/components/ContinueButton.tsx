"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronRight, Zap } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";

export default function ContinueButton({
    fixedDark,
    className = "",
    fallbackPath,
    fallbackLabel,
}: {
    fixedDark?: boolean;
    className?: string;
    fallbackPath?: string;
    fallbackLabel?: string;
}) {
    const { dictionary, localizePath } = useLocale();
    const [history, setHistory] = useState<{ chapter: string; title: string } | null>(null);

    useEffect(() => {
        const chapter = localStorage.getItem("lastReadChapter");
        const title = localStorage.getItem("lastReadTitle");
        if (chapter && title) {
            setHistory({ chapter, title });
        }
    }, []);

    if (!history) {
        if (!fallbackPath || !fallbackLabel) return null;

        return (
            <Link
                href={localizePath(fallbackPath)}
                className={`${fixedDark ? "btn-fixed-dark" : "btn-toxic"} ${className} flex items-center justify-center gap-2 px-6 py-3 text-base`}
            >
                <span className="max-w-[220px] truncate sm:max-w-none">{fallbackLabel}</span>
                <ChevronRight size={16} />
            </Link>
        );
    }

    return (
        <Link
            href={localizePath(`/chapters/${history.chapter}`)}
            className={`${fixedDark ? "btn-fixed-dark" : "btn-toxic"} ${className} flex items-center gap-2 px-6 py-3 text-base animate-pulse-slow`}
        >
            <Zap size={16} fill="currentColor" />
            <span className="max-w-[200px] truncate sm:max-w-none">
                {dictionary.reader.continueReading} CH.{history.chapter}
            </span>
        </Link>
    );
}
