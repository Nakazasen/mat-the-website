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
    runAdminAiPlayground,
    AdminAiPlaygroundResult,
    getAdminOracleHealth,
    OracleHealthStatus,
    resetAdminOracleRateLimit,
} from '@/lib/api';
import { Save, AlertTriangle, CheckCircle2, Loader2, BookOpen, User, FileText, Image as ImageIcon, Tag, Upload, ShieldAlert, Bot, FlaskConical, Plus, Play, Wand2, ChevronLeft, ChevronRight, Trash2 } from 'lucide-react';
import RichTextEditor from '@/components/Editor';

const DEFAULT_AI_MODEL = 'gemini-3-flash-preview';
const DEFAULT_AI_MODELS = [
    'gemini-3.1-flash-lite-preview',
    'gemma-3n-1b-it',
    'gemma-3n-e2b-it',
    'gemma-3-4b-it',
    'gemma-3-12b-it',
    'gemma-3-27b-it',
    'gemini-robotics-er-1.5-preview',
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
];
type ApiKeyRow = {
    id: string;
    kind: 'existing' | 'new';
    value: string;
    originalIndex?: number;
};

function buildApiKeyRows(savedCount: number): ApiKeyRow[] {
    const rows: ApiKeyRow[] = Array.from({ length: savedCount }, (_, index) => ({
        id: `existing-${index}`,
        kind: 'existing',
        value: '',
        originalIndex: index,
    }));
    rows.push({
        id: `new-${Date.now()}`,
        kind: 'new',
        value: '',
    });
    return rows;
}

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
        ai_model_name: DEFAULT_AI_MODEL,
        has_ai_key: false,
    });
    const [genreInput, setGenreInput] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [token, setToken] = useState<string | null>(null);
    const [userRole, setUserRole] = useState<string>('editor');
    const [aiModelName, setAiModelName] = useState(DEFAULT_AI_MODEL);
    const [aiApiKeyRows, setAiApiKeyRows] = useState<ApiKeyRow[]>(buildApiKeyRows(0));
    const [customModelInput, setCustomModelInput] = useState('');
    const [modelCatalog, setModelCatalog] = useState<string[]>(DEFAULT_AI_MODELS);
    const [playgroundPrompt, setPlaygroundPrompt] = useState('Tra loi ngan gon bang tieng Viet: xac nhan model dang hoat dong va san sang phan hoi.');
    const [playgroundChapter, setPlaygroundChapter] = useState(1);
    const [playgroundApiKey, setPlaygroundApiKey] = useState('');
    const [playgroundResults, setPlaygroundResults] = useState<AdminAiPlaygroundResult[]>([]);
    const [playgroundRunning, setPlaygroundRunning] = useState(false);
    const [playgroundError, setPlaygroundError] = useState<string | null>(null);
    const [oracleHealth, setOracleHealth] = useState<OracleHealthStatus | null>(null);
    const [oracleHealthLoading, setOracleHealthLoading] = useState(false);
    const [oracleResetLoading, setOracleResetLoading] = useState(false);
    const [oracleAdminMessage, setOracleAdminMessage] = useState<string | null>(null);

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
                setAiModelName(data.ai_model_name || DEFAULT_AI_MODEL);
                setModelCatalog(Array.from(new Set([...(data.ai_model_catalog || []), ...DEFAULT_AI_MODELS])));
                setPlaygroundChapter(Math.max(data.max_chapter || 1, 1));
                setAiApiKeyRows(buildApiKeyRows(data.ai_api_keys_count || 0));
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

            const payload: Partial<NovelSettings> & {
                ai_api_key?: string;
                ai_api_keys?: string[];
                append_ai_api_keys?: string[];
                remove_ai_key_indexes?: number[];
            } = {
                title: settings.title,
                author: settings.author,
                description: settings.description,
                status: settings.status,
                cover_url: settings.cover_url,
                genres: settings.genres,
                donate_qr_url: settings.donate_qr_url,
            };

            if (userRole === 'superadmin') {
                payload.ai_model_name = aiModelName.trim() || DEFAULT_AI_MODEL;
                payload.ai_model_catalog = Array.from(new Set(modelCatalog.map((model) => model.trim()).filter(Boolean)));
                const newKeys = aiApiKeyRows
                    .filter((row) => row.kind === 'new')
                    .map((row) => row.value.trim())
                    .filter(Boolean);
                const keptExistingIndexes = aiApiKeyRows
                    .filter((row) => row.kind === 'existing')
                    .map((row) => row.originalIndex)
                    .filter((index): index is number => typeof index === 'number');
                const removedExistingIndexes = Array.from(
                    { length: settings.ai_api_keys_count || 0 },
                    (_, index) => index,
                ).filter((index) => !keptExistingIndexes.includes(index));

                if (newKeys.length > 0) {
                    payload.append_ai_api_keys = newKeys;
                }
                if (removedExistingIndexes.length > 0) {
                    payload.remove_ai_key_indexes = removedExistingIndexes;
                }
            }

            const response = await updateNovelSettings(payload, freshToken);
            const nextKeyCount = response.data.ai_api_keys_count ?? settings.ai_api_keys_count ?? 0;
            setSuccess(true);
            setAiApiKeyRows(buildApiKeyRows(nextKeyCount));
            setSettings((prev) => ({
                ...prev,
                has_ai_key: response.data.has_ai_key ?? prev.has_ai_key,
                ai_api_keys_count: nextKeyCount,
                ai_model_name: response.data.ai_model_name || prev.ai_model_name,
                ai_model_catalog: response.data.ai_model_catalog || prev.ai_model_catalog,
            }));
            setTimeout(() => setSuccess(false), 3000);
        } catch (err: any) {
            setError(err?.message || 'Lỗi không xác định khi lưu cấu hình.');
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

    const addModelToCatalog = () => {
        const nextModel = customModelInput.trim();
        if (!nextModel) return;
        setModelCatalog((current) => Array.from(new Set([...current, nextModel])));
        setAiModelName(nextModel);
        setCustomModelInput('');
    };

    const removeModelFromCatalog = (model: string) => {
        setModelCatalog((current) => current.filter((item) => item !== model));
        if (aiModelName === model) {
            const fallbackModel = modelCatalog.find((item) => item !== model) || DEFAULT_AI_MODEL;
            setAiModelName(fallbackModel);
        }
    };

    const moveModel = (index: number, direction: 'left' | 'right') => {
        setModelCatalog((current) => {
            const next = [...current];
            const targetIndex = direction === 'left' ? index - 1 : index + 1;
            if (targetIndex < 0 || targetIndex >= next.length) {
                return current;
            }

            const currentValue = next[index];
            next[index] = next[targetIndex];
            next[targetIndex] = currentValue;
            return next;
        });
    };

    const addApiKeyRow = () => {
        setAiApiKeyRows((current) => ([
            ...current,
            {
                id: `new-${Date.now()}-${current.length}`,
                kind: 'new',
                value: '',
            },
        ]));
    };

    const updateApiKeyRowValue = (id: string, value: string) => {
        setAiApiKeyRows((current) => current.map((row) => (row.id === id ? { ...row, value } : row)));
    };

    const removeApiKeyRow = (id: string) => {
        setAiApiKeyRows((current) => {
            const next = current.filter((row) => row.id !== id);
            return next.length > 0 ? next : buildApiKeyRows(0);
        });
    };

    const runPlayground = async (models: string[]) => {
        if (!token) return;
        const dedupedModels = Array.from(new Set(models.map((model) => model.trim()).filter(Boolean)));
        if (dedupedModels.length === 0) {
            setPlaygroundError('Chọn ít nhất một model để test.');
            return;
        }

        setPlaygroundRunning(true);
        setPlaygroundError(null);

        try {
            const freshToken = await getFreshAdminAccessToken();
            setToken(freshToken);
            const response = await runAdminAiPlayground({
                models: dedupedModels,
                prompt: playgroundPrompt,
                chapter_progress: playgroundChapter,
                api_key: playgroundApiKey.trim() || undefined,
            }, freshToken);
            setPlaygroundResults(response.results);
        } catch (err: any) {
            setPlaygroundError(err?.message || 'Không thể chạy AI playground.');
        } finally {
            setPlaygroundRunning(false);
        }
    };

    const checkOracleHealth = async () => {
        if (!token) return;
        setOracleHealthLoading(true);
        setOracleAdminMessage(null);
        try {
            const freshToken = await getFreshAdminAccessToken();
            setToken(freshToken);
            const response = await getAdminOracleHealth(freshToken);
            setOracleHealth(response);
        } catch (err: any) {
            setOracleAdminMessage(err?.message || 'Không thể kiểm tra Oracle health.');
        } finally {
            setOracleHealthLoading(false);
        }
    };

    const resetOracleRateLimit = async () => {
        if (!token) return;
        setOracleResetLoading(true);
        setOracleAdminMessage(null);
        try {
            const freshToken = await getFreshAdminAccessToken();
            setToken(freshToken);
            const response = await resetAdminOracleRateLimit(freshToken);
            setOracleAdminMessage(`${response.detail} Deleted rows: ${response.deleted_rows}.`);
        } catch (err: any) {
            setOracleAdminMessage(err?.message || 'Không thể reset Oracle rate limit.');
        } finally {
            setOracleResetLoading(false);
        }
    };

    const getStatusTone = (status: string) => {
        if (status === 'success') return 'border-emerald-800/50 bg-emerald-950/20 text-emerald-300';
        if (status === 'auth_error' || status === 'missing_key') return 'border-amber-800/50 bg-amber-950/20 text-amber-300';
        return 'border-red-900/40 bg-red-950/20 text-red-300';
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

                <div className="rounded border border-gray-800 bg-[#0a0a0a] p-4 space-y-3">
                    <p className="text-xs font-mono tracking-widest text-gray-400">AI COMMAND</p>
                    {userRole === 'superadmin' ? (
                        <div className="space-y-4">
                            <div className="grid grid-cols-1 gap-4">
                                <div className="space-y-2">
                                    <label className="text-[11px] font-mono text-gray-500 uppercase tracking-widest">Tên Model</label>
                                    <input
                                        type="text"
                                        value={aiModelName}
                                        onChange={(e) => setAiModelName(e.target.value)}
                                        className="w-full bg-black border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500"
                                        placeholder={DEFAULT_AI_MODEL}
                                    />
                                    <div className="mt-2 space-y-2">
                                        {aiApiKeyRows.map((row, index) => (
                                            <div key={row.id} className="flex items-center gap-2">
                                                <input
                                                    type="password"
                                                    value={row.kind === 'new' ? row.value : ''}
                                                    onChange={(e) => row.kind === 'new' && updateApiKeyRowValue(row.id, e.target.value)}
                                                    readOnly={row.kind === 'existing'}
                                                    className="w-full bg-black border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500 read-only:text-gray-500"
                                                    placeholder={
                                                        row.kind === 'existing'
                                                            ? `Đã lưu key project ${index + 1} (ẩn hoàn toàn)`
                                                            : `Nhập API key project mới ${index + 1}`
                                                    }
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => removeApiKeyRow(row.id)}
                                                    className="inline-flex items-center justify-center rounded border border-red-900/40 px-3 py-2.5 text-red-300 hover:border-red-500 hover:text-red-200"
                                                    title={row.kind === 'existing' ? 'Xóa dòng key đã lưu này' : 'Bỏ dòng key mới này'}
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                    <button
                                        type="button"
                                        onClick={addApiKeyRow}
                                        className="inline-flex items-center gap-2 rounded border border-gray-700 px-4 py-2 text-xs font-mono text-gray-300 hover:border-green-500 hover:text-green-300"
                                    >
                                        <Plus size={14} />
                                        THÊM DÒNG KEY
                                    </button>
                                    <p className="text-xs text-gray-500">
                                        Đang lưu trên server: {settings.ai_api_keys_count || 0} key. Backend sẽ xoay từng tổ hợp <span className="font-mono text-gray-300">key x model</span> theo thứ tự ưu tiên.
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-[11px] font-mono text-gray-500 uppercase tracking-widest">
                                    <Bot size={12} />
                                    Model Catalog
                                </div>
                                <p className="text-xs text-gray-500">
                                    Danh sách này được lưu server-side. Backend sẽ tự thử model tiếp theo trong catalog nếu model hiện tại bị rate-limit hoặc hết quota/RPD.
                                </p>
                                <p className="text-xs text-gray-500">
                                    Rotation backend đang chạy theo thứ tự catalog và thử từng tổ hợp key x model cho đến khi có model trả lời thành công.
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {modelCatalog.map((model, index) => {
                                        const isActive = aiModelName === model;
                                        return (
                                            <div
                                                key={model}
                                                className={`inline-flex items-center gap-2 rounded border px-3 py-1.5 text-xs font-mono transition-colors ${isActive ? 'border-green-500 bg-green-950/30 text-green-300' : 'border-gray-800 bg-black text-gray-400 hover:border-gray-700 hover:text-gray-200'}`}
                                            >
                                                <button
                                                    type="button"
                                                    onClick={() => setAiModelName(model)}
                                                    className="text-left"
                                                >
                                                    <span className="mr-2 text-[10px] text-gray-500">{index + 1}.</span>
                                                    <span>{model}</span>
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => moveModel(index, 'left')}
                                                    disabled={index === 0}
                                                    className="text-gray-500 hover:text-gray-200 disabled:cursor-not-allowed disabled:text-gray-800"
                                                >
                                                    <ChevronLeft size={12} />
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => moveModel(index, 'right')}
                                                    disabled={index === modelCatalog.length - 1}
                                                    className="text-gray-500 hover:text-gray-200 disabled:cursor-not-allowed disabled:text-gray-800"
                                                >
                                                    <ChevronRight size={12} />
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => removeModelFromCatalog(model)}
                                                    className="text-red-400"
                                                >
                                                    x
                                                </button>
                                            </div>
                                        );
                                    })}
                                </div>
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={customModelInput}
                                        onChange={(e) => setCustomModelInput(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addModelToCatalog())}
                                        className="flex-1 bg-black border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500"
                                        placeholder="Thêm model name bất kỳ..."
                                    />
                                    <button
                                        type="button"
                                        onClick={addModelToCatalog}
                                        className="inline-flex items-center gap-2 rounded border border-gray-700 px-4 py-2 text-xs font-mono text-gray-300 hover:border-green-500 hover:text-green-300"
                                    >
                                        <Plus size={14} />
                                        THÊM MODEL
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-center gap-2 text-sm text-gray-500 italic">
                            <ShieldAlert size={14} className="text-amber-500" />
                            <span>Chỉ superadmin được thay đổi AI model và API key.</span>
                        </div>
                    )}
                </div>

                {userRole === 'superadmin' && (
                    <div className="rounded border border-gray-800 bg-[#0a0a0a] p-4 space-y-4">
                        <div className="flex items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-mono tracking-widest text-gray-400">AI PLAYGROUND</p>
                                <p className="mt-1 text-sm text-gray-500">Autotest model đang chọn hoặc quét toàn bộ catalog với key lưu sẵn hay key tạm thời.</p>
                            </div>
                            <FlaskConical className="text-green-500" size={18} />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2 md:col-span-2">
                                <label className="text-[11px] font-mono text-gray-500 uppercase tracking-widest">Prompt Test</label>
                                <textarea
                                    value={playgroundPrompt}
                                    onChange={(e) => setPlaygroundPrompt(e.target.value)}
                                    rows={4}
                                    className="w-full resize-none bg-black border border-gray-800 rounded px-4 py-3 text-gray-200 text-sm focus:outline-none focus:border-green-500"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[11px] font-mono text-gray-500 uppercase tracking-widest">Tiến Độ Chương</label>
                                <input
                                    type="number"
                                    min={1}
                                    value={playgroundChapter}
                                    onChange={(e) => setPlaygroundChapter(Number(e.target.value) || 1)}
                                    className="w-full bg-black border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[11px] font-mono text-gray-500 uppercase tracking-widest">API Key Tạm Thời</label>
                                <input
                                    type="password"
                                    value={playgroundApiKey}
                                    onChange={(e) => setPlaygroundApiKey(e.target.value)}
                                    className="w-full bg-black border border-gray-800 rounded px-4 py-2.5 text-gray-200 text-sm focus:outline-none focus:border-green-500"
                                    placeholder="Bỏ trống để dùng key đã lưu"
                                />
                            </div>
                        </div>

                        <div className="flex flex-wrap gap-3">
                            <button
                                type="button"
                                onClick={() => runPlayground([aiModelName])}
                                disabled={playgroundRunning}
                                className="inline-flex items-center gap-2 rounded bg-green-600 px-4 py-2.5 text-xs font-mono tracking-widest text-white hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-500"
                            >
                                {playgroundRunning ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                                TEST MODEL HIEN TAI
                            </button>
                            <button
                                type="button"
                                onClick={() => runPlayground(modelCatalog)}
                                disabled={playgroundRunning}
                                className="inline-flex items-center gap-2 rounded border border-gray-700 px-4 py-2.5 text-xs font-mono tracking-widest text-gray-300 hover:border-green-500 hover:text-green-300 disabled:border-gray-800 disabled:text-gray-600"
                            >
                                {playgroundRunning ? <Loader2 size={14} className="animate-spin" /> : <Wand2 size={14} />}
                                AUTOTEST TOAN BO
                            </button>
                            <button
                                type="button"
                                onClick={checkOracleHealth}
                                disabled={oracleHealthLoading}
                                className="inline-flex items-center gap-2 rounded border border-cyan-800 px-4 py-2.5 text-xs font-mono tracking-widest text-cyan-300 hover:border-cyan-500 hover:text-cyan-200 disabled:border-gray-800 disabled:text-gray-600"
                            >
                                {oracleHealthLoading ? <Loader2 size={14} className="animate-spin" /> : <ShieldAlert size={14} />}
                                KIEM TRA ORACLE
                            </button>
                            <button
                                type="button"
                                onClick={resetOracleRateLimit}
                                disabled={oracleResetLoading}
                                className="inline-flex items-center gap-2 rounded border border-amber-800 px-4 py-2.5 text-xs font-mono tracking-widest text-amber-300 hover:border-amber-500 hover:text-amber-200 disabled:border-gray-800 disabled:text-gray-600"
                            >
                                {oracleResetLoading ? <Loader2 size={14} className="animate-spin" /> : <AlertTriangle size={14} />}
                                RESET RATE LIMIT
                            </button>
                        </div>

                        {playgroundError && (
                            <div className="rounded border border-red-900/40 bg-red-950/20 px-4 py-3 text-sm text-red-300">
                                {playgroundError}
                            </div>
                        )}

                        {oracleAdminMessage && (
                            <div className="rounded border border-amber-900/40 bg-amber-950/20 px-4 py-3 text-sm text-amber-200">
                                {oracleAdminMessage}
                            </div>
                        )}

                        {oracleHealth && (
                            <div className="rounded border border-cyan-900/40 bg-cyan-950/10 px-4 py-3 text-sm text-cyan-100 space-y-2">
                                <div className="font-mono text-xs uppercase tracking-widest text-cyan-300">
                                    Oracle Health: {oracleHealth.status}
                                </div>
                                <div>Active model: {oracleHealth.active_model}</div>
                                <div>Has API key: {oracleHealth.has_api_key ? 'yes' : 'no'}</div>
                                <div>Cache configured: {oracleHealth.cache_configured ? 'yes' : 'no'}</div>
                                <div>Rate limit configured: {oracleHealth.rate_limit_configured ? 'yes' : 'no'}</div>
                                <div>Detail: {oracleHealth.detail}</div>
                                {oracleHealth.upstream_error && <div>Upstream error: {oracleHealth.upstream_error}</div>}
                            </div>
                        )}
                        {playgroundResults.length > 0 && (
                            <div className="grid grid-cols-1 gap-3">
                                {playgroundResults.map((result) => (
                                    <div key={result.model} className={`rounded border px-4 py-3 ${getStatusTone(result.status)}`}>
                                        <div className="flex flex-wrap items-center justify-between gap-2">
                                                <div className="font-mono text-sm">{result.model}</div>
                                                <div className="font-mono text-xs uppercase tracking-widest">
                                                    {result.status} · {result.latency_ms}ms · {result.used_saved_key ? 'saved-key' : 'temp-key'}
                                                </div>
                                            </div>
                                        {result.error && <p className="mt-2 text-sm">{result.error}</p>}
                                        {result.answer_preview && <p className="mt-2 text-sm text-gray-200">{result.answer_preview}</p>}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

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
