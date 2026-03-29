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
        <div className="relative overflow-hidden rounded-[24px] border border-toxic-green-DEFAULT/25 bg-black/45 shadow-[0_0_70px_rgba(57,255,20,0.12)]">
            <div className="pointer-events-none absolute inset-0 z-10 opacity-20 [background-image:linear-gradient(rgba(57,255,20,0.12)_1px,transparent_1px)] [background-size:100%_6px]" />
            <div className="pointer-events-none absolute inset-0 z-10 bg-[radial-gradient(circle_at_top_right,rgba(57,255,20,0.12),transparent_30%),linear-gradient(180deg,rgba(0,0,0,0.08),rgba(0,0,0,0.28))]" />

            <video
                ref={videoRef}
                className="aspect-video w-full bg-black object-cover"
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
                <div className="rounded-full border border-white/15 bg-black/60 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.28em] text-ash-100 backdrop-blur">
                    {title}
                </div>
                <div className="rounded-full border border-toxic-green-DEFAULT/25 bg-toxic-green-DEFAULT/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.28em] text-toxic-green-bright backdrop-blur">
                    Trailer
                </div>
            </div>

            <div className="absolute bottom-3 left-3 right-3 z-20 flex flex-wrap gap-2 sm:bottom-4 sm:left-4 sm:right-4">
                <button
                    type="button"
                    onClick={() => void handleTogglePlayback()}
                    className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/65 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.28em] text-ash-100 backdrop-blur transition hover:border-white/30 hover:bg-black/80"
                >
                    {isPlaying ? <Pause size={13} /> : <Play size={13} />}
                    {isPlaying ? "Pause" : "Play"}
                </button>
                <button
                    type="button"
                    onClick={handleToggleMuted}
                    className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/65 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.28em] text-ash-100 backdrop-blur transition hover:border-white/30 hover:bg-black/80"
                >
                    {isMuted ? <VolumeX size={13} /> : <Volume2 size={13} />}
                    {isMuted ? "Muted" : "Sound"}
                </button>
            </div>
        </div>
    );
}
