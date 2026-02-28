'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { Play, Pause, Square, Volume2, VolumeX, ChevronLeft, ChevronRight } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Script from 'next/script';

interface AudioPlayerProps {
    content: string;
    chapterTitle: string;
    chapterNumber: number;
    prevId: number | null;
    nextId: number | null;
}

type PlayState = 'stopped' | 'playing' | 'paused';

// ResponsiveVoice type stub
interface ResponsiveVoice {
    speak: (text: string, voice: string, options?: {
        rate?: number;
        pitch?: number;
        volume?: number;
        onstart?: () => void;
        onend?: () => void;
        onerror?: () => void;
        onpause?: () => void;
        onresume?: () => void;
    }) => void;
    pause: () => void;
    resume: () => void;
    cancel: () => void;
    isPlaying: () => boolean;
    voiceSupport: () => boolean;
}

declare global {
    interface Window {
        responsiveVoice?: ResponsiveVoice;
    }
}

export default function AudioPlayer({
    content,
    chapterTitle,
    chapterNumber,
    prevId,
    nextId,
}: AudioPlayerProps) {
    const router = useRouter();
    const [playState, setPlayState] = useState<PlayState>('stopped');
    const [speed, setSpeed] = useState(1);
    const [isMuted, setIsMuted] = useState(false);
    const [rvLoaded, setRvLoaded] = useState(false);
    const [rvError, setRvError] = useState(false);
    const textRef = useRef<string>('');

    useEffect(() => {
        textRef.current = `Chương ${chapterNumber}: ${chapterTitle}. ${content}`;
    }, [content, chapterTitle, chapterNumber]);

    // Poll cho đến khi ResponsiveVoice sẵn sàng
    useEffect(() => {
        let attempts = 0;
        const check = setInterval(() => {
            attempts++;
            if (window.responsiveVoice) {
                setRvLoaded(true);
                clearInterval(check);
            } else if (attempts > 150) { // 15s timeout
                setRvError(true);
                clearInterval(check);
            }
        }, 100);
        return () => clearInterval(check);
    }, []);

    // Stop on unmount
    useEffect(() => {
        return () => {
            window.responsiveVoice?.cancel();
        };
    }, []);

    const setupMediaSession = useCallback(() => {
        if (!('mediaSession' in navigator)) return;
        navigator.mediaSession.metadata = new MediaMetadata({
            title: `Chương ${chapterNumber}: ${chapterTitle}`,
            artist: 'Mạt Thế - Sinh Hoá Nguy Cơ ☣️',
            album: 'Nghe truyện',
        });
        navigator.mediaSession.setActionHandler('pause', () => {
            window.responsiveVoice?.pause();
            setPlayState('paused');
            navigator.mediaSession.playbackState = 'paused';
        });
        navigator.mediaSession.setActionHandler('play', () => {
            window.responsiveVoice?.resume();
            setPlayState('playing');
            navigator.mediaSession.playbackState = 'playing';
        });
        navigator.mediaSession.setActionHandler('previoustrack', () => {
            if (prevId) { window.responsiveVoice?.cancel(); router.push(`/chapters/${prevId}`); }
        });
        navigator.mediaSession.setActionHandler('nexttrack', () => {
            if (nextId) { window.responsiveVoice?.cancel(); router.push(`/chapters/${nextId}`); }
        });
        navigator.mediaSession.playbackState = 'playing';
    }, [chapterNumber, chapterTitle, prevId, nextId, router]);

    const stop = useCallback(() => {
        window.responsiveVoice?.cancel();
        setPlayState('stopped');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
    }, []);

    const play = useCallback(() => {
        if (!window.responsiveVoice) return;
        window.responsiveVoice.cancel();

        window.responsiveVoice.speak(textRef.current, 'Vietnamese Female', {
            rate: speed,
            volume: isMuted ? 0 : 1,
            pitch: 1,
            onstart: () => {
                setPlayState('playing');
                setupMediaSession();
            },
            onend: () => {
                setPlayState('stopped');
                if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
                if (nextId) setTimeout(() => router.push(`/chapters/${nextId}`), 500);
            },
            onerror: () => setPlayState('stopped'),
        });
    }, [speed, isMuted, setupMediaSession, nextId, router]);

    const pause = useCallback(() => {
        window.responsiveVoice?.pause();
        setPlayState('paused');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'paused';
    }, []);

    const resume = useCallback(() => {
        window.responsiveVoice?.resume();
        setPlayState('playing');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'playing';
    }, []);

    const changeSpeed = (s: number) => {
        setSpeed(s);
        if (playState !== 'stopped') stop();
    };

    return (
        <>
            {/* Load ResponsiveVoice CDN */}
            <Script
                src="https://code.responsivevoice.org/responsivevoice.js?key=FREE"
                strategy="afterInteractive"
            />

            <div className="mt-6 rounded-lg border border-toxic-green-DEFAULT/20 bg-[#141414] p-4 text-gray-200">
                {/* Header */}
                <div className="flex items-center gap-2 mb-3 pb-3 border-b border-ash-800">
                    <Volume2 size={14} className="text-toxic-green-DEFAULT" />
                    <span className="text-[10px] font-mono text-toxic-green-DEFAULT tracking-[0.2em] uppercase">
                        Nghe Truyện
                    </span>
                    <span className="text-[10px] font-mono text-gray-500 ml-auto">
                        {rvError && '❌ Không load được thư viện'}
                        {!rvError && !rvLoaded && '⏳ Đang tải...'}
                        {rvLoaded && playState === 'playing' && '▶ Đang đọc...'}
                        {rvLoaded && playState === 'paused' && '⏸ Tạm dừng'}
                        {rvLoaded && playState === 'stopped' && '■ Dừng'}
                    </span>
                </div>

                {/* Error / Play button disabled when not loaded */}
                {rvError && (
                    <div className="mb-3 px-3 py-2 rounded border border-red-600/40 bg-red-900/20 text-red-400 text-[10px] font-mono">
                        ❌ Không tải được thư viện giọng đọc. Vui lòng thử tắt VPN hoặc reload trang.
                    </div>
                )}

                {/* Controls */}
                <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-2">
                        {playState === 'stopped' && (
                            <button
                                onClick={play}
                                disabled={!rvLoaded}
                                className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 hover:border-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm disabled:opacity-40 disabled:cursor-wait"
                            >
                                <Play size={15} fill="currentColor" />
                                <span>PHÁT</span>
                            </button>
                        )}
                        {playState === 'playing' && (
                            <button
                                onClick={pause}
                                className="flex items-center gap-2 px-4 py-2 bg-[#252525] border border-gray-700 rounded-lg text-gray-200 hover:border-toxic-green-DEFAULT hover:text-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm"
                            >
                                <Pause size={15} fill="currentColor" />
                                <span>DỪNG</span>
                            </button>
                        )}
                        {playState === 'paused' && (
                            <button
                                onClick={resume}
                                className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 transition-all font-biohazard tracking-widest text-sm"
                            >
                                <Play size={15} fill="currentColor" />
                                <span>TIẾP</span>
                            </button>
                        )}
                        {playState !== 'stopped' && (
                            <button
                                onClick={stop}
                                className="p-2 border border-gray-700 rounded-lg text-gray-400 hover:border-red-500 hover:text-red-400 transition-all"
                            >
                                <Square size={15} fill="currentColor" />
                            </button>
                        )}
                    </div>

                    <div className="w-px h-8 bg-gray-800" />

                    {/* Speed */}
                    <div className="flex items-center gap-1">
                        {[0.75, 1, 1.25, 1.5, 1.75].map((s) => (
                            <button
                                key={s}
                                onClick={() => changeSpeed(s)}
                                className={`px-2 py-1 rounded text-[10px] font-mono transition-all ${speed === s
                                    ? 'bg-toxic-green-DEFAULT text-black font-bold'
                                    : 'text-gray-500 hover:text-gray-200'
                                    }`}
                            >
                                {s}x
                            </button>
                        ))}
                    </div>

                    {/* Mute */}
                    <button
                        onClick={() => setIsMuted(!isMuted)}
                        className="ml-auto p-2 text-gray-500 hover:text-gray-200 transition-colors"
                    >
                        {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                    </button>
                </div>

                {/* Chapter nav (when playing) */}
                {playState !== 'stopped' && (
                    <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-800">
                        <span className="text-[10px] font-mono text-gray-600">Chuyển chương:</span>
                        {prevId && (
                            <button
                                onClick={() => { stop(); router.push(`/chapters/${prevId}`); }}
                                className="flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-toxic-green-DEFAULT transition-colors"
                            >
                                <ChevronLeft size={12} /> Trước
                            </button>
                        )}
                        {nextId && (
                            <button
                                onClick={() => { stop(); router.push(`/chapters/${nextId}`); }}
                                className="flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-toxic-green-DEFAULT transition-colors"
                            >
                                Tiếp <ChevronRight size={12} />
                            </button>
                        )}
                        <span className="ml-auto text-[10px] font-mono text-gray-600 animate-pulse">
                            💡 Tắt màn hình vẫn nghe được
                        </span>
                    </div>
                )}
            </div>
        </>
    );
}
