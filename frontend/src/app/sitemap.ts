import type { MetadataRoute } from "next";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://mat-the-website.onrender.com";
const SITE_URL = "https://matthesinhhoa.vercel.app";
const LOCALES = ["vi", "en", "zh-CN", "ja"] as const;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const staticPaths = ["/", "/chapters", "/wiki", "/map", "/huong-dan"];

    const staticPages: MetadataRoute.Sitemap = LOCALES.flatMap((locale) =>
        staticPaths.map((path, index) => ({
            url: `${SITE_URL}/${locale}${path === "/" ? "" : path}`,
            lastModified: new Date(),
            changeFrequency: index <= 1 ? "daily" : "weekly",
            priority: path === "/" ? 1 : 0.7,
        })),
    );

    let chapterPages: MetadataRoute.Sitemap = [];
    try {
        const response = await fetch(`${API_BASE_URL}/api/chapters?page=1&limit=100&sort=asc`, {
            cache: "no-store",
        });
        if (response.ok) {
            const data = await response.json();
            const chapters = data.chapters || [];
            chapterPages = LOCALES.flatMap((locale) =>
                chapters.map((chapter: any) => ({
                    url: `${SITE_URL}/${locale}/chapters/${chapter.chapter_number}`,
                    lastModified: new Date(chapter.created_at),
                    changeFrequency: "monthly" as const,
                    priority: 0.8,
                })),
            );
        }
    } catch {
        // keep sitemap resilient
    }

    return [...staticPages, ...chapterPages];
}
