import { createBrowserClient } from '@supabase/ssr';

// const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
// const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Client for use in browser-side admin components
export function createAdminClient() {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (typeof window !== 'undefined') {
        console.log("--- Supabase Client Diagnostics ---");
        console.log("Window exists: true");
        console.log("NEXT_PUBLIC_SUPABASE_URL detected:", !!url);
        console.log("NEXT_PUBLIC_SUPABASE_ANON_KEY detected:", !!key);

        // Log the first few chars of URL for verification (safely)
        if (url) console.log("URL starts with:", url.substring(0, 8));
    }

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
