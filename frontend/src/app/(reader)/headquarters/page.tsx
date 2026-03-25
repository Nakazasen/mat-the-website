"use client";

import { useEffect, useState } from "react";
import { useNovel } from "@/context/NovelContext";

interface HQStatus {
    chapter_id: number;
    faction: string;
    food_days: number;
    crystal_count: number;
    water_unit: number;
    warriors: number;
    researchers: number;
    civilians: number;
    wall_level: number;
    territory_km2: number;
    morale: number;
    total_population: number;
}

interface HQHistoryPoint {
    chapter_id: number;
    food_days: number;
    crystal_count: number;
    warriors: number;
    morale: number;
}

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function formatNumber(value: number): string {
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
    return `${value}`;
}

function StatBar({
    label,
    value,
    max,
    color,
    unit = "",
}: {
    label: string;
    value: number;
    max: number;
    color: string;
    unit?: string;
}) {
    const pct = Math.min(100, Math.max(0, (value / Math.max(max, 1)) * 100));
    return (
        <div style={{ marginBottom: 16 }}>
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: 11,
                    color: "rgba(255,255,255,0.55)",
                    letterSpacing: "0.12em",
                    marginBottom: 6,
                    fontFamily: "monospace",
                }}
            >
                <span>{label}</span>
                <span style={{ color }}>
                    {formatNumber(value)}
                    {unit}
                </span>
            </div>
            <div
                style={{
                    height: 5,
                    background: "rgba(255,255,255,0.08)",
                    borderRadius: 3,
                    overflow: "hidden",
                }}
            >
                <div
                    style={{
                        height: "100%",
                        width: `${pct}%`,
                        background: color,
                        boxShadow: `0 0 8px ${color}`,
                        transition: "width 350ms ease",
                    }}
                />
            </div>
        </div>
    );
}

function WallLevel({ level }: { level: number }) {
    return (
        <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
            {[1, 2, 3, 4, 5].map((slot) => (
                <div
                    key={slot}
                    style={{
                        flex: 1,
                        height: 8,
                        borderRadius: 3,
                        background: slot <= level ? "#39FF14" : "rgba(255,255,255,0.08)",
                        boxShadow: slot <= level ? "0 0 8px rgba(57,255,20,0.55)" : "none",
                    }}
                />
            ))}
        </div>
    );
}

