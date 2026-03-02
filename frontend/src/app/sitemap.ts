import type { MetadataRoute } from 'next';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-website.onrender.com';
const SITE_URL = 'https://matthesinhhoa.vercel.app';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    // Static pages
    const staticPages: MetadataRoute.Sitemap = [
        {
            url: SITE_URL,
            lastModified: new Date(),
            changeFrequency: 'daily',
            priority: 1,
        },
        {
            url: `${SITE_URL}/chapters`,
            lastModified: new Date(),
            changeFrequency: 'daily',
            priority: 0.9,
        },
        {
            url: `${SITE_URL}/wiki`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.7,
        },
        {
            url: `${SITE_URL}/map`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.6,
        },
        {
            url: `${SITE_URL}/huong-dan`,
            lastModified: new Date(),
            changeFrequency: 'monthly',
            priority: 0.5,
        },
    ];

    // Dynamic chapter pages
    let chapterPages: MetadataRoute.Sitemap = [];
    try {
        const res = await fetch(`${API_BASE_URL}/api/chapters?page=1&limit=100&sort=asc`, {
            cache: 'no-store',
        });
        if (res.ok) {
            const data = await res.json();
            chapterPages = (data.chapters || []).map((ch: any) => ({
                url: `${SITE_URL}/chapters/${ch.chapter_number}`,
                lastModified: new Date(ch.created_at),
                changeFrequency: 'monthly' as const,
                priority: 0.8,
            }));

            // Fetch remaining pages if > 100 chapters
            const totalPages = data.total_pages || 1;
            for (let page = 2; page <= totalPages; page++) {
                const pageRes = await fetch(`${API_BASE_URL}/api/chapters?page=${page}&limit=100&sort=asc`, {
                    cache: 'no-store',
                });
                if (pageRes.ok) {
                    const pageData = await pageRes.json();
                    chapterPages.push(
                        ...(pageData.chapters || []).map((ch: any) => ({
                            url: `${SITE_URL}/chapters/${ch.chapter_number}`,
                            lastModified: new Date(ch.created_at),
                            changeFrequency: 'monthly' as const,
                            priority: 0.8,
                        }))
                    );
                }
            }
        }
    } catch {
        // Sitemap generation should never crash
    }

    return [...staticPages, ...chapterPages];
}
