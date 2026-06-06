import { NextRequest, NextResponse } from "next/server";

const RAW_BACKEND_URL = process.env.NEXT_PUBLIC_API_URL?.trim() ?? "";
const IS_PRODUCTION = process.env.NODE_ENV === "production";

function getBackendUrl(): string | null {
  if (RAW_BACKEND_URL) {
    return RAW_BACKEND_URL.replace(/\/$/, "");
  }

  if (IS_PRODUCTION) {
    return null;
  }

  return "http://localhost:8000";
}

/**
 * POST /api/oracle/feedback
 * Proxies feedback request to the FastAPI Oracle backend.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const backendUrl = getBackendUrl();
    if (!backendUrl) {
      return NextResponse.json(
        { error: "Oracle backend chưa được cấu hình trên production." },
        { status: 503 }
      );
    }

    const res = await fetch(`${backendUrl}/oracle/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: body.question,
        answer: body.answer,
        source: body.source,
        citations: body.citations,
        chapter_progress: body.chapter_progress,
        feedback_type: body.feedback_type,
        user_comment: body.user_comment,
        suggested_correction: body.suggested_correction,
      }),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      const detail = typeof errorData.detail === "string" ? errorData.detail : "Backend error";
      return NextResponse.json({ error: detail }, { status: res.status });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: "Không kết nối được tới Oracle backend." },
      { status: 502 }
    );
  }
}
