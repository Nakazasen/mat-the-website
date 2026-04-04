'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { AlertTriangle, ArrowLeft, CheckCircle2, ClipboardCopy, ClipboardPenLine, Languages, Save } from 'lucide-react';

import RichTextEditor from '@/components/Editor';
import { importAdminChapterTranslation, importAdminChapterTranslations, translateAdminChapter, uploadAudioR2, type AdminChapterTranslateResult, type TranslationFailure } from '@/lib/api';
import { createAdminClient } from '@/lib/supabase-admin';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
const MANUAL_IMPORT_LOCALES = ['en', 'zh-CN', 'ja'] as const;
const LOCALE_SAFE_COPY_OPTIONS = [
    { locale: 'en', label: 'EN ONLY' },
    { locale: 'zh-CN', label: 'ZH ONLY' },
    { locale: 'ja', label: 'JA ONLY' },
] as const;
type TargetLocale = (typeof MANUAL_IMPORT_LOCALES)[number];

type GrokImportPayload = {
    chapter_number: number;
    translations: Record<(typeof MANUAL_IMPORT_LOCALES)[number], { title: string; content: string }>;
};

function stripCodeFences(raw: string): string {
    const text = raw.trim();
    if (!text.startsWith('```')) return text;
    const lines = text.split(/\r?\n/);
    if (lines.length <= 2) return text.replace(/^```[a-zA-Z0-9_-]*\s*/, '').replace(/```$/, '').trim();
    const firstLine = lines[0].trim();
    const lastLine = lines[lines.length - 1].trim();
    if (firstLine.startsWith('```') && lastLine === '```') {
        return lines.slice(1, -1).join('\n').trim();
    }
    return text;
}

function parseCsvRow(line: string): string[] {
    const cells: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i += 1) {
        const char = line[i];
        const next = line[i + 1];
        if (char === '"' && inQuotes && next === '"') {
            current += '"';
            i += 1;
            continue;
        }
        if (char === '"') {
            inQuotes = !inQuotes;
            continue;
        }
        if (char === ',' && !inQuotes) {
            cells.push(current);
            current = '';
            continue;
        }
        current += char;
    }

    cells.push(current);
    return cells.map((cell) => cell.trim());
}

function extractGrokImportPayload(rawInput: string, chapterNumber: number): GrokImportPayload {
    const text = stripCodeFences(rawInput);
    if (!text.trim()) {
        throw new Error('Khong co du lieu Grok de import.');
    }

    const tryParseJson = (): GrokImportPayload | null => {
        try {
            const parsed = JSON.parse(text);
            const candidates = Array.isArray(parsed) ? parsed : [parsed];
            for (const candidate of candidates) {
                if (!candidate || typeof candidate !== 'object') continue;
                const translations = candidate.translations;
                if (!translations || typeof translations !== 'object') continue;
                const responseChapterNumber = Number(candidate.chapter_number || chapterNumber);
                if (Number.isFinite(responseChapterNumber) && responseChapterNumber !== chapterNumber) {
                    continue;
                }
                const nextPayload = {
                    chapter_number: responseChapterNumber,
                    translations: {
                        en: {
                            title: String(translations.en?.title || ''),
                            content: String(translations.en?.content || ''),
                        },
                        'zh-CN': {
                            title: String(translations['zh-CN']?.title || ''),
                            content: String(translations['zh-CN']?.content || ''),
                        },
                        ja: {
                            title: String(translations.ja?.title || ''),
                            content: String(translations.ja?.content || ''),
                        },
                    },
                } satisfies GrokImportPayload;
                return nextPayload;
            }
        } catch {
            // Fall through to CSV parsing.
        }
        return null;
    };

    const jsonPayload = tryParseJson();
    if (jsonPayload) return jsonPayload;

    const lines = text
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => line.length > 0);
    if (lines.length < 2) {
        throw new Error('Khong nhan ra JSON hoac CSV hop le tu Grok.');
    }

    const dataLines = lines[0].toLowerCase().includes('chapter_number') ? lines.slice(1) : lines;
    const translations: GrokImportPayload['translations'] = {
        en: { title: '', content: '' },
        'zh-CN': { title: '', content: '' },
        ja: { title: '', content: '' },
    };

    for (const line of dataLines) {
        const cells = parseCsvRow(line);
        if (cells.length < 6) continue;
        const rowChapterNumber = Number(cells[0]);
        const locale = cells[1] as (typeof MANUAL_IMPORT_LOCALES)[number];
        if (!MANUAL_IMPORT_LOCALES.includes(locale)) continue;
        if (!Number.isFinite(rowChapterNumber) || rowChapterNumber !== chapterNumber) continue;
        translations[locale] = {
            title: cells[4] || '',
            content: cells[5] || '',
        };
    }

    if (
        !translations.en.title && !translations.en.content
        && !translations['zh-CN'].title && !translations['zh-CN'].content
        && !translations.ja.title && !translations.ja.content
    ) {
        throw new Error('Khong tim thay dong CSV hop le cho chapter nay.');
    }

    return { chapter_number: chapterNumber, translations };
}

