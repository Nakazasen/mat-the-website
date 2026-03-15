"use client";

import { useState, useEffect, useCallback } from "react";
import { X, Plus, Trash2, Edit2, Save, Loader2, Users, ChevronRight, Search } from "lucide-react";
import {
    FactionMember, FactionMemberIn, WikiEntry,
    getWikiEntries, addFactionMember, updateFactionMember, deleteFactionMember
} from "@/lib/api";

interface Props {
    factionId: string;
    factionTitle: string;
    members: FactionMember[];
    adminToken: string;
    onClose: () => void;
    onRefresh: () => void;
}

interface TreeNode extends FactionMember {
    children: TreeNode[];
}

function buildTree(members: FactionMember[]): TreeNode[] {
    const map: Record<string, TreeNode> = {};
    const roots: TreeNode[] = [];

    members.forEach(m => { map[m.id] = { ...m, children: [] }; });
    members.forEach(m => {
        const node = map[m.id];
        if (m.parent_id && map[m.parent_id]) {
            map[m.parent_id].children.push(node);
        } else {
            roots.push(node);
        }
    });

    // Sort children by sort_order
    const sortChildren = (nodes: TreeNode[]) => {
        nodes.sort((a, b) => a.sort_order - b.sort_order);
        nodes.forEach(n => sortChildren(n.children));
    };
    sortChildren(roots);
    return roots;
}

