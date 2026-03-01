import { createBrowserClient } from '@supabase/ssr';

// const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
// const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Client for use in browser-side admin components
export function createAdminClient() {
    // Build Version tag to verify deployment
    const BUILD_VERSION = "2026-03-01-0925";

    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!url || !key) {
        console.warn("Supabase credentials missing. Client side auth will fail.");
        return null;
    }

    try {
        return createBrowserClient(url, key);
    } catch (e) {
        console.error("Failed to create Supabase browser client:", e);
        return null;
    }
}
