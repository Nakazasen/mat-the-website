"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Users } from "lucide-react";
import { FactionMember, getFactionHierarchy } from "@/lib/api";

/* ── helpers ── */

interface TreeNode extends FactionMember {
    children: TreeNode[];
}

/**
 * Build a proper tree when parent_id is available.
 * Fallback: group flat members by rank_level into tiers.
 */
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

/**
 * Check if the data has meaningful parent_id relationships.
 * If every node is a root → no tree structure was defined.
 */
function hasTreeStructure(members: FactionMember[]): boolean {
    return members.some(m => m.parent_id != null);
}

/**
 * Group flat members into tiers by rank_level.
 * Each tier is rendered as a separate row.
 */
function groupByRank(members: FactionMember[]): Map<number, FactionMember[]> {
    const tiers = new Map<number, FactionMember[]>();
    const sorted = [...members].sort((a, b) => a.rank_level - b.rank_level || a.sort_order - b.sort_order);
    for (const m of sorted) {
        const list = tiers.get(m.rank_level) || [];
        list.push(m);
        tiers.set(m.rank_level, list);
    }
    return tiers;
}

/* ── avatar sizing by rank ── */

function getAvatarStyle(rank: number) {
    if (rank === 0) return { size: "w-20 h-20", border: "border-[3px] border-yellow-500 shadow-lg shadow-yellow-500/20", icon: 28 };
    if (rank === 1) return { size: "w-14 h-14", border: "border-2 border-green-500 shadow-md shadow-green-500/10", icon: 20 };
    if (rank === 2) return { size: "w-12 h-12", border: "border-2 border-cyan-500 shadow-md shadow-cyan-500/10", icon: 16 };
    return { size: "w-10 h-10", border: "border-2 border-gray-700", icon: 14 };
}

function getRoleColor(rank: number): string {
    if (rank === 0) return "text-yellow-400";
    if (rank === 1) return "text-green-400";
    if (rank === 2) return "text-cyan-400";
    return "text-gray-400";
}

/* ── card component ── */

function MemberCard({ member }: { member: FactionMember }) {
    const style = getAvatarStyle(member.rank_level);
    const roleColor = getRoleColor(member.rank_level);

    const card = (
        <div className={`flex flex-col items-center text-center group transition-all duration-200 ${member.character_slug ? "cursor-pointer" : ""}`}>
            {member.character_image ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                    src={member.character_image}
                    alt={member.character_name || ""}
                    className={`${style.size} rounded-full object-cover ${style.border} transition-transform duration-200 group-hover:scale-110`}
                />
            ) : (
                <div className={`${style.size} rounded-full bg-gray-900 flex items-center justify-center ${style.border}`}>
                    <Users size={style.icon} className="text-gray-600" />
                </div>
            )}
            <p className={`mt-2 text-xs font-mono font-semibold ${member.character_name ? "text-gray-200 group-hover:text-white" : "text-gray-600"} truncate max-w-[120px]`}>
                {member.character_name || "—"}
            </p>
            <p className={`text-[10px] font-mono ${roleColor} truncate max-w-[120px]`}>
                {member.role_title}
            </p>
            {member.division && (
                <span className="mt-0.5 text-[9px] font-mono text-gray-600 bg-gray-900 px-1.5 py-0.5 rounded">
                    {member.division}
                </span>
            )}
        </div>
    );

    if (member.character_slug) {
        return <Link href={`/wiki/${member.character_slug}`}>{card}</Link>;
    }
    return card;
}

/* ── connector lines ── */

function VerticalLine() {
    return <div className="w-px h-6 bg-gray-800 mx-auto" />;
}

/* ── tree-based render (when parent_id is used) ── */

function TreeNodeView({ node, depth }: { node: TreeNode; depth: number }) {
    return (
        <div className="flex flex-col items-center">
            <MemberCard member={node} />
            {node.children.length > 0 && (
                <>
                    <VerticalLine />
                    {/* Horizontal connector for multiple children */}
                    {node.children.length > 1 && (
                        <div className="relative w-full flex justify-center">
                            <div className="absolute top-0 h-px bg-gray-800"
                                style={{ width: `${Math.min(node.children.length * 140, 600)}px` }} />
                        </div>
                    )}
                    <div className="flex flex-wrap justify-center gap-6 md:gap-8 mt-1">
                        {node.children.map(child => (
                            <TreeNodeView key={child.id} node={child} depth={depth + 1} />
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}

/* ── tier-based render (fallback when no parent_id) ── */

function TierView({ tiers }: { tiers: Map<number, FactionMember[]> }) {
    const ranks = Array.from(tiers.keys()).sort((a, b) => a - b);

    return (
        <div className="flex flex-col items-center gap-2">
            {ranks.map((rank, idx) => {
                const members = tiers.get(rank)!;
                return (
                    <div key={rank}>
                        {/* Connector between tiers */}
                        {idx > 0 && <VerticalLine />}

                        {/* Tier row */}
                        <div className="flex flex-wrap justify-center gap-6 md:gap-8">
                            {members.map(m => (
                                <MemberCard key={m.id} member={m} />
                            ))}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

/* ── main component ── */

interface Props {
    slug: string;
}

export default function FactionOrgChart({ slug }: Props) {
    const [members, setMembers] = useState<FactionMember[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getFactionHierarchy(slug).then(data => {
            setMembers(data.members);
        }).catch(() => {}).finally(() => setLoading(false));
    }, [slug]);

    if (loading) {
        return (
            <div className="mt-8 p-6 border border-gray-800 rounded-xl text-center">
                <p className="text-gray-600 font-mono text-xs">Đang tải sơ đồ tổ chức...</p>
            </div>
        );
    }

    if (members.length === 0) return null;

    const useTree = hasTreeStructure(members);

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
                {useTree ? (
                    /* Tree mode: parent_id defines hierarchy */
                    <div className="flex flex-wrap justify-center gap-6 md:gap-8">
                        {buildTree(members).map(root => (
                            <TreeNodeView key={root.id} node={root} depth={0} />
                        ))}
                    </div>
                ) : (
                    /* Tier mode: group by rank_level */
                    <TierView tiers={groupByRank(members)} />
                )}
            </div>
        </div>
    );
}
