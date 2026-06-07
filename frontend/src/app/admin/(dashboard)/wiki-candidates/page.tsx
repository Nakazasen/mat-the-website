'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  LibraryBig, 
  Loader2, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Copy, 
  Download,
  BookOpen,
  Info,
  Calendar,
  AlertCircle,
  Plus,
  Trash2,
  FileJson
} from 'lucide-react';

interface EvidenceItem {
  chapter_number?: number | string | null;
  chapter_title?: string | null;
  chunk_index?: number | string | null;
  content_hash?: string | null;
  preview?: string | null;
}

interface WikiCandidate {
  correction_id: string;
  entity_name: string;
  entity_type: string;
  summary: string;
  content: string;
  aliases: string[];
  evidence: EvidenceItem[];
  source: string;
  status: 'ready_for_review' | 'needs_human_fill' | 'invalid' | string;
  human_review_required: boolean;
  notes: string;
}

// Map db categories to Vietnamese labels
const CATEGORIES = ["Nhân vật", "Sinh vật", "Thế lực", "Vật phẩm", "Địa điểm"];

const STATUS_LABELS: Record<string, string> = {
  ready_for_review: "Sẵn sàng duyệt (Ready)",
  needs_human_fill: "Cần điền thêm (Needs Fill)",
  invalid: "Không hợp lệ (Invalid)"
};

const STATUS_COLORS: Record<string, string> = {
  ready_for_review: "text-green-400 bg-green-950/20 border-green-800/40",
  needs_human_fill: "text-yellow-500 bg-yellow-950/20 border-yellow-800/40",
  invalid: "text-red-400 bg-red-950/20 border-red-800/40"
};

