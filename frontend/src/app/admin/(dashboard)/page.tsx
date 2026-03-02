import { BarChart3, BookOpen, TrendingUp, PlusCircle, Eye, Heart } from 'lucide-react';
import Link from 'next/link';
import { getServerAdminClient } from '@/lib/supabase-server';
import { getChapters, getNovelSettings } from '@/lib/api';

async function getDashboardData() {
    try {
        const [novel, chaptersResp] = await Promise.all([
            getNovelSettings(),
            getChapters(1, 1)
        ]);
        return {
            total: novel.total_chapters || chaptersResp.total || 0,
            max_chapter: novel.max_chapter || chaptersResp.max_chapter || 0,
            total_views: novel.total_views || 0,
            total_likes: novel.total_likes || 0
        };
    } catch {
        return { total: 0, max_chapter: 0, total_views: 0, total_likes: 0 };
    }
}

async function getTopChapters() {
    const supabase = await getServerAdminClient();
    try {
        const { data } = await supabase
            .from('chapters')
            .select('chapter_number, title, view_count')
            .order('view_count', { ascending: false })
            .limit(5);
        return data || [];
    } catch {
        return [];
    }
}

async function getTopLiked() {
    const supabase = await getServerAdminClient();
    try {
        const { data } = await supabase
            .from('chapters')
            .select('chapter_number, title, likes_count')
            .order('likes_count', { ascending: false })
            .limit(5);
        return data || [];
    } catch {
        return [];
    }
}

export default async function AdminDashboardPage() {
    const [stats, topChapters, topLiked] = await Promise.all([
        getDashboardData(),
        getTopChapters(),
        getTopLiked(),
    ]);

    const totalViews = stats.total_views;
    const totalLikes = stats.total_likes;

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-xl font-mono text-gray-100 tracking-wide">DASHBOARD</h1>
                <p className="text-xs font-mono text-gray-600 mt-1">Tổng quan hệ thống - Mạt Thế ☣</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <BookOpen size={14} className="text-green-400" />
                        <span className="text-xs font-mono text-gray-500 tracking-widest">TỔNG CHƯƠNG</span>
                    </div>
                    <div className="text-3xl font-mono text-green-400 font-bold">{stats.max_chapter}</div>
                </div>

                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp size={14} className="text-blue-400" />
                        <span className="text-xs font-mono text-gray-500 tracking-widest">CHƯƠNG MỚI</span>
                    </div>
                    <div className="text-3xl font-mono text-blue-400 font-bold">{stats.max_chapter}</div>
                </div>

                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Eye size={14} className="text-purple-400" />
                        <span className="text-xs font-mono text-gray-500 tracking-widest">TỔNG VIEW</span>
                    </div>
                    <div className="text-3xl font-mono text-purple-400 font-bold">{totalViews.toLocaleString()}</div>
                </div>

                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Heart size={14} className="text-red-400" />
                        <span className="text-xs font-mono text-gray-500 tracking-widest">TỔNG TIM</span>
                    </div>
                    <div className="text-3xl font-mono text-red-400 font-bold">{totalLikes.toLocaleString()}</div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Top Read Chapters */}
                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-5">
                    <div className="flex items-center gap-2 mb-4">
                        <Eye size={14} className="text-purple-400" />
                        <h2 className="text-xs font-mono text-gray-500 tracking-widest uppercase">Top 5 chương đọc nhiều nhất</h2>
                    </div>
                    <div className="space-y-3">
                        {topChapters.length > 0 ? (
                            topChapters.map((ch: any, idx: number) => {
                                const maxViews = topChapters[0]?.view_count || 1;
                                const pct = Math.max(5, ((ch.view_count || 0) / maxViews) * 100);
                                return (
                                    <div key={ch.chapter_number} className="group">
                                        <div className="flex items-center justify-between mb-1">
                                            <div className="flex items-center gap-2">
                                                <span className={`text-[10px] font-mono font-bold w-5 text-center rounded-sm py-0.5 ${idx === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                                                    idx === 1 ? 'bg-gray-400/20 text-gray-300' :
                                                        idx === 2 ? 'bg-amber-700/20 text-amber-500' :
                                                            'text-gray-700'
                                                    }`}>{idx + 1}</span>
                                                <span className="text-sm text-gray-300 font-mono truncate max-w-[180px]">
                                                    Ch.{ch.chapter_number}: {ch.title}
                                                </span>
                                            </div>
                                            <span className="text-xs font-mono text-purple-400 font-bold">
                                                {(ch.view_count || 0).toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-900 rounded-full h-1">
                                            <div className="bg-purple-500/50 h-1 rounded-full transition-all" style={{ width: `${pct}%` }} />
                                        </div>
                                    </div>
                                );
                            })
                        ) : (
                            <p className="text-xs font-mono text-gray-600 italic">Chưa có dữ liệu lượt xem...</p>
                        )}
                    </div>
                </div>

                {/* Top Liked Chapters */}
                <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg p-5">
                    <div className="flex items-center gap-2 mb-4">
                        <Heart size={14} className="text-red-400" />
                        <h2 className="text-xs font-mono text-gray-500 tracking-widest uppercase">Top 5 chương được yêu thích</h2>
                    </div>
                    <div className="space-y-3">
                        {topLiked.length > 0 ? (
                            topLiked.map((ch: any, idx: number) => {
                                const maxLikes = topLiked[0]?.likes_count || 1;
                                const pct = Math.max(5, ((ch.likes_count || 0) / maxLikes) * 100);
                                return (
                                    <div key={ch.chapter_number} className="group">
                                        <div className="flex items-center justify-between mb-1">
                                            <div className="flex items-center gap-2">
                                                <span className={`text-[10px] font-mono font-bold w-5 text-center rounded-sm py-0.5 ${idx === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                                                    idx === 1 ? 'bg-gray-400/20 text-gray-300' :
                                                        idx === 2 ? 'bg-amber-700/20 text-amber-500' :
                                                            'text-gray-700'
                                                    }`}>{idx + 1}</span>
                                                <span className="text-sm text-gray-300 font-mono truncate max-w-[180px]">
                                                    Ch.{ch.chapter_number}: {ch.title}
                                                </span>
                                            </div>
                                            <span className="text-xs font-mono text-red-400 font-bold flex items-center gap-1">
                                                <Heart size={10} fill="currentColor" />
                                                {(ch.likes_count || 0).toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-900 rounded-full h-1">
                                            <div className="bg-red-500/50 h-1 rounded-full transition-all" style={{ width: `${pct}%` }} />
                                        </div>
                                    </div>
                                );
                            })
                        ) : (
                            <p className="text-xs font-mono text-gray-600 italic">Chưa có dữ liệu lượt thích...</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="mb-8">
                <h2 className="text-xs font-mono text-gray-600 tracking-widest mb-3 uppercase">Thao tác nhanh</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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

            {/* Info box */}
            <div className="bg-[#0d0d0d] border border-yellow-900/40 rounded-lg p-4 text-xs font-mono text-gray-500">
                <span className="text-yellow-500">⚠ LƯU Ý:</span> Trang này chỉ dành cho Admin. Mọi thay đổi sẽ có hiệu lực ngay trên web sau khi lưu.
            </div>
        </div>
    );
}
