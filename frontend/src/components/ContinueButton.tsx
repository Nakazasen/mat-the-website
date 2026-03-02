"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Zap } from "lucide-react";

export default function ContinueButton() {
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
            href={`/chapters/${history.chapter}`}
            className="btn-toxic flex items-center gap-2 text-base py-3 px-6 animate-pulse-slow"
        >
            <Zap size={16} fill="currentColor" />
            <span className="truncate max-w-[200px] sm:max-w-none">
                TIẾP TỤC HÀNH TRÌNH TẠI CHƯƠNG {history.chapter}
            </span>
        </Link>
    );
}
