import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

const SUPPORTED_LOCALES = ["vi", "en", "zh-CN", "ja"] as const;
const LOCALE_COOKIE = "mt_locale";

function isSupportedLocale(value: string | null | undefined): value is (typeof SUPPORTED_LOCALES)[number] {
    return Boolean(value && SUPPORTED_LOCALES.includes(value as (typeof SUPPORTED_LOCALES)[number]));
}

function normalizeLocale(value: string | null | undefined) {
    if (!value) return "vi";
    if (isSupportedLocale(value)) return value;

    const lowered = value.toLowerCase();
    if (lowered.startsWith("vi")) return "vi";
    if (lowered.startsWith("en")) return "en";
    if (lowered.startsWith("zh")) return "zh-CN";
    if (lowered.startsWith("ja")) return "ja";
    return "vi";
}

function detectPreferredLocale(request: NextRequest) {
    const cookieLocale = request.cookies.get(LOCALE_COOKIE)?.value;
    if (isSupportedLocale(cookieLocale)) return cookieLocale;

    const accepted = request.headers.get("accept-language") ?? "";
    for (const part of accepted.split(",")) {
        const candidate = normalizeLocale(part.split(";")[0]?.trim());
        if (candidate) return candidate;
    }
    return "vi";
}

function isPublicAsset(pathname: string) {
    return pathname.startsWith("/_next")
        || pathname.startsWith("/favicon")
        || pathname.startsWith("/icon-")
        || pathname === "/manifest.json"
        || pathname === "/sw.js"
        || pathname.includes(".");
}

function buildLocaleResponse(request: NextRequest, locale: string, pathname: string) {
    const headers = new Headers(request.headers);
    headers.set("x-mt-locale", locale);
    headers.set("x-mt-path", pathname);

    const rewritten = request.nextUrl.clone();
    rewritten.pathname = pathname.slice(locale.length + 1) || "/";

    const response = NextResponse.rewrite(rewritten, { request: { headers } });
    response.cookies.set(LOCALE_COOKIE, locale, { path: "/", maxAge: 60 * 60 * 24 * 365 });
    return response;
}

export async function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;
    const isAdminRoute = pathname.startsWith("/admin");
    const isApiRoute = pathname.startsWith("/api");

    if (!isAdminRoute && !isApiRoute && !isPublicAsset(pathname)) {
        if (pathname === "/") {
            const preferred = detectPreferredLocale(request);
            const url = request.nextUrl.clone();
            url.pathname = `/${preferred}`;
            const response = NextResponse.redirect(url);
            response.cookies.set(LOCALE_COOKIE, preferred, { path: "/", maxAge: 60 * 60 * 24 * 365 });
            return response;
        }

        const localeSegment = pathname.split("/")[1];
        if (isSupportedLocale(localeSegment)) {
            return buildLocaleResponse(request, localeSegment, pathname);
        }

        const preferred = detectPreferredLocale(request);
        const url = request.nextUrl.clone();
        url.pathname = `/${preferred}${pathname}`;
        const response = NextResponse.redirect(url);
        response.cookies.set(LOCALE_COOKIE, preferred, { path: "/", maxAge: 60 * 60 * 24 * 365 });
        return response;
    }

    if (!isAdminRoute) {
        return NextResponse.next();
    }

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    let supabaseResponse = NextResponse.next({ request });

    try {
        if (!supabaseUrl || !supabaseAnonKey) {
            return supabaseResponse;
        }

        const supabase = createServerClient(
            supabaseUrl,
            supabaseAnonKey,
            {
                cookies: {
                    getAll() {
                        return request.cookies.getAll();
                    },
                    setAll(cookiesToSet: any[]) {
                        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
                        supabaseResponse = NextResponse.next({ request });
                        cookiesToSet.forEach(({ name, value, options }) => {
                            supabaseResponse.cookies.set(name, value, options);
                        });
                    },
                },
            },
        );

        const {
            data: { user },
        } = await supabase.auth.getUser();

        const isLoginRoute = pathname === "/admin/login";

        if (!isLoginRoute && !user) {
            return NextResponse.redirect(new URL("/admin/login", request.url));
        }

        if (isLoginRoute && user) {
            return NextResponse.redirect(new URL("/admin", request.url));
        }
    } catch (error) {
        console.error("Middleware auth error:", error);
    }

    return supabaseResponse;
}

export const config = {
    matcher: ["/((?!_next/static|_next/image).*)"],
};
