"use client";
import { useEffect, useState, Suspense } from "react";
import { useRouter } from "next/navigation";
import { createAdminClient } from "@/lib/supabase-admin";
import { Skull, Heart, BookOpen, ShieldCheck, Calendar, ArrowLeft, LogOut, Bookmark, Trash2 } from "lucide-react";
import Link from "next/link";
import type { User } from "@supabase/supabase-js";

interface ReaderStats {
    chaptersRead: number;
    likesGiven: number;
    exp: number;
}

function ProfileContent() {
    const router = useRouter();
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState<ReaderStats>({ chaptersRead: 0, likesGiven: 0, exp: 0 });
    const [bookmarks, setBookmarks] = useState<any[]>([]);

    useEffect(() => {
        const supabase = createAdminClient();
        if (!supabase) {
            router.push("/");
            return;
        }

        supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session?.user) {
                router.push("/");
                return;
            }
            setUser(session.user);
            setLoading(false);

            // Fetch real profile stats from Database
            fetch('/api/user').then(res => {
                if (res.ok) return res.json();
                throw new Error("Failed to fetch profile");
            }).then(profileData => {
                setStats(prev => ({
                    ...prev,
                    chaptersRead: profileData.chapters_read || 0,
                    exp: profileData.exp || 0
                }));
            }).catch(err => {
                console.error("Profile fetch error:", err);
            });

            // Fetch bookmarks
            fetch('/api/user/bookmarks').then(res => {
                if (res.ok) return res.json();
                return [];
            }).then(data => {
                if (Array.isArray(data)) setBookmarks(data);
            }).catch(() => { });

            // Load likes given (still from localStorage for now as it's not and DB profile natively yet)
            try {
                let likesGiven = 0;
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key && key.startsWith("liked_chapter_")) {
                        const val = localStorage.getItem(key);
                        if (val === "true") likesGiven++;
                    }
                }
                setStats(prev => ({ ...prev, likesGiven }));
            } catch { }
        });
    }, [router]);

    const handleLogout = async () => {
        const supabase = createAdminClient();
        if (!supabase) return;
        await supabase.auth.signOut();
        router.push("/");
    };

    const handleRemoveBookmark = async (e: React.MouseEvent, chapterId: string, bookmarkId: string) => {
        e.preventDefault();
        e.stopPropagation();
        try {
            const res = await fetch(`/api/user/bookmarks?chapter_id=${chapterId}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                setBookmarks(prev => prev.filter(bm => bm.id !== bookmarkId));
            } else {
                console.error("Failed to delete bookmark");
            }
        } catch (error) {
            console.error("Error removing bookmark", error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <Skull size={32} className="text-toxic-green-DEFAULT animate-pulse" />
            </div>
        );
    }

    if (!user) return null;

    const joinDate = new Date(user.created_at).toLocaleDateString("vi-VN", {
        timeZone: "Asia/Ho_Chi_Minh",
        year: "numeric",
        month: "long",
        day: "numeric",
    });

    // Determine rank based on EXP
    const getRank = (exp: number) => {
        if (exp >= 5000) return { title: "Huy hiệu Hi Vọng Bậc S", color: "text-yellow-400", border: "border-yellow-500/50" };
        if (exp >= 2000) return { title: "Huy hiệu Hi Vọng Bậc A", color: "text-purple-400", border: "border-purple-500/50" };
        if (exp >= 1000) return { title: "Huy hiệu Hi Vọng Bậc B", color: "text-blue-400", border: "border-blue-500/50" };
        if (exp >= 500) return { title: "Huy hiệu Hi Vọng Bậc C", color: "text-green-400", border: "border-green-500/50" };
        return { title: "Huy hiệu Hi Vọng Bậc D", color: "text-amber-700", border: "border-amber-900/50" };
    };

    const rank = getRank(stats.exp);

    return (
        <div className="min-h-screen bg-black">
            {/* Header */}
            <div className="max-w-2xl mx-auto px-4 pt-6 pb-4">
                <Link href="/" className="inline-flex items-center gap-2 text-sm text-ash-400 hover:text-toxic-green-DEFAULT transition-colors font-mono">
                    <ArrowLeft size={14} />
                    QUAY VỀ TRẤN HI VỌNG
                </Link>
            </div>

            <div className="max-w-2xl mx-auto px-4 pb-12">
                {/* ID Card */}
                <div className="relative bg-ash-900 border border-ash-700 rounded-xl overflow-hidden shadow-2xl">
                    {/* Card header bar */}
                    <div className="bg-gradient-to-r from-ash-800 via-ash-700 to-ash-800 px-6 py-3 flex items-center justify-between border-b border-ash-600">
                        <div className="flex items-center gap-2">
                            <span className="text-xl">☣</span>
                            <span className="font-biohazard text-xs text-toxic-green-DEFAULT tracking-[0.3em] uppercase">THẺ CĂN CƯỚC CÔNG DÂN</span>
                        </div>
                        <span className="text-[10px] font-mono text-ash-500">TRẤN HI VỌNG</span>
                    </div>

                    {/* Rusty texture overlay on the whole card */}
                    <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
                        style={{
                            backgroundImage: "url('https://www.transparenttextures.com/patterns/black-linen.png')",
                        }}
                    />

                    {/* Card body */}
                    <div className="p-6 md:p-8">
                        <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">
                            {/* Avatar with rusty metallic frame */}
                            <div className="relative flex-shrink-0">
                                {/* Outer metallic frame */}
                                <div className="w-28 h-28 rounded-lg bg-gradient-to-br from-amber-900/40 via-stone-700/30 to-amber-800/40 p-1 shadow-inner relative">
                                    {/* Scratches overlay */}
                                    <div className="absolute inset-0 rounded-lg opacity-20 pointer-events-none"
                                        style={{
                                            background: "linear-gradient(135deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%)",
                                        }}
                                    />
                                    {/* Inner border (rust effect) */}
                                    <div className="w-full h-full rounded-md border-2 border-amber-900/50 overflow-hidden relative bg-ash-950">
                                        {user.user_metadata?.avatar_url ? (
                                            <img
                                                src={user.user_metadata.avatar_url}
                                                alt="Avatar"
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center">
                                                <Skull size={36} className="text-ash-600" />
                                            </div>
                                        )}
                                        {/* Blood splatter corner */}
                                        <div className="absolute -top-1 -right-1 w-6 h-6 bg-blood-red-DEFAULT/30 rounded-full blur-sm" />
                                        <div className="absolute -bottom-1 -left-1 w-4 h-4 bg-blood-red-deep/20 rounded-full blur-sm" />
                                    </div>
                                </div>
                                {/* Status badge */}
                                <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-ash-800 border border-toxic-green-DEFAULT/40 rounded-full px-3 py-0.5">
                                    <span className="text-[9px] font-mono text-toxic-green-DEFAULT tracking-wider">ACTIVE</span>
                                </div>
                            </div>

                            {/* Info */}
                            <div className="flex-1 space-y-4 text-center md:text-left">
                                {/* Name */}
                                <div>
                                    <div className="text-[10px] font-mono text-ash-500 tracking-widest uppercase mb-1">HỌ TÊN SINH TỒN</div>
                                    <h2 className="text-xl font-biohazard text-white tracking-widest">
                                        {user.user_metadata?.full_name || user.email?.split("@")[0] || "Ẩn Danh"}
                                    </h2>
                                </div>

                                {/* Email */}
                                <div>
                                    <div className="text-[10px] font-mono text-ash-500 tracking-widest uppercase mb-1">LIÊN LẠC</div>
                                    <p className="text-sm font-mono text-ash-300">{user.email}</p>
                                </div>

                                {/* Join date & Rank */}
                                <div className="flex flex-wrap gap-4 justify-center md:justify-start">
                                    <div>
                                        <div className="text-[10px] font-mono text-ash-500 tracking-widest uppercase mb-1 flex items-center gap-1">
                                            <Calendar size={10} />
                                            NGÀY NHẬP CƯ
                                        </div>
                                        <p className="text-sm font-mono text-ash-300">{joinDate}</p>
                                    </div>
                                    <div>
                                        <div className="text-[10px] font-mono text-ash-500 tracking-widest uppercase mb-1 flex items-center gap-1">
                                            <ShieldCheck size={10} />
                                            DANH HIỆU
                                        </div>
                                        <p className={`text-sm font-biohazard tracking-wider ${rank.color}`}>{rank.title}</p>
                                    </div>
                                </div>

                                {/* EXP Bar */}
                                <div className="mt-2 text-left">
                                    <div className="flex justify-between items-center mb-1">
                                        <div className="text-[9px] font-mono text-toxic-green-DEFAULT/60 tracking-widest uppercase">KINH NGHIỆM SINH TỒN</div>
                                        <div className="text-[9px] font-mono text-toxic-green-DEFAULT">{stats.exp} EXP</div>
                                    </div>
                                    <div className="h-1.5 w-full bg-ash-950 rounded-full border border-ash-800 overflow-hidden p-0.5">
                                        <div
                                            className="h-full bg-toxic-green-DEFAULT rounded-full shadow-[0_0_10px_rgba(57,255,20,0.5)] transition-all duration-1000"
                                            style={{ width: `${Math.min(100, (stats.exp % 1000) / 10)}%` }} // Simple level logic for visual: reset bar every 1000 EXP
                                        />
                                    </div>
                                    <div className="text-[8px] font-mono text-ash-600 mt-1 text-right italic">Bản ghi được đồng bộ vĩnh viễn với Database</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Divider with hazard stripes */}
                    <div className="h-px bg-gradient-to-r from-transparent via-ash-600 to-transparent mx-6" />

                    {/* Stats section */}
                    <div className="p-6 md:p-8">
                        <div className="text-[10px] font-mono text-ash-500 tracking-[0.3em] uppercase mb-4 flex items-center gap-2">
                            <span className="text-toxic-green-DEFAULT">☣</span>
                            THỐNG KÊ SINH TỒN
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            {/* Chapters read */}
                            <div className="bg-ash-800/50 border border-ash-700/50 rounded-lg p-4 text-center hover:border-toxic-green-DEFAULT/30 transition-colors">
                                <BookOpen size={20} className="mx-auto mb-2 text-toxic-green-DEFAULT" />
                                <div className="text-2xl font-biohazard text-white tracking-widest">{stats.chaptersRead}</div>
                                <div className="text-[10px] font-mono text-ash-500 tracking-wider mt-1">CHƯƠNG ĐÃ CHINH PHỤC</div>
                            </div>
                            {/* Likes given */}
                            <div className="bg-ash-800/50 border border-ash-700/50 rounded-lg p-4 text-center hover:border-blood-red-bright/30 transition-colors">
                                <Heart size={20} className="mx-auto mb-2 text-blood-red-bright" />
                                <div className="text-2xl font-biohazard text-white tracking-widest">{stats.likesGiven}</div>
                                <div className="text-[10px] font-mono text-ash-500 tracking-wider mt-1">TIM ĐÃ TRAO</div>
                            </div>
                        </div>
                    </div>

                    {/* Bookmarks Section */}
                    <div className="p-6 md:p-8 border-t border-ash-700/30">
                        <div className="text-[10px] font-mono text-ash-500 tracking-[0.3em] uppercase mb-4 flex items-center gap-2">
                            <Bookmark size={14} className="text-amber-500" />
                            TỦ SÁCH SINH TỒN
                        </div>
                        {bookmarks.length === 0 ? (
                            <div className="text-center py-8 text-ash-500 font-mono text-xs border border-dashed border-ash-700/50 rounded-lg bg-ash-800/20">
                                CHƯA CÓ DỮ LIỆU LƯU TRỮ
                            </div>
                        ) : (
                            <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                                {bookmarks.map((bm) => (
                                    <div key={bm.id} className="relative group">
                                        <Link
                                            href={`/chapters/${bm.chapter?.chapter_number || '#'}`}
                                            className="flex flex-col gap-1 p-3 pr-10 rounded-lg bg-ash-800/40 hover:bg-ash-800 border border-ash-700/50 hover:border-toxic-green-DEFAULT/30 transition-all block w-full"
                                        >
                                            <div className="flex items-center justify-between">
                                                <span className="font-mono text-xs text-toxic-green-DEFAULT tracking-widest">
                                                    CHƯƠNG {bm.chapter?.chapter_number || 'BỊ XÓA'}
                                                </span>
                                                <span className="text-[10px] font-mono text-ash-500">{new Date(bm.created_at).toLocaleDateString('vi-VN')}</span>
                                            </div>
                                            <span className="text-sm text-ash-300 group-hover:text-white transition-colors truncate font-reading text-left lg:text-base">
                                                {bm.chapter?.title || 'Nội dung không còn tồn tại...'}
                                            </span>
                                        </Link>
                                        <button
                                            onClick={(e) => handleRemoveBookmark(e, bm.chapter_id, bm.id)}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-ash-500 hover:text-red-500 hover:bg-red-500/10 rounded-md opacity-0 group-hover:opacity-100 transition-all focus:opacity-100"
                                            title="Xóa khỏi tủ sách"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="px-6 pb-6 md:px-8 md:pb-8">
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center justify-center gap-2 py-3 text-sm font-mono text-red-400 bg-red-950/20 hover:bg-red-950/40 border border-red-900/30 tracking-widest rounded-lg transition-all"
                        >
                            <LogOut size={16} />
                            RỜI TRẤN HI VỌNG
                        </button>
                    </div>
                </div>

                {/* Bottom decoration */}
                <div className="text-center mt-6 text-[10px] font-mono text-ash-600 tracking-widest">
                    ☣ DOCUMENT #MTW-{user.id.slice(0, 8).toUpperCase()} · CLASSIFIED ☣
                </div>
            </div>
        </div>
    );
}

export default function ProfilePage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-black flex items-center justify-center">
                <Skull size={32} className="text-toxic-green-DEFAULT animate-pulse" />
            </div>
        }>
            <ProfileContent />
        </Suspense>
    );
}
