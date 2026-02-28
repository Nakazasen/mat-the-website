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
type TTSEngine = 'detecting' | 'webspeech' | 'proxy';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

// ── Helpers ──────────────────────────────────────────────────────────────────

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

function findViVoice(): SpeechSynthesisVoice | null {
    if (!('speechSynthesis' in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    return (
        voices.find(v => v.lang.startsWith('vi') && v.name.toLowerCase().includes('google')) ??
        voices.find(v => v.lang.startsWith('vi')) ??
        null
    );
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function AudioPlayer({ content, chapterTitle, chapterNumber, prevId, nextId }: AudioPlayerProps) {
    const router = useRouter();
    const [playState, setPlayState] = useState<PlayState>('stopped');
    const [speed, setSpeed] = useState(1);
    const [isMuted, setIsMuted] = useState(false);
    const [engine, setEngine] = useState<TTSEngine>('detecting');

    // Refs
    const audioRef = useRef<HTMLAudioElement>(null);     // for proxy engine
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null); // for web speech
    const viVoiceRef = useRef<SpeechSynthesisVoice | null>(null);
    const chunksRef = useRef<string[]>([]);
    const chunkIdxRef = useRef(0);
    const stoppedRef = useRef(true);
    const speedRef = useRef(speed);
    const mutedRef = useRef(isMuted);
    const keepAliveRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => { speedRef.current = speed; }, [speed]);
    useEffect(() => {
        mutedRef.current = isMuted;
        if (audioRef.current) audioRef.current.muted = isMuted;
    }, [isMuted]);

    // Detect engine + preload Vietnamese voice
    useEffect(() => {
        if (!('speechSynthesis' in window)) { setEngine('proxy'); return; }

        const detect = () => {
            const voice = findViVoice();
            viVoiceRef.current = voice;
            setEngine(voice ? 'webspeech' : 'proxy');
        };

        detect();
        window.speechSynthesis.addEventListener('voiceschanged', detect);
        return () => window.speechSynthesis.removeEventListener('voiceschanged', detect);
    }, []);

    // Prepare text chunks
    useEffect(() => {
        const full = `Chương ${chapterNumber}: ${chapterTitle}. ${content}`;
        chunksRef.current = splitIntoChunks(full);
    }, [content, chapterTitle, chapterNumber]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stoppedRef.current = true;
            window.speechSynthesis?.cancel();
            if (keepAliveRef.current) clearInterval(keepAliveRef.current);
        };
    }, []);

    // ── Media Session ─────────────────────────────────────────────────────────

    const setupMediaSession = useCallback(() => {
        if (!('mediaSession' in navigator)) return;
        navigator.mediaSession.metadata = new MediaMetadata({
            title: `Chương ${chapterNumber}: ${chapterTitle}`,
            artist: 'Mạt Thế - Sinh Hoá Nguy Cơ ☣️',
            album: 'Nghe truyện',
        });
        navigator.mediaSession.setActionHandler('play', () => {
            if (engine === 'webspeech') window.speechSynthesis.resume();
            else audioRef.current?.play();
            setPlayState('playing');
            navigator.mediaSession.playbackState = 'playing';
        });
        navigator.mediaSession.setActionHandler('pause', () => {
            if (engine === 'webspeech') { stoppedRef.current = true; window.speechSynthesis.pause(); }
            else { stoppedRef.current = true; audioRef.current?.pause(); }
            setPlayState('paused');
            navigator.mediaSession.playbackState = 'paused';
        });
        navigator.mediaSession.setActionHandler('previoustrack', () => {
            if (prevId) { stopAll(); router.push(`/chapters/${prevId}`); }
        });
        navigator.mediaSession.setActionHandler('nexttrack', () => {
            if (nextId) { stopAll(); router.push(`/chapters/${nextId}`); }
        });
        navigator.mediaSession.playbackState = 'playing';
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [chapterNumber, chapterTitle, prevId, nextId, router, engine]);

    // ── Web Speech Engine ─────────────────────────────────────────────────────

    const playWebSpeech = useCallback((text: string, onEnd: () => void) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'vi-VN';
        utterance.rate = speedRef.current;
        utterance.volume = mutedRef.current ? 0 : 1;
        utterance.pitch = 1;
        if (viVoiceRef.current) utterance.voice = viVoiceRef.current;

        utterance.onend = () => { if (!stoppedRef.current) onEnd(); };
        utterance.onerror = (e) => { if (e.error !== 'interrupted' && !stoppedRef.current) onEnd(); };

        utteranceRef.current = utterance;
        window.speechSynthesis.speak(utterance);

        // Chrome mobile keep-alive (pauses/resumes every 10s to prevent auto-stop)
        if (keepAliveRef.current) clearInterval(keepAliveRef.current);
        keepAliveRef.current = setInterval(() => {
            if (!window.speechSynthesis.speaking) { clearInterval(keepAliveRef.current!); return; }
            if (!window.speechSynthesis.paused) {
                window.speechSynthesis.pause();
                window.speechSynthesis.resume();
            }
        }, 10000);
    }, []);

    const playWebSpeechChain = useCallback((idx: number) => {
        if (stoppedRef.current || idx >= chunksRef.current.length) {
            if (!stoppedRef.current) {
                setPlayState('stopped');
                if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
                if (nextId) setTimeout(() => router.push(`/chapters/${nextId}`), 500);
            }
            return;
        }
        chunkIdxRef.current = idx;
        playWebSpeech(chunksRef.current[idx], () => playWebSpeechChain(idx + 1));
    }, [playWebSpeech, nextId, router]);

    // ── Proxy Engine (DOM audio) ──────────────────────────────────────────────

    const playProxyChunk = useCallback((idx: number) => {
        if (stoppedRef.current || !audioRef.current) return;
        if (idx >= chunksRef.current.length) {
            setPlayState('stopped');
            if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
            if (nextId) setTimeout(() => router.push(`/chapters/${nextId}`), 800);
            return;
        }
        chunkIdxRef.current = idx;
        const url = `${API_URL}/api/tts?lang=vi&speed=${speedRef.current}&text=${encodeURIComponent(chunksRef.current[idx])}`;
        audioRef.current.src = url;
        audioRef.current.load();
        audioRef.current.play().catch(() => { if (!stoppedRef.current) playProxyChunk(idx + 1); });
    }, [nextId, router]);

    // Wire up DOM audio events
    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;
        const onEnded = () => { if (!stoppedRef.current) playProxyChunk(chunkIdxRef.current + 1); };
        const onError = () => { if (!stoppedRef.current) playProxyChunk(chunkIdxRef.current + 1); };
        audio.addEventListener('ended', onEnded);
        audio.addEventListener('error', onError);
        return () => { audio.removeEventListener('ended', onEnded); audio.removeEventListener('error', onError); };
    }, [playProxyChunk]);

    // ── Actions ───────────────────────────────────────────────────────────────

    const play = useCallback(() => {
        stoppedRef.current = false;
        chunkIdxRef.current = 0;
        setPlayState('playing');
        setupMediaSession();
        if (engine === 'webspeech') {
            window.speechSynthesis.cancel();
            playWebSpeechChain(0);
        } else {
            playProxyChunk(0);
        }
    }, [engine, playWebSpeechChain, playProxyChunk, setupMediaSession]);

    const pause = useCallback(() => {
        stoppedRef.current = true;
        if (engine === 'webspeech') window.speechSynthesis.pause();
        else audioRef.current?.pause();
        setPlayState('paused');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'paused';
    }, [engine]);

    const resume = useCallback(() => {
        stoppedRef.current = false;
        setPlayState('playing');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'playing';
        if (engine === 'webspeech') {
            // Resume web speech từ chunk hiện tại
            window.speechSynthesis.resume();
            // Nếu đã cancel, phát lại từ chunk
            if (!window.speechSynthesis.speaking) playWebSpeechChain(chunkIdxRef.current);
        } else {
            playProxyChunk(chunkIdxRef.current);
        }
    }, [engine, playWebSpeechChain, playProxyChunk]);

    function stopAll() {
        stoppedRef.current = true;
        if (keepAliveRef.current) clearInterval(keepAliveRef.current);
        window.speechSynthesis?.cancel();
        if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }
        chunkIdxRef.current = 0;
        setPlayState('stopped');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'none';
    }

    // ── UI ────────────────────────────────────────────────────────────────────

    const engineBadge = engine === 'webspeech'
        ? '🎙️ Giọng Google'
        : engine === 'proxy'
            ? '🌐 Giọng Online'
            : '⏳ Đang nhận diện...';

    return (
        <>
            {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
            <audio ref={audioRef} style={{ display: 'none' }} />

            <div className="mt-6 rounded-lg border border-toxic-green-DEFAULT/20 bg-[#141414] p-4 text-gray-200">
                <div className="flex items-center gap-2 mb-3 pb-3 border-b border-gray-800">
                    <Volume2 size={14} className="text-toxic-green-DEFAULT" />
                    <span className="text-[10px] font-mono text-toxic-green-DEFAULT tracking-[0.2em] uppercase">Nghe Truyện</span>
                    <span className="text-[10px] font-mono text-gray-600 ml-1">· {engineBadge}</span>
                    <span className="text-[10px] font-mono text-gray-500 ml-auto">
                        {playState === 'playing' && '▶ Đang đọc...'}
                        {playState === 'paused' && '⏸ Tạm dừng'}
                        {playState === 'stopped' && '■ Dừng'}
                    </span>
                </div>

                <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-2">
                        {playState === 'stopped' && (
                            <button onClick={play} disabled={engine === 'detecting'}
                                className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 hover:border-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm disabled:opacity-40">
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
                            <button onClick={stopAll}
                                className="p-2 border border-gray-700 rounded-lg text-gray-400 hover:border-red-500 hover:text-red-400 transition-all">
                                <Square size={15} fill="currentColor" />
                            </button>
                        )}
                    </div>

                    <div className="w-px h-8 bg-gray-800" />

                    <div className="flex items-center gap-1">
                        {[0.75, 1, 1.25, 1.5, 1.75].map(s => (
                            <button key={s} onClick={() => setSpeed(s)}
                                className={`px-2 py-1 rounded text-[10px] font-mono transition-all ${speed === s ? 'bg-toxic-green-DEFAULT text-black font-bold' : 'text-gray-500 hover:text-gray-200'}`}>
                                {s}x
                            </button>
                        ))}
                    </div>

                    <button onClick={() => setIsMuted(!isMuted)} className="ml-auto p-2 text-gray-500 hover:text-gray-200 transition-colors">
                        {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                    </button>
                </div>

                {playState !== 'stopped' && (
                    <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-800">
                        <span className="text-[10px] font-mono text-gray-600">Chuyển chương:</span>
                        {prevId && <button onClick={() => { stopAll(); router.push(`/chapters/${prevId}`); }} className="flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-toxic-green-DEFAULT transition-colors"><ChevronLeft size={12} /> Trước</button>}
                        {nextId && <button onClick={() => { stopAll(); router.push(`/chapters/${nextId}`); }} className="flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-toxic-green-DEFAULT transition-colors">Tiếp <ChevronRight size={12} /></button>}
                        <span className="ml-auto text-[10px] font-mono text-gray-600 animate-pulse">💡 Tắt màn hình vẫn nghe được</span>
                    </div>
                )}
            </div>
        </>
    );
}
