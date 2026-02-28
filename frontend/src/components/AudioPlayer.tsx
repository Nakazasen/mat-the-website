'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { Play, Pause, Square, Volume2, VolumeX, ChevronLeft, ChevronRight } from 'lucide-react';
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
    const textRef = useRef<string>('');

    // Check browser support
    useEffect(() => {
        setIsSupported('speechSynthesis' in window);
    }, []);

    // Prepare full text to read
    useEffect(() => {
        textRef.current = `Chương ${chapterNumber}: ${chapterTitle}. ${content}`;
    }, [content, chapterTitle, chapterNumber]);

    // Cleanup on unmount or chapter change
    useEffect(() => {
        return () => {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        };
    }, []);

    const setupMediaSession = useCallback(() => {
        if (!('mediaSession' in navigator)) return;

        navigator.mediaSession.metadata = new MediaMetadata({
            title: `Chương ${chapterNumber}: ${chapterTitle}`,
            artist: 'Mạt Thế - Sinh Hoá Nguy Cơ ☣️',
            album: 'Đọc truyện tự động',
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

        navigator.mediaSession.setActionHandler('stop', () => {
            stop();
        });

        navigator.mediaSession.setActionHandler('previoustrack', () => {
            if (prevId) {
                stop();
                router.push(`/chapters/${prevId}`);
            }
        });

        navigator.mediaSession.setActionHandler('nexttrack', () => {
            if (nextId) {
                stop();
                router.push(`/chapters/${nextId}`);
            }
        });

        navigator.mediaSession.playbackState = 'playing';
    }, [chapterNumber, chapterTitle, prevId, nextId, router]);

    const stop = useCallback(() => {
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        setPlayState('stopped');
        if ('mediaSession' in navigator) {
            navigator.mediaSession.playbackState = 'none';
        }
    }, []);

    const play = useCallback(() => {
        if (!window.speechSynthesis) return;

        window.speechSynthesis.cancel();

        const doSpeak = (voice: SpeechSynthesisVoice | null) => {
            const utterance = new SpeechSynthesisUtterance(textRef.current);
            utterance.lang = 'vi-VN';
            utterance.rate = speed;
            utterance.volume = isMuted ? 0 : 1;
            utterance.pitch = 1;

            if (voice) {
                utterance.voice = voice;
            }

            utterance.onstart = () => {
                setPlayState('playing');
                setupMediaSession();
            };
            utterance.onpause = () => setPlayState('paused');
            utterance.onresume = () => setPlayState('playing');
            utterance.onerror = (e) => {
                if (e.error !== 'interrupted') setPlayState('stopped');
            };

            // Workaround for Chrome mobile bug: speech stops after ~15s
            const keepAlive = setInterval(() => {
                if (window.speechSynthesis.paused) return;
                if (window.speechSynthesis.speaking) {
                    window.speechSynthesis.pause();
                    window.speechSynthesis.resume();
                } else {
                    clearInterval(keepAlive);
                }
            }, 10000);

            utterance.onend = () => {
                clearInterval(keepAlive);
                setPlayState('stopped');
                if ('mediaSession' in navigator) {
                    navigator.mediaSession.playbackState = 'none';
                }
                if (nextId) {
                    setTimeout(() => router.push(`/chapters/${nextId}`), 500);
                }
            };

            utteranceRef.current = utterance;
            window.speechSynthesis.speak(utterance);
        };

        // --- Tìm giọng tiếng Việt ---
        const findViVoice = (voices: SpeechSynthesisVoice[]) =>
            voices.find((v) => v.lang.startsWith('vi') && v.name.toLowerCase().includes('google'))
            || voices.find((v) => v.lang.startsWith('vi'))
            || null;

        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
            // Voices đã load rồi → dùng luôn
            doSpeak(findViVoice(voices));
        } else {
            // Chưa load → chờ event rồi mới speak
            window.speechSynthesis.addEventListener(
                'voiceschanged',
                () => {
                    doSpeak(findViVoice(window.speechSynthesis.getVoices()));
                },
                { once: true }
            );
            // Fallback: nếu trình duyệt không bao giờ fire voiceschanged (hiếm)
            setTimeout(() => {
                if (!window.speechSynthesis.speaking) {
                    doSpeak(findViVoice(window.speechSynthesis.getVoices()));
                }
            }, 500);
        }
    }, [speed, isMuted, setupMediaSession, nextId, router]);

    const pause = useCallback(() => {
        if (window.speechSynthesis) {
            window.speechSynthesis.pause();
            setPlayState('paused');
            if ('mediaSession' in navigator) {
                navigator.mediaSession.playbackState = 'paused';
            }
        }
    }, []);

    const resume = useCallback(() => {
        if (window.speechSynthesis) {
            window.speechSynthesis.resume();
            setPlayState('playing');
            if ('mediaSession' in navigator) {
                navigator.mediaSession.playbackState = 'playing';
            }
        }
    }, []);

    // Update speech rate without restarting
    const changeSpeed = (newSpeed: number) => {
        setSpeed(newSpeed);
        if (playState !== 'stopped') {
            stop();
            setSpeed(newSpeed);
            // Will restart with new speed via user action
        }
    };

    if (!isSupported) return null;

    return (
        <div className="mt-6 rounded-lg border border-toxic-green-DEFAULT/20 bg-ash-950/80 backdrop-blur-sm p-4">
            {/* Header */}
            <div className="flex items-center gap-2 mb-3 pb-3 border-b border-ash-800">
                <Volume2 size={14} className="text-toxic-green-DEFAULT" />
                <span className="text-[10px] font-mono text-toxic-green-DEFAULT tracking-[0.2em] uppercase">
                    Nghe Truyện
                </span>
                <span className="text-[10px] font-mono text-ash-600 ml-auto">
                    {playState === 'playing' && '▶ Đang đọc...'}
                    {playState === 'paused' && '⏸ Tạm dừng'}
                    {playState === 'stopped' && '■ Dừng'}
                </span>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-3">
                {/* Play/Pause/Stop */}
                <div className="flex items-center gap-2">
                    {playState === 'stopped' && (
                        <button
                            onClick={play}
                            className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 hover:border-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm"
                            title="Bắt đầu nghe"
                        >
                            <Play size={15} fill="currentColor" />
                            <span>PHÁT</span>
                        </button>
                    )}
                    {playState === 'playing' && (
                        <button
                            onClick={pause}
                            className="flex items-center gap-2 px-4 py-2 bg-ash-800 border border-ash-700 rounded-lg text-ash-200 hover:border-toxic-green-DEFAULT hover:text-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm"
                            title="Tạm dừng"
                        >
                            <Pause size={15} fill="currentColor" />
                            <span>DỪNG</span>
                        </button>
                    )}
                    {playState === 'paused' && (
                        <button
                            onClick={resume}
                            className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 hover:border-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm"
                            title="Tiếp tục"
                        >
                            <Play size={15} fill="currentColor" />
                            <span>TIẾP</span>
                        </button>
                    )}

                    {playState !== 'stopped' && (
                        <button
                            onClick={stop}
                            className="p-2 border border-ash-700 rounded-lg text-ash-400 hover:border-blood-red-bright hover:text-blood-red-bright transition-all"
                            title="Dừng hẳn"
                        >
                            <Square size={15} fill="currentColor" />
                        </button>
                    )}
                </div>

                {/* Divider */}
                <div className="w-px h-8 bg-ash-800" />

                {/* Speed Control */}
                <div className="flex items-center gap-1">
                    {[0.75, 1, 1.25, 1.5, 1.75].map((s) => (
                        <button
                            key={s}
                            onClick={() => changeSpeed(s)}
                            className={`px-2 py-1 rounded text-[10px] font-mono transition-all ${speed === s
                                ? 'bg-toxic-green-DEFAULT text-black font-bold'
                                : 'text-ash-500 hover:text-ash-200'
                                }`}
                        >
                            {s}x
                        </button>
                    ))}
                </div>

                {/* Mute */}
                <button
                    onClick={() => setIsMuted(!isMuted)}
                    className="ml-auto p-2 text-ash-500 hover:text-ash-200 transition-colors"
                    title={isMuted ? 'Bật âm' : 'Tắt tiếng'}
                >
                    {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                </button>
            </div>

            {/* Chapter nav shortcuts */}
            {playState !== 'stopped' && (
                <div className="flex items-center gap-3 mt-3 pt-3 border-t border-ash-800">
                    <span className="text-[10px] font-mono text-ash-600">Chuyển chương:</span>
                    {prevId && (
                        <button
                            onClick={() => { stop(); router.push(`/chapters/${prevId}`); }}
                            className="flex items-center gap-1 text-[10px] font-mono text-ash-400 hover:text-toxic-green-DEFAULT transition-colors"
                        >
                            <ChevronLeft size={12} /> Trước
                        </button>
                    )}
                    {nextId && (
                        <button
                            onClick={() => { stop(); router.push(`/chapters/${nextId}`); }}
                            className="flex items-center gap-1 text-[10px] font-mono text-ash-400 hover:text-toxic-green-DEFAULT transition-colors"
                        >
                            Tiếp <ChevronRight size={12} />
                        </button>
                    )}
                    <span className="ml-auto text-[10px] font-mono text-ash-600 animate-pulse">
                        💡 Tắt màn hình vẫn nghe được
                    </span>
                </div>
            )}
        </div>
    );
}
