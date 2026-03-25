import { NextRequest, NextResponse } from "next/server";

const RAW_BACKEND_URL = process.env.NEXT_PUBLIC_API_URL?.trim() ?? "";
const IS_PRODUCTION = process.env.NODE_ENV === "production";

type OracleProxyErrorCode =
  | "backend_offline"
  | "missing_api_key"
  | "rate_limited"
  | "model_exhausted"
  | "invalid_question"
  | "backend_error";

function getBackendUrl(): string | null {
  if (RAW_BACKEND_URL) {
    return RAW_BACKEND_URL.replace(/\/$/, "");
  }

  if (IS_PRODUCTION) {
    return null;
  }

  return "http://localhost:8000";
}

function buildErrorResponse(
  status: number,
  error: string,
  errorCode: OracleProxyErrorCode,
) {
  return NextResponse.json({ error, error_code: errorCode }, { status });
}

function classifyBackendError(status: number, detail: string): OracleProxyErrorCode {
  const normalized = detail.toLowerCase();

  if (status === 400) {
    return "invalid_question";
  }

  if (
    status === 503 &&
    (normalized.includes("not configured") ||
      normalized.includes("missing api key") ||
      normalized.includes("api key"))
  ) {
    return "missing_api_key";
  }

  if (
    normalized.includes("resource exhausted") ||
    normalized.includes("quota") ||
    normalized.includes("rate limit")
  ) {
    return "model_exhausted";
  }

  if (status === 429) {
    return "rate_limited";
  }

  return "backend_error";
}

/**
 * POST /api/oracle/ask
 * Proxies to the FastAPI AI Oracle backend.
 * The API key never reaches the browser; it stays in backend storage/env only.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const question = typeof body.question === "string" ? body.question.trim() : "";

    if (question.length < 5) {
      return buildErrorResponse(
        400,
        "Câu hỏi không hợp lệ. Hãy nhập ít nhất 5 ký tự.",
        "invalid_question",
      );
    }

    const backendUrl = getBackendUrl();
    if (!backendUrl) {
      return buildErrorResponse(
        503,
        "Oracle backend chưa được cấu hình trên production.",
        "backend_offline",
      );
    }

    const res = await fetch(`${backendUrl}/oracle/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Forwarded-For": request.headers.get("x-forwarded-for") ?? "",
      },
      body: JSON.stringify({
        question: question.slice(0, 500),
        chapter_progress: Math.max(1, Number(body.chapter_progress) || 1),
      }),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      const detail = typeof errorData.detail === "string" ? errorData.detail : "Backend error";
      const errorCode = classifyBackendError(res.status, detail);

      let message = detail;
      if (errorCode === "missing_api_key") {
        message = "AI Oracle chưa có API key hợp lệ.";
      } else if (errorCode === "rate_limited") {
        message = "Bạn đã chạm giới hạn truy vấn trong ngày. Thử lại sau.";
      } else if (errorCode === "model_exhausted") {
        message = "Toàn bộ model hiện tại đã hết quota hoặc đang bị giới hạn.";
      }

      return buildErrorResponse(res.status, message, errorCode);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return buildErrorResponse(
      502,
      "Không kết nối được tới Oracle backend.",
      "backend_offline",
    );
  }
}