export default function FactionHierarchyEditor({ factionId, factionTitle, members: initialMembers, adminToken, onClose, onRefresh }: Props) {
    const [members, setMembers] = useState<FactionMember[]>(initialMembers);
    const [characters, setCharacters] = useState<WikiEntry[]>([]);
    const [showAddForm, setShowAddForm] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);
    const [searchChar, setSearchChar] = useState("");

    const [form, setForm] = useState<FactionMemberIn>({
        character_id: undefined,
        parent_id: null,
        role_title: "",
        division: "",
        rank_level: 0,
        sort_order: 0,
    });

    // Load characters for picker
    useEffect(() => {
        getWikiEntries("Nhân vật", undefined, 1, 1000).then(res => setCharacters(res.entries)).catch(() => {});
    }, []);

    const tree = buildTree(members);

    const filteredChars = characters.filter(c =>
        c.title.toLowerCase().includes(searchChar.toLowerCase())
    );

    function openAdd(parentId: string | null = null, parentRank: number = -1) {
        setForm({
            character_id: undefined,
            parent_id: parentId,
            role_title: "",
            division: "",
            rank_level: parentRank + 1,
            sort_order: 0,
        });
        setEditingId(null);
        setShowAddForm(true);
        setSearchChar("");
    }

    function openEdit(member: FactionMember) {
        setForm({
            character_id: member.character_id || undefined,
            parent_id: member.parent_id || null,
            role_title: member.role_title,
            division: member.division || "",
            rank_level: member.rank_level,
            sort_order: member.sort_order,
        });
        setEditingId(member.id);
        setShowAddForm(true);
        setSearchChar("");
    }

    async function handleSave() {
        if (!form.role_title.trim()) return;
        setSaving(true);
        try {
            if (editingId) {
                const updated = await updateFactionMember(editingId, form, adminToken);
                setMembers(prev => prev.map(m => m.id === editingId ? { ...m, ...updated } : m));
            } else {
                const created = await addFactionMember(factionId, form, adminToken);
                // Enrich with character info
                const char = characters.find(c => c.id === form.character_id);
                setMembers(prev => [...prev, {
                    ...created,
                    character_name: char?.title,
                    character_slug: char?.slug,
                    character_image: char?.image_url,
                }]);
            }
            setShowAddForm(false);
            onRefresh();
        } catch {
            // silently fail
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(id: string) {
        if (!confirm("Xóa thành viên này? (Các node con sẽ được tách ra)")) return;
        try {
            await deleteFactionMember(id, adminToken);
            // Detach children in local state
            setMembers(prev => prev
                .filter(m => m.id !== id)
                .map(m => m.parent_id === id ? { ...m, parent_id: undefined } : m)
            );
            onRefresh();
        } catch {
            // silently fail
        }
    }

    function renderNode(node: TreeNode, depth: number = 0) {
        const rankColors = ["text-yellow-400", "text-green-400", "text-cyan-400"];
        const rankColor = rankColors[Math.min(node.rank_level, rankColors.length - 1)] || "text-gray-500";

        return (
            <div key={node.id} style={{ paddingLeft: depth * 24 }}>
                <div className="flex items-center gap-2 py-2 px-3 rounded-lg hover:bg-[#1a1a1a] group transition-colors">
                    {/* Connector */}
                    {depth > 0 && <ChevronRight size={12} className="text-gray-700 -ml-4" />}

                    {/* Avatar */}
                    {node.character_image ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={node.character_image} alt="" className={`w-8 h-8 rounded-full object-cover border-2 ${
                            node.rank_level === 0 ? "border-yellow-500" : node.rank_level === 1 ? "border-green-600" : node.rank_level === 2 ? "border-cyan-600" : "border-gray-700"
                        }`} />
                    ) : (
                        <div className={`w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center border-2 ${
                            node.rank_level === 0 ? "border-yellow-500" : node.rank_level === 1 ? "border-green-600" : node.rank_level === 2 ? "border-cyan-600" : "border-gray-700"
                        }`}>
                            <Users size={14} className="text-gray-600" />
                        </div>
                    )}

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                            <span className={`text-xs font-mono font-bold ${rankColor}`}>
                                {node.role_title || "Chưa đặt tên"}
                            </span>
                            {node.division && (
                                <span className="text-[10px] font-mono text-gray-600 bg-gray-900 px-1.5 py-0.5 rounded">
                                    {node.division}
                                </span>
                            )}
                        </div>
                        <div className="text-[11px] font-mono text-gray-500 truncate">
                            {node.character_name || "Chưa gán nhân vật"}
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => openAdd(node.id, node.rank_level)} className="p-1.5 text-gray-600 hover:text-green-400" title="Thêm con">
                            <Plus size={12} />
                        </button>
                        <button onClick={() => openEdit(node)} className="p-1.5 text-gray-600 hover:text-blue-400" title="Sửa">
                            <Edit2 size={12} />
                        </button>
                        <button onClick={() => handleDelete(node.id)} className="p-1.5 text-gray-600 hover:text-red-400" title="Xóa">
                            <Trash2 size={12} />
                        </button>
                    </div>
                </div>

                {/* Children */}
                {node.children.map(child => renderNode(child, depth + 1))}
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4" onClick={e => e.target === e.currentTarget && onClose()}>
            <div className="bg-[#111] border border-gray-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="flex items-center justify-between p-5 border-b border-gray-800">
                    <div>
                        <h2 className="font-mono text-gray-200 text-sm flex items-center gap-2">
                            <Users size={16} className="text-yellow-500" /> Sơ đồ tổ chức
                        </h2>
                        <p className="text-xs font-mono text-gray-600 mt-1">{factionTitle}</p>
                    </div>
                    <button onClick={onClose} className="text-gray-600 hover:text-gray-400"><X size={18} /></button>
                </div>

                {/* Tree view */}
                <div className="p-5">
                    {tree.length === 0 ? (
                        <div className="text-center py-10 border border-dashed border-gray-800 rounded-lg">
                            <p className="text-gray-600 font-mono text-sm">Chưa có thành viên nào.</p>
                        </div>
                    ) : (
                        <div className="space-y-0.5">
                            {tree.map(node => renderNode(node))}
                        </div>
                    )}

                    {/* Add root button */}
                    <button onClick={() => openAdd(null, -1)}
                        className="mt-4 w-full flex items-center justify-center gap-2 py-2.5 border border-dashed border-gray-700 hover:border-green-700 text-gray-500 hover:text-green-400 text-xs font-mono rounded-lg transition-colors">
                        <Plus size={14} /> Thêm thành viên
                    </button>
                </div>

                {/* Add/Edit Form */}
                {showAddForm && (
                    <div className="border-t border-gray-800 p-5 space-y-3">
                        <h3 className="text-xs font-mono text-gray-400 tracking-wider">
                            {editingId ? "✏️ SỬA THÀNH VIÊN" : "➕ THÊM THÀNH VIÊN"}
                        </h3>

                        <div className="grid grid-cols-2 gap-3">
                            {/* Role title */}
                            <div>
                                <label className="block text-[10px] font-mono text-gray-600 mb-1">Chức danh *</label>
                                <input value={form.role_title} onChange={e => setForm(f => ({ ...f, role_title: e.target.value }))}
                                    placeholder="VD: Người sáng lập, Trưởng khối..."
                                    className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                            </div>
                            {/* Division */}
                            <div>
                                <label className="block text-[10px] font-mono text-gray-600 mb-1">Khối/Bộ phận</label>
                                <input value={form.division || ""} onChange={e => setForm(f => ({ ...f, division: e.target.value }))}
                                    placeholder="VD: Quân đội, Dân sự..."
                                    className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            {/* Rank level */}
                            <div>
                                <label className="block text-[10px] font-mono text-gray-600 mb-1">Cấp bậc (0 = đỉnh)</label>
                                <input type="number" min={0} value={form.rank_level}
                                    onChange={e => setForm(f => ({ ...f, rank_level: parseInt(e.target.value) || 0 }))}
                                    className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                            </div>
                            {/* Sort order */}
                            <div>
                                <label className="block text-[10px] font-mono text-gray-600 mb-1">Thứ tự sắp xếp</label>
                                <input type="number" min={0} value={form.sort_order}
                                    onChange={e => setForm(f => ({ ...f, sort_order: parseInt(e.target.value) || 0 }))}
                                    className="w-full bg-[#0d0d0d] border border-gray-800 rounded px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                            </div>
                        </div>

                        {/* Character picker */}
                        <div>
                            <label className="block text-[10px] font-mono text-gray-600 mb-1">Gán nhân vật</label>
                            <div className="relative">
                                <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600" />
                                <input value={searchChar} onChange={e => setSearchChar(e.target.value)}
                                    placeholder="Tìm nhân vật..."
                                    className="w-full bg-[#0d0d0d] border border-gray-800 rounded pl-8 pr-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-green-700" />
                            </div>
                            {searchChar && (
                                <div className="mt-1 max-h-32 overflow-y-auto bg-[#0d0d0d] border border-gray-800 rounded">
                                    {filteredChars.map(c => (
                                        <button key={c.id} onClick={() => { setForm(f => ({ ...f, character_id: c.id })); setSearchChar(""); }}
                                            className={`w-full flex items-center gap-2 px-3 py-1.5 text-left hover:bg-gray-800 transition-colors ${form.character_id === c.id ? "bg-green-950/30" : ""}`}>
                                            {c.image_url ? (
                                                // eslint-disable-next-line @next/next/no-img-element
                                                <img src={c.image_url} alt="" className="w-5 h-5 rounded-full object-cover" />
                                            ) : (
                                                <div className="w-5 h-5 rounded-full bg-gray-800" />
                                            )}
                                            <span className="text-xs font-mono text-gray-300">{c.title}</span>
                                        </button>
                                    ))}
                                    {filteredChars.length === 0 && (
                                        <p className="px-3 py-2 text-xs font-mono text-gray-600">Không tìm thấy</p>
                                    )}
                                </div>
                            )}
                            {/* Selected character display */}
                            {form.character_id && (
                                <div className="mt-1 flex items-center gap-2 px-2 py-1 bg-green-950/20 border border-green-900 rounded text-xs font-mono text-green-400">
                                    ✓ {characters.find(c => c.id === form.character_id)?.title || "Đã chọn"}
                                    <button onClick={() => setForm(f => ({ ...f, character_id: undefined }))} className="ml-auto text-gray-600 hover:text-red-400">
                                        <X size={10} />
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2">
                            <button onClick={handleSave} disabled={saving || !form.role_title.trim()}
                                className="flex-1 flex items-center justify-center gap-2 py-2 bg-green-900 hover:bg-green-800 border border-green-700 text-green-300 text-xs font-mono rounded transition-colors disabled:opacity-50">
                                {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                                {saving ? "Đang lưu..." : "Lưu"}
                            </button>
                            <button onClick={() => setShowAddForm(false)}
                                className="px-4 py-2 border border-gray-800 text-gray-500 text-xs font-mono rounded hover:border-gray-700 transition-colors">
                                Hủy
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
