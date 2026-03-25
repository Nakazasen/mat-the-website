"use client";

import { useEffect, useState } from "react";
import type { CharacterStatus, DangerLevel } from "@/hooks/useChapterMeta";

interface SystemHUDProps {
  chapterNumber: number;
  totalChapters: number;
  readingProgress: number;
  dangerLevel: DangerLevel;
  dangerLabel: string;
  dangerColor: string;
  characterStatus: CharacterStatus;
}

const HEARTBEAT_PATHS = {
  normal: "M0,15 L8,15 L12,5 L16,25 L20,15 L28,15",
  danger: "M0,15 L6,15 L10,2 L14,28 L18,2 L22,28 L26,15 L28,15",
};

const STATUS_COLORS: Record<string, string> = {
  "Bình thường": "#39FF14",
  "Bị thương": "#f59e0b",
  "Dị biến": "#a855f7",
  "Nguy kịch": "#ef4444",
};

export default function SystemHUD({
  chapterNumber,
  totalChapters,
  readingProgress,
  dangerLevel,
  dangerLabel,
  dangerColor,
  characterStatus,
}: SystemHUDProps) {
  const [tick, setTick] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const updateViewport = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      setIsMinimized(mobile);
    };
    updateViewport();
    window.addEventListener("resize", updateViewport);
    return () => window.removeEventListener("resize", updateViewport);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 800);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setTick((t) => (t + 1) % 100);
    }, dangerLevel >= 2 ? 600 : 1200);
    return () => clearInterval(interval);
  }, [dangerLevel]);

  const statusColor = STATUS_COLORS[characterStatus] ?? "#39FF14";
  const isExtreme = dangerLevel === 3;
  const isCombat = dangerLevel >= 2;
  const heartPath = isCombat ? HEARTBEAT_PATHS.danger : HEARTBEAT_PATHS.normal;

  return (
    <div
      style={{
        position: "fixed",
        right: isMinimized ? "-160px" : "0",
        top: isMobile ? "42%" : "50%",
        transform: "translateY(-50%)",
        zIndex: 500,
        transition: "right 0.4s cubic-bezier(0.23, 1, 0.32, 1), opacity 0.6s ease",
        opacity: isVisible ? 1 : 0,
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        userSelect: "none",
        pointerEvents: "auto",
      }}
    >
      <button
        onClick={() => setIsMinimized((prev) => !prev)}
        title={isMinimized ? "Mở HUD" : "Thu gọn HUD"}
        style={{
          background: "rgba(10,10,10,0.85)",
          border: "1px solid rgba(57,255,20,0.3)",
          borderRight: "none",
          color: "#39FF14",
          padding: "8px 4px",
          cursor: "pointer",
          fontSize: "10px",
          fontFamily: "monospace",
          letterSpacing: "0.1em",
          writingMode: "vertical-rl",
          borderRadius: "4px 0 0 4px",
          backdropFilter: "blur(8px)",
          flexShrink: 0,
        }}
      >
        {isMinimized ? "MỞ HUD" : "HUD THU"}
      </button>

      <div
        style={{
          width: "160px",
          background: "rgba(8, 10, 8, 0.88)",
          border: `1px solid ${isExtreme ? "rgba(220,38,38,0.6)" : "rgba(57,255,20,0.25)"}`,
          borderLeft: "none",
          backdropFilter: "blur(12px)",
          padding: "12px 10px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          fontFamily: "'Courier Prime', 'JetBrains Mono', monospace",
          boxShadow: isExtreme
            ? "0 0 30px rgba(220,38,38,0.15), inset 0 0 20px rgba(220,38,38,0.05)"
            : "0 0 20px rgba(57,255,20,0.05)",
          animation: isExtreme ? "hud-danger-pulse 1.2s ease-in-out infinite" : undefined,
        }}
      >
        <div
          style={{
            fontSize: "9px",
            color: "rgba(57,255,20,0.6)",
            letterSpacing: "0.2em",
            borderBottom: "1px solid rgba(57,255,20,0.15)",
            paddingBottom: "6px",
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <span>THE SYSTEM</span>
          <span style={{ color: "rgba(57,255,20,0.4)" }}>v2.1</span>
        </div>

        <div>
          <div style={{ fontSize: "8px", color: "rgba(255,255,255,0.4)", letterSpacing: "0.15em", marginBottom: "4px" }}>
            DANGER LEVEL
          </div>
          <div style={{ display: "flex", gap: "3px", marginBottom: "3px" }}>
            {[0, 1, 2, 3].map((level) => (
              <div
                key={level}
                style={{
                  flex: 1,
                  height: "6px",
                  borderRadius: "1px",
                  background: level <= dangerLevel ? dangerColor : "rgba(255,255,255,0.08)",
                  transition: "background 0.4s ease",
                  animation:
                    level === dangerLevel && dangerLevel > 0
                      ? "hud-bar-blink 1s ease-in-out infinite"
                      : undefined,
                }}
              />
            ))}
          </div>
          <div style={{ fontSize: "10px", color: dangerColor, letterSpacing: "0.08em", fontWeight: 700 }}>
            {dangerLabel}
          </div>
        </div>

        <div>
          <div style={{ fontSize: "8px", color: "rgba(255,255,255,0.4)", letterSpacing: "0.15em", marginBottom: "4px" }}>
            BIO-MONITOR
          </div>
          <svg width="100%" height="30" viewBox="0 0 28 30" style={{ overflow: "visible" }}>
            <line x1="0" y1="15" x2="28" y2="15" stroke="rgba(57,255,20,0.08)" strokeWidth="0.5" />
            <path
              d={heartPath}
              fill="none"
              stroke={statusColor}
              strokeWidth="1.5"
              strokeLinecap="round"
              style={{ filter: `drop-shadow(0 0 3px ${statusColor})`, transition: "d 0.4s ease, stroke 0.4s ease" }}
            />
            <line
              x1={((tick % 30) / 30) * 28}
              y1="0"
              x2={((tick % 30) / 30) * 28}
              y2="30"
              stroke="rgba(57,255,20,0.3)"
              strokeWidth="0.5"
            />
          </svg>
        </div>

        <div>
          <div style={{ fontSize: "8px", color: "rgba(255,255,255,0.4)", letterSpacing: "0.15em", marginBottom: "4px" }}>
            MC STATUS
          </div>
          <div
            style={{
              fontSize: "10px",
              color: statusColor,
              fontWeight: 700,
              letterSpacing: "0.05em",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <span
              style={{
                display: "inline-block",
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                background: statusColor,
                boxShadow: `0 0 6px ${statusColor}`,
                animation: "hud-dot-pulse 1.5s ease-in-out infinite",
                flexShrink: 0,
              }}
            />
            {characterStatus}
          </div>
        </div>

        <div>
          <div
            style={{
              fontSize: "8px",
              color: "rgba(255,255,255,0.4)",
              letterSpacing: "0.15em",
              marginBottom: "4px",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <span>CHƯƠNG</span>
            <span style={{ color: "rgba(57,255,20,0.7)" }}>
              {chapterNumber}/{totalChapters}
            </span>
          </div>
          <div style={{ height: "3px", background: "rgba(255,255,255,0.08)", borderRadius: "2px", overflow: "hidden" }}>
            <div
              style={{
                height: "100%",
                width: `${(chapterNumber / totalChapters) * 100}%`,
                background: "linear-gradient(90deg, rgba(57,255,20,0.5), #39FF14)",
                borderRadius: "2px",
                transition: "width 0.5s ease",
              }}
            />
          </div>
        </div>

        <div>
          <div
            style={{
              fontSize: "8px",
              color: "rgba(255,255,255,0.4)",
              letterSpacing: "0.15em",
              marginBottom: "4px",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <span>TIẾN ĐỘ ĐỌC</span>
            <span style={{ color: "rgba(57,255,20,0.7)" }}>{Math.round(readingProgress)}%</span>
          </div>
          <div style={{ height: "3px", background: "rgba(255,255,255,0.08)", borderRadius: "2px", overflow: "hidden" }}>
            <div
              style={{
                height: "100%",
                width: `${readingProgress}%`,
                background: "linear-gradient(90deg, rgba(57,255,20,0.3), #39FF14)",
                borderRadius: "2px",
                transition: "width 0.2s linear",
              }}
            />
          </div>
        </div>

        <div
          style={{
            fontSize: "8px",
            color: "rgba(57,255,20,0.25)",
            letterSpacing: "0.1em",
            borderTop: "1px solid rgba(57,255,20,0.1)",
            paddingTop: "6px",
            textAlign: "center",
          }}
        >
          SYS-UPLINK
        </div>
      </div>
    </div>
  );
}
