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

export default async function AdminDashboardPage() {
    const stats = await getStats();

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

            {/* Quick Actions */}
            <div className="mb-6">
                <h2 className="text-xs font-mono text-gray-600 tracking-widest mb-3">THAO TÁC NHANH</h2>
                <div className="flex flex-wrap gap-3">
                    <Link
                        href="/admin/chapters/new"
                        className="flex items-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-500 text-white rounded font-mono text-sm transition-colors"
                    >
                        <PlusCircle size={14} />
                        Đăng Chương Mới
                    </Link>
                    <Link
                        href="/admin/chapters"
                        className="flex items-center gap-2 px-4 py-2.5 border border-gray-700 text-gray-300 hover:border-gray-500 hover:text-white rounded font-mono text-sm transition-colors"
                    >
                        <BookOpen size={14} />
                        Quản Lý Chương
                    </Link>
                </div>
            </div>

            {/* Info box */}
            <div className="bg-[#0d0d0d] border border-yellow-900/40 rounded-lg p-4 text-xs font-mono text-gray-500">
                <span className="text-yellow-500">⚠ LƯU Ý:</span> Trang này chỉ dành cho Admin. Mọi thay đổi sẽ có hiệu lực ngay trên web sau khi lưu.
            </div>
        </div>
    );
}
