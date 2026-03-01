'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { createAdminClient } from '@/lib/supabase-admin';
import { ArrowLeft, Save, AlertTriangle, CheckCircle2 } from 'lucide-react';

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

    // Load chapter data on mount
    useEffect(() => {
        const supabase = createAdminClient();
        supabase.auth.getSession().then(async ({ data: { session } }) => {
            if (!session) { router.push('/admin/login'); return; }
            setToken(session.access_token);

            // Fetch chapter metadata
            const metaRes = await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}`);
            if (!metaRes.ok) { setError('Không tìm thấy chương'); setInitialLoading(false); return; }
            const meta = await metaRes.json();
            setTitle(meta.title);

            // Fetch chapter content from R2
            if (meta.content_url) {
                const contentRes = await fetch(meta.content_url, { cache: 'no-store' });
                if (contentRes.ok) setContent(await contentRes.text());
            }
            setInitialLoading(false);
        });
    }, [chapterNumber, router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;
        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ title: title.trim(), content: content.trim() }),
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
        <div className="max-w-3xl">
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

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">TIÊU ĐỀ *</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                        className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                    />
                </div>

                <div>
                    <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">
                        NỘI DUNG * ({content.trim().split(/\s+/).filter(Boolean).length} từ)
                    </label>
                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        required
                        rows={20}
                        className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors font-mono leading-relaxed resize-y"
                    />
                </div>

                <div className="flex gap-3 pt-2">
                    <button
                        type="submit"
                        disabled={loading || success}
                        className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-mono text-sm rounded transition-all"
                    >
                        <Save size={14} />
                        {loading ? 'ĐANG LƯU...' : 'LƯU THAY ĐỔI'}
                    </button>
                    <Link
                        href="/admin/chapters"
                        className="px-5 py-2.5 border border-gray-700 text-gray-400 hover:text-gray-200 font-mono text-sm rounded transition-colors"
                    >
                        HỦY
                    </Link>
                </div>
            </form>
        </div>
    );
}
