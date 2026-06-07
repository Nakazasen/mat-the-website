import { NextRequest, NextResponse } from "next/server";
import { getServerAdminClient } from "@/lib/supabase-server";

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
 * GET /api/oracle/feedback/pending
 * Proxies the request to GET {backend}/oracle/feedback/pending
 */
export async function GET(request: NextRequest) {
  try {
    // 1. Verify Supabase admin session
    const supabase = await getServerAdminClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return NextResponse.json(
        { error: "Unauthorized: Vui lòng đăng nhập admin" },
        { status: 401 }
      );
    }

    // 2. Read admin token from environment
    const adminToken = process.env.ORACLE_FEEDBACK_ADMIN_TOKEN;
    if (!adminToken || !adminToken.trim()) {
      return NextResponse.json(
        { error: "Admin feedback token is not configured on server" },
        { status: 503 }
      );
    }

    const backendUrl = getBackendUrl();
    if (!backendUrl) {
      return NextResponse.json(
        { error: "Oracle backend chưa được cấu hình trên production." },
        { status: 503 }
      );
    }

    const res = await fetch(`${backendUrl}/oracle/feedback/pending`, {
      method: "GET",
      headers: {
        "X-Oracle-Feedback-Admin-Token": adminToken.trim(),
      },
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
