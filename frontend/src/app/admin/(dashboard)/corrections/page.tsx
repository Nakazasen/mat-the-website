'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  FileText, 
  Loader2, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Check, 
  BookOpen,
  Info,
  Calendar,
  AlertCircle
} from 'lucide-react';

interface CorrectionItem {
  id: string;
  feedback_id: string | null;
  entity_name: string | null;
  correction_type: 'wiki_update' | 'entity_profile' | 'eval_case' | 'retrieval_rule' | 'other' | string;
  proposed_content: string;
  evidence: Array<{
    chapter_number?: number | string | null;
    chapter_title?: string | null;
    chunk_index?: number | string | null;
    content_hash?: string | null;
    preview?: string | null;
  }>;
  status: string;
  reviewer_note: string | null;
  created_at: string;
  updated_at: string;
}

const CORRECTION_TYPE_LABELS: Record<string, string> = {
  wiki_update: "Cập nhật Wiki",
  entity_profile: "Hồ sơ thực thể",
  eval_case: "Test case đánh giá",
  retrieval_rule: "Luật tìm kiếm RAG",
  other: "Khác"
};

const CORRECTION_TYPE_COLORS: Record<string, string> = {
  wiki_update: "text-blue-400 bg-blue-950/20 border-blue-800/40",
  entity_profile: "text-green-400 bg-green-950/20 border-green-800/40",
  eval_case: "text-purple-400 bg-purple-950/20 border-purple-800/40",
  retrieval_rule: "text-orange-400 bg-orange-950/20 border-orange-800/40",
  other: "text-gray-400 bg-gray-900 border-gray-800"
};

// Map database statuses ('draft', 'approved', 'rejected', 'applied') to user-friendly labels
const DB_STATUS_LABELS: Record<string, string> = {
  draft: "Nháp (Chờ duyệt)",
  approved: "Đã duyệt (Approved)",
  rejected: "Từ chối (Rejected)",
  applied: "Đã áp dụng (Applied)"
};

const DB_STATUS_COLORS: Record<string, string> = {
  draft: "text-yellow-500 bg-yellow-950/20 border-yellow-800/40",
  approved: "text-green-400 bg-green-950/20 border-green-800/40",
  rejected: "text-red-400 bg-red-950/20 border-red-800/40",
  applied: "text-blue-400 bg-blue-950/20 border-blue-800/40"
};

