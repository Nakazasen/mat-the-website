"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

export default function ChapterJump() {
    const [chapter, setChapter] = useState("");
    const router = useRouter();

    const handleJump = (e: React.FormEvent) => {
        e.preventDefault();
        const num = parseInt(chapter, 10);
        if (!isNaN(num) && num > 0) {
            router.push(`/chapters/${num}`);
        }
    };

    return (
        <form
            onSubmit={handleJump}
            className="flex items-center gap-2 text-ash-400 text-sm shrink-0 bg-ash-950/50 border border-ash-800 rounded px-2 py-1 focus-within:border-toxic-green-DEFAULT/50 transition-colors"
        >
            <Search size={14} className="text-ash-600" />
            <input
                type="number"
                value={chapter}
                onChange={(e) => setChapter(e.target.value)}
                placeholder="NHẢY ĐẾN CHƯƠNG..."
                className="bg-transparent border-none outline-none font-mono text-xs w-32 placeholder:text-ash-700 text-ash-200"
            />
            <button
                type="submit"
                className="text-[10px] font-mono bg-ash-800 hover:bg-toxic-green-DEFAULT hover:text-black px-1.5 py-0.5 rounded transition-colors"
            >
                OK
            </button>
        </form>
    );
}
