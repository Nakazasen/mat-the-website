import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { chaptersReadCount, newExpAmount = 10 } = body; // default +10 EXP per chapter

        if (typeof chaptersReadCount !== 'number') {
            return NextResponse.json({ error: 'chaptersReadCount is required' }, { status: 400 });
        }

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

        // Call the RPC function to increment stats
        const { data, error } = await supabase.rpc('increment_reader_stats', {
            user_id_param: userId,
            new_chapters_count: chaptersReadCount,
            new_exp_amount: newExpAmount
        });

        if (error) {
            console.error("Error updating reader stats:", error);
            // Don't fail the request, stats update is non-critical
            return NextResponse.json({ success: false, error: error.message });
        }

        return NextResponse.json({ success: true });
    } catch (error: any) {
        console.error("API error in read-progress:", error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
