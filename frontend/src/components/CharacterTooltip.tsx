"use client";

import React, { useCallback, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { useLocale } from "@/context/LocaleContext";

interface WikiCharacter {
    name: string;
    faction?: string;
    status?: string;
    ability?: string;
    first_appearance?: number;
}

interface CharacterTooltipProps {
    name: string;
    chapterProgress: number;
    children: React.ReactNode;
}

export default function CharacterTooltip({
    name,
    chapterProgress,
    children,
}: CharacterTooltipProps) {
    const { locale, dictionary } = useLocale();
    const [isVisible, setIsVisible] = useState(false);
    const [character, setCharacter] = useState<WikiCharacter | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [position, setPosition] = useState<"above" | "below">("above");
    const [tooltipCoords, setTooltipCoords] = useState({ left: 0, top: 0 });
    const triggerRef = useRef<HTMLSpanElement>(null);
    const fetchedRef = useRef(false);

    const fetchCharacter = useCallback(async () => {
        if (fetchedRef.current || isLoading) return;
        fetchedRef.current = true;
        setIsLoading(true);
        try {
            const params = new URLSearchParams({
                name,
                chapter: String(chapterProgress),
                locale,
            });
            const response = await fetch(`/api/wiki/character?${params.toString()}`);
            if (response.ok) {
                setCharacter(await response.json());
            }
        } finally {
            setIsLoading(false);
        }
    }, [chapterProgress, isLoading, locale, name]);

    const handleMouseEnter = () => {
        if (triggerRef.current) {
            const rect = triggerRef.current.getBoundingClientRect();
            const nextPosition = rect.top > 150 ? "above" : "below";
            setPosition(nextPosition);
            setTooltipCoords({
                left: rect.left + rect.width / 2,
                top: nextPosition === "above" ? rect.top - 8 : rect.bottom + 8,
            });
        }
        setIsVisible(true);
        fetchCharacter();
    };

    const statusColor = (status?: string) => {
        if (!status) return "#737373";
        const normalized = status.toLowerCase();
        if (normalized.includes("dead") || normalized.includes("chết") || normalized.includes("tử vong")) return "#ef4444";
        if (normalized.includes("injured") || normalized.includes("bị thương")) return "#f59e0b";
        return "#39FF14";
    };

    return (
        <span className="character-tooltip-wrapper" style={{ position: "relative", display: "inline" }}>
            <span
                ref={triggerRef}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={() => setIsVisible(false)}
                style={{
                    color: "var(--toxic-green)",
                    borderBottom: "1px dashed rgba(57,255,20,0.5)",
                    cursor: "crosshair",
                    transition: "border-color 0.2s",
                }}
            >
                {children}
            </span>

            {isVisible && typeof document !== "undefined" && createPortal(
                <div
                    style={{
                        position: "fixed",
                        top: `${tooltipCoords.top}px`,
                        left: `${tooltipCoords.left}px`,
                        transform: `translate(-50%, ${position === "above" ? "-100%" : "0"})`,
                        zIndex: 9999,
                        width: "220px",
                        background: "rgba(10, 10, 10, 0.95)",
                        border: "1px solid rgba(57, 255, 20, 0.4)",
                        borderRadius: "4px",
                        padding: "10px 12px",
                        fontFamily: "'JetBrains Mono', 'Courier Prime', monospace",
                        fontSize: "11px",
                        color: "#d4d0c8",
                        boxShadow: "0 0 20px rgba(57,255,20,0.15), 0 4px 24px rgba(0,0,0,0.8)",
                        pointerEvents: "none",
                        animation: "fadeInTooltip 0.15s ease-out",
                    }}
                >
                    <div style={{
                        color: "#39FF14",
                        fontWeight: 700,
                        marginBottom: "6px",
                        borderBottom: "1px solid rgba(57,255,20,0.2)",
                        paddingBottom: "4px",
                        letterSpacing: "0.05em",
                        fontSize: "12px",
                    }}>
                        {dictionary.tooltip.title}
                    </div>

                    {isLoading ? (
                        <div style={{ color: "#737373", fontSize: "10px" }}>{dictionary.tooltip.loading}</div>
                    ) : character ? (
                        <>
                            <div style={{ marginBottom: "3px" }}>
                                <span style={{ color: "#737373" }}>{dictionary.tooltip.name}: </span>
                                <span style={{ color: "#fff", fontWeight: 600 }}>{character.name}</span>
                            </div>
                            {character.faction && (
                                <div style={{ marginBottom: "3px" }}>
                                    <span style={{ color: "#737373" }}>{dictionary.tooltip.faction}: </span>
                                    <span>{character.faction}</span>
                                </div>
                            )}
                            {character.status && (
                                <div style={{ marginBottom: "3px" }}>
                                    <span style={{ color: "#737373" }}>{dictionary.tooltip.status}: </span>
                                    <span style={{ color: statusColor(character.status) }}>{character.status}</span>
                                </div>
                            )}
                            {character.ability && (
                                <div style={{ marginBottom: "3px" }}>
                                    <span style={{ color: "#737373" }}>{dictionary.tooltip.ability}: </span>
                                    <span style={{ color: "#f59e0b" }}>{character.ability}</span>
                                </div>
                            )}
                            {character.first_appearance && (
                                <div style={{ color: "#555", fontSize: "10px", marginTop: "4px" }}>
                                    {dictionary.tooltip.firstAppearance}: {dictionary.tooltip.chapter} {character.first_appearance}
                                </div>
                            )}
                        </>
                    ) : (
                        <div style={{ color: "#555", fontSize: "10px" }}>{dictionary.tooltip.notFound}</div>
                    )}
                </div>,
                document.body,
            )}
        </span>
    );
}
