'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { getFreshAdminAccessToken } from '@/lib/admin-session';
import { getUserRole } from '@/lib/api';
import {
    Cpu,
    Activity,
    Save,
    ShieldAlert,
    AlertTriangle,
    CheckCircle2,
    Loader2,
    Plus,
    Trash2,
    RefreshCw,
    Server,
    Settings,
    Zap,
    Play,
    Hourglass,
    Check,
    ChevronDown,
    ChevronUp
} from 'lucide-react';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');

interface ProviderConfig {
    name: string;
    display_name: string;
    type: string;
    enabled: boolean;
    base_url: string;
    api_keys: string[];
    models: string[];
    default_model: string;
    timeout: number;
}

interface FullConfig {
    providers: Record<string, ProviderConfig>;
    translation_policy: {
        mode: 'waterfall' | 'ai_pool_auto';
        provider_order?: string[];
    };
    chat_policy: {
        mode: 'waterfall' | 'ai_pool_auto';
        provider_order?: string[];
    };
}

interface HealthSnapshotItem {
    provider_name: string;
    display_name: string;
    model: string;
    is_available: boolean;
    health_status: string;
    consecutive_failures: number;
    success_count: number;
    failure_count: number;
    last_error_type: string;
    last_latency_ms: number;
    quality_score: number;
    latency_score: number;
}

interface HealthCheckResultItem {
    provider_id: string;
    provider_name: string;
    model_id: string;
    status: string;
    error_category: string;
    message: string;
    latency_ms: number;
    checked_at: string;
    suggestion: string;
    raw_error_sanitized: string;
}

