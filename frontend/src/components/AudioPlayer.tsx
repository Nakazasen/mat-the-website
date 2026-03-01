'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { ChevronLeft, ChevronRight, Pause, Play, Square, Volume2, VolumeX } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { splitIntoChunks } from '@/lib/tts-utils';

interface AudioPlayerProps {
    content: string;
    chapterTitle: string;
    chapterNumber: number;
    prevId: number | null;
    nextId: number | null;
    onIndexChange?: (index: number | null) => void;
}

type PlayState = 'stopped' | 'playing' | 'paused';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-api.onrender.com';

function ttsUrl(text: string, speed: number): string {
    return `${API_URL}/api/tts?lang=vi&speed=${speed}&text=${encodeURIComponent(text)}`;
}

export default function AudioPlayer({
    content,
    chapterTitle,
    chapterNumber,
    prevId,
    nextId,
    onIndexChange,
}: AudioPlayerProps) {
    const router = useRouter();
    const [playState, setPlayState] = useState<PlayState>('stopped');
    const [speed, setSpeed] = useState(1);
    const [isMuted, setIsMuted] = useState(false);

    const audioRef = useRef<HTMLAudioElement>(null);
    const chunksRef = useRef<string[]>([]);
    const chunkIndexRef = useRef(0);
    const speedRef = useRef(speed);
    const stoppedRef = useRef(true);
    const wakeLockRef = useRef<any>(null);

    useEffect(() => {
        speedRef.current = speed;
        if (audioRef.current) {
            audioRef.current.playbackRate = speed;
        }
    }, [speed]);

    useEffect(() => {
        // Chỉ chunk nội dung chính để Karaoke khớp với text hiển thị
        // Phần Tiêu đề sẽ được đọc riêng hoặc bỏ qua trong highlight
        chunksRef.current = splitIntoChunks(content);
    }, [content]);

    useEffect(() => {
        if (audioRef.current) audioRef.current.muted = isMuted;
    }, [isMuted]);

    useEffect(() => {
        return () => {
            stoppedRef.current = true;
            if (onIndexChange) onIndexChange(null);
        };
    }, [onIndexChange]);

    const updateMetadata = useCallback(() => {
        if (!('mediaSession' in navigator)) return;

        navigator.mediaSession.metadata = new MediaMetadata({
            title: `Chương ${chapterNumber}`,
            artist: chapterTitle,
            album: 'Mạt Thế - Sinh Hoá Nguy Cơ ☣️',
            artwork: [
                { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
                { src: '/icon-192.png', sizes: '192x192', type: 'image/png' }
            ]
        });
    }, [chapterNumber, chapterTitle]);

    const setupMediaSession = useCallback(() => {
        if (!('mediaSession' in navigator)) return;

        updateMetadata();

        const actionHandlers: [MediaSessionAction, MediaSessionActionHandler][] = [
            ['play', () => { audioRef.current?.play(); }],
            ['pause', () => { audioRef.current?.pause(); }],
            ['previoustrack', () => { if (prevId) { stop(); router.push(`/chapters/${prevId}`); } }],
            ['nexttrack', () => { if (nextId) { stop(); router.push(`/chapters/${nextId}`); } }]
        ];

        for (const [action, handler] of actionHandlers) {
            try {
                navigator.mediaSession.setActionHandler(action, handler);
            } catch (error) {
                console.log(`Action ${action} not supported.`);
            }
        }
    }, [prevId, nextId, router, updateMetadata]);

    const playChunk = useCallback((index: number) => {
        if (stoppedRef.current) return;
        const audio = audioRef.current;
        if (!audio) return;

        if (index >= chunksRef.current.length) {
            stop();
            if (nextId) setTimeout(() => router.push(`/chapters/${nextId}`), 1000);
            return;
        }

        chunkIndexRef.current = index;
        if (onIndexChange) onIndexChange(index);

        const url = ttsUrl(chunksRef.current[index], speedRef.current);

        // Cố gắng không gán src nếu nó giống hệt (tránh flicker session)
        if (audio.src !== url) {
            audio.src = url;
            audio.load();
        }

        audio.play().then(() => {
            audio.playbackRate = speedRef.current;
        }).catch(e => {
            console.error("Playback failed", e);
            if (!stoppedRef.current) playChunk(index + 1);
        });
    }, [nextId, router, onIndexChange]);

    const requestWakeLock = useCallback(async () => {
        if ('wakeLock' in navigator) {
            try {
                wakeLockRef.current = await (navigator as any).wakeLock.request('screen');
            } catch (err) {
                console.error(`Wake Lock error: ${err}`);
            }
        }
    }, []);

    const releaseWakeLock = useCallback(() => {
        if (wakeLockRef.current) {
            wakeLockRef.current.release();
            wakeLockRef.current = null;
        }
    }, []);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const syncPlaying = () => {
            if ('mediaSession' in navigator) {
                navigator.mediaSession.playbackState = 'playing';
            }
            setPlayState('playing');
        };

        const syncPaused = () => {
            if ('mediaSession' in navigator) {
                navigator.mediaSession.playbackState = 'paused';
            }
            setPlayState('paused');
        };

        const handleEnded = () => {
            if (!stoppedRef.current) {
                playChunk(chunkIndexRef.current + 1);
            }
        };

        audio.addEventListener('play', syncPlaying);
        audio.addEventListener('playing', syncPlaying);
        audio.addEventListener('pause', syncPaused);
        audio.addEventListener('ended', handleEnded);
        audio.addEventListener('error', handleEnded);

        return () => {
            audio.removeEventListener('play', syncPlaying);
            audio.removeEventListener('playing', syncPlaying);
            audio.removeEventListener('pause', syncPaused);
            audio.removeEventListener('ended', handleEnded);
            audio.removeEventListener('error', handleEnded);
        };
    }, [playChunk]);

    const play = useCallback(() => {
        stoppedRef.current = false;
        chunkIndexRef.current = 0;
        setupMediaSession();
        requestWakeLock();
        playChunk(0);
    }, [playChunk, setupMediaSession, requestWakeLock]);

    const pause = useCallback(() => {
        audioRef.current?.pause();
    }, []);

    const resume = useCallback(() => {
        stoppedRef.current = false;
        requestWakeLock();
        if (audioRef.current?.paused) {
            audioRef.current.play();
        } else {
            playChunk(chunkIndexRef.current);
        }
    }, [playChunk, requestWakeLock]);

    const stop = useCallback(() => {
        stoppedRef.current = true;
        releaseWakeLock();
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.src = '';
        }
        chunkIndexRef.current = 0;
        if (onIndexChange) onIndexChange(null);
        setPlayState('stopped');
        if ('mediaSession' in navigator) {
            navigator.mediaSession.playbackState = 'none';
        }
    }, [onIndexChange, releaseWakeLock]);

    return (
        <>
            {/* DOM audio element — phải trong document để Media Session hoạt động */}
            {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
            <audio ref={audioRef} style={{ display: 'none' }} />

            <div className="mt-6 rounded-lg border border-toxic-green-DEFAULT/20 bg-[#141414] p-4 text-gray-200">
                {/* Header */}
                <div className="flex items-center gap-2 mb-3 pb-3 border-b border-gray-800">
                    <Volume2 size={14} className="text-toxic-green-DEFAULT" />
                    <span className="text-[10px] font-mono text-toxic-green-DEFAULT tracking-[0.2em] uppercase">
                        Nghe Truyện
                    </span>
                    <span className="text-[10px] font-mono text-gray-500 ml-auto">
                        {playState === 'playing' && '▶ Đang đọc...'}
                        {playState === 'paused' && '⏸ Tạm dừng'}
                        {playState === 'stopped' && '■ Dừng'}
                    </span>
                </div>

                {/* Controls */}
                <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-2">
                        {playState === 'stopped' && (
                            <button onClick={play}
                                className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 hover:border-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm">
                                <Play size={15} fill="currentColor" /><span>PHÁT</span>
                            </button>
                        )}
                        {playState === 'playing' && (
                            <button onClick={pause}
                                className="flex items-center gap-2 px-4 py-2 bg-[#252525] border border-gray-700 rounded-lg text-gray-200 hover:border-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm">
                                <Pause size={15} fill="currentColor" /><span>DỪNG</span>
                            </button>
                        )}
                        {playState === 'paused' && (
                            <button onClick={resume}
                                className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 transition-all font-biohazard tracking-widest text-sm">
                                <Play size={15} fill="currentColor" /><span>TIẾP</span>
                            </button>
                        )}
                        {playState !== 'stopped' && (
                            <button onClick={stop}
                                className="p-2 border border-gray-700 rounded-lg text-gray-400 hover:border-red-500 hover:text-red-400 transition-all">
                                <Square size={15} fill="currentColor" />
                            </button>
                        )}
                    </div>

                    <div className="w-px h-8 bg-gray-800" />

                    {/* Speed */}
                    <div className="flex items-center gap-1">
                        {[0.75, 1, 1.25, 1.5, 1.75].map((s) => (
                            <button key={s} onClick={() => setSpeed(s)}
                                className={`px-2 py-1 rounded text-[10px] font-mono transition-all ${speed === s ? 'bg-toxic-green-DEFAULT text-black font-bold' : 'text-gray-500 hover:text-gray-200'
                                    }`}>
                                {s}x
                            </button>
                        ))}
                    </div>

                    {/* Mute */}
                    <button onClick={() => setIsMuted(!isMuted)}
                        className="ml-auto p-2 text-gray-500 hover:text-gray-200 transition-colors">
                        {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                    </button>
                </div>

                {/* Chapter nav khi đang phát */}
                {playState !== 'stopped' && (
                    <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-800">
                        <span className="text-[10px] font-mono text-gray-600">Chuyển chương:</span>
                        {prevId && (
                            <button onClick={() => { stop(); router.push(`/chapters/${prevId}`); }}
                                className="flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-toxic-green-DEFAULT transition-colors">
                                <ChevronLeft size={12} /> Trước
                            </button>
                        )}
                        {nextId && (
                            <button onClick={() => { stop(); router.push(`/chapters/${nextId}`); }}
                                className="flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-toxic-green-DEFAULT transition-colors">
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
