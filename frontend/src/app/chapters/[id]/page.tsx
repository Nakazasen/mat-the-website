import { notFound } from "next/navigation";
import {
    getChapter,
    getChapterContent,
    getChapters,
} from "@/lib/api";
import ReadingClient from "@/components/ReadingClient";
import type { Metadata } from "next";

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

    let chapter, content: string, totalChapters: number;
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

// Generate static paths for first 20 chapters (others on-demand)
export async function generateStaticParams() {
    return Array.from({ length: 20 }, (_, i) => ({ id: String(i + 1) }));
}
