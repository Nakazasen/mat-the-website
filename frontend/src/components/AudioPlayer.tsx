'use client';

import { useCallback, useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from 'react';
import { ChevronLeft, ChevronRight, GripHorizontal, Pause, Play, Square, Volume2, VolumeX } from 'lucide-react';
import { useRouter } from 'next/navigation';

import { useLocale } from '@/context/LocaleContext';
import type { Locale } from '@/lib/i18n/config';
import { splitIntoChunks, stripHtml } from '@/lib/tts-utils';

interface AudioPlayerProps {
    content: string;
    chapterTitle: string;
    chapterNumber: number;
    prevId: number | null;
    nextId: number | null;
    onIndexChange?: (index: number | null) => void;
    locale?: Locale;
    resolvedContent?: string;
    voice?: string;
}

type PlayState = 'stopped' | 'playing' | 'paused';

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-website.onrender.com').replace(/\/$/, '');
const AUDIO_FLOATING_STORAGE_KEY = 'reader-audio-floating-position-v1';
const AUDIO_PLAYBACK_SPEED_STORAGE_KEY = 'reader-audio-playback-speed-v1';
const AUDIO_FLOATING_WIDTH = 360;
const AUDIO_FLOATING_MARGIN = 16;
const MOBILE_PANEL_EVENT = 'reader-learning-mobile-panel';
const AUDIO_LAYOUT_EVENT = 'reader-audio-layout';
const AUDIO_SPEED_OPTIONS = [0.75, 1, 1.25, 1.5, 1.75] as const;

const AUDIO_VOICE_STORAGE_KEY = 'reader-audio-voice-v1';
const AVAILABLE_VOICES: Record<Locale, { id: string; label: string }[]> = {
    vi: [
        { id: 'google', label: 'Google Chị Cả' },
        { id: 'vi-VN-HoaiMyNeural', label: 'Edge Hoài Mỹ (Nữ)' },
        { id: 'vi-VN-NamMinhNeural', label: 'Edge Nam Minh (Nam)' },
    ],
    en: [
        { id: 'google', label: 'Google Default' },
        { id: 'en-US-AriaNeural', label: 'Edge Aria (Female)' },
        { id: 'en-US-GuyNeural', label: 'Edge Guy (Male)' },
    ],
    ja: [
        { id: 'google', label: 'Google Default' },
        { id: 'ja-JP-NanamiNeural', label: 'Edge Nanami (Female)' },
        { id: 'ja-JP-KeitaNeural', label: 'Edge Keita (Male)' },
    ],
    'zh-CN': [
        { id: 'google', label: 'Google Default' },
        { id: 'zh-CN-XiaoxiaoNeural', label: 'Edge Xiaoxiao (Female)' },
        { id: 'zh-CN-YunxiNeural', label: 'Edge Yunxi (Male)' },
    ],
};

function normalizePlaybackSpeed(value: number | null | undefined): number {
    if (typeof value !== 'number' || Number.isNaN(value)) return 1;
    return AUDIO_SPEED_OPTIONS.includes(value as typeof AUDIO_SPEED_OPTIONS[number]) ? value : 1;
}

function readSavedPlaybackSpeed(): number {
    if (typeof window === 'undefined') return 1;
    try {
        const raw = window.localStorage.getItem(AUDIO_PLAYBACK_SPEED_STORAGE_KEY);
        if (!raw) return 1;
        return normalizePlaybackSpeed(Number(raw));
    } catch {
        return 1;
    }
}

function readSavedVoice(locale: Locale): string {
    if (typeof window === 'undefined') return 'google';
    try {
        const raw = window.localStorage.getItem(AUDIO_VOICE_STORAGE_KEY);
        if (!raw) return 'google';
        const voices = AVAILABLE_VOICES[locale] || AVAILABLE_VOICES.vi;
        return voices.some(v => v.id === raw) ? raw : 'google';
    } catch {
        return 'google';
    }
}

function shouldIgnoreAudioHotkeys(target: EventTarget | null): boolean {
    if (!(target instanceof HTMLElement)) return false;
    return Boolean(target.closest('input, textarea, select, [contenteditable="true"]'));
}

function ttsLocale(locale: Locale) {
    if (locale === 'zh-CN') return 'zh-CN';
    return locale;
}

function ttsUrl(text: string, lang: Locale, speed: number, voice?: string): string {
    const params = new URLSearchParams({
        lang: ttsLocale(lang),
        speed: String(speed),
        text,
    });
    if (voice) params.set('voice', voice);
    return `${API_URL}/api/tts?${params.toString()}`;
}

export default function AudioPlayer({
    content,
    chapterTitle,
    chapterNumber,
    prevId,
    nextId,
    onIndexChange,
    locale,
    resolvedContent,
    voice,
}: AudioPlayerProps) {
    const router = useRouter();
    const { dictionary, localizePath, locale: contextLocale } = useLocale();
    const activeLocale = locale ?? contextLocale;

    const [playState, setPlayState] = useState<PlayState>('stopped');
    const [speed, setSpeed] = useState(() => readSavedPlaybackSpeed());
    const [activeVoice, setActiveVoice] = useState(() => readSavedVoice(activeLocale));
    const [isMuted, setIsMuted] = useState(false);


    const audioRef = useRef<HTMLAudioElement>(null);
    const chunksRef = useRef<string[]>([]);
    const chunkIndexRef = useRef(0);
    const speedRef = useRef(speed);
    const stoppedRef = useRef(true);
    const wakeLockRef = useRef<any>(null);
    const preloadTimerRef = useRef<any>(null);
    const floatingPanelRef = useRef<HTMLDivElement>(null);
    const draggingPointerIdRef = useRef<number | null>(null);
    const [isDesktop, setIsDesktop] = useState(false);
    const [floatingDragging, setFloatingDragging] = useState(false);
    const [floatingPosition, setFloatingPosition] = useState<{ top: number; left: number } | null>(null);
    const [mobileLearningPanelActive, setMobileLearningPanelActive] = useState(false);

    useEffect(() => {
        speedRef.current = speed;
        if (audioRef.current) {
            audioRef.current.playbackRate = speed;
        }
    }, [speed]);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        try {
            window.localStorage.setItem(AUDIO_PLAYBACK_SPEED_STORAGE_KEY, String(speed));
        } catch {
            // ignore storage errors
        }
    }, [speed]);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        try {
            window.localStorage.setItem(AUDIO_VOICE_STORAGE_KEY, activeVoice);
        } catch {
            // ignore storage errors
        }
    }, [activeVoice]);


    useEffect(() => {
        const cleanText = stripHtml(resolvedContent || content);
        chunksRef.current = splitIntoChunks(cleanText);
    }, [content, resolvedContent]);

    useEffect(() => {
        if (audioRef.current) audioRef.current.muted = isMuted;
    }, [isMuted]);

    useEffect(() => {
        const updateViewport = () => setIsDesktop(window.innerWidth >= 768);
        updateViewport();
        window.addEventListener('resize', updateViewport);
        return () => window.removeEventListener('resize', updateViewport);
    }, []);

    useEffect(() => {
        const handleMobilePanelEvent = (event: Event) => {
            const detail = (event as CustomEvent<{ active?: boolean }>).detail;
            setMobileLearningPanelActive(Boolean(detail?.active));
        };

        window.addEventListener(MOBILE_PANEL_EVENT, handleMobilePanelEvent as EventListener);
        return () => window.removeEventListener(MOBILE_PANEL_EVENT, handleMobilePanelEvent as EventListener);
    }, []);

    const getFloatingMinTop = useCallback(() => {
        if (typeof window === 'undefined') return 96;
        const header = document.querySelector('header');
        if (!(header instanceof HTMLElement)) return 96;
        return Math.max(96, Math.ceil(header.getBoundingClientRect().bottom + 12));
    }, []);

    const getFloatingDefaultPosition = useCallback(() => {
        if (typeof window === 'undefined') {
            return { top: 420, left: 24 };
        }
        const panelHeight = floatingPanelRef.current?.offsetHeight ?? 148;
        const minTop = getFloatingMinTop();
        const top = Math.max(minTop, window.innerHeight - panelHeight - 24);
        return { top, left: 24 };
    }, [getFloatingMinTop]);

    const clampFloatingPosition = useCallback((position: { top: number; left: number }) => {
        if (typeof window === 'undefined') return position;
        const panelHeight = floatingPanelRef.current?.offsetHeight ?? 148;
        const minTop = getFloatingMinTop();
        const maxTop = Math.max(minTop, window.innerHeight - panelHeight - AUDIO_FLOATING_MARGIN);
        const maxLeft = Math.max(AUDIO_FLOATING_MARGIN, window.innerWidth - AUDIO_FLOATING_WIDTH - AUDIO_FLOATING_MARGIN);
        return {
            top: Math.min(Math.max(minTop, position.top), maxTop),
            left: Math.min(Math.max(AUDIO_FLOATING_MARGIN, position.left), maxLeft),
        };
    }, [getFloatingMinTop]);

    useEffect(() => {
        if (!isDesktop || playState === 'stopped') return;
        try {
            const raw = window.localStorage.getItem(AUDIO_FLOATING_STORAGE_KEY);
            if (!raw) {
                setFloatingPosition(clampFloatingPosition(getFloatingDefaultPosition()));
                return;
            }
            const parsed = JSON.parse(raw) as { top?: number; left?: number };
            if (typeof parsed.top === 'number' && typeof parsed.left === 'number') {
                setFloatingPosition(clampFloatingPosition({ top: parsed.top, left: parsed.left }));
                return;
            }
            setFloatingPosition(clampFloatingPosition(getFloatingDefaultPosition()));
        } catch {
            setFloatingPosition(clampFloatingPosition(getFloatingDefaultPosition()));
        }
    }, [clampFloatingPosition, getFloatingDefaultPosition, isDesktop, playState]);

    useEffect(() => {
        if (!isDesktop || !floatingPosition) return;
        try {
            window.localStorage.setItem(AUDIO_FLOATING_STORAGE_KEY, JSON.stringify(floatingPosition));
        } catch {
            // ignore storage errors
        }
    }, [floatingPosition, isDesktop]);

    useEffect(() => {
        if (!isDesktop || playState === 'stopped') return;
        setFloatingPosition((current) => clampFloatingPosition(current || getFloatingDefaultPosition()));
    }, [clampFloatingPosition, getFloatingDefaultPosition, isDesktop, playState]);

    useEffect(() => {
        return () => {
            stoppedRef.current = true;
            if (preloadTimerRef.current) {
                clearTimeout(preloadTimerRef.current);
                preloadTimerRef.current = null;
            }
            if (onIndexChange) onIndexChange(null);
        };
    }, [onIndexChange]);


    useEffect(() => {
        window.dispatchEvent(new CustomEvent('reader-audio-state', {
            detail: { active: playState !== 'stopped' },
        }));

        return () => {
            window.dispatchEvent(new CustomEvent('reader-audio-state', {
                detail: { active: false },
            }));
        };
    }, [playState]);

    useEffect(() => {
        const emitLayout = () => {
            const isMobileActive = !isDesktop && playState !== 'stopped' && !mobileLearningPanelActive;
            const height = isMobileActive ? (floatingPanelRef.current?.offsetHeight ?? 0) : 0;
            window.dispatchEvent(new CustomEvent(AUDIO_LAYOUT_EVENT, {
                detail: {
                    active: isMobileActive,
                    height,
                },
            }));
        };

        emitLayout();
        window.addEventListener('resize', emitLayout);
        return () => {
            window.removeEventListener('resize', emitLayout);
            window.dispatchEvent(new CustomEvent(AUDIO_LAYOUT_EVENT, {
                detail: {
                    active: false,
                    height: 0,
                },
            }));
        };
    }, [isDesktop, mobileLearningPanelActive, playState]);

    const stop = useCallback(() => {
        stoppedRef.current = true;
        if (preloadTimerRef.current) {
            clearTimeout(preloadTimerRef.current);
            preloadTimerRef.current = null;
        }
        if (wakeLockRef.current) {
            wakeLockRef.current.release();
            wakeLockRef.current = null;
        }
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
    }, [onIndexChange]);


    const updateMetadata = useCallback(() => {
        if (!('mediaSession' in navigator)) return;

        navigator.mediaSession.metadata = new MediaMetadata({
            title: `${dictionary.reader.chapter} ${chapterNumber}`,
            artist: chapterTitle,
            album: 'Mat The',
            artwork: [
                { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
                { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
            ],
        });
    }, [chapterNumber, chapterTitle, dictionary.reader.chapter]);

    const playChunk = useCallback((index: number) => {
        if (stoppedRef.current) return;
        const audio = audioRef.current;
        if (!audio) return;

        // Clear any pending preload timer to prevent racing
        if (preloadTimerRef.current) {
            clearTimeout(preloadTimerRef.current);
            preloadTimerRef.current = null;
        }

        if (index >= chunksRef.current.length) {
            stop();
            if (nextId) setTimeout(() => router.push(localizePath(`/chapters/${nextId}`)), 1000);
            return;
        }

        chunkIndexRef.current = index;
        if (onIndexChange) onIndexChange(index);

        const url = ttsUrl(chunksRef.current[index], activeLocale, speedRef.current, activeVoice);
        if (audio.src !== url) {
            audio.src = url;
            audio.load();
        }

        audio.play().then(() => {
            audio.playbackRate = speedRef.current;
            
            // Pre-fetch the next chunk in the background after a small delay to avoid concurrent socket clashes on Microsoft server
            if (typeof window !== 'undefined') {
                const nextIndex = index + 1;
                if (nextIndex < chunksRef.current.length) {
                    preloadTimerRef.current = setTimeout(() => {
                        const nextUrl = ttsUrl(chunksRef.current[nextIndex], activeLocale, speedRef.current, activeVoice);
                        const preloader = new window.Audio();
                        preloader.src = nextUrl;
                        preloader.preload = 'auto';
                        preloader.load();
                    }, 2200); // 2.2 seconds delay is ideal
                }
            }
        }).catch(() => {
            if (!stoppedRef.current) playChunk(index + 1);
        });
    }, [activeLocale, localizePath, nextId, onIndexChange, router, stop, activeVoice]);




    const requestWakeLock = useCallback(async () => {
        if ('wakeLock' in navigator) {
            try {
                wakeLockRef.current = await (navigator as any).wakeLock.request('screen');
            } catch {
                // ignore
            }
        }
    }, []);

    const setupMediaSession = useCallback(() => {
        if (!('mediaSession' in navigator)) return;

        updateMetadata();
        const actionHandlers: [MediaSessionAction, MediaSessionActionHandler][] = [
            ['play', () => { audioRef.current?.play(); }],
            ['pause', () => { audioRef.current?.pause(); }],
            ['previoustrack', () => { if (prevId) { stop(); router.push(localizePath(`/chapters/${prevId}`)); } }],
            ['nexttrack', () => { if (nextId) { stop(); router.push(localizePath(`/chapters/${nextId}`)); } }],
        ];

        for (const [action, handler] of actionHandlers) {
            try {
                navigator.mediaSession.setActionHandler(action, handler);
            } catch {
                // unsupported
            }
        }
    }, [localizePath, nextId, prevId, router, stop, updateMetadata]);

    const jumpToChunk = useCallback((index: number) => {
        if (!chunksRef.current.length) return;
        const nextIndex = Math.min(Math.max(index, 0), chunksRef.current.length - 1);
        stoppedRef.current = false;
        setupMediaSession();
        requestWakeLock();
        playChunk(nextIndex);
    }, [playChunk, requestWakeLock, setupMediaSession]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const syncPlaying = () => {
            if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'playing';
            setPlayState('playing');
        };

        const syncPaused = () => {
            if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'paused';
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
    }, [playChunk, requestWakeLock, setupMediaSession]);

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

    const replayCurrentChunk = useCallback(() => {
        const audio = audioRef.current;
        if (playState !== 'stopped' && audio && audio.currentTime > 3) {
            audio.currentTime = 0;
            return;
        }
        jumpToChunk(Math.max(0, chunkIndexRef.current - 1));
    }, [jumpToChunk, playState]);

    const skipToNextChunk = useCallback(() => {
        if (playState === 'stopped') {
            play();
            return;
        }
        jumpToChunk(chunkIndexRef.current + 1);
    }, [jumpToChunk, play, playState]);

    const handleFloatingDragStart = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
        if (!isDesktop || !floatingPosition) return;
        event.preventDefault();
        draggingPointerIdRef.current = event.pointerId;
        event.currentTarget.setPointerCapture(event.pointerId);
        const startX = event.clientX;
        const startY = event.clientY;
        const origin = floatingPosition;
        setFloatingDragging(true);

        const handleMove = (moveEvent: PointerEvent) => {
            if (draggingPointerIdRef.current !== null && moveEvent.pointerId !== draggingPointerIdRef.current) {
                return;
            }
            setFloatingPosition(clampFloatingPosition({
                left: origin.left + (moveEvent.clientX - startX),
                top: origin.top + (moveEvent.clientY - startY),
            }));
        };

        const handleUp = () => {
            setFloatingDragging(false);
            draggingPointerIdRef.current = null;
            window.removeEventListener('pointermove', handleMove);
            window.removeEventListener('pointerup', handleUp);
        };

        window.addEventListener('pointermove', handleMove);
        window.addEventListener('pointerup', handleUp);
    }, [clampFloatingPosition, floatingPosition, isDesktop]);

    useEffect(() => {
        const handleHotkeys = (event: KeyboardEvent) => {
            if (!event.altKey || event.ctrlKey || event.metaKey || shouldIgnoreAudioHotkeys(event.target)) {
                return;
            }

            const key = event.key.toLowerCase();
            if (key === 'p') {
                event.preventDefault();
                if (playState === 'stopped') {
                    play();
                } else if (playState === 'playing') {
                    pause();
                } else {
                    resume();
                }
            } else if (key === 's') {
                event.preventDefault();
                stop();
            } else if (event.key === '[') {
                event.preventDefault();
                replayCurrentChunk();
            } else if (event.key === ']') {
                event.preventDefault();
                skipToNextChunk();
            }
        };

        window.addEventListener('keydown', handleHotkeys);
        return () => window.removeEventListener('keydown', handleHotkeys);
    }, [pause, play, playState, replayCurrentChunk, resume, skipToNextChunk, stop]);

    const showCompactMobilePlayer = !isDesktop && playState !== 'stopped' && mobileLearningPanelActive;
    const showFloatingPlayer = playState !== 'stopped' && !showCompactMobilePlayer;

    return (
        <>
            {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
            <audio ref={audioRef} style={{ display: 'none' }} />

            <div className="mt-6 rounded-lg border border-toxic-green-DEFAULT/20 bg-[#141414] p-4 text-gray-200">
                <div className="flex items-center gap-2 mb-3 pb-3 border-b border-gray-800">
                    <Volume2 size={14} className="text-toxic-green-DEFAULT" />
                    <span className="text-[10px] font-mono text-toxic-green-DEFAULT tracking-[0.2em] uppercase">
                        {dictionary.audio.title}
                    </span>
                    <span className="text-[10px] font-mono text-gray-500 ml-auto">
                        {playState === 'playing' && dictionary.audio.playing}
                        {playState === 'paused' && dictionary.audio.paused}
                        {playState === 'stopped' && dictionary.audio.stopped}
                    </span>
                </div>

                <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-2">
                        {playState === 'stopped' && (
                            <button onClick={play} className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 hover:border-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm">
                                <Play size={15} fill="currentColor" /><span>{dictionary.audio.play}</span>
                            </button>
                        )}
                        {playState === 'playing' && (
                            <button onClick={pause} className="flex items-center gap-2 px-4 py-2 bg-[#252525] border border-gray-700 rounded-lg text-gray-200 hover:border-toxic-green-DEFAULT transition-all font-biohazard tracking-widest text-sm">
                                <Pause size={15} fill="currentColor" /><span>{dictionary.audio.pause}</span>
                            </button>
                        )}
                        {playState === 'paused' && (
                            <button onClick={resume} className="flex items-center gap-2 px-4 py-2 bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/40 rounded-lg text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20 transition-all font-biohazard tracking-widest text-sm">
                                <Play size={15} fill="currentColor" /><span>{dictionary.audio.resume}</span>
                            </button>
                        )}
                        {playState !== 'stopped' && (
                            <button onClick={stop} className="p-2 border border-gray-700 rounded-lg text-gray-400 hover:border-red-500 hover:text-red-400 transition-all">
                                <Square size={15} fill="currentColor" />
                            </button>
                        )}
                    </div>

                    <div className="w-px h-8 bg-gray-800" />

                    <div className="flex items-center gap-1">
                        {AUDIO_SPEED_OPTIONS.map((s) => (
                            <button
                                key={s}
                                onClick={() => setSpeed(s)}
                                className={`px-2 py-1 rounded text-[10px] font-mono transition-all ${speed === s ? 'bg-toxic-green-DEFAULT text-black font-bold' : 'text-gray-500 hover:text-gray-200'}`}
                            >
                                {s}x
                            </button>
                        ))}
                    </div>

                    <div className="w-px h-8 bg-gray-800" />

                    <div className="flex items-center gap-1.5 ml-1">
                        <select
                            value={activeVoice}
                            onChange={(e) => setActiveVoice(e.target.value)}
                            className="bg-[#1a1a1a] border border-gray-800 text-gray-300 text-[10px] font-mono rounded px-2 py-1 focus:outline-none focus:border-toxic-green-DEFAULT cursor-pointer transition-all hover:border-gray-700"
                        >
                            {(AVAILABLE_VOICES[activeLocale] || AVAILABLE_VOICES.vi).map((v) => (
                                <option key={v.id} value={v.id}>
                                    {v.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <button onClick={() => setIsMuted(!isMuted)} className="ml-auto p-2 text-gray-500 hover:text-gray-200 transition-colors">
                        {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                    </button>

                </div>

                {playState !== 'stopped' && (
                    <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-800">
                        <span className="text-[10px] font-mono text-gray-600">{dictionary.audio.changeChapter}:</span>
                        {prevId && (
                            <button onClick={() => { stop(); router.push(localizePath(`/chapters/${prevId}`)); }} className="flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-toxic-green-DEFAULT transition-colors">
                                <ChevronLeft size={12} /> {dictionary.reader.previous}
                            </button>
                        )}
                        {nextId && (
                            <button onClick={() => { stop(); router.push(localizePath(`/chapters/${nextId}`)); }} className="flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-toxic-green-DEFAULT transition-colors">
                                {dictionary.reader.next} <ChevronRight size={12} />
                            </button>
                        )}
                        <span className="ml-auto text-[10px] font-mono text-gray-600 animate-pulse">
                            {dictionary.audio.keepScreenOn}
                        </span>
                    </div>
                )}

                <div className="mt-3 border-t border-gray-800 pt-3 text-[10px] font-mono text-gray-500">
                    {dictionary.audio.shortcuts}
                </div>
            </div>

            {showCompactMobilePlayer && (
                <div className="fixed bottom-4 right-4 z-[72] md:hidden">
                    <div className="w-[min(92vw,360px)] rounded-2xl border border-toxic-green-DEFAULT/25 bg-[#0d1116]/96 px-3 py-3 text-gray-100 shadow-[0_18px_50px_rgba(0,0,0,0.42)] backdrop-blur">
                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                onClick={playState === 'playing' ? pause : resume}
                                className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-toxic-green-DEFAULT/35 bg-toxic-green-DEFAULT/10 text-toxic-green-DEFAULT"
                                aria-label={playState === 'playing' ? dictionary.audio.pause : dictionary.audio.resume}
                            >
                                {playState === 'playing' ? <Pause size={14} /> : <Play size={14} />}
                            </button>
                            <div className="min-w-0 flex-1">
                                <div className="truncate text-[10px] font-mono uppercase tracking-[0.18em] text-toxic-green-DEFAULT">
                                    {dictionary.audio.floatingTitle}
                                </div>
                                <div className="truncate text-[11px] text-gray-300">
                                    {chunkIndexRef.current + 1}/{Math.max(chunksRef.current.length, 1)}
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={stop}
                                className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-gray-800 text-gray-400 hover:border-red-500 hover:text-red-400"
                                aria-label="Stop audio"
                            >
                                <Square size={13} fill="currentColor" />
                            </button>
                        </div>

                        <div className="mt-3 flex flex-wrap items-center gap-1.5 border-t border-gray-800 pt-3">
                            <span className="mr-1 text-[10px] font-mono uppercase tracking-[0.16em] text-gray-500">
                                {dictionary.audio.speed}
                            </span>
                            {AUDIO_SPEED_OPTIONS.map((option) => (
                                <button
                                    key={`compact-speed-${option}`}
                                    type="button"
                                    onClick={() => setSpeed(option)}
                                    className={`rounded-md px-2 py-1 text-[10px] font-mono transition-all ${
                                        speed === option
                                            ? 'bg-toxic-green-DEFAULT text-black font-bold'
                                            : 'border border-gray-800 text-gray-400 hover:border-toxic-green-DEFAULT/40 hover:text-toxic-green-DEFAULT'
                                    }`}
                                >
                                    {option}x
                                </button>
                            ))}
                        </div>

                        <div className="mt-2.5 flex flex-wrap items-center gap-1.5 border-t border-gray-800 pt-2.5">
                            <span className="mr-1 text-[10px] font-mono uppercase tracking-[0.16em] text-gray-500">
                                GIỌNG:
                            </span>
                            <select
                                value={activeVoice}
                                onChange={(e) => setActiveVoice(e.target.value)}
                                className="bg-[#1e1e1e] border border-gray-800 text-gray-300 text-[10px] font-mono rounded px-2 py-1 focus:outline-none focus:border-toxic-green-DEFAULT/50 cursor-pointer"
                            >
                                {(AVAILABLE_VOICES[activeLocale] || AVAILABLE_VOICES.vi).map((v) => (
                                    <option key={v.id} value={v.id}>
                                        {v.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                    </div>
                </div>
            )}

            {showFloatingPlayer && (
                <div
                    ref={floatingPanelRef}
                    className="fixed bottom-24 left-4 right-4 z-[62] md:right-auto md:w-[360px]"
                    style={
                        isDesktop && floatingPosition
                            ? { top: `${floatingPosition.top}px`, left: `${floatingPosition.left}px` }
                            : { bottom: '96px' }
                    }
                >
                    <div className="rounded-2xl border border-toxic-green-DEFAULT/25 bg-[#0d1116]/95 px-4 py-3 text-gray-100 shadow-[0_18px_50px_rgba(0,0,0,0.45)] backdrop-blur">
                        <div
                            className={`flex items-center gap-2 ${isDesktop ? 'cursor-grab select-none touch-none' : ''} ${floatingDragging ? 'cursor-grabbing' : ''}`}
                            onPointerDown={isDesktop ? handleFloatingDragStart : undefined}
                        >
                            <Volume2 size={14} className="text-toxic-green-DEFAULT shrink-0" />
                            <div className="min-w-0 flex-1">
                                <div className="truncate text-[11px] font-mono uppercase tracking-[0.2em] text-toxic-green-DEFAULT">
                                    {dictionary.audio.floatingTitle}
                                </div>
                                <div className="truncate text-xs text-gray-400">
                                    {chapterTitle} · {chunkIndexRef.current + 1}/{Math.max(chunksRef.current.length, 1)}
                                </div>
                            </div>
                            <span className="text-[10px] font-mono text-gray-500">
                                {playState === 'playing' ? dictionary.audio.playing : dictionary.audio.paused}
                            </span>
                            {isDesktop && (
                                <span className="inline-flex items-center gap-1 text-[10px] font-mono uppercase tracking-[0.18em] text-gray-500">
                                    <GripHorizontal size={12} />
                                    Kéo
                                </span>
                            )}
                        </div>

                        <div className="mt-3 flex items-center gap-2">
                            <button
                                type="button"
                                onClick={replayCurrentChunk}
                                className="inline-flex items-center gap-1 rounded-lg border border-gray-800 px-3 py-2 text-[11px] font-mono text-gray-300 hover:border-toxic-green-DEFAULT/40 hover:text-toxic-green-DEFAULT"
                            >
                                <ChevronLeft size={12} />
                                {dictionary.audio.replay}
                            </button>

                            {playState === 'playing' ? (
                                <button
                                    type="button"
                                    onClick={pause}
                                    className="inline-flex items-center gap-2 rounded-lg border border-toxic-green-DEFAULT/40 bg-toxic-green-DEFAULT/10 px-3 py-2 text-[11px] font-mono text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20"
                                >
                                    <Pause size={13} />
                                    {dictionary.audio.pause}
                                </button>
                            ) : (
                                <button
                                    type="button"
                                    onClick={resume}
                                    className="inline-flex items-center gap-2 rounded-lg border border-toxic-green-DEFAULT/40 bg-toxic-green-DEFAULT/10 px-3 py-2 text-[11px] font-mono text-toxic-green-DEFAULT hover:bg-toxic-green-DEFAULT/20"
                                >
                                    <Play size={13} fill="currentColor" />
                                    {dictionary.audio.resume}
                                </button>
                            )}

                            <button
                                type="button"
                                onClick={stop}
                                className="rounded-lg border border-gray-800 p-2 text-gray-400 hover:border-red-500 hover:text-red-300"
                                title={dictionary.audio.stopped}
                            >
                                <Square size={13} fill="currentColor" />
                            </button>

                            <button
                                type="button"
                                onClick={skipToNextChunk}
                                className="ml-auto inline-flex items-center gap-1 rounded-lg border border-gray-800 px-3 py-2 text-[11px] font-mono text-gray-300 hover:border-toxic-green-DEFAULT/40 hover:text-toxic-green-DEFAULT"
                            >
                                {dictionary.audio.skip}
                                <ChevronRight size={12} />
                            </button>
                        </div>

                        <div className="mt-3 flex flex-wrap items-center justify-between gap-1.5 border-t border-gray-800 pt-3">
                            <div className="flex items-center gap-1">
                                <span className="mr-1 text-[10px] font-mono uppercase tracking-[0.16em] text-gray-500">
                                    GIỌNG:
                                </span>
                                <select
                                    value={activeVoice}
                                    onChange={(e) => setActiveVoice(e.target.value)}
                                    className="bg-[#12161f] border border-gray-850 text-gray-300 text-[10px] font-mono rounded px-1.5 py-1 focus:outline-none focus:border-toxic-green-DEFAULT/50 cursor-pointer max-w-[125px]"
                                >
                                    {(AVAILABLE_VOICES[activeLocale] || AVAILABLE_VOICES.vi).map((v) => (
                                        <option key={v.id} value={v.id}>
                                            {v.label}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="flex items-center gap-1.5">
                                <span className="mr-1 text-[10px] font-mono uppercase tracking-[0.16em] text-gray-500">
                                    {dictionary.audio.speed}
                                </span>
                                <div className="flex gap-0.5">
                                    {AUDIO_SPEED_OPTIONS.map((option) => (
                                        <button
                                            key={`floating-speed-${option}`}
                                            type="button"
                                            onClick={() => setSpeed(option)}
                                            className={`rounded px-1.5 py-0.5 text-[9px] font-mono transition-all ${
                                                speed === option
                                                    ? 'bg-toxic-green-DEFAULT text-black font-bold'
                                                    : 'border border-gray-800 text-gray-400 hover:border-toxic-green-DEFAULT/40 hover:text-toxic-green-DEFAULT'
                                            }`}
                                        >
                                            {option}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            )}
        </>
    );
}
