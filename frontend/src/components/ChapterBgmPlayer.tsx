"use client";

import { Music4, Pause, Play, Volume2, VolumeX } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

type SupportedLocale = "vi" | "en" | "ja" | "zh-CN";

interface ChapterBgmPlayerProps {
    chapterNumber: number;
    locale: string;
    bgmUrl?: string | null;
    bgmTitle?: string | null;
}

const BGM_ENABLED_STORAGE_KEY = "reader-bgm-enabled-v1";
const BGM_VOLUME_STORAGE_KEY = "reader-bgm-volume-v1";
const BGM_MUTED_STORAGE_KEY = "reader-bgm-muted-v1";

const LABELS: Record<SupportedLocale, {
    panel: string;
    titleFallback: string;
    play: string;
    pause: string;
    mute: string;
    unmute: string;
    volume: string;
    chapter: string;
    hint: string;
}> = {
    vi: {
        panel: "Nhạc nền",
        titleFallback: "Ambient chapter",
        play: "Bật",
        pause: "Tắt",
        mute: "Tắt tiếng",
        unmute: "Mở tiếng",
        volume: "Âm lượng",
        chapter: "Chương",
        hint: "Opt-in. Chỉ tải khi bạn bật.",
    },
    en: {
        panel: "Background music",
        titleFallback: "Chapter ambient",
        play: "Play",
        pause: "Stop",
        mute: "Mute",
        unmute: "Unmute",
        volume: "Volume",
        chapter: "Chapter",
        hint: "Opt-in. Loads only after you start it.",
    },
    ja: {
        panel: "BGM",
        titleFallback: "チャプターBGM",
        play: "再生",
        pause: "停止",
        mute: "消音",
        unmute: "消音解除",
        volume: "音量",
        chapter: "章",
        hint: "オプトイン。再生するまで読み込みません。",
    },
    "zh-CN": {
        panel: "背景音乐",
        titleFallback: "章节氛围曲",
        play: "播放",
        pause: "停止",
        mute: "静音",
        unmute: "取消静音",
        volume: "音量",
        chapter: "章节",
        hint: "默认不加载，点击后才会播放。",
    },
};

function resolveLabels(locale: string) {
    if (locale === "ja" || locale === "zh-CN" || locale === "en" || locale === "vi") {
        return LABELS[locale];
    }
    return LABELS.vi;
}

