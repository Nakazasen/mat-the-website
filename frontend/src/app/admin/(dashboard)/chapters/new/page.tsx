'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { createAdminClient } from '@/lib/supabase-admin';
import { ArrowLeft, Save, AlertTriangle, CheckCircle2 } from 'lucide-react';
import RichTextEditor from '@/components/Editor';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
const ADMIN_TOKEN = process.env.NEXT_PUBLIC_ADMIN_TOKEN || "mat-the-admin-2026";

export default function NewChapterPage() {
    const router = useRouter();
    const [chapterNumber, setChapterNumber] = useState('');
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [isSideStory, setIsSideStory] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const supabase = createAdminClient();
        if (!supabase) {
            setError('Lỗi cấu hình: Thiếu NEXT_PUBLIC_SUPABASE_URL trên Vercel.');
            setLoading(false);
            return;
        }
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
            router.push('/admin/login');
            return;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/chapters`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`,
                },
                body: JSON.stringify({
                    chapter_number: parseInt(chapterNumber),
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

    return (
        <div className="max-w-3xl">
            <div className="flex items-center gap-3 mb-6">
                <Link href="/admin/chapters" className="text-gray-500 hover:text-gray-200 transition-colors">
                    <ArrowLeft size={16} />
                </Link>
                <h1 className="text-lg font-mono text-gray-100 tracking-wide">ĐĂNG CHƯƠNG MỚI</h1>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-3 text-sm mb-4">
                    <CheckCircle2 size={14} />
                    <span>Đăng chương thành công! Đang chuyển về danh sách...</span>
                </div>
            )}

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-3 text-sm mb-4">
                    <AlertTriangle size={14} />
                    <span>{error}</span>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">SỐ CHƯƠNG *</label>
                        <input
                            type="number"
                            value={chapterNumber}
                            onChange={(e) => setChapterNumber(e.target.value)}
                            required
                            min="1"
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                            placeholder="814"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">TIÊU ĐỀ *</label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            required
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                            placeholder="Tên chương..."
                        />
                    </div>
                </div>

                <div className="flex items-center gap-2 py-2">
                    <input
                        type="checkbox"
                        id="isSideStory"
                        checked={isSideStory}
                        onChange={(e) => setIsSideStory(e.target.checked)}
                        className="w-4 h-4 rounded bg-[#0a0a0a] border-gray-700 text-green-500 focus:ring-green-500/20 accent-green-600 cursor-pointer"
                    />
                    <label htmlFor="isSideStory" className="text-sm font-mono text-gray-300 cursor-pointer select-none">
                        📜 Đây là Ngoại Truyện / Hồ sơ phụ (Không làm loạn số mạch truyện chính)
                    </label>
                </div>

                <div>
                    <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">
                        NỘI DUNG * ({content.trim().split(/\s+/).filter(Boolean).length} từ)
                    </label>
                    <RichTextEditor
                        content={content}
                        onChange={(html) => setContent(html)}
                        placeholder="Bắt đầu viết chương mới ở đây..."
                        adminToken={ADMIN_TOKEN}
                    />
                </div>

                <div className="flex gap-3 pt-2">
                    <button
                        type="submit"
                        disabled={loading || success}
                        className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-mono text-sm rounded transition-all"
                    >
                        <Save size={14} />
                        {loading ? 'ĐANG LƯU...' : 'ĐĂNG CHƯƠNG'}
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
