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
        <div className="relative overflow-hidden rounded-[22px] border border-toxic-green-DEFAULT/25 bg-black/45 shadow-[0_0_70px_rgba(57,255,20,0.12)] lg:rounded-[30px] lg:shadow-[0_0_90px_rgba(57,255,20,0.14)]">
            <div className="pointer-events-none absolute inset-0 z-10 opacity-15 [background-image:linear-gradient(rgba(57,255,20,0.12)_1px,transparent_1px)] [background-size:100%_6px] sm:opacity-20" />
            <div className="pointer-events-none absolute inset-0 z-10 bg-[radial-gradient(circle_at_top_right,rgba(57,255,20,0.12),transparent_30%),linear-gradient(180deg,rgba(0,0,0,0.08),rgba(0,0,0,0.28))]" />

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
                <div className="rounded-full border border-white/15 bg-black/60 px-3 py-1 font-mono text-[9px] uppercase tracking-[0.24em] text-ash-100 backdrop-blur sm:text-[10px] sm:tracking-[0.28em]">
                    {title}
                </div>
                <div className="hidden rounded-full border border-toxic-green-DEFAULT/25 bg-toxic-green-DEFAULT/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.28em] text-toxic-green-bright backdrop-blur sm:block">
                    Trailer
                </div>
            </div>

            <div className="absolute bottom-3 left-3 right-3 z-20 flex flex-wrap gap-2 sm:bottom-4 sm:left-4 sm:right-4">
                <button
                    type="button"
                    onClick={() => void handleTogglePlayback()}
                    className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/65 px-2.5 py-2 font-mono text-[9px] uppercase tracking-[0.22em] text-ash-100 backdrop-blur transition hover:border-white/30 hover:bg-black/80 sm:px-3 sm:text-[10px] sm:tracking-[0.28em]"
                >
                    {isPlaying ? <Pause size={13} /> : <Play size={13} />}
                    <span className="hidden sm:inline">{isPlaying ? "Pause" : "Play"}</span>
                </button>
                <button
                    type="button"
                    onClick={handleToggleMuted}
                    className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/65 px-2.5 py-2 font-mono text-[9px] uppercase tracking-[0.22em] text-ash-100 backdrop-blur transition hover:border-white/30 hover:bg-black/80 sm:px-3 sm:text-[10px] sm:tracking-[0.28em]"
                >
                    {isMuted ? <VolumeX size={13} /> : <Volume2 size={13} />}
                    <span className="hidden sm:inline">{isMuted ? "Muted" : "Sound"}</span>
                </button>
            </div>
        </div>
    );
}
