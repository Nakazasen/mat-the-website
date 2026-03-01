'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { createAdminClient } from '@/lib/supabase-admin';
import { useRouter } from 'next/navigation';
import { PlusCircle, Pencil, Trash2, RefreshCw, AlertTriangle } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-api.onrender.com';

interface Chapter {
    id: number;
    chapter_number: number;
    title: string;
    word_count?: number;
}

export default function AdminChaptersPage() {
    const router = useRouter();
    const [chapters, setChapters] = useState<Chapter[]>([]);
    const [loading, setLoading] = useState(true);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [token, setToken] = useState<string | null>(null);

    useEffect(() => {
        const supabase = createAdminClient();
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session) { router.push('/admin/login'); return; }
            setToken(session.access_token);
        });
    }, [router]);

    const fetchChapters = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE_URL}/api/chapters?page=1&limit=100&sort=desc`, { cache: 'no-store' });
            if (!res.ok) throw new Error('Không thể tải danh sách chương');
            const data = await res.json();
            setChapters(data.chapters || []);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchChapters(); }, [fetchChapters]);

    const handleDelete = async (chapterNumber: number) => {
        if (!token) return;
        if (!confirm(`Bạn chắc muốn XÓA Chương ${chapterNumber}?\nHành động này không thể hoàn tác!`)) return;

        setDeletingId(chapterNumber);
        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` },
            });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Lỗi khi xóa');
            }
            await fetchChapters();
        } catch (err: any) {
            alert(`Lỗi: ${err.message}`);
        } finally {
            setDeletingId(null);
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-lg font-mono text-gray-100 tracking-wide">QUẢN LÝ CHƯƠNG</h1>
                    <p className="text-xs font-mono text-gray-600 mt-0.5">{chapters.length} chương đang hiển thị</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={fetchChapters}
                        className="flex items-center gap-1.5 px-3 py-2 border border-gray-700 text-gray-400 hover:text-gray-200 rounded font-mono text-xs transition-colors"
                    >
                        <RefreshCw size={12} />
                        Làm mới
                    </button>
                    <Link
                        href="/admin/chapters/new"
                        className="flex items-center gap-1.5 px-3 py-2 bg-green-600 hover:bg-green-500 text-white rounded font-mono text-xs transition-colors"
                    >
                        <PlusCircle size={12} />
                        Đăng Chương Mới
                    </Link>
                </div>
            </div>

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-3 text-sm mb-4">
                    <AlertTriangle size={14} />
                    <span>{error}</span>
                </div>
            )}

            {loading ? (
                <div className="space-y-2">
                    {Array.from({ length: 10 }).map((_, i) => (
                        <div key={i} className="h-10 bg-[#0d0d0d] rounded animate-pulse border border-gray-800" />
                    ))}
                </div>
            ) : (
                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg overflow-hidden">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-gray-800">
                                <th className="px-4 py-2.5 text-left font-mono text-xs text-gray-600 tracking-widest">#</th>
                                <th className="px-4 py-2.5 text-left font-mono text-xs text-gray-600 tracking-widest">TIÊU ĐỀ</th>
                                <th className="px-4 py-2.5 text-right font-mono text-xs text-gray-600 tracking-widest">TỪ</th>
                                <th className="px-4 py-2.5 text-right font-mono text-xs text-gray-600 tracking-widest">HÀNH ĐỘNG</th>
                            </tr>
                        </thead>
                        <tbody>
                            {chapters.map((ch) => (
                                <tr key={ch.id} className="border-b border-gray-800/50 hover:bg-gray-800/20 transition-colors">
                                    <td className="px-4 py-2.5 font-mono text-xs text-green-400">
                                        {String(ch.chapter_number).padStart(3, '0')}
                                    </td>
                                    <td className="px-4 py-2.5 text-gray-300 max-w-xs truncate">{ch.title}</td>
                                    <td className="px-4 py-2.5 text-right font-mono text-xs text-gray-600">
                                        {ch.word_count?.toLocaleString() || '—'}
                                    </td>
                                    <td className="px-4 py-2.5 text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            <Link
                                                href={`/admin/chapters/${ch.chapter_number}/edit`}
                                                className="flex items-center gap-1 px-2.5 py-1 border border-gray-700 hover:border-blue-500 text-gray-400 hover:text-blue-400 rounded text-xs font-mono transition-colors"
                                            >
                                                <Pencil size={10} />
                                                Sửa
                                            </Link>
                                            <button
                                                onClick={() => handleDelete(ch.chapter_number)}
                                                disabled={deletingId === ch.chapter_number}
                                                className="flex items-center gap-1 px-2.5 py-1 border border-gray-700 hover:border-red-600 text-gray-500 hover:text-red-400 disabled:opacity-50 rounded text-xs font-mono transition-colors"
                                            >
                                                <Trash2 size={10} />
                                                {deletingId === ch.chapter_number ? '...' : 'Xóa'}
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