export default function HeadquartersPage() {
    const [chapter, setChapter] = useState<number>(() => {
        if (typeof window !== "undefined") {
            const stored = Number.parseInt(localStorage.getItem("lastReadChapter") ?? "1", 10);
            return Number.isFinite(stored) && stored > 0 ? stored : 1;
        }
        return 1;
    });

    const [status, setStatus] = useState<HQStatus | null>(null);
    const [history, setHistory] = useState<HQHistoryPoint[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const { novel } = useNovel();
    const maxChapter = novel?.max_chapter || 1000;

    useEffect(() => {
        const fetchData = async () => {
            setIsLoading(true);
            setError(null);

            try {
                const [statusRes, historyRes] = await Promise.all([
                    fetch(`${BACKEND}/hq/status?chapter=${chapter}&faction=main`, { cache: "no-store" }),
                    fetch(`${BACKEND}/hq/history?chapter=${chapter}&faction=main&limit=5`, { cache: "no-store" }),
                ]);

                if (!statusRes.ok) {
                    throw new Error(`Khong th? t?i d? li?u HQ (${statusRes.status})`);
                }

                const statusData = (await statusRes.json()) as HQStatus;
                const historyData = historyRes.ok ? ((await historyRes.json()) as HQHistoryPoint[]) : [];

                setStatus(statusData);
                setHistory(Array.isArray(historyData) ? historyData : []);
            } catch (e: any) {
                setError(e?.message ?? "Khong th? k?t n?i d? li?u Headquarters.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, [chapter]);

    return (
        <div
            style={{
                minHeight: "100vh",
                background: "#090b0a",
                color: "#d4d0c8",
                paddingBottom: 64,
            }}
        >
            <div
                style={{
                    position: "sticky",
                    top: 0,
                    zIndex: 10,
                    background: "rgba(10,12,11,0.92)",
                    borderBottom: "1px solid rgba(57,255,20,0.15)",
                    backdropFilter: "blur(10px)",
                }}
            >
                <div style={{ maxWidth: 920, margin: "0 auto", padding: "20px 20px 16px" }}>
                    <div style={{ fontSize: 10, color: "rgba(57,255,20,0.55)", letterSpacing: "0.26em" }}>
                        HEADQUARTERS FEED
                    </div>
                    <h1
                        style={{
                            margin: "6px 0 0",
                            fontSize: "clamp(1.7rem, 4.8vw, 2.4rem)",
                            color: "#39FF14",
                            letterSpacing: "0.06em",
                        }}
                    >
                        S? Ch? Huy
                    </h1>
                    <p style={{ margin: "6px 0 0", fontSize: 13, color: "rgba(255,255,255,0.52)" }}>
                        B?ng ?i?u hanh nh?p vai theo di?n bi?n ch??ng, khong l? d? li?u t??ng lai.
                    </p>

                    <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 12 }}>
                        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.45)", fontFamily: "monospace" }}>
                            CH??NG:
                        </span>
                        <input
                            type="range"
                            min={1}
                            max={maxChapter}
                            value={chapter}
                            onChange={(event) => setChapter(Number(event.target.value))}
                            style={{ flex: 1, maxWidth: 320, accentColor: "#39FF14", cursor: "pointer" }}
                        />
                        <span style={{ minWidth: 72, textAlign: "center", color: "#39FF14", fontFamily: "monospace" }}>
                            CH.{chapter}
                        </span>
                    </div>
                </div>
            </div>

            <div style={{ maxWidth: 920, margin: "28px auto 0", padding: "0 20px" }}>
                {isLoading && (
                    <div style={{ textAlign: "center", padding: "56px 0", color: "rgba(57,255,20,0.6)", fontFamily: "monospace" }}>
                        ?ang ??ng b? d? li?u HQ...
                    </div>
                )}

                {error && (
                    <div
                        style={{
                            border: "1px solid rgba(239,68,68,0.25)",
                            background: "rgba(127,29,29,0.18)",
                            color: "#fca5a5",
                            borderRadius: 8,
                            padding: 14,
                            fontSize: 13,
                        }}
                    >
                        {error}
                    </div>
                )}

                {status && !isLoading && !error && (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 18 }}>
                        <section style={{ background: "rgba(20,24,22,0.8)", border: "1px solid rgba(57,255,20,0.14)", borderRadius: 8, padding: 18 }}>
                            <div style={{ fontSize: 10, color: "rgba(57,255,20,0.55)", letterSpacing: "0.2em", marginBottom: 12 }}>TAI NGUYEN</div>
                            <StatBar label="L??ng th?c" value={status.food_days} max={365} color="#39FF14" unit=" ngay" />
                            <StatBar label="Tinh h?ch" value={status.crystal_count} max={100_000} color="#a855f7" />
                            <StatBar label="N??c" value={status.water_unit} max={1_000_000} color="#38bdf8" unit="L" />
                        </section>

                        <section style={{ background: "rgba(20,24,22,0.8)", border: "1px solid rgba(57,255,20,0.14)", borderRadius: 8, padding: 18 }}>
                            <div style={{ fontSize: 10, color: "rgba(57,255,20,0.55)", letterSpacing: "0.2em", marginBottom: 12 }}>
                                NHAN L?C ({formatNumber(status.total_population)})
                            </div>
                            <StatBar label="Chi?n binh" value={status.warriors} max={status.total_population || 1} color="#ef4444" />
                            <StatBar label="Nghien c?u" value={status.researchers} max={status.total_population || 1} color="#f59e0b" />
                            <StatBar label="Dan th??ng" value={status.civilians} max={status.total_population || 1} color="#6b7280" />
                        </section>

                        <section style={{ background: "rgba(20,24,22,0.8)", border: "1px solid rgba(57,255,20,0.14)", borderRadius: 8, padding: 18 }}>
                            <div style={{ fontSize: 10, color: "rgba(57,255,20,0.55)", letterSpacing: "0.2em", marginBottom: 12 }}>C? S? H? T?NG</div>
                            <div style={{ marginBottom: 16 }}>
                                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.55)", fontFamily: "monospace", marginBottom: 6 }}>
                                    T??ng phong th? (Lv {status.wall_level}/5)
                                </div>
                                <WallLevel level={status.wall_level} />
                            </div>
                            <StatBar label="Lanh th?" value={status.territory_km2} max={3000} color="#10b981" unit=" km2" />
                            <StatBar label="S? khi" value={status.morale} max={100} color="#f59e0b" unit="%" />
                        </section>

                        <section
                            style={{
                                gridColumn: "1 / -1",
                                background: "rgba(14,18,16,0.82)",
                                border: "1px solid rgba(57,255,20,0.14)",
                                borderRadius: 8,
                                padding: 18,
                            }}
                        >
                            <div style={{ fontSize: 10, color: "rgba(57,255,20,0.55)", letterSpacing: "0.2em", marginBottom: 8 }}>
                                D?U M?C G?N NH?T: CH??NG {status.chapter_id}
                            </div>
                            <p style={{ margin: 0, fontSize: 13, lineHeight: 1.65, color: "rgba(255,255,255,0.55)" }}>
                                D? li?u ch? hi?n th? theo ch??ng b?n ch?n ?? gi? tr?i nghi?m spoiler-safe.
                            </p>
                            {history.length > 0 && (
                                <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 8 }}>
                                    {history.map((point) => (
                                        <span
                                            key={point.chapter_id}
                                            style={{
                                                fontFamily: "monospace",
                                                fontSize: 11,
                                                color: "rgba(255,255,255,0.65)",
                                                border: "1px solid rgba(255,255,255,0.12)",
                                                borderRadius: 999,
                                                padding: "4px 10px",
                                            }}
                                        >
                                            CH.{point.chapter_id} F:{point.food_days} C:{formatNumber(point.crystal_count)} M:{point.morale}%
                                        </span>
                                    ))}
                                </div>
                            )}
                        </section>
                    </div>
                )}
            </div>
        </div>
    );
}
