"use client";

import { useEffect, useState } from "react";
import { MessageSquare, Send, User } from "lucide-react";

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
    const [comments, setComments] = useState<Comment[]>([]);
    const [userName, setUserName] = useState("");
    const [content, setContent] = useState("");
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(true);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    useEffect(() => {
        fetchComments();
    }, [chapterNumber]);

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
        <div className="mt-16 pt-10 border-t border-ash-800/60 max-w-4xl mx-auto px-4">
            <div className="flex items-center gap-3 mb-8">
                <MessageSquare className="text-toxic-green-DEFAULT" size={24} />
                <h2 className="font-biohazard text-2xl tracking-wider text-worn-white">BÌNH LUẬN</h2>
                <div className="bg-ash-800/50 px-2 py-0.5 rounded text-[10px] font-mono text-ash-400">
                    {comments.length} PHẢN HỒI
                </div>
            </div>

            {/* Comment Form */}
            <form onSubmit={handleSubmit} className="mb-12 bg-ash-900/30 p-6 rounded-lg border border-ash-800/40 backdrop-blur-sm">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                    <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 text-ash-600" size={14} />
                        <input
                            type="text"
                            placeholder="TÊN CỦA BẠN (TÙY CHỌN)"
                            value={userName}
                            onChange={(e) => setUserName(e.target.value)}
                            className="w-full bg-ash-950/50 border border-ash-800 rounded px-10 py-2 text-xs font-mono text-ash-200 outline-none focus:border-toxic-green-DEFAULT/50 transition-colors"
                        />
                    </div>
                </div>
                <textarea
                    placeholder="BẠN ĐANG NGHĨ GÌ VỀ CHƯƠNG NÀY?"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    required
                    rows={3}
                    className="w-full bg-ash-950/50 border border-ash-800 rounded p-4 text-sm text-ash-200 outline-none focus:border-toxic-green-DEFAULT/50 transition-colors resize-none mb-4"
                />
                <button
                    type="submit"
                    disabled={loading || !content.trim()}
                    className="btn-toxic w-full sm:w-auto flex items-center justify-center gap-2 py-2 px-8 text-xs font-mono disabled:opacity-50 disabled:grayscale"
                >
                    <Send size={14} />
                    {loading ? "ĐANG GỬI..." : "ĐĂNG BÌNH LUẬN"}
                </button>
            </form>

            {/* Comments List */}
            <div className="space-y-6">
                {fetching ? (
                    <div className="text-center py-10">
                        <div className="animate-spin w-6 h-6 border-2 border-toxic-green-DEFAULT border-t-transparent rounded-full mx-auto mb-2" />
                        <span className="text-ash-500 text-[10px] font-mono tracking-widest">ĐANG TẢI...</span>
                    </div>
                ) : comments.length === 0 ? (
                    <div className="text-center py-10 border border-dashed border-ash-800/40 rounded-lg">
                        <p className="text-ash-600 text-xs font-mono">CHƯA CÓ BÌNH LUẬN NÀO. HÃY LÀ NGƯỜI ĐẦU TIÊN!</p>
                    </div>
                ) : (
                    comments.map((comment) => (
                        <div key={comment.id} className="group flex gap-4 p-4 rounded-lg bg-ash-950/50 border border-ash-800/30 hover:border-ash-700/50 transition-all">
                            <div className="w-10 h-10 rounded bg-ash-800 flex items-center justify-center shrink-0 border border-ash-700">
                                <User className="text-ash-500" size={20} />
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-mono text-xs text-toxic-green-DEFAULT">{comment.user_name}</span>
                                    <span className="text-[10px] font-mono text-ash-600">
                                        {new Date(comment.created_at).toLocaleDateString("vi-VN")}
                                    </span>
                                </div>
                                <p className="text-ash-300 text-sm leading-relaxed whitespace-pre-wrap">
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
