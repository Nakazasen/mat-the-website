'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { getNovelSettings, NovelSettings } from '@/lib/api';
import { Save, AlertTriangle, CheckCircle2, Loader2, BookOpen, User, FileText, Image as ImageIcon, Tag } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-api.onrender.com';

export default function AdminNovelPage() {
    const router = useRouter();
    const [settings, setSettings] = useState<NovelSettings>({
        title: '',
        author: '',
        description: '',
        cover_url: '',
        status: '',
        genres: []
    });
    const [genreInput, setGenreInput] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [token, setToken] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            const supabase = createAdminClient();
            if (!supabase) {
                setError('Lỗi cấu hình: Thiếu NEXT_PUBLIC_SUPABASE_URL.');
                setLoading(false);
                return;
            }

            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push('/admin/login');
                return;
            }
            setToken(session.access_token);

            try {
                const data = await getNovelSettings();
                setSettings(data);
            } catch (err: any) {
                console.warn("Could not load settings, using defaults.", err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [router]);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;
        setSaving(true);
        setError(null);
        setSuccess(false);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/novel`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(settings),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Lỗi không xác định');

            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    };

    const addGenre = () => {
        const val = genreInput.trim();
        if (val && !settings.genres.includes(val)) {
            setSettings({ ...settings, genres: [...settings.genres, val] });
            setGenreInput('');
        }
    };

    const removeGenre = (genre: string) => {
        setSettings({ ...settings, genres: settings.genres.filter(g => g !== genre) });
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 gap-3">
                <Loader2 className="animate-spin text-green-500" size={32} />
                <p className="font-mono text-xs text-gray-500 tracking-widest">ĐANG TẢI CẤU HÌNH...</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl">
            <div className="mb-8">
                <h1 className="text-2xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
                    <BookOpen className="text-green-500" size={24} />
                    THÔNG TIN TRUYỆN
                </h1>
                <p className="text-gray-500 text-sm font-mono mt-1">Quản lý các thông tin hiển thị trên trang chủ và mục lục.</p>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-4 text-sm mb-6 animate-in fade-in slide-in-from-top-2">
                    <CheckCircle2 size={16} />
                    <span>Đã lưu tất cả thay đổi thành công!</span>
                </div>
            )}

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-4 text-sm mb-6">
                    <AlertTriangle size={16} />
                    <span>{error}</span>
                </div>
            )}

            <form onSubmit={handleSave} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Title */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <FileText size={12} /> Tên truyện
                        </label>
                        <input
                            type="text"
                            value={settings.title}
                            onChange={(e) => setSettings({ ...settings, title: e.target.value })}
                            required
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
                            placeholder="Ví dụ: Mạt Thế - Sinh Hoá Nguy Cơ"
                        />
                        <p className="text-[10px] text-gray-600 font-mono italic">Mẹo: Dùng dấu gạch ngang '-' để tách tiêu đề to và nhỏ (ví dụ: Mạt Thế - Sinh Hoá Nguy Cơ)</p>
                    </div>

                    {/* Author */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <User size={12} /> Tác giả
                        </label>
                        <input
                            type="text"
                            value={settings.author}
                            onChange={(e) => setSettings({ ...settings, author: e.target.value })}
                            required
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
                            placeholder="Hà Phong"
                        />
                    </div>

                    {/* Status */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <Tag size={12} /> Tình trạng
                        </label>
                        <select
                            value={settings.status}
                            onChange={(e) => setSettings({ ...settings, status: e.target.value })}
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all appearance-none"
                        >
                            <option value="Đang cập nhật">Đang cập nhật</option>
                            <option value="Hoàn thành">Hoàn thành</option>
                            <option value="Tạm ngưng">Tạm ngưng</option>
                        </select>
                    </div>

                    {/* Cover URL */}
                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <ImageIcon size={12} /> Ảnh bìa (URL)
                        </label>
                        <input
                            type="text"
                            value={settings.cover_url}
                            onChange={(e) => setSettings({ ...settings, cover_url: e.target.value })}
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
                            placeholder="/hero-bg.png"
                        />
                    </div>
                </div>

                {/* Genres */}
                <div className="space-y-2">
                    <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                        Thể loại
                    </label>
                    <div className="flex flex-wrap gap-2 mb-2 min-h-[32px]">
                        {settings.genres.map((genre) => (
                            <span
                                key={genre}
                                className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-900/20 text-green-400 border border-green-800/30 rounded text-xs font-mono group"
                            >
                                {genre}
                                <button
                                    type="button"
                                    onClick={() => removeGenre(genre)}
                                    className="hover:text-red-400 transition-colors"
                                >
                                    ×
                                </button>
                            </span>
                        ))}
                    </div>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={genreInput}
                            onChange={(e) => setGenreInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addGenre())}
                            className="flex-1 bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-all font-mono"
                            placeholder="Thêm thể loại và nhấn Enter..."
                        />
                        <button
                            type="button"
                            onClick={addGenre}
                            className="px-4 py-2 border border-gray-700 text-gray-400 hover:text-gray-200 rounded text-sm font-mono transition-colors"
                        >
                            THÊM
                        </button>
                    </div>
                </div>

                {/* Description */}
                <div className="space-y-2">
                    <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                        Giới thiệu truyện
                    </label>
                    <textarea
                        value={settings.description}
                        onChange={(e) => setSettings({ ...settings, description: e.target.value })}
                        required
                        rows={6}
                        className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-3 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all font-reading leading-relaxed resize-none"
                        placeholder="Nhập giới thiệu truyện..."
                    />
                </div>

                {/* Submit */}
                <div className="flex justify-end pt-4">
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center gap-2 px-8 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-mono text-sm tracking-widest rounded transition-all shadow-lg shadow-green-900/10"
                    >
                        {saving ? (
                            <>
                                <Loader2 className="animate-spin" size={16} />
                                ĐANG LƯU...
                            </>
                        ) : (
                            <>
                                <Save size={16} />
                                LƯU CẤU HÌNH
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
