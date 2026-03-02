"use client";

import { useEffect, useState } from "react";
import { MessageSquare, Send, User, Coffee, Heart, X, QrCode } from "lucide-react";
import { useTheme } from "@/context/ThemeContext";
import { createBrowserClient } from "@supabase/ssr";

interface Comment {
    id: string;
    user_name: string;
    content: string;
    created_at: string;
}

interface CommentSectionProps {
    chapterNumber: number;
}

export default function CommentSection({ chapterNumber }: CommentSectionProps) {
    const { theme } = useTheme();
    const [comments, setComments] = useState<Comment[]>([]);
    const [userName, setUserName] = useState("");
    const [content, setContent] = useState("");
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(true);
    const [user, setUser] = useState<any>(null);

    const supabase = createBrowserClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    useEffect(() => {
        fetchComments();
        checkUser();
    }, [chapterNumber]);

    const checkUser = async () => {
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
            setUser(user);
            setUserName(user.user_metadata?.full_name || user.email?.split('@')[0] || "");
        }
    };

    const fetchComments = async () => {
        setFetching(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}/comments`);
            if (res.ok) {
                const data = await res.json();
                setComments(data);
            }
        } catch (error) {
            console.error("Failed to fetch comments:", error);
        } finally {
            setFetching(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim()) return;

        setLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/chapters/${chapterNumber}/comments`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_name: userName.trim() || "Ẩn danh",
                    content: content.trim(),
                }),
            });

            if (res.ok) {
                setContent("");
                fetchComments(); // Refresh list
            }
        } catch (error) {
            console.error("Failed to post comment:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mt-16 pt-10 border-t border-reader-border max-w-4xl mx-auto px-4">
            <div className="flex items-center gap-3 mb-8">
                <MessageSquare className="text-reader-accent" size={24} />
                <h2 className="font-biohazard text-2xl tracking-wider text-reader-text">BÌNH LUẬN</h2>
                <div className="bg-reader-card-bg px-2 py-0.5 rounded text-[10px] font-mono text-reader-muted">
                    {comments.length} PHẢN HỒI
                </div>
            </div>

            {/* Comment Form */}
            <form onSubmit={handleSubmit} className="mb-12 bg-reader-card-bg p-6 rounded-lg border border-reader-border backdrop-blur-sm shadow-sm">
                {!user ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-reader-muted" size={14} />
                            <input
                                type="text"
                                placeholder="TÊN CỦA BẠN (TÙY CHỌN)"
                                value={userName}
                                onChange={(e) => setUserName(e.target.value)}
                                className="w-full bg-reader-bg border border-reader-border rounded px-10 py-2 text-xs font-mono text-reader-text outline-none focus:border-reader-accent transition-colors placeholder:text-reader-muted/60"
                            />
                        </div>
                    </div>
                ) : (
                    <div className="mb-4 flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-reader-accent/10 flex items-center justify-center border border-reader-accent/20">
                            <User className="text-reader-accent" size={12} />
                        </div>
                        <span className="text-xs font-mono text-reader-accent tracking-wider uppercase">Đang đăng bằng: {userName}</span>
                    </div>
                )}
                <textarea
                    placeholder="BẠN ĐANG NGHĨ GÌ VỀ CHƯƠNG NÀY?"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    required
                    rows={3}
                    className="w-full bg-reader-bg border border-reader-border rounded p-4 text-sm text-reader-text outline-none focus:border-reader-accent transition-colors resize-none mb-4 placeholder:text-reader-muted"
                />
                <button
                    type="submit"
                    disabled={loading || !content.trim()}
                    className="btn-toxic w-full sm:w-auto flex items-center justify-center gap-2 py-2 px-8 text-xs font-mono disabled:opacity-50 disabled:grayscale transition-all"
                    style={{
                        backgroundColor: theme !== 'dark' ? 'var(--reader-accent)' : 'transparent',
                        color: theme !== 'dark' ? 'white' : 'var(--reader-accent)',
                        borderColor: 'var(--reader-accent)'
                    }}
                >
                    <Send size={14} />
                    {loading ? "ĐANG GỬI..." : "ĐĂNG BÌNH LUẬN"}
                </button>
            </form>

            {/* Comments List */}
            <div className="space-y-6">
                {fetching ? (
                    <div className="text-center py-10">
                        <div className="animate-spin w-6 h-6 border-2 border-reader-accent border-t-transparent rounded-full mx-auto mb-2" />
                        <span className="text-reader-muted text-[10px] font-mono tracking-widest">ĐANG TẢI...</span>
                    </div>
                ) : comments.length === 0 ? (
                    <div className="text-center py-10 border border-dashed border-reader-border rounded-lg">
                        <p className="text-reader-muted text-xs font-mono">CHƯA CÓ BÌNH LUẬN NÀO. HÃY LÀ NGƯỜI ĐẦU TIÊN!</p>
                    </div>
                ) : (
                    comments.map((comment) => (
                        <div key={comment.id} className="group flex gap-4 p-4 rounded-lg bg-reader-card-bg border border-reader-border hover:border-reader-accent/40 transition-all">
                            <div className="w-10 h-10 rounded bg-reader-bg flex items-center justify-center shrink-0 border border-reader-border">
                                <User className="text-reader-muted" size={20} />
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-mono text-xs text-reader-accent">{comment.user_name}</span>
                                    <span className="text-[10px] font-mono text-reader-muted">
                                        {new Date(comment.created_at).toLocaleDateString("vi-VN")}
                                    </span>
                                </div>
                                <p className="text-reader-text text-sm leading-relaxed whitespace-pre-wrap">
                                    {comment.content}
                                </p>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
