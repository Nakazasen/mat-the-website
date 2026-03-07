import { notFound } from "next/navigation";
import {
    getChapter,
    getChapterContent,
    getChapters,
    getNovelSettings,
    type Chapter,
} from "@/lib/api";
import ReadingClient from "@/components/ReadingClient";
import type { Metadata } from "next";
export const dynamic = "force-dynamic";

interface Props {
    params: { id: string };
}

export async function generateMetadata({
    params,
}: {
    params: Promise<{ id: string }>;
}): Promise<Metadata> {
    try {
        const resolvedParams = await params;
        const [chapter, novel] = await Promise.all([
            getChapter(parseInt(resolvedParams.id)),
            getNovelSettings()
        ]);
        const title = `Chương ${chapter.chapter_number}: ${chapter.title} | ${novel.title}`;
        const description = `Đọc Chương ${chapter.chapter_number} - ${chapter.title}. Truyện ${novel.title} full ${novel.total_chapters}+ chương. Zombie, dị biến sinh học, sinh tồn.`;
        return {
            title,
            description,
            keywords: [`chương ${chapter.chapter_number}`, chapter.title, 'mạt thế', 'zombie', 'đọc truyện online', 'sinh hoá nguy cơ'],
            openGraph: {
                title,
                description,
                type: 'article',
                siteName: novel.title,
            },
        };
    } catch {
        return { title: "Không tìm thấy chương" };
    }
}

export default async function ReadingPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const resolvedParams = await params;
    const chapterNumber = parseInt(resolvedParams.id, 10);
    if (isNaN(chapterNumber) || chapterNumber < 1) notFound();

    let chapter: Chapter;
    let content: string;
    let totalChapters: number;
    try {
        const [chapterData, novelData] = await Promise.all([
            getChapter(chapterNumber),
            getNovelSettings()
        ]);
        chapter = chapterData;
        content = await getChapterContent(chapter.content_url);
        totalChapters = novelData.max_chapter;
    } catch {
        notFound();
    }

    // prev/next chapter IDs assume sequential chapter numbers
    const prevId = chapterNumber > 1 ? chapterNumber - 1 : null;
    const nextId = chapterNumber < totalChapters ? chapterNumber + 1 : null;

    return (
        <ReadingClient
            chapterId={chapter.id}
            chapterNumber={chapter.chapter_number}
            chapterTitle={chapter.title}
            content={content}
            prevId={prevId}
            nextId={nextId}
            totalChapters={totalChapters}
        />
    );
}

// Removed generateStaticParams to avoid build timeouts when backend is offline
