'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { getFreshAdminAccessToken } from '@/lib/admin-session';
import {
    getNovelSettings,
    NovelSettings,
    uploadImageR2,
    getUserRole,
    updateNovelSettings,
} from '@/lib/api';
import { Save, AlertTriangle, CheckCircle2, Loader2, BookOpen, User, FileText, Image as ImageIcon, Tag, Upload, ShieldAlert } from 'lucide-react';
import RichTextEditor from '@/components/Editor';

export default function AdminNovelPage() {
    const router = useRouter();
    const [settings, setSettings] = useState<NovelSettings>({
        title: '',
        author: '',
        description: '',
        cover_url: '',
        status: '',
        genres: [],
        donate_qr_url: '',
        total_chapters: 0,
        max_chapter: 0,
        total_views: 0,
        total_likes: 0,
    });
    const [genreInput, setGenreInput] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [token, setToken] = useState<string | null>(null);
    const [userRole, setUserRole] = useState<string>('editor');

    useEffect(() => {
        const loadData = async () => {
            const supabase = createAdminClient();
            if (!supabase) {
                setError('Lỗi cấu hình: thiếu NEXT_PUBLIC_SUPABASE_URL.');
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
                const role = await getUserRole(session.access_token);
                setUserRole(role);

                const data = await getNovelSettings();
                setSettings(data);
            } catch {
                setError('Không thể tải dữ liệu cấu hình hiện tại.');
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
            const freshToken = await getFreshAdminAccessToken();
            setToken(freshToken);

            const payload: Partial<NovelSettings> = {
                title: settings.title,
                author: settings.author,
                description: settings.description,
                status: settings.status,
                cover_url: settings.cover_url,
                genres: settings.genres,
                donate_qr_url: settings.donate_qr_url,
            };

            await updateNovelSettings(payload, freshToken);
            setSuccess(true);
            setSettings((prev) => ({
                ...prev,
                ...payload,
            }));
            setTimeout(() => setSuccess(false), 3000);
        } catch {
            setError('Lỗi lưu thông tin.');
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
        setSettings({ ...settings, genres: settings.genres.filter((g) => g !== genre) });
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
                <p className="text-gray-500 text-sm font-mono mt-1">Quản lý thông tin hiển thị trên homepage và danh sách chương.</p>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-4 text-sm mb-6">
                    <CheckCircle2 size={16} />
                    <span>Đã lưu thay đổi thành công.</span>
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
                            placeholder="Mạt Thế - Sinh Hóa Nguy Cơ"
                        />
                    </div>

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

                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <Tag size={12} /> Tình trạng
                        </label>
                        <select
                            value={settings.status}
                            onChange={(e) => setSettings({ ...settings, status: e.target.value })}
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all appearance-none"
                        >
                            <option value="Dang cap nhat">Đang cập nhật</option>
                            <option value="Hoan thanh">Hoàn thành</option>
                            <option value="Tam ngung">Tạm ngừng</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <ImageIcon size={12} /> Ảnh bìa (URL)
                        </label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={settings.cover_url}
                                onChange={(e) => setSettings({ ...settings, cover_url: e.target.value })}
                                className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
                                placeholder="/hero-bg.png"
                            />
                            <label className="flex items-center justify-center px-4 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 rounded cursor-pointer transition-colors" title="Tải ảnh lên R2">
                                <Upload size={16} />
                                <input
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    onChange={async (e) => {
                                        const file = e.target.files?.[0];
                                        if (!file || !token) return;
                                        try {
                                            const url = await uploadImageR2(file, token);
                                            setSettings((s) => ({ ...s, cover_url: url }));
                                        } catch {
                                            setError('Lỗi tải ảnh bìa. Vui lòng thử lại.');
                                        }
                                    }}
                                />
                            </label>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <ImageIcon size={12} /> QR Donate (URL)
                        </label>
                        {userRole === 'superadmin' ? (
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={settings.donate_qr_url || ''}
                                    onChange={(e) => setSettings({ ...settings, donate_qr_url: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
                                    placeholder="Link ảnh QR..."
                                />
                                <label className="flex items-center justify-center px-4 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 rounded cursor-pointer transition-colors" title="Tải QR lên R2">
                                    <Upload size={16} />
                                    <input
                                        type="file"
                                        accept="image/*"
                                        className="hidden"
                                        onChange={async (e) => {
                                            const file = e.target.files?.[0];
                                            if (!file || !token) return;
                                            try {
                                                const url = await uploadImageR2(file, token);
                                                setSettings((s) => ({ ...s, donate_qr_url: url }));
                                            } catch {
                                                setError('Lỗi tải ảnh QR. Vui lòng thử lại.');
                                            }
                                        }}
                                    />
                                </label>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-500 text-sm italic">
                                <ShieldAlert size={14} className="text-amber-500" />
                                <span>Chỉ superadmin được xem và chỉnh sửa QR Donate.</span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">Thể loại</label>
                    <div className="flex flex-wrap gap-2 mb-2 min-h-[32px]">
                        {settings.genres.map((genre) => (
                            <span
                                key={genre}
                                className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-900/20 text-green-400 border border-green-800/30 rounded text-xs font-mono"
                            >
                                {genre}
                                <button type="button" onClick={() => removeGenre(genre)} className="hover:text-red-400 transition-colors">x</button>
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

                <div className="space-y-2">
                    <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">Giới thiệu truyện</label>
                    <RichTextEditor
                        content={settings.description}
                        onChange={(html) => setSettings({ ...settings, description: html })}
                        placeholder="Nhập giới thiệu truyện..."
                        adminToken={token || undefined}
                    />
                </div>

                <div className="flex justify-end pt-4">
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center gap-2 px-8 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-mono text-sm tracking-widest rounded transition-all"
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
