import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const {
            chaptersReadCount,
            newExpAmount = 10,
            chapterId,
            locale,
        } = body;

        const cookieStore = await cookies();
        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() {
                        return cookieStore.getAll();
                    },
                    setAll(cookiesToSet) {
                        try {
                            cookiesToSet.forEach(({ name, value, options }) =>
                                cookieStore.set(name, value, options)
                            );
                        } catch {
                            // Ignored in route handler
                        }
                    },
                },
            }
        );

        // Verify user session
        const { data: { session } } = await supabase.auth.getSession();
        if (!session?.user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const userId = session.user.id;

        if (Number.isFinite(chapterId) && Number(chapterId) > 0) {
            const insertResp = await supabase
                .from('user_chapter_reads')
                .insert({
                    user_id: userId,
                    chapter_id: Number(chapterId),
                    locale: typeof locale === 'string' ? locale : null,
                })
                .select('id')
                .single();

            const insertError = insertResp.error;
            const inserted = Boolean(insertResp.data);
            if (insertError && insertError.code !== '23505') {
                console.error("Error inserting chapter read:", insertError);
                return NextResponse.json({ success: false, error: insertError.message });
            }

            const profileResp = await supabase
                .from('profiles')
                .select('chapters_read, exp')
                .eq('id', userId)
                .single();
            if (profileResp.error) {
                console.error("Error loading profile for read-progress:", profileResp.error);
                return NextResponse.json({ success: false, error: profileResp.error.message });
            }

            const readsCountResp = await supabase
                .from('user_chapter_reads')
                .select('id', { count: 'exact', head: true })
                .eq('user_id', userId);
            if (readsCountResp.error) {
                console.error("Error counting user chapter reads:", readsCountResp.error);
                return NextResponse.json({ success: false, error: readsCountResp.error.message });
            }

            const existingChaptersRead = Number(profileResp.data?.chapters_read || 0);
            const existingExp = Number(profileResp.data?.exp || 0);
            const readsCount = Number(readsCountResp.count || 0);
            const shouldAwardExp = inserted && readsCount > existingChaptersRead;

            const updatePayload: Record<string, number> = {
                chapters_read: Math.max(existingChaptersRead, readsCount),
            };
            if (shouldAwardExp) {
                updatePayload.exp = existingExp + Number(newExpAmount || 0);
            }

            const updateResp = await supabase
                .from('profiles')
                .update(updatePayload)
                .eq('id', userId);
            if (updateResp.error) {
                console.error("Error updating profile read-progress:", updateResp.error);
                return NextResponse.json({ success: false, error: updateResp.error.message });
            }

            return NextResponse.json({
                success: true,
                counted: inserted,
                exp_awarded: shouldAwardExp ? Number(newExpAmount || 0) : 0,
                chapters_read: updatePayload.chapters_read,
            });
        }

        if (typeof chaptersReadCount !== 'number') {
            return NextResponse.json({ error: 'chaptersReadCount hoặc chapterId là bắt buộc' }, { status: 400 });
        }

        const { error } = await supabase.rpc('increment_reader_stats', {
            user_id_param: userId,
            new_chapters_count: chaptersReadCount,
            new_exp_amount: newExpAmount
        });

        if (error) {
            console.error("Error updating reader stats:", error);
            return NextResponse.json({ success: false, error: error.message });
        }

        return NextResponse.json({ success: true });
    } catch (error: any) {
        console.error("API error in read-progress:", error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
