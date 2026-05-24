import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function GET() {
    try {
        const cookieStore = await cookies();
        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() { return cookieStore.getAll(); },
                    setAll(cookiesToSet) {
                        try {
                            cookiesToSet.forEach(({ name, value, options }) =>
                                cookieStore.set(name, value, options)
                            );
                        } catch { }
                    },
                },
            }
        );

        const { data: { user }, error: authError } = await supabase.auth.getUser();
        if (authError || !user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const { data, error } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', user.id)
            .single();

        if (error) throw error;

        let chaptersRead = Number(data?.chapters_read || 0);
        let likesGiven = 0;

        try {
            const readsResp = await supabase
                .from('user_chapter_reads')
                .select('id', { count: 'exact', head: true })
                .eq('user_id', user.id);
            if (!readsResp.error && typeof readsResp.count === 'number') {
                chaptersRead = Math.max(chaptersRead, readsResp.count);
            }
        } catch {
            // keep legacy profile count
        }

        try {
            const likesResp = await supabase
                .from('user_chapter_likes')
                .select('id', { count: 'exact', head: true })
                .eq('user_id', user.id);
            if (!likesResp.error && typeof likesResp.count === 'number') {
                likesGiven = likesResp.count;
            }
        } catch {
            // keep default zero when table is not present yet
        }

        return NextResponse.json({
            ...data,
            chapters_read: chaptersRead,
            likes_given: likesGiven,
        });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
