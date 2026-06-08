import { NextRequest, NextResponse } from "next/server";
import { getServerAdminClient } from "@/lib/supabase-server";
import { createServerClient } from "@supabase/ssr";
import fs from "fs";
import path from "path";

/**
 * GET /api/oracle/feedback-policy-dashboard
 * Returns stats, recent feedbacks, aggregated summaries, and knowledge patches.
 * Requires admin session.
 */
export async function GET(request: NextRequest) {
  try {
    // 1. Verify Supabase admin session
    const supabaseAnon = await getServerAdminClient();
    const { data: { user } } = await supabaseAnon.auth.getUser();
    if (!user) {
      return NextResponse.json(
        { error: "Unauthorized: Vui lòng đăng nhập admin" },
        { status: 401 }
      );
    }

    // 2. Create Service Role client to bypass RLS for administrative stats
    const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      serviceRoleKey,
      {
        cookies: {
          getAll() {
            return [];
          },
          setAll() {
            // No-op
          },
        },
      }
    );

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
      pendingFeedbackRes,
      oracleSummariesRes,
      oraclePatchesRes,
      oracleActivePatchesRes,
      ragFeedbackPendingRes,
      ragFeedbackResolvedRes
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
        .eq("status", "pending"),

      // Oracle Answer Summaries (graceful fallback if table doesn't exist)
      supabase
        .from("oracle_answer_feedback_summary")
        .select("*")
        .order("total_feedback", { ascending: false })
        .limit(100)
        .then(res => res.error ? { data: [], error: null } : res),

      // Oracle Answer Patches (graceful fallback if table doesn't exist)
      supabase
        .from("oracle_answer_effective_patches")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(100)
        .then(res => res.error ? { data: [], error: null } : res),

      // Oracle Active Patches Count (graceful fallback if table doesn't exist)
      supabase
        .from("oracle_answer_effective_patches")
        .select("id", { count: "exact", head: true })
        .eq("effective_status", "active")
        .then(res => res.error ? { count: 0, error: null } : res),

      // Oracle RAG Feedbacks - Pending (graceful fallback if table doesn't exist)
      supabase
        .from("rag_feedback")
        .select("id", { count: "exact", head: true })
        .eq("status", "pending")
        .then(res => res.error ? { count: 0, error: null } : res),

      // Oracle RAG Feedbacks - Resolved (graceful fallback if table doesn't exist)
      supabase
        .from("rag_feedback")
        .select("id", { count: "exact", head: true })
        .eq("status", "resolved")
        .then(res => res.error ? { count: 0, error: null } : res)
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

    // 5. Read regression report
    let reportData: any = null;
    try {
      const pathA = path.join(process.cwd(), "..", "backend", "rag", "generated_oracle_self_learning_regression_report.json");
      const pathB = path.join(process.cwd(), "backend", "rag", "generated_oracle_self_learning_regression_report.json");
      const pathC = "D:\\Sandbox\\Web_matthesinhhoanguyco\\mat-the-website\\backend\\rag\\generated_oracle_self_learning_regression_report.json";

      let finalPath = "";
      if (fs.existsSync(pathA)) {
        finalPath = pathA;
      } else if (fs.existsSync(pathB)) {
        finalPath = pathB;
      } else if (fs.existsSync(pathC)) {
        finalPath = pathC;
      }

      if (finalPath) {
        const raw = fs.readFileSync(finalPath, "utf-8");
        reportData = JSON.parse(raw);
      }
    } catch (e) {
      console.warn("Failed to read regression report file:", e);
    }

    let regression_total = 0;
    let regression_passed = 0;
    let regression_failed = 0;
    let latest_report_created_at: string | null = null;
    let failed_cases: Array<{ query: string; chapter_progress: number | null; reason: string | null }> = [];

    if (reportData) {
      regression_total = reportData.summary?.total || 0;
      regression_passed = reportData.summary?.passed || 0;
      regression_failed = reportData.summary?.failed || 0;
      latest_report_created_at = reportData.timestamp || null;

      if (reportData.results && Array.isArray(reportData.results)) {
        failed_cases = reportData.results
          .filter((r: any) => !r.passed)
          .map((r: any) => ({
            query: r.question || "",
            chapter_progress: r.chapter_progress || null,
            reason: r.failure_reason || "Unknown failure"
          }));
      }
    }

    const oracle_self_learning_quality = {
      regression_total,
      regression_passed,
      regression_failed,
      latest_report_created_at,
      failed_cases,
      active_oracle_patches: oracleActivePatchesRes.count || 0,
      pending_rag_feedback: ragFeedbackPendingRes.count || 0,
      resolved_rag_feedback: ragFeedbackResolvedRes.count || 0
    };

    // 6. Return formatted data
    return NextResponse.json({
      feedback_recent: recentFeedbackRes.data || [],
      summaries: summariesRes.data || [],
      patches: patchesRes.data || [],
      oracle_summaries: oracleSummariesRes.data || [],
      oracle_patches: oraclePatchesRes.data || [],
      stats: {
        feedback_total: totalFeedbackRes.count || 0,
        summary_total: totalSummaryRes.count || 0,
        patch_active: activePatchesRes.count || 0,
        warn_count: warnCountRes.count || 0,
        block_count: blockCountRes.count || 0,
        oracle_patch_active: oracleActivePatchesRes.count || 0
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
      },
      oracle_self_learning_quality
    });

  } catch (error: any) {
    console.error("Error loading feedback policy dashboard data:", error);
    return NextResponse.json(
      { error: error.message || "Không thể tải dữ liệu vòng tự học." },
      { status: 500 }
    );
  }
}
