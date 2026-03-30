'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { createAdminClient } from '@/lib/supabase-admin';
import { ArrowLeft, Save, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { uploadAudioR2 } from '@/lib/api';
import RichTextEditor from '@/components/Editor';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function NewChapterPage() {
    const router = useRouter();
    const [chapterNumber, setChapterNumber] = useState('');
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [isSideStory, setIsSideStory] = useState(false);
    const [bgmUrl, setBgmUrl] = useState('');
    const [bgmTitle, setBgmTitle] = useState('');
    const [uploadingBgm, setUploadingBgm] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [token, setToken] = useState<string | null>(null);

    useEffect(() => {
        const loadSession = async () => {
            const supabase = createAdminClient();
            if (!supabase) return;
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;
            setToken(session.access_token);
        };
        loadSession();
    }, []);

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
                    bgm_url: bgmUrl.trim() || null,
                    bgm_title: bgmTitle.trim() || null,
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

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">BGM URL</label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={bgmUrl}
                                onChange={(e) => setBgmUrl(e.target.value)}
                                className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                                placeholder="/media/chapter-bgm.mp3 hoặc https://..."
                            />
                            <label className={`inline-flex shrink-0 cursor-pointer items-center justify-center rounded border border-gray-700 px-3 py-2 text-xs font-mono text-gray-300 transition-colors hover:border-green-500 hover:text-white ${uploadingBgm ? "pointer-events-none opacity-50" : ""}`}>
                                {uploadingBgm ? 'ĐANG TẢI...' : 'UPLOAD'}
                                <input
                                    type="file"
                                    accept="audio/mpeg,audio/mp3,audio/wav,audio/x-wav,audio/ogg,audio/webm,audio/mp4,audio/x-m4a,audio/aac,.mp3,.wav,.ogg,.webm,.m4a,.aac"
                                    className="hidden"
                                    onChange={async (e) => {
                                        const file = e.target.files?.[0];
                                        if (!file || !token) return;
                                        try {
                                            setUploadingBgm(true);
                                            const url = await uploadAudioR2(file, token);
                                            setBgmUrl(url);
                                            if (!bgmTitle.trim()) {
                                                const fallbackTitle = file.name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").trim();
                                                setBgmTitle(fallbackTitle);
                                            }
                                            setSuccess(false);
                                        } catch (err: any) {
                                            setError(err.message || 'Lỗi tải audio BGM');
                                        } finally {
                                            setUploadingBgm(false);
                                            e.target.value = '';
                                        }
                                    }}
                                />
                            </label>
                        </div>
                        <p className="mt-1 text-[11px] text-gray-500">Dùng URL public. Đường dẫn local Windows sẽ không phát được trên web.</p>
                    </div>
                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">BGM TITLE</label>
                        <input
                            type="text"
                            value={bgmTitle}
                            onChange={(e) => setBgmTitle(e.target.value)}
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                            placeholder="Dark Cello / Ambient Tension"
                        />
                    </div>
                </div>

                {bgmUrl.trim() && (
                    <div className="rounded-lg border border-gray-800 bg-[#0b0b0b] p-4 space-y-3">
                        <div className="flex items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-mono tracking-[0.28em] text-gray-500">BGM PREVIEW</p>
                                <p className="mt-1 text-sm text-gray-200">{bgmTitle.trim() || 'Chưa đặt tiêu đề BGM'}</p>
                            </div>
                            <div className="flex items-center gap-3">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setBgmUrl('');
                                        setBgmTitle('');
                                        setSuccess(false);
                                        setError(null);
                                    }}
                                    className="text-[11px] font-mono tracking-[0.2em] text-red-400 transition-colors hover:text-red-300"
                                >
                                    XÓA BGM
                                </button>
                                <a
                                    href={bgmUrl}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-[11px] font-mono tracking-[0.2em] text-gray-400 transition-colors hover:text-white"
                                >
                                    MỞ FILE
                                </a>
                            </div>
                        </div>
                        <audio
                            key={bgmUrl}
                            controls
                            preload="none"
                            src={bgmUrl}
                            className="w-full h-11 rounded-md"
                        >
                            Trình duyệt không hỗ trợ phát audio preview.
                        </audio>
                    </div>
                )}

                <div>
                    <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">
                        NỘI DUNG * ({content.trim().split(/\s+/).filter(Boolean).length} từ)
                    </label>
                    <RichTextEditor
                        content={content}
                        onChange={(html) => setContent(html)}
                        placeholder="Bắt đầu viết chương mới ở đây..."
                        adminToken={token || undefined}
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
