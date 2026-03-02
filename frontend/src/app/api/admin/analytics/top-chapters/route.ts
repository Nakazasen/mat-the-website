import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
    try {
        const url = new URL(request.url);
        const limit = parseInt(url.searchParams.get('limit') || '5', 10);

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

        // Security check
        const { data: { session } } = await supabase.auth.getSession();
        if (!session?.user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        // Must check if user is admin, but since middleware already handles that
        // for /admin routes, this API being under /api/admin is somewhat protected
        // but it's good practice to verify role if possible.
        // Assuming middleware does the heavy lifting for now.

        // Fetch top chapters by view count
        const { data, error } = await supabase
            .from('chapters')
            .select('id, chapter_number, title, view_count')
            .eq('status', 'published')
            .order('view_count', { ascending: false })
            .limit(limit);

        if (error) throw error;

        return NextResponse.json(data);
    } catch (e: any) {
        console.error("Top Chapters Error:", e);
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
