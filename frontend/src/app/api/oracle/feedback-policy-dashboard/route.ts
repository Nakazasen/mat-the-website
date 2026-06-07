import { NextRequest, NextResponse } from "next/server";
import { getServerAdminClient } from "@/lib/supabase-server";

/**
 * GET /api/oracle/feedback-policy-dashboard
 * Returns stats, recent feedbacks, aggregated summaries, and knowledge patches.
 * Requires admin session.
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

    // 2. Query stats & lists in parallel
    const [
      recentFeedbackRes,
      summariesRes,
      patchesRes,
      totalFeedbackRes,
      totalSummaryRes,
      activePatchesRes,
      warnCountRes,
      blockCountRes
    ] = await Promise.all([
      // Fetch 50 most recent community feedbacks
      supabase
        .from("provisional_library_feedback")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(50),
      
      // Fetch feedback summaries sorted by dispute score desc
      supabase
        .from("provisional_library_feedback_summary")
        .select("*")
        .order("dispute_score", { ascending: false })
        .order("updated_at", { ascending: false })
        .limit(100),
      
      // Fetch active effective patches
      supabase
        .from("provisional_library_effective_patches")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(100),

      // Counts for stats cards
      supabase
        .from("provisional_library_feedback")
        .select("id", { count: "exact", head: true }),
      supabase
        .from("provisional_library_feedback_summary")
        .select("provisional_id", { count: "exact", head: true }),
      supabase
        .from("provisional_library_effective_patches")
        .select("id", { count: "exact", head: true })
        .eq("effective_status", "active"),
      supabase
        .from("provisional_library_feedback_summary")
        .select("provisional_id", { count: "exact", head: true })
        .eq("oracle_policy", "warn"),
      supabase
        .from("provisional_library_feedback_summary")
        .select("provisional_id", { count: "exact", head: true })
        .eq("oracle_policy", "block")
    ]);

    // 3. Check for errors
    if (recentFeedbackRes.error) throw new Error(recentFeedbackRes.error.message);
    if (summariesRes.error) throw new Error(summariesRes.error.message);
    if (patchesRes.error) throw new Error(patchesRes.error.message);

    // 4. Return formatted data
    return NextResponse.json({
      feedback_recent: recentFeedbackRes.data || [],
      summaries: summariesRes.data || [],
      patches: patchesRes.data || [],
      stats: {
        feedback_total: totalFeedbackRes.count || 0,
        summary_total: totalSummaryRes.count || 0,
        patch_active: activePatchesRes.count || 0,
        warn_count: warnCountRes.count || 0,
        block_count: blockCountRes.count || 0
      }
    });

  } catch (error: any) {
    console.error("Error loading feedback policy dashboard data:", error);
    return NextResponse.json(
      { error: error.message || "Không thể tải dữ liệu vòng tự học." },
      { status: 500 }
    );
  }
}
