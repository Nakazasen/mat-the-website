"use client";

import { Music4, Pause, Play, Volume2, VolumeX, ChevronDown, ChevronUp, Repeat, ListMusic } from "lucide-react";
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
const BGM_PLAY_MODE_STORAGE_KEY = "reader-bgm-play-mode-v1";

const PRESET_ZOMBIE_PLAYLIST = [
    {
        title: "Dark Cello / Ambient Tension",
        url: "https://pub-7b84345562bb41c6acf9cda324d194f8.r2.dev/bgm/20260331_5b1d8133_bgm_817_optimized_64k.mp3"
    },
    {
        title: "The Descent / Deep Cello Tension",
        url: "https://pub-7b84345562bb41c6acf9cda324d194f8.r2.dev/bgm/20260531_2bb03743_the_descent___deep_cello_tension.mp3"
    },
    {
        title: "Unseen Horrors / Creepy Scraping",
        url: "https://pub-7b84345562bb41c6acf9cda324d194f8.r2.dev/bgm/20260531_f707249c_unseen_horrors___creepy_scraping.mp3"
    },
    {
        title: "Anxiety / High String Tension",
        url: "https://pub-7b84345562bb41c6acf9cda324d194f8.r2.dev/bgm/20260531_4f8f64c8_anxiety___high_string_tension.mp3"
    },
    {
        title: "Phantasm / Melancholic Suspense",
        url: "https://pub-7b84345562bb41c6acf9cda324d194f8.r2.dev/bgm/20260531_39e2db0b_phantasm___melancholic_suspense.mp3"
    }
];

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
    playlist: string;
    mode: string;
    loopSingle: string;
    playPlaylist: string;
}> = {
    vi: {
        panel: "Nhạc nền mạt thế",
        titleFallback: "Ambient chapter",
        play: "Bật",
        pause: "Tắt",
        mute: "Tắt tiếng",
        unmute: "Mở tiếng",
        volume: "Âm lượng",
        chapter: "Chương",
        hint: "Opt-in. Chỉ tải khi bạn bật.",
        playlist: "Danh sách phát",
        mode: "Chế độ",
        loopSingle: "Lặp 1 bài",
        playPlaylist: "Phát Playlist",
    },
    en: {
        panel: "Ambient Music",
        titleFallback: "Chapter ambient",
        play: "Play",
        pause: "Stop",
        mute: "Mute",
        unmute: "Unmute",
        volume: "Volume",
        chapter: "Chapter",
        hint: "Opt-in. Loads only after you start it.",
        playlist: "Playlist",
        mode: "Mode",
        loopSingle: "Loop Track",
        playPlaylist: "Play Playlist",
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
        playlist: "プレイリスト",
        mode: "モード",
        loopSingle: "1曲ループ",
        playPlaylist: "順次再生",
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
        playlist: "播放列表",
        mode: "模式",
        loopSingle: "单曲循环",
        playPlaylist: "顺序播放",
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
    
    // Playlist states
    const [playMode, setPlayMode] = useState<'loop' | 'playlist'>('playlist');
    const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
    const [isPlaylistExpanded, setIsPlaylistExpanded] = useState(false);

    const labels = useMemo(() => resolveLabels(locale), [locale]);

    // Build the dynamic playlist: Chapter BGM at front if unique, else use the preset 5
    const playlist = useMemo(() => {
        const base = [...PRESET_ZOMBIE_PLAYLIST];
        const normUrl = (bgmUrl || "").trim();
        const normTitle = (bgmTitle || "").trim() || "Ambient chapter";
        if (normUrl && !base.some(t => t.url === normUrl)) {
            // Uniquely uploaded BGM for this chapter - add to front
            base.unshift({ title: normTitle, url: normUrl });
        }
        return base;
    }, [bgmUrl, bgmTitle]);

    const activeTrack = playlist[currentTrackIndex] || playlist[0] || { title: bgmTitle, url: bgmUrl };
    const normalizedUrl = (activeTrack?.url || "").trim();
    const activeTitle = activeTrack?.title || bgmTitle || "Ambient chapter";

    // Load configurations from storage
    useEffect(() => {
        try {
            const savedEnabled = window.localStorage.getItem(BGM_ENABLED_STORAGE_KEY);
            const savedMuted = window.localStorage.getItem(BGM_MUTED_STORAGE_KEY);
            const savedVolume = window.localStorage.getItem(BGM_VOLUME_STORAGE_KEY);
            const savedPlayMode = window.localStorage.getItem(BGM_PLAY_MODE_STORAGE_KEY);

            setEnabled(savedEnabled === "1");
            setIsMuted(savedMuted === "1");

            const parsedVolume = Number.parseFloat(savedVolume || "");
            if (Number.isFinite(parsedVolume)) {
                setVolume(Math.min(1, Math.max(0, parsedVolume)));
            }

            if (savedPlayMode === "loop" || savedPlayMode === "playlist") {
                setPlayMode(savedPlayMode);
            }
        } catch {
            // ignore storage issues
        }
    }, []);

    // Sync playMode and indices when bgmUrl changes
    useEffect(() => {
        const normUrl = (bgmUrl || "").trim();
        const foundIndex = playlist.findIndex(t => t.url === normUrl);
        if (foundIndex !== -1) {
            setCurrentTrackIndex(foundIndex);
        } else {
            setCurrentTrackIndex(0);
        }
    }, [bgmUrl, playlist]);

    useEffect(() => {
        try {
            window.localStorage.setItem(BGM_ENABLED_STORAGE_KEY, enabled ? "1" : "0");
        } catch {}
    }, [enabled]);

    useEffect(() => {
        try {
            window.localStorage.setItem(BGM_MUTED_STORAGE_KEY, isMuted ? "1" : "0");
        } catch {}
    }, [isMuted]);

    useEffect(() => {
        try {
            window.localStorage.setItem(BGM_VOLUME_STORAGE_KEY, volume.toFixed(2));
        } catch {}
    }, [volume]);

    useEffect(() => {
        try {
            window.localStorage.setItem(BGM_PLAY_MODE_STORAGE_KEY, playMode);
        } catch {}
    }, [playMode]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        audio.muted = isMuted;
        audio.volume = isMuted ? 0 : Math.min(1, Math.max(0, ducked ? volume * 0.22 : volume));
    }, [ducked, isMuted, volume]);

    // Keep fresh refs for the event listener to avoid stale closures
    const playModeRef = useRef(playMode);
    const currentTrackIndexRef = useRef(currentTrackIndex);
    const playlistRef = useRef(playlist);
    const enabledRef = useRef(enabled);

    useEffect(() => { playModeRef.current = playMode; }, [playMode]);
    useEffect(() => { currentTrackIndexRef.current = currentTrackIndex; }, [currentTrackIndex]);
    useEffect(() => { playlistRef.current = playlist; }, [playlist]);
    useEffect(() => { enabledRef.current = enabled; }, [enabled]);

    // Sync audio playing status
    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const syncPlay = () => setIsPlaying(true);
        const syncPause = () => setIsPlaying(false);
        const syncEnded = () => {
            if (playModeRef.current === 'playlist') {
                // Move to next track in playlist sequentially
                const nextIndex = (currentTrackIndexRef.current + 1) % playlistRef.current.length;
                setCurrentTrackIndex(nextIndex);
                
                // Play next track
                setTimeout(() => {
                    const aud = audioRef.current;
                    if (aud && enabledRef.current) {
                        aud.pause();
                        aud.src = playlistRef.current[nextIndex].url;
                        aud.load();
                        aud.play().catch(() => {});
                    }
                }, 50);
            } else {
                setIsPlaying(false);
            }
        };

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

    // Trigger audio source changes
    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        audio.pause();
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

    const handleSelectTrack = (index: number) => {
        setCurrentTrackIndex(index);
        setEnabled(true);
        
        setTimeout(() => {
            const audio = audioRef.current;
            if (audio) {
                audio.pause();
                audio.src = playlist[index].url;
                audio.load();
                audio.play().catch(() => {});
            }
        }, 50);
    };

    return (
        <div className="mt-5 rounded-2xl border border-white/8 bg-black/45 p-4 text-left shadow-[0_18px_40px_rgba(0,0,0,0.3)] backdrop-blur-md transition-all duration-300">
            <audio ref={audioRef} preload="none" loop={playMode === 'loop'} className="hidden" />

            {/* Top row: Info & Primary Controls */}
            <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                        <Music4 size={14} className="shrink-0 text-toxic-green-DEFAULT animate-pulse" />
                        <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-toxic-green-DEFAULT">{labels.panel}</span>
                    </div>
                    <div className="mt-2 truncate font-biohazard text-lg tracking-[0.05em] text-worn-white" title={activeTitle}>
                        {activeTitle}
                    </div>
                    <div className="mt-1 text-[11px] font-mono uppercase tracking-[0.18em] text-ash-500">
                        {labels.chapter} {chapterNumber} • {labels.hint}
                    </div>
                </div>

                <div className="flex flex-col items-end gap-2 shrink-0">
                    <button
                        type="button"
                        onClick={() => void handleTogglePlayback()}
                        className="inline-flex shrink-0 items-center gap-2 rounded-full border border-toxic-green-DEFAULT/35 bg-toxic-green-DEFAULT/10 px-4 py-2 font-mono text-[10px] uppercase tracking-[0.2em] text-toxic-green-DEFAULT transition hover:bg-toxic-green-DEFAULT/20 active:scale-95"
                    >
                        {enabled && isPlaying ? <Pause size={13} /> : <Play size={13} fill="currentColor" />}
                        <span>{enabled && isPlaying ? labels.pause : labels.play}</span>
                    </button>
                </div>
            </div>

            {/* Second row: Mode Toggle & Collapsible Playlist Toggler */}
            <div className="mt-4 flex items-center justify-between border-t border-white/5 pt-3">
                {/* Playback Mode */}
                <div className="flex items-center gap-2">
                    <span className="font-mono text-[9px] uppercase tracking-[0.18em] text-ash-500">{labels.mode}:</span>
                    <button
                        type="button"
                        onClick={() => setPlayMode(playMode === 'loop' ? 'playlist' : 'loop')}
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[9px] font-mono uppercase border transition-colors ${
                            playMode === 'playlist'
                                ? 'border-toxic-green-DEFAULT/30 bg-toxic-green-DEFAULT/5 text-toxic-green-DEFAULT'
                                : 'border-white/10 bg-black/20 text-ash-300'
                        }`}
                        title={playMode === 'loop' ? labels.loopSingle : labels.playPlaylist}
                    >
                        {playMode === 'loop' ? <Repeat size={10} /> : <ListMusic size={10} />}
                        <span>{playMode === 'loop' ? labels.loopSingle : labels.playPlaylist}</span>
                    </button>
                </div>

                {/* Playlist Expand Button */}
                <button
                    type="button"
                    onClick={() => setIsPlaylistExpanded(!isPlaylistExpanded)}
                    className="inline-flex items-center gap-1 font-mono text-[10px] text-ash-400 hover:text-white transition-colors"
                >
                    <span>{labels.playlist} ({playlist.length})</span>
                    {isPlaylistExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                </button>
            </div>

            {/* Playlist Collapsible Container */}
            {isPlaylistExpanded && (
                <div className="mt-3 border-t border-white/5 pt-3 max-h-[160px] overflow-y-auto pr-1 space-y-1.5 scrollbar-thin scrollbar-thumb-white/10">
                    {playlist.map((track, index) => {
                        const isCurrent = currentTrackIndex === index;
                        return (
                            <div
                                key={index}
                                onClick={() => handleSelectTrack(index)}
                                className={`flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-all duration-200 ${
                                    isCurrent
                                        ? 'bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/25 text-toxic-green-DEFAULT'
                                        : 'bg-black/20 border border-transparent text-ash-400 hover:bg-black/40 hover:text-worn-white'
                                }`}
                            >
                                <div className="flex items-center gap-2 min-w-0">
                                    <span className="font-mono text-[9px] opacity-50">{index + 1}.</span>
                                    <span className="font-mono text-[11px] truncate">{track.title}</span>
                                </div>
                                <div className="shrink-0 flex items-center gap-1.5 font-mono text-[9px] uppercase tracking-wider pl-2">
                                    {isCurrent && isPlaying ? (
                                        <span className="w-1.5 h-1.5 bg-toxic-green-DEFAULT rounded-full animate-ping" />
                                    ) : null}
                                    <span className="opacity-65">
                                        {track.url === bgmUrl ? "Default BGM" : `Track ${index}`}
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Bottom row: Mute & Volume slider */}
            <div className="mt-4 flex items-center gap-3 border-t border-white/5 pt-3">
                <button
                    type="button"
                    onClick={() => setIsMuted((current) => !current)}
                    className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/10 bg-black/28 text-ash-300 transition hover:border-white/18 hover:text-white active:scale-95"
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
                        className="h-1.5 w-full cursor-pointer accent-toxic-green-DEFAULT bg-white/10 rounded-full appearance-none"
                    />
                </div>
            </div>
        </div>
    );
}
