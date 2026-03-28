"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { createPortal } from "react-dom";
import { ExternalLink } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";

interface WikiCharacter {
    name: string;
    slug?: string;
    image_url?: string;
    faction?: string;
    status?: string;
    ability?: string;
    first_appearance?: number;
    description?: string;
}

interface CharacterTooltipProps {
    name: string;
    chapterProgress: number;
    children: React.ReactNode;
}

const TOOLTIP_WIDTH = 264;

export default function CharacterTooltip({
    name,
    chapterProgress,
    children,
}: CharacterTooltipProps) {
    const { locale, dictionary, localizePath } = useLocale();
    const [isVisible, setIsVisible] = useState(false);
    const [character, setCharacter] = useState<WikiCharacter | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [position, setPosition] = useState<"above" | "below">("above");
    const [tooltipCoords, setTooltipCoords] = useState({ left: 0, top: 0 });
    const triggerRef = useRef<HTMLSpanElement>(null);
    const fetchedRef = useRef(false);
    const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const clearHideTimer = () => {
        if (hideTimerRef.current) {
            clearTimeout(hideTimerRef.current);
            hideTimerRef.current = null;
        }
    };

    const scheduleHide = () => {
        clearHideTimer();
        hideTimerRef.current = setTimeout(() => {
            setIsVisible(false);
        }, 100);
    };

    useEffect(() => () => clearHideTimer(), []);

    const fetchCharacter = useCallback(async () => {
        if ((fetchedRef.current && character) || isLoading) return;
        setIsLoading(true);
        try {
            const params = new URLSearchParams({
                name,
                chapter: String(chapterProgress),
                locale,
            });
            const response = await fetch(`/api/wiki/character?${params.toString()}`);
            if (response.ok) {
                const payload = await response.json();
                setCharacter(payload);
                if (payload) {
                    fetchedRef.current = true;
                }
            }
        } finally {
            setIsLoading(false);
        }
    }, [chapterProgress, character, isLoading, locale, name]);

    const updateTooltipPosition = useCallback(() => {
        if (!triggerRef.current || typeof window === "undefined") return;
        const rect = triggerRef.current.getBoundingClientRect();
        const nextPosition = rect.top > 220 ? "above" : "below";
        const halfWidth = TOOLTIP_WIDTH / 2;
        const safeLeft = Math.min(
            Math.max(rect.left + rect.width / 2, halfWidth + 12),
            window.innerWidth - halfWidth - 12,
        );
        setPosition(nextPosition);
        setTooltipCoords({
            left: safeLeft,
            top: nextPosition === "above" ? rect.top - 10 : rect.bottom + 10,
        });
    }, []);

    const handleOpen = () => {
        clearHideTimer();
        updateTooltipPosition();
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

    const wikiHref = character?.slug ? localizePath(`/wiki/${character.slug}`) : null;

    return (
        <span className="character-tooltip-wrapper" style={{ position: "relative", display: "inline" }}>
            <span
                ref={triggerRef}
                onMouseEnter={handleOpen}
                onMouseLeave={scheduleHide}
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
                    onMouseEnter={handleOpen}
                    onMouseLeave={scheduleHide}
                    style={{
                        position: "fixed",
                        top: `${tooltipCoords.top}px`,
                        left: `${tooltipCoords.left}px`,
                        transform: `translate(-50%, ${position === "above" ? "-100%" : "0"})`,
                        zIndex: 9999,
                        width: `${TOOLTIP_WIDTH}px`,
                        background: "rgba(10, 10, 10, 0.97)",
                        border: "1px solid rgba(57, 255, 20, 0.4)",
                        borderRadius: "8px",
                        padding: "12px",
                        fontFamily: "'JetBrains Mono', 'Courier Prime', monospace",
                        fontSize: "11px",
                        color: "#d4d0c8",
                        boxShadow: "0 0 24px rgba(57,255,20,0.14), 0 8px 30px rgba(0,0,0,0.8)",
                        pointerEvents: "auto",
                        animation: "fadeInTooltip 0.15s ease-out",
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            gap: "8px",
                            color: "#39FF14",
                            fontWeight: 700,
                            marginBottom: "8px",
                            borderBottom: "1px solid rgba(57,255,20,0.2)",
                            paddingBottom: "6px",
                            letterSpacing: "0.05em",
                            fontSize: "12px",
                        }}
                    >
                        <span>{dictionary.tooltip.title}</span>
                        {wikiHref && (
                            <Link
                                href={wikiHref}
                                style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: "4px",
                                    color: "#9fffc0",
                                    textDecoration: "none",
                                    fontSize: "10px",
                                }}
                            >
                                <span>Wiki</span>
                                <ExternalLink size={12} />
                            </Link>
                        )}
                    </div>

                    {isLoading ? (
                        <div style={{ color: "#737373", fontSize: "10px" }}>{dictionary.tooltip.loading}</div>
                    ) : character ? (
                        <>
                            {(character.image_url || character.slug) && (
                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "10px",
                                        marginBottom: "10px",
                                    }}
                                >
                                    {character.image_url ? (
                                        <img
                                            src={character.image_url}
                                            alt={character.name}
                                            style={{
                                                width: "52px",
                                                height: "52px",
                                                objectFit: "cover",
                                                borderRadius: "8px",
                                                border: "1px solid rgba(57,255,20,0.3)",
                                                background: "rgba(255,255,255,0.04)",
                                            }}
                                        />
                                    ) : (
                                        <div
                                            style={{
                                                width: "52px",
                                                height: "52px",
                                                borderRadius: "8px",
                                                border: "1px solid rgba(57,255,20,0.18)",
                                                display: "flex",
                                                alignItems: "center",
                                                justifyContent: "center",
                                                color: "#39FF14",
                                                fontWeight: 700,
                                            }}
                                        >
                                            {character.name.slice(0, 1).toUpperCase()}
                                        </div>
                                    )}
                                    <div style={{ minWidth: 0 }}>
                                        <div style={{ color: "#fff", fontWeight: 700, fontSize: "13px", lineHeight: 1.35 }}>
                                            {character.name}
                                        </div>
                                        {wikiHref && (
                                            <Link
                                                href={wikiHref}
                                                style={{
                                                    color: "#7ee7ff",
                                                    textDecoration: "none",
                                                    fontSize: "10px",
                                                }}
                                            >
                                                /wiki/{character.slug}
                                            </Link>
                                        )}
                                    </div>
                                </div>
                            )}

                            {!character.image_url && !character.slug && (
                                <div style={{ marginBottom: "4px" }}>
                                    <span style={{ color: "#737373" }}>{dictionary.tooltip.name}: </span>
                                    <span style={{ color: "#fff", fontWeight: 600 }}>{character.name}</span>
                                </div>
                            )}

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
                            {character.description && (
                                <div
                                    style={{
                                        marginTop: "8px",
                                        paddingTop: "6px",
                                        borderTop: "1px solid rgba(57,255,20,0.12)",
                                        color: "#c9c4bb",
                                        lineHeight: 1.5,
                                    }}
                                >
                                    {character.description}
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