export default function ChapterBgmPlayer({
    chapterNumber,
    locale,
    bgmUrl,
    bgmTitle,
}: ChapterBgmPlayerProps) {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [enabled, setEnabled] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [volume, setVolume] = useState(0.32);
    const [ducked, setDucked] = useState(false);

    const labels = useMemo(() => resolveLabels(locale), [locale]);
    const normalizedUrl = (bgmUrl || "").trim();

    useEffect(() => {
        try {
            const savedEnabled = window.localStorage.getItem(BGM_ENABLED_STORAGE_KEY);
            const savedMuted = window.localStorage.getItem(BGM_MUTED_STORAGE_KEY);
            const savedVolume = window.localStorage.getItem(BGM_VOLUME_STORAGE_KEY);

            setEnabled(savedEnabled === "1");
            setIsMuted(savedMuted === "1");

            const parsedVolume = Number.parseFloat(savedVolume || "");
            if (Number.isFinite(parsedVolume)) {
                setVolume(Math.min(1, Math.max(0, parsedVolume)));
            }
        } catch {
            // ignore storage issues
        }
    }, []);

    useEffect(() => {
        try {
            window.localStorage.setItem(BGM_ENABLED_STORAGE_KEY, enabled ? "1" : "0");
        } catch {
            // ignore storage issues
        }
    }, [enabled]);

    useEffect(() => {
        try {
            window.localStorage.setItem(BGM_MUTED_STORAGE_KEY, isMuted ? "1" : "0");
        } catch {
            // ignore storage issues
        }
    }, [isMuted]);

    useEffect(() => {
        try {
            window.localStorage.setItem(BGM_VOLUME_STORAGE_KEY, volume.toFixed(2));
        } catch {
            // ignore storage issues
        }
    }, [volume]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        audio.muted = isMuted;
        audio.volume = isMuted ? 0 : Math.min(1, Math.max(0, ducked ? volume * 0.22 : volume));
    }, [ducked, isMuted, volume]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const syncPlay = () => setIsPlaying(true);
        const syncPause = () => setIsPlaying(false);
        const syncEnded = () => setIsPlaying(false);

        audio.addEventListener("play", syncPlay);
        audio.addEventListener("pause", syncPause);
        audio.addEventListener("ended", syncEnded);

        return () => {
            audio.removeEventListener("play", syncPlay);
            audio.removeEventListener("pause", syncPause);
            audio.removeEventListener("ended", syncEnded);
        };
    }, []);

    useEffect(() => {
        const handleReaderAudioState = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean }>).detail;
            setDucked(Boolean(detail?.active));
        };

        window.addEventListener("reader-audio-state", handleReaderAudioState as EventListener);
        return () => window.removeEventListener("reader-audio-state", handleReaderAudioState as EventListener);
    }, []);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        audio.pause();
        audio.currentTime = 0;
        setIsPlaying(false);

        if (!normalizedUrl) {
            audio.removeAttribute("src");
            audio.load();
            return;
        }

        audio.src = normalizedUrl;
        audio.load();

        if (!enabled) return;

        void audio.play().catch(() => {
            setIsPlaying(false);
        });
    }, [chapterNumber, enabled, normalizedUrl]);

    useEffect(() => {
        return () => {
            audioRef.current?.pause();
        };
    }, []);

    if (!normalizedUrl) return null;

    const handleTogglePlayback = async () => {
        const audio = audioRef.current;
        if (!audio) return;

        if (enabled && !audio.paused) {
            audio.pause();
            audio.currentTime = 0;
            setEnabled(false);
            return;
        }

        setEnabled(true);
        if (audio.src !== normalizedUrl) {
            audio.src = normalizedUrl;
            audio.load();
        }

        try {
            await audio.play();
        } catch {
            setIsPlaying(false);
        }
    };

    return (
        <div className="mt-5 rounded-2xl border border-white/8 bg-black/35 p-4 text-left shadow-[0_18px_40px_rgba(0,0,0,0.24)] backdrop-blur-md">
            <audio ref={audioRef} preload="none" loop className="hidden" />

            <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                    <div className="flex items-center gap-2">
                        <Music4 size={14} className="shrink-0 text-toxic-green-DEFAULT" />
                        <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-toxic-green-DEFAULT">{labels.panel}</span>
                    </div>
                    <div className="mt-2 truncate font-biohazard text-lg tracking-[0.05em] text-worn-white">
                        {bgmTitle?.trim() || labels.titleFallback}
                    </div>
                    <div className="mt-1 text-[11px] font-mono uppercase tracking-[0.18em] text-ash-500">
                        {labels.chapter} {chapterNumber} • {labels.hint}
                    </div>
                </div>

                <button
                    type="button"
                    onClick={() => void handleTogglePlayback()}
                    className="inline-flex shrink-0 items-center gap-2 rounded-full border border-toxic-green-DEFAULT/35 bg-toxic-green-DEFAULT/10 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.2em] text-toxic-green-DEFAULT transition hover:bg-toxic-green-DEFAULT/18"
                >
                    {enabled && isPlaying ? <Pause size={13} /> : <Play size={13} fill="currentColor" />}
                    <span>{enabled && isPlaying ? labels.pause : labels.play}</span>
                </button>
            </div>

            <div className="mt-4 flex items-center gap-3">
                <button
                    type="button"
                    onClick={() => setIsMuted((current) => !current)}
                    className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/10 bg-black/28 text-ash-300 transition hover:border-white/18 hover:text-white"
                    title={isMuted ? labels.unmute : labels.mute}
                >
                    {isMuted ? <VolumeX size={15} /> : <Volume2 size={15} />}
                </button>
                <div className="flex min-w-0 flex-1 items-center gap-3">
                    <span className="shrink-0 font-mono text-[10px] uppercase tracking-[0.18em] text-ash-500">{labels.volume}</span>
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={volume}
                        onChange={(event) => setVolume(Number.parseFloat(event.target.value))}
                        className="h-1.5 w-full cursor-pointer accent-toxic-green-DEFAULT"
                    />
                </div>
            </div>
        </div>
    );
}
