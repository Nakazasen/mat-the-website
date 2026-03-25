"use client";

import { useEffect, useState } from "react";
import { useNovel } from "@/context/NovelContext";
import { getNovelSettings, updateNovelSettings } from "@/lib/api";

// =========================================================
// Types
// =========================================================
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

// =========================================================
// Helpers
// =========================================================
const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
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
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div style={{ marginBottom: "16px" }}>
      <div style={{
        display: "flex", justifyContent: "space-between",
        fontSize: "11px", color: "rgba(255,255,255,0.5)",
        letterSpacing: "0.12em", marginBottom: "5px",
        fontFamily: "'Courier Prime', monospace",
      }}>
        <span>{label}</span>
        <span style={{ color }}>
          {formatNumber(value)}{unit}
        </span>
      </div>
      <div style={{
        height: "4px", background: "rgba(255,255,255,0.07)",
        borderRadius: "2px", overflow: "hidden",
      }}>
        <div style={{
          height: "100%", width: `${pct}%`,
          background: color,
          borderRadius: "2px",
          transition: "width 1s cubic-bezier(0.23, 1, 0.32, 1)",
          boxShadow: `0 0 8px ${color}`,
        }} />
      </div>
    </div>
  );
}

function WallLevel({ level }: { level: number }) {
  return (
    <div style={{ display: "flex", gap: "5px", marginTop: "4px" }}>
      {[1, 2, 3, 4, 5].map((l) => (
        <div key={l} style={{
          flex: 1, height: "8px", borderRadius: "2px",
          background: l <= level ? "#39FF14" : "rgba(255,255,255,0.07)",
          boxShadow: l <= level ? "0 0 6px rgba(57,255,20,0.6)" : "none",
          transition: "background 0.4s ease",
        }} />
      ))}
    </div>
  );
}

