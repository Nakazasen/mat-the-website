"use client";
import { useEffect, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Skull } from "lucide-react";

/** Generate eerie ambient sound using Web Audio API (no external files needed) */
function playAmbientSound() {
    try {
        const ctx = new AudioContext();
        const duration = 2.8;

        // Layer 1: Low rumble (distant machinery)
        const rumbleOsc = ctx.createOscillator();
        const rumbleGain = ctx.createGain();
        rumbleOsc.type = "sawtooth";
        rumbleOsc.frequency.setValueAtTime(45, ctx.currentTime);
        rumbleOsc.frequency.linearRampToValueAtTime(55, ctx.currentTime + duration);
        rumbleGain.gain.setValueAtTime(0, ctx.currentTime);
        rumbleGain.gain.linearRampToValueAtTime(0.06, ctx.currentTime + 0.3);
        rumbleGain.gain.linearRampToValueAtTime(0.04, ctx.currentTime + duration - 0.5);
        rumbleGain.gain.linearRampToValueAtTime(0, ctx.currentTime + duration);
        rumbleOsc.connect(rumbleGain).connect(ctx.destination);

        // Layer 2: Static/white noise (radio interference)
        const bufferSize = ctx.sampleRate * duration;
        const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const noiseData = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            noiseData[i] = (Math.random() * 2 - 1) * 0.03;
        }
        const noiseSource = ctx.createBufferSource();
        noiseSource.buffer = noiseBuffer;
        const noiseGain = ctx.createGain();
        noiseGain.gain.setValueAtTime(0, ctx.currentTime);
        noiseGain.gain.linearRampToValueAtTime(0.15, ctx.currentTime + 0.2);
        noiseGain.gain.setValueAtTime(0.08, ctx.currentTime + 1);
        noiseGain.gain.linearRampToValueAtTime(0, ctx.currentTime + duration);
        // Bandpass filter to make it sound like old radio
        const bpFilter = ctx.createBiquadFilter();
        bpFilter.type = "bandpass";
        bpFilter.frequency.setValueAtTime(800, ctx.currentTime);
        bpFilter.Q.setValueAtTime(2, ctx.currentTime);
        noiseSource.connect(bpFilter).connect(noiseGain).connect(ctx.destination);

        // Layer 3: Heartbeat (two low thumps)
        const beatTimes = [0.3, 0.6, 1.3, 1.6, 2.0];
        beatTimes.forEach((t) => {
            const beatOsc = ctx.createOscillator();
            const beatGain = ctx.createGain();
            beatOsc.type = "sine";
            beatOsc.frequency.setValueAtTime(60, ctx.currentTime + t);
            beatOsc.frequency.exponentialRampToValueAtTime(30, ctx.currentTime + t + 0.15);
            beatGain.gain.setValueAtTime(0, ctx.currentTime + t);
            beatGain.gain.linearRampToValueAtTime(0.12, ctx.currentTime + t + 0.02);
            beatGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.2);
            beatOsc.connect(beatGain).connect(ctx.destination);
            beatOsc.start(ctx.currentTime + t);
            beatOsc.stop(ctx.currentTime + t + 0.25);
        });

        // Start all layers
        rumbleOsc.start(ctx.currentTime);
        rumbleOsc.stop(ctx.currentTime + duration);
        noiseSource.start(ctx.currentTime);
        noiseSource.stop(ctx.currentTime + duration);

        // Cleanup
        setTimeout(() => ctx.close(), (duration + 0.5) * 1000);
    } catch {
        // Silently fail if AudioContext is not available
    }
}

function WelcomeContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const hasPlayed = useRef(false);

    useEffect(() => {
        const next = searchParams?.get("next") || "/";

        // Play ambient sound once
        if (!hasPlayed.current) {
            hasPlayed.current = true;
            playAmbientSound();
        }

        const timer = setTimeout(() => {
            router.push(next);
        }, 2500);

        return () => clearTimeout(timer);
    }, [router, searchParams]);

    return (
        <div className="relative z-10 flex flex-col items-center gap-8">
            {/* Logo with Glitch */}
            <div className="relative animate-glitch">
                {/* Glowing aura */}
                <div className="absolute inset-0 bg-toxic-green-DEFAULT/20 w-32 h-32 blur-2xl rounded-full animate-pulse" />

                {/* Radar rings */}
                <div className="absolute inset-0 border-2 border-toxic-green-DEFAULT/40 w-32 h-32 rounded-full animate-ping" style={{ animationDuration: "2s" }} />
                <div className="absolute inset-0 border border-toxic-green-DEFAULT/20 w-48 h-48 -m-8 rounded-full animate-spin-fast" />

                {/* Main Skull with scanning effect */}
                <div className="w-32 h-32 rounded-full bg-ash-900 border-2 border-toxic-green-DEFAULT flex items-center justify-center relative overflow-hidden shadow-[0_0_30px_rgba(57,255,20,0.3)]">
                    <Skull size={48} className="text-toxic-green-DEFAULT animate-pulse" />

                    {/* Scanning green line */}
                    <div className="absolute left-0 right-0 h-0.5 bg-toxic-green-DEFAULT/60 animate-scan shadow-[0_0_8px_rgba(57,255,20,0.8)]" />

                    {/* CRT scanlines overlay */}
                    <div className="absolute inset-0 opacity-20 pointer-events-none"
                        style={{
                            backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.3) 2px, rgba(0,0,0,0.3) 4px)",
                        }}
                    />
                </div>
            </div>

            {/* Text content with glitch */}
            <div className="text-center flex flex-col gap-4">
                {/* Title with glitch layers */}
                <div className="relative">
                    <h1 className="text-2xl font-biohazard text-white tracking-widest drop-shadow-[0_0_10px_rgba(255,255,255,0.5)] animate-glow-text">
                        MẠT THẾ · SINH HOÁ NGUY CƠ
                    </h1>
                    {/* Glitch ghost layers */}
                    <h1 className="absolute inset-0 text-2xl font-biohazard tracking-widest text-red-500/30 animate-glitch-text" aria-hidden="true"
                        style={{ clipPath: "inset(10% 0 60% 0)" }}>
                        MẠT THẾ · SINH HOÁ NGUY CƠ
                    </h1>
                    <h1 className="absolute inset-0 text-2xl font-biohazard tracking-widest text-cyan-400/30 animate-glitch-text" aria-hidden="true"
                        style={{ clipPath: "inset(60% 0 10% 0)", animationDelay: "0.1s" }}>
                        MẠT THẾ · SINH HOÁ NGUY CƠ
                    </h1>
                </div>

                {/* Status text with pulsing dots */}
                <div className="flex items-center justify-center gap-2">
                    <div className="flex gap-1.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-toxic-green-DEFAULT animate-bounce" style={{ animationDelay: "0ms" }} />
                        <div className="w-1.5 h-1.5 rounded-full bg-toxic-green-DEFAULT animate-bounce" style={{ animationDelay: "150ms" }} />
                        <div className="w-1.5 h-1.5 rounded-full bg-toxic-green-DEFAULT animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                    <p className="font-mono text-sm text-toxic-green-DEFAULT tracking-widest uppercase animate-pulse">
                        Đang xác nhận danh tính tại Trấn Hi Vọng...
                    </p>
                </div>

                {/* Fake terminal output */}
                <div className="font-mono text-[10px] text-ash-500 space-y-0.5 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
                    <p>&gt; SCANNING BIOMETRIC DATA...</p>
                    <p>&gt; VERIFYING SURVIVOR ID...</p>
                    <p className="text-toxic-green-DEFAULT/60">&gt; STATUS: <span className="animate-flicker">AUTHORIZED</span></p>
                </div>
            </div>
        </div>
    );
}

export default function WelcomeLoadingPage() {
    return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden relative">
            <Suspense fallback={<div className="text-toxic-green-DEFAULT font-mono">Đang tải...</div>}>
                <WelcomeContent />
            </Suspense>

            {/* Background layers */}
            <div className="absolute inset-0 pointer-events-none">
                {/* Radial glow */}
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(57,255,20,0.08)_0,transparent_60%)]" />
                {/* Grid pattern */}
                <div className="absolute inset-0 opacity-5 bg-grid-overlay" style={{ backgroundSize: "40px 40px" }} />
                {/* CRT scanline moving */}
                <div className="absolute left-0 right-0 h-[2px] bg-white/5 animate-scanline" />
                {/* Vignette */}
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_50%,rgba(0,0,0,0.8)_100%)]" />
            </div>
        </div>
    );
}
