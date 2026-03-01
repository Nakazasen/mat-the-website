// === API CLIENT ===
// Frontend calls backend API to get chapter metadata + R2 URL
// Then fetches content directly from Cloudflare CDN

const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
}

// Fetch general novel settings (Title, Author, Desc etc)
export async function getNovelSettings(): Promise<NovelSettings> {
    const res = await fetch(`${API_BASE_URL}/api/novel`, {
        next: { revalidate: 60 }, // cache 1 minute (instead of 1 hour)
    });
    if (!res.ok) throw new Error("Failed to fetch novel settings");
    return res.json();
}

/**
 * Analytics: Gửi tín hiệu đã đọc chương về backend.
 * Sẽ được gọi sau 15-20s khi người dùng ở lại trang đọc.
 */
export async function reportView(chapterNumber: number): Promise<void> {
    try {
        await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}/view`, {
            method: "POST",
            keepalive: true,
        });
    } catch (e) {
        console.warn("Analytics Error:", e);
    }
}

// Utility
export function formatChapterTitle(chapter: Chapter): string {
    return `Chương ${chapter.chapter_number}: ${chapter.title}`;
}
