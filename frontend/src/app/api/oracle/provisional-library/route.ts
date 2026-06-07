import { NextRequest, NextResponse } from "next/server";
import { getServerAdminClient } from "@/lib/supabase-server";

/**
 * GET /api/oracle/provisional-library
 * Queries the provisional_library table in Supabase.
 * Only allowed for logged in admin users.
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

    const { searchParams } = new URL(request.url);
    const getStats = searchParams.get("stats") === "true";

    if (getStats) {
      // Fetch stats for cards
      const [totalRes, highRes, medRes] = await Promise.all([
        supabase.from("provisional_library").select("id", { count: "exact", head: true }),
        supabase.from("provisional_library").select("id", { count: "exact", head: true }).eq("quality_class", "high_confidence"),
        supabase.from("provisional_library").select("id", { count: "exact", head: true }).eq("quality_class", "medium_confidence")
      ]);

      return NextResponse.json({
        total: totalRes.count || 0,
        high_confidence: highRes.count || 0,
        medium_confidence: medRes.count || 0
      });
    }

    // 2. Parse query parameters
    const search = searchParams.get("search") || "";
    const type = searchParams.get("type") || "";
    const qualityClass = searchParams.get("quality_class") || "";
    const page = parseInt(searchParams.get("page") || "1", 10);
    const pageSize = parseInt(searchParams.get("page_size") || "50", 10);

    // 3. Build query
    let query = supabase.from("provisional_library").select("*", { count: "exact" });

    if (search) {
      query = query.or(`name.ilike.%${search}%,normalized_name.ilike.%${search}%,summary.ilike.%${search}%`);
    }

    if (type && type !== "all") {
      query = query.eq("type", type);
    }

    if (qualityClass && qualityClass !== "all") {
      query = query.eq("quality_class", qualityClass);
    }

    // Default sorting: confidence desc, then name asc
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
    console.error("Error loading provisional library:", error);
    return NextResponse.json(
      { error: "Không thể tải danh sách thư viện tự động." },
      { status: 500 }
    );
  }
}
