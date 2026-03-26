"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { useLocale } from "@/context/LocaleContext";

interface Message {
    role: "user" | "oracle";
    text: string;
    source?: "cache" | "local_wiki" | "gemini";
}

interface OraclePanelProps {
    chapterProgress: number;
    defaultOpen?: boolean;
}

type DiagnosticCode =
    | "ready"
    | "processing"
    | "backend_offline"
    | "missing_api_key"
    | "rate_limited"
    | "model_exhausted"
    | "invalid_question"
    | "backend_error";

interface OracleErrorPayload {
    error?: string;
    error_code?: DiagnosticCode;
    answer?: string;
    source?: "cache" | "local_wiki" | "gemini";
}

interface FloatingPosition {
    x: number;
    y: number;
}

const BUTTON_SIZE = 48;
const PANEL_GAP = 10;

const DIAGNOSTIC_COLORS: Record<DiagnosticCode, { color: string; border: string }> = {
    ready: { color: "#39FF14", border: "rgba(57,255,20,0.35)" },
    processing: { color: "#fbbf24", border: "rgba(251,191,36,0.35)" },
    backend_offline: { color: "#f87171", border: "rgba(248,113,113,0.35)" },
    missing_api_key: { color: "#fb7185", border: "rgba(251,113,133,0.35)" },
    rate_limited: { color: "#f59e0b", border: "rgba(245,158,11,0.35)" },
    model_exhausted: { color: "#f97316", border: "rgba(249,115,22,0.35)" },
    invalid_question: { color: "#c084fc", border: "rgba(192,132,252,0.35)" },
    backend_error: { color: "#94a3b8", border: "rgba(148,163,184,0.35)" },
};

function getDefaultButtonPosition(isMobile: boolean): FloatingPosition {
    if (typeof window === "undefined") return { x: 0, y: 0 };
    const margin = isMobile ? 12 : 24;
    const bottomOffset = isMobile ? 84 : 24;
    return {
        x: window.innerWidth - BUTTON_SIZE - margin,
        y: window.innerHeight - BUTTON_SIZE - bottomOffset,
    };
}

function clampButtonPosition(position: FloatingPosition): FloatingPosition {
    if (typeof window === "undefined") return position;
    const margin = 8;
    return {
        x: Math.min(Math.max(position.x, margin), window.innerWidth - BUTTON_SIZE - margin),
        y: Math.min(Math.max(position.y, margin), window.innerHeight - BUTTON_SIZE - margin),
    };
}

