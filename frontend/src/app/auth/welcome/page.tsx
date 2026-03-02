"use client";
import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Skull } from "lucide-react";

function WelcomeContent() {
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        const next = searchParams?.get("next") || "/";

        const timer = setTimeout(() => {
            router.push(next);
        }, 2500); // Show loading for 2.5 seconds

        return () => clearTimeout(timer);
    }, [router, searchParams]);

    return (
        <div className="relative z-10 flex flex-col items-center gap-8">
            {/* Logo and Animation */}
            <div className="relative">
                {/* Glowing background behind skull */}
                <div className="absolute inset-0 bg-toxic-green-DEFAULT/20 w-32 h-32 blur-2xl rounded-full" />

                {/* Pulsing rings */}
                <div className="absolute inset-0 border-2 border-toxic-green-DEFAULT/40 w-32 h-32 rounded-full animate-ping" style={{ animationDuration: "2s" }} />
                <div className="absolute inset-0 border border-toxic-green-DEFAULT/20 w-48 h-48 -m-8 rounded-full animate-spin-fast" />

                {/* Main Skull Icon */}
                <div className="w-32 h-32 rounded-full bg-ash-900 border-2 border-toxic-green-DEFAULT flex items-center justify-center relative overflow-hidden shadow-[0_0_30px_rgba(57,255,20,0.3)]">
                    <Skull size={48} className="text-toxic-green-DEFAULT animate-pulse" />

                    {/* Scanning line effect */}
                    <div className="absolute top-0 left-0 right-0 h-1 bg-white/50 animate-scan" />
                </div>
            </div>

            {/* Text content */}
            <div className="text-center flex flex-col gap-3">
                <h1 className="text-2xl font-biohazard text-white tracking-widest drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]">
                    MẠT THẾ · SINH HOÁ NGUY CƠ
                </h1>
                <div className="flex items-center justify-center gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-toxic-green-DEFAULT animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-toxic-green-DEFAULT animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-toxic-green-DEFAULT animate-bounce" style={{ animationDelay: "300ms" }} />
                    <p className="font-mono text-sm text-toxic-green-DEFAULT tracking-widest uppercase ml-2 animate-pulse">
                        Đang xác nhận danh tính tại Trấn Hi Vọng...
                    </p>
                </div>
            </div>
        </div>
    );
}

export default function WelcomeLoadingPage() {
    return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden">
            <Suspense fallback={<div className="text-toxic-green-DEFAULT font-mono">Đang tải...</div>}>
                <WelcomeContent />
            </Suspense>

            {/* Background elements */}
            <div className="absolute inset-0 opacity-10 pointer-events-none">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(57,255,20,0.4)_0,transparent_70%)]" />
                <div className="w-full h-full bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] mix-blend-overlay" />
            </div>
        </div>
    );
}
