"use client";

import { useState, useEffect } from "react";
import { Heart } from "lucide-react";

interface LikeButtonProps {
    chapterId: number;
    chapterNumber: number;
}

const STORAGE_KEY = (n: number) => `liked_chapter_${n}`;

export default function LikeButton({ chapterId, chapterNumber }: LikeButtonProps) {
    const [liked, setLiked] = useState(false);
    const [count, setCount] = useState<number | null>(null);
    const [animating, setAnimating] = useState(false);
    const [showTip, setShowTip] = useState(false);

    useEffect(() => {
        let active = true;

        const loadLikeState = async () => {
            const localLiked = localStorage.getItem(STORAGE_KEY(chapterNumber)) === "true";
            if (active) {
                setLiked(localLiked);
            }

            try {
                const response = await fetch(`/api/user/chapter-engagement?chapter_id=${chapterId}`);
                if (!response.ok) return;
                const payload = await response.json();
                if (!active) return;
                if (payload?.has_liked) {
                    setLiked(true);
                    localStorage.setItem(STORAGE_KEY(chapterNumber), "true");
                }
            } catch {
                // Keep local fallback for guests or temporary API issues.
            }
        };

        loadLikeState();
        return () => {
            active = false;
        };
    }, [chapterId, chapterNumber]);

    async function handleLike() {
        if (liked) {
            setShowTip(true);
            setTimeout(() => setShowTip(false), 2000);
            return;
        }

        // Optimistic: mark liked immediately
        setLiked(true);
        localStorage.setItem(STORAGE_KEY(chapterNumber), "true");
        setAnimating(true);
        setTimeout(() => setAnimating(false), 600);

        try {
            const response = await fetch("/api/user/chapter-engagement", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    action: "like",
                    chapter_id: chapterId,
                    chapter_number: chapterNumber,
                }),
            });

            if (!response.ok) {
                throw new Error("Không ghi nhận được lượt tim.");
            }

            const payload = await response.json();
            if (typeof payload.likes_count === "number") {
                setCount(payload.likes_count);
            }
        } catch {
            // Keep UI consistent with DB when write fails.
            setLiked(false);
            localStorage.removeItem(STORAGE_KEY(chapterNumber));
        }
    }

    return (
        <div className="relative flex flex-col items-center gap-1">
            <button
                onClick={handleLike}
                title={liked ? "Bạn đã thả tim rồi!" : "Thả tim cho chương này"}
                className={`relative flex items-center gap-2 px-6 py-3 rounded-full border font-mono text-sm transition-all duration-300
                    ${liked
                        ? "bg-red-950/60 border-red-700 text-red-400 shadow-[0_0_12px_rgba(220,38,38,0.25)]"
                        : "bg-[#111] border-gray-800 text-gray-500 hover:border-red-900 hover:text-red-500"
                    }
                    ${animating ? "scale-125" : "scale-100"}
                `}
            >
                <Heart
                    size={18}
                    className={`transition-all duration-300 ${liked ? "fill-red-500 text-red-500" : "fill-none"}`}
                />
                <span>{liked ? "Đã thả tim" : "Thả tim"}</span>
                {count !== null && (
                    <span className="text-xs opacity-70">({count})</span>
                )}
            </button>

            {/* Tooltip */}
            {showTip && (
                <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-[#222] border border-gray-700 text-gray-400 text-xs font-mono px-3 py-1.5 rounded whitespace-nowrap">
                    ❤️ Anh đã thả tim rồi!
                </div>
            )}
        </div>
    );
}