export default function OraclePanel({
    chapterProgress,
    defaultOpen = false,
}: OraclePanelProps) {
    const { dictionary } = useLocale();
    const [isOpen, setIsOpen] = useState(defaultOpen);
    const [messages, setMessages] = useState<Message[]>([{ role: "oracle", text: dictionary.oracle.readyMessage(chapterProgress) }]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [diagnostic, setDiagnostic] = useState<DiagnosticCode>("ready");
    const [isMobile, setIsMobile] = useState(false);
    const [buttonPosition, setButtonPosition] = useState<FloatingPosition>({ x: 0, y: 0 });
    const [hasCustomPosition, setHasCustomPosition] = useState(false);
    const [dragState, setDragState] = useState<{ offsetX: number; offsetY: number } | null>(null);
    const bottomRef = useRef<HTMLDivElement>(null);
    const buttonRef = useRef<HTMLButtonElement>(null);

    useEffect(() => {
        const updateViewport = () => {
            const mobile = window.innerWidth < 768;
            setIsMobile(mobile);
            setButtonPosition((prev) => (hasCustomPosition ? clampButtonPosition(prev) : getDefaultButtonPosition(mobile)));
        };
        updateViewport();
        window.addEventListener("resize", updateViewport);
        return () => window.removeEventListener("resize", updateViewport);
    }, [hasCustomPosition]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [diagnostic, isOpen, messages]);

    useEffect(() => {
        setMessages([{ role: "oracle", text: dictionary.oracle.readyMessage(chapterProgress) }]);
        setDiagnostic("ready");
    }, [chapterProgress, dictionary]);

    useEffect(() => {
        if (!dragState) return;

        const handlePointerMove = (event: PointerEvent) => {
            setButtonPosition(clampButtonPosition({
                x: event.clientX - dragState.offsetX,
                y: event.clientY - dragState.offsetY,
            }));
        };
        const handlePointerUp = () => {
            setDragState(null);
            setHasCustomPosition(true);
        };

        window.addEventListener("pointermove", handlePointerMove);
        window.addEventListener("pointerup", handlePointerUp);
        return () => {
            window.removeEventListener("pointermove", handlePointerMove);
            window.removeEventListener("pointerup", handlePointerUp);
        };
    }, [dragState]);

    const panelMetrics = useMemo(() => {
        if (typeof window === "undefined") {
            return { width: 340, maxHeight: 500, left: 0, top: 0 };
        }
        const width = isMobile ? Math.min(340, window.innerWidth - 24) : Math.min(380, window.innerWidth - 40);
        const maxHeight = isMobile ? Math.floor(window.innerHeight * 0.52) : 500;
        const preferredLeft = buttonPosition.x + BUTTON_SIZE - width;
        const left = Math.min(Math.max(preferredLeft, 12), window.innerWidth - width - 12);
        const preferredTop = buttonPosition.y - maxHeight - PANEL_GAP;
        const top = Math.max(12, preferredTop);
        return { width, maxHeight, left, top };
    }, [buttonPosition.x, buttonPosition.y, isMobile]);

    const submitQuestion = async (question: string) => {
        const trimmed = question.trim();
        if (!trimmed || isLoading) return;

        setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
        setInput("");
        setIsLoading(true);
        setDiagnostic("processing");

        try {
            const response = await fetch("/api/oracle/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: trimmed,
                    chapter_progress: chapterProgress,
                }),
            });

            const payload = (await response.json().catch(() => ({}))) as OracleErrorPayload;
            if (!response.ok) {
                const code = payload.error_code ?? "backend_error";
                setDiagnostic(code);
                setMessages((prev) => [
                    ...prev,
                    {
                        role: "oracle",
                        text: payload.error ?? dictionary.oracle.unknownError,
                    },
                ]);
                return;
            }

            setDiagnostic("ready");
            setMessages((prev) => [
                ...prev,
                {
                    role: "oracle",
                    text: payload.answer ?? dictionary.oracle.invalidResponse,
                    source: payload.source,
                },
            ]);
        } catch {
            setDiagnostic("backend_offline");
            setMessages((prev) => [...prev, { role: "oracle", text: dictionary.oracle.backendOffline }]);
        } finally {
            setIsLoading(false);
        }
    };

    const diagnosticLabel = dictionary.oracle.diagnostics[diagnostic];
    const diagnosticMeta = DIAGNOSTIC_COLORS[diagnostic];

    return (
        <>
            <button
                ref={buttonRef}
                onClick={() => {
                    if (!dragState) setIsOpen((prev) => !prev);
                }}
                onPointerDown={(event) => {
                    if (!buttonRef.current) return;
                    const rect = buttonRef.current.getBoundingClientRect();
                    setDragState({
                        offsetX: event.clientX - rect.left,
                        offsetY: event.clientY - rect.top,
                    });
                }}
                title={dictionary.oracle.title}
                style={{
                    position: "fixed",
                    left: `${buttonPosition.x}px`,
                    top: `${buttonPosition.y}px`,
                    width: `${BUTTON_SIZE}px`,
                    height: `${BUTTON_SIZE}px`,
                    borderRadius: "50%",
                    background: isOpen ? "rgba(220, 38, 38, 0.92)" : "rgba(57, 255, 20, 0.12)",
                    border: `2px solid ${isOpen ? "#dc2626" : "rgba(57,255,20,0.45)"}`,
                    color: isOpen ? "#fff" : "#39FF14",
                    fontSize: "18px",
                    cursor: dragState ? "grabbing" : "grab",
                    zIndex: 60,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: isOpen ? "0 0 20px rgba(220,38,38,0.4)" : "0 0 20px rgba(57,255,20,0.25)",
                    transition: dragState ? "none" : "all 0.25s ease",
                    backdropFilter: "blur(8px)",
                    touchAction: "none",
                    userSelect: "none",
                }}
            >
                {isOpen ? "X" : "AI"}
            </button>

            {isOpen && (
                <div
                    style={{
                        position: "fixed",
                        left: `${panelMetrics.left}px`,
                        top: `${panelMetrics.top}px`,
                        width: `${panelMetrics.width}px`,
                        maxHeight: `${panelMetrics.maxHeight}px`,
                        background: "rgba(10, 10, 10, 0.97)",
                        border: "1px solid rgba(57, 255, 20, 0.2)",
                        borderRadius: "10px",
                        display: "flex",
                        flexDirection: "column",
                        zIndex: 59,
                        boxShadow: "0 0 40px rgba(57,255,20,0.08), 0 25px 50px rgba(0,0,0,0.8)",
                        backdropFilter: "blur(20px)",
                        overflow: "hidden",
                    }}
                >
                    <div style={{ padding: "12px 14px 10px", borderBottom: "1px solid rgba(57,255,20,0.1)", background: "rgba(15,15,15,0.5)" }}>
                        <div style={{ fontSize: "9px", letterSpacing: "0.25em", color: "rgba(57,255,20,0.5)" }}>
                            {dictionary.oracle.title.toUpperCase()}
                        </div>
                        <div style={{ fontFamily: "'Courier Prime', monospace", color: "#39FF14", fontSize: "12px", marginTop: "2px" }}>
                            {dictionary.oracle.scope}: 1-{chapterProgress} | {dictionary.oracle.antiSpoiler}
                        </div>
                        <div
                            style={{
                                marginTop: "8px",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "6px",
                                padding: "4px 8px",
                                borderRadius: "999px",
                                border: `1px solid ${diagnosticMeta.border}`,
                                color: diagnosticMeta.color,
                                fontSize: "10px",
                                fontFamily: "monospace",
                                letterSpacing: "0.08em",
                                background: "rgba(255,255,255,0.02)",
                            }}
                        >
                            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: diagnosticMeta.color, boxShadow: `0 0 10px ${diagnosticMeta.color}` }} />
                            {diagnosticLabel}
                        </div>
                    </div>

                    <div style={{ flex: 1, overflowY: "auto", padding: "12px", display: "flex", flexDirection: "column", gap: "10px" }}>
                        {messages.map((message, index) => (
                            <div key={`${message.role}-${index}`} style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                                <div
                                    style={{
                                        alignSelf: message.role === "user" ? "flex-end" : "flex-start",
                                        maxWidth: "88%",
                                        padding: "8px 12px",
                                        borderRadius: message.role === "user" ? "12px 12px 4px 12px" : "12px 12px 12px 4px",
                                        background: message.role === "user" ? "rgba(57,255,20,0.12)" : "rgba(30,30,30,0.8)",
                                        border: `1px solid ${message.role === "user" ? "rgba(57,255,20,0.3)" : "rgba(255,255,255,0.06)"}`,
                                        fontSize: "12px",
                                        lineHeight: 1.6,
                                        color: message.role === "user" ? "rgba(255,255,255,0.92)" : "#d4d0c8",
                                        fontFamily: message.role === "oracle" ? "'Courier Prime', monospace" : undefined,
                                        whiteSpace: "pre-wrap",
                                    }}
                                >
                                    {message.text}
                                </div>
                                {message.source && (
                                    <div style={{ fontSize: "9px", color: "rgba(255,255,255,0.25)", fontFamily: "monospace", paddingLeft: "4px" }}>
                                        {dictionary.oracle.sources[message.source] ?? message.source}
                                    </div>
                                )}
                            </div>
                        ))}

                        {isLoading && (
                            <div style={{ fontFamily: "monospace", fontSize: "11px", color: "rgba(57,255,20,0.5)", letterSpacing: "0.15em", animation: "hud-bar-blink 1s ease infinite" }}>
                                {dictionary.oracle.diagnostics.processing}...
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>

                    <div style={{ padding: "0 12px 10px", display: "flex", flexWrap: "wrap", gap: "8px" }}>
                        {dictionary.oracle.quickPrompts.map((prompt) => (
                            <button
                                key={prompt}
                                type="button"
                                onClick={() => submitQuestion(prompt)}
                                disabled={isLoading}
                                style={{
                                    background: "rgba(57,255,20,0.08)",
                                    border: "1px solid rgba(57,255,20,0.18)",
                                    borderRadius: "999px",
                                    padding: "6px 10px",
                                    color: "#baf7ab",
                                    fontSize: "11px",
                                    cursor: isLoading ? "not-allowed" : "pointer",
                                    opacity: isLoading ? 0.5 : 1,
                                }}
                            >
                                {prompt}
                            </button>
                        ))}
                    </div>

                    <form
                        onSubmit={(event) => {
                            event.preventDefault();
                            submitQuestion(input);
                        }}
                        style={{ display: "flex", gap: "8px", padding: "10px 12px", borderTop: "1px solid rgba(57,255,20,0.1)", background: "rgba(15,15,15,0.5)" }}
                    >
                        <input
                            value={input}
                            onChange={(event) => setInput(event.target.value)}
                            placeholder={dictionary.oracle.placeholder}
                            maxLength={500}
                            disabled={isLoading}
                            style={{
                                flex: 1,
                                background: "rgba(255,255,255,0.04)",
                                border: "1px solid rgba(57,255,20,0.15)",
                                borderRadius: "6px",
                                padding: "7px 10px",
                                fontSize: "12px",
                                color: "#d4d0c8",
                                outline: "none",
                                fontFamily: "monospace",
                            }}
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !input.trim()}
                            style={{
                                background: "rgba(57,255,20,0.12)",
                                border: "1px solid rgba(57,255,20,0.3)",
                                borderRadius: "6px",
                                padding: "7px 12px",
                                color: "#39FF14",
                                fontSize: "11px",
                                cursor: isLoading || !input.trim() ? "not-allowed" : "pointer",
                                opacity: isLoading || !input.trim() ? 0.5 : 1,
                                fontFamily: "monospace",
                            }}
                        >
                            {dictionary.oracle.submit}
                        </button>
                    </form>
                </div>
            )}
        </>
    );
}
