import { createBrowserClient } from '@supabase/ssr';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Client for use in browser-side admin components
export function createAdminClient() {
    if (!supabaseUrl || !supabaseAnonKey) {
        console.warn("Supabase credentials missing. Client side auth will fail.");
        return null;
    }

    try {
        return createBrowserClient(supabaseUrl, supabaseAnonKey);
    } catch (e) {
        console.error("Failed to create Supabase browser client:", e);
        return null;
    }
}
