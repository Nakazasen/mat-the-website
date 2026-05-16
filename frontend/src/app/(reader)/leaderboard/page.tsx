import Link from "next/link";
import { ArrowLeft, Trophy, Skull, ShieldCheck, Flame, Medal } from "lucide-react";
import { createAdminClient } from "@/lib/supabase-admin";

export const dynamic = "force-dynamic";
export const revalidate = 0;
export const fetchCache = "force-no-store";

// Map ranks based on EXP, syncing with profile/page.tsx
const getRankInfo = (exp: number) => {
    if (exp >= 5000) return { title: "Huy hiệu Hi Vọng Bậc S", color: "text-yellow-400", border: "border-yellow-500/50", glow: "shadow-[0_0_15px_rgba(250,204,21,0.3)]" };
    if (exp >= 2000) return { title: "Huy hiệu Hi Vọng Bậc A", color: "text-purple-400", border: "border-purple-500/50", glow: "" };
    if (exp >= 1000) return { title: "Huy hiệu Hi Vọng Bậc B", color: "text-blue-400", border: "border-blue-500/50", glow: "" };
    if (exp >= 500) return { title: "Huy hiệu Hi Vọng Bậc C", color: "text-green-400", border: "border-green-500/50", glow: "" };
    return { title: "Huy hiệu Hi Vọng Bậc D", color: "text-amber-700", border: "border-amber-900/50", glow: "" };
};