function formatTranslationFailures(failures: TranslationFailure[] | undefined): string {
    if (!Array.isArray(failures) || failures.length === 0) {
        return 'Không nhận được chi tiết lỗi từ backend.';
    }
    return failures
        .map((item) => `${item.locale || 'unknown'}: ${(item.detail || '').trim() || 'Không rõ nguyên nhân lỗi.'}`)
        .join(' | ');
}

function buildTranslateNotice(chapterNumber: number, result: AdminChapterTranslateResult): string {
    const translatedLocales = Array.isArray(result.translated_locales) ? result.translated_locales : [];
    const failedLocales = Array.isArray(result.failed_translations) ? result.failed_translations : [];
    if (failedLocales.length === 0) {
        return `Đã dịch chương ${chapterNumber}: ${translatedLocales.join(', ') || 'không có locale nào cần xử lý'}.`;
    }
    if (translatedLocales.length === 0) {
        return `Chương ${chapterNumber} chưa dịch được locale nào. ${formatTranslationFailures(failedLocales)}`;
    }
    return `Chương ${chapterNumber} dịch được ${translatedLocales.join(', ')}, nhưng còn lỗi: ${formatTranslationFailures(failedLocales)}`;
}

export default function EditChapterPage() {
    const params = useParams();
    const router = useRouter();
    const chapterNumber = Number(params.id);

    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [sourceRawContent, setSourceRawContent] = useState('');
    const [isSideStory, setIsSideStory] = useState(false);
    const [bgmUrl, setBgmUrl] = useState('');
    const [bgmTitle, setBgmTitle] = useState('');
    const [uploadingBgm, setUploadingBgm] = useState(false);
    const [loading, setLoading] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [translating, setTranslating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [token, setToken] = useState<string | null>(null);
    const [translateNotice, setTranslateNotice] = useState<string | null>(null);
    const [manualLocale, setManualLocale] = useState<(typeof MANUAL_IMPORT_LOCALES)[number]>('en');
    const [manualTitle, setManualTitle] = useState('');
    const [manualContent, setManualContent] = useState('');
    const [importingTranslation, setImportingTranslation] = useState(false);
    const [manualImportNotice, setManualImportNotice] = useState<string | null>(null);
    const [grokResponseInput, setGrokResponseInput] = useState('');
    const [grokImporting, setGrokImporting] = useState(false);
    const [grokImportNotice, setGrokImportNotice] = useState<string | null>(null);
    const [templateNotice, setTemplateNotice] = useState<string | null>(null);
    const [grokPromptNotice, setGrokPromptNotice] = useState<string | null>(null);

    useEffect(() => {
        const supabase = createAdminClient();
        if (!supabase) {
            setError('Lỗi cấu hình: thiếu NEXT_PUBLIC_SUPABASE_URL.');
            setInitialLoading(false);
            return;
        }

        supabase.auth.getSession().then(async ({ data: { session } }) => {
            if (!session) {
                router.push('/admin/login');
                return;
            }
            setToken(session.access_token);

            try {
                const metaRes = await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}`);
                if (!metaRes.ok) {
                    setError(`Không tìm thấy thông tin chương ${chapterNumber} (status ${metaRes.status})`);
                    setInitialLoading(false);
                    return;
                }

                const meta = await metaRes.json();
                setTitle(meta.title || `Chương ${chapterNumber}`);
                setIsSideStory(meta.is_side_story || false);
                setBgmUrl(meta.bgm_url || '');
                setBgmTitle(meta.bgm_title || '');

                const contentRes = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}/content`, {
                    headers: { Authorization: `Bearer ${session.access_token}` },
                    cache: 'no-store',
                });

                if (contentRes.ok) {
                    const text = await contentRes.text();
                    setSourceRawContent(text || '');
                    const isHtml = text.trim().startsWith('<');
                    if (isHtml) {
                        setContent(text || '<p></p>');
                    } else {
                        const htmlContent = text
                            .split('\n')
                            .map((line) => line.trim())
                            .filter((line) => line.length > 0)
                            .map((line) => `<p>${line}</p>`)
                            .join('');
                        setContent(htmlContent || '<p></p>');
                    }
                } else {
                    const errData = await contentRes.json().catch(() => ({}));
                    setError(`Lỗi khi tải nội dung chương: ${errData.detail || contentRes.statusText}`);
                }
            } catch (err: any) {
                setError(`Lỗi hệ thống khi tải dữ liệu: ${err.message}`);
            } finally {
                setInitialLoading(false);
            }
        });
    }, [chapterNumber, router]);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!token) return;
        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    title: title.trim(),
                    content: content.trim(),
                    is_side_story: isSideStory,
                    bgm_url: bgmUrl.trim() || null,
                    bgm_title: bgmTitle.trim() || null,
                }),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Lỗi không xác định');

            setSuccess(true);
            setTimeout(() => router.push('/admin/chapters'), 1500);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleTranslate = async () => {
        if (!token) return;
        setTranslating(true);
        setTranslateNotice(null);
        try {
            const result = await translateAdminChapter(chapterNumber, token);
            setTranslateNotice(buildTranslateNotice(chapterNumber, result));
        } catch (err: any) {
            setTranslateNotice(`Lỗi dịch chương ${chapterNumber}: ${err?.message || 'Không nhận được thông báo lỗi từ backend.'}`);
        } finally {
            setTranslating(false);
        }
    };

    const handleManualImport = async () => {
        if (!token) return;
        setImportingTranslation(true);
        setManualImportNotice(null);
        try {
            const result = await importAdminChapterTranslation(
                chapterNumber,
                {
                    locale: manualLocale,
                    title: manualTitle.trim(),
                    content: manualContent.trim(),
                },
                token,
            );
            setManualImportNotice(buildTranslateNotice(chapterNumber, result));
        } catch (err: any) {
            setManualImportNotice(`Lỗi import bản dịch ${manualLocale} cho chương ${chapterNumber}: ${err?.message || 'Không nhận được thông báo lỗi từ backend.'}`);
        } finally {
            setImportingTranslation(false);
        }
    };

    const handleImportGrokResponse = async () => {
        if (!token) return;
        setGrokImporting(true);
        setGrokImportNotice(null);

        try {
            const parsed = extractGrokImportPayload(grokResponseInput, chapterNumber);
            const nonEmptyTranslations = Object.fromEntries(
                Object.entries(parsed.translations).filter(([, value]) => value.title.trim() || value.content.trim()),
            );
            if (Object.keys(nonEmptyTranslations).length === 0) {
                throw new Error('Khong tim thay locale nao co du lieu de import.');
            }
            const result = await importAdminChapterTranslations(
                chapterNumber,
                {
                    translations: nonEmptyTranslations,
                },
                token,
            );
            setGrokImportNotice(buildTranslateNotice(chapterNumber, result));
        } catch (err: any) {
            setGrokImportNotice(`Loi import Grok cho chuong ${chapterNumber}: ${err?.message || 'Khong nhan duoc du lieu hop le.'}`);
        } finally {
            setGrokImporting(false);
        }
    };

    const buildSingleChapterTemplate = () => JSON.stringify(
        {
            instruction: 'Translate the Vietnamese source chapter into en, zh-CN, and ja. Preserve full meaning, paragraph order, and completeness. Return valid JSON only and fill the empty title/content fields.',
            chapter_number: chapterNumber,
            source: {
                locale: 'vi',
                title: title.trim(),
                content: sourceRawContent || content,
            },
            translations: {
                en: { title: '', content: '' },
                'zh-CN': { title: '', content: '' },
                ja: { title: '', content: '' },
            },
        },
        null,
        2,
    );

    const buildSingleLocaleChapterTemplate = (locale: TargetLocale) => JSON.stringify(
        {
            instruction: `Translate the Vietnamese source chapter into ${locale}. Preserve full meaning, paragraph order, and completeness. Return valid JSON only and fill the empty title/content fields.`,
            chapter_number: chapterNumber,
            source: {
                locale: 'vi',
                title: title.trim(),
                content: sourceRawContent || content,
            },
            translations: {
                [locale]: { title: '', content: '' },
            },
        },
        null,
        2,
    );

    const escapeCsvField = (value: string) => `"${String(value || '').replace(/"/g, '""')}"`;

    const buildSingleChapterCsvTemplate = () => {
        const header = 'chapter_number,locale,source_title,source_content,title,content';
        const sourceTitle = escapeCsvField(title.trim());
        const sourceContent = escapeCsvField(sourceRawContent || content || '');
        const rows = MANUAL_IMPORT_LOCALES.map((locale) => (
            [
                chapterNumber,
                locale,
                sourceTitle,
                sourceContent,
                escapeCsvField(''),
                escapeCsvField(''),
            ].join(',')
        ));
        return [header, ...rows].join('\n');
    };

    const buildSingleChapterGrokPrompt = () => [
        'Translate the Vietnamese source chapter into en, zh-CN, and ja.',
        'Return valid JSON only. Do not return Markdown. Do not wrap in code fences. Do not add commentary.',
        'Keep the JSON structure exactly the same as the input.',
        'Do not remove keys. Do not rename keys. Do not add extra keys.',
        'Only fill translations.en.title, translations.en.content, translations["zh-CN"].title, translations["zh-CN"].content, translations.ja.title, and translations.ja.content.',
        'Do not change chapter_number, source.locale, source.title, source.content, or instruction.',
        'Preserve full meaning, paragraph order, names, tone, and completeness.',
        'Do not summarize. Do not censor. Do not skip paragraphs.',
        'Each content field must contain the full translated chapter as plain text.',
        'Use locale-specific output only: en for English, zh-CN for Simplified Chinese, ja for Japanese.',
    ].join('\n');

    const buildSingleLocaleChapterGrokPrompt = (locale: TargetLocale) => [
        `Translate the Vietnamese source chapter into ${locale} only.`,
        'Return valid JSON only. Do not return Markdown. Do not wrap in code fences. Do not add commentary.',
        'Keep the JSON structure exactly the same as the input.',
        'Do not remove keys. Do not rename keys. Do not add extra keys.',
        `Only fill translations["${locale}"].title and translations["${locale}"].content.`,
        'Do not change chapter_number, source.locale, source.title, source.content, or instruction.',
        'Preserve full meaning, paragraph order, names, tone, and completeness.',
        'Do not summarize. Do not censor. Do not skip paragraphs.',
        'Each content field must contain the full translated chapter as plain text.',
    ].join('\n');

    const buildSingleChapterCsvGrokPrompt = () => [
        'Translate the Vietnamese source rows into the target locale of each row.',
        'Return CSV only. Do not return Markdown. Do not wrap in code fences. Do not add explanations.',
        'Keep the exact same header and the exact same number of rows.',
        'Input columns are: chapter_number,locale,source_title,source_content,title,content.',
        'Only fill the last two columns: title and content.',
        'Do not change chapter_number, locale, source_title, or source_content.',
        'Preserve full meaning, paragraph order, names, and chapter completeness.',
        'Content must stay in one CSV field per row, properly quoted.',
        'Use locale-specific output only: en for English, zh-CN for Simplified Chinese, ja for Japanese.',
    ].join('\n');

    const handleCopyTemplate = async () => {
        try {
            await navigator.clipboard.writeText(buildSingleChapterTemplate());
            setTemplateNotice(`Đã copy template JSON chương ${chapterNumber} cho 3 locale.`);
            window.setTimeout(() => setTemplateNotice(null), 2500);
        } catch (err: any) {
            setTemplateNotice(`Không copy được template: ${err?.message || 'Clipboard error'}`);
        }
    };

    const handleCopyGrokPrompt = async () => {
        try {
            await navigator.clipboard.writeText(buildSingleChapterGrokPrompt());
            setGrokPromptNotice(`Da copy prompt Grok cho chuong ${chapterNumber}.`);
            window.setTimeout(() => setGrokPromptNotice(null), 2500);
        } catch (err: any) {
            setGrokPromptNotice(`Khong copy duoc prompt Grok: ${err?.message || 'Clipboard error'}`);
        }
    };

    const handleCopyAllForGrok = async () => {
        try {
            const combined = [
                'GROK PROMPT',
                buildSingleChapterGrokPrompt(),
                '',
                'TEMPLATE',
                buildSingleChapterTemplate(),
            ].join('\n');
            await navigator.clipboard.writeText(combined);
            setGrokPromptNotice(`Da copy ALL FOR GROK cho chuong ${chapterNumber}.`);
            window.setTimeout(() => setGrokPromptNotice(null), 2500);
        } catch (err: any) {
            setGrokPromptNotice(`Khong copy duoc ALL FOR GROK: ${err?.message || 'Clipboard error'}`);
        }
    };

    const handleCopyAllForGrokByFormat = async (format: 'json' | 'csv') => {
        try {
            const combined = [
                'GROK PROMPT',
                format === 'json' ? buildSingleChapterGrokPrompt() : buildSingleChapterCsvGrokPrompt(),
                '',
                'TEMPLATE',
                format === 'json' ? buildSingleChapterTemplate() : buildSingleChapterCsvTemplate(),
            ].join('\n');
            await navigator.clipboard.writeText(combined);
            setGrokPromptNotice(`Da copy ALL FOR GROK (${format.toUpperCase()} ONLY) cho chuong ${chapterNumber}.`);
            window.setTimeout(() => setGrokPromptNotice(null), 2500);
        } catch (err: any) {
            setGrokPromptNotice(`Khong copy duoc ALL FOR GROK (${format.toUpperCase()} ONLY): ${err?.message || 'Clipboard error'}`);
        }
    };

    const handleCopyAllForGrokByLocale = async (locale: TargetLocale) => {
        try {
            const combined = [
                'GROK PROMPT',
                buildSingleLocaleChapterGrokPrompt(locale),
                '',
                'TEMPLATE',
                buildSingleLocaleChapterTemplate(locale),
            ].join('\n');
            await navigator.clipboard.writeText(combined);
            setGrokPromptNotice(`Da copy SAFE MODE ${locale.toUpperCase()} cho chuong ${chapterNumber}.`);
            window.setTimeout(() => setGrokPromptNotice(null), 2500);
        } catch (err: any) {
            setGrokPromptNotice(`Khong copy duoc SAFE MODE ${locale.toUpperCase()}: ${err?.message || 'Clipboard error'}`);
        }
    };

    if (initialLoading) {
        return <div className="font-mono text-xs text-gray-500 animate-pulse">ĐANG TẢI DỮ LIỆU...</div>;
    }

    return (
        <div className="max-w-4xl pb-20">
            <div className="flex items-center justify-between gap-4 mb-6 flex-wrap">
                <div className="flex items-center gap-3">
                    <Link href="/admin/chapters" className="text-gray-500 hover:text-gray-200 transition-colors">
                        <ArrowLeft size={16} />
                    </Link>
                    <h1 className="text-lg font-mono text-gray-100 tracking-wide">SỬA CHƯƠNG {String(chapterNumber).padStart(3, '0')}</h1>
                </div>

                <button
                    type="button"
                    onClick={handleTranslate}
                    disabled={!token || translating}
                    className="flex items-center gap-2 px-4 py-2 rounded-md border border-purple-700/60 text-purple-300 hover:bg-purple-500/10 hover:border-purple-500 disabled:opacity-50 font-mono text-xs"
                >
                    <Languages size={14} />
                    {translating ? 'ĐANG DỊCH 3 NGÔN NGỮ...' : 'DỊCH 3 NGÔN NGỮ'}
                </button>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-3 text-sm mb-4">
                    <CheckCircle2 size={14} />
                    <span>Cập nhật thành công. Đang chuyển về danh sách...</span>
                </div>
            )}

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-3 text-sm mb-4">
                    <AlertTriangle size={14} />
                    <span>{error}</span>
                </div>
            )}

            {translateNotice && (
                <div className="flex items-start gap-2 text-amber-200 bg-amber-950/20 border border-amber-900/40 rounded p-3 text-sm mb-4">
                    <Languages size={14} className="mt-0.5 shrink-0" />
                    <span className="whitespace-pre-wrap break-words">{translateNotice}</span>
                </div>
            )}

            {manualImportNotice && (
                <div className="flex items-start gap-2 text-cyan-100 bg-cyan-950/20 border border-cyan-900/40 rounded p-3 text-sm mb-4">
                    <ClipboardPenLine size={14} className="mt-0.5 shrink-0" />
                    <span className="whitespace-pre-wrap break-words">{manualImportNotice}</span>
                </div>
            )}

            {grokImportNotice && (
                <div className="flex items-start gap-2 text-green-100 bg-green-950/20 border border-green-900/40 rounded p-3 text-sm mb-4">
                    <ClipboardCopy size={14} className="mt-0.5 shrink-0" />
                    <span className="whitespace-pre-wrap break-words">{grokImportNotice}</span>
                </div>
            )}

            {templateNotice && (
                <div className="flex items-start gap-2 text-cyan-100 bg-cyan-950/20 border border-cyan-900/40 rounded p-3 text-sm mb-4">
                    <ClipboardCopy size={14} className="mt-0.5 shrink-0" />
                    <span className="whitespace-pre-wrap break-words">{templateNotice}</span>
                </div>
            )}

            {grokPromptNotice && (
                <div className="flex items-start gap-2 text-cyan-100 bg-cyan-950/20 border border-cyan-900/40 rounded p-3 text-sm mb-4">
                    <ClipboardCopy size={14} className="mt-0.5 shrink-0" />
                    <span className="whitespace-pre-wrap break-words">{grokPromptNotice}</span>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="bg-[#0f0f0f] border border-green-900/40 rounded-lg p-6 space-y-4">
                    <div className="flex items-center justify-between gap-4 flex-wrap">
                        <div>
                            <h2 className="text-sm font-mono text-green-200 tracking-[0.2em] uppercase">Paste Grok Response</h2>
                            <p className="mt-1 text-xs text-gray-500">
                                Dán nguyên JSON hoặc CSV Grok trả về. Hệ thống sẽ tự parse và import 3 locale cho chapter hiện tại.
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={handleImportGrokResponse}
                            disabled={!token || grokImporting || !grokResponseInput.trim()}
                            className="flex items-center gap-2 px-4 py-2 rounded-md border border-green-700/60 text-green-300 hover:bg-green-500/10 hover:border-green-500 disabled:opacity-50 font-mono text-xs"
                        >
                            <ClipboardCopy size={14} />
                            {grokImporting ? 'DANG IMPORT...' : 'IMPORT FROM GROK'}
                        </button>
                    </div>
                    <textarea
                        value={grokResponseInput}
                        onChange={(event) => setGrokResponseInput(event.target.value)}
                        rows={14}
                        className="w-full bg-[#0a0a0a] border border-gray-700 rounded-md px-4 py-3 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors font-mono"
                        placeholder='Paste JSON hoac CSV Grok tra ve vao day...'
                    />
                </div>

                <div className="bg-[#0f0f0f] border border-cyan-900/40 rounded-lg p-6 space-y-4">
                    <div className="flex items-center justify-between gap-4 flex-wrap">
                        <div>
                            <h2 className="text-sm font-mono text-cyan-200 tracking-[0.2em] uppercase">Import bản dịch thủ công</h2>
                            <p className="mt-1 text-xs text-gray-500">
                                Paste bản dịch từ nguồn ngoài như Grok rồi publish qua cùng quality gate đối chiếu với bản VI.
                            </p>
                        </div>
                        <div className="flex items-center gap-2 flex-wrap">
                            <button
                                type="button"
                                onClick={handleCopyTemplate}
                                className="flex items-center gap-2 px-3 py-2 rounded-md border border-cyan-700/60 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 font-mono text-xs"
                            >
                                <ClipboardCopy size={14} />
                                COPY TEMPLATE 3 LOCALE
                            </button>
                            <button
                                type="button"
                                onClick={handleCopyGrokPrompt}
                                className="flex items-center gap-2 px-3 py-2 rounded-md border border-cyan-700/60 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 font-mono text-xs"
                            >
                                <ClipboardCopy size={14} />
                                COPY PROMPT GROK
                            </button>
                            <button
                                type="button"
                                onClick={handleCopyAllForGrok}
                                className="flex items-center gap-2 px-3 py-2 rounded-md border border-cyan-700/60 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 font-mono text-xs"
                            >
                                <ClipboardCopy size={14} />
                                COPY ALL FOR GROK
                            </button>
                            <button
                                type="button"
                                onClick={() => handleCopyAllForGrokByFormat('json')}
                                className="flex items-center gap-2 px-3 py-2 rounded-md border border-cyan-700/60 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 font-mono text-xs"
                            >
                                <ClipboardCopy size={14} />
                                COPY ALL FOR GROK (JSON ONLY)
                            </button>
                            <button
                                type="button"
                                onClick={() => handleCopyAllForGrokByFormat('csv')}
                                className="flex items-center gap-2 px-3 py-2 rounded-md border border-cyan-700/60 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 font-mono text-xs"
                            >
                                <ClipboardCopy size={14} />
                                COPY ALL FOR GROK (CSV ONLY)
                            </button>
                            {LOCALE_SAFE_COPY_OPTIONS.map((option) => (
                                <button
                                    key={option.locale}
                                    type="button"
                                    onClick={() => handleCopyAllForGrokByLocale(option.locale)}
                                    className="flex items-center gap-2 px-3 py-2 rounded-md border border-amber-700/60 text-amber-300 hover:bg-amber-500/10 hover:border-amber-500 font-mono text-xs"
                                >
                                    <ClipboardCopy size={14} />
                                    {option.label}
                                </button>
                            ))}
                            <select
                                value={manualLocale}
                                onChange={(event) => setManualLocale(event.target.value as (typeof MANUAL_IMPORT_LOCALES)[number])}
                                className="bg-[#0a0a0a] border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500 transition-colors"
                            >
                                {MANUAL_IMPORT_LOCALES.map((locale) => (
                                    <option key={locale} value={locale}>{locale}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <p className="text-xs text-amber-300/80">
                        Safe mode cho chapter dai: tach tung locale rieng. Neu Grok hay bi cat giua chung, uu tien `JA ONLY`.
                    </p>

                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-2 tracking-widest uppercase">Tiêu đề bản dịch</label>
                        <input
                            type="text"
                            value={manualTitle}
                            onChange={(event) => setManualTitle(event.target.value)}
                            placeholder={`Tiêu đề ${manualLocale}`}
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded-md px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-2 tracking-widest uppercase">Nội dung bản dịch</label>
                        <textarea
                            value={manualContent}
                            onChange={(event) => setManualContent(event.target.value)}
                            placeholder={`Paste toàn bộ nội dung locale ${manualLocale} vào đây`}
                            rows={12}
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded-md px-4 py-3 text-gray-200 text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                        />
                    </div>

                    <div className="flex justify-end">
                        <button
                            type="button"
                            onClick={handleManualImport}
                            disabled={!token || importingTranslation || !manualTitle.trim() || !manualContent.trim()}
                            className="flex items-center gap-2 px-4 py-2 rounded-md border border-cyan-700/60 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 disabled:opacity-50 font-mono text-xs"
                        >
                            <ClipboardPenLine size={14} />
                            {importingTranslation ? 'ĐANG IMPORT...' : `IMPORT ${manualLocale.toUpperCase()}`}
                        </button>
                    </div>
                </div>

                <div className="bg-[#0f0f0f] border border-gray-800 rounded-lg p-6 space-y-4">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                            <label className="block text-xs font-mono text-gray-500 mb-2 tracking-widest uppercase">BGM URL</label>
                            <div className="flex gap-2">
                            <input
                                type="text"
                                value={bgmUrl}
                                onChange={(event) => setBgmUrl(event.target.value)}
                                placeholder="/media/chapter-bgm.mp3 hoặc https://..."
                                className="w-full bg-[#0a0a0a] border border-gray-700 rounded-md px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                            />
                            <label className={`inline-flex shrink-0 cursor-pointer items-center justify-center rounded-md border border-gray-700 px-3 py-2 text-xs font-mono text-gray-300 transition-colors hover:border-green-500 hover:text-white ${uploadingBgm ? 'pointer-events-none opacity-50' : ''}`}>
                                {uploadingBgm ? 'ĐANG TẢI...' : 'CHỌN FILE'}
                                <input
                                    type="file"
                                    accept="audio/mpeg,audio/mp3,audio/wav,audio/x-wav,audio/ogg,audio/webm,audio/mp4,audio/x-m4a,audio/aac,.mp3,.wav,.ogg,.webm,.m4a,.aac"
                                    className="hidden"
                                    onChange={async (event) => {
                                        const file = event.target.files?.[0];
                                        if (!file || !token) return;
                                        try {
                                            setUploadingBgm(true);
                                            setError('');
                                            const url = await uploadAudioR2(file, token);
                                            setBgmUrl(url);
                                            if (!bgmTitle.trim()) {
                                                const fallbackTitle = file.name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ').trim();
                                                setBgmTitle(fallbackTitle);
                                            }
                                        } catch (err: any) {
                                            setError(err.message || 'Lỗi tải audio BGM');
                                        } finally {
                                            setUploadingBgm(false);
                                            event.target.value = '';
                                        }
                                    }}
                                />
                            </label>
                            </div>
                            <p className="mt-1 text-[11px] text-gray-500">Có thể chọn file local bằng nút bên cạnh, hệ thống sẽ upload lên R2 và tự điền URL public.</p>
                        </div>
                        <div>
                            <label className="block text-xs font-mono text-gray-500 mb-2 tracking-widest uppercase">BGM title</label>
                            <input
                                type="text"
                                value={bgmTitle}
                                onChange={(event) => setBgmTitle(event.target.value)}
                                placeholder="Dark Cello / Ambient Tension"
                                className="w-full bg-[#0a0a0a] border border-gray-700 rounded-md px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                            />
                        </div>
                    </div>

                    {bgmUrl.trim() && (
                        <div className="rounded-lg border border-gray-800 bg-[#0b0b0b] p-4 space-y-3">
                            <div className="flex items-center justify-between gap-3">
                                <div>
                                    <p className="text-xs font-mono tracking-[0.28em] text-gray-500">BGM PREVIEW</p>
                                    <p className="mt-1 text-sm text-gray-200">{bgmTitle.trim() || 'Chưa đặt tiêu đề BGM'}</p>
                                </div>
                                <div className="flex items-center gap-3">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setBgmUrl('');
                                            setBgmTitle('');
                                            setSuccess(false);
                                            setError(null);
                                        }}
                                        className="text-[11px] font-mono tracking-[0.2em] text-red-400 transition-colors hover:text-red-300"
                                    >
                                        XÓA BGM
                                    </button>
                                    <a
                                        href={bgmUrl}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-[11px] font-mono tracking-[0.2em] text-gray-400 transition-colors hover:text-white"
                                    >
                                        MỞ FILE
                                    </a>
                                </div>
                            </div>
                            <audio
                                key={bgmUrl}
                                controls
                                preload="none"
                                src={bgmUrl}
                                className="w-full h-11 rounded-md"
                            >
                                Trình duyệt không hỗ trợ phát audio preview.
                            </audio>
                        </div>
                    )}

                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-2 tracking-widest uppercase">Tiêu đề chương</label>
                        <input
                            type="text"
                            value={title}
                            onChange={(event) => setTitle(event.target.value)}
                            required
                            placeholder="Ví dụ: Đầu lâu không lộ ngoài cửa sổ"
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded-md px-4 py-2.5 text-gray-200 text-base focus:outline-none focus:border-green-500 transition-colors"
                        />
                    </div>

                    <div className="flex items-center gap-2 py-2">
                        <input
                            type="checkbox"
                            id="isSideStory"
                            checked={isSideStory}
                            onChange={(event) => setIsSideStory(event.target.checked)}
                            className="w-4 h-4 rounded bg-[#0a0a0a] border-gray-700 text-green-500 focus:ring-green-500/20 accent-green-600 cursor-pointer"
                        />
                        <label htmlFor="isSideStory" className="text-sm font-mono text-gray-300 cursor-pointer select-none">
                            Đây là ngoại truyện / hồ sơ phụ
                        </label>
                    </div>

                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-2 tracking-widest uppercase">Nội dung chương</label>
                        <RichTextEditor
                            content={content}
                            onChange={(html) => setContent(html)}
                            placeholder="Nội dung chương..."
                            adminToken={token || undefined}
                        />
                    </div>
                </div>

                <div className="flex gap-3 pt-2">
                    <button
                        type="submit"
                        disabled={loading || success}
                        className="flex items-center gap-2 px-8 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-mono text-sm font-bold rounded-md transition-all shadow-lg active:scale-95"
                    >
                        <Save size={16} />
                        {loading ? 'ĐANG LƯU...' : 'LƯU THAY ĐỔI'}
                    </button>
                    <Link
                        href="/admin/chapters"
                        className="px-8 py-3 border border-gray-700 text-gray-400 hover:text-gray-200 font-mono text-sm rounded-md transition-colors"
                    >
                        HỦY
                    </Link>
                </div>
            </form>
        </div>
    );
}
