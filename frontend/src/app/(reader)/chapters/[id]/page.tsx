import { notFound } from "next/navigation";
import {
    getChapter,
    getChapterContent,
    getChapters,
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
        const chapter = await getChapter(parseInt(resolvedParams.id));
        return {
            title: `Chương ${chapter.chapter_number}: ${chapter.title}`,
            description: `Đọc Chương ${chapter.chapter_number} - ${chapter.title} | Mạt Thế Sinh Hoá Nguy Cơ`,
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
        chapter = await getChapter(chapterNumber);
        content = await getChapterContent(chapter.content_url);
        const meta = await getChapters(1, 1);
        totalChapters = meta.max_chapter;
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
