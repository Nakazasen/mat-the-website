'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  MessageSquare, 
  Loader2, 
  CheckCircle2, 
  AlertTriangle, 
  X, 
  Save, 
  Search, 
  ShieldAlert, 
  Check, 
  XCircle,
  HelpCircle,
  BookOpen
} from 'lucide-react';

interface FeedbackItem {
  id: string;
  question: string;
  answer: string;
  source: string;
  citations: string[];
  chapter_progress: number;
  feedback_type: 'wrong' | 'missing' | 'spoiler' | 'hallucination' | 'other' | string;
  user_comment: string;
  suggested_correction: string;
  status: string;
  created_at: string;
}

const FEEDBACK_TYPE_LABELS: Record<string, string> = {
  wrong: "Sai kiến thức",
  missing: "Thiếu thông tin",
  spoiler: "Lộ tình tiết/spoiler",
  hallucination: "AI bịa",
  other: "Khác"
};

const FEEDBACK_TYPE_COLORS: Record<string, string> = {
  wrong: "text-red-400 bg-red-950/20 border-red-800/40",
  missing: "text-yellow-400 bg-yellow-950/20 border-yellow-800/40",
  spoiler: "text-purple-400 bg-purple-950/20 border-purple-800/40",
  hallucination: "text-orange-400 bg-orange-950/20 border-orange-800/40",
  other: "text-blue-400 bg-blue-950/20 border-blue-800/40"
};

