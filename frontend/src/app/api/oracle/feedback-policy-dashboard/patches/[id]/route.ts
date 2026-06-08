import { NextRequest, NextResponse } from "next/server";
import { getServerAdminClient } from "@/lib/supabase-server";
import { createServerClient } from "@supabase/ssr";

/**
 * PATCH /api/oracle/feedback-policy-dashboard/patches/[id]
 * Disables or restores an effective patch.
 * Requires admin session.
 */
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    // 1. Verify Supabase admin session (Anon client is used to check the user cookie)
    const supabaseAnon = await getServerAdminClient();
    const { data: { user } } = await supabaseAnon.auth.getUser();
    if (!user) {
      return NextResponse.json(
        { error: "Unauthorized: Vui lòng đăng nhập admin" },
        { status: 401 }
      );
    }

    // 2. Create Service Role client to bypass RLS for administrative updates
    const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
    
    // Log key length to debug if it is loaded on Vercel (safe log, no actual key exposure)
    console.log("DB update client initialized with key length:", serviceRoleKey ? serviceRoleKey.length : 0, "prefix:", serviceRoleKey ? serviceRoleKey.substring(0, 10) : "");

    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      serviceRoleKey,
      {
        cookies: {
          getAll() {
            return [];
          },
          setAll() {
            // No-op for service role client
          },
        },
      }
    );


    // 2. Parse request body
    let body;
    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        { error: "Invalid JSON body" },
        { status: 400 }
      );
    }

    const { action, reviewer_note } = body;

    // 3. Validate request parameters
    if (action !== "disable" && action !== "restore") {
      return NextResponse.json(
        { error: "Action must be 'disable' or 'restore'" },
        { status: 400 }
      );
    }

    if (typeof reviewer_note !== "string") {
      return NextResponse.json(
        { error: "Reviewer note must be a string" },
        { status: 400 }
      );
    }

    // 4. Fetch the target patch to check existence and retrieve target details
    let patchTable = "provisional_library_effective_patches";
    let { data: patch, error: fetchErr } = await supabase
      .from(patchTable)
      .select("*")
      .eq("id", id)
      .single();

    if (fetchErr || !patch) {
      patchTable = "oracle_answer_effective_patches";
      const { data: oPatch, error: oFetchErr } = await supabase
        .from(patchTable)
        .select("*")
        .eq("id", id)
        .single();

      if (oFetchErr || !oPatch) {
        return NextResponse.json(
          { error: "Patch not found" },
          { status: 404 }
        );
      }
      patch = oPatch;
    }

    // 5. Calculate new status and reason
    const newStatus = action === "disable" ? "disabled" : "active";
    
    // Append or construct the reviewer note
    let newReason = patch.reason || "";
    const prefix = action === "disable" ? "Disabled" : "Restored";
    const noteText = reviewer_note.trim() ? `: ${reviewer_note.trim()}` : "";
    const formattedNote = `[Admin ${prefix}${noteText}]`;
    newReason = newReason.trim() ? `${newReason} | ${formattedNote}` : formattedNote;

    // 6. Update the patch in database
    const { error: updateErr } = await supabase
      .from(patchTable)
      .update({
        effective_status: newStatus,
        reason: newReason,
        updated_at: new Date().toISOString()
      })
      .eq("id", id);

    if (updateErr) {
      return NextResponse.json(
        { error: `Database update failed: ${updateErr.message}` },
        { status: 500 }
      );
    }

    // 7. Clear selective oracle_cache based on target_name / target_entity / query_pattern
    const targetsToClear: string[] = [];
    if (patch.target_name) {
      targetsToClear.push(patch.target_name);
    }
    if (patch.target_entity) {
      targetsToClear.push(patch.target_entity);
    }
    if (patch.query_pattern) {
      targetsToClear.push(patch.query_pattern);
      const clean = patch.query_pattern.replace(" là ai", "").replace(" là gì", "").trim();
      if (clean.length >= 2) {
        targetsToClear.push(clean);
      }
    }

    let cacheClearedCount = 0;
    if (targetsToClear.length > 0) {
      const { data: cacheEntries, error: cacheErr } = await supabase
        .from("oracle_cache")
        .select("id, response");

      if (!cacheErr && cacheEntries) {
        const idsToDelete: number[] = [];
        for (const entry of cacheEntries) {
          const responseText = (entry.response || "").toLowerCase();
          for (const target of targetsToClear) {
            if (responseText.includes(target.toLowerCase())) {
              idsToDelete.push(entry.id);
              break;
            }
          }
        }

        if (idsToDelete.length > 0) {
          const { error: deleteErr } = await supabase
            .from("oracle_cache")
            .delete()
            .in("id", idsToDelete);
          
          if (!deleteErr) {
            cacheClearedCount = idsToDelete.length;
          }
        }
      }
    }

    return NextResponse.json({
      ok: true,
      patch_id: id,
      status: newStatus,
      cache_cleared_count: cacheClearedCount
    });

  } catch (error: any) {
    console.error("Error in patch status update route:", error);
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: 500 }
    );
  }
}
