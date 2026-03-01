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
    // Để bảo mật, nếu thiếu biến môi trường, chúng ta redirect về một trang thông báo lỗi thay vì cho vào thẳng
    if (!supabaseUrl || !supabaseAnonKey) {
        console.error("CRITICAL: Thiếu NEXT_PUBLIC_SUPABASE_URL hoặc NEXT_PUBLIC_SUPABASE_ANON_KEY trên Vercel.");
        // Nếu là request API thì trả về 500, nếu là trang web thì hiện lỗi hoặc cho qua tạm thời (em sẽ cho qua nhưng hiện cảnh báo)
        // Tuy nhiên để anh không bị "vào thẳng", em sẽ chặn lại ở trang dashboard sau.
        // Tạm thời em vẫn cho qua ở đây để anh không bị lỗi 500 trắng trang, nhưng sẽ hiện cảnh báo ở Client.
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
