import { NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

function createRouteClient(cookieStore: Awaited<ReturnType<typeof cookies>>) {
    return createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll();
                },
                setAll(cookiesToSet) {
                    try {
                        cookiesToSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options));
                    } catch {
                        // ignored in route handler
                    }
                },
            },
        },
    );
}

async function getAuthenticatedClient() {
    const cookieStore = await cookies();
    const supabase = createRouteClient(cookieStore);
    const {
        data: { user },
        error
    } = await supabase.auth.getUser();

    if (error || !user) {
        return { supabase, userId: null as string | null };
    }

    return { supabase, userId: user.id };
}

export async function GET(request: Request) {
    try {
        const { supabase, userId } = await getAuthenticatedClient();
        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { searchParams } = new URL(request.url);
        const chapterIdRaw = searchParams.get("chapter_id");
        const chapterId = Number.parseInt(chapterIdRaw || "", 10);
        if (!Number.isFinite(chapterId) || chapterId <= 0) {
            return NextResponse.json({ error: "chapter_id query param is required" }, { status: 400 });
        }

        const [readResp, likeResp] = await Promise.all([
            supabase
                .from("user_chapter_reads")
                .select("id", { count: "exact", head: true })
                .eq("user_id", userId)
                .eq("chapter_id", chapterId),
            supabase
                .from("user_chapter_likes")
                .select("id", { count: "exact", head: true })
                .eq("user_id", userId)
                .eq("chapter_id", chapterId),
        ]);

        const readError = readResp.error;
        const likeError = likeResp.error;
        if (readError || likeError) {
            throw readError || likeError;
        }

        return NextResponse.json({
            has_read: (readResp.count || 0) > 0,
            has_liked: (likeResp.count || 0) > 0,
        });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

export async function POST(request: Request) {
    try {
        const { supabase, userId } = await getAuthenticatedClient();
        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const body = await request.json();
        const action = typeof body.action === "string" ? body.action : "";
        const chapterId = Number.parseInt(String(body.chapter_id || ""), 10);
        const chapterNumber = Number.parseInt(String(body.chapter_number || ""), 10);
        const locale = typeof body.locale === "string" ? body.locale : null;
        const expAmount = Number.isFinite(body.exp_amount) ? Number(body.exp_amount) : 10;

        if (!Number.isFinite(chapterId) || chapterId <= 0) {
            return NextResponse.json({ error: "chapter_id is required" }, { status: 400 });
        }

        if (action === "read") {
            const insertResp = await supabase
                .from("user_chapter_reads")
                .insert({
                    user_id: userId,
                    chapter_id: chapterId,
                    locale,
                })
                .select("id")
                .single();

            const insertError = insertResp.error;
            const inserted = Boolean(insertResp.data);
            if (insertError && insertError.code !== "23505") {
                throw insertError;
            }

            const profileResp = await supabase
                .from("profiles")
                .select("chapters_read, exp")
                .eq("id", userId)
                .single();
            if (profileResp.error) {
                throw profileResp.error;
            }

            const readCountResp = await supabase
                .from("user_chapter_reads")
                .select("id", { count: "exact", head: true })
                .eq("user_id", userId);
            if (readCountResp.error) {
                throw readCountResp.error;
            }

            const existingChaptersRead = Number(profileResp.data?.chapters_read || 0);
            const existingExp = Number(profileResp.data?.exp || 0);
            const readCount = Number(readCountResp.count || 0);
            const shouldAwardExp = inserted && readCount > existingChaptersRead;

            const updatePayload: Record<string, number> = {
                chapters_read: Math.max(existingChaptersRead, readCount),
            };
            if (shouldAwardExp) {
                updatePayload.exp = existingExp + expAmount;
            }

            const profileUpdateResp = await supabase
                .from("profiles")
                .update(updatePayload)
                .eq("id", userId);
            if (profileUpdateResp.error) {
                throw profileUpdateResp.error;
            }

            return NextResponse.json({
                counted: inserted,
                exp_awarded: shouldAwardExp ? expAmount : 0,
                chapters_read: updatePayload.chapters_read,
            });
        }

        if (action === "like") {
            const insertResp = await supabase
                .from("user_chapter_likes")
                .insert({
                    user_id: userId,
                    chapter_id: chapterId,
                    locale,
                })
                .select("id")
                .single();

            const insertError = insertResp.error;
            const inserted = Boolean(insertResp.data);
            if (insertError && insertError.code !== "23505") {
                throw insertError;
            }

            let likesCount: number | null = null;

            if (inserted) {
                const chapterResp = await supabase
                    .from("chapters")
                    .select("id, likes_count")
                    .eq("id", chapterId)
                    .single();
                if (chapterResp.error) {
                    throw chapterResp.error;
                }

                const currentLikes = Number(chapterResp.data?.likes_count || 0);
                likesCount = currentLikes + 1;

                const updateResp = await supabase
                    .from("chapters")
                    .update({ likes_count: likesCount })
                    .eq("id", chapterId)
                    .eq("likes_count", currentLikes)
                    .select("likes_count")
                    .single();
                if (updateResp.error) {
                    throw updateResp.error;
                }
                likesCount = Number(updateResp.data?.likes_count || likesCount);
            } else if (Number.isFinite(chapterNumber) && chapterNumber > 0) {
                const chapterResp = await supabase
                    .from("chapters")
                    .select("likes_count")
                    .eq("chapter_number", chapterNumber)
                    .single();
                if (!chapterResp.error) {
                    likesCount = Number(chapterResp.data?.likes_count || 0);
                }
            }

            return NextResponse.json({
                liked: true,
                counted: inserted,
                likes_count: likesCount,
            });
        }

        return NextResponse.json({ error: "Unsupported action" }, { status: 400 });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
