"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";

export default function ChapterJump() {
    const [chapter, setChapter] = useState("");
    const router = useRouter();
    const { dictionary, localizePath } = useLocale();

    const handleJump = (event: React.FormEvent) => {
        event.preventDefault();
        if (!chapter.trim()) return;

        const num = parseInt(chapter, 10);
        if (!Number.isNaN(num) && num > 0) {
            router.push(localizePath(`/chapters/${num}`));
            return;
        }

        router.push(localizePath(`/chapters?search=${encodeURIComponent(chapter)}`));
    };

    return (
        <form
            onSubmit={handleJump}
            className="flex shrink-0 items-center gap-2 rounded border border-ash-800 bg-ash-950/50 px-2 py-1 text-sm text-ash-400 transition-colors focus-within:border-toxic-green-DEFAULT/50"
        >
            <Search size={14} className="text-ash-600" />
            <input
                type="text"
                value={chapter}
                onChange={(event) => setChapter(event.target.value)}
                placeholder={dictionary.reader.jumpPlaceholder}
                className="w-48 border-none bg-transparent font-mono text-xs text-ash-200 outline-none placeholder:text-ash-700"
            />
            <button
                type="submit"
                className="rounded bg-ash-800 px-1.5 py-0.5 font-mono text-[10px] transition-colors hover:bg-toxic-green-DEFAULT hover:text-black"
            >
                {dictionary.reader.jumpAction}
            </button>
        </form>
    );
}
