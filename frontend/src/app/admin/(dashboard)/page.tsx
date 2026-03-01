import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { BarChart3, BookOpen, TrendingUp, PlusCircle } from 'lucide-react';
import Link from 'next/link';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-website.onrender.com';

async function getStats() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/chapters?page=1&limit=1`, { cache: 'no-store' });
        if (!res.ok) return { total: 0, max_chapter: 0 };
        const data = await res.json();
        return { total: data.total || 0, max_chapter: data.max_chapter || 0 };
    } catch {
        return { total: 0, max_chapter: 0 };
    }
}

async function getTopChapters() {
    try {
        const cookieStore = await cookies();
        const supabaseToken = cookieStore.get('sb-access-token')?.value;

        const res = await fetch(`${API_BASE_URL}/api/admin/analytics/top-chapters?limit=5`, {
            headers: {
                'Authorization': `Bearer ${supabaseToken}`
            },
            cache: 'no-store'
        });
        if (!res.ok) return [];
        return await res.json();
    } catch {
        return [];
    }
}

export default async function AdminDashboardPage() {
    const stats = await getStats();
    const topChapters = await getTopChapters();

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-xl font-mono text-gray-100 tracking-wide">DASHBOARD</h1>
                <p className="text-xs font-mono text-gray-600 mt-1">Tổng quan hệ thống - Mạt Thế ☣</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <BookOpen size={14} className="text-green-400" />
                        <span className="text-xs font-mono text-gray-500 tracking-widest">TỔNG CHƯƠNG</span>
                    </div>
                    <div className="text-3xl font-mono text-green-400 font-bold">{stats.total}</div>
                </div>

                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp size={14} className="text-blue-400" />
                        <span className="text-xs font-mono text-gray-500 tracking-widest">CHƯƠNG MỚI NHẤT</span>
                    </div>
                    <div className="text-3xl font-mono text-blue-400 font-bold">{stats.max_chapter}</div>
                </div>

                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <BarChart3 size={14} className="text-yellow-400" />
                        <span className="text-xs font-mono text-gray-500 tracking-widest">STATUS</span>
                    </div>
                    <div className="text-sm font-mono text-yellow-400 font-bold mt-2">🟢 ONLINE</div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Top Read Chapters */}
                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-5">
                    <h2 className="text-xs font-mono text-gray-500 tracking-widest mb-4 uppercase">Chương đọc nhiều nhất</h2>
                    <div className="space-y-3">
                        {topChapters.length > 0 ? (
                            topChapters.map((ch: any, idx: number) => (
                                <div key={ch.chapter_number} className="flex items-center justify-between border-b border-gray-900 pb-2 last:border-0">
                                    <div className="flex items-center gap-3">
                                        <span className="text-[10px] font-mono text-gray-700 w-4">{idx + 1}.</span>
                                        <div className="text-sm text-gray-300 font-mono truncate max-w-[200px]">
                                            Chương {ch.chapter_number}: {ch.title}
                                        </div>
                                    </div>
                                    <div className="text-xs font-mono text-green-500">
                                        {ch.view_count.toLocaleString()} <span className="text-[10px] text-gray-600">LẦN</span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-xs font-mono text-gray-600 italic">Chưa có dữ liệu thống kê...</p>
                        )}
                    </div>
                </div>

                {/* Quick Actions */}
                <div>
                    <h2 className="text-xs font-mono text-gray-600 tracking-widest mb-3 uppercase">Thao tác nhanh</h2>
                    <div className="flex flex-col gap-3">
                        <Link
                            href="/admin/chapters/new"
                            className="flex items-center gap-3 px-4 py-3 bg-green-950/20 border border-green-900/40 text-green-400 hover:bg-green-900/30 rounded font-mono text-sm transition-all"
                        >
                            <PlusCircle size={16} />
                            Đăng Chương Mới
                        </Link>
                        <Link
                            href="/admin/chapters"
                            className="flex items-center gap-3 px-4 py-3 bg-blue-950/20 border border-blue-900/40 text-blue-400 hover:bg-blue-900/30 rounded font-mono text-sm transition-all"
                        >
                            <BookOpen size={16} />
                            Quản Lý Chương
                        </Link>
                    </div>
                </div>
            </div>

            {/* Info box */}
            <div className="bg-[#0d0d0d] border border-yellow-900/40 rounded-lg p-4 text-xs font-mono text-gray-500">
                <span className="text-yellow-500">⚠ LƯU Ý:</span> Trang này chỉ dành cho Admin. Mọi thay đổi sẽ có hiệu lực ngay trên web sau khi lưu.
            </div>
        </div>
    );
}
