// === API CLIENT ===
import imageCompression from 'browser-image-compression';
import type { Locale } from '@/lib/i18n/config';

// Frontend calls backend API to get chapter metadata + R2 URL
// Then fetches content directly from Cloudflare CDN

const API_BASE_URL =
    (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

async function readJsonSafely<T>(res: Response): Promise<T | Record<string, unknown>> {
    const text = await res.text();
    if (!text) return {};
    try {
        return JSON.parse(text) as T;
    } catch {
        return {};
    }
}

function buildFailureDetails(
    failures: Array<{ locale: string; detail?: string; status_code?: number }> | undefined,
    fallback: string,
): string {
    if (!Array.isArray(failures) || failures.length === 0) return fallback;
    return failures
        .map((item) => {
            const locale = item.locale || "unknown";
            const detail = (item.detail || "").trim() || fallback;
            return `${locale}: ${detail}`;
        })
        .join(" | ");
}

export interface Chapter {
    id: number;
    chapter_number: number;
    title: string;
    content_url: string; // Cloudflare R2 public URL
    created_at: string;
    word_count?: number;
    requested_locale?: Locale;
    resolved_locale?: Locale;
    is_fallback?: boolean;
    translated_title?: string;
    translated_content?: string;
}

export interface TranslationFailure {
    locale: string;
    detail?: string;
    status_code?: number;
}

export interface AdminChapterTranslateResult {
    message: string;
    chapter_number: number;
    translated_locales: string[];
    failed_translations?: TranslationFailure[];
}

export interface ChaptersResponse {
    chapters: Chapter[];
    total: number;
    page: number;
    limit: number;
    total_pages: number;
    max_chapter: number;
}

// Fetch paginated list of chapters
export async function getChapters(
    page: number = 1,
    limit: number = 50,
    locale?: Locale
): Promise<ChaptersResponse> {
    const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
    });
    if (locale) params.set("locale", locale);

    const res = await fetch(
        `${API_BASE_URL}/api/chapters?${params.toString()}`,
        {
            cache: "no-store", // Tắt hoàn toàn cache cho danh sách chương
        }
    );
    if (!res.ok) throw new Error(`Failed to fetch chapters: ${res.status}`);
    return res.json();
}

// Fetch latest N chapters for homepage
export async function getLatestChapters(count: number = 10, locale?: Locale): Promise<Chapter[]> {
    const params = new URLSearchParams({
        page: "1",
        limit: count.toString(),
        sort: "desc",
    });
    if (locale) params.set("locale", locale);

    const res = await fetch(
        `${API_BASE_URL}/api/chapters?${params.toString()}`,
        {
            cache: "no-store", // Tắt hoàn toàn cache cho trang chủ
        }
    );
    if (!res.ok) throw new Error("Failed to fetch latest chapters");
    const data: ChaptersResponse = await res.json();
    return data.chapters;
}

