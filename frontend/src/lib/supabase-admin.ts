import { createBrowserClient } from '@supabase/ssr';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Client for use in browser-side admin components
export function createAdminClient() {
    return createBrowserClient(supabaseUrl, supabaseAnonKey);
}
