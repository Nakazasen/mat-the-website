'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { Save, AlertTriangle, CheckCircle2, Loader2, Home, Type, AlertCircle, List, Trash2, Plus } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface Feature {
    icon: string;
    title: string;
    desc: string;
}

interface HomepageSettings {
    warning_title: string;
    warning_subtitle: string;
    warning_headline: string;
    warning_description: string;
    features_title: string;
    features_json: Feature[];
}

export default function AdminHomepagePage() {
    const router = useRouter();
    const [settings, setSettings] = useState<HomepageSettings>({
        warning_title: 'CẢNH BÁO KHU VỰC CẤM',
        warning_subtitle: 'BIOSAFETY LEVEL 4 · RESTRICTED ACCESS',
        warning_headline: 'TRẬN ĐỊA SINH TỬ',
        warning_description: 'Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...',
        features_title: 'ĐIỂM NỔI BẬT',
        features_json: []
    });
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
                const res = await fetch(`${API_BASE_URL}/api/homepage`);
                if (res.ok) {
                    const data = await res.json();
                    setSettings(data);
                }
            } catch (err: any) {
                console.warn("Could not load homepage settings, using defaults.", err);
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
            const res = await fetch(`${API_BASE_URL}/api/admin/homepage`, {
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

    const updateFeature = (index: number, field: keyof Feature, value: string) => {
        const newFeatures = [...settings.features_json];
        newFeatures[index] = { ...newFeatures[index], [field]: value };
        setSettings({ ...settings, features_json: newFeatures });
    };

    const removeFeature = (index: number) => {
        const newFeatures = settings.features_json.filter((_, i) => i !== index);
        setSettings({ ...settings, features_json: newFeatures });
    };

    const addFeature = () => {
        setSettings({
            ...settings,
            features_json: [...settings.features_json, { icon: '☣️', title: 'Tiêu đề mới', desc: 'Mô tả ngắn...' }]
        });
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 gap-3">
                <Loader2 className="animate-spin text-green-500" size={32} />
                <p className="font-mono text-xs text-gray-500 tracking-widest uppercase">Đang tải cấu hình trang chủ...</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl">
            <div className="mb-8">
                <h1 className="text-2xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
                    <Home className="text-green-500" size={24} />
                    CẤU HÌNH TRANG CHỦ
                </h1>
                <p className="text-gray-500 text-sm font-mono mt-1">Tùy biến các nội dung văn bản hiển thị trên trang chủ độc giả.</p>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-4 text-sm mb-6 animate-in fade-in slide-in-from-top-2">
                    <CheckCircle2 size={16} />
                    <span>Đã cập nhật nội dung trang chủ thành công!</span>
                </div>
            )}

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-4 text-sm mb-6">
                    <AlertTriangle size={16} />
                    <span>{error}</span>
                </div>
            )}

            <form onSubmit={handleSave} className="space-y-10">
                {/* SECTION: WARNING CARD */}
                <div className="space-y-6">
                    <div className="flex items-center gap-3 border-b border-gray-800 pb-2">
                        <AlertCircle className="text-orange-500" size={18} />
                        <h2 className="text-lg font-mono text-gray-200 uppercase tracking-wider">Khu vực Cảnh báo (Warning Card)</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-xs font-mono text-gray-500 tracking-widest uppercase flex items-center gap-2">
                                <Type size={12} /> Tiêu đề nhỏ (Top)
                            </label>
                            <input
                                type="text"
                                value={settings.warning_title}
                                onChange={(e) => setSettings({ ...settings, warning_title: e.target.value })}
                                className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                placeholder="CẢNH BÁO KHU VỰC CẤM"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-mono text-gray-500 tracking-widest uppercase flex items-center gap-2">
                                <Type size={12} /> Phụ đề nhỏ (Bottom Top)
                            </label>
                            <input
                                type="text"
                                value={settings.warning_subtitle}
                                onChange={(e) => setSettings({ ...settings, warning_subtitle: e.target.value })}
                                className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                placeholder="BIOSAFETY LEVEL 4 · RESTRICTED ACCESS"
                            />
                        </div>

                        <div className="md:col-span-2 space-y-2">
                            <label className="text-xs font-mono text-gray-500 tracking-widest uppercase flex items-center gap-2">
                                <Type size={12} /> Tiêu đề chính (Headline)
                            </label>
                            <input
                                type="text"
                                value={settings.warning_headline}
                                onChange={(e) => setSettings({ ...settings, warning_headline: e.target.value })}
                                className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-lg font-bold focus:border-green-500 outline-none transition-all"
                                placeholder="TRẬN ĐỊA SINH TỬ"
                            />
                        </div>

                        <div className="md:col-span-2 space-y-2">
                            <label className="text-xs font-mono text-gray-500 tracking-widest uppercase flex items-center gap-2">
                                <Type size={12} /> Mô tả tóm tắt
                            </label>
                            <textarea
                                value={settings.warning_description}
                                onChange={(e) => setSettings({ ...settings, warning_description: e.target.value })}
                                rows={4}
                                className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:border-green-500 outline-none transition-all resize-none"
                                placeholder="Nhập tóm tắt bối cảnh..."
                            />
                        </div>
                    </div>
                </div>

                {/* SECTION: HIGHLIGHTS */}
                <div className="space-y-6">
                    <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                        <div className="flex items-center gap-3">
                            <List className="text-green-500" size={18} />
                            <h2 className="text-lg font-mono text-gray-200 uppercase tracking-wider">Điểm Nổi Bật (Highlights)</h2>
                        </div>
                        <button
                            type="button"
                            onClick={addFeature}
                            className="text-xs font-mono text-green-500 hover:text-green-400 flex items-center gap-1 transition-colors"
                        >
                            <Plus size={14} /> THÊM MỚI
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div className="grid grid-cols-1 gap-4">
                            <div className="space-y-2 mb-4">
                                <label className="text-xs font-mono text-gray-500 tracking-widest uppercase">Tiêu đề khu vực (Feature Title)</label>
                                <input
                                    type="text"
                                    value={settings.features_title}
                                    onChange={(e) => setSettings({ ...settings, features_title: e.target.value })}
                                    className="w-full max-w-xs bg-[#0a0a0a] border border-gray-800 rounded px-4 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                    placeholder="ĐIỂM NỔI BẬT"
                                />
                            </div>

                            {settings.features_json.map((feature, idx) => (
                                <div key={idx} className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex gap-4 items-start group relative">
                                    <div className="flex flex-col gap-2 items-center">
                                        <label className="text-[10px] font-mono text-gray-600 uppercase">Icon</label>
                                        <input
                                            type="text"
                                            value={feature.icon}
                                            onChange={(e) => updateFeature(idx, 'icon', e.target.value)}
                                            className="w-12 h-12 bg-[#0a0a0a] border border-gray-800 rounded text-center text-xl focus:border-green-500 outline-none transition-all"
                                            placeholder="🧟"
                                        />
                                    </div>
                                    <div className="flex-1 space-y-3">
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">Tiêu đề</label>
                                            <input
                                                type="text"
                                                value={feature.title}
                                                onChange={(e) => updateFeature(idx, 'title', e.target.value)}
                                                className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-1.5 text-gray-200 text-xs focus:border-green-500 outline-none"
                                            />
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">Mô tả ngắn</label>
                                            <input
                                                type="text"
                                                value={feature.desc}
                                                onChange={(e) => updateFeature(idx, 'desc', e.target.value)}
                                                className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-1.5 text-gray-400 text-xs focus:border-green-500 outline-none"
                                            />
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => removeFeature(idx)}
                                        className="text-gray-600 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                        title="Xóa điểm này"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* SUBMIT */}
                <div className="flex justify-end pt-10 border-t border-gray-800">
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center gap-2 px-10 py-3.5 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-mono text-sm tracking-widest rounded-md transition-all shadow-xl shadow-green-900/10 active:scale-95 uppercase font-bold"
                    >
                        {saving ? (
                            <>
                                <Loader2 className="animate-spin" size={18} />
                                Đang lưu hệ thống...
                            </>
                        ) : (
                            <>
                                <Save size={18} />
                                Cập nhật Trang Chủ
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
