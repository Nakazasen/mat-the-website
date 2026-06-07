import { NextRequest, NextResponse } from "next/server";
import { getServerAdminClient } from "@/lib/supabase-server";
import * as fs from "fs";
import * as path from "path";

function findCandidatesFile(): string | null {
  const paths = [
    path.join(process.cwd(), "..", "backend", "rag", "generated_wiki_candidates.json"),
    path.join(process.cwd(), "backend", "rag", "generated_wiki_candidates.json"),
  ];
  for (const p of paths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return null;
}

/**
 * GET /api/oracle/wiki-candidates
 * Loads candidates generated from approved corrections.
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

    // 2. Read candidates file
    const filePath = findCandidatesFile();
    if (!filePath) {
      // If the file doesn't exist, return empty array rather than failing, but log a warning.
      console.warn("Wiki candidates file not found. Returning empty array.");
      return NextResponse.json([]);
    }

    const fileContent = fs.readFileSync(filePath, "utf8");
    const candidates = JSON.parse(fileContent);

    return NextResponse.json(candidates);
  } catch (error: any) {
    console.error("Error loading wiki candidates:", error);
    return NextResponse.json(
      { error: "Không thể tải danh sách ứng viên Wiki." },
      { status: 500 }
    );
  }
}