// Fetch single chapter metadata by chapter_number
export async function getChapter(chapterNumber: number, locale?: Locale): Promise<Chapter> {
    const params = new URLSearchParams();
    if (locale) params.set("locale", locale);

    const res = await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}${params.toString() ? `?${params.toString()}` : ""}`, {
        next: { revalidate: 3600 }, // cache 1 hour
    });
    if (!res.ok) throw new Error(`Chapter ${chapterNumber} not found`);
    return res.json();
}

// Fetch chapter CONTENT from Cloudflare R2 CDN directly
export async function getChapterContent(contentUrl: string): Promise<string> {
    const res = await fetch(contentUrl, {
        cache: "no-store", // Tắt cache tạm để ép browser load nội dung mới
    });
    if (!res.ok) throw new Error("Failed to fetch chapter content from CDN");

    let text = await res.text();

    // Nếu r2 vẫn trả về định dạng JSON (bị lưu nháp / cache), cố gắng parse
    try {
        const parsed = JSON.parse(text);
        if (parsed && typeof parsed.content === "string") {
            text = parsed.content;
        }
    } catch (e) {
        // Ignored: đây đã là text chuẩn
    }

    // Replace ký tự \n ảo do python dump sai format trước đó
    return text.replace(/\\n/g, "\n");
}

export interface NovelSettings {
    title: string;
    author: string;
    description: string;
    cover_url: string;
    status: string;
    genres: string[];
    donate_qr_url?: string;
    total_chapters: number;
    max_chapter: number;
    total_views: number;
    total_likes: number;
    ai_model_name?: string;
    ai_model_catalog?: string[];
    ai_api_keys_count?: number;
    has_ai_key?: boolean;
    requested_locale?: Locale;
    resolved_locale?: Locale;
    is_fallback?: boolean;
}

export interface AdminAiPlaygroundRequest {
    models: string[];
    prompt?: string;
    chapter_progress?: number;
    api_key?: string;
}

export interface AdminAiPlaygroundResult {
    model: string;
    status: string;
    latency_ms: number;
    answer_preview?: string;
    error?: string;
    used_saved_key: boolean;
}

export interface AdminAiPlaygroundResponse {
    prompt: string;
    chapter_progress: number;
    results: AdminAiPlaygroundResult[];
}

export interface OracleHealthStatus {
    ok: boolean;
    status: string;
    active_model: string;
    model_catalog: string[];
    has_api_key: boolean;
    rate_limit_configured: boolean;
    cache_configured: boolean;
    detail: string;
    upstream_status?: number | null;
    upstream_error?: string | null;
}

export interface AdminOracleResetResponse {
    deleted_rows: number;
    detail: string;
}

// Fetch general novel settings (Title, Author, Desc etc)
export async function getNovelSettings(locale?: Locale): Promise<NovelSettings> {
    const params = new URLSearchParams();
    if (locale) params.set("locale", locale);

    const res = await fetch(`${API_BASE_URL}/api/novel${params.toString() ? `?${params.toString()}` : ""}`, {
        cache: "no-store", // Bỏ qua cache để cập nhật tức thì khi admin đổi model
    });
    if (!res.ok) throw new Error("Failed to fetch novel settings");
    return res.json();
}

/**
 * [Admin] Cập nhật thông tin chung và cấu hình AI
 */
export async function updateNovelSettings(
    data: Partial<NovelSettings>,
    token: string
): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/api/admin/novel`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(data)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to update novel settings");
    }
    return res.json();
}

export async function runAdminAiPlayground(
    data: AdminAiPlaygroundRequest,
    token: string
): Promise<AdminAiPlaygroundResponse> {
    const res = await fetch(`${API_BASE_URL}/oracle/admin/playground`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(data),
    });
    const payload = await res.json();
    if (!res.ok) {
        throw new Error(payload.detail || "Failed to run AI playground");
    }
    return payload;
}

export async function getAdminOracleHealth(token: string): Promise<OracleHealthStatus> {
    const res = await fetch(`${API_BASE_URL}/oracle/admin/health`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
    });
    const payload = await res.json();
    if (!res.ok) {
        throw new Error(payload.detail || "Failed to fetch Oracle health");
    }
    return payload;
}

