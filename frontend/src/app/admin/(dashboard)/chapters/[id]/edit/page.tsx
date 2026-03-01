'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { createAdminClient } from '@/lib/supabase-admin';
import { ArrowLeft, Save, AlertTriangle, CheckCircle2 } from 'lucide-react';

// Import React Quill dynamically to avoid SSR issues
const ReactQuill = dynamic(() => import('react-quill-new'), {
    ssr: false,
    loading: () => <div className="h-96 w-full bg-[#0a0a0a] border border-gray-800 rounded animate-pulse" />
});

import 'react-quill-new/dist/quill.snow.css';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-api.onrender.com';

export default function EditChapterPage() {
    const params = useParams();
    const router = useRouter();
    const chapterNumber = Number(params.id);

    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [token, setToken] = useState<string | null>(null);

    // Quill modules configuration
    const modules = useMemo(() => ({
        toolbar: [
            [{ 'header': [1, 2, 3, false] }],
            ['bold', 'italic', 'underline', 'strike'],
            [{ 'list': 'ordered' }, { 'list': 'bullet' }],
            ['clean']
        ],
    }), []);

    // Load chapter data on mount
    useEffect(() => {
        const supabase = createAdminClient();
        if (!supabase) {
            setError('Lỗi cấu hình: Thiếu NEXT_PUBLIC_SUPABASE_URL trên Vercel.');
            setInitialLoading(false);
            return;
        }
        supabase.auth.getSession().then(async ({ data: { session } }) => {
            if (!session) { router.push('/admin/login'); return; }
            setToken(session.access_token);

            try {
                // Fetch chapter metadata
                const metaRes = await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}`);
                if (!metaRes.ok) {
                    setError(`Không tìm thấy thông tin chương ${chapterNumber} (Status: ${metaRes.status})`);
                    setInitialLoading(false);
                    return;
                }
                const meta = await metaRes.json();
                setTitle(meta.title || `Chương ${chapterNumber}`);

                // Fetch chapter content from Backend (Proxy to avoid CORS)
                const contentRes = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}/content`, {
                    headers: { 'Authorization': `Bearer ${session.access_token}` },
                    cache: 'no-store'
                });

                if (contentRes.ok) {
                    const text = await contentRes.text();
                    // Convert plain text to simple HTML for Quill
                    const htmlContent = text.split('\n')
                        .map(line => line.trim())
                        .filter(line => line.length > 0)
                        .map(line => `<p>${line}</p>`)
                        .join('');

                    setContent(htmlContent || '<p></p>');
                } else {
                    const errData = await contentRes.json().catch(() => ({}));
                    console.error("Failed to load content from proxy:", errData);
                    setError(`Lỗi khi tải nội dung chương: ${errData.detail || contentRes.statusText || 'Lỗi proxy'}`);
                }
            } catch (err: any) {
                console.error("Error loading chapter:", err);
                setError(`Lỗi hệ thống khi tải dữ liệu: ${err.message}`);
            } finally {
                setInitialLoading(false);
            }
        });
    }, [chapterNumber, router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;
        setLoading(true);
        setError(null);

        // Strip HTML if necessary for backend (though backend already accepts strings)
        // For now we keep it simple as the backend expects content: str
        const cleanContent = content
            .replace(/<\/p><p>/g, '\n')
            .replace(/<p>/g, '')
            .replace(/<\/p>/g, '')
            .replace(/<br\s*\/?>/g, '\n')
            .replace(/&nbsp;/g, ' ');

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    title: title.trim(),
                    content: cleanContent.trim()
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

    if (initialLoading) {
        return <div className="font-mono text-xs text-gray-500 animate-pulse">ĐANG TẢI DỮ LIỆU...</div>;
    }

    return (
        <div className="max-w-4xl pb-20">
            <style jsx global>{`
                .ql-container {
                    background: #0a0a0a !important;
                    border-color: #1f2937 !important;
                    color: #e5e7eb !important;
                    font-family: inherit !important;
                    font-size: 1rem !important;
                    min-height: 500px;
                }
                .ql-toolbar {
                    background: #111827 !important;
                    border-color: #1f2937 !important;
                }
                .ql-stroke { stroke: #9ca3af !important; }
                .ql-fill { fill: #9ca3af !important; }
                .ql-picker { color: #9ca3af !important; }
            `}</style>

            <div className="flex items-center gap-3 mb-6">
                <Link href="/admin/chapters" className="text-gray-500 hover:text-gray-200 transition-colors">
                    <ArrowLeft size={16} />
                </Link>
                <h1 className="text-lg font-mono text-gray-100 tracking-wide">SỬA CHƯƠNG {String(chapterNumber).padStart(3, '0')}</h1>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-3 text-sm mb-4">
                    <CheckCircle2 size={14} />
                    <span>Cập nhật thành công! Đang chuyển về danh sách...</span>
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
                            onChange={(e) => setTitle(e.target.value)}
                            required
                            placeholder="Ví dụ: Đầu lâu khổng lồ ngoài cửa sổ"
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded-md px-4 py-2.5 text-gray-200 text-base focus:outline-none focus:border-green-500 transition-colors"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-2 tracking-widest uppercase">Nội dung chương</label>
                        <ReactQuill
                            theme="snow"
                            value={content}
                            onChange={setContent}
                            modules={modules}
                            className="rounded-md overflow-hidden"
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
