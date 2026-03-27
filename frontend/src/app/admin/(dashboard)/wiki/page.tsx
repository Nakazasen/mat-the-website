"use client";

import { useState, useEffect, useCallback } from "react";
import { PlusCircle, Edit2, Trash2, BookOpen, X, Save, Loader2, AlertCircle, CheckCircle, Upload, Users, Star, Languages } from "lucide-react";
import { useRouter } from "next/navigation";
import { createAdminClient } from "@/lib/supabase-admin";
import {
    WikiEntry, WikiEntryIn, WIKI_CATEGORIES, FactionMember,
    getWikiEntries, createWikiEntry, updateWikiEntry, deleteWikiEntry, uploadImageR2, getFactionHierarchy,
    translateAdminWikiEntry, translateAdminWikiBatch
} from "@/lib/api";
import RichTextEditor from "@/components/Editor";
import FactionHierarchyEditor from "@/components/FactionHierarchyEditor";

// ── Auto-generate slug from title ─────────────────────────
function toSlug(text: string): string {
    return text
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/đ/gi, "d")
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, "")
        .trim()
        .replace(/\s+/g, "-");
}

const EMPTY_FORM: WikiEntryIn = { title: "", category: "Sinh vật", slug: "", summary: "", content: "", image_url: "", tags: [], sort_order: 0, is_main_character: false };
const CATEGORY_ICONS: Record<string, string> = {
    "Nhân vật": "👤", "Sinh vật": "🧟", "Thế lực": "⚔️", "Vật phẩm": "🗡️", "Địa điểm": "📍"
};

