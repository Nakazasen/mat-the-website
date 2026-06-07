import { NextRequest, NextResponse } from "next/server";
import { getServerAdminClient } from "@/lib/supabase-server";

/**
 * GET /api/public/provisional-library
 * Queries the provisional_library table in Supabase.
 * Publicly accessible read-only API. Only returns high_confidence and medium_confidence entries.
 */
export async function GET(request: NextRequest) {
  try {
    const supabase = await getServerAdminClient();

    const { searchParams } = new URL(request.url);

    // 1. Parse query parameters
    const search = searchParams.get("search") || "";
    const type = searchParams.get("type") || "";
    const qualityClass = searchParams.get("quality_class") || "";
    const page = parseInt(searchParams.get("page") || "1", 10);
    // Limit page_size to max 50 to prevent abuse
    const rawPageSize = parseInt(searchParams.get("page_size") || "20", 10);
    const pageSize = Math.max(1, Math.min(rawPageSize, 50));

    // 2. Build query - only high_confidence and medium_confidence are public
    let query = supabase
      .from("provisional_library")
      .select("*", { count: "exact" })
      .in("quality_class", ["high_confidence", "medium_confidence"]);

    if (search) {
      query = query.or(`name.ilike.%${search}%,normalized_name.ilike.%${search}%,summary.ilike.%${search}%`);
    }

    if (type && type !== "all") {
      query = query.eq("type", type);
    }

    if (qualityClass && qualityClass !== "all") {
      if (["high_confidence", "medium_confidence"].includes(qualityClass)) {
        query = query.eq("quality_class", qualityClass);
      }
    }

    // Default sorting: confidence desc, name asc
    query = query.order("confidence", { ascending: false }).order("name", { ascending: true });

    // Pagination range (0-indexed, inclusive)
    const from = (page - 1) * pageSize;
    const to = from + pageSize - 1;
    query = query.range(from, to);

    const { data, count, error } = await query;
    if (error) {
      console.error("Supabase query error:", error);
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    const items = data || [];
    const ids = items.map((item: any) => item.id).filter(Boolean);

    const summaries: Record<string, any> = {};
    if (ids.length > 0) {
      const { data: summaryData, error: summaryError } = await supabase
        .from("provisional_library_feedback_summary")
        .select("provisional_id, effective_status, oracle_policy, dispute_score, total_feedback")
        .in("provisional_id", ids);

      if (!summaryError && summaryData) {
        summaryData.forEach((s: any) => {
          summaries[s.provisional_id] = s;
        });
      }
    }

    const activePatches: Record<string, any> = {};
    if (ids.length > 0) {
      const { data: patchData, error: patchError } = await supabase
        .from("provisional_library_effective_patches")
        .select("target_id, patch_type, oracle_policy, effective_status, reason, effective_summary")
        .eq("effective_status", "active")
        .eq("target_type", "provisional_record")
        .in("target_id", ids);

      if (!patchError && patchData) {
        patchData.forEach((p: any) => {
          activePatches[p.target_id] = p;
        });
      }
    }

    const mappedItems = items.map((item: any) => {
      const summary = summaries[item.id] || {};
      const patch = activePatches[item.id] || {};
      return {
        ...item,
        effective_status: patch.effective_status || summary.effective_status || "trusted",
        oracle_policy: patch.oracle_policy || summary.oracle_policy || "allow",
        dispute_score: summary.dispute_score ?? 0,
        total_feedback: summary.total_feedback ?? 0,
        patch_type: patch.patch_type || null,
        reason: patch.reason || null,
        effective_summary: patch.effective_summary || null
      };
    });

    return NextResponse.json({
      items: mappedItems,
      total: count || 0,
      page,
      page_size: pageSize
    });
  } catch (error: any) {
    console.error("Error loading public provisional library:", error);
    return NextResponse.json(
      { error: "Không thể tải danh sách thư viện tự động." },
      { status: 500 }
    );
  }
}
