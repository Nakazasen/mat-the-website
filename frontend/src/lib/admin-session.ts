import { createAdminClient } from '@/lib/supabase-admin';

const SESSION_REFRESH_LEEWAY_MS = 60_000;

export async function getFreshAdminAccessToken(): Promise<string> {
    const supabase = createAdminClient();
    if (!supabase) {
        throw new Error('Lỗi cấu hình admin. Thiếu kết nối Supabase.');
    }

    const sessionResult = await supabase.auth.getSession();
    let session = sessionResult.data.session;

    const expiresAtMs = (session?.expires_at || 0) * 1000;
    const shouldRefresh =
        !session ||
        (expiresAtMs > 0 && expiresAtMs <= Date.now() + SESSION_REFRESH_LEEWAY_MS);

    if (shouldRefresh) {
        const refreshResult = await supabase.auth.refreshSession();
        if (refreshResult.error && !session) {
            throw new Error('Phiên đăng nhập admin đã hết hạn. Hãy đăng nhập lại.');
        }
        session = refreshResult.data.session || session;
    }

    if (!session?.access_token) {
        throw new Error('Phiên đăng nhập admin đã hết hạn. Hãy đăng nhập lại.');
    }

    return session.access_token;
}
