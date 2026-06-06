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
 * PATCH /api/oracle/feedback/[id]
 * Proxies the request to PATCH {backend}/oracle/feedback/{id}
 */
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const adminToken = request.headers.get("X-Oracle-Feedback-Admin-Token");
    if (!adminToken) {
      return NextResponse.json(
        { error: "Forbidden: Missing admin token" },
        { status: 403 }
      );
    }

    const backendUrl = getBackendUrl();
    if (!backendUrl) {
      return NextResponse.json(
        { error: "Oracle backend chưa được cấu hình trên production." },
        { status: 503 }
      );
    }

    const body = await request.json();

    const res = await fetch(`${backendUrl}/oracle/feedback/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-Oracle-Feedback-Admin-Token": adminToken,
      },
      body: JSON.stringify({
        status: body.status,
        reviewer_note: body.reviewer_note,
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
