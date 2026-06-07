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

    return NextResponse.json({
      items: data || [],
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
