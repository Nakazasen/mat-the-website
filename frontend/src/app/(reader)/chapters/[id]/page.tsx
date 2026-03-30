import type { Metadata } from "next";
import { notFound } from "next/navigation";

import ReadingClient from "@/components/ReadingClient";
import { getChapter, getChapterContent, getNovelSettings, type Chapter } from "@/lib/api";
import { getCurrentLocale } from "@/lib/i18n/server";

export const dynamic = "force-dynamic";

export async function generateMetadata({
    params,
}: {
    params: Promise<{ id: string }>;
}): Promise<Metadata> {
    try {
        const locale = await getCurrentLocale();
        const resolvedParams = await params;
        const [chapter, novel] = await Promise.all([
            getChapter(parseInt(resolvedParams.id, 10), locale),
            getNovelSettings(locale),
        ]);

        const displayTitle = chapter.translated_title || chapter.title;
        const description = (chapter.translated_content || "").slice(0, 160) || `${displayTitle} | ${novel.title}`;

        return {
            title: `${displayTitle} | ${novel.title}`,
            description,
            keywords: [`chapter ${chapter.chapter_number}`, displayTitle, "mat the", "zombie"],
            openGraph: {
                title: `${displayTitle} | ${novel.title}`,
                description,
                type: "article",
                siteName: novel.title,
            },
        };
    } catch {
        return { title: "Chapter not found" };
    }
}

export default async function ReadingPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const locale = await getCurrentLocale();
    const resolvedParams = await params;
    const chapterNumber = parseInt(resolvedParams.id, 10);
    if (Number.isNaN(chapterNumber) || chapterNumber < 1) notFound();

    let chapter: Chapter;
    let content: string;
    let totalChapters: number;

    try {
        const [chapterData, novelData] = await Promise.all([
            getChapter(chapterNumber, locale),
            getNovelSettings(locale),
        ]);
        chapter = chapterData;
        content = chapter.translated_content || await getChapterContent(chapter.content_url);
        totalChapters = novelData.max_chapter;
    } catch {
        notFound();
    }

    const prevId = chapterNumber > 1 ? chapterNumber - 1 : null;
    const nextId = chapterNumber < totalChapters ? chapterNumber + 1 : null;

    return (
        <ReadingClient
            chapterId={chapter.id}
            chapterNumber={chapter.chapter_number}
            chapterTitle={chapter.translated_title || chapter.title}
            content={content}
            prevId={prevId}
            nextId={nextId}
            totalChapters={totalChapters}
            resolvedLocale={chapter.resolved_locale}
            isFallback={chapter.is_fallback}
            bgmUrl={chapter.bgm_url}
            bgmTitle={chapter.bgm_title}
        />
    );
}
