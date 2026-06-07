import { NextRequest, NextResponse } from "next/server";
import { getServerAdminClient } from "@/lib/supabase-server";

const ALLOWED_FEEDBACK_TYPES = [
  "wrong_info",
  "wrong_type",
  "wrong_evidence",
  "duplicate",
  "spoiler",
  "missing_info",
  "other"
];

/**
 * POST /api/public/provisional-library/feedback
 * Submit public reader feedback on an auto-extracted record.
 */
export async function POST(request: NextRequest) {
  try {
    // 1. Parse payload
    const body = await request.json().catch(() => ({}));
    const {
      provisional_id,
      record_name,
      feedback_type,
      user_comment,
      suggested_correction,
      page_url,
      website // Honeypot field
    } = body;

    // Honeypot check (Optional field website, if filled it's a bot)
    if (website !== undefined && website !== "") {
      return NextResponse.json(
        { error: "Yêu cầu bị từ chối do nghi ngờ spam." },
        { status: 400 }
      );
    }

    // Trim all inputs
    const trimmedId = typeof provisional_id === "string" ? provisional_id.trim() : "";
    const trimmedRecordName = typeof record_name === "string" ? record_name.trim() : "";
    const trimmedComment = typeof user_comment === "string" ? user_comment.trim() : "";
    const trimmedCorrection = typeof suggested_correction === "string" ? suggested_correction.trim() : "";
    const trimmedUrl = typeof page_url === "string" ? page_url.trim() : "";

    // 2. Validate input
    if (!trimmedId) {
      return NextResponse.json(
        { error: "provisional_id là bắt buộc." },
        { status: 400 }
      );
    }

    // Strict provisional_id format check (alphanumeric/hyphen/underscore, min length 6)
    if (trimmedId.length < 6 || !/^[a-zA-Z0-9\-_]+$/.test(trimmedId)) {
      return NextResponse.json(
        { error: "provisional_id không hợp lệ." },
        { status: 400 }
      );
    }

    if (!feedback_type || !ALLOWED_FEEDBACK_TYPES.includes(feedback_type)) {
      return NextResponse.json(
        { error: "Loại feedback không hợp lệ." },
        { status: 400 }
      );
    }

    if (!trimmedComment) {
      return NextResponse.json(
        { error: "Ý kiến đóng góp không được trống." },
        { status: 400 }
      );
    }

    if (trimmedComment.length < 3) {
      return NextResponse.json(
        { error: "Ý kiến đóng góp quá ngắn (tối thiểu 3 ký tự)." },
        { status: 400 }
      );
    }

    if (trimmedComment.length > 2000) {
      return NextResponse.json(
        { error: "Ý kiến đóng góp vượt quá giới hạn 2000 ký tự." },
        { status: 400 }
      );
    }

    // Limit URLs in user_comment (max 2 links)
    const urlPattern = /https?:\/\/[^\s]+|www\.[^\s]+/gi;
    const urlMatches = trimmedComment.match(urlPattern);
    if (urlMatches && urlMatches.length > 2) {
      return NextResponse.json(
        { error: "Ý kiến đóng góp chứa quá nhiều liên kết (tối đa 2)." },
        { status: 400 }
      );
    }

    // Repeated garbage character check (e.g. non-dot, non-space characters repeated 6+ times consecutively)
    const repeatedPattern = /([^\s.])\1{5,}/;
    if (repeatedPattern.test(trimmedComment)) {
      return NextResponse.json(
        { error: "Ý kiến đóng góp chứa nhiều ký tự lặp lại vô nghĩa." },
        { status: 400 }
      );
    }

    if (trimmedCorrection && trimmedCorrection.length > 4000) {
      return NextResponse.json(
        { error: "Đề xuất sửa đổi vượt quá giới hạn 4000 ký tự." },
        { status: 400 }
      );
    }

    // 3. Extract metadata (user agent)
    const userAgent = request.headers.get("user-agent") || "";

    const supabase = await getServerAdminClient();

    // 4. Rate limit / Duplicate check (same user_agent, provisional_id, and comment in last 5 minutes)
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
    try {
      const { count: duplicateCount } = await supabase
        .from("provisional_library_feedback")
        .select("id", { count: "exact", head: true })
        .eq("user_agent", userAgent)
        .eq("provisional_id", trimmedId)
        .eq("user_comment", trimmedComment)
        .gte("created_at", fiveMinutesAgo);

      if (duplicateCount && duplicateCount > 0) {
        return NextResponse.json(
          { error: "Đóng góp trùng lặp hoặc gửi quá nhanh. Vui lòng thử lại sau." },
          { status: 429 }
        );
      }
    } catch (err) {
      console.warn("Failed to check duplicate feedback in rate limiter:", err);
    }

    // 5. Save to database using service client
    const { data, error } = await supabase
      .from("provisional_library_feedback")
      .insert({
        provisional_id: trimmedId,
        record_name: trimmedRecordName || null,
        feedback_type,
        user_comment: trimmedComment,
        suggested_correction: trimmedCorrection || null,
        page_url: trimmedUrl || null,
        user_agent: userAgent,
        status: "pending"
      })
      .select("id")
      .single();

    if (error) {
      console.error("Supabase insert feedback error:", error);
      return NextResponse.json(
        { error: "Không thể lưu ý kiến đóng góp vào hệ thống." },
        { status: 500 }
      );
    }

    return NextResponse.json({
      ok: true,
      feedback_id: data.id
    });
  } catch (error: any) {
    console.error("Error submitting public provisional library feedback:", error);
    return NextResponse.json(
      { error: "Lỗi kết nối máy chủ." },
      { status: 500 }
    );
  }
}
