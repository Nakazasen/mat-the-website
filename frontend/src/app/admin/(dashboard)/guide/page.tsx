"use client";

import { useEffect, useState } from "react";
import { FileText, Save, BookOpen, ShieldCheck, Loader2 } from "lucide-react";
import { createAdminClient } from "@/lib/supabase-admin";
import { getAdminGuide, updateGuide } from "@/lib/api";
import dynamic from "next/dynamic";

const RichTextEditor = dynamic(() => import("@/components/Editor"), { ssr: false });

type TabId = "reader-guide" | "admin-sop";

const TABS: { id: TabId; label: string; icon: typeof BookOpen; description: string }[] = [
    { id: "reader-guide", label: "Hướng Dẫn Độc Giả", icon: BookOpen, description: "Nội dung này sẽ hiển thị công khai tại trang /huong-dan" },
    { id: "admin-sop", label: "SOP Nội Bộ", icon: ShieldCheck, description: "Chỉ Admin/Editor mới xem được (không công khai)" },
];

export default function GuidePage() {
    const [activeTab, setActiveTab] = useState<TabId>("reader-guide");
    const [content, setContent] = useState("");
    const [title, setTitle] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [token, setToken] = useState(process.env.NEXT_PUBLIC_ADMIN_TOKEN || "mat-the-admin-2026");

    useEffect(() => {
        const supabase = createAdminClient();
        if (!supabase) return;
        supabase.auth.getSession().then(({ data }) => {
            if (data.session?.access_token) {
                setToken(data.session.access_token);
            }
        });
    }, []);

    useEffect(() => {
        if (!token) return;
        setLoading(true);
        setSaved(false);
        getAdminGuide(activeTab, token)
            .then((data) => {
                setContent(data.content || "");
                setTitle(data.title || "");
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [activeTab, token]);

    const handleSave = async () => {
        if (!token) return;
        setSaving(true);
        try {
            await updateGuide(activeTab, { title, content }, token);
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch (e) {
            console.error(e);
            alert("Lỗi khi lưu hướng dẫn!");
        } finally {
            setSaving(false);
        }
    };

    const activeTabInfo = TABS.find((t) => t.id === activeTab)!;

    return (
        <div>
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="font-biohazard text-2xl tracking-wider text-green-400 flex items-center gap-3">
                        <FileText size={22} />
                        HƯỚNG DẪN & SOP
                    </h1>
                    <p className="text-gray-500 text-xs font-mono mt-1">Soạn thảo tài liệu hướng dẫn sử dụng</p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={saving || loading}
                    className="flex items-center gap-2 px-5 py-2.5 bg-green-900/40 text-green-400 border border-green-800/50 rounded font-mono text-xs tracking-wider hover:bg-green-900/60 transition-all disabled:opacity-50"
                >
                    {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                    {saving ? "ĐANG LƯU..." : saved ? "✓ ĐÃ LƯU!" : "LƯU NỘI DUNG"}
                </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 mb-6">
                {TABS.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2.5 rounded font-mono text-xs tracking-wider transition-all border ${activeTab === tab.id
                            ? "bg-green-900/30 text-green-400 border-green-800/50"
                            : "text-gray-500 border-gray-800 hover:text-gray-300 hover:border-gray-700"
                            }`}
                    >
                        <tab.icon size={14} />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Scope info */}
            <div className={`mb-4 px-4 py-2.5 rounded border text-[11px] font-mono ${activeTab === "admin-sop"
                ? "bg-yellow-950/30 border-yellow-800/30 text-yellow-500"
                : "bg-blue-950/30 border-blue-800/30 text-blue-400"
                }`}>
                {activeTab === "admin-sop" ? "🔒" : "🌐"} {activeTabInfo.description}
            </div>

            {/* Title input */}
            <input
                type="text"
                placeholder="TIÊU ĐỀ TRANG HƯỚNG DẪN"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-[#0d1117] border border-gray-700 rounded px-4 py-2.5 text-sm font-mono text-gray-200 outline-none focus:border-green-600 transition-colors mb-4 placeholder:text-gray-600"
            />

            {/* Editor */}
            {loading ? (
                <div className="flex items-center justify-center py-20 bg-[#0d1117] rounded border border-gray-700">
                    <div className="flex flex-col items-center gap-3">
                        <div className="w-6 h-6 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-gray-500 text-xs font-mono">ĐANG TẢI NỘI DUNG...</span>
                    </div>
                </div>
            ) : (
                <RichTextEditor
                    content={content}
                    onChange={setContent}
                    placeholder="Bắt đầu soạn thảo hướng dẫn..."
                    adminToken={token}
                />
            )}
        </div>
    );
}
