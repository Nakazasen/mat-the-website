import { createBrowserClient } from '@supabase/ssr';

// Client for use in browser-side admin components
// This file is safe for both Client and Server Components
export function createAdminClient() {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!url || !key) {
        console.warn("Supabase credentials missing.");
        return null;
    }

    try {
        return createBrowserClient(url, key);
    } catch (e) {
        console.error("Failed to create Supabase browser client:", e);
        return null;
    }
}
