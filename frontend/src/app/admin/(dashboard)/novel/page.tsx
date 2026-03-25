'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { getNovelSettings, NovelSettings, uploadImageR2, getUserRole, updateNovelSettings } from '@/lib/api';
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
        ai_model_name: 'gemini-3.1-flash-lite-preview',
        has_ai_key: false,
    });
    const [genreInput, setGenreInput] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [token, setToken] = useState<string | null>(null);
    const [userRole, setUserRole] = useState<string>('editor');
    const [aiModelName, setAiModelName] = useState('gemini-3.1-flash-lite-preview');
    const [aiApiKeyInput, setAiApiKeyInput] = useState('');

    useEffect(() => {
        const loadData = async () => {
            const supabase = createAdminClient();
            if (!supabase) {
                setError('Loi cau hinh: thieu NEXT_PUBLIC_SUPABASE_URL.');
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
                setAiModelName(data.ai_model_name || 'gemini-3.1-flash-lite-preview');
            } catch {
                setError('Khong the tai du lieu cau hinh hien tai.');
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
            const payload: Partial<NovelSettings> & { ai_api_key?: string } = {
                title: settings.title,
                author: settings.author,
                description: settings.description,
                status: settings.status,
                cover_url: settings.cover_url,
                genres: settings.genres,
                donate_qr_url: settings.donate_qr_url,
            };

            if (userRole === 'superadmin') {
                payload.ai_model_name = aiModelName.trim() || 'gemini-3.1-flash-lite-preview';
                if (aiApiKeyInput.trim()) {
                    payload.ai_api_key = aiApiKeyInput.trim();
                }
            }

            await updateNovelSettings(payload, token);
            setSuccess(true);
            setAiApiKeyInput('');
            setSettings((prev) => ({
                ...prev,
                has_ai_key: prev.has_ai_key || Boolean(payload.ai_api_key),
                ai_model_name: payload.ai_model_name || prev.ai_model_name,
            }));
            setTimeout(() => setSuccess(false), 3000);
        } catch (err: any) {
            setError(err?.message || 'Loi khong xac dinh khi luu cau hinh.');
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
                <p className="font-mono text-xs text-gray-500 tracking-widest">DANG TAI CAU HINH...</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl">
            <div className="mb-8">
                <h1 className="text-2xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
                    <BookOpen className="text-green-500" size={24} />
                    THONG TIN TRUYEN
                </h1>
                <p className="text-gray-500 text-sm font-mono mt-1">Quan ly thong tin hien thi tren homepage va danh sach chuong.</p>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-4 text-sm mb-6">
                    <CheckCircle2 size={16} />
                    <span>Da luu thay doi thanh cong.</span>
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
                            <FileText size={12} /> Ten truyen
                        </label>
                        <input
                            type="text"
                            value={settings.title}
                            onChange={(e) => setSettings({ ...settings, title: e.target.value })}
                            required
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
                            placeholder="Mat The - Sinh Hoa Nguy Co"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <User size={12} /> Tac gia
                        </label>
                        <input
                            type="text"
                            value={settings.author}
                            onChange={(e) => setSettings({ ...settings, author: e.target.value })}
                            required
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
                            placeholder="Ho Phong"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <Tag size={12} /> Tinh trang
                        </label>
                        <select
                            value={settings.status}
                            onChange={(e) => setSettings({ ...settings, status: e.target.value })}
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all appearance-none"
                        >
                            <option value="Dang cap nhat">Dang cap nhat</option>
                            <option value="Hoan thanh">Hoan thanh</option>
                            <option value="Tam ngung">Tam ngung</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">
                            <ImageIcon size={12} /> Anh bia (URL)
                        </label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={settings.cover_url}
                                onChange={(e) => setSettings({ ...settings, cover_url: e.target.value })}
                                className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
                                placeholder="/hero-bg.png"
                            />
                            <label className="flex items-center justify-center px-4 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 rounded cursor-pointer transition-colors" title="Tai anh len R2">
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
                                            setError('Loi tai anh bia. Vui long thu lai.');
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
                                    placeholder="Link anh QR..."
                                />
                                <label className="flex items-center justify-center px-4 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 rounded cursor-pointer transition-colors" title="Tai QR len R2">
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
                                                setError('Loi tai anh QR. Vui long thu lai.');
                                            }
                                        }}
                                    />
                                </label>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-500 text-sm italic">
                                <ShieldAlert size={14} className="text-amber-500" />
                                <span>Chi superadmin duoc xem va chinh sua QR Donate.</span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">The loai</label>
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
                            placeholder="Them the loai va nhan Enter..."
                        />
                        <button
                            type="button"
                            onClick={addGenre}
                            className="px-4 py-2 border border-gray-700 text-gray-400 hover:text-gray-200 rounded text-sm font-mono transition-colors"
                        >
                            THEM
                        </button>
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="flex items-center gap-2 text-xs font-mono text-gray-500 tracking-widest uppercase">Gioi thieu truyen</label>
                    <RichTextEditor
                        content={settings.description}
                        onChange={(html) => setSettings({ ...settings, description: html })}
                        placeholder="Nhap gioi thieu truyen..."
                        adminToken={token || undefined}
                    />
                </div>

                <div className="rounded border border-gray-800 bg-[#0a0a0a] p-4 space-y-3">
                    <p className="text-xs font-mono tracking-widest text-gray-400">AI COMMAND</p>
                    {userRole === 'superadmin' ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-[11px] font-mono text-gray-500 uppercase tracking-widest">Model Name</label>
                                <input
                                    type="text"
                                    value={aiModelName}
                                    onChange={(e) => setAiModelName(e.target.value)}
                                    className="w-full bg-black border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500"
                                    placeholder="gemini-3.1-flash-lite-preview"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[11px] font-mono text-gray-500 uppercase tracking-widest">
                                    API Key {settings.has_ai_key ? '(configured)' : '(not set)'}
                                </label>
                                <input
                                    type="password"
                                    value={aiApiKeyInput}
                                    onChange={(e) => setAiApiKeyInput(e.target.value)}
                                    className="w-full bg-black border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500"
                                    placeholder="Nhap API key moi de ghi de"
                                />
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-center gap-2 text-sm text-gray-500 italic">
                            <ShieldAlert size={14} className="text-amber-500" />
                            <span>Chi superadmin duoc thay doi AI model va API key.</span>
                        </div>
                    )}
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
                                DANG LUU...
                            </>
                        ) : (
                            <>
                                <Save size={16} />
                                LUU CAU HINH
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