export default function AdminWikiCandidatesPage() {
  const router = useRouter();
  const [candidates, setCandidates] = useState<WikiCandidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isUnauthorized, setIsUnauthorized] = useState(false);

  // Local modifications state indexed by candidate correction_id
  const [editedCandidates, setEditedCandidates] = useState<Record<string, Partial<WikiCandidate>>>({});
  const [newAlias, setNewAlias] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<'editor' | 'json_preview'>('editor');
  const [saving, setSaving] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadCandidates();
  }, []);

  const loadCandidates = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setIsUnauthorized(false);

    try {
      const res = await fetch('/api/oracle/wiki-candidates');

      if (res.ok) {
        const data = await res.json();
        setCandidates(data);
        // Initialize edited states
        const initialEdits: Record<string, Partial<WikiCandidate>> = {};
        data.forEach((item: WikiCandidate) => {
          initialEdits[item.correction_id] = {
            entity_type: item.entity_type,
            summary: item.summary,
            content: item.content,
            aliases: [...item.aliases]
          };
        });
        setEditedCandidates(initialEdits);
      } else {
        if (res.status === 401) {
          setIsUnauthorized(true);
          setError("Bạn cần đăng nhập admin");
        } else {
          const err = await res.json().catch(() => ({}));
          setError(err.error || "Không thể tải danh sách ứng viên.");
        }
      }
    } catch (err) {
      setError("Lỗi kết nối server khi tải ứng viên.");
    } finally {
      setLoading(false);
    }
  };

  // Helper to get fully updated candidate representation
  const getUpdatedCandidate = (original: WikiCandidate): WikiCandidate => {
    const edits = editedCandidates[original.correction_id] || {};
    const updated = {
      ...original,
      ...edits
    } as WikiCandidate;

    // Recalculate status dynamically for the UI preview based on builder rule
    if (!updated.entity_name || !Array.isArray(updated.evidence)) {
      updated.status = 'invalid';
    } else if (!updated.summary || !updated.content) {
      updated.status = 'needs_human_fill';
    } else {
      updated.status = 'ready_for_review';
    }

    return updated;
  };

  const updateField = (id: string, field: keyof WikiCandidate, value: any) => {
    setEditedCandidates(prev => ({
      ...prev,
      [id]: {
        ...prev[id],
        [field]: value
      }
    }));
  };

  const handleAddAlias = (id: string) => {
    const aliasText = (newAlias[id] || "").trim();
    if (!aliasText) return;

    const currentEdits = editedCandidates[id] || {};
    const currentAliases = currentEdits.aliases || [];

    if (!currentAliases.includes(aliasText)) {
      updateField(id, 'aliases', [...currentAliases, aliasText]);
    }

    setNewAlias(prev => ({ ...prev, [id]: "" }));
  };

  const handleRemoveAlias = (id: string, indexToRemove: number) => {
    const currentEdits = editedCandidates[id] || {};
    const currentAliases = currentEdits.aliases || [];
    const updated = currentAliases.filter((_, idx) => idx !== indexToRemove);
    updateField(id, 'aliases', updated);
  };

  const handleCopyJSON = async (candidate: WikiCandidate) => {
    const fullCandidate = getUpdatedCandidate(candidate);
    try {
      await navigator.clipboard.writeText(JSON.stringify(fullCandidate, null, 2));
      setSuccess(`Đã copy JSON của thực thể "${fullCandidate.entity_name}" vào clipboard!`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError("Không thể copy vào clipboard.");
    }
  };

  const handleDownloadJSON = (candidate: WikiCandidate) => {
    const fullCandidate = getUpdatedCandidate(candidate);
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(fullCandidate, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `candidate_${fullCandidate.entity_name.replace(/\s+/g, '_').toLowerCase()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleSaveDraft = async (original: WikiCandidate) => {
    const id = original.correction_id;
    setSaving(prev => ({ ...prev, [id]: true }));
    setError(null);
    setSuccess(null);

    const updated = getUpdatedCandidate(original);

    const proposedPayload = {
      entity_name: updated.entity_name,
      entity_type: updated.entity_type === "Nhân vật" ? "character" :
                   updated.entity_type === "Sinh vật" ? "concept" :
                   updated.entity_type === "Thế lực" ? "faction" :
                   updated.entity_type === "Vật phẩm" ? "item" :
                   updated.entity_type === "Địa điểm" ? "location" : "unknown",
      summary: updated.summary,
      content: updated.content,
      aliases: updated.aliases,
      evidence: updated.evidence,
      source: "admin_edited_wiki_candidate",
      human_review_required: true,
      notes: "Edited by admin; not applied to wiki_entries."
    };

    try {
      const res = await fetch(`/api/oracle/corrections/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          status: "accepted", // maps to "approved" in database
          reviewer_note: "wiki candidate edited; not applied to wiki_entries",
          proposed_content: JSON.stringify(proposedPayload)
        })
      });

      if (res.ok) {
        setSuccess(`Đã lưu bản nháp của thực thể "${updated.entity_name}" thành công!`);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        if (res.status === 401) {
          setIsUnauthorized(true);
          setError("Bạn cần đăng nhập admin");
        } else {
          const err = await res.json().catch(() => ({}));
          setError(err.error || "Lỗi khi lưu bản nháp.");
        }
      }
    } catch (err) {
      setError("Lỗi kết nối server khi lưu bản nháp.");
    } finally {
      setSaving(prev => ({ ...prev, [id]: false }));
    }
  };

  return (
    <div className="max-w-6xl">
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
            <LibraryBig className="text-green-500" size={24} />
            ỨNG VIÊN WIKI ORACLE
          </h1>
          <p className="text-gray-500 text-sm font-mono mt-1">
            Xem xét các ứng viên Wiki được tổng hợp từ các sửa đổi đã duyệt.
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
          {/* Header Bar */}
          <div className="bg-[#181818] border border-gray-800 p-4 rounded-lg flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
            <div className="flex items-center gap-4">
              <span className="text-gray-400">
                Tổng cộng: <span className="text-green-400 font-bold">{candidates.length}</span> ứng viên được sinh.
              </span>
              <button
                onClick={() => loadCandidates()}
                disabled={loading}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-green-900/30 text-green-400 hover:bg-green-900/50 border border-green-800/40 rounded transition-colors cursor-pointer"
              >
                {loading ? <Loader2 className="animate-spin" size={12} /> : null}
                LÀM MỚI DANH SÁCH
              </button>
            </div>

            <div className="flex bg-[#0a0a0a] rounded p-0.5 border border-gray-800">
              <button
                onClick={() => setActiveTab('editor')}
                className={`px-3 py-1.5 rounded text-[10px] uppercase font-bold tracking-wider transition-all cursor-pointer ${activeTab === 'editor' ? 'bg-green-900/40 text-green-400' : 'text-gray-500 hover:text-gray-300'}`}
              >
                Giao diện sửa
              </button>
              <button
                onClick={() => setActiveTab('json_preview')}
                className={`px-3 py-1.5 rounded text-[10px] uppercase font-bold tracking-wider transition-all cursor-pointer ${activeTab === 'json_preview' ? 'bg-green-900/40 text-green-400' : 'text-gray-500 hover:text-gray-300'}`}
              >
                Xem JSON xuất
              </button>
            </div>
          </div>

          {/* LIST */}
          {loading && candidates.length === 0 ? (
            <div className="flex justify-center py-20">
              <Loader2 className="animate-spin text-green-500" size={36} />
            </div>
          ) : candidates.length === 0 ? (
            <div className="bg-[#181818] border border-gray-800 rounded-lg p-12 text-center text-gray-500 text-xs italic font-mono">
              Không có ứng viên Wiki nào sẵn sàng. Vui lòng phê duyệt (Approve) các bản nháp ở Dashboard "Bản nháp Oracle" rồi chạy script tổng hợp candidates.
            </div>
          ) : (
            <div className="grid gap-6">
              {candidates.map((original) => {
                const updated = getUpdatedCandidate(original);
                const edits = editedCandidates[original.correction_id] || {};
                const statusLabel = STATUS_LABELS[updated.status] || updated.status;
                const statusColor = STATUS_COLORS[updated.status] || "text-gray-400 bg-gray-900 border-gray-800";

                const isNeedsFill = !updated.summary || !updated.content;

                if (activeTab === 'json_preview') {
                  return (
                    <div key={original.correction_id} className="bg-[#181818] border border-gray-800 rounded-lg p-5 font-mono">
                      <div className="flex items-center justify-between border-b border-gray-800 pb-3 mb-4 text-xs">
                        <span className="text-gray-100 font-bold">{updated.entity_name}</span>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleCopyJSON(original)}
                            className="flex items-center gap-1.5 px-2.5 py-1 bg-green-950/40 text-green-400 hover:bg-green-900/40 border border-green-800/40 rounded transition-colors cursor-pointer"
                          >
                            <Copy size={12} /> COPY JSON
                          </button>
                          <button
                            onClick={() => handleDownloadJSON(original)}
                            className="flex items-center gap-1.5 px-2.5 py-1 bg-blue-950/40 text-blue-400 hover:bg-blue-900/40 border border-blue-800/40 rounded transition-colors cursor-pointer"
                          >
                            <Download size={12} /> TẢI FILE
                          </button>
                        </div>
                      </div>
                      <pre className="bg-[#0a0a0a] text-gray-300 p-4 rounded text-xs overflow-x-auto max-h-[400px]">
                        {JSON.stringify(updated, null, 2)}
                      </pre>
                    </div>
                  );
                }

                return (
                  <div 
                    key={original.correction_id} 
                    className="bg-[#181818] border border-gray-800 rounded-lg p-5 flex flex-col lg:flex-row gap-6 hover:border-gray-700 transition-all font-mono"
                  >
                    <div className="flex-1 space-y-4">
                      {/* Meta header */}
                      <div className="flex flex-wrap items-center gap-3 text-xs">
                        <span className="text-gray-100 font-bold text-sm tracking-wide">
                          {updated.entity_name}
                        </span>
                        <span className="text-gray-600">|</span>
                        <select
                          value={updated.entity_type}
                          onChange={(e) => updateField(original.correction_id, 'entity_type', e.target.value)}
                          className="bg-[#0a0a0a] border border-gray-800 rounded px-2 py-0.5 text-xs text-green-400 focus:border-green-500 outline-none capitalize"
                        >
                          {CATEGORIES.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                          ))}
                        </select>
                        <span className="text-gray-600">|</span>
                        <span className={`px-2 py-0.5 border rounded-full text-[10px] uppercase font-bold ${statusColor}`}>
                          {statusLabel}
                        </span>
                        {isNeedsFill && (
                          <>
                            <span className="text-gray-600">|</span>
                            <span className="px-2 py-0.5 border border-yellow-800/40 bg-yellow-950/20 text-yellow-400 rounded-full text-[10px] font-bold">
                              Cần người duyệt điền nội dung
                            </span>
                          </>
                        )}
                      </div>

                      {/* Editing fields */}
                      <div className="space-y-3">
                        <div className="space-y-1.5">
                          <label className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">
                            Tóm tắt ngắn (Summary)
                          </label>
                          <textarea
                            placeholder="Nhập tóm tắt một câu của thực thể..."
                            value={edits.summary ?? ""}
                            onChange={(e) => updateField(original.correction_id, 'summary', e.target.value)}
                            rows={2}
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded p-2 text-xs text-gray-200 focus:border-green-500 outline-none resize-none transition-all font-sans"
                          />
                        </div>

                        <div className="space-y-1.5">
                          <label className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">
                            Nội dung chi tiết (Content)
                          </label>
                          <textarea
                            placeholder="Nhập chi tiết về thực thể, vai trò, thuộc tính..."
                            value={edits.content ?? ""}
                            onChange={(e) => updateField(original.correction_id, 'content', e.target.value)}
                            rows={4}
                            className="w-full bg-[#0a0a0a] border border-gray-800 rounded p-2 text-xs text-gray-200 focus:border-green-500 outline-none resize-none transition-all font-sans"
                          />
                        </div>

                        {/* Aliases editing */}
                        <div className="space-y-1.5">
                          <label className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">
                            Tên gọi khác (Aliases)
                          </label>
                          <div className="flex flex-wrap gap-1.5 items-center mb-1.5">
                            {updated.aliases.map((alias, aliasIdx) => (
                              <span key={aliasIdx} className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-900 border border-gray-800 text-gray-300 rounded text-xs">
                                {alias}
                                <button
                                  onClick={() => handleRemoveAlias(original.correction_id, aliasIdx)}
                                  className="text-gray-500 hover:text-red-400 cursor-pointer"
                                >
                                  &times;
                                </button>
                              </span>
                            ))}
                            {updated.aliases.length === 0 && (
                              <span className="text-[10px] text-gray-600 italic">Không có biệt danh.</span>
                            )}
                          </div>
                          <div className="flex max-w-xs gap-1.5">
                            <input
                              type="text"
                              placeholder="Thêm biệt danh..."
                              value={newAlias[original.correction_id] || ""}
                              onChange={(e) => setNewAlias(prev => ({ ...prev, [original.correction_id]: e.target.value }))}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  handleAddAlias(original.correction_id);
                                }
                              }}
                              className="bg-[#0a0a0a] border border-gray-800 rounded px-2.5 py-1 text-xs text-gray-300 focus:border-green-500 outline-none flex-1 font-sans"
                            />
                            <button
                              onClick={() => handleAddAlias(original.correction_id)}
                              className="p-1.5 bg-gray-900 border border-gray-800 hover:bg-gray-800 text-gray-300 rounded cursor-pointer"
                            >
                              <Plus size={12} />
                            </button>
                          </div>
                        </div>

                        {/* Evidence section */}
                        {updated.evidence && updated.evidence.length > 0 && (
                          <div className="space-y-2 pt-2 border-t border-gray-900">
                            <div className="text-xs text-yellow-500 font-bold flex items-center gap-1.5">
                              <BookOpen size={12} /> BẰNG CHỨNG HỖ TRỢ ({updated.evidence.length} nguồn):
                            </div>
                            <div className="space-y-2 pl-4">
                              {updated.evidence.map((ev, evIdx) => (
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
                      </div>
                    </div>

                    {/* Action Block */}
                    <div className="w-full lg:w-60 shrink-0 flex flex-col justify-between border-t lg:border-t-0 lg:border-l border-gray-800 pt-4 lg:pt-0 lg:pl-6 space-y-4">
                      <div className="space-y-2 text-xs">
                        <div className="text-gray-500 uppercase tracking-widest text-[9px] font-bold">Metadata gốc</div>
                        <div className="bg-[#0a0a0a]/50 p-2.5 border border-gray-900 rounded space-y-1.5 text-[10px] text-gray-400">
                          <div>
                            <span className="text-gray-600">Correction ID:</span>
                            <div className="truncate font-mono text-[9px] select-all">{updated.correction_id}</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Nguồn gốc:</span>{" "}
                            <span className="capitalize">{updated.source}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Cần duyệt thủ công:</span>{" "}
                            <span>{updated.human_review_required ? "Có" : "Không"}</span>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <button
                          onClick={() => handleSaveDraft(original)}
                          disabled={saving[original.correction_id]}
                          className="w-full flex items-center justify-center gap-2 py-2.5 bg-yellow-950/30 text-yellow-400 hover:bg-yellow-900/40 border border-yellow-800/40 rounded text-[11px] font-bold tracking-wider transition-colors cursor-pointer disabled:opacity-50"
                        >
                          {saving[original.correction_id] ? (
                            <Loader2 className="animate-spin" size={12} />
                          ) : (
                            <CheckCircle2 size={12} />
                          )}
                          LƯU BẢN NHÁP
                        </button>
                        <button
                          onClick={() => handleCopyJSON(original)}
                          className="w-full flex items-center justify-center gap-2 py-2.5 bg-green-950/30 text-green-400 hover:bg-green-900/40 border border-green-800/40 rounded text-[11px] font-bold tracking-wider transition-colors cursor-pointer"
                        >
                          <Copy size={12} /> COPY CANDIDATE JSON
                        </button>
                        <button
                          onClick={() => handleDownloadJSON(original)}
                          className="w-full flex items-center justify-center gap-2 py-2.5 bg-blue-950/30 text-blue-400 hover:bg-blue-900/40 border border-blue-800/40 rounded text-[11px] font-bold tracking-wider transition-colors cursor-pointer"
                        >
                          <Download size={12} /> TẢI FILE PAYLOAD
                        </button>
                      </div>

                      <div className="text-[10px] text-gray-600 italic leading-snug border-t border-gray-900 pt-3">
                        Lưu ý: Không có nút "Apply to wiki". Các chỉnh sửa trên trang này sẽ được lưu lại vào bản nháp tri thức của hệ thống (RAG Corrections) khi nhấn "Lưu bản nháp".
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
