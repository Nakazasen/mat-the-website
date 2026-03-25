// === API CLIENT ===
import imageCompression from 'browser-image-compression';

// Frontend calls backend API to get chapter metadata + R2 URL
// Then fetches content directly from Cloudflare CDN

const API_BASE_URL =
    (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

export interface Chapter {
    id: number;
    chapter_number: number;
    title: string;
    content_url: string; // Cloudflare R2 public URL
    created_at: string;
    word_count?: number;
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
    limit: number = 50
): Promise<ChaptersResponse> {
    const res = await fetch(
        `${API_BASE_URL}/api/chapters?page=${page}&limit=${limit}`,
        {
            cache: "no-store", // Tắt hoàn toàn cache cho danh sách chương
        }
    );
    if (!res.ok) throw new Error(`Failed to fetch chapters: ${res.status}`);
    return res.json();
}

// Fetch latest N chapters for homepage
export async function getLatestChapters(count: number = 10): Promise<Chapter[]> {
    const res = await fetch(
        `${API_BASE_URL}/api/chapters?page=1&limit=${count}&sort=desc`,
        {
            cache: "no-store", // Tắt hoàn toàn cache cho trang chủ
        }
    );
    if (!res.ok) throw new Error("Failed to fetch latest chapters");
    const data: ChaptersResponse = await res.json();
    return data.chapters;
}

// Fetch single chapter metadata by chapter_number
export async function getChapter(chapterNumber: number): Promise<Chapter> {
    const res = await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}`, {
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
    has_ai_key?: boolean;
}

// Fetch general novel settings (Title, Author, Desc etc)
export async function getNovelSettings(): Promise<NovelSettings> {
    const res = await fetch(`${API_BASE_URL}/api/novel`, {
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
    token: string = "mat-the-admin-2026"
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
    limit: number = 50
): Promise<WikiEntriesResponse> {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (search) params.set("search", search);
    params.set("page", page.toString());
    params.set("limit", limit.toString());
    
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

export async function getWikiEntry(slug: string): Promise<WikiEntry> {
    const res = await fetch(`${API_BASE_URL}/api/wiki/${slug}`, { cache: "no-store" });
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
}

export async function getHomepageSettings(): Promise<HomepageSettings> {
    const res = await fetch(`${API_BASE_URL}/api/homepage`, {
        next: { revalidate: 300 } // cache 5 minutes
    });
    if (!res.ok) throw new Error("Failed to fetch homepage settings");
    return res.json();
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
}

export async function getPublicGuide(slug: string): Promise<GuidePage> {
    const res = await fetch(`${API_BASE_URL}/api/guide/${slug}`, { cache: "no-store" });
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