// =========================================================
// Main component
// =========================================================
export default function HeadquartersPage() {
  const [chapter, setChapter] = useState<number>(() => {
    // Read last chapter from localStorage (set by ReadingClient)
    if (typeof window !== "undefined") {
      return parseInt(localStorage.getItem("lastReadChapter") ?? "1", 10);
    }
    return 1;
  });

  const [status, setStatus] = useState<HQStatus | null>(null);
  const [history, setHistory] = useState<HQHistoryPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // AI Model Config State
  const [aiModel, setAiModel] = useState("gemini-1.5-flash");
  const [isUpdatingModel, setIsUpdatingModel] = useState(false);
  const [modelUpdateMsg, setModelUpdateMsg] = useState("");

  const { novel } = useNovel();
  const maxChapter = novel?.max_chapter || 1000;

  // Initialize AI Model from novel settings
  useEffect(() => {
    if (novel?.ai_model_name) {
      setAiModel(novel.ai_model_name);
    }
  }, [novel]);

  const handleSaveModel = async () => {
    setIsUpdatingModel(true);
    setModelUpdateMsg("");
    try {
      await updateNovelSettings({ ai_model_name: aiModel });
      setModelUpdateMsg("Successfully updated AI model!");
      // Automatically clear message after 3 seconds
      setTimeout(() => setModelUpdateMsg(""), 3000);
    } catch (e: any) {
      setModelUpdateMsg(`Error: ${e.message}`);
    } finally {
      setIsUpdatingModel(false);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [statusRes, historyRes] = await Promise.all([
          fetch(`${BACKEND}/hq/status?chapter=${chapter}&faction=main`),
          fetch(`${BACKEND}/hq/history?chapter=${chapter}&faction=main&limit=5`),
        ]);

        if (!statusRes.ok) throw new Error(`Backend error: ${statusRes.status}`);
        const statusData = await statusRes.json();
        const historyData = historyRes.ok ? await historyRes.json() : [];

        setStatus(statusData);
        setHistory(historyData);
      } catch (e: any) {
        setError(e.message ?? "Không thể kết nối đến server.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [chapter]);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0a0a0a",
      color: "#d4d0c8",
      fontFamily: "'Inter', sans-serif",
      padding: "0 0 80px 0",
    }}>
      {/* ---- Header ---- */}
      <div style={{
        background: "rgba(13,13,13,0.95)",
        borderBottom: "1px solid rgba(57,255,20,0.15)",
        padding: "24px 20px 20px",
        position: "sticky", top: 0, zIndex: 10,
        backdropFilter: "blur(12px)",
      }}>
        <div style={{ maxWidth: "900px", margin: "0 auto" }}>
          <div style={{ fontSize: "9px", color: "rgba(57,255,20,0.5)", letterSpacing: "0.3em", marginBottom: "4px" }}>
            ◈ COMMAND CENTER — REAL-TIME INTEL
          </div>
          <h1 style={{
            fontFamily: "'Bebas Neue', Impact, sans-serif",
            fontSize: "clamp(1.8rem, 5vw, 2.5rem)",
            color: "#39FF14",
            letterSpacing: "0.1em",
            textShadow: "0 0 30px rgba(57,255,20,0.4)",
            margin: 0,
          }}>
            🏰 CĂN CỨ ĐỊA
          </h1>
          <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "13px", marginTop: "4px" }}>
            Trạng thái tài nguyên & nhân lực — Xem theo diễn biến truyện
          </p>

          {/* Chapter Selector */}
          <div style={{ marginTop: "12px", display: "flex", alignItems: "center", gap: "12px" }}>
            <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.4)", fontFamily: "monospace" }}>
              XEM TẠI CHƯƠNG:
            </span>
            <input
              type="range"
              min={1} max={maxChapter} value={chapter}
              onChange={(e) => setChapter(Number(e.target.value))}
              style={{
                flex: 1, maxWidth: "300px",
                accentColor: "#39FF14",
                cursor: "pointer",
              }}
            />
            <span style={{
              minWidth: "60px", textAlign: "center",
              fontFamily: "'Courier Prime', monospace",
              color: "#39FF14", fontSize: "14px", fontWeight: 700,
            }}>
              CH.{chapter}
            </span>
          </div>
        </div>
      </div>

      {/* ---- Main Content ---- */}
      <div style={{ maxWidth: "900px", margin: "32px auto", padding: "0 20px" }}>
        {isLoading && (
          <div style={{
            textAlign: "center", padding: "60px 0",
            fontFamily: "monospace", color: "rgba(57,255,20,0.6)",
            letterSpacing: "0.2em", fontSize: "13px",
          }}>
            ⟳ ĐANG KẾT NỐI VỚI HỆ THỐNG...
          </div>
        )}

        {error && (
          <div style={{
            textAlign: "center", padding: "40px",
            color: "#ef4444", background: "rgba(239,68,68,0.05)",
            border: "1px solid rgba(239,68,68,0.2)", borderRadius: "6px",
            fontFamily: "monospace", fontSize: "13px",
          }}>
            ⚠️ {error}
          </div>
        )}

        {status && !isLoading && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>

            {/* ---- Tài nguyên ---- */}
            <div style={{
              background: "rgba(26,26,26,0.8)",
              border: "1px solid rgba(57,255,20,0.12)",
              borderRadius: "8px", padding: "20px",
            }}>
              <div style={{
                fontSize: "9px", color: "rgba(57,255,20,0.5)",
                letterSpacing: "0.25em", marginBottom: "14px",
              }}>
                🌾 TÀI NGUYÊN
              </div>
              <StatBar label="LƯƠNG THỰC" value={status.food_days} max={365} color="#39FF14" unit=" ngày" />
              <StatBar label="TINH HẠCH" value={status.crystal_count} max={100000} color="#a855f7" />
              <StatBar label="NGUỒN NƯỚC" value={status.water_unit} max={1_000_000} color="#38bdf8" unit="L" />
            </div>

            {/* ---- Nhân lực ---- */}
            <div style={{
              background: "rgba(26,26,26,0.8)",
              border: "1px solid rgba(57,255,20,0.12)",
              borderRadius: "8px", padding: "20px",
            }}>
              <div style={{
                fontSize: "9px", color: "rgba(57,255,20,0.5)",
                letterSpacing: "0.25em", marginBottom: "14px",
              }}>
                👥 DÂN SỐ — {formatNumber(status.total_population)} người
              </div>
              <StatBar label="CHIẾN BINH" value={status.warriors} max={status.total_population || 1} color="#ef4444" />
              <StatBar label="NHÀ KHOA HỌC" value={status.researchers} max={status.total_population || 1} color="#f59e0b" />
              <StatBar label="DÂN THƯỜNG" value={status.civilians} max={status.total_population || 1} color="#6b7280" />
            </div>

            {/* ---- Cơ sở hạ tầng ---- */}
            <div style={{
              background: "rgba(26,26,26,0.8)",
              border: "1px solid rgba(57,255,20,0.12)",
              borderRadius: "8px", padding: "20px",
            }}>
              <div style={{
                fontSize: "9px", color: "rgba(57,255,20,0.5)",
                letterSpacing: "0.25em", marginBottom: "14px",
              }}>
                🏗️ CƠ SỞ HẠ TẦNG
              </div>

              <div style={{ marginBottom: "16px" }}>
                <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.5)", letterSpacing: "0.12em", marginBottom: "5px", fontFamily: "monospace" }}>
                  TƯỜNG PHÒNG THỦ (LV {status.wall_level}/5)
                </div>
                <WallLevel level={status.wall_level} />
              </div>

              <StatBar label="LÃNH THỔ" value={status.territory_km2} max={3000} color="#10b981" unit=" km²" />
              <StatBar label="SĨ KHÍ" value={status.morale} max={100} color="#f59e0b" unit="%" />
            </div>

            {/* ---- Last known chapter ---- */}
            <div style={{
              background: "rgba(26,26,26,0.8)",
              border: "1px solid rgba(57,255,20,0.12)",
              borderRadius: "8px", padding: "20px",
              gridColumn: "1 / -1",
              display: "flex", alignItems: "center", gap: "16px",
            }}>
              <div style={{ flex: 1 }}>
                <div style={{
                  fontSize: "9px", color: "rgba(57,255,20,0.5)",
                  letterSpacing: "0.25em", marginBottom: "6px",
                }}>
                  📡 PHÂN TÍCH DỮ LIỆU — CẬP NHẬT ĐẾN CHƯƠNG {status.chapter_id}
                </div>
                <p style={{ color: "rgba(255,255,255,0.5)", fontSize: "12px", lineHeight: 1.6, margin: 0 }}>
                  Dữ liệu mốc gần nhất được ghi nhận. Dữ liệu sẽ tự động cập nhật khi bạn kéo slider đến chương tiếp theo.
                  Nội dung tương lai được ẩn để tránh spoiler.
                </p>
              </div>
              <div style={{
                fontFamily: "'Bebas Neue', Impact, sans-serif",
                fontSize: "3rem", color: "rgba(57,255,20,0.15)",
                lineHeight: 1, flexShrink: 0,
              }}>
                ☣
              </div>
            </div>

            {/* ---- Cấu hình Hệ Thống (AI Model) ---- */}
            <div style={{
              background: "rgba(13,13,13,0.9)",
              border: "1px dashed rgba(57,255,20,0.3)",
              borderRadius: "8px", padding: "20px",
              gridColumn: "1 / -1",
              marginTop: "20px",
            }}>
              <div style={{
                fontSize: "9px", color: "#39FF14",
                letterSpacing: "0.25em", marginBottom: "14px",
                display: "flex", alignItems: "center", gap: "8px"
              }}>
                <span style={{ fontSize: "14px" }}>⚙</span> CẤU HÌNH HỆ THỐNG (TECHNICAL COMMAND)
              </div>
              
              <div style={{ display: "flex", flexWrap: "wrap", gap: "20px", alignItems: "flex-end" }}>
                <div style={{ flex: 1, minWidth: "250px" }}>
                  <label style={{ 
                    display: "block", fontSize: "11px", color: "rgba(255,255,255,0.4)", 
                    marginBottom: "8px", fontFamily: "monospace" 
                  }}>
                    AI MODEL (GEMINI NAME):
                  </label>
                  <input
                    type="text"
                    value={aiModel}
                    onChange={(e) => setAiModel(e.target.value)}
                    placeholder="e.g. gemini-1.5-flash"
                    style={{
                      width: "100%",
                      background: "rgba(0,0,0,0.3)",
                      border: "1px solid rgba(57,255,20,0.2)",
                      borderRadius: "4px",
                      padding: "10px 12px",
                      color: "#39FF14",
                      fontFamily: "'Courier Prime', monospace",
                      fontSize: "14px",
                      outline: "none",
                    }}
                  />
                  <p style={{ fontSize: "10px", color: "rgba(255,255,255,0.3)", marginTop: "6px" }}>
                    Nhập tên model Gemini (VD: gemini-3.1-flash-lite-preview, gemini-3.1-pro).
                  </p>
                </div>
                
                <button
                  onClick={handleSaveModel}
                  disabled={isUpdatingModel}
                  style={{
                    background: isUpdatingModel ? "rgba(57,255,20,0.1)" : "rgba(57,255,20,0.15)",
                    border: "1px solid #39FF14",
                    color: "#39FF14",
                    padding: "10px 24px",
                    borderRadius: "4px",
                    fontSize: "12px",
                    fontWeight: 600,
                    cursor: isUpdatingModel ? "not-allowed" : "pointer",
                    transition: "all 0.2s ease",
                    fontFamily: "monospace",
                    height: "42px",
                  }}
                  onMouseOver={(e) => (e.currentTarget.style.background = "rgba(57,255,20,0.25)")}
                  onMouseOut={(e) => (e.currentTarget.style.background = "rgba(57,255,20,0.15)")}
                >
                  {isUpdatingModel ? "LOADING..." : "UPDATE SYSTEM"}
                </button>
              </div>
              
              {modelUpdateMsg && (
                <div style={{ 
                  marginTop: "12px", fontSize: "12px", 
                  color: modelUpdateMsg.includes("Error") ? "#ef4444" : "#39FF14",
                  fontFamily: "monospace"
                }}>
                  {modelUpdateMsg}
                </div>
              )}
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
