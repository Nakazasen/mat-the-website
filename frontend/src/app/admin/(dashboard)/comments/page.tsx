'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { MessageSquare, Trash2, Loader2, CheckCircle2, AlertTriangle, Pencil, X, Save, Search, ChevronLeft, ChevronRight } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface Comment {
    id: string;
    chapter_number: number;
    user_name: string;
    content: string;
    created_at: string;
}

export default function AdminCommentsPage() {
    const router = useRouter();
    const [comments, setComments] = useState<Comment[]>([]);
    const [loading, setLoading] = useState(true);
    const [token, setToken] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Pagination
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalComments, setTotalComments] = useState(0);
    const limit = 20;

    // Edit state
    const [editingComment, setEditingComment] = useState<Comment | null>(null);
    const [editContent, setEditContent] = useState('');
    const [saving, setSaving] = useState(false);

    const loadComments = async (currentPage = page) => {
        setLoading(true);
        const supabase = createAdminClient();
        if (!supabase) return;

        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
            router.push('/admin/login');
            return;
        }
        setToken(session.access_token);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/comments?page=${currentPage}&limit=${limit}`, {
                headers: { 'Authorization': `Bearer ${session.access_token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setComments(data.comments);
                setTotalPages(data.total_pages);
                setTotalComments(data.total);
            } else {
                const err = await res.json();
                setError(err.detail || "Không có quyền truy cập danh sách bình luận.");
            }
        } catch (err) {
            setError("Lỗi kết nối server.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadComments(page);
    }, [page, router]);

    const handleDelete = async (commentId: string) => {
        if (!token) return;
        if (!confirm('Bạn có chắc muốn xoá bình luận này?\nHành động này không thể hoàn tác.')) return;

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/comments/${commentId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                setComments(comments.filter(c => c.id !== commentId));
                setTotalComments(prev => prev - 1);
                setSuccess('Đã xoá bình luận thành công');
                setTimeout(() => setSuccess(null), 3000);
            } else {
                const data = await res.json();
                setError(data.detail || "Lỗi khi xoá bình luận");
            }
        } catch (err) {
            setError("Lỗi kết nối server.");
        }
    };

    const startEdit = (comment: Comment) => {
        setEditingComment(comment);
        setEditContent(comment.content);
        setError(null);
        setSuccess(null);
    };

    const handleSaveEdit = async () => {
        if (!token || !editingComment) return;
        if (!editContent.trim()) {
            setError("Nội dung không được để trống");
            return;
        }

        setSaving(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/comments/${editingComment.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    content: editContent.trim()
                })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Lỗi khi cập nhật bình luận');

            setSuccess('Đã cập nhật bình luận');
            setEditingComment(null);
            setTimeout(() => setSuccess(null), 3000);

            // Update in local state to avoid refetch
            setComments(comments.map(c =>
                c.id === editingComment.id ? { ...c, content: editContent.trim() } : c
            ));
        } catch (err: any) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="max-w-6xl">
            <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
                        <MessageSquare className="text-green-500" size={24} />
                        QUẢN LÝ BÌNH LUẬN
                    </h1>
                    <p className="text-gray-500 text-sm font-mono mt-1">
                        Kiểm duyệt, sửa hoặc xoá bình luận của độc giả. Tổng: {totalComments} bình luận.
                    </p>
                </div>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-4 text-sm mb-6 animate-in fade-in slide-in-from-top-2">
                    <CheckCircle2 size={16} />
                    <span>{success}</span>
                </div>
            )}

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-4 text-sm mb-6">
                    <AlertTriangle size={16} />
                    <span>{error}</span>
                </div>
            )}

            {/* EDIT MODAL */}
            {editingComment && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
                    <div className="bg-[#181818] border border-gray-700 rounded-lg p-6 w-full max-w-xl mx-4 shadow-2xl">
                        <div className="flex items-center justify-between mb-6 border-b border-gray-800 pb-3">
                            <h2 className="text-sm font-mono text-gray-200 uppercase tracking-widest flex items-center gap-2">
                                <Pencil className="text-green-500" size={16} />
                                Chỉnh Sửa Bình Luận
                            </h2>
                            <button onClick={() => setEditingComment(null)} className="text-gray-500 hover:text-gray-300 transition-colors">
                                <X size={18} />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-xs font-mono text-gray-500 mb-2">
                                <span>Chương: {editingComment.chapter_number}</span>
                                <span>•</span>
                                <span>Người đăng: {editingComment.user_name}</span>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    Nội dung
                                </label>
                                <textarea
                                    value={editContent}
                                    onChange={(e) => setEditContent(e.target.value)}
                                    rows={5}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded p-3 text-gray-200 text-sm focus:border-green-500 outline-none transition-all resize-none"
                                />
                            </div>
                        </div>

                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => setEditingComment(null)}
                                className="flex-1 py-2.5 border border-gray-700 text-gray-400 hover:text-gray-200 hover:border-gray-600 rounded font-mono text-xs tracking-widest transition-all"
                            >
                                HỦY
                            </button>
                            <button
                                onClick={handleSaveEdit}
                                disabled={saving}
                                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded font-mono text-xs tracking-widest transition-all"
                            >
                                {saving ? <Loader2 className="animate-spin" size={14} /> : <Save size={14} />}
                                {saving ? "ĐANG LƯU..." : "LƯU THAY ĐỔI"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* TABLE */}
            <div className="bg-[#181818] border border-gray-800 rounded-lg overflow-x-auto">
                <table className="w-full text-left text-sm font-mono whitespace-nowrap">
                    <thead className="bg-[#0d0d0d] border-b border-gray-800 text-gray-500 uppercase text-[10px] tracking-[0.2em]">
                        <tr>
                            <th className="px-4 py-4 sm:px-6 w-16 text-center">Chương</th>
                            <th className="px-4 py-4 sm:px-6 w-1/5">Người dùng</th>
                            <th className="px-4 py-4 sm:px-6 min-w-[300px]">Nội dung</th>
                            <th className="px-4 py-4 sm:px-6 w-32">Ngày đăng</th>
                            <th className="px-4 py-4 sm:px-6 w-24 text-right">Thao tác</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {loading ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-12 text-center">
                                    <Loader2 className="animate-spin text-green-500 max-w-full mx-auto" size={24} />
                                </td>
                            </tr>
                        ) : comments.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-8 text-center text-gray-500 text-xs italic">
                                    Chưa có bình luận nào.
                                </td>
                            </tr>
                        ) : (
                            comments.map((comment) => (
                                <tr key={comment.id} className="hover:bg-gray-800/20 transition-colors group">
                                    <td className="px-4 py-4 sm:px-6 text-center">
                                        <span className="text-gray-400 font-bold">{comment.chapter_number}</span>
                                    </td>
                                    <td className="px-4 py-4 sm:px-6">
                                        <div className="text-green-400 font-bold truncate">{comment.user_name}</div>
                                    </td>
                                    <td className="px-4 py-4 sm:px-6 max-w-[300px] sm:max-w-md lg:max-w-xl">
                                        <div className="text-gray-300 truncate font-sans text-sm" title={comment.content}>
                                            {comment.content}
                                        </div>
                                    </td>
                                    <td className="px-4 py-4 sm:px-6 text-xs text-gray-500">
                                        {new Date(comment.created_at).toLocaleDateString('vi-VN')}
                                    </td>
                                    <td className="px-4 py-4 sm:px-6 text-right">
                                        <div className="flex items-center justify-end gap-1">
                                            <button
                                                onClick={() => startEdit(comment)}
                                                className="text-gray-600 hover:text-green-500 transition-colors p-2"
                                                title="Sửa nội dung"
                                            >
                                                <Pencil size={15} />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(comment.id)}
                                                className="text-gray-600 hover:text-red-500 transition-colors p-2"
                                                title="Xoá bình luận"
                                            >
                                                <Trash2 size={15} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {!loading && totalPages > 1 && (
                <div className="flex items-center justify-between mt-6 bg-[#181818] border border-gray-800 p-4 rounded-lg">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="flex items-center gap-2 px-3 py-1.5 border border-gray-700 rounded text-gray-400 font-mono text-xs hover:text-white hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <ChevronLeft size={14} /> Trước
                    </button>
                    <span className="text-xs font-mono text-gray-500">
                        Trang <span className="text-white font-bold">{page}</span> / {totalPages}
                    </span>
                    <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="flex items-center gap-2 px-3 py-1.5 border border-gray-700 rounded text-gray-400 font-mono text-xs hover:text-white hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        Sau <ChevronRight size={14} />
                    </button>
                </div>
            )}
        </div>
    );
}