export async function resetAdminOracleRateLimit(token: string): Promise<AdminOracleResetResponse> {
    const res = await fetch(`${API_BASE_URL}/oracle/admin/reset-rate-limit`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    const payload = await res.json();
    if (!res.ok) {
        throw new Error(payload.detail || "Failed to reset Oracle rate limits");
    }
    return payload;
}

export async function translateAdminChapter(chapterNumber: number, token: string): Promise<AdminChapterTranslateResult> {
    const res = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}/translate`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    const payload = await readJsonSafely<AdminChapterTranslateResult>(res) as AdminChapterTranslateResult;
    if (!res.ok) {
        const errorMessage =
            (payload as { detail?: string })?.detail ||
            buildFailureDetails(payload.failed_translations, "Failed to translate chapter");
        throw new Error(errorMessage);
    }
    return payload;
}

export async function translateAdminChaptersBatch(
    data: { start_chapter: number; end_chapter: number; only_missing?: boolean },
    token: string
): Promise<{
    message: string;
    translated_count: number;
    skipped_count: number;
    failed_count: number;
    translated_chapters: Array<{ chapter_number: number; translated_locales: string[] }>;
    skipped_chapters: number[];
    failed_chapters: Array<{ chapter_number: number; detail?: string }>;
}> {
    const res = await fetch(`${API_BASE_URL}/api/admin/chapters/translate-batch`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
    });
    const payload = await res.json();
    if (!res.ok) {
        throw new Error(payload.detail || "Failed to batch translate chapters");
    }
    return payload;
}

export async function getAdminChapterTranslationStatuses(
    chapterNumbers: number[],
    token: string
): Promise<{
    statuses: Array<{
        chapter_number: number;
        published_locales: string[];
        failed_locales: string[];
        in_progress_locales: string[];
        published_count: number;
        failed_count: number;
        in_progress_count: number;
        attempt_count: number;
        last_error?: string | null;
        last_error_locale?: string | null;
        status_label: string;
    }>;
}> {
    const res = await fetch(`${API_BASE_URL}/api/admin/chapters/translation-statuses`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ chapter_numbers: chapterNumbers }),
    });
    const payload = await res.json();
    if (!res.ok) {
        throw new Error(payload.detail || "Failed to fetch chapter translation statuses");
    }
    return payload;
}

// reportView moved to ANALYTICS section below (with localStorage anti-spam)

// Utility
export function formatChapterTitle(chapter: Chapter): string {
    return `Chương ${chapter.chapter_number}: ${chapter.title}`;
}

// ============================================================
// WIKI API
// ============================================================

export interface WikiEntry {
    id: string;
    title: string;
    category: string;
    slug: string;
    summary?: string;
    content?: string;
    image_url?: string;
    tags?: string[];
    sort_order: number;
    is_main_character: boolean;
    created_at: string;
    updated_at: string;
    requested_locale?: Locale;
    resolved_locale?: Locale;
    is_fallback?: boolean;
}

export interface WikiEntryIn {
    title: string;
    category: string;
    slug: string;
    summary?: string;
    content?: string;
    image_url?: string;
    tags?: string[];
    sort_order?: number;
    is_main_character?: boolean;
}

export interface WikiEntriesResponse {
    entries: WikiEntry[];
    total: number;
    page: number;
    limit: number;
    total_pages: number;
}

export async function getUserRole(token: string): Promise<string> {
    try {
        const res = await fetch(`${API_BASE_URL}/api/user/role`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        if (!res.ok) return 'editor';
        const data = await res.json();
        return data.role || 'editor';
    } catch {
        return 'editor';
    }
}

export const WIKI_CATEGORIES = ["Nhân vật", "Sinh vật", "Thế lực", "Vật phẩm", "Địa điểm"] as const;

export async function getWikiEntries(
    category?: string, 
    search?: string,
    page: number = 1,
    limit: number = 50,
    locale?: Locale
): Promise<WikiEntriesResponse> {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (search) params.set("search", search);
    params.set("page", page.toString());
    params.set("limit", limit.toString());
    if (locale) params.set("locale", locale);
    
    const response = await fetch(`${API_BASE_URL}/api/wiki?${params.toString()}`, { cache: "no-store" });
    if (!response.ok) throw new Error("Failed to fetch wiki entries");
    
    const data = await response.json();
    
    // Backward compatibility: If it's an array (old API), wrap it in the expected object structure
    if (Array.isArray(data)) {
        return {
            entries: data,
            total: data.length,
            page: 1,
            limit: Math.max(data.length, limit),
            total_pages: 1
        };
    }
    
    return data;
}

export async function getWikiEntry(slug: string, locale?: Locale): Promise<WikiEntry> {
    const params = new URLSearchParams();
    if (locale) params.set("locale", locale);

    const res = await fetch(`${API_BASE_URL}/api/wiki/${slug}${params.toString() ? `?${params.toString()}` : ""}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Wiki entry '${slug}' not found`);
    return res.json();
}

export async function createWikiEntry(data: WikiEntryIn, token: string): Promise<WikiEntry> {
    const res = await fetch(`${API_BASE_URL}/api/wiki`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create wiki entry");
    return res.json();
}

export async function updateWikiEntry(id: string, data: WikiEntryIn, token: string): Promise<WikiEntry> {
    const res = await fetch(`${API_BASE_URL}/api/wiki/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update wiki entry");
    return res.json();
}

export async function translateAdminWikiEntry(
    entryId: string,
    token: string
): Promise<{ message: string; entry_id: string; translated_locales: string[]; failed_translations?: Array<{ locale: string; detail?: string }> }> {
    const res = await fetch(`${API_BASE_URL}/api/admin/wiki/${entryId}/translate`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    const payload = await res.json();
    if (!res.ok) {
        throw new Error(payload.detail || "Failed to translate wiki entry");
    }
    return payload;
}

export async function translateAdminWikiBatch(
    data: { category?: string; search?: string; page?: number; limit?: number; only_missing?: boolean },
    token: string
): Promise<{
    message: string;
    page: number;
    limit: number;
    total_entries: number;
    translated_count: number;
    skipped_count: number;
    failed_count: number;
    translated_entries: Array<{ entry_id: string; title: string; translated_locales: string[] }>;
    skipped_entries: Array<{ entry_id: string; title: string }>;
    failed_entries: Array<{ entry_id: string; title: string; detail?: string }>;
}> {
    const res = await fetch(`${API_BASE_URL}/api/admin/wiki/translate-batch`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
    });
    const payload = await res.json();
    if (!res.ok) {
        throw new Error(payload.detail || "Failed to batch translate wiki");
    }
    return payload;
}

