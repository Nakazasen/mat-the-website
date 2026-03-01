import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;
    const isAdminRoute = pathname.startsWith('/admin');

    // Nếu không phải trang admin thì đi tiếp luôn cho nhẹ
    if (!isAdminRoute) {
        return NextResponse.next();
    }

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    // PHẢI CÓ ENV: Nếu thiếu env trên Vercel, middleware sẽ crash (invocation failed)
    // Nếu thiếu, chúng ta trả về response bình thường để tránh crash 500 middleware
    if (!supabaseUrl || !supabaseAnonKey) {
        console.error("CRITICAL: Thiếu NEXT_PUBLIC_SUPABASE_URL hoặc NEXT_PUBLIC_SUPABASE_ANON_KEY trên Vercel Environment Variables.");
        return NextResponse.next();
    }

    let supabaseResponse = NextResponse.next({ request });

    try {
        const supabase = createServerClient(
            supabaseUrl,
            supabaseAnonKey,
            {
                cookies: {
                    getAll() {
                        return request.cookies.getAll();
                    },
                    setAll(cookiesToSet) {
                        cookiesToSet.forEach(({ name, value }) =>
                            request.cookies.set(name, value)
                        );
                        supabaseResponse = NextResponse.next({ request });
                        cookiesToSet.forEach(({ name, value, options }) =>
                            supabaseResponse.cookies.set(name, value, options)
                        );
                    },
                },
            }
        );

        // Refresh session if expired
        const { data: { user } } = await supabase.auth.getUser();

        const isLoginRoute = pathname === '/admin/login';

        // Redirect logic
        if (!isLoginRoute && !user) {
            const loginUrl = new URL('/admin/login', request.url);
            return NextResponse.redirect(loginUrl);
        }

        if (isLoginRoute && user) {
            const dashboardUrl = new URL('/admin', request.url);
            return NextResponse.redirect(dashboardUrl);
        }
    } catch (e) {
        console.error("Middleware Auth Error:", e);
    }

    return supabaseResponse;
}

export const config = {
    matcher: ['/admin/:path*'],
};
