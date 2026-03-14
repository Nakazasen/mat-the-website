"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Users } from "lucide-react";
import { FactionMember, getFactionHierarchy } from "@/lib/api";

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

    const sortChildren = (nodes: TreeNode[]) => {
        nodes.sort((a, b) => a.sort_order - b.sort_order);
        nodes.forEach(n => sortChildren(n.children));
    };
    sortChildren(roots);
    return roots;
}

function getAvatarSize(rank: number): { container: string; img: string; border: string } {
    if (rank === 0) return { container: "w-20 h-20", img: "w-20 h-20", border: "border-[3px] border-yellow-500 shadow-lg shadow-yellow-500/20" };
    if (rank <= 2) return { container: "w-14 h-14", img: "w-14 h-14", border: "border-2 border-green-500 shadow-md shadow-green-500/10" };
    return { container: "w-10 h-10", img: "w-10 h-10", border: "border-2 border-gray-700" };
}

function getRoleColor(rank: number): string {
    if (rank === 0) return "text-yellow-400";
    if (rank <= 2) return "text-green-400";
    return "text-gray-400";
}

function MemberCard({ node }: { node: TreeNode }) {
    const size = getAvatarSize(node.rank_level);
    const roleColor = getRoleColor(node.rank_level);

    const content = (
        <div className={`flex flex-col items-center text-center group transition-all duration-200 ${node.character_slug ? "cursor-pointer" : ""}`}>
            {/* Avatar */}
            {node.character_image ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                    src={node.character_image}
                    alt={node.character_name || ""}
                    className={`${size.img} rounded-full object-cover ${size.border} transition-transform duration-200 group-hover:scale-110`}
                />
            ) : (
                <div className={`${size.container} rounded-full bg-gray-900 flex items-center justify-center ${size.border}`}>
                    <Users size={node.rank_level === 0 ? 28 : node.rank_level <= 2 ? 20 : 14} className="text-gray-600" />
                </div>
            )}

            {/* Name */}
            <p className={`mt-2 text-xs font-mono font-semibold ${node.character_name ? "text-gray-200 group-hover:text-white" : "text-gray-600"} truncate max-w-[120px]`}>
                {node.character_name || "—"}
            </p>

            {/* Role */}
            <p className={`text-[10px] font-mono ${roleColor} truncate max-w-[120px]`}>
                {node.role_title}
            </p>

            {/* Division badge */}
            {node.division && (
                <span className="mt-0.5 text-[9px] font-mono text-gray-600 bg-gray-900 px-1.5 py-0.5 rounded">
                    {node.division}
                </span>
            )}
        </div>
    );

    if (node.character_slug) {
        return <Link href={`/wiki/${node.character_slug}`}>{content}</Link>;
    }
    return content;
}

function NodeGroup({ nodes, depth }: { nodes: TreeNode[]; depth: number }) {
    if (nodes.length === 0) return null;

    return (
        <div className="flex flex-col items-center gap-6">
            {/* Current level nodes */}
            <div className="flex flex-wrap justify-center gap-6 md:gap-8">
                {nodes.map(node => (
                    <div key={node.id} className="flex flex-col items-center">
                        <MemberCard node={node} />

                        {/* Connector line down */}
                        {node.children.length > 0 && (
                            <div className="w-px h-6 bg-gray-800 mt-2" />
                        )}

                        {/* Children */}
                        {node.children.length > 0 && (
                            <div className="relative">
                                {/* Horizontal line connecting children */}
                                {node.children.length > 1 && (
                                    <div className="absolute top-0 left-1/2 -translate-x-1/2 h-px bg-gray-800"
                                        style={{ width: `${Math.max(node.children.length - 1, 1) * 140}px` }} />
                                )}
                                <NodeGroup nodes={node.children} depth={depth + 1} />
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

interface Props {
    slug: string;
}

export default function FactionOrgChart({ slug }: Props) {
    const [members, setMembers] = useState<FactionMember[]>([]);
    const [loading, setLoading] = useState(true);
    const [factionTitle, setFactionTitle] = useState("");

    useEffect(() => {
        getFactionHierarchy(slug).then(data => {
            setMembers(data.members);
            setFactionTitle(data.faction_title);
        }).catch(() => {}).finally(() => setLoading(false));
    }, [slug]);

    const tree = buildTree(members);

    if (loading) {
        return (
            <div className="mt-8 p-6 border border-gray-800 rounded-xl text-center">
                <p className="text-gray-600 font-mono text-xs">Đang tải sơ đồ tổ chức...</p>
            </div>
        );
    }

    if (members.length === 0) return null; // Don't show section if empty

    return (
        <div className="mt-10">
            {/* Section header */}
            <div className="flex items-center gap-3 mb-6">
                <div className="flex-1 h-px bg-gray-800" />
                <h2 className="text-xs font-mono text-green-600 tracking-widest flex items-center gap-2">
                    <Users size={14} /> SƠ ĐỒ TỔ CHỨC
                </h2>
                <div className="flex-1 h-px bg-gray-800" />
            </div>

            {/* Chart */}
            <div className="p-6 bg-[#0a0a0a] border border-gray-800 rounded-xl overflow-x-auto">
                <NodeGroup nodes={tree} depth={0} />
            </div>
        </div>
    );
}
