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
    const [isSupported, setIsSupported] = useState(false);

    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
    const keepAliveRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const speedRef = useRef(speed);

    useEffect(() => { speedRef.current = speed; }, [speed]);

    useEffect(() => {
        setIsSupported('speechSynthesis' in window);
    }, []);

    // Dừng khi rời trang
    useEffect(() => {
        return () => {
            if (window.speechSynthesis) window.speechSynthesis.cancel();
            if (keepAliveRef.current) clearInterval(keepAliveRef.current);
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
            window.speechSynthesis.resume();
            setPlayState('playing');
            navigator.mediaSession.playbackState = 'playing';
        });
        navigator.mediaSession.setActionHandler('pause', () => {
            window.speechSynthesis.pause();
            setPlayState('paused');
            navigator.mediaSession.playbackState = 'paused';
        });
        navigator.mediaSession.setActionHandler('previoustrack', () => {
            if (prevId) { window.speechSynthesis.cancel(); router.push(`/chapters/${prevId}`); }
        });
        navigator.mediaSession.setActionHandler('nexttrack', () => {
            if (nextId) { window.speechSynthesis.cancel(); router.push(`/chapters/${nextId}`); }
        });
        navigator.mediaSession.playbackState = 'playing';
    }, [chapterNumber, chapterTitle, prevId, nextId, router]);

    const doSpeak = useCallback((voice: SpeechSynthesisVoice | null) => {
        const fullText = `Chương ${chapterNumber}: ${chapterTitle}. ${content}`;
        const utterance = new SpeechSynthesisUtterance(fullText);
        utterance.lang = 'vi-VN';
        utterance.rate = speedRef.current;
        utterance.volume = isMuted ? 0 : 1;
        utterance.pitch = 1;
        if (voice) utterance.voice = voice;

        utterance.onstart = () => {
            setPlayState('playing');
            setupMediaSession();
        };
        utterance.onpause = () => setPlayState('paused');
        utterance.onresume = () => setPlayState('playing');
        utterance.onerror = (e) => {
            if (e.error !== 'interrupted' && e.error !== 'canceled') {
                setPlayState('stopped');
            }
        };

        // Chrome mobile bug: speech stops after ~15s unless we ping it
        if (keepAliveRef.current) clearInterval(keepAliveRef.current);
        keepAliveRef.current = setInterval(() => {
            if (!window.speechSynthesis.speaking) {
                clearInterval(keepAliveRef.current!);
                return;
            }
            if (!window.speechSynthesis.paused) {
                window.speechSynthesis.pause();
                window.speechSynthesis.resume();
            }
        }, 10000);

        utterance.onend = () => {
            if (keepAliveRef.current) clearInterval(keepAliveRef.current);
            setPlayState('stopped');
            if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
            if (nextId) setTimeout(() => router.push(`/chapters/${nextId}`), 500);
        };

        utteranceRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    }, [chapterNumber, chapterTitle, content, isMuted, setupMediaSession, nextId, router]);

    const play = useCallback(() => {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();

        const voices = window.speechSynthesis.getVoices();

        const findViVoice = (list: SpeechSynthesisVoice[]) =>
            list.find(v => v.lang.startsWith('vi') && v.name.toLowerCase().includes('google'))
            ?? list.find(v => v.lang.startsWith('vi'))
            ?? null;

        if (voices.length > 0) {
            doSpeak(findViVoice(voices));
        } else {
            // Voices chưa load → đợi event voiceschanged
            const handler = () => {
                doSpeak(findViVoice(window.speechSynthesis.getVoices()));
            };
            window.speechSynthesis.addEventListener('voiceschanged', handler, { once: true });
            // Fallback 1s nếu event không bao giờ kích
            setTimeout(() => {
                if (!window.speechSynthesis.speaking) {
                    doSpeak(findViVoice(window.speechSynthesis.getVoices()));
                }
            }, 1000);
        }
    }, [doSpeak]);

    const pause = useCallback(() => {
        window.speechSynthesis?.pause();
        setPlayState('paused');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'paused';
    }, []);

    const resume = useCallback(() => {
        window.speechSynthesis?.resume();
        setPlayState('playing');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'playing';
    }, []);

    const stop = useCallback(() => {
        window.speechSynthesis?.cancel();
        if (keepAliveRef.current) clearInterval(keepAliveRef.current);
        setPlayState('stopped');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
    }, []);

    if (!isSupported) return null;

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

            {/* Chapter nav (khi đang phát) */}
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