export async function deleteWikiEntry(id: string, token: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/api/wiki/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to delete wiki entry");
}

// ============================================================
// LIKE / HEART SYSTEM
// ============================================================

export async function likeChapter(chapterNumber: number): Promise<{ likes_count: number }> {
    const res = await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}/like`, {
        method: "POST",
        keepalive: true,
    });
    if (!res.ok) throw new Error("Failed to like chapter");
    return res.json();
}

// ============================================================
// UPLOAD API
// ============================================================

export async function uploadImageR2(file: File, adminToken: string): Promise<string> {
    let fileToUpload: File | Blob = file;

    // Nén ảnh nếu là file ảnh và dung lượng lớn (> 1MB)
    if (file.type.startsWith('image/') && file.size > 1024 * 1024) {
        try {
            const options = {
                maxSizeMB: 1.5,
                maxWidthOrHeight: 1920,
                useWebWorker: true,
                initialQuality: 0.8,
            };
            fileToUpload = await imageCompression(file, options);
        } catch (error) {
            console.error('Compression failed:', error);
            // Nếu nén lỗi thì cứ dùng file gốc
            fileToUpload = file;
        }
    }

    const formData = new FormData();
    formData.append('file', fileToUpload);

    const res = await fetch(`${API_BASE_URL}/api/upload/image`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${adminToken}`,
        },
        body: formData,
    });

    if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Xảy ra lỗi khi upload ảnh");
    }
    const data = await res.json();
    return data.url;
}

// ============================================================
// FACTION HIERARCHY API
// ============================================================

export interface FactionMember {
    id: string;
    faction_id: string;
    character_id?: string;
    parent_id?: string;
    role_title: string;
    division?: string;
    rank_level: number;
    sort_order: number;
    created_at: string;
    character_name?: string;
    character_slug?: string;
    character_image?: string;
}

export interface FactionHierarchy {
    faction_id: string;
    faction_title: string;
    members: FactionMember[];
}

export interface FactionMemberIn {
    character_id?: string;
    parent_id?: string | null;
    role_title: string;
    division?: string;
    rank_level: number;
    sort_order: number;
}

export async function getFactionHierarchy(slug: string): Promise<FactionHierarchy> {
    const res = await fetch(`${API_BASE_URL}/api/wiki/${slug}/hierarchy`, { cache: "no-store" });
    if (!res.ok) {
        if (res.status === 404 || res.status === 400) return { faction_id: "", faction_title: "", members: [] };
        throw new Error("Failed to fetch faction hierarchy");
    }
    return res.json();
}