export default function AdminAiPage() {
    const router = useRouter();
    const [config, setConfig] = useState<FullConfig | null>(null);
    const [healthSnapshot, setHealthSnapshot] = useState<HealthSnapshotItem[]>([]);
    const [healthCheckResults, setHealthCheckResults] = useState<HealthCheckResultItem[]>([]);
    
    // UI state
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [probing, setProbing] = useState(false);
    const [resetting, setResetting] = useState(false);
    const [discoveringProviders, setDiscoveringProviders] = useState<Record<string, boolean>>({});
    const [userRole, setUserRole] = useState<string>('editor');
    const [token, setToken] = useState<string | null>(null);
    
    // Status banners
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    
    // Accordion state
    const [expandedProvider, setExpandedProvider] = useState<string | null>(null);

    // Load configurations and health snapshot
    useEffect(() => {
        const loadInitialData = async () => {
            const supabase = createAdminClient();
            if (!supabase) {
                setError('Lỗi cấu hình admin. Thiếu Supabase.');
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

                if (role !== 'superadmin') {
                    setError('Bạn không có quyền superadmin để quản trị hệ thống AI.');
                    setLoading(false);
                    return;
                }

                // Fetch AI Config and Snapshot parallelly
                const [configRes, snapshotRes] = await Promise.all([
                    fetch(`${API_BASE_URL}/api/admin/ai/providers/config`, {
                        headers: { 'Authorization': `Bearer ${session.access_token}` }
                    }),
                    fetch(`${API_BASE_URL}/api/admin/ai/providers/health-snapshot`, {
                        headers: { 'Authorization': `Bearer ${session.access_token}` },
                        cache: 'no-store'
                    })
                ]);

                if (configRes.ok) {
                    const configData = await configRes.json();
                    setConfig(configData);
                } else {
                    throw new Error('Không thể tải cấu hình AI.');
                }

                if (snapshotRes.ok) {
                    const snapshotData = await snapshotRes.json();
                    setHealthSnapshot(snapshotData.snapshot || []);
                }
            } catch (err: any) {
                setError(err?.message || 'Không thể kết nối API cấu hình AI.');
            } finally {
                setLoading(false);
            }
        };

        loadInitialData();
    }, [router]);

    // Save configuration updates
    const handleSaveConfig = async () => {
        if (!token || !config) return;
        setSaving(true);
        setError(null);
        setSuccess(null);

        try {
            const freshToken = await getFreshAdminAccessToken();
            setToken(freshToken);

            const res = await fetch(`${API_BASE_URL}/api/admin/ai/providers`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${freshToken}`
                },
                body: JSON.stringify({
                    providers: config.providers,
                    translation_policy: config.translation_policy,
                    chat_policy: config.chat_policy
                })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Lỗi lưu cấu hình.');

            setSuccess('Đã lưu cấu hình AI Providers và làm mới bộ định tuyến thành công!');
            setTimeout(() => setSuccess(null), 4000);
            
            // Reload snapshot
            const snapshotRes = await fetch(`${API_BASE_URL}/api/admin/ai/providers/health-snapshot`, {
                headers: { 'Authorization': `Bearer ${freshToken}` },
                cache: 'no-store'
            });
            if (snapshotRes.ok) {
                const snapshotData = await snapshotRes.json();
                setHealthSnapshot(snapshotData.snapshot || []);
            }
        } catch (err: any) {
            setError(err?.message || 'Không thể lưu cấu hình.');
        } finally {
            setSaving(false);
        }
    };

    // Dynamically discover models from provider's API key
    const handleDiscoverModels = async (providerKey: string) => {
        if (!token) return;
        setDiscoveringProviders(prev => ({ ...prev, [providerKey]: true }));
        setError(null);
        setSuccess(null);
        try {
            const freshToken = await getFreshAdminAccessToken();
            setToken(freshToken);

            const res = await fetch(`${API_BASE_URL}/api/admin/ai/providers/${providerKey}/discover-models`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${freshToken}`
                }
            });
            const data = await res.json();
            if (res.ok) {
                setSuccess(`Đã dò quét thành công! Phát hiện ${data.discovered_count} model hợp lệ từ API của ${providerKey}.`);
                // Reload configuration to get the fresh list of models
                const configRes = await fetch(`${API_BASE_URL}/api/admin/ai/providers/config`, {
                    headers: { 'Authorization': `Bearer ${freshToken}` }
                });
                if (configRes.ok) {
                    const configData = await configRes.json();
                    setConfig(configData);
                }
            } else {
                throw new Error(data.detail || `Lỗi dò quét model cho ${providerKey}`);
            }
        } catch (err: any) {
            setError(err?.message || `Lỗi kết nối khi dò quét model cho ${providerKey}`);
        } finally {
            setDiscoveringProviders(prev => ({ ...prev, [providerKey]: false }));
        }
    };

    // Run dynamic full health probe (ONE-CLICK AUTOMATIC HEALTH CHECK)
    const handleRunHealthCheck = async () => {
        if (!token) return;
        setProbing(true);
        setError(null);
        setSuccess(null);
        setHealthCheckResults([]);

        try {
            const freshToken = await getFreshAdminAccessToken();
            setToken(freshToken);

            const res = await fetch(`${API_BASE_URL}/api/admin/ai/providers/health-check`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${freshToken}`
                },
                body: JSON.stringify({}) // Empty body runs check for all enabled providers
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Lỗi chạy kiểm tra sức khỏe.');

            setHealthCheckResults(data.results || []);
            setSuccess(`Đã hoàn thành dò quét sức khỏe của ${data.total} mô hình AI!`);
            
            // Reload snapshot info to get the fresh runtime status
            const snapshotRes = await fetch(`${API_BASE_URL}/api/admin/ai/providers/health-snapshot`, {
                headers: { 'Authorization': `Bearer ${freshToken}` },
                cache: 'no-store'
            });
            if (snapshotRes.ok) {
                const snapshotData = await snapshotRes.json();
                setHealthSnapshot(snapshotData.snapshot || []);
            }
        } catch (err: any) {
            setError(err?.message || 'Lỗi trong quá trình kiểm tra sức khỏe AI.');
        } finally {
            setProbing(false);
        }
    };

    // Clear cooldown penalties instantly
    const handleResetCooldowns = async () => {
        if (!token) return;
        setResetting(true);
        setError(null);
        setSuccess(null);

        try {
            const freshToken = await getFreshAdminAccessToken();
            setToken(freshToken);

            const res = await fetch(`${API_BASE_URL}/api/admin/ai/providers/reset-cooldowns`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${freshToken}` }
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Lỗi xóa cooldown.');

            setSuccess('Đã dọn sạch cooldown! Toàn bộ mô hình đã được khôi phục trạng thái sẵn sàng.');
            setTimeout(() => setSuccess(null), 3000);

            // Reload snapshot info to get the fresh status
            const snapshotRes = await fetch(`${API_BASE_URL}/api/admin/ai/providers/health-snapshot`, {
                headers: { 'Authorization': `Bearer ${freshToken}` },
                cache: 'no-store'
            });
            if (snapshotRes.ok) {
                const snapshotData = await snapshotRes.json();
                setHealthSnapshot(snapshotData.snapshot || []);
            }
        } catch (err: any) {
            setError(err?.message || 'Không thể xóa cooldown.');
        } finally {
            setResetting(false);
        }
    };

    // Helper functions to mutate local UI config state
    const updateProviderField = (provider: string, field: keyof ProviderConfig, value: any) => {
        if (!config) return;
        setConfig({
            ...config,
            providers: {
                ...config.providers,
                [provider]: {
                    ...config.providers[provider],
                    [field]: value
                }
            }
        });
    };

    const addApiKeyField = (provider: string) => {
        if (!config) return;
        const currentKeys = config.providers[provider].api_keys || [];
        updateProviderField(provider, 'api_keys', [...currentKeys, '']);
    };

    const removeApiKeyField = (provider: string, index: number) => {
        if (!config) return;
        const currentKeys = [...(config.providers[provider].api_keys || [])];
        currentKeys.splice(index, 1);
        updateProviderField(provider, 'api_keys', currentKeys);
    };

    const updateApiKeyFieldValue = (provider: string, index: number, value: string) => {
        if (!config) return;
        const currentKeys = [...(config.providers[provider].api_keys || [])];
        currentKeys[index] = value;
        updateProviderField(provider, 'api_keys', currentKeys);
    };

    const addModelField = (provider: string, modelName: string) => {
        if (!config || !modelName.trim()) return;
        const currentModels = config.providers[provider].models || [];
        if (currentModels.includes(modelName.trim())) return;
        updateProviderField(provider, 'models', [...currentModels, modelName.trim()]);
    };

    const removeModelField = (provider: string, modelName: string) => {
        if (!config) return;
        const currentModels = (config.providers[provider].models || []).filter(m => m !== modelName);
        let defaultModel = config.providers[provider].default_model;
        if (defaultModel === modelName) {
            defaultModel = currentModels[0] || '';
        }
        setConfig({
            ...config,
            providers: {
                ...config.providers,
                [provider]: {
                    ...config.providers[provider],
                    models: currentModels,
                    default_model: defaultModel
                }
            }
        });
    };

    const moveProviderOrder = (type: 'translation' | 'chat', index: number, direction: 'up' | 'down') => {
        if (!config) return;
        const policyKey = type === 'translation' ? 'translation_policy' : 'chat_policy';
        const currentOrder = [...(config[policyKey].provider_order || [])];
        
        const targetIndex = direction === 'up' ? index - 1 : index + 1;
        if (targetIndex < 0 || targetIndex >= currentOrder.length) return;

        const temp = currentOrder[index];
        currentOrder[index] = currentOrder[targetIndex];
        currentOrder[targetIndex] = temp;

        setConfig({
            ...config,
            [policyKey]: {
                ...config[policyKey],
                provider_order: currentOrder
            }
        });
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-96 gap-4">
                <Loader2 className="animate-spin text-green-500" size={40} />
                <p className="font-mono text-xs text-gray-500 tracking-widest animate-pulse">ĐANG KẾT NỐI HỆ THỐNG AI PROVIDERS...</p>
            </div>
        );
    }

    if (error && userRole !== 'superadmin') {
        return (
            <div className="max-w-4xl mx-auto mt-10">
                <div className="flex items-center gap-3 text-red-400 bg-red-950/20 border border-red-900/40 rounded-lg p-6 font-mono text-sm shadow-xl">
                    <ShieldAlert size={24} className="shrink-0" />
                    <div>
                        <h2 className="font-bold text-base mb-1">CẢNH BÁO QUYỀN HẠN</h2>
                        <span>{error}</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto pb-20">
            {/* Header Banner */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 border-b border-gray-800 pb-6">
                <div>
                    <h1 className="text-2xl md:text-3xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
                        <Cpu className="text-green-500 animate-pulse" size={28} />
                        CẤU HÌNH AI XOAY TUA ĐỘNG
                    </h1>
                    <p className="text-gray-500 text-sm font-mono mt-1">
                        Hệ thống dịch và chatbot bất tử - Tự động quản lý API Key, xoay tua Model, xử lý lỗi và Cooldown.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleSaveConfig}
                        disabled={saving}
                        className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-500 text-white rounded font-mono text-xs tracking-wider font-semibold py-2.5 px-5 transition-all duration-200 shadow-lg shadow-green-950/30 active:scale-95 disabled:opacity-50"
                    >
                        {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                        LƯU CẤU HÌNH
                    </button>
                </div>
            </div>

            {/* Notification Banners */}
            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded-lg p-4 text-sm font-mono mb-6 shadow-md transition-all duration-300">
                    <CheckCircle2 size={16} className="shrink-0" />
                    <span>{success}</span>
                </div>
            )}

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded-lg p-4 text-sm font-mono mb-6 shadow-md transition-all duration-300">
                    <AlertTriangle size={16} className="shrink-0" />
                    <span>{error}</span>
                </div>
            )}

            {/* MAIN GRID */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                {/* LEFT & CENTER COLUMN: Configs & Accordions */}
                <div className="lg:col-span-2 space-y-8">
                    
                    {/* Dynamic Policies Panel */}
                    {config && (
                        <div className="bg-[#0f0f0f] border border-gray-800 rounded-lg p-6 shadow-lg">
                            <h2 className="text-sm font-mono tracking-widest text-gray-400 uppercase mb-4 flex items-center gap-2">
                                <Settings size={14} className="text-gray-500" />
                                CƠ CHẾ ĐỊNH TUYẾN AI (ROUTING POLICY)
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                
                                {/* Translation Policy */}
                                <div className="space-y-4 bg-black/40 border border-gray-800/60 rounded p-4">
                                    <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                                        <span className="font-mono text-xs text-green-400 font-bold uppercase tracking-wider">Hệ Thống Dịch Thuật</span>
                                        <Zap size={12} className="text-green-500" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-mono text-gray-500 uppercase">Thuật toán định tuyến</label>
                                        <select
                                            value={config.translation_policy.mode}
                                            onChange={(e) => setConfig({
                                                ...config,
                                                translation_policy: {
                                                    ...config.translation_policy,
                                                    mode: e.target.value as any
                                                }
                                            })}
                                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-xs font-mono focus:outline-none focus:border-green-500 appearance-none"
                                        >
                                            <option value="waterfall">Waterfall (Thử tuần tự theo ưu tiên)</option>
                                            <option value="ai_pool_auto">AI Pool Auto (Định tuyến động theo tốc độ + chất lượng)</option>
                                        </select>
                                    </div>
                                </div>

                                {/* Chat Policy */}
                                <div className="space-y-4 bg-black/40 border border-gray-800/60 rounded p-4">
                                    <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                                        <span className="font-mono text-xs text-cyan-400 font-bold uppercase tracking-wider">AI Oracle Chatbot</span>
                                        <Cpu size={12} className="text-cyan-500" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-mono text-gray-500 uppercase">Thuật toán định tuyến</label>
                                        <select
                                            value={config.chat_policy.mode}
                                            onChange={(e) => setConfig({
                                                ...config,
                                                chat_policy: {
                                                    ...config.chat_policy,
                                                    mode: e.target.value as any
                                                }
                                            })}
                                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-xs font-mono focus:outline-none focus:border-green-500 appearance-none"
                                        >
                                            <option value="waterfall">Waterfall (Thử tuần tự theo ưu tiên)</option>
                                            <option value="ai_pool_auto">AI Pool Auto (Định tuyến động theo tốc độ + chất lượng)</option>
                                        </select>
                                    </div>
                                </div>

                            </div>
                        </div>
                    )}

                    {/* Providers Configurations Accordions */}
                    {config && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-sm font-mono tracking-widest text-gray-400 uppercase flex items-center gap-2">
                                    <Server size={14} className="text-gray-500" />
                                    DANH SÁCH AI PROVIDERS ({Object.keys(config.providers).length})
                                </h2>
                                <span className="text-[10px] text-gray-500 font-mono">* Bật và nhập Key để kích hoạt</span>
                            </div>

                            <div className="space-y-3">
                                {Object.entries(config.providers).map(([providerKey, provider]) => {
                                    const isExpanded = expandedProvider === providerKey;
                                    const hasKeys = (provider.api_keys || []).filter(k => k.trim()).length > 0;
                                    const isActive = provider.enabled && hasKeys;

                                    return (
                                        <div
                                            key={providerKey}
                                            className={`bg-[#0f0f0f] border rounded-lg transition-all duration-200 overflow-hidden ${
                                                isActive ? 'border-green-800/40 shadow-green-950/5' : 'border-gray-800/80'
                                            }`}
                                        >
                                            {/* Header */}
                                            <div
                                                onClick={() => setExpandedProvider(isExpanded ? null : providerKey)}
                                                className="flex items-center justify-between p-4 cursor-pointer hover:bg-black/20 select-none"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-green-500 shadow-md shadow-green-500/50' : 'bg-gray-700'}`} />
                                                    <div>
                                                        <span className="font-mono text-sm font-bold text-gray-200">{provider.display_name}</span>
                                                        <span className="font-mono text-[9px] text-gray-500 ml-2 tracking-wider uppercase">({providerKey})</span>
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-4">
                                                    <div className="flex items-center gap-2">
                                                        <label className="text-[10px] font-mono text-gray-500 uppercase cursor-pointer">BẬT</label>
                                                        <input
                                                            type="checkbox"
                                                            checked={provider.enabled}
                                                            onClick={(e) => e.stopPropagation()} // Stop accordion toggling
                                                            onChange={(e) => updateProviderField(providerKey, 'enabled', e.target.checked)}
                                                            className="w-3.5 h-3.5 rounded border-gray-800 bg-black text-green-500 focus:ring-0 focus:ring-offset-0 cursor-pointer accent-green-600"
                                                        />
                                                    </div>
                                                    {isExpanded ? <ChevronUp size={16} className="text-gray-500" /> : <ChevronDown size={16} className="text-gray-500" />}
                                                </div>
                                            </div>

                                            {/* Body Expanded */}
                                            {isExpanded && (
                                                <div className="p-5 border-t border-gray-850 bg-black/30 space-y-6">
                                                    
                                                    {/* Row: Base URL & Timeout */}
                                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                        <div className="md:col-span-2 space-y-1.5">
                                                            <label className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Base API URL</label>
                                                            <input
                                                                type="text"
                                                                value={provider.base_url}
                                                                onChange={(e) => updateProviderField(providerKey, 'base_url', e.target.value)}
                                                                className="w-full bg-[#050505] border border-gray-800 rounded px-3 py-2 text-gray-300 font-mono text-xs focus:outline-none focus:border-green-500 transition-all"
                                                                placeholder="Nhập endpoint chuẩn..."
                                                            />
                                                        </div>
                                                        <div className="space-y-1.5">
                                                            <label className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Timeout (giây)</label>
                                                            <input
                                                                type="number"
                                                                min={1}
                                                                value={provider.timeout || 20}
                                                                onChange={(e) => updateProviderField(providerKey, 'timeout', parseInt(e.target.value) || 20)}
                                                                className="w-full bg-[#050505] border border-gray-800 rounded px-3 py-2 text-gray-300 font-mono text-xs focus:outline-none focus:border-green-500 transition-all"
                                                            />
                                                        </div>
                                                    </div>

                                                    {/* API Keys Rotation Panel */}
                                                    <div className="space-y-2">
                                                        <label className="text-[10px] font-mono text-gray-500 uppercase tracking-widest flex items-center gap-1.5">
                                                            <span>Danh sách API Keys</span>
                                                            <span className="text-[9px] text-gray-600 font-normal">(Xoay tua vòng lặp)</span>
                                                        </label>
                                                        
                                                        <div className="space-y-2">
                                                            {(provider.api_keys || []).map((key, kIndex) => {
                                                                const isMasked = key.startsWith('****');
                                                                return (
                                                                    <div key={kIndex} className="flex items-center gap-2">
                                                                        <input
                                                                            type={isMasked ? 'text' : 'password'}
                                                                            value={isMasked ? '' : key}
                                                                            readOnly={isMasked}
                                                                            onChange={(e) => !isMasked && updateApiKeyFieldValue(providerKey, kIndex, e.target.value)}
                                                                            className="flex-1 bg-[#050505] border border-gray-800 rounded px-3 py-2 text-gray-300 font-mono text-xs focus:outline-none focus:border-green-500 read-only:text-gray-500"
                                                                            placeholder={
                                                                                isMasked 
                                                                                    ? `Đã lưu API Key #${kIndex + 1} (ẩn bảo mật)`
                                                                                    : `Nhập API Key #${kIndex + 1}...`
                                                                            }
                                                                        />
                                                                        <button
                                                                            type="button"
                                                                            onClick={() => removeApiKeyField(providerKey, kIndex)}
                                                                            className="p-2 border border-red-900/40 text-red-400 hover:bg-red-950/20 hover:text-red-300 rounded transition-colors"
                                                                            title="Xóa dòng key này"
                                                                        >
                                                                            <Trash2 size={12} />
                                                                        </button>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>

                                                        <button
                                                            type="button"
                                                            onClick={() => addApiKeyField(providerKey)}
                                                            className="inline-flex items-center gap-1 text-[10px] font-mono text-gray-400 hover:text-green-400 border border-gray-800 hover:border-green-800/40 px-3 py-1.5 rounded transition-all"
                                                        >
                                                            <Plus size={10} />
                                                            THÊM DÒNG KEY
                                                        </button>
                                                    </div>

                                                    {/* Supported Models Catalog & Default Model */}
                                                    <div className="space-y-3">
                                                        <label className="text-[10px] font-mono text-gray-500 uppercase tracking-widest flex items-center gap-1.5">
                                                            Danh Sách Mô Hình Hoạt Động (Model Catalog)
                                                        </label>
                                                        
                                                        {/* Models lists tags */}
                                                        <div className="flex flex-wrap gap-2 min-h-[30px] p-2 bg-[#050505]/60 border border-gray-850 rounded">
                                                            {(provider.models || []).map(modelName => {
                                                                const isDefault = provider.default_model === modelName;
                                                                return (
                                                                    <div
                                                                        key={modelName}
                                                                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[10px] font-mono border ${
                                                                            isDefault 
                                                                                ? 'border-green-800/60 bg-green-950/20 text-green-300'
                                                                                : 'border-gray-800 bg-black text-gray-400'
                                                                        }`}
                                                                    >
                                                                        <button
                                                                            type="button"
                                                                            onClick={() => updateProviderField(providerKey, 'default_model', modelName)}
                                                                            className="font-bold hover:underline"
                                                                            title="Đặt làm model mặc định chính"
                                                                        >
                                                                            {modelName} {isDefault && '★'}
                                                                        </button>
                                                                        <button
                                                                            type="button"
                                                                            onClick={() => removeModelField(providerKey, modelName)}
                                                                            className="text-red-400 hover:text-red-300 font-bold"
                                                                            title="Xóa model này"
                                                                        >
                                                                            x
                                                                        </button>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>

                                                        {/* Input add model */}
                                                        <div className="flex gap-2">
                                                            <input
                                                                type="text"
                                                                id={`new-model-input-${providerKey}`}
                                                                placeholder="Thêm model ID khác (ví dụ: gemma-2b-it)..."
                                                                onKeyDown={(e) => {
                                                                    if (e.key === 'Enter') {
                                                                        e.preventDefault();
                                                                        const inputEl = e.currentTarget;
                                                                        addModelField(providerKey, inputEl.value);
                                                                        inputEl.value = '';
                                                                    }
                                                                }}
                                                                className="flex-1 bg-[#050505] border border-gray-800 rounded px-3 py-1.5 text-gray-300 font-mono text-xs focus:outline-none focus:border-green-500"
                                                            />
                                                            <button
                                                                type="button"
                                                                onClick={() => {
                                                                    const el = document.getElementById(`new-model-input-${providerKey}`) as HTMLInputElement;
                                                                    if (el) {
                                                                        addModelField(providerKey, el.value);
                                                                        el.value = '';
                                                                    }
                                                                }}
                                                                className="px-3 py-1.5 border border-gray-800 hover:border-green-800/40 text-gray-400 hover:text-green-300 rounded font-mono text-[10px]"
                                                            >
                                                                THÊM MODEL
                                                            </button>
                                                            <button
                                                                type="button"
                                                                disabled={discoveringProviders[providerKey]}
                                                                onClick={() => handleDiscoverModels(providerKey)}
                                                                className="px-3 py-1.5 border border-cyan-900/50 hover:border-cyan-800/80 hover:bg-cyan-950/10 text-cyan-400 hover:text-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed rounded font-mono text-[10px] transition-all"
                                                                title="Tự động kết nối tới API của nhà cung cấp để quét và chèn toàn bộ các mô hình live hiện tại"
                                                            >
                                                                {discoveringProviders[providerKey] ? 'ĐANG QUÉT...' : 'DÒ TÌM MODEL TỰ ĐỘNG'}
                                                            </button>
                                                        </div>
                                                    </div>

                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                </div>

                {/* RIGHT COLUMN: Health Dashboard & Probing Controls (ONE-CLICK PROBE) */}
                <div className="space-y-8">
                    
                    {/* ONE-CLICK HEALTH CHECK BOARD (Visual Premium Interface) */}
                    <div className="bg-[#0f0f0f] border border-gray-850 rounded-lg p-6 shadow-xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-8 opacity-5">
                            <Activity size={100} className="text-green-500" />
                        </div>
                        
                        <div className="mb-4">
                            <h2 className="text-sm font-mono tracking-widest text-gray-200 uppercase flex items-center gap-2">
                                <Activity size={16} className="text-green-500 animate-pulse" />
                                HỆ THỐNG KIỂM TRA SỨC KHỎE
                            </h2>
                            <p className="text-[10px] text-gray-500 font-mono mt-0.5">
                                Kích hoạt tự động quét và kiểm thử từng mô hình AI trong danh mục bằng 1 nút bấm duy nhất.
                            </p>
                        </div>

                        {/* BIG GLOWING PROBE BUTTON */}
                        <div className="py-4">
                            <button
                                onClick={handleRunHealthCheck}
                                disabled={probing}
                                className="w-full flex items-center justify-center gap-3 py-4 px-6 rounded-lg bg-green-600 hover:bg-green-500 text-white font-mono text-sm tracking-widest font-bold transition-all duration-200 shadow-xl shadow-green-950/40 hover:shadow-green-500/20 disabled:bg-gray-800 disabled:text-gray-500 disabled:shadow-none hover:scale-[1.01] active:scale-[0.99]"
                            >
                                {probing ? (
                                    <>
                                        <Loader2 size={16} className="animate-spin" />
                                        ĐANG DÒ QUÉT...
                                    </>
                                ) : (
                                    <>
                                        <Play size={16} fill="white" />
                                        BẮT ĐẦU PROBE KIỂM TRA SỨC KHỎE
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Action auxiliary controls */}
                        <div className="grid grid-cols-2 gap-3 border-t border-gray-850 pt-4 mt-2">
                            <button
                                onClick={handleResetCooldowns}
                                disabled={resetting}
                                className="inline-flex items-center justify-center gap-1.5 py-2 px-3 border border-gray-800 hover:border-green-800/40 rounded text-[10px] font-mono text-gray-400 hover:text-green-300 disabled:opacity-50 transition-colors"
                                title="Giải phóng các model đang bị tạm ngưng/chờ cooldown do lỗi mạng"
                            >
                                {resetting ? <Loader2 size={10} className="animate-spin" /> : <RefreshCw size={10} />}
                                RESET COOLDOWNS
                            </button>

                            <button
                                onClick={async () => {
                                    if (!token) return;
                                    setLoading(true);
                                    try {
                                        const res = await fetch(`${API_BASE_URL}/api/admin/ai/providers/health-snapshot`, {
                                            headers: { 'Authorization': `Bearer ${token}` },
                                            cache: 'no-store'
                                        });
                                        if (res.ok) {
                                            const data = await res.json();
                                            setHealthSnapshot(data.snapshot || []);
                                        }
                                    } catch {} finally {
                                        setLoading(false);
                                    }
                                }}
                                className="inline-flex items-center justify-center gap-1.5 py-2 px-3 border border-gray-800 rounded text-[10px] font-mono text-gray-400 hover:text-gray-200 transition-colors"
                            >
                                <RefreshCw size={10} />
                                LÀM MỚI SNAPSHOT
                            </button>
                        </div>
                    </div>

                    {/* Runtime Availability Status snapshot */}
                    <div className="bg-[#0f0f0f] border border-gray-850 rounded-lg p-5 space-y-4 shadow-lg">
                        <div className="border-b border-gray-850 pb-2">
                            <h3 className="text-xs font-mono tracking-wider font-bold text-gray-400 uppercase flex items-center gap-2">
                                <Server size={12} className="text-gray-500" />
                                TRẠNG THÁI RUNTIME (SNAPSHOT)
                            </h3>
                        </div>

                        {healthSnapshot.length === 0 ? (
                            <p className="text-xs font-mono text-gray-600 italic py-2">Chưa có dữ liệu snapshot hoạt động.</p>
                        ) : (
                            <div className="space-y-3.5 max-h-[300px] overflow-y-auto pr-1">
                                {healthSnapshot.map(item => {
                                    const statusTone = item.is_available 
                                        ? 'bg-green-500/10 text-green-400 border-green-900/30'
                                        : item.health_status === 'cooldown' 
                                            ? 'bg-amber-500/10 text-amber-400 border-amber-900/30'
                                            : 'bg-red-500/10 text-red-400 border-red-900/30';
                                    
                                    return (
                                        <div key={`${item.provider_name}-${item.model}`} className="flex flex-col gap-1 border-b border-gray-850/60 pb-2.5 last:border-0 last:pb-0 font-mono text-[10px]">
                                            <div className="flex items-center justify-between">
                                                <span className="font-bold text-gray-300">{item.display_name}</span>
                                                <span className={`px-2 py-0.5 border rounded text-[9px] ${statusTone}`}>
                                                    {item.is_available ? 'ONLINE' : item.health_status.toUpperCase()}
                                                </span>
                                            </div>
                                            <div className="flex items-center justify-between text-gray-500">
                                                <span>Model: {item.model}</span>
                                                <span>{item.last_latency_ms} ms</span>
                                            </div>
                                            {item.failure_count > 0 && (
                                                <div className="flex items-center justify-between text-[9px]">
                                                    <span className="text-green-600">Thành công: {item.success_count}</span>
                                                    <span className="text-red-500">Lỗi liên tiếp: {item.consecutive_failures}</span>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Probing Health check results details log */}
                    {healthCheckResults.length > 0 && (
                        <div className="bg-[#0f0f0f] border border-gray-850 rounded-lg p-5 space-y-4 shadow-lg transition-all duration-300">
                            <div className="border-b border-gray-850 pb-2 flex items-center justify-between">
                                <h3 className="text-xs font-mono tracking-wider font-bold text-gray-400 uppercase">
                                    NHẬT KÝ KIỂM TRA (PROBING LOG)
                                </h3>
                                <span className="text-[9px] bg-green-950/40 text-green-400 border border-green-800/40 px-2 py-0.5 rounded font-mono">Xong</span>
                            </div>

                            <div className="space-y-3.5 max-h-[350px] overflow-y-auto pr-1">
                                {healthCheckResults.map((item, idx) => {
                                    const isSuccess = item.status === 'success';
                                    return (
                                        <div key={idx} className="flex flex-col gap-1 border-b border-gray-850/60 pb-3 last:border-0 last:pb-0 font-mono text-[10px]">
                                            <div className="flex items-center justify-between">
                                                <span className="font-bold text-gray-300">{item.provider_name}</span>
                                                <span className={`px-1.5 py-0.5 rounded-[3px] text-[8px] ${
                                                    isSuccess ? 'bg-emerald-950/40 text-emerald-400' : 'bg-red-950/40 text-red-400'
                                                }`}>
                                                    {item.status.toUpperCase()}
                                                </span>
                                            </div>
                                            <div className="text-gray-500 text-[9px] truncate">Model: {item.model_id}</div>
                                            <div className="flex items-center justify-between text-gray-600">
                                                <span>Thời gian kiểm tra:</span>
                                                <span>{item.latency_ms} ms</span>
                                            </div>
                                            {!isSuccess && (
                                                <div className="mt-1 p-2 bg-red-950/10 border border-red-900/30 rounded text-[9px] space-y-1 text-red-400">
                                                    <div><span className="font-bold uppercase text-red-300">Lỗi ({item.error_category}):</span> {item.message}</div>
                                                    <div className="text-gray-500"><span className="font-bold text-gray-400">Gợi ý:</span> {item.suggestion}</div>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                </div>

            </div>
        </div>
    );
}
