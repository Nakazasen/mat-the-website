"use client";

import { Pause, Play, Volume2, VolumeX } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface HomepageHeroVideoProps {
    title: string;
    subtitle: string;
    src: string;
    poster: string;
}

export default function HomepageHeroVideo({ title, subtitle, src, poster }: HomepageHeroVideoProps) {
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
        <div className="group relative overflow-hidden rounded-[28px] border border-toxic-green-DEFAULT/30 bg-ash-950/75 shadow-[0_0_90px_rgba(57,255,20,0.14)] backdrop-blur">
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(57,255,20,0.18),transparent_34%),radial-gradient(circle_at_bottom_left,rgba(185,0,0,0.18),transparent_28%)]" />
            <div className="pointer-events-none absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(57,255,20,0.08)_1px,transparent_1px)] [background-size:100%_6px]" />
            <div className="relative border-b border-toxic-green-DEFAULT/15 px-5 py-4">
                <div className="flex items-center justify-between gap-4">
                    <div>
                        <div className="font-mono text-[10px] uppercase tracking-[0.35em] text-toxic-green-DEFAULT/80">
                            Character Spotlight
                        </div>
                        <h3 className="mt-2 font-biohazard text-2xl tracking-[0.18em] text-worn-white">
                            {title}
                        </h3>
                    </div>
                    <div className="rounded-full border border-toxic-green-DEFAULT/25 bg-toxic-green-DEFAULT/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.28em] text-toxic-green-bright">
                        Trailer Feed
                    </div>
                </div>
                <p className="mt-3 max-w-xl font-reading text-sm leading-relaxed text-ash-300">
                    {subtitle}
                </p>
            </div>

            <div className="relative">
                <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-24 bg-gradient-to-b from-black/65 to-transparent" />
                <div className="pointer-events-none absolute inset-0 z-10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),transparent_26%,rgba(57,255,20,0.10))]" />
                <div className="pointer-events-none absolute inset-0 z-10 shadow-[inset_0_0_0_1px_rgba(57,255,20,0.14),inset_0_0_60px_rgba(57,255,20,0.08)]" />
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

                <div className="absolute left-4 top-4 z-20 flex flex-wrap gap-2">
                    <button
                        type="button"
                        onClick={() => void handleTogglePlayback()}
                        className="inline-flex items-center gap-2 rounded-full border border-toxic-green-DEFAULT/30 bg-black/60 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-toxic-green-bright backdrop-blur transition hover:border-toxic-green-DEFAULT/60 hover:bg-black/80"
                    >
                        {isPlaying ? <Pause size={14} /> : <Play size={14} />}
                        {isPlaying ? "Pause Trailer" : "Play Trailer"}
                    </button>
                    <button
                        type="button"
                        onClick={handleToggleMuted}
                        className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/55 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-ash-100 backdrop-blur transition hover:border-white/30 hover:bg-black/75"
                    >
                        {isMuted ? <VolumeX size={14} /> : <Volume2 size={14} />}
                        {isMuted ? "Muted" : "Sound On"}
                    </button>
                </div>

                <div className="absolute inset-x-4 bottom-4 z-20 rounded-2xl border border-white/10 bg-black/60 px-4 py-3 backdrop-blur-sm">
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <div className="font-mono text-[10px] uppercase tracking-[0.35em] text-toxic-green-DEFAULT">
                                Main Character Intro
                            </div>
                            <div className="mt-1 font-reading text-sm leading-relaxed text-ash-100">
                                Trailer giới thiệu Hàn Phong được đặt như một điểm nhấn cinematic thay cho việc dàn trải nhiều video ngay ở màn hình đầu.
                            </div>
                        </div>
                        <div className="hidden rounded-full border border-blood-red-DEFAULT/20 bg-blood-red-DEFAULT/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.3em] text-blood-red-bright sm:block">
                            8s Cut
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
