'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
    AlertTriangle,
    ArrowRight,
    CheckSquare,
    CheckSquare2,
    ChevronLeft,
    ChevronRight,
    Languages,
    Loader2,
    Pencil,
    PlusCircle,
    RefreshCw,
    Search,
    Trash2,
    Hash,
} from 'lucide-react';

import { createAdminClient } from '@/lib/supabase-admin';
import { translateAdminChapter, translateAdminChaptersBatch } from '@/lib/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-website.onrender.com';
const SAFE_BATCH_LIMIT = 2;

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
    const [translatingId, setTranslatingId] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [token, setToken] = useState<string | null>(null);

    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalChapters, setTotalChapters] = useState(0);
    const limit = 100;

    const [searchQuery, setSearchQuery] = useState('');
    const [jumpNumber, setJumpNumber] = useState('');
    const [batchStart, setBatchStart] = useState('1');
    const [batchEnd, setBatchEnd] = useState('');
    const [batchOnlyMissing, setBatchOnlyMissing] = useState(true);
    const [batchRunning, setBatchRunning] = useState(false);
    const [batchResult, setBatchResult] = useState<string | null>(null);
    const [batchFailureDetails, setBatchFailureDetails] = useState<Array<{ chapter_number: number; detail?: string }>>([]);
    const [batchBlockSize, setBatchBlockSize] = useState('2');
    const [fullBatchRunning, setFullBatchRunning] = useState(false);
    const [fullBatchProgress, setFullBatchProgress] = useState<{ completed: number; total: number; translated: number; skipped: number; failed: number } | null>(null);

    useEffect(() => {
        const supabase = createAdminClient();
        if (!supabase) {
            setError('Lỗi cấu hình: thiếu biến môi trường NEXT_PUBLIC_SUPABASE_URL.');
            setLoading(false);
            return;
        }
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session) {
                router.push('/admin/login');
                return;
            }
            setToken(session.access_token);
        });
    }, [router]);

    const fetchChapters = useCallback(async (page: number) => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE_URL}/api/chapters?page=${page}&limit=${limit}&sort=desc`, { cache: 'no-store' });
            if (!res.ok) throw new Error('Không thể tải danh sách chương');
            const data = await res.json();
            setChapters(data.chapters || []);
            setTotalPages(data.total_pages || 1);
            setTotalChapters(data.total || 0);
            setCurrentPage(page);
            setBatchEnd((current) => current || String(data.total || data.total_pages || ''));
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchChapters(1);
    }, [fetchChapters]);

    const filteredChapters = useMemo(() => {
        if (!searchQuery.trim()) return chapters;
        const query = searchQuery.toLowerCase().trim();
        return chapters.filter((chapter) =>
            chapter.title.toLowerCase().includes(query) || chapter.chapter_number.toString().includes(query),
        );
    }, [chapters, searchQuery]);

    const handleJump = (event?: React.FormEvent) => {
        event?.preventDefault();
        if (!jumpNumber) return;
        const value = parseInt(jumpNumber, 10);
        if (Number.isNaN(value) || value < 1) {
            alert('Vui lòng nhập số chương hợp lệ.');
            return;
        }
        router.push(`/admin/chapters/${value}/edit`);
    };

    const handleDelete = async (chapterNumber: number) => {
        if (!token) return;
        if (!confirm(`Xóa chương ${chapterNumber}? Hành động này không thể hoàn tác.`)) return;

        setDeletingId(chapterNumber);
        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Lỗi khi xóa chương');
            }
            await fetchChapters(currentPage);
        } catch (err: any) {
            alert(`Lỗi: ${err.message}`);
        } finally {
            setDeletingId(null);
        }
    };

    const handleTranslate = async (chapterNumber: number) => {
        if (!token) return;
        setTranslatingId(chapterNumber);
        try {
            const result = await translateAdminChapter(chapterNumber, token);
            alert(`Đã dịch chương ${chapterNumber}: ${result.translated_locales.join(', ')}`);
        } catch (err: any) {
            alert(`Lỗi dịch chương ${chapterNumber}: ${err.message}`);
        } finally {
            setTranslatingId(null);
        }
    };

    const handleBatchTranslate = async () => {
        if (!token) return;

        const startChapter = Math.max(1, parseInt(batchStart || '1', 10) || 1);
        const endChapter = Math.max(startChapter, parseInt(batchEnd || `${totalChapters || startChapter}`, 10) || startChapter);
        const selectedCount = endChapter - startChapter + 1;
        if (selectedCount > SAFE_BATCH_LIMIT) {
            setError(`Batch thủ công hiện chỉ nên chạy tối đa ${SAFE_BATCH_LIMIT} chương mỗi lượt. Hãy chia nhỏ khoảng chương.`);
            return;
        }

        setBatchRunning(true);
        setBatchResult(null);
        setBatchFailureDetails([]);
        setError(null);

        try {
            const result = await translateAdminChaptersBatch(
                {
                    start_chapter: startChapter,
                    end_chapter: endChapter,
                    only_missing: batchOnlyMissing,
                },
                token,
            );
            setBatchResult(
                `Đã xử lý ${startChapter}-${endChapter}. Dịch mới: ${result.translated_count}, bỏ qua: ${result.skipped_count}, lỗi: ${result.failed_count}.`
            );
            setBatchFailureDetails(result.failed_chapters || []);
        } catch (err: any) {
            setError(err?.message || 'Không thể batch dịch chương.');
        } finally {
            setBatchRunning(false);
        }
    };

    const handleTranslateAllMissing = async () => {
        if (!token) return;

        const total = Math.max(totalChapters, 0);
        const blockSize = Math.min(SAFE_BATCH_LIMIT, Math.max(1, parseInt(batchBlockSize || '2', 10) || 2));
        if (total === 0) {
            setError('Không có chương nào để dịch.');
            return;
        }

        setFullBatchRunning(true);
        setBatchRunning(false);
        setError(null);
        setBatchResult(null);
        setBatchFailureDetails([]);
        setFullBatchProgress({ completed: 0, total, translated: 0, skipped: 0, failed: 0 });

        let translated = 0;
        let skipped = 0;
        let failed = 0;
        let completed = 0;
        const aggregatedFailures: Array<{ chapter_number: number; detail?: string }> = [];

        try {
            for (let start = 1; start <= total; start += blockSize) {
                const end = Math.min(start + blockSize - 1, total);
                const result = await translateAdminChaptersBatch(
                    {
                        start_chapter: start,
                        end_chapter: end,
                        only_missing: true,
                    },
                    token,
                );

                translated += result.translated_count;
                skipped += result.skipped_count;
                failed += result.failed_count;
                completed = end;
                aggregatedFailures.push(...(result.failed_chapters || []));

                setFullBatchProgress({
                    completed,
                    total,
                    translated,
                    skipped,
                    failed,
                });
                setBatchResult(
                    `Đã chạy tới chương ${end}/${total}. Dịch mới: ${translated}, bỏ qua: ${skipped}, lỗi: ${failed}.`
                );
                setBatchFailureDetails([...aggregatedFailures]);
            }
        } catch (err: any) {
            setError(err?.message || 'Không thể dịch toàn bộ chương còn thiếu.');
        } finally {
            setFullBatchRunning(false);
        }
    };

    return (
        <div className="pb-10">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-xl font-mono text-gray-100 tracking-wider uppercase font-bold">Quản lý chương</h1>
                    <p className="text-xs font-mono text-gray-600 mt-1">
                        Hiển thị {chapters.length} / {totalChapters} chương, trang {currentPage}/{totalPages}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => fetchChapters(currentPage)}
                        className="flex items-center gap-1.5 px-3 py-2 border border-gray-700 text-gray-400 hover:text-gray-200 rounded font-mono text-xs transition-all active:scale-95"
                    >
                        <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                        Làm mới
                    </button>
                    <Link
                        href="/admin/chapters/new"
                        className="flex items-center gap-1.5 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded font-mono text-xs font-bold transition-all shadow-lg shadow-green-900/20 active:scale-95"
                    >
                        <PlusCircle size={14} />
                        Đăng chương mới
                    </Link>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-toxic-green-DEFAULT transition-colors" size={16} />
                    <input
                        type="text"
                        placeholder="Tìm theo tiêu đề hoặc số chương..."
                        value={searchQuery}
                        onChange={(event) => setSearchQuery(event.target.value)}
                        className="w-full bg-[#0d0d0d] border border-gray-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-toxic-green-DEFAULT/50 focus:ring-1 focus:ring-toxic-green-DEFAULT/20 transition-all font-mono"
                    />
                    {searchQuery && (
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono text-gray-600">
                            {filteredChapters.length} kết quả
                        </span>
                    )}
                </div>

                <form onSubmit={handleJump} className="relative group flex gap-2">
                    <div className="relative flex-1">
                        <Hash className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-400 transition-colors" size={16} />
                        <input
                            type="number"
                            placeholder="Nhảy đến chương số..."
                            value={jumpNumber}
                            onChange={(event) => setJumpNumber(event.target.value)}
                            className="w-full bg-[#0d0d0d] border border-gray-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all font-mono"
                        />
                    </div>
                    <button
                        type="submit"
                        className="px-4 bg-gray-800 hover:bg-gray-700 text-blue-400 border border-gray-700 hover:border-blue-500/50 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-2 whitespace-nowrap active:scale-95"
                    >
                        NHẢY <ArrowRight size={14} />
                    </button>
                </form>
            </div>

            <div className="mb-6 rounded-lg border border-gray-800 bg-[#0d0d0d] p-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
                    <div>
                        <p className="font-mono text-xs tracking-widest text-purple-300 uppercase">Batch Translate</p>
                        <p className="mt-1 text-xs text-gray-500">
                            Chạy hàng loạt theo khoảng chương. Để ổn định, batch thủ công hiện chỉ nên chạy tối đa 2 chương mỗi lượt.
                        </p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 w-full lg:w-auto">
                        <input
                            type="number"
                            min={1}
                            value={batchStart}
                            onChange={(event) => setBatchStart(event.target.value)}
                            className="bg-black border border-gray-800 rounded px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
                            placeholder="Từ chương"
                        />
                        <input
                            type="number"
                            min={1}
                            value={batchEnd}
                            onChange={(event) => setBatchEnd(event.target.value)}
                            className="bg-black border border-gray-800 rounded px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
                            placeholder="Đến chương"
                        />
                        <label className="flex items-center gap-2 rounded border border-gray-800 px-3 py-2 text-xs font-mono text-gray-300">
                            <input
                                type="checkbox"
                                checked={batchOnlyMissing}
                                onChange={(event) => setBatchOnlyMissing(event.target.checked)}
                                className="accent-purple-500"
                            />
                            Chỉ dịch chương còn thiếu
                        </label>
                        <button
                            type="button"
                            onClick={handleBatchTranslate}
                            disabled={!token || batchRunning || fullBatchRunning}
                            className="inline-flex items-center justify-center gap-2 rounded border border-purple-700/60 px-4 py-2 text-xs font-mono text-purple-300 hover:bg-purple-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {batchRunning ? <Loader2 size={14} className="animate-spin" /> : <CheckSquare size={14} />}
                            {batchRunning ? 'ĐANG CHẠY BATCH...' : 'DỊCH THEO KHOẢNG'}
                        </button>
                    </div>
                </div>
                <div className="mt-4 flex flex-col gap-3 border-t border-gray-800 pt-4 lg:flex-row lg:items-end lg:justify-between">
                    <div>
                        <p className="font-mono text-xs tracking-widest text-cyan-300 uppercase">Translate All Missing</p>
                        <p className="mt-1 text-xs text-gray-500">
                            Tự động chạy từ chương 1 đến chương {totalChapters}, chia block nhỏ để hạn chế timeout và dễ theo dõi tiến độ.
                        </p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-[140px_auto] gap-3 w-full lg:w-auto">
                        <input
                            type="number"
                            min={1}
                            value={batchBlockSize}
                            onChange={(event) => setBatchBlockSize(event.target.value)}
                            className="bg-black border border-gray-800 rounded px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
                            placeholder="Kích thước block"
                        />
                        <button
                            type="button"
                            onClick={handleTranslateAllMissing}
                            disabled={!token || fullBatchRunning || batchRunning}
                            className="inline-flex items-center justify-center gap-2 rounded border border-cyan-700/60 px-4 py-2 text-xs font-mono text-cyan-300 hover:bg-cyan-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {fullBatchRunning ? <Loader2 size={14} className="animate-spin" /> : <CheckSquare2 size={14} />}
                            {fullBatchRunning ? 'ĐANG DỊCH TOÀN BỘ...' : 'DỊCH TOÀN BỘ CHƯƠNG CHƯA DỊCH'}
                        </button>
                    </div>
                </div>
                {batchResult && (
                    <div className="mt-3 rounded border border-green-900/50 bg-green-950/30 px-3 py-2 text-sm text-green-300">
                        {batchResult}
                    </div>
                )}
                {fullBatchProgress && (
                    <div className="mt-3 rounded border border-cyan-900/50 bg-cyan-950/20 px-3 py-3 text-sm text-cyan-200">
                        <div className="font-mono text-xs uppercase tracking-widest text-cyan-300">
                            Đã xong {fullBatchProgress.completed} / {fullBatchProgress.total} chương
                        </div>
                        <div className="mt-1">
                            Dịch mới: {fullBatchProgress.translated} | Bỏ qua: {fullBatchProgress.skipped} | Lỗi: {fullBatchProgress.failed}
                        </div>
                    </div>
                )}
                {batchFailureDetails.length > 0 && (
                    <div className="mt-3 rounded border border-red-900/50 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                        <div className="font-mono text-xs uppercase tracking-widest text-red-300">
                            Chi tiết lỗi
                        </div>
                        <div className="mt-2 space-y-2">
                            {batchFailureDetails.slice(0, 12).map((item) => (
                                <div key={`${item.chapter_number}-${item.detail || 'error'}`} className="rounded border border-red-900/40 bg-black/20 px-3 py-2">
                                    <div className="font-medium">Chương {item.chapter_number}</div>
                                    <div className="mt-1 text-xs text-red-300/90 whitespace-pre-wrap break-words">
                                        {item.detail || 'Không rõ nguyên nhân lỗi.'}
                                    </div>
                                </div>
                            ))}
                            {batchFailureDetails.length > 12 && (
                                <div className="text-xs text-red-300/80">
                                    Còn {batchFailureDetails.length - 12} lỗi khác chưa hiển thị.
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-3 text-sm mb-4">
                    <AlertTriangle size={14} />
                    <span>{error}</span>
                </div>
            )}

            {loading ? (
                <div className="space-y-2">
                    {Array.from({ length: 15 }).map((_, index) => (
                        <div key={index} className="h-12 bg-[#0d0d0d] rounded animate-pulse border border-gray-800" />
                    ))}
                </div>
            ) : (
                <>
                    <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg overflow-hidden mb-6">
                        <table className="w-full text-sm">
                            <thead className="hidden md:table-header-group">
                                <tr className="border-b border-gray-800 bg-[#111111]">
                                    <th className="px-4 py-3 text-left font-mono text-xs text-gray-600 tracking-widest">#</th>
                                    <th className="px-4 py-3 text-left font-mono text-xs text-gray-600 tracking-widest">TIÊU ĐỀ</th>
                                    <th className="px-4 py-3 text-right font-mono text-xs text-gray-600 tracking-widest">TỪ</th>
                                    <th className="px-4 py-3 text-right font-mono text-xs text-gray-600 tracking-widest">HÀNH ĐỘNG</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredChapters.length > 0 ? (
                                    filteredChapters.map((chapter) => (
                                        <tr key={chapter.id} className="border-b border-gray-800/50 hover:bg-gray-800/20 transition-colors">
                                            <td className="px-4 py-3 font-mono text-xs text-green-400 whitespace-nowrap font-bold">
                                                {String(chapter.chapter_number).padStart(3, '0')}
                                            </td>
                                            <td className="px-4 py-3 text-gray-200">
                                                <div className="max-w-xs md:max-w-md truncate font-medium">{chapter.title}</div>
                                            </td>
                                            <td className="px-4 py-3 text-right font-mono text-xs text-gray-600 hidden md:table-cell">
                                                {chapter.word_count?.toLocaleString() || '—'}
                                            </td>
                                            <td className="px-4 py-3 text-right">
                                                <div className="flex items-center justify-end gap-2 flex-wrap">
                                                    <button
                                                        onClick={() => handleTranslate(chapter.chapter_number)}
                                                        disabled={!token || translatingId === chapter.chapter_number}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 border border-purple-700/60 hover:border-purple-500 text-purple-300 hover:text-purple-200 disabled:opacity-50 rounded text-xs font-mono transition-all hover:bg-purple-500/10"
                                                    >
                                                        <Languages size={10} />
                                                        {translatingId === chapter.chapter_number ? 'ĐANG DỊCH...' : 'DỊCH 3 NGÔN NGỮ'}
                                                    </button>
                                                    <Link
                                                        href={`/admin/chapters/${chapter.chapter_number}/edit`}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-700 hover:border-blue-500 text-gray-400 hover:text-blue-400 rounded text-xs font-mono transition-all hover:bg-blue-500/10"
                                                    >
                                                        <Pencil size={10} />
                                                        Sửa
                                                    </Link>
                                                    <button
                                                        onClick={() => handleDelete(chapter.chapter_number)}
                                                        disabled={deletingId === chapter.chapter_number}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-700 hover:border-red-600 text-gray-500 hover:text-red-400 disabled:opacity-50 rounded text-xs font-mono transition-all hover:bg-red-500/10"
                                                    >
                                                        <Trash2 size={10} />
                                                        {deletingId === chapter.chapter_number ? '...' : 'Xóa'}
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={4} className="px-4 py-10 text-center text-gray-600 font-mono text-xs">
                                            {searchQuery ? `Không tìm thấy chương nào khớp với "${searchQuery}"` : 'Không có dữ liệu chương'}
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>

                    {!searchQuery && totalPages > 1 && (
                        <div className="flex items-center justify-center gap-4 mt-8">
                            <button
                                onClick={() => fetchChapters(currentPage - 1)}
                                disabled={currentPage === 1 || loading}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-700 text-gray-400 hover:text-gray-100 disabled:opacity-30 disabled:hover:text-gray-400 rounded-md font-mono text-xs transition-all active:scale-95"
                            >
                                <ChevronLeft size={16} />
                                TRƯỚC
                            </button>

                            <div className="flex items-center gap-2">
                                {Array.from({ length: Math.min(5, totalPages) }).map((_, index) => {
                                    let pageNum = index + 1;
                                    if (totalPages > 5) {
                                        if (currentPage > 3) pageNum = currentPage - 3 + index;
                                        if (pageNum > totalPages) pageNum = totalPages - 4 + index;
                                        if (pageNum < 1) pageNum = index + 1;
                                    }
                                    if (pageNum > totalPages) return null;
                                    return (
                                        <button
                                            key={pageNum}
                                            onClick={() => fetchChapters(pageNum)}
                                            className={`w-8 h-8 flex items-center justify-center rounded font-mono text-xs transition-colors ${currentPage === pageNum ? 'bg-green-600 text-white' : 'text-gray-500 hover:bg-gray-800 hover:text-gray-200'}`}
                                        >
                                            {pageNum}
                                        </button>
                                    );
                                })}
                            </div>

                            <button
                                onClick={() => fetchChapters(currentPage + 1)}
                                disabled={currentPage === totalPages || loading}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-700 text-gray-400 hover:text-gray-100 disabled:opacity-30 disabled:hover:text-gray-400 rounded-md font-mono text-xs transition-all active:scale-95"
                            >
                                TIẾP
                                <ChevronRight size={16} />
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
