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
      blockCountRes,
      latestRunRes,
      failuresRes,
      pendingFeedbackRes
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
        .eq("oracle_policy", "block"),

      // Observability: latest run
      supabase
        .from("feedback_policy_pipeline_runs")
        .select("*")
        .order("started_at", { ascending: false })
        .limit(1),

      // Observability: total failures
      supabase
        .from("feedback_policy_pipeline_runs")
        .select("id", { count: "exact", head: true })
        .eq("ok", false),

      // Observability: pending feedback count
      supabase
        .from("provisional_library_feedback")
        .select("id", { count: "exact", head: true })
        .eq("status", "pending")
    ]);

    // 3. Check for errors
    if (recentFeedbackRes.error) throw new Error(recentFeedbackRes.error.message);
    if (summariesRes.error) throw new Error(summariesRes.error.message);
    if (patchesRes.error) throw new Error(patchesRes.error.message);

    // 4. Calculate health block
    const latestRun = latestRunRes.data && latestRunRes.data.length > 0 ? latestRunRes.data[0] : null;
    let last_run_at: string | null = null;
    let last_run_ok = true;
    let last_run_errors: string[] = [];
    let hours_since_last_run = 999;
    let pipeline_stale = true;
    let last_run_feedback_read = 0;
    let last_run_summaries_written = 0;
    let last_run_patches_written = 0;
    let last_run_cache_deleted = 0;
    let last_run_dry_run = false;

    if (latestRun) {
      last_run_at = latestRun.started_at;
      last_run_ok = latestRun.ok;
      last_run_errors = latestRun.errors || [];
      last_run_feedback_read = latestRun.feedback_rows_read || 0;
      last_run_summaries_written = latestRun.summary_rows_written || 0;
      last_run_patches_written = latestRun.patches_written || 0;
      last_run_cache_deleted = latestRun.cache_rows_deleted || 0;
      last_run_dry_run = latestRun.dry_run || false;

      const elapsedMs = Date.now() - new Date(latestRun.started_at).getTime();
      hours_since_last_run = elapsedMs / (1000 * 60 * 60);
      pipeline_stale = hours_since_last_run > 3;
    }

    // 5. Return formatted data
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
      },
      health: {
        last_run_at,
        last_run_ok,
        last_run_errors,
        hours_since_last_run,
        pipeline_stale,
        recent_failures: failuresRes.count || 0,
        pending_feedbacks: pendingFeedbackRes.count || 0,
        last_run_feedback_read,
        last_run_summaries_written,
        last_run_patches_written,
        last_run_cache_deleted,
        last_run_dry_run
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
