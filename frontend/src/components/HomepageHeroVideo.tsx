"use client";

import { Pause, Play, Volume2, VolumeX } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface HomepageHeroVideoProps {
    title: string;
    src: string;
    poster: string;
}

export default function HomepageHeroVideo({ title, src, poster }: HomepageHeroVideoProps) {
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const [isPlaying, setIsPlaying] = useState(true);
    const [isMuted, setIsMuted] = useState(true);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const syncState = () => {
            setIsPlaying(!video.paused);
            setIsMuted(video.muted);
        };

        syncState();
        video.addEventListener("play", syncState);
        video.addEventListener("pause", syncState);
        video.addEventListener("volumechange", syncState);

        return () => {
            video.removeEventListener("play", syncState);
            video.removeEventListener("pause", syncState);
            video.removeEventListener("volumechange", syncState);
        };
    }, []);

    const handleTogglePlayback = async () => {
        const video = videoRef.current;
        if (!video) return;
        if (video.paused) {
            await video.play();
        } else {
            video.pause();
        }
    };

    const handleToggleMuted = () => {
        const video = videoRef.current;
        if (!video) return;
        video.muted = !video.muted;
        setIsMuted(video.muted);
    };

    return (
        <div className="relative overflow-hidden rounded-[22px] border border-white/10 bg-black/55 shadow-[0_28px_100px_rgba(0,0,0,0.4)] lg:rounded-[30px]">
            <div className="pointer-events-none absolute inset-0 z-10 opacity-10 [background-image:linear-gradient(rgba(57,255,20,0.1)_1px,transparent_1px)] [background-size:100%_6px] sm:opacity-15" />
            <div className="pointer-events-none absolute inset-0 z-10 bg-[radial-gradient(circle_at_top_right,rgba(57,255,20,0.08),transparent_28%),linear-gradient(180deg,rgba(0,0,0,0.02),rgba(0,0,0,0.38))]" />

            <video
                ref={videoRef}
                className="aspect-[4/3] w-full bg-black object-cover sm:aspect-video"
                autoPlay
                loop
                muted
                playsInline
                controls
                preload="metadata"
                poster={poster}
            >
                <source src={src} type="video/mp4" />
            </video>

            <div className="absolute left-3 top-3 z-20 flex items-center gap-2 sm:left-4 sm:top-4">
                <div className="rounded-full border border-white/12 bg-black/68 px-3 py-1 font-mono text-[9px] uppercase tracking-[0.24em] text-ash-100 backdrop-blur-md sm:text-[10px] sm:tracking-[0.28em]">
                    {title}
                </div>
                <div className="hidden rounded-full border border-white/12 bg-black/68 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.28em] text-ash-200 backdrop-blur-md sm:block">
                    Trailer
                </div>
            </div>

            <div className="absolute bottom-3 left-3 right-3 z-20 flex flex-wrap gap-2 sm:bottom-4 sm:left-4 sm:right-4">
                <button
                    type="button"
                    onClick={() => void handleTogglePlayback()}
                    className="inline-flex items-center gap-2 rounded-full border border-white/12 bg-black/68 px-2.5 py-2 font-mono text-[9px] uppercase tracking-[0.22em] text-ash-100 backdrop-blur-md transition hover:border-white/24 hover:bg-black/82 sm:px-3 sm:text-[10px] sm:tracking-[0.28em]"
                >
                    {isPlaying ? <Pause size={13} /> : <Play size={13} />}
                    <span className="hidden sm:inline">{isPlaying ? "Pause" : "Play"}</span>
                </button>
                <button
                    type="button"
                    onClick={handleToggleMuted}
                    className="inline-flex items-center gap-2 rounded-full border border-white/12 bg-black/68 px-2.5 py-2 font-mono text-[9px] uppercase tracking-[0.22em] text-ash-100 backdrop-blur-md transition hover:border-white/24 hover:bg-black/82 sm:px-3 sm:text-[10px] sm:tracking-[0.28em]"
                >
                    {isMuted ? <VolumeX size={13} /> : <Volume2 size={13} />}
                    <span className="hidden sm:inline">{isMuted ? "Muted" : "Sound"}</span>
                </button>
            </div>
        </div>
    );
}
