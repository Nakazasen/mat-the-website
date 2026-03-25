"use client";

import { useEffect, useRef, useState } from "react";

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
}

const SOURCE_LABELS: Record<string, string> = {
  cache: "Bộ nhớ cache",
  local_wiki: "Bách khoa địa phương",
  gemini: "AI Oracle",
};

const DIAGNOSTIC_META: Record<
  DiagnosticCode,
  { label: string; color: string; border: string }
> = {
  ready: {
    label: "ONLINE",
    color: "#39FF14",
    border: "rgba(57,255,20,0.35)",
  },
  processing: {
    label: "ĐANG XỬ LÝ",
    color: "#fbbf24",
    border: "rgba(251,191,36,0.35)",
  },
  backend_offline: {
    label: "BACKEND OFFLINE",
    color: "#f87171",
    border: "rgba(248,113,113,0.35)",
  },
  missing_api_key: {
    label: "MISSING API KEY",
    color: "#fb7185",
    border: "rgba(251,113,133,0.35)",
  },
  rate_limited: {
    label: "RATE LIMITED",
    color: "#f59e0b",
    border: "rgba(245,158,11,0.35)",
  },
  model_exhausted: {
    label: "MODEL EXHAUSTED",
    color: "#f97316",
    border: "rgba(249,115,22,0.35)",
  },
  invalid_question: {
    label: "INVALID INPUT",
    color: "#c084fc",
    border: "rgba(192,132,252,0.35)",
  },
  backend_error: {
    label: "BACKEND ERROR",
    color: "#94a3b8",
    border: "rgba(148,163,184,0.35)",
  },
};

function getInitialMessage(chapterProgress: number): Message {
  return {
    role: "oracle",
    text:
      `[HỆ THỐNG ĐÃ KHỞI ĐỘNG]\n` +
      `Kết nối thành công. Tiến trình đọc: Chương ${chapterProgress}.\n` +
      `Tôi chỉ tiết lộ thông tin trong phạm vi bạn đã đọc. Hãy đặt câu hỏi.`,
  };
}

export default function OraclePanel({
  chapterProgress,
  defaultOpen = false,
}: OraclePanelProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [messages, setMessages] = useState<Message[]>([getInitialMessage(chapterProgress)]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [diagnostic, setDiagnostic] = useState<DiagnosticCode>("ready");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, diagnostic]);

  useEffect(() => {
    setMessages([getInitialMessage(chapterProgress)]);
    setDiagnostic("ready");
  }, [chapterProgress]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || isLoading) {
      return;
    }

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setIsLoading(true);
    setDiagnostic("processing");

    try {
      const res = await fetch("/api/oracle/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          chapter_progress: chapterProgress,
        }),
      });

      if (!res.ok) {
        const errorData = (await res.json().catch(() => ({}))) as OracleErrorPayload;
        const errorCode = errorData.error_code ?? "backend_error";
        const errorMessage =
          errorData.error ??
          "Oracle không thể trả lời lúc này. Thử lại sau.";

        setDiagnostic(errorCode);
        setMessages((prev) => [
          ...prev,
          {
            role: "oracle",
            text: `[CHẨN ĐOÁN HỆ THỐNG]\n${errorMessage}`,
          },
        ]);
        return;
      }

      const data = await res.json();
      setDiagnostic("ready");
      setMessages((prev) => [
        ...prev,
        { role: "oracle", text: data.answer, source: data.source },
      ]);
    } catch {
      setDiagnostic("backend_offline");
      setMessages((prev) => [
        ...prev,
        {
          role: "oracle",
          text: "[CHẨN ĐOÁN HỆ THỐNG]\nKhông kết nối được tới Oracle backend.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const diagnosticMeta = DIAGNOSTIC_META[diagnostic];

  return (
    <>
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        title="AI Oracle"
        style={{
          position: "fixed",
          bottom: "24px",
          right: "36px",
          width: "44px",
          height: "44px",
          borderRadius: "50%",
          background: isOpen ? "rgba(220, 38, 38, 0.9)" : "rgba(57, 255, 20, 0.1)",
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
        {isOpen ? "X" : "AI"}
      </button>

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
          <div
            style={{
              padding: "12px 14px 10px",
              borderBottom: "1px solid rgba(57,255,20,0.1)",
              background: "rgba(15,15,15,0.5)",
            }}
          >
            <div
              style={{
                fontSize: "9px",
                letterSpacing: "0.25em",
                color: "rgba(57,255,20,0.5)",
              }}
            >
              AI ORACLE - THE SYSTEM
            </div>
            <div
              style={{
                fontFamily: "'Courier Prime', monospace",
                color: "#39FF14",
                fontSize: "12px",
                marginTop: "2px",
              }}
            >
              Phạm vi: Chương 1-{chapterProgress} | Chống spoiler ON
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
              <span
                style={{
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: diagnosticMeta.color,
                  boxShadow: `0 0 10px ${diagnosticMeta.color}`,
                }}
              />
              {diagnosticMeta.label}
            </div>
          </div>

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
            {messages.map((message, index) => (
              <div key={index} style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                <div
                  style={{
                    alignSelf: message.role === "user" ? "flex-end" : "flex-start",
                    maxWidth: "85%",
                    padding: "8px 12px",
                    borderRadius:
                      message.role === "user"
                        ? "12px 12px 4px 12px"
                        : "12px 12px 12px 4px",
                    background:
                      message.role === "user"
                        ? "rgba(57,255,20,0.12)"
                        : "rgba(30,30,30,0.8)",
                    border: `1px solid ${
                      message.role === "user"
                        ? "rgba(57,255,20,0.3)"
                        : "rgba(255,255,255,0.06)"
                    }`,
                    fontSize: "12px",
                    lineHeight: 1.6,
                    color: message.role === "user" ? "rgba(255,255,255,0.9)" : "#d4d0c8",
                    fontFamily:
                      message.role === "oracle" ? "'Courier Prime', monospace" : undefined,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {message.text}
                </div>
                {message.source && (
                  <div
                    style={{
                      fontSize: "9px",
                      color: "rgba(255,255,255,0.25)",
                      fontFamily: "monospace",
                      paddingLeft: "4px",
                    }}
                  >
                    {SOURCE_LABELS[message.source] ?? message.source}
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
                ĐANG XỬ LÝ...
              </div>
            )}
            <div ref={bottomRef} />
          </div>

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
