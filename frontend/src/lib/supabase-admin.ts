import { createBrowserClient } from '@supabase/ssr';

// Loại bỏ dấu ! để tránh crash ứng dụng khi build/load nếu thiếu env
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

// Client for use in browser-side admin components
export function createAdminClient() {
    if (!supabaseUrl || !supabaseAnonKey) {
        console.warn("Supabase credentials missing. Check your environment variables.");
    }
    return createBrowserClient(supabaseUrl, supabaseAnonKey);
}
