'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { AlertTriangle, ArrowLeft, CheckCircle2, Languages, Save } from 'lucide-react';

import RichTextEditor from '@/components/Editor';
import { translateAdminChapter } from '@/lib/api';
import { createAdminClient } from '@/lib/supabase-admin';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function EditChapterPage() {
    const params = useParams();
    const router = useRouter();
    const chapterNumber = Number(params.id);

    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [isSideStory, setIsSideStory] = useState(false);
    const [loading, setLoading] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [translating, setTranslating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [token, setToken] = useState<string | null>(null);

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

                const contentRes = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}/content`, {
                    headers: { Authorization: `Bearer ${session.access_token}` },
                    cache: 'no-store',
                });

                if (contentRes.ok) {
                    const text = await contentRes.text();
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
        try {
            const result = await translateAdminChapter(chapterNumber, token);
            alert(`Đã dịch chương ${chapterNumber}: ${result.translated_locales.join(', ')}`);
        } catch (err: any) {
            alert(`Lỗi dịch chương ${chapterNumber}: ${err.message}`);
        } finally {
            setTranslating(false);
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

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="bg-[#0f0f0f] border border-gray-800 rounded-lg p-6 space-y-4">
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
