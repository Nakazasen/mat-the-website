'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { ChevronLeft, ChevronRight, Pause, Play, Square, Volume2, VolumeX } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface AudioPlayerProps {
    content: string;
    chapterTitle: string;
    chapterNumber: number;
    prevId: number | null;
    nextId: number | null;
}

type PlayState = 'stopped' | 'playing' | 'paused';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'https://mat-the-api.onrender.com';

// Split text thành chunks ≤ 180 ký tự tại điểm câu/dấu phẩy
function splitIntoChunks(text: string, maxLen = 180): string[] {
    const chunks: string[] = [];
    let remaining = text;
    while (remaining.length > 0) {
        if (remaining.length <= maxLen) { chunks.push(remaining.trim()); break; }
        let cutAt = -1;
        const slice = remaining.substring(0, maxLen);
        for (const sep of ['. ', '! ', '? ', ', ', '; ', ' ']) {
            const idx = slice.lastIndexOf(sep);
            if (idx > 40) { cutAt = idx + sep.length; break; }
        }
        if (cutAt === -1) cutAt = maxLen;
        chunks.push(remaining.substring(0, cutAt).trim());
        remaining = remaining.substring(cutAt).trim();
    }
    return chunks.filter(c => c.length > 0);
}

// Tạo URL gọi TTS qua backend proxy
function ttsUrl(text: string, speed: number): string {
    return `${API_URL}/api/tts?lang=vi&speed=${speed}&text=${encodeURIComponent(text)}`;
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

    const audioRef = useRef<HTMLAudioElement | null>(null);
    const chunksRef = useRef<string[]>([]);
    const chunkIndexRef = useRef(0);
    const speedRef = useRef(speed);
    const mutedRef = useRef(isMuted);
    const stoppedRef = useRef(true);

    useEffect(() => { speedRef.current = speed; }, [speed]);
    useEffect(() => {
        mutedRef.current = isMuted;
        if (audioRef.current) audioRef.current.muted = isMuted;
    }, [isMuted]);

    // Chuẩn bị chunks khi content thay đổi
    useEffect(() => {
        const fullText = `Chương ${chapterNumber}: ${chapterTitle}. ${content}`;
        chunksRef.current = splitIntoChunks(fullText);
    }, [content, chapterTitle, chapterNumber]);

    // Dừng khi rời trang
    useEffect(() => {
        return () => {
            stoppedRef.current = true;
            audioRef.current?.pause();
        };
    }, []);

    const setupMediaSession = useCallback(() => {
        if (!('mediaSession' in navigator)) return;
        navigator.mediaSession.metadata = new MediaMetadata({
            title: `Chương ${chapterNumber}: ${chapterTitle}`,
            artist: 'Mạt Thế - Sinh Hoá Nguy Cơ ☣️',
            album: 'Nghe truyện',
        });
        navigator.mediaSession.setActionHandler('play', () => {
            audioRef.current?.play();
            setPlayState('playing');
            navigator.mediaSession.playbackState = 'playing';
        });
        navigator.mediaSession.setActionHandler('pause', () => {
            audioRef.current?.pause();
            setPlayState('paused');
            navigator.mediaSession.playbackState = 'paused';
        });
        navigator.mediaSession.setActionHandler('previoustrack', () => {
            if (prevId) { stoppedRef.current = true; audioRef.current?.pause(); router.push(`/chapters/${prevId}`); }
        });
        navigator.mediaSession.setActionHandler('nexttrack', () => {
            if (nextId) { stoppedRef.current = true; audioRef.current?.pause(); router.push(`/chapters/${nextId}`); }
        });
        navigator.mediaSession.playbackState = 'playing';
    }, [chapterNumber, chapterTitle, prevId, nextId, router]);

    const playChunk = useCallback((index: number) => {
        if (stoppedRef.current) return;
        if (index >= chunksRef.current.length) {
            setPlayState('stopped');
            if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
            if (nextId) setTimeout(() => router.push(`/chapters/${nextId}`), 800);
            return;
        }

        const url = ttsUrl(chunksRef.current[index], speedRef.current);
        const audio = new Audio(url);
        audio.muted = mutedRef.current;
        audioRef.current = audio;
        chunkIndexRef.current = index;

        audio.onended = () => { if (!stoppedRef.current) playChunk(index + 1); };
        audio.onerror = () => { if (!stoppedRef.current) playChunk(index + 1); };
        audio.play().catch(() => setPlayState('stopped'));
    }, [nextId, router]);

    const play = useCallback(() => {
        stoppedRef.current = false;
        chunkIndexRef.current = 0;
        setPlayState('playing');
        setupMediaSession();
        playChunk(0);
    }, [playChunk, setupMediaSession]);

    const pause = useCallback(() => {
        audioRef.current?.pause();
        stoppedRef.current = true; // stop new chunks from loading
        setPlayState('paused');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'paused';
    }, []);

    const resume = useCallback(() => {
        stoppedRef.current = false;
        setPlayState('playing');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'playing';
        // Phát lại từ chunk hiện tại (chunk mới bắt đầu)
        playChunk(chunkIndexRef.current);
    }, [playChunk]);

    const stop = useCallback(() => {
        stoppedRef.current = true;
        audioRef.current?.pause();
        audioRef.current = null;
        chunkIndexRef.current = 0;
        setPlayState('stopped');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
    }, []);

    return (
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
    );
}