export default async function LeaderboardPage() {
    const supabase = createAdminClient();
    let topUsers: any[] = [];

    if (supabase) {
        // Fetch top 10 users using RPC to securely join auth.users and profiles
        const { data } = await supabase.rpc('get_leaderboard');

        if (data && Array.isArray(data)) {
            topUsers = data;
        }
    }

    return (
        <div className="min-h-screen bg-black">
            {/* Header */}
            <div className="max-w-3xl mx-auto px-4 pt-6 pb-2">
                <Link href="/" className="inline-flex items-center gap-2 text-sm text-ash-400 hover:text-toxic-green-DEFAULT transition-colors font-mono">
                    <ArrowLeft size={14} />
                    QUAY VỀ TRẤN HI VỌNG
                </Link>
            </div>

            <div className="max-w-3xl mx-auto px-4 py-8">
                {/* Title Section */}
                <div className="text-center mb-12 relative">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-toxic-green-DEFAULT/10 blur-[50px] pointer-events-none" />
                    <Trophy size={48} className="mx-auto mb-4 text-toxic-green-DEFAULT" />
                    <h1 className="font-biohazard text-4xl sm:text-5xl text-white tracking-[0.2em] mb-2 uppercase">BẢNG PHONG THẦN</h1>
                    <p className="text-ash-400 font-mono tracking-widest text-sm">TOP 10 HUYỀN THOẠI TRẤN HI VỌNG</p>
                </div>

                {/* Leaderboard List */}
                <div className="space-y-4">
                    {topUsers.length === 0 ? (
                        <div className="text-center py-12 border border-dashed border-ash-700/50 rounded-xl bg-ash-900/50">
                            <Skull size={32} className="mx-auto mb-3 text-ash-600" />
                            <p className="font-mono text-ash-500 text-sm tracking-widest leading-relaxed px-4">ĐANG THU THẬP DỮ LIỆU SINH TỒN...</p>
                        </div>
                    ) : (
                        topUsers.map((user, index) => {
                            const rank = getRankInfo(user.exp || 0);
                            const isTop3 = index < 3;

                            return (
                                <div
                                    key={user.id}
                                    className={`relative flex items-center gap-4 p-4 sm:p-5 rounded-xl border bg-ash-900/40 backdrop-blur-sm transition-all hover:bg-ash-800/60
                                        ${isTop3 ? 'border-toxic-green-DEFAULT/30 bg-gradient-to-r from-toxic-green-DEFAULT/5 to-transparent' : 'border-ash-800'}
                                    `}
                                >
                                    {/* Rank Number */}
                                    <div className={`w-10 text-center font-biohazard text-2xl flex-shrink-0
                                        ${index === 0 ? 'text-yellow-400 text-3xl drop-shadow-[0_0_8px_rgba(250,204,21,0.5)]' : ''}
                                        ${index === 1 ? 'text-gray-300' : ''}
                                        ${index === 2 ? 'text-amber-700' : ''}
                                        ${index > 2 ? 'text-ash-600' : ''}
                                    `}>
                                        #{index + 1}
                                    </div>

                                    {/* Avatar */}
                                    <div className={`relative w-12 h-12 sm:w-14 sm:h-14 rounded-full border-2 flex-shrink-0 bg-ash-950
                                        ${index === 0 ? 'border-blood-red-bright shadow-[0_0_20px_rgba(255,51,51,0.6)]' :
                                            index === 1 ? 'border-toxic-green-DEFAULT shadow-[0_0_20px_rgba(57,255,20,0.5)]' :
                                                index === 2 ? 'border-blue-400 shadow-[0_0_20px_rgba(96,165,250,0.5)]' :
                                                    `${rank.border} ${rank.glow}`} 
                                        overflow-hidden`}>
                                        {user.avatar_url ? (
                                            <img src={user.avatar_url} alt={user.full_name || "Survivor"} className="w-full h-full object-cover" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center">
                                                <Skull size={20} className="text-ash-600" />
                                            </div>
                                        )}
                                        {isTop3 && (
                                            <div className={`absolute -top-1 -right-1 w-4 h-4 rounded-full blur-[2px] opacity-40 animate-pulse
                                                ${index === 0 ? 'bg-blood-red-bright' : index === 1 ? 'bg-toxic-green-DEFAULT' : 'bg-blue-400'}`}
                                            />
                                        )}
                                    </div>

                                    {/* User Info */}
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-base sm:text-lg font-biohazard tracking-widest text-white truncate mb-1">
                                            {user.full_name || "Ẩn Danh"}
                                        </h3>
                                        <div className="flex items-center gap-2">
                                            <ShieldCheck size={12} className={rank.color} />
                                            <span className={`text-[10px] sm:text-xs font-mono tracking-wider truncate ${rank.color}`}>
                                                {rank.title}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Stats */}
                                    <div className="text-right flex-shrink-0 pr-2">
                                        <div className="flex items-center justify-end gap-1.5 mb-1">
                                            <Flame size={14} className="text-toxic-green-DEFAULT" />
                                            <span className="font-biohazard text-lg sm:text-xl text-white">
                                                {user.exp || 0}
                                            </span>
                                        </div>
                                        <div className="text-[9px] sm:text-[10px] font-mono text-ash-500 tracking-widest uppercase">
                                            KINH NGHIỆM
                                        </div>
                                    </div>

                                    {/* Subtle Top 3 Medal Icon */}
                                    {isTop3 && (
                                        <div className="absolute right-4 bottom-4 opacity-10 pointer-events-none">
                                            <Medal size={48} className={
                                                index === 0 ? "text-yellow-400" :
                                                    index === 1 ? "text-gray-300" : "text-amber-700"
                                            } />
                                        </div>
                                    )}
                                </div>
                            );
                        })
                    )}
                </div>

                {/* Leaderboard CTA */}
                <div className="mt-12 text-center">
                    <p className="font-mono text-ash-500 text-xs tracking-widest mb-6 px-4">Đọc càng nhiều, cấp càng cao. Hệ thống tự động cập nhật và tính điểm mỗi khi bạn mở khóa chương truyện mới.</p>
                    <Link href="/chapters/1" className="inline-flex items-center justify-center gap-2 py-3 px-8 text-sm font-mono text-toxic-green-DEFAULT bg-toxic-green-DEFAULT/5 hover:bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/30 tracking-widest rounded transition-all shadow-[0_0_15px_rgba(57,255,20,0.1)] hover:shadow-[0_0_20px_rgba(57,255,20,0.2)]">
                        <Trophy size={16} />
                        BẮT ĐẦU CÀY RANK
                    </Link>
                </div>
            </div>
        </div>
    );
}
