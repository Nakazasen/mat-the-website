"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "oracle";
  text: string;
  source?: "cache" | "local_wiki" | "gemini";
}

interface OraclePanelProps {
  chapterProgress: number;
  defaultOpen?: boolean;
}

const SOURCE_LABELS: Record<string, string> = {
  cache: "⚡ Bộ nhớ cache",
  local_wiki: "📖 Bách khoa địa phương",
  gemini: "🤖 AI Oracle",
};

export default function OraclePanel({ chapterProgress, defaultOpen = false }: OraclePanelProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "oracle",
      text: `[HỆ THỐNG ĐÃ KHỞI ĐỘNG]\nKết nối thành công. Tiến trình đọc: Chương ${chapterProgress}.\nTôi chỉ tiết lộ thông tin trong phạm vi bạn đã đọc. Hãy đặt câu hỏi.`,
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [remaining, setRemaining] = useState<number | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || isLoading) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("/api/oracle/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, chapter_progress: chapterProgress }),
      });

      if (res.status === 429) {
        setMessages((prev) => [
          ...prev,
          {
            role: "oracle",
            text: "[CẢNH BÁO HỆ THỐNG] Băng thông AI đã cạn kiệt hôm nay. Thử lại vào ngày mai.",
            source: undefined,
          },
        ]);
        return;
      }

      if (!res.ok) {
        throw new Error(`Server error ${res.status}`);
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "oracle", text: data.answer, source: data.source },
      ]);

      if (data.source === "gemini" && remaining !== null) {
        setRemaining((r) => (r !== null ? Math.max(0, r - 1) : null));
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "oracle",
          text: "[LỖI HỆ THỐNG] Mất kết nối với Oracle. Thử lại sau.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Toggle button (fixed bottom-right) */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        title="AI Oracle"
        style={{
          position: "fixed",
          bottom: "24px",
          right: "36px", // Offset from HUD tab on the right
          width: "44px",
          height: "44px",
          borderRadius: "50%",
          background: isOpen
            ? "rgba(220, 38, 38, 0.9)"
            : "rgba(57, 255, 20, 0.1)",
          border: `2px solid ${isOpen ? "#dc2626" : "rgba(57,255,20,0.4)"}`,
          color: isOpen ? "#fff" : "#39FF14",
          fontSize: "20px",
          cursor: "pointer",
          zIndex: 60,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: isOpen
            ? "0 0 20px rgba(220,38,38,0.4)"
            : "0 0 20px rgba(57,255,20,0.2)",
          transition: "all 0.25s ease",
          backdropFilter: "blur(8px)",
        }}
      >
        {isOpen ? "✕" : "🤖"}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div
          style={{
            position: "fixed",
            bottom: "80px",
            right: "20px",
            width: "clamp(300px, 90vw, 380px)",
            maxHeight: "500px",
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
          {/* Header */}
          <div
            style={{
              padding: "12px 14px 10px",
              borderBottom: "1px solid rgba(57,255,20,0.1)",
              background: "rgba(15,15,15,0.5)",
            }}
          >
            <div style={{ fontSize: "9px", letterSpacing: "0.25em", color: "rgba(57,255,20,0.5)" }}>
              ◈ AI ORACLE — THE SYSTEM
            </div>
            <div
              style={{
                fontFamily: "'Courier Prime', monospace",
                color: "#39FF14",
                fontSize: "12px",
                marginTop: "2px",
              }}
            >
              Phạm vi: Chương 1–{chapterProgress} | Chống spoiler ON
            </div>
          </div>

          {/* Message list */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "12px",
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            {messages.map((m, i) => (
              <div key={i} style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                <div
                  style={{
                    alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                    maxWidth: "85%",
                    padding: "8px 12px",
                    borderRadius: m.role === "user" ? "12px 12px 4px 12px" : "12px 12px 12px 4px",
                    background:
                      m.role === "user"
                        ? "rgba(57,255,20,0.12)"
                        : "rgba(30,30,30,0.8)",
                    border: `1px solid ${
                      m.role === "user"
                        ? "rgba(57,255,20,0.3)"
                        : "rgba(255,255,255,0.06)"
                    }`,
                    fontSize: "12px",
                    lineHeight: 1.6,
                    color: m.role === "user" ? "rgba(255,255,255,0.9)" : "#d4d0c8",
                    fontFamily: m.role === "oracle" ? "'Courier Prime', monospace" : undefined,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {m.text}
                </div>
                {m.source && (
                  <div
                    style={{
                      fontSize: "9px",
                      color: "rgba(255,255,255,0.25)",
                      fontFamily: "monospace",
                      paddingLeft: "4px",
                    }}
                  >
                    {SOURCE_LABELS[m.source] ?? m.source}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div
                style={{
                  fontFamily: "monospace",
                  fontSize: "11px",
                  color: "rgba(57,255,20,0.5)",
                  letterSpacing: "0.15em",
                  animation: "hud-bar-blink 1s ease infinite",
                }}
              >
                ⟳ ĐANG XỬ LÝ...
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <form
            onSubmit={handleSubmit}
            style={{
              display: "flex",
              gap: "8px",
              padding: "10px 12px",
              borderTop: "1px solid rgba(57,255,20,0.1)",
              background: "rgba(15,15,15,0.5)",
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Đặt câu hỏi cho Hệ Thống..."
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
                transition: "opacity 0.2s",
              }}
            >
              GỬI
            </button>
          </form>
        </div>
      )}
    </>
  );
}