export async function addFactionMember(factionId: string, data: FactionMemberIn, token: string): Promise<FactionMember> {
    const res = await fetch(`${API_BASE_URL}/api/admin/wiki/${factionId}/members`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to add faction member");
    return res.json();
}

export async function updateFactionMember(memberId: string, data: FactionMemberIn, token: string): Promise<FactionMember> {
    const res = await fetch(`${API_BASE_URL}/api/admin/wiki/members/${memberId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update faction member");
    return res.json();
}

export async function deleteFactionMember(memberId: string, token: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/api/admin/wiki/members/${memberId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to delete faction member");
}


// HOMEPAGE SETTINGS API
// ============================================================

export interface Feature {
    icon: string;
    title: string;
    desc: string;
}

export interface HomepageSettings {
    warning_title: string;
    warning_subtitle: string;
    warning_headline: string;
    warning_description: string;
    features_title: string;
    features_json: Feature[];
    requested_locale?: Locale;
    resolved_locale?: Locale;
    is_fallback?: boolean;
}

export async function getHomepageSettings(locale?: Locale): Promise<HomepageSettings> {
    const params = new URLSearchParams();
    if (locale) params.set("locale", locale);

    const res = await fetch(`${API_BASE_URL}/api/homepage${params.toString() ? `?${params.toString()}` : ""}`, {
        next: { revalidate: 300 } // cache 5 minutes
    });
    if (!res.ok) throw new Error("Failed to fetch homepage settings");
    return res.json();
}

export async function translateAdminHomepage(
    token: string,
    locale?: Locale
): Promise<{ message: string; translated_locales: string[]; failed_translations?: Array<{ locale: string; detail?: string }> }> {
    const params = new URLSearchParams();
    if (locale) params.set("locale", locale);

    const res = await fetch(`${API_BASE_URL}/api/admin/homepage/translate${params.toString() ? `?${params.toString()}` : ""}`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    const rawText = await res.text();
    let payload: any = {};
    try {
        payload = rawText ? JSON.parse(rawText) : {};
    } catch {
        payload = {};
    }
    if (!res.ok) {
        throw new Error(payload.detail || "Failed to translate homepage settings");
    }
    return payload;
}
// ============================================================
// MAP LOCATIONS API (Phase 09)
// ============================================================

export type MapLocationType = 'safe_zone' | 'danger_zone' | 'neutral' | 'outpost' | 'ruins' | 'system_map';

export interface MapLocation {
    id: string;
    name: string;
    type: MapLocationType;
    description?: string;
    lat: number;
    lng: number;
    image_url?: string;
    created_at: string;
}

export interface AdminMapLocationIn {
    name: string;
    type: MapLocationType;
    description?: string;
    lat: number;
    lng: number;
    image_url?: string;
}

export async function getMapLocations(): Promise<MapLocation[]> {
    const res = await fetch(`${API_BASE_URL}/api/map-locations`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch map locations");
    return res.json();
}

export async function createMapLocation(data: AdminMapLocationIn, token: string): Promise<MapLocation> {
    const res = await fetch(`${API_BASE_URL}/api/admin/map-locations`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create map location");
    return res.json();
}

export async function updateMapLocation(id: string, data: AdminMapLocationIn, token: string): Promise<MapLocation> {
    const res = await fetch(`${API_BASE_URL}/api/admin/map-locations/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update map location");
    return res.json();
}

export async function deleteMapLocation(id: string, token: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/api/admin/map-locations/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to delete map location");
}

// === ANALYTICS ===

export async function reportView(chapterNumber: number): Promise<void> {
    // Anti-spam: only count 1 view per chapter per browser session
    const key = `viewed_ch_${chapterNumber}`;
    if (typeof window !== "undefined" && localStorage.getItem(key)) return;

    try {
        await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}/view`, { method: "POST" });
        if (typeof window !== "undefined") {
            localStorage.setItem(key, "1");
        }
    } catch {
        // Silent fail - analytics should never break reading
    }
}

export async function getTopLikedChapters(token: string, limit = 5): Promise<any[]> {
    try {
        const res = await fetch(`${API_BASE_URL}/api/admin/analytics/top-liked?limit=${limit}`, {
            headers: { Authorization: `Bearer ${token}` },
            cache: "no-store",
        });
        if (!res.ok) return [];
        return res.json();
    } catch {
        return [];
    }
}

// === GUIDE PAGES ===

export interface GuidePage {
    id?: string;
    slug: string;
    title: string;
    content: string;
    scope: string;
    updated_at?: string;
    requested_locale?: Locale;
    resolved_locale?: Locale;
    is_fallback?: boolean;
}

export async function getPublicGuide(slug: string, locale?: Locale): Promise<GuidePage> {
    const params = new URLSearchParams();
    if (locale) params.set("locale", locale);
    const res = await fetch(`${API_BASE_URL}/api/guide/${slug}${params.toString() ? `?${params.toString()}` : ""}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch guide");
    return res.json();
}

export async function getAdminGuide(slug: string, token: string): Promise<GuidePage> {
    const res = await fetch(`${API_BASE_URL}/api/admin/guide/${slug}`, {
        headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to fetch guide");
    return res.json();
}

export async function updateGuide(slug: string, data: { title?: string; content?: string }, token: string): Promise<GuidePage> {
    const res = await fetch(`${API_BASE_URL}/api/admin/guide/${slug}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update guide");
    return res.json();
}

export async function translateAdminGuide(
    slug: string,
    token: string,
    locale?: Locale
): Promise<{ message: string; slug: string; translated_locales: string[]; failed_translations?: Array<{ locale: string; detail?: string }> }> {
    const params = new URLSearchParams();
    if (locale) params.set("locale", locale);
    const res = await fetch(`${API_BASE_URL}/api/admin/guide/${slug}/translate${params.toString() ? `?${params.toString()}` : ""}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
    });
    const payload = await res.json();
    if (!res.ok) throw new Error(payload.detail || "Failed to translate guide");
    return payload;
}
