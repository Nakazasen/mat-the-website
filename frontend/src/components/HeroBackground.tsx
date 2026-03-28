"use client";

import { useEffect, useState } from "react";
import Image from "next/image";

interface HeroBackgroundProps {
    images: string[];
    fallbackImage: string;
    intervalMs?: number;
    title: string;
}

export default function HeroBackground({ images, fallbackImage, intervalMs = 6000, title }: HeroBackgroundProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [mounted, setMounted] = useState(false);

    // Filter out invalid images, fallback to original if none exist
    const finalImages = images && images.length > 0 ? images : [fallbackImage];

    useEffect(() => {
        setMounted(true);
        if (finalImages.length <= 1) return;

        const timer = setInterval(() => {
            setCurrentIndex((prevIndex) => (prevIndex + 1) % finalImages.length);
        }, intervalMs);

        return () => clearInterval(timer);
    }, [finalImages.length, intervalMs]);

    return (
        <div className="absolute inset-0 z-0">
            {finalImages.map((src, index) => {
                const isActive = index === currentIndex;
                const isPrevious = index === (currentIndex - 1 + finalImages.length) % finalImages.length;
                
                // Show currently active image and the previous one (while active fades in) to prevent flashing
                const isVisible = isActive || isPrevious || (!mounted && index === 0);

                return (
                    <div
                        key={src}
                        className={`absolute inset-0 transition-opacity duration-[2000ms] ease-in-out ${
                            isActive ? "opacity-100 z-10" : "opacity-0 z-0"
                        }`}
                        aria-hidden={!isActive}
                    >
                        {isVisible && (
                            <Image
                                src={src}
                                alt={`${title} theme image ${index + 1}`}
                                fill
                                priority={index === 0} // Only prioritize the first image for LCP
                                className="object-cover object-center"
                                sizes="100vw"
                            />
                        )}
                    </div>
                );
            })}

            {/* Gradient Overlays tailored for the Mạt Thế reading UI theme */}
            <div className="absolute inset-0 z-20 bg-gradient-to-b from-black/50 via-ash-950/70 to-ash-950" />
            <div className="absolute inset-0 z-20 bg-gradient-to-r from-ash-950/80 via-transparent to-ash-950/50" />
            <div className="absolute bottom-0 left-0 right-0 z-20 h-48 bg-gradient-to-t from-ash-dark to-transparent" />
        </div>
    );
}