export default function AdminWikiPage() {
    const router = useRouter();
    const [entries, setEntries] = useState<WikiEntry[]>([]);
    const [filter, setFilter] = useState<string>("all");
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [form, setForm] = useState<WikiEntryIn>(EMPTY_FORM);
    const [saving, setSaving] = useState(false);
    const [toast, setToast] = useState<{ type: "success" | "error"; msg: string } | null>(null);
    const [hierarchyEntry, setHierarchyEntry] = useState<WikiEntry | null>(null);
    const [hierarchyMembers, setHierarchyMembers] = useState<FactionMember[]>([]);
    const [isUploadingImg, setIsUploadingImg] = useState(false);
    const [token, setToken] = useState<string | null>(null);
    const [translatingId, setTranslatingId] = useState<string | null>(null);
    const [batchTranslating, setBatchTranslating] = useState(false);
    const [batchOnlyMissing, setBatchOnlyMissing] = useState(true);
    const [batchResult, setBatchResult] = useState<{ translated: number; skipped: number; failed: number; failedEntries: Array<{ title: string; detail?: string }> } | null>(null);

    useEffect(() => {
        const loadSession = async () => {
            const supabase = createAdminClient();
            if (!supabase) return;
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push("/admin/login");
                return;
            }
            setToken(session.access_token);
        };
        loadSession();
    }, [router]);

    const load = useCallback(async () => {
        setLoading(true);
        try {
            const response = await getWikiEntries(filter === "all" ? undefined : filter, undefined, page);
            setEntries(response.entries);
            setTotalPages(response.total_pages);
            setTotal(response.total);
        } catch {
            showToast("error", "Không tải được danh sách Wiki");
        } finally {
            setLoading(false);
        }
    }, [filter, page]);

    useEffect(() => { setPage(1); }, [filter]);

    useEffect(() => { load(); }, [load]);

    function showToast(type: "success" | "error", msg: string) {
        setToast({ type, msg });
        setTimeout(() => setToast(null), 3000);
    }

    function openNew() {
        setForm(EMPTY_FORM);
        setEditingId(null);
        setShowForm(true);
    }

    function openEdit(entry: WikiEntry) {
        setForm({
            title: entry.title, category: entry.category, slug: entry.slug,
            summary: entry.summary || "", content: entry.content || "",
            image_url: entry.image_url || "", tags: entry.tags || [],
            sort_order: entry.sort_order || 0, is_main_character: entry.is_main_character || false,
        });
        setEditingId(entry.id);
        setShowForm(true);
    }

    async function handleSave() {
        if (!token) {
            showToast("error", "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
            return;
        }
        if (!form.title || !form.slug || !form.category) {
            showToast("error", "Vui lòng điền Tiêu đề, Slug và Category");
            return;
        }
        setSaving(true);
        try {
            if (editingId) {
                await updateWikiEntry(editingId, form, token as string);
                showToast("success", "Đã cập nhật entry!");
            } else {
                await createWikiEntry(form, token as string);
                showToast("success", "Đã tạo entry mới!");
            }
            setShowForm(false);
            load();
        } catch (e) {
            showToast("error", `Lỗi: ${(e as Error).message}`);
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(entry: WikiEntry) {
        if (!token) {
            showToast("error", "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
            return;
        }
        if (!confirm(`Xóa "${entry.title}"? Không thể khôi phục!`)) return;
        try {
            await deleteWikiEntry(entry.id, token as string);
            showToast("success", "Đã xóa entry!");
            load();
        } catch {
            showToast("error", "Xóa thất bại!");
        }
    }

    async function handleTranslateEntry(entry: WikiEntry) {
        if (!token) {
            showToast("error", "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
            return;
        }
        setTranslatingId(entry.id);
        try {
            const result = await translateAdminWikiEntry(entry.id, token);
            showToast(
                "success",
                `Đã dịch ${entry.title}: ${result.translated_locales?.length || 0} locale thành công, ${result.failed_translations?.length || 0} locale lỗi.`,
            );
        } catch (e) {
            showToast("error", `Lỗi dịch wiki: ${(e as Error).message}`);
        } finally {
            setTranslatingId(null);
        }
    }

    async function handleBatchTranslate() {
        if (!token) {
            showToast("error", "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
            return;
        }
        setBatchTranslating(true);
        setBatchResult(null);
        try {
            const result = await translateAdminWikiBatch(
                {
                    category: filter === "all" ? undefined : filter,
                    page,
                    limit: 50,
                    only_missing: batchOnlyMissing,
                },
                token,
            );
            setBatchResult({
                translated: result.translated_count,
                skipped: result.skipped_count,
                failed: result.failed_count,
                failedEntries: result.failed_entries || [],
            });
            showToast("success", `Batch wiki xong: dịch ${result.translated_count}, bỏ qua ${result.skipped_count}, lỗi ${result.failed_count}.`);
        } catch (e) {
            showToast("error", `Lỗi batch wiki: ${(e as Error).message}`);
        } finally {
            setBatchTranslating(false);
        }
    }

    return (
        <div className="relative">
            {/* Toast */}
            {toast && (
                <div className={`fixed top-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-mono shadow-lg
                    ${toast.type === "success" ? "bg-[#0d1f0d] border-green-700 text-green-400" : "bg-[#1f0d0d] border-red-700 text-red-400"}`}>
                    {toast.type === "success" ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                    {toast.msg}
                </div>
            )}

            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-mono text-gray-100 tracking-wide flex items-center gap-2">
                        <BookOpen size={20} className="text-green-500" /> CẨM NANG MẠT THẾ
                    </h1>
                    <p className="text-xs font-mono text-gray-600 mt-1">{total} entries · Quản lý Bách Khoa</p>
                </div>
                <button onClick={openNew} className="flex items-center gap-2 px-4 py-2 bg-green-900 hover:bg-green-800 border border-green-700 text-green-300 text-sm font-mono rounded transition-colors">
                    <PlusCircle size={16} /> Thêm mới
                </button>
            </div>

            {/* Category filter */}
            <div className="flex flex-wrap gap-2 mb-6">
                {["all", ...WIKI_CATEGORIES].map(cat => (
                    <button key={cat} onClick={() => setFilter(cat)}
                        className={`px-3 py-1 text-xs font-mono rounded border transition-colors
                            ${filter === cat ? "bg-green-900 border-green-600 text-green-300" : "bg-[#0d0d0d] border-gray-800 text-gray-500 hover:border-gray-600"}`}>
                        {cat === "all" ? "📋 Tất cả" : `${CATEGORY_ICONS[cat]} ${cat}`}
                    </button>
                ))}
            </div>

            <div className="mb-6 border border-gray-800 rounded-lg bg-[#0d0d0d] px-4 py-4">
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div>
                        <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest">Wiki Translate</div>
                        <p className="mt-1 text-xs font-mono text-gray-500">
                            Dịch AI cho các mục wiki của trang hiện tại. Backend gom tối đa 3 locale trong 1 request JSON.
                        </p>
                    </div>
                    <div className="flex flex-wrap items-center gap-3">
                        <label className="flex items-center gap-2 text-xs font-mono text-gray-400">
                            <input
                                type="checkbox"
                                checked={batchOnlyMissing}
                                onChange={(e) => setBatchOnlyMissing(e.target.checked)}
                                className="w-4 h-4 rounded bg-[#0d0d0d] border-gray-800 text-green-600 focus:ring-0 focus:ring-offset-0"
                            />
                            Chỉ dịch locale còn thiếu
                        </label>
                        <button
                            onClick={handleBatchTranslate}
                            disabled={batchTranslating || !token}
                            className="flex items-center gap-2 px-4 py-2 bg-[#111827] hover:bg-[#172033] border border-cyan-700 text-cyan-300 text-xs font-mono rounded transition-colors disabled:opacity-50"
                        >
                            {batchTranslating ? <Loader2 size={14} className="animate-spin" /> : <Languages size={14} />}
                            {batchTranslating ? "ĐANG DỊCH WIKI..." : "DỊCH AI TRANG HIỆN TẠI"}
                        </button>
                    </div>
                </div>
                {batchResult && (
                    <div className="mt-4 space-y-2">
                        <div className="rounded border border-gray-800 bg-[#081218] px-3 py-3 text-xs font-mono text-gray-200">
                            Dịch mới: {batchResult.translated} | Bỏ qua: {batchResult.skipped} | Lỗi: {batchResult.failed}
                        </div>
                        {batchResult.failedEntries.length > 0 && (
                            <div className="rounded border border-red-900/60 bg-[#1b0f0f] px-3 py-3">
                                <div className="text-xs font-mono text-red-300 uppercase tracking-widest mb-2">Chi tiết lỗi</div>
                                <div className="space-y-2">
                                    {batchResult.failedEntries.slice(0, 5).map((item) => (
                                        <div key={item.title} className="text-xs font-mono text-red-200 whitespace-pre-wrap">
                                            <div className="font-semibold">{item.title}</div>
                                            <div>{item.detail || "Không có chi tiết lỗi"}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Table */}
            {loading ? (
                <div className="text-center py-20 text-gray-600 font-mono">Đang tải dữ liệu...</div>
            ) : entries.length === 0 ? (
                <div className="text-center py-20 border border-dashed border-gray-800 rounded-lg">
                    <p className="text-gray-600 font-mono text-sm">Chưa có entry nào.</p>
                    <button onClick={openNew} className="mt-4 text-green-500 text-sm font-mono hover:text-green-400">+ Thêm entry đầu tiên</button>
                </div>
            ) : (
                <div className="space-y-2">
                    {entries.map(entry => (
                        <div key={entry.id} className="flex items-center justify-between bg-[#0d0d0d] border border-gray-800 rounded-lg px-4 py-3 group hover:border-gray-700 transition-colors">
                            <div className="flex items-center gap-3 min-w-0">
                                {entry.image_url && (
                                    // eslint-disable-next-line @next/next/no-img-element
                                    <img src={entry.image_url} alt={entry.title} className="w-10 h-10 rounded object-cover border border-gray-800" />
                                )}
                                <div className="min-w-0">
                                    <div className="font-mono text-sm text-gray-200 truncate flex items-center gap-2">
                                        {entry.is_main_character && <Star size={12} className="text-yellow-500 fill-yellow-500" />}
                                        {entry.title}
                                        <span className="text-[10px] text-gray-700 font-mono ml-1">#{entry.sort_order}</span>
                                    </div>
                                    <div className="text-xs text-gray-600 font-mono">{CATEGORY_ICONS[entry.category]} {entry.category} · /{entry.slug}</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 ml-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                    onClick={() => handleTranslateEntry(entry)}
                                    disabled={translatingId === entry.id || !token}
                                    className="p-2 text-gray-500 hover:text-cyan-400 transition-colors disabled:opacity-40"
                                    title="Dịch 3 ngôn ngữ"
                                >
                                    {translatingId === entry.id ? <Loader2 size={14} className="animate-spin" /> : <Languages size={14} />}
                                </button>
                                {entry.category === "Thế lực" && (
                                    <button onClick={async () => {
                                        try {
                                            const data = await getFactionHierarchy(entry.slug);
                                            setHierarchyMembers(data.members);
                                            setHierarchyEntry(entry);
                                        } catch { setHierarchyEntry(entry); setHierarchyMembers([]); }
                                    }} className="p-2 text-gray-500 hover:text-yellow-400 transition-colors" title="Sơ đồ tổ chức">
                                        <Users size={14} />
                                    </button>
                                )}
                                <button onClick={() => openEdit(entry)} className="p-2 text-gray-500 hover:text-green-400 transition-colors"><Edit2 size={14} /></button>
                                <button onClick={() => handleDelete(entry)} className="p-2 text-gray-500 hover:text-red-400 transition-colors"><Trash2 size={14} /></button>
                            </div>
                        </div>
                    ))}

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-center gap-4 mt-6">
                            <button 
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="px-3 py-1.5 bg-[#0d0d0d] border border-gray-800 text-gray-400 rounded hover:border-gray-600 disabled:opacity-30 disabled:cursor-not-allowed font-mono text-xs transition-colors"
                            >
                                ← Trước
                            </button>
                            <span className="text-xs font-mono text-gray-600 uppercase tracking-widest">
                                Trang {page} / {totalPages}
                            </span>
                            <button 
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                                className="px-3 py-1.5 bg-[#0d0d0d] border border-gray-800 text-gray-400 rounded hover:border-gray-600 disabled:opacity-30 disabled:cursor-not-allowed font-mono text-xs transition-colors"
                            >
                                Sau →
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Form Modal */}
            {showForm && (
                <div className="fixed inset-0 z-40 bg-black/80 flex items-center justify-center p-4" onClick={e => e.target === e.currentTarget && setShowForm(false)}>
                    <div className="bg-[#111] border border-gray-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between p-6 border-b border-gray-800">
                            <h2 className="font-mono text-gray-200 text-sm">{editingId ? "✏️ Sửa Entry" : "➕ Thêm Wiki Entry"}</h2>
                            <button onClick={() => setShowForm(false)} className="text-gray-600 hover:text-gray-400"><X size={18} /></button>
                        </div>

                        <div className="p-6 space-y-4">
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                {/* Category */}
                                <div>
                                    <label className="block text-xs font-mono text-gray-500 mb-1">Category *</label>
                                    <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                                        className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700">
                                        {WIKI_CATEGORIES.map(c => <option key={c} value={c}>{CATEGORY_ICONS[c]} {c}</option>)}
                                    </select>
                                </div>
                                {/* Sort Order */}
                                <div>
                                    <label className="block text-xs font-mono text-gray-500 mb-1">Thứ tự sắp xếp</label>
                                    <input type="number" value={form.sort_order}
                                        onChange={e => setForm(f => ({ ...f, sort_order: parseInt(e.target.value) || 0 }))}
                                        className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                                </div>
                                {/* Is Main Character */}
                                <div className="flex items-end pb-2">
                                    <label className="flex items-center gap-2 cursor-pointer group">
                                        <input type="checkbox" checked={form.is_main_character}
                                            onChange={e => setForm(f => ({ ...f, is_main_character: e.target.checked }))}
                                            className="w-4 h-4 rounded bg-[#0d0d0d] border-gray-800 text-green-600 focus:ring-0 focus:ring-offset-0" />
                                        <span className="text-xs font-mono text-gray-500 group-hover:text-gray-300 transition-colors">Nổi bật / Chính</span>
                                    </label>
                                </div>

                                {/* Title */}
                                <div className="md:col-span-3">
                                    <label className="block text-xs font-mono text-gray-500 mb-1">Tiêu đề *</label>
                                    <input value={form.title}
                                        onChange={e => setForm(f => ({ ...f, title: e.target.value, slug: f.slug || toSlug(e.target.value) }))}
                                        placeholder="VD: Zombie Cấp 1 - Hunter" className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                                </div>
                            </div>

                            {/* Slug */}
                            <div>
                                <label className="block text-xs font-mono text-gray-500 mb-1">Slug (URL) *</label>
                                <input value={form.slug} onChange={e => setForm(f => ({ ...f, slug: e.target.value }))}
                                    placeholder="zombie-cap-1-hunter" className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                                <p className="text-xs text-gray-700 font-mono mt-1">URL: /wiki/{form.slug || "..."}</p>
                            </div>

                            {/* Image URL */}
                            <div>
                                <label className="block text-xs font-mono text-gray-500 mb-1">Ảnh Bìa (R2 URL)</label>
                                <div className="flex gap-2">
                                    <input value={form.image_url || ""} onChange={e => setForm(f => ({ ...f, image_url: e.target.value }))}
                                        placeholder="https://pub-xxx.r2.dev/wiki/zombie-cap-1.jpg" className="flex-1 bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                                    <label className={`flex items-center justify-center px-4 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 rounded cursor-pointer transition-colors ${isUploadingImg ? "opacity-50 cursor-not-allowed" : ""}`} title="Tải ảnh lên R2">
                                        {isUploadingImg ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
                                        <input type="file" accept="image/*" className="hidden" disabled={isUploadingImg} onChange={async (e) => {
                                            const file = e.target.files?.[0];
                                            if (file) {
                                                setIsUploadingImg(true);
                                                try {
                                                    if (!token) throw new Error("Missing access token");
                                                    const url = await uploadImageR2(file, token as string);
                                                    setForm(f => ({ ...f, image_url: url }));
                                                    showToast("success", "Tải ảnh bìa thành công!");
                                                } catch (err) {
                                                    showToast("error", "Lỗi tải ảnh bìa");
                                                } finally {
                                                    setIsUploadingImg(false);
                                                }
                                            }
                                        }} />
                                    </label>
                                </div>
                            </div>

                            {/* Tags */}
                            <div>
                                <label className="block text-xs font-mono text-gray-500 mb-1">Tags (phân cách bởi dấu phẩy)</label>
                                <input value={(form.tags || []).join(", ")}
                                    onChange={e => setForm(f => ({ ...f, tags: e.target.value.split(",").map(t => t.trim()).filter(Boolean) }))}
                                    placeholder="Zombie, Đột biến, Nguy hiểm" className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                            </div>

                            {/* Summary */}
                            <div>
                                <label className="block text-xs font-mono text-gray-500 mb-1">Tóm tắt ngắn</label>
                                <textarea value={form.summary || ""} onChange={e => setForm(f => ({ ...f, summary: e.target.value }))}
                                    rows={2} placeholder="Mô tả 1-2 câu để hiển thị trong danh sách..."
                                    className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700 resize-none" />
                            </div>

                            {/* Content */}
                            <div>
                                <label className="block text-xs font-mono text-gray-500 mb-1">Nội dung đầy đủ (Sử dụng Editor)</label>
                                <RichTextEditor
                                    content={form.content || ""}
                                    onChange={(html) => setForm(f => ({ ...f, content: html }))}
                                    adminToken={token || undefined}
                                />
                            </div>

                            <button onClick={handleSave} disabled={saving || isUploadingImg}
                                className="w-full flex items-center justify-center gap-2 py-3 bg-green-900 hover:bg-green-800 border border-green-700 text-green-300 text-sm font-mono rounded transition-colors disabled:opacity-50">
                                {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
                                {saving ? "Đang lưu..." : "Lưu Entry"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Faction Hierarchy Modal */}
            {hierarchyEntry && (
                <FactionHierarchyEditor
                    factionId={hierarchyEntry.id}
                    factionTitle={hierarchyEntry.title}
                    members={hierarchyMembers}
                    adminToken={token || ""}
                    onClose={() => setHierarchyEntry(null)}
                    onRefresh={async () => {
                        try {
                            const data = await getFactionHierarchy(hierarchyEntry.slug);
                            setHierarchyMembers(data.members);
                        } catch {}
                    }}
                />
            )}
        </div>
    );
}