export default function AdminFeedbackPage() {
  const router = useRouter();
  const [feedbacks, setFeedbacks] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isUnauthorized, setIsUnauthorized] = useState(false);

  // Review notes state indexed by feedback ID
  const [reviewerNotes, setReviewerNotes] = useState<Record<string, string>>({});
  // Submitting state for each feedback item
  const [actionProgress, setActionProgress] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadFeedbacks();
  }, []);

  const loadFeedbacks = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setIsUnauthorized(false);

    try {
      const res = await fetch('/api/oracle/feedback/pending');

      if (res.ok) {
        const data = await res.json();
        setFeedbacks(data);
      } else {
        if (res.status === 401) {
          setIsUnauthorized(true);
          setError("Bạn cần đăng nhập admin");
        } else {
          const err = await res.json().catch(() => ({}));
          setError(err.error || "Không thể tải danh sách phản hồi.");
        }
      }
    } catch (err) {
      setError("Lỗi kết nối server khi tải feedback.");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id: string, status: 'reviewed' | 'accepted' | 'rejected' | 'resolved') => {
    setActionProgress(prev => ({ ...prev, [id]: true }));
    setError(null);
    setSuccess(null);

    const note = reviewerNotes[id] || "";

    try {
      const res = await fetch(`/api/oracle/feedback/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          status,
          reviewer_note: note.trim()
        })
      });

      if (res.ok) {
        // Remove item from pending list
        setFeedbacks(prev => prev.filter(item => item.id !== id));
        setSuccess(`Đã cập nhật phản hồi thành công sang trạng thái: ${status.toUpperCase()}`);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        if (res.status === 401) {
          setIsUnauthorized(true);
          setError("Bạn cần đăng nhập admin");
        } else {
          const data = await res.json().catch(() => ({}));
          setError(data.error || "Lỗi khi xử lý phản hồi");
        }
      }
    } catch (err) {
      setError("Lỗi kết nối server khi gửi cập nhật.");
    } finally {
      setActionProgress(prev => ({ ...prev, [id]: false }));
    }
  };

  return (
    <div className="max-w-6xl">
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
            <MessageSquare className="text-green-500" size={24} />
            QUẢN LÝ BÁO LỖI ORACLE RAG
          </h1>
          <p className="text-gray-500 text-sm font-mono mt-1">
            Kiểm duyệt ý kiến phản hồi và đính chính câu trả lời từ Hệ thống Chatbot.
          </p>
        </div>
      </div>

      {success && (
        <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-4 text-sm mb-6 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 size={16} />
          <span>{success}</span>
        </div>
      )}

      {error && !isUnauthorized && (
        <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-4 text-sm mb-6">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {isUnauthorized ? (
        <div className="bg-[#181818] border border-gray-800 rounded-lg p-6 max-w-md mx-auto mt-12 shadow-xl text-center">
          <h2 className="text-sm font-mono text-gray-200 uppercase tracking-widest flex items-center justify-center gap-2 mb-4">
            <ShieldAlert className="text-red-500" size={18} />
            YÊU CẦU XÁC THỰC ADMIN
          </h2>
          <p className="text-gray-400 text-xs font-mono mb-6">
            Bạn cần đăng nhập bằng tài khoản Admin để truy cập trang này.
          </p>
          <button
            onClick={() => router.push('/admin/login')}
            className="w-full flex items-center justify-center gap-2 py-3 bg-green-600 hover:bg-green-500 text-white rounded font-mono text-xs tracking-widest transition-all cursor-pointer"
          >
            ĐẾN TRANG ĐĂNG NHẬP
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Active Session Bar */}
          <div className="flex items-center justify-between bg-[#181818] border border-gray-800 px-4 py-3 rounded-lg text-xs font-mono">
            <div className="text-gray-400">
              Tổng số: <span className="text-green-400 font-bold">{feedbacks.length}</span> báo lỗi chờ duyệt.
            </div>
            <button
              onClick={() => loadFeedbacks()}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1 bg-green-900/30 text-green-400 hover:bg-green-900/50 border border-green-800/40 rounded transition-colors cursor-pointer"
            >
              {loading ? <Loader2 className="animate-spin" size={12} /> : null}
              TẢI PHẢN HỒI
            </button>
          </div>

          {/* LIST */}
          {loading && feedbacks.length === 0 ? (
            <div className="flex justify-center py-20">
              <Loader2 className="animate-spin text-green-500" size={36} />
            </div>
          ) : feedbacks.length === 0 ? (
            <div className="bg-[#181818] border border-gray-800 rounded-lg p-12 text-center text-gray-500 text-xs italic font-mono">
              Không có báo lỗi pending nào cần xử lý.
            </div>
          ) : (
            <div className="grid gap-6">
              {feedbacks.map((item) => {
                const label = FEEDBACK_TYPE_LABELS[item.feedback_type] || item.feedback_type;
                const colorClass = FEEDBACK_TYPE_COLORS[item.feedback_type] || "text-gray-400 bg-gray-900 border-gray-800";
                
                return (
                  <div 
                    key={item.id} 
                    className="bg-[#181818] border border-gray-800 rounded-lg p-5 flex flex-col md:flex-row gap-6 hover:border-gray-700 transition-all font-mono"
                  >
                    <div className="flex-1 space-y-4">
                      {/* Meta header */}
                      <div className="flex flex-wrap items-center gap-3 text-xs">
                        <span className={`px-2 py-0.5 border rounded-full text-[10px] uppercase font-bold ${colorClass}`}>
                          {label}
                        </span>
                        <span className="text-gray-600">|</span>
                        <span className="text-gray-400 flex items-center gap-1">
                          <BookOpen size={12} /> Chương {item.chapter_progress}
                        </span>
                        <span className="text-gray-600">|</span>
                        <span className="text-gray-500">
                          Nguồn: <span className="text-green-500">{item.source || "N/A"}</span>
                        </span>
                        <span className="text-gray-600">|</span>
                        <span className="text-gray-500 text-[10px]">
                          {new Date(item.created_at).toLocaleString('vi-VN')}
                        </span>
                      </div>

                      {/* Content block */}
                      <div className="space-y-3">
                        <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3 text-xs">
                          <div className="text-green-500 font-bold mb-1 flex items-center gap-1.5">
                            <HelpCircle size={12} /> QUESTION:
                          </div>
                          <div className="text-gray-300 font-sans">{item.question}</div>
                        </div>

                        <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3 text-xs">
                          <div className="text-yellow-500 font-bold mb-1 flex items-center gap-1.5">
                            <Check size={12} /> ORACLE ANSWER:
                          </div>
                          <div className="text-gray-300 font-sans whitespace-pre-wrap">{item.answer}</div>
                        </div>

                        {item.user_comment && (
                          <div className="bg-[#0d2a13]/10 border border-green-900/20 rounded p-3 text-xs">
                            <div className="text-green-400 font-bold mb-1">GÓP Ý CỦA BẠN:</div>
                            <div className="text-gray-300 font-sans">{item.user_comment}</div>
                          </div>
                        )}

                        {item.suggested_correction && (
                          <div className="bg-[#1e2a38]/20 border border-blue-900/20 rounded p-3 text-xs">
                            <div className="text-blue-400 font-bold mb-1">ĐỀ XUẤT ĐÍNH CHÍNH:</div>
                            <div className="text-gray-300 font-sans">{item.suggested_correction}</div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Block */}
                    <div className="w-full md:w-64 shrink-0 flex flex-col justify-between border-t md:border-t-0 md:border-l border-gray-800 pt-4 md:pt-0 md:pl-6 space-y-4">
                      <div className="space-y-2">
                        <label className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">
                          Ghi chú đánh giá (Reviewer Note)
                        </label>
                        <textarea
                          placeholder="Viết ghi chú duyệt (tối đa 2000 ký tự)..."
                          value={reviewerNotes[item.id] || ""}
                          onChange={(e) => setReviewerNotes(prev => ({ ...prev, [item.id]: e.target.value }))}
                          rows={3}
                          className="w-full bg-[#0a0a0a] border border-gray-800 rounded p-2 text-xs text-gray-200 focus:border-green-500 outline-none resize-none transition-all font-sans"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={() => handleAction(item.id, 'reviewed')}
                          disabled={actionProgress[item.id]}
                          className="py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-[10px] text-gray-300 font-bold rounded tracking-wider transition-colors cursor-pointer"
                        >
                          {actionProgress[item.id] ? "..." : "REVIEWED"}
                        </button>
                        <button
                          onClick={() => handleAction(item.id, 'rejected')}
                          disabled={actionProgress[item.id]}
                          className="py-2 bg-red-950/40 hover:bg-red-900/40 border border-red-900/60 disabled:opacity-50 text-[10px] text-red-400 font-bold rounded tracking-wider transition-colors cursor-pointer"
                        >
                          {actionProgress[item.id] ? "..." : "REJECT"}
                        </button>
                        <button
                          onClick={() => handleAction(item.id, 'accepted')}
                          disabled={actionProgress[item.id]}
                          className="py-2 bg-blue-950/40 hover:bg-blue-900/40 border border-blue-900/60 disabled:opacity-50 text-[10px] text-blue-400 font-bold rounded tracking-wider transition-colors cursor-pointer"
                        >
                          {actionProgress[item.id] ? "..." : "ACCEPT"}
                        </button>
                        <button
                          onClick={() => handleAction(item.id, 'resolved')}
                          disabled={actionProgress[item.id]}
                          className="py-2 bg-green-950/40 hover:bg-green-900/40 border border-green-900/60 disabled:opacity-50 text-[10px] text-green-400 font-bold rounded tracking-wider transition-colors cursor-pointer"
                        >
                          {actionProgress[item.id] ? "..." : "RESOLVE"}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
