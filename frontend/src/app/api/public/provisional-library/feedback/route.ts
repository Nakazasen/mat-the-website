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
      page_url
    } = body;

    // 2. Validate input
    if (!provisional_id || typeof provisional_id !== "string") {
      return NextResponse.json(
        { error: "provisional_id là bắt buộc." },
        { status: 400 }
      );
    }

    if (!feedback_type || !ALLOWED_FEEDBACK_TYPES.includes(feedback_type)) {
      return NextResponse.json(
        { error: "Loại feedback không hợp lệ." },
        { status: 400 }
      );
    }

    if (!user_comment || typeof user_comment !== "string") {
      return NextResponse.json(
        { error: "Ý kiến đóng góp không được trống." },
        { status: 400 }
      );
    }

    const trimmedComment = user_comment.trim();
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

    if (suggested_correction && typeof suggested_correction === "string" && suggested_correction.length > 4000) {
      return NextResponse.json(
        { error: "Đề xuất sửa đổi vượt quá giới hạn 4000 ký tự." },
        { status: 400 }
      );
    }

    // 3. Extract metadata (user agent)
    const userAgent = request.headers.get("user-agent") || "";

    // 4. Save to database using service client
    const supabase = await getServerAdminClient();
    const { data, error } = await supabase
      .from("provisional_library_feedback")
      .insert({
        provisional_id,
        record_name: record_name || null,
        feedback_type,
        user_comment: trimmedComment,
        suggested_correction: suggested_correction || null,
        page_url: page_url || null,
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
