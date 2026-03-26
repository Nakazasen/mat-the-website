"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
    AlertCircle,
    AlertTriangle,
    CheckCircle2,
    Globe2,
    Home,
    Languages,
    Loader2,
    Plus,
    Save,
    Trash2,
    Type,
} from "lucide-react";

import { createAdminClient } from "@/lib/supabase-admin";
import { translateAdminHomepage, type HomepageSettings } from "@/lib/api";
import { LOCALE_LABELS, SUPPORTED_LOCALES, type Locale } from "@/lib/i18n/config";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

interface Feature {
    icon: string;
    title: string;
    desc: string;
}

const DEFAULT_SETTINGS: HomepageSettings = {
    warning_title: "CẢNH BÁO KHU VỰC CẤM",
    warning_subtitle: "BIOSAFETY LEVEL 4 • RESTRICTED ACCESS",
    warning_headline: "TRẬN ĐỊA SINH TỬ",
    warning_description: "Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...",
    features_title: "ĐIỂM NỔI BẬT",
    features_json: [],
};

export default function AdminHomepagePage() {
    const router = useRouter();
    const [settings, setSettings] = useState<HomepageSettings>(DEFAULT_SETTINGS);
    const [locale, setLocale] = useState<Locale>("vi");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [translating, setTranslating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [token, setToken] = useState<string | null>(null);

    useEffect(() => {
        const bootstrap = async () => {
            const supabase = createAdminClient();
            if (!supabase) {
                setError("Thiếu cấu hình NEXT_PUBLIC_SUPABASE_URL.");
                setLoading(false);
                return;
            }

            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push("/admin/login");
                return;
            }

            setToken(session.access_token);
        };

        bootstrap();
    }, [router]);

    useEffect(() => {
        if (!token) return;

        const loadSettings = async () => {
            setLoading(true);
            setError(null);

            try {
                const params = new URLSearchParams({ locale });
                const res = await fetch(`${API_BASE_URL}/api/homepage?${params.toString()}`, { cache: "no-store" });
                if (!res.ok) {
                    throw new Error("Không thể tải cấu hình trang chủ.");
                }
                const payload = (await res.json()) as HomepageSettings;
                setSettings({
                    ...DEFAULT_SETTINGS,
                    ...payload,
                    features_json: Array.isArray(payload.features_json) ? payload.features_json : [],
                });
            } catch (eventualError: any) {
                setError(eventualError?.message || "Không thể tải cấu hình trang chủ.");
            } finally {
                setLoading(false);
            }
        };

        loadSettings();
    }, [locale, token]);

    const handleSave = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!token) return;

        setSaving(true);
        setError(null);
        setSuccess(null);

        try {
            const params = new URLSearchParams({ locale });
            const res = await fetch(`${API_BASE_URL}/api/admin/homepage?${params.toString()}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(settings),
            });

            const payload = await res.json();
            if (!res.ok) {
                throw new Error(payload.detail || "Lưu cấu hình thất bại.");
            }

            setSuccess(`Đã lưu cấu hình locale ${locale}.`);
        } catch (eventualError: any) {
            setError(eventualError?.message || "Lưu cấu hình thất bại.");
        } finally {
            setSaving(false);
        }
    };

    const handleTranslate = async () => {
        if (!token) return;

        setTranslating(true);
        setError(null);
        setSuccess(null);

        try {
            const result = await translateAdminHomepage(token);
            setSuccess(`Đã dịch: ${result.translated_locales.join(", ")}`);
            if (locale !== "vi") {
                const params = new URLSearchParams({ locale });
                const res = await fetch(`${API_BASE_URL}/api/homepage?${params.toString()}`, { cache: "no-store" });
                if (res.ok) {
                    const payload = (await res.json()) as HomepageSettings;
                    setSettings({
                        ...DEFAULT_SETTINGS,
                        ...payload,
                        features_json: Array.isArray(payload.features_json) ? payload.features_json : [],
                    });
                }
            }
        } catch (eventualError: any) {
            setError(eventualError?.message || "Dịch AI thất bại.");
        } finally {
            setTranslating(false);
        }
    };

    const updateFeature = (index: number, field: keyof Feature, value: string) => {
        const nextFeatures = [...settings.features_json];
        nextFeatures[index] = { ...nextFeatures[index], [field]: value };
        setSettings({ ...settings, features_json: nextFeatures });
    };

    const removeFeature = (index: number) => {
        setSettings({
            ...settings,
            features_json: settings.features_json.filter((_, itemIndex) => itemIndex !== index),
        });
    };

    const addFeature = () => {
        setSettings({
            ...settings,
            features_json: [
                ...settings.features_json,
                {
                    icon: "☣",
                    title: locale === "vi" ? "Tiêu đề mới" : "New title",
                    desc: locale === "vi" ? "Mô tả ngắn..." : "Short description...",
                },
            ],
        });
    };

    if (loading) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-3">
                <Loader2 className="animate-spin text-green-500" size={32} />
                <p className="font-mono text-xs uppercase tracking-widest text-gray-500">
                    Đang tải cấu hình homepage...
                </p>
            </div>
        );
    }

    return (
        <div className="max-w-5xl">
            <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                <div>
                    <h1 className="flex items-center gap-3 text-2xl tracking-tight text-gray-100 font-mono">
                        <Home className="text-green-500" size={24} />
                        CMS Trang Chủ Đa Ngôn Ngữ
                    </h1>
                    <p className="mt-1 text-sm text-gray-500 font-mono">
                        Chỉnh nội dung homepage theo từng locale và dịch AI từ bản gốc tiếng Việt.
                    </p>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                    <button
                        type="button"
                        onClick={handleTranslate}
                        disabled={!token || translating}
                        className="flex items-center gap-2 rounded-md border border-purple-700/60 px-4 py-2 text-xs font-mono text-purple-300 transition-all hover:bg-purple-500/10 hover:border-purple-500 disabled:opacity-50"
                    >
                        {translating ? <Loader2 size={14} className="animate-spin" /> : <Languages size={14} />}
                        {translating ? "ĐANG DỊCH AI..." : "DỊCH AI 3 NGÔN NGỮ"}
                    </button>
                </div>
            </div>

            <div className="mb-6 rounded-lg border border-gray-800 bg-[#0d0d0d] p-4">
                <div className="mb-3 flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-gray-500">
                    <Globe2 size={14} />
                    Locale đang chỉnh sửa
                </div>
                <div className="flex flex-wrap gap-2">
                    {SUPPORTED_LOCALES.map((item) => (
                        <button
                            key={item}
                            type="button"
                            onClick={() => {
                                setLocale(item);
                                setSuccess(null);
                                setError(null);
                            }}
                            className={`rounded-full px-3 py-1.5 text-xs font-mono tracking-widest transition-colors ${
                                item === locale
                                    ? "bg-green-500 text-black"
                                    : "border border-gray-700 text-gray-400 hover:border-green-500/40 hover:text-green-400"
                            }`}
                        >
                            {LOCALE_LABELS[item]}
                        </button>
                    ))}
                </div>
                <div className="mt-3 text-xs text-gray-500 font-mono">
                    {settings.is_fallback && locale !== "vi"
                        ? `Locale ${locale} chưa có bản dịch riêng, đang hiển thị fallback tiếng Việt.`
                        : `Đang chỉnh trực tiếp nội dung cho locale ${locale}.`}
                </div>
            </div>

            {success && (
                <div className="mb-6 flex items-center gap-2 rounded border border-green-800/50 bg-green-950/30 p-4 text-sm text-green-400">
                    <CheckCircle2 size={16} />
                    <span>{success}</span>
                </div>
            )}

            {error && (
                <div className="mb-6 flex items-center gap-2 rounded border border-red-900/50 bg-red-950/30 p-4 text-sm text-red-400">
                    <AlertTriangle size={16} />
                    <span>{error}</span>
                </div>
            )}

            <form onSubmit={handleSave} className="space-y-10">
                <div className="space-y-6">
                    <div className="flex items-center gap-3 border-b border-gray-800 pb-2">
                        <AlertCircle className="text-orange-500" size={18} />
                        <h2 className="text-lg uppercase tracking-wider text-gray-200 font-mono">
                            Warning Card
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                        <div className="space-y-2">
                            <label className="flex items-center gap-2 text-xs uppercase tracking-widest text-gray-500 font-mono">
                                <Type size={12} />
                                Dòng tiêu đề trên
                            </label>
                            <input
                                type="text"
                                value={settings.warning_title}
                                onChange={(event) => setSettings({ ...settings, warning_title: event.target.value })}
                                className="w-full rounded border border-gray-800 bg-[#0a0a0a] px-4 py-2.5 text-sm text-gray-200 outline-none transition-all focus:border-green-500"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="flex items-center gap-2 text-xs uppercase tracking-widest text-gray-500 font-mono">
                                <Type size={12} />
                                Dòng phụ
                            </label>
                            <input
                                type="text"
                                value={settings.warning_subtitle}
                                onChange={(event) => setSettings({ ...settings, warning_subtitle: event.target.value })}
                                className="w-full rounded border border-gray-800 bg-[#0a0a0a] px-4 py-2.5 text-sm text-gray-200 outline-none transition-all focus:border-green-500"
                            />
                        </div>

                        <div className="space-y-2 md:col-span-2">
                            <label className="flex items-center gap-2 text-xs uppercase tracking-widest text-gray-500 font-mono">
                                <Type size={12} />
                                Headline chính
                            </label>
                            <input
                                type="text"
                                value={settings.warning_headline}
                                onChange={(event) => setSettings({ ...settings, warning_headline: event.target.value })}
                                className="w-full rounded border border-gray-800 bg-[#0a0a0a] px-4 py-2.5 text-lg text-gray-200 outline-none transition-all focus:border-green-500"
                            />
                        </div>

                        <div className="space-y-2 md:col-span-2">
                            <label className="flex items-center gap-2 text-xs uppercase tracking-widest text-gray-500 font-mono">
                                <Type size={12} />
                                Mô tả
                            </label>
                            <textarea
                                value={settings.warning_description}
                                onChange={(event) => setSettings({ ...settings, warning_description: event.target.value })}
                                rows={5}
                                className="w-full resize-none rounded border border-gray-800 bg-[#0a0a0a] px-4 py-2.5 text-sm text-gray-200 outline-none transition-all focus:border-green-500"
                            />
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                        <div className="flex items-center gap-3">
                            <Languages className="text-green-500" size={18} />
                            <h2 className="text-lg uppercase tracking-wider text-gray-200 font-mono">
                                Highlights
                            </h2>
                        </div>
                        <button
                            type="button"
                            onClick={addFeature}
                            className="flex items-center gap-1 text-xs font-mono text-green-500 transition-colors hover:text-green-400"
                        >
                            <Plus size={14} />
                            THÊM Ô
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs uppercase tracking-widest text-gray-500 font-mono">
                                Tiêu đề section
                            </label>
                            <input
                                type="text"
                                value={settings.features_title}
                                onChange={(event) => setSettings({ ...settings, features_title: event.target.value })}
                                className="w-full max-w-sm rounded border border-gray-800 bg-[#0a0a0a] px-4 py-2 text-sm text-gray-200 outline-none transition-all focus:border-green-500"
                            />
                        </div>

                        {settings.features_json.map((feature, index) => (
                            <div
                                key={`${feature.title}-${index}`}
                                className="group relative flex items-start gap-4 rounded-lg border border-gray-800 bg-[#181818] p-4"
                            >
                                <div className="flex flex-col items-center gap-2">
                                    <label className="text-[10px] uppercase text-gray-600 font-mono">Icon</label>
                                    <input
                                        type="text"
                                        value={feature.icon}
                                        onChange={(event) => updateFeature(index, "icon", event.target.value)}
                                        className="h-12 w-12 rounded border border-gray-800 bg-[#0a0a0a] text-center text-xl outline-none transition-all focus:border-green-500"
                                    />
                                </div>

                                <div className="flex-1 space-y-3">
                                    <div className="space-y-1">
                                        <label className="text-[10px] uppercase tracking-widest text-gray-600 font-mono">
                                            Tiêu đề
                                        </label>
                                        <input
                                            type="text"
                                            value={feature.title}
                                            onChange={(event) => updateFeature(index, "title", event.target.value)}
                                            className="w-full rounded border border-gray-800 bg-[#0a0a0a] px-3 py-1.5 text-xs text-gray-200 outline-none transition-all focus:border-green-500"
                                        />
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-[10px] uppercase tracking-widest text-gray-600 font-mono">
                                            Mô tả ngắn
                                        </label>
                                        <input
                                            type="text"
                                            value={feature.desc}
                                            onChange={(event) => updateFeature(index, "desc", event.target.value)}
                                            className="w-full rounded border border-gray-800 bg-[#0a0a0a] px-3 py-1.5 text-xs text-gray-300 outline-none transition-all focus:border-green-500"
                                        />
                                    </div>
                                </div>

                                <button
                                    type="button"
                                    onClick={() => removeFeature(index)}
                                    className="p-1 text-gray-600 opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100"
                                    title="Xóa ô này"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="flex justify-end border-t border-gray-800 pt-10">
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center gap-2 rounded-md bg-green-600 px-10 py-3.5 text-sm font-bold uppercase tracking-widest text-white shadow-xl shadow-green-900/10 transition-all hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 font-mono"
                    >
                        {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
                        {saving ? "ĐANG LƯU..." : `LƯU ${LOCALE_LABELS[locale]}`}
                    </button>
                </div>
            </form>
        </div>
    );
}