export default function AdminCorrectionsPage() {
  const router = useRouter();
  const [corrections, setCorrections] = useState<CorrectionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isUnauthorized, setIsUnauthorized] = useState(false);

  // Filters
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('draft');

  // Review notes state indexed by correction ID
  const [reviewerNotes, setReviewerNotes] = useState<Record<string, string>>({});
  // Submitting state for each correction item
  const [actionProgress, setActionProgress] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadCorrections();
  }, [selectedType, selectedStatus]);

  const loadCorrections = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setIsUnauthorized(false);

    try {
      let url = `/api/oracle/corrections/pending?status=${selectedStatus}`;
      if (selectedType) {
        url += `&correction_type=${selectedType}`;
      }

      const res = await fetch(url);

      if (res.ok) {
        const data = await res.json();
        setCorrections(data);
        // Initialize notes
        const notes: Record<string, string> = {};
        data.forEach((item: CorrectionItem) => {
          notes[item.id] = item.reviewer_note || "";
        });
        setReviewerNotes(notes);
      } else {
        if (res.status === 401) {
          setIsUnauthorized(true);
          setError("Bạn cần đăng nhập admin");
        } else {
          const err = await res.json().catch(() => ({}));
          setError(err.error || "Không thể tải danh sách bản nháp.");
        }
      }
    } catch (err) {
      setError("Lỗi kết nối server khi tải bản nháp.");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (
    id: string, 
    status: 'reviewed' | 'accepted' | 'rejected' | 'resolved' | 'needs_more_info'
  ) => {
    setActionProgress(prev => ({ ...prev, [id]: true }));
    setError(null);
    setSuccess(null);

    const note = reviewerNotes[id] || "";

    try {
      const res = await fetch(`/api/oracle/corrections/${id}`, {
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
        // Remove item from visible list since status changes
        setCorrections(prev => prev.filter(item => item.id !== id));
        setSuccess(`Đã cập nhật trạng thái bản nháp thành công sang: ${status.toUpperCase()}`);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        if (res.status === 401) {
          setIsUnauthorized(true);
          setError("Bạn cần đăng nhập admin");
        } else {
          const data = await res.json().catch(() => ({}));
          setError(data.error || "Lỗi khi cập nhật bản nháp");
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
            <FileText className="text-green-500" size={24} />
            DUYỆT BẢN NHÁP TRI THỨC ORACLE
          </h1>
          <p className="text-gray-500 text-sm font-mono mt-1">
            Xem xét và chỉnh sửa các bản nháp thực thể (Entity profiles) trước khi phê duyệt.
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
          {/* Filter Bar */}
          <div className="bg-[#181818] border border-gray-800 p-4 rounded-lg flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Loại:</span>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="bg-[#0a0a0a] border border-gray-800 rounded px-2.5 py-1.5 text-gray-300 focus:border-green-500 outline-none"
                >
                  <option value="">Tất cả loại</option>
                  <option value="entity_profile">Hồ sơ thực thể (entity_profile)</option>
                  <option value="wiki_update">Cập nhật Wiki (wiki_update)</option>
                  <option value="eval_case">Test case (eval_case)</option>
                  <option value="retrieval_rule">Luật tìm kiếm (retrieval_rule)</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-gray-400">Trạng thái:</span>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="bg-[#0a0a0a] border border-gray-800 rounded px-2.5 py-1.5 text-gray-300 focus:border-green-500 outline-none"
                >
                  <option value="draft">Chờ duyệt (draft)</option>
                  <option value="approved">Đã duyệt (approved)</option>
                  <option value="rejected">Từ chối (rejected)</option>
                  <option value="applied">Đã áp dụng (applied)</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-gray-400">
                Tổng cộng: <span className="text-green-400 font-bold">{corrections.length}</span> bản nháp.
              </span>
              <button
                onClick={() => loadCorrections()}
                disabled={loading}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-green-900/30 text-green-400 hover:bg-green-900/50 border border-green-800/40 rounded transition-colors cursor-pointer"
              >
                {loading ? <Loader2 className="animate-spin" size={12} /> : null}
                TẢI BẢN NHÁP
              </button>
            </div>
          </div>

          {/* LIST */}
          {loading && corrections.length === 0 ? (
            <div className="flex justify-center py-20">
              <Loader2 className="animate-spin text-green-500" size={36} />
            </div>
          ) : corrections.length === 0 ? (
            <div className="bg-[#181818] border border-gray-800 rounded-lg p-12 text-center text-gray-500 text-xs italic font-mono">
              Không có bản nháp tri thức nào khớp với bộ lọc.
            </div>
          ) : (
            <div className="grid gap-6">
              {corrections.map((item) => {
                const label = CORRECTION_TYPE_LABELS[item.correction_type] || item.correction_type;
                const typeColor = CORRECTION_TYPE_COLORS[item.correction_type] || "text-gray-400 bg-gray-900 border-gray-800";
                const statusLabel = DB_STATUS_LABELS[item.status] || item.status;
                const statusColor = DB_STATUS_COLORS[item.status] || "text-gray-400 bg-gray-900 border-gray-800";

                // Parse proposed_content if it is serialized JSON (e.g. from generated_missing_entity_profiles.json)
                let parsedProfile: any = null;
                try {
                  parsedProfile = JSON.parse(item.proposed_content);
                } catch (e) {
                  // Keep as raw text
                }

                return (
                  <div 
                    key={item.id} 
                    className="bg-[#181818] border border-gray-800 rounded-lg p-5 flex flex-col md:flex-row gap-6 hover:border-gray-700 transition-all font-mono"
                  >
                    <div className="flex-1 space-y-4">
                      {/* Meta header */}
                      <div className="flex flex-wrap items-center gap-3 text-xs">
                        <span className="text-gray-100 font-bold text-sm tracking-wide">
                          {item.entity_name || "Thực thể không tên"}
                        </span>
                        <span className="text-gray-600">|</span>
                        <span className={`px-2 py-0.5 border rounded-full text-[10px] uppercase font-bold ${typeColor}`}>
                          {label}
                        </span>
                        <span className="text-gray-600">|</span>
                        <span className={`px-2 py-0.5 border rounded-full text-[10px] uppercase font-bold ${statusColor}`}>
                          {statusLabel}
                        </span>
                        <span className="text-gray-600">|</span>
                        <span className="text-gray-500 text-[10px] flex items-center gap-1">
                          <Calendar size={12} /> {new Date(item.created_at).toLocaleString('vi-VN')}
                        </span>
                      </div>

                      {/* Content block */}
                      <div className="space-y-3">
                        <div className="bg-[#0f0f0f] border border-gray-900 rounded p-4 text-xs space-y-2">
                          <div className="text-green-500 font-bold flex items-center gap-1.5 border-b border-gray-900 pb-1.5">
                            <Info size={12} /> NỘI DUNG ĐỀ XUẤT:
                          </div>
                          
                          {parsedProfile ? (
                            <div className="space-y-2.5 font-sans text-gray-300">
                              <div className="grid grid-cols-2 gap-2 text-xs font-mono border-b border-gray-950 pb-2">
                                <div>
                                  <span className="text-gray-500">Phân loại loại thực thể:</span>{" "}
                                  <span className="text-green-400 capitalize">{parsedProfile.entity_type || "N/A"}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Độ ưu tiên (Priority):</span>{" "}
                                  <span className="text-yellow-400 capitalize">{parsedProfile.priority || "N/A"}</span>
                                </div>
                              </div>
                              {parsedProfile.summary && (
                                <div>
                                  <div className="text-[10px] font-mono text-gray-500 uppercase">Tóm tắt (Summary)</div>
                                  <div className="mt-0.5">{parsedProfile.summary}</div>
                                </div>
                              )}
                              {parsedProfile.content && (
                                <div>
                                  <div className="text-[10px] font-mono text-gray-500 uppercase">Chi tiết (Content)</div>
                                  <div className="mt-0.5 whitespace-pre-wrap">{parsedProfile.content}</div>
                                </div>
                              )}
                              {!parsedProfile.summary && !parsedProfile.content && (
                                <div className="text-xs font-mono text-gray-500 italic">
                                  Bản nháp được khởi tạo từ logs (Chưa điền nội dung tri thức).
                                </div>
                              )}
                            </div>
                          ) : (
                            <div className="text-gray-300 font-sans whitespace-pre-wrap">{item.proposed_content}</div>
                          )}
                        </div>

                        {/* Evidence block */}
                        {item.evidence && item.evidence.length > 0 && (
                          <div className="space-y-2">
                            <div className="text-xs text-yellow-500 font-bold flex items-center gap-1.5">
                              <BookOpen size={12} /> BẰNG CHỨNG TRUYỆN ({item.evidence.length} trích đoạn):
                            </div>
                            <div className="space-y-2 pl-4">
                              {item.evidence.map((ev, evIdx) => (
                                <div key={evIdx} className="bg-[#0f0f0f]/40 border border-gray-900 rounded p-2.5 text-xs font-sans text-gray-400">
                                  <div className="font-mono text-[10px] text-green-500/80 mb-1 flex items-center gap-1 justify-between">
                                    <span>
                                      Chương {ev.chapter_number || "N/A"} : {ev.chapter_title || "N/A"}
                                    </span>
                                    {ev.chunk_index !== undefined && (
                                      <span className="text-gray-600">Chunk #{ev.chunk_index}</span>
                                    )}
                                  </div>
                                  <div className="italic font-sans text-gray-300">
                                    &ldquo;{ev.preview || "Không có trích đoạn hiển thị..."}&rdquo;
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {item.evidence && item.evidence.length === 0 && (
                          <div className="flex items-center gap-1.5 text-xs text-yellow-500/80 bg-yellow-950/10 border border-yellow-900/10 p-2.5 rounded">
                            <AlertCircle size={14} />
                            <span>Bản nháp này không có bằng chứng tự động (Cần tra cứu thêm hoặc bổ sung tay).</span>
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
                        <button
                          onClick={() => handleAction(item.id, 'needs_more_info')}
                          disabled={actionProgress[item.id]}
                          className="col-span-2 py-2 bg-[#1b1b1b] border border-gray-800 hover:bg-gray-800 disabled:opacity-50 text-[10px] text-gray-400 font-bold rounded tracking-wider transition-colors cursor-pointer"
                        >
                          {actionProgress[item.id] ? "..." : "NEEDS MORE INFO"}
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
