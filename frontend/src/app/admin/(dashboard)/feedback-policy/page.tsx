'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  MessageSquare,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  TrendingUp,
  XCircle,
  Clock,
  Eye,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
  Loader2,
  ShieldAlert
} from 'lucide-react';

interface FeedbackItem {
  id: string;
  provisional_id: string;
  record_name: string;
  feedback_type: string;
  user_comment: string;
  suggested_correction: string | null;
  page_url: string | null;
  user_agent: string | null;
  status: string;
  created_at: string;
}

interface SummaryItem {
  provisional_id: string;
  record_name: string;
  total_feedback: number;
  wrong_info_count: number;
  wrong_type_count: number;
  wrong_evidence_count: number;
  duplicate_count: number;
  spoiler_count: number;
  missing_info_count: number;
  other_count: number;
  unique_user_agent_count: number;
  dispute_score: number;
  effective_status: string;
  oracle_policy: string;
  top_comments: { comment: string; type: string }[];
  updated_at: string;
}

interface PatchItem {
  id: string;
  target_type: string;
  target_id: string | null;
  target_name: string | null;
  query_pattern: string | null;
  patch_type: string;
  effective_status: string;
  oracle_policy: string;
  effective_summary: string | null;
  effective_content: string | null;
  effective_type: string | null;
  evidence: any[];
  feedback_ids: string[];
  confidence: number;
  reason: string | null;
  created_by: string;
  created_at: string;
}

interface DashboardStats {
  feedback_total: number;
  summary_total: number;
  patch_active: number;
  warn_count: number;
  block_count: number;
  oracle_patch_active?: number;
}

interface OracleSummaryItem {
  query_pattern: string;
  total_feedback: number;
  shallow_count: number;
  misclassification_count: number;
  irrelevant_count: number;
  missing_entity_count: number;
  stale_cache_count: number;
  wrong_summary_count: number;
  too_mechanical_count: number;
  unknown_count: number;
  top_comments: { comment: string; created_at: string }[];
  updated_at: string;
}

interface OraclePatchItem {
  id: string;
  issue_type: string;
  query_pattern: string;
  target_entity: string | null;
  target_intent: string | null;
  patch_type: string;
  policy: any;
  effective_status: string;
  confidence: number;
  source_feedback_ids: string[];
  reason: string | null;
  created_at: string;
  updated_at: string;
}

const FEEDBACK_TYPE_LABELS: Record<string, string> = {
  wrong_info: "Sai thông tin",
  wrong_type: "Sai phân loại",
  wrong_evidence: "Sai minh chứng",
  duplicate: "Trùng lặp mục",
  spoiler: "Tiết lộ cốt truyện (Spoiler)",
  missing_info: "Thiếu thông tin quan trọng",
  other: "Khác"
};

const POLICY_BADGES: Record<string, { label: string; style: string }> = {
  allow: { label: "Allow (Cho phép)", style: "text-green-400 bg-green-950/20 border-green-800/40" },
  trusted: { label: "Trusted (Tin cậy)", style: "text-green-400 bg-green-950/20 border-green-800/40" },
  warn: { label: "Warn (Cảnh báo)", style: "text-yellow-400 bg-yellow-950/20 border-yellow-800/40" },
  disputed: { label: "Disputed (Tranh chấp)", style: "text-yellow-400 bg-yellow-950/20 border-yellow-800/40" },
  deprioritize: { label: "Deprioritize (Hạ độ ưu tiên)", style: "text-orange-400 bg-orange-950/20 border-orange-800/40" },
  needs_review: { label: "Needs Review (Cần xem xét)", style: "text-orange-400 bg-orange-950/20 border-orange-800/40" },
  block: { label: "Block (Chặn hiển thị)", style: "text-red-400 bg-red-950/20 border-red-800/40" },
  hidden_from_oracle: { label: "Hidden (Ẩn khỏi Oracle)", style: "text-red-400 bg-red-950/20 border-red-800/40" },
  active: { label: "Active (Hoạt động)", style: "text-green-400 bg-green-950/20 border-green-800/40" },
  disabled: { label: "Disabled (Đã tắt)", style: "text-red-400 bg-red-950/20 border-red-800/40" }
};

interface PipelineHealth {
  last_run_at: string | null;
  last_run_ok: boolean;
  last_run_errors: string[];
  hours_since_last_run: number;
  pipeline_stale: boolean;
  recent_failures: number;
  pending_feedbacks: number;
  last_run_feedback_read: number;
  last_run_summaries_written: number;
  last_run_patches_written: number;
  last_run_cache_deleted: number;
  last_run_dry_run: boolean;
}

export default function AdminFeedbackPolicyDashboard() {
  const router = useRouter();

  // State variables
  const [feedbackRecent, setFeedbackRecent] = useState<FeedbackItem[]>([]);
  const [summaries, setSummaries] = useState<SummaryItem[]>([]);
  const [patches, setPatches] = useState<PatchItem[]>([]);
  const [oracleSummaries, setOracleSummaries] = useState<OracleSummaryItem[]>([]);
  const [oraclePatches, setOraclePatches] = useState<OraclePatchItem[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    feedback_total: 0,
    summary_total: 0,
    patch_active: 0,
    warn_count: 0,
    block_count: 0,
    oracle_patch_active: 0
  });
  const [health, setHealth] = useState<PipelineHealth | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUnauthorized, setIsUnauthorized] = useState(false);
  const [activeTab, setActiveTab] = useState<'feedback' | 'summaries' | 'patches' | 'oracle_summaries' | 'oracle_patches'>('feedback');
  
  // Selected detail modal/expand states
  const [expandedComments, setExpandedComments] = useState<Record<string, boolean>>({});

  // Patch control and filtering states
  const [patchFilter, setPatchFilter] = useState<'all' | 'active' | 'disabled'>('all');
  const [actioningPatchId, setActioningPatchId] = useState<string | null>(null);
  const [reviewerNote, setReviewerNote] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);


  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    setIsUnauthorized(false);

    try {
      const res = await fetch('/api/oracle/feedback-policy-dashboard');
      if (res.ok) {
        const data = await res.json();
        setFeedbackRecent(data.feedback_recent || []);
        setSummaries(data.summaries || []);
        setPatches(data.patches || []);
        setOracleSummaries(data.oracle_summaries || []);
        setOraclePatches(data.oracle_patches || []);
        setStats(data.stats || {
          feedback_total: 0,
          summary_total: 0,
          patch_active: 0,
          warn_count: 0,
          block_count: 0,
          oracle_patch_active: 0
        });
        setHealth(data.health || null);
      } else {
        if (res.status === 401) {
          setIsUnauthorized(true);
          setError("Bạn cần đăng nhập admin để xem dữ liệu này.");
        } else {
          const err = await res.json().catch(() => ({}));
          setError(err.error || "Không thể tải dữ liệu vòng tự học.");
        }
      }
    } catch (err) {
      setError("Lỗi kết nối server khi tải dữ liệu.");
    } finally {
      setLoading(false);
    }
  };

  const toggleExpandComment = (id: string) => {
    setExpandedComments(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleUpdatePatchStatus = async (patchId: string, action: 'disable' | 'restore', note: string) => {
    setActionLoading(true);
    setActionError(null);
    setActionSuccess(null);

    try {
      const res = await fetch(`/api/oracle/feedback-policy-dashboard/patches/${patchId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action,
          reviewer_note: note,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const successMessage = action === 'disable'
          ? `Đã tắt bản vá thành công. Vô hiệu hóa ảnh hưởng lên RAG & xóa ${data.cache_cleared_count} cache liên quan.`
          : `Đã khôi phục hoạt động bản vá thành công & xóa ${data.cache_cleared_count} cache liên quan.`;

        setActionSuccess(successMessage);
        setActioningPatchId(null);
        setReviewerNote('');

        // Reload dashboard data to refresh UI status and counters
        await loadDashboardData();

        setTimeout(() => setActionSuccess(null), 5000);
      } else {
        const err = await res.json().catch(() => ({}));
        setActionError(err.error || "Không thể cập nhật trạng thái bản vá.");
      }
    } catch (err) {
      setActionError("Lỗi kết nối khi gửi yêu cầu cập nhật bản vá.");
    } finally {
      setActionLoading(false);
    }
  };


  const getPolicyBadge = (policyKey: string) => {
    const badge = POLICY_BADGES[policyKey] || { label: policyKey, style: "text-gray-400 bg-gray-900 border-gray-800" };
    return (
      <span className={`px-2 py-0.5 border rounded-full text-[9px] uppercase font-bold tracking-wider ${badge.style}`}>
        {badge.label}
      </span>
    );
  };

  if (isUnauthorized) {
    return (
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
    );
  }

  return (
    <div className="max-w-6xl space-y-6">
      {/* Header section */}
      <div className="mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
            <RefreshCw className="text-green-500 animate-pulse" size={24} />
            VÒNG TỰ HỌC CỘNG ĐỒNG (SELF-LEARNING)
          </h1>
          <p className="text-gray-500 text-sm font-mono mt-1">
            Hệ thống tự động hóa xử lý phản hồi từ độc giả, tổng hợp độ tin cậy và tạo bản vá kiến thức (Knowledge Patches).
          </p>
        </div>
      </div>

      {/* High-visibility Warning/Explanation banner */}
      <div className="flex items-start gap-3 text-blue-400 bg-blue-950/20 border border-blue-800/40 rounded-lg p-4 text-xs font-mono leading-relaxed">
        <ShieldCheck className="shrink-0 mt-0.5" size={16} />
        <div>
          <span className="font-bold uppercase">GIÁM SÁT VÒNG TỰ HỌC (READ-ONLY):</span> Bản điều khiển này giúp admin quan sát luồng tự học khép kín: 
          độc giả gửi phản hồi qua Chatbot &rarr; hệ thống tổng hợp chỉ số tranh chấp &rarr; tạo bản vá kiến thức động điều hướng RAG. 
          Không tích hợp nút apply vào `wiki_entries` hay chỉnh sửa trực tiếp cơ sở dữ liệu `provisional_library` để tuân thủ quy tắc an toàn canon.
        </div>
      </div>

      {/* Pipeline Observability / Health Section */}
      {health && (
        <div className="bg-[#181818] border border-gray-800 rounded-lg p-5 font-mono text-xs space-y-4">
          <div className="flex items-center justify-between border-b border-gray-900 pb-3">
            <h2 className="text-sm font-bold text-gray-200 tracking-wider flex items-center gap-2 uppercase">
              <Cpu className={health.last_run_ok && !health.pipeline_stale ? "text-green-500 animate-pulse" : "text-red-500"} size={16} />
              Tình trạng pipeline tự học
            </h2>
            <div className="flex items-center gap-2">
              <span className="text-gray-500">Lần chạy gần nhất:</span>
              {health.last_run_at ? (
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  health.last_run_ok
                    ? "bg-green-950/40 text-green-400 border border-green-900/30"
                    : "bg-red-950/40 text-red-400 border border-red-900/30"
                }`}>
                  {health.last_run_ok ? "OK" : "FAIL"}
                </span>
              ) : (
                <span className="text-gray-400 italic">Chưa có dữ liệu</span>
              )}
            </div>
          </div>

          {/* Stale Alert */}
          {health.pipeline_stale && (
            <div className="flex items-start gap-2.5 text-red-400 bg-red-950/20 border border-red-900/40 rounded p-3 leading-relaxed">
              <AlertTriangle className="shrink-0 mt-0.5" size={16} />
              <div>
                <span className="font-bold uppercase">CẢNH BÁO PIPELINE BỊ ĐÌNH TRỆ:</span> Pipeline tự học đã không hoạt động trong {health.hours_since_last_run ? health.hours_since_last_run.toFixed(1) : "N/A"} giờ qua (lần chạy cuối: {health.last_run_at ? new Date(health.last_run_at).toLocaleString('vi-VN') : 'N/A'}). Vui lòng kiểm tra lại scheduled workflow trên GitHub Actions.
              </div>
            </div>
          )}

          {/* Failure Alert */}
          {!health.last_run_ok && health.last_run_errors.length > 0 && (
            <div className="flex items-start gap-2.5 text-red-400 bg-red-950/20 border border-red-900/40 rounded p-3 leading-relaxed">
              <ShieldAlert className="shrink-0 mt-0.5" size={16} />
              <div>
                <span className="font-bold uppercase">LỖI PIPELINE GẦN NHẤT:</span> Lần chạy cuối gặp sự cố nghiêm trọng:
                <ul className="list-disc pl-4 mt-1 space-y-1">
                  {health.last_run_errors.map((err, idx) => (
                    <li key={idx} className="select-all">{err}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Details Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-4">
            <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider">Lần chạy cuối</div>
              <div className="text-gray-200 mt-1 font-bold">
                {health.last_run_at ? new Date(health.last_run_at).toLocaleTimeString('vi-VN') : "N/A"}
              </div>
              <div className="text-[9px] text-gray-600 mt-0.5">
                {health.last_run_at ? new Date(health.last_run_at).toLocaleDateString('vi-VN') : ""}
              </div>
            </div>

            <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider">Feedback đã đọc</div>
              <div className="text-gray-200 mt-1 font-bold text-sm">
                {health.last_run_feedback_read} rows
              </div>
              <div className="text-[9px] text-gray-600 mt-0.5">
                Chờ xử lý: {health.pending_feedbacks}
              </div>
            </div>

            <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider">Summary đã ghi</div>
              <div className="text-gray-200 mt-1 font-bold text-sm">
                {health.last_run_summaries_written} rows
              </div>
              <div className="text-[9px] text-gray-600 mt-0.5">
                Mode: {health.last_run_dry_run ? "Simulated" : "Supabase Commit"}
              </div>
            </div>

            <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider">Bản vá (Patch) mới</div>
              <div className="text-green-400 mt-1 font-bold text-sm">
                +{health.last_run_patches_written} patches
              </div>
              <div className="text-[9px] text-gray-600 mt-0.5">
                Tổng active: {stats.patch_active}
              </div>
            </div>

            <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3 col-span-2 sm:col-span-1">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider">Xóa RAG Cache</div>
              <div className="text-gray-200 mt-1 font-bold text-sm">
                {health.last_run_cache_deleted > 0 ? `Đã xóa ${health.last_run_cache_deleted}` : "Không xóa"}
              </div>
              <div className="text-[9px] text-gray-600 mt-0.5">
                {health.last_run_dry_run ? "Dry-run bypass" : "Dynamic target clear"}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider">Tổng phản hồi</div>
            <div className="text-xl font-bold text-gray-100 mt-1">
              {loading ? <Loader2 className="animate-spin text-green-500 inline" size={16} /> : stats.feedback_total}
            </div>
          </div>
          <MessageSquare className="text-green-500/25" size={24} />
        </div>

        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider">Concept tranh chấp</div>
            <div className="text-xl font-bold text-yellow-400 mt-1">
              {loading ? <Loader2 className="animate-spin text-green-500 inline" size={16} /> : stats.summary_total}
            </div>
          </div>
          <AlertTriangle className="text-yellow-500/25" size={24} />
        </div>

        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider">Bản vá đang hoạt động</div>
            <div className="text-xl font-bold text-green-400 mt-1">
              {loading ? <Loader2 className="animate-spin text-green-500 inline" size={16} /> : stats.patch_active}
            </div>
          </div>
          <ShieldCheck className="text-green-500/25" size={24} />
        </div>

        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider">Cảnh báo (Warn)</div>
            <div className="text-xl font-bold text-orange-400 mt-1">
              {loading ? <Loader2 className="animate-spin text-green-500 inline" size={16} /> : stats.warn_count}
            </div>
          </div>
          <TrendingUp className="text-orange-500/25" size={24} />
        </div>

        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider">Chặn (Block)</div>
            <div className="text-xl font-bold text-red-500 mt-1">
              {loading ? <Loader2 className="animate-spin text-green-500 inline" size={16} /> : stats.block_count}
            </div>
          </div>
          <XCircle className="text-red-500/25" size={24} />
        </div>

        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider">Bản vá Oracle RAG</div>
            <div className="text-xl font-bold text-blue-400 mt-1">
              {loading ? <Loader2 className="animate-spin text-green-500 inline" size={16} /> : (stats.oracle_patch_active || 0)}
            </div>
          </div>
          <Cpu className="text-blue-500/25" size={24} />
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex flex-wrap border-b border-gray-800 font-mono text-xs">
        <button
          onClick={() => setActiveTab('feedback')}
          className={`px-4 py-2.5 font-bold transition-all border-b-2 cursor-pointer ${
            activeTab === 'feedback'
              ? 'border-green-500 text-green-400 bg-green-950/10'
              : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          Ý kiến độc giả ({feedbackRecent.length})
        </button>
        <button
          onClick={() => setActiveTab('summaries')}
          className={`px-4 py-2.5 font-bold transition-all border-b-2 cursor-pointer ${
            activeTab === 'summaries'
              ? 'border-green-500 text-green-400 bg-green-950/10'
              : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          Tranh chấp Concept ({summaries.length})
        </button>
        <button
          onClick={() => setActiveTab('patches')}
          className={`px-4 py-2.5 font-bold transition-all border-b-2 cursor-pointer ${
            activeTab === 'patches'
              ? 'border-green-500 text-green-400 bg-green-950/10'
              : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          Bản vá Concept ({patches.length})
        </button>
        <button
          onClick={() => setActiveTab('oracle_summaries')}
          className={`px-4 py-2.5 font-bold transition-all border-b-2 cursor-pointer ${
            activeTab === 'oracle_summaries'
              ? 'border-green-500 text-green-400 bg-green-950/10'
              : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          Tranh chấp Oracle RAG ({oracleSummaries.length})
        </button>
        <button
          onClick={() => setActiveTab('oracle_patches')}
          className={`px-4 py-2.5 font-bold transition-all border-b-2 cursor-pointer ${
            activeTab === 'oracle_patches'
              ? 'border-green-500 text-green-400 bg-green-950/10'
              : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          Bản vá Oracle RAG ({oraclePatches.length})
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex items-center gap-2 text-red-400 bg-red-950/20 border border-red-900/50 rounded-lg p-4 text-xs font-mono">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {actionSuccess && (
        <div className="flex items-center gap-2 text-green-400 bg-green-950/20 border border-green-900/50 rounded-lg p-4 text-xs font-mono animate-in fade-in duration-200">
          <CheckCircle2 size={16} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {actionError && (
        <div className="flex items-center gap-2 text-red-400 bg-red-950/20 border border-red-900/50 rounded-lg p-4 text-xs font-mono animate-in fade-in duration-200">
          <AlertTriangle size={16} />
          <span>{actionError}</span>
        </div>
      )}


      {/* Tab Content Panels */}
      {loading ? (
        <div className="flex justify-center items-center py-24">
          <Loader2 className="animate-spin text-green-500" size={36} />
        </div>
      ) : (
        <div className="space-y-4">
          
          {/* TAB 1: Recent Feedbacks */}
          {activeTab === 'feedback' && (
            <div className="space-y-3 font-mono">
              <div className="text-xs text-gray-500 px-1">
                Hiển thị tối đa 50 phản hồi cộng đồng nhận được gần đây nhất.
              </div>

              {feedbackRecent.length === 0 ? (
                <div className="bg-[#181818] border border-gray-800 rounded-lg p-8 text-center text-gray-500 text-xs italic">
                  Không tìm thấy phản hồi cộng đồng nào.
                </div>
              ) : (
                <div className="grid gap-3">
                  {feedbackRecent.map((item) => {
                    const isExpanded = expandedComments[item.id] || false;
                    return (
                      <div
                        key={item.id}
                        className="bg-[#181818] border border-gray-800 rounded-lg p-4 space-y-3 hover:border-gray-700 transition-all text-xs"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-gray-100 font-bold text-sm font-sans">{item.record_name}</span>
                            <span className="text-gray-600">/</span>
                            <span className="text-gray-400 font-bold">{FEEDBACK_TYPE_LABELS[item.feedback_type] || item.feedback_type}</span>
                            <span className="text-gray-600">|</span>
                            <span className="px-1.5 py-0.2 bg-gray-900 text-gray-400 rounded text-[9px] uppercase">
                              id: {item.provisional_id?.slice(0, 8)}...
                            </span>
                          </div>
                          <div className="text-[10px] text-gray-500 flex items-center gap-1.5">
                            <Clock size={10} />
                            <span>{new Date(item.created_at).toLocaleString('vi-VN')}</span>
                          </div>
                        </div>

                        <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3 text-gray-300 font-sans leading-relaxed">
                          <div className="text-gray-500 font-mono text-[9px] uppercase tracking-wider mb-1">Ý kiến đóng góp:</div>
                          "{item.user_comment}"
                        </div>

                        {item.suggested_correction && (
                          <div className="bg-[#0f0f15] border border-blue-950/40 rounded p-3 text-gray-300 font-sans leading-relaxed">
                            <div className="text-blue-500 font-mono text-[9px] uppercase tracking-wider mb-1">Đề xuất sửa đổi:</div>
                            "{item.suggested_correction}"
                          </div>
                        )}

                        <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1 border-t border-gray-900/60">
                          <div className="truncate max-w-[350px]">
                            URL: <span className="text-gray-400 select-all font-sans">{item.page_url || 'N/A'}</span>
                          </div>
                          
                          <button
                            onClick={() => toggleExpandComment(item.id)}
                            className="flex items-center gap-1 px-2.5 py-0.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-[9px] tracking-wider transition-colors cursor-pointer"
                          >
                            <Eye size={10} /> {isExpanded ? "ẨN META" : "CHI TIẾT META"}
                          </button>
                        </div>

                        {isExpanded && (
                          <div className="bg-[#0c0c0c] border border-gray-900 rounded p-3 space-y-1 font-mono text-[10px] text-gray-400 animate-in fade-in duration-150">
                            <div>User Agent: <span className="text-gray-300 select-all font-sans">{item.user_agent || 'N/A'}</span></div>
                            <div>System UUID: <span className="text-gray-300 select-all">{item.id}</span></div>
                            <div>Status: <span className="text-green-400 font-bold">{item.status}</span></div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Aggregated Summaries */}
          {activeTab === 'summaries' && (
            <div className="space-y-3 font-mono">
              <div className="text-xs text-gray-500 px-1">
                Concept tranh chấp được tính toán dispute score và oracle policy từ cộng đồng (sắp xếp theo dispute_score giảm dần).
              </div>

              {summaries.length === 0 ? (
                <div className="bg-[#181818] border border-gray-800 rounded-lg p-8 text-center text-gray-500 text-xs italic">
                  Không tìm thấy concept tranh chấp tổng hợp nào.
                </div>
              ) : (
                <div className="grid gap-3">
                  {summaries.map((item) => (
                    <div
                      key={item.provisional_id}
                      className="bg-[#181818] border border-gray-800 rounded-lg p-5 space-y-4 hover:border-gray-700 transition-all text-xs"
                    >
                      {/* Concept meta header */}
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex flex-wrap items-center gap-3">
                          <span className="text-gray-100 font-bold text-base font-sans">{item.record_name}</span>
                          <span className="text-gray-600">/</span>
                          <span className="text-gray-400">UUID: <span className="select-all">{item.provisional_id}</span></span>
                        </div>

                        <div className="flex flex-wrap items-center gap-2">
                          <span>Status:</span> {getPolicyBadge(item.effective_status)}
                          <span className="text-gray-600">|</span>
                          <span>Policy:</span> {getPolicyBadge(item.oracle_policy)}
                        </div>
                      </div>

                      {/* Score grid */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3 bg-[#0f0f0f] border border-gray-900 rounded p-3 text-[10px] text-gray-400">
                        <div>
                          Phản hồi: <span className="text-gray-200 font-bold">{item.total_feedback}</span>
                        </div>
                        <div>
                          Sai thông tin: <span className="text-gray-200 font-bold">{item.wrong_info_count}</span>
                        </div>
                        <div>
                          Sai minh chứng: <span className="text-gray-200 font-bold">{item.wrong_evidence_count}</span>
                        </div>
                        <div>
                          Tiết lộ truyện: <span className="text-gray-200 font-bold">{item.spoiler_count}</span>
                        </div>
                        <div>
                          Trùng lặp: <span className="text-gray-200 font-bold">{item.duplicate_count}</span>
                        </div>
                        <div className="border-l border-gray-900 pl-2">
                          Dispute Score: <span className="text-yellow-400 font-bold text-xs">{item.dispute_score.toFixed(2)}</span>
                        </div>
                      </div>

                      {/* Top comments preview */}
                      {item.top_comments && item.top_comments.length > 0 && (
                        <div className="space-y-2">
                          <div className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Ý kiến hàng đầu:</div>
                          <div className="space-y-1.5 font-sans pl-2 border-l border-green-800/40">
                            {item.top_comments.slice(0, 3).map((cmt, idx) => (
                              <div key={idx} className="text-gray-300 text-xs">
                                <span className="font-mono text-[10px] text-gray-500 mr-2">[{FEEDBACK_TYPE_LABELS[cmt.type] || cmt.type}]</span>
                                "{cmt.comment}"
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Effective Patches */}
          {activeTab === 'patches' && (
            <div className="space-y-3 font-mono">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-1">
                <div className="text-xs text-gray-500">
                  Các bản vá kiến thức động (Knowledge Patches) đang hoạt động điều hướng luồng truy vấn chatbot RAG.
                </div>

                {/* Status Filter */}
                <div className="flex items-center gap-1.5 bg-[#121212] border border-gray-800 rounded p-1 text-[10px] text-gray-400 self-start sm:self-auto">
                  <span className="pl-1 uppercase tracking-wider font-bold">Lọc:</span>
                  <button
                    onClick={() => setPatchFilter('all')}
                    className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                      patchFilter === 'all'
                        ? 'bg-green-600 text-white font-bold'
                        : 'hover:text-gray-200'
                    }`}
                  >
                    Tất cả
                  </button>
                  <button
                    onClick={() => setPatchFilter('active')}
                    className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                      patchFilter === 'active'
                        ? 'bg-green-600 text-white font-bold'
                        : 'hover:text-gray-200'
                    }`}
                  >
                    Hoạt động
                  </button>
                  <button
                    onClick={() => setPatchFilter('disabled')}
                    className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                      patchFilter === 'disabled'
                        ? 'bg-green-600 text-white font-bold'
                        : 'hover:text-gray-200'
                    }`}
                  >
                    Đã tắt
                  </button>
                </div>
              </div>

              {(() => {
                const filteredPatches = patches.filter(item => {
                  if (patchFilter === 'active') return item.effective_status === 'active';
                  if (patchFilter === 'disabled') return item.effective_status === 'disabled';
                  return true;
                });

                if (filteredPatches.length === 0) {
                  return (
                    <div className="bg-[#181818] border border-gray-800 rounded-lg p-8 text-center text-gray-500 text-xs italic">
                      Không tìm thấy bản vá kiến thức nào phù hợp bộ lọc.
                    </div>
                  );
                }

                return (
                  <div className="grid gap-3">
                    {filteredPatches.map((item) => (
                      <div
                        key={item.id}
                        className="bg-[#181818] border border-gray-800 rounded-lg p-5 space-y-4 hover:border-gray-700 transition-all text-xs"
                      >
                        {/* Patch title row */}
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div className="flex flex-wrap items-center gap-3">
                            <span className="px-2 py-0.5 bg-green-950/30 text-green-400 border border-green-900/30 rounded text-[10px] uppercase font-bold tracking-wider">
                              {item.patch_type}
                            </span>
                            <span className="text-gray-100 font-bold text-sm font-sans">
                              {item.target_name || item.query_pattern || "Bản vá không tên"}
                            </span>
                            <span className="text-gray-600">/</span>
                            <span className="text-gray-400">Target: {item.target_type}</span>
                          </div>

                          <div className="flex flex-wrap items-center gap-2">
                            <span>Status:</span> {getPolicyBadge(item.effective_status)}
                            <span className="text-gray-600">|</span>
                            <span>Policy:</span> {getPolicyBadge(item.oracle_policy)}
                          </div>
                        </div>

                        {/* Patch content override info */}
                        {(item.effective_summary || item.effective_type) && (
                          <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3.5 space-y-2 text-xs leading-relaxed font-sans text-gray-300">
                            <div className="text-[10px] font-mono text-green-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
                              <CheckCircle2 size={12} />
                              Nội dung bản vá điều chỉnh:
                            </div>
                            {item.effective_type && (
                              <div>Phân loại điều chỉnh: <span className="font-mono text-yellow-500 text-xs">{item.effective_type}</span></div>
                            )}
                            {item.effective_summary && (
                              <div>Tóm tắt điều chỉnh: <span className="text-gray-100 italic">"{item.effective_summary}"</span></div>
                            )}
                          </div>
                        )}

                        {/* Patch metadata footer */}
                        <div className="flex flex-wrap items-center justify-between gap-3 text-[10px] text-gray-500 pt-2 border-t border-gray-900/60">
                          <div>
                            Lý do tạo: <span className="text-gray-300 font-sans italic">{item.reason || "N/A"}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span>Tạo bởi: <span className="text-gray-400">{item.created_by}</span></span>
                            <span>|</span>
                            <span>{new Date(item.created_at).toLocaleString('vi-VN')}</span>
                          </div>
                        </div>

                        {/* Inline Admin Emergency Override Controls */}
                        <div className="pt-3 border-t border-gray-900/60 flex flex-col gap-2">
                          {actioningPatchId === item.id ? (
                            <div className="p-3 bg-[#121212] border border-gray-900 rounded space-y-2.5 animate-in fade-in duration-200">
                              <div className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">
                                Ghi chú người duyệt / Lý do kiểm toán (Reviewer Note):
                              </div>
                              <input
                                type="text"
                                value={reviewerNote}
                                onChange={(e) => setReviewerNote(e.target.value)}
                                placeholder="Nhập lý do ngắn (bắt buộc)..."
                                className="w-full bg-[#0c0c0c] border border-gray-800 rounded px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-green-500 font-sans"
                                disabled={actionLoading}
                              />
                              <div className="flex justify-end gap-2">
                                <button
                                  onClick={() => {
                                    setActioningPatchId(null);
                                    setReviewerNote('');
                                  }}
                                  className="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-[10px] font-bold cursor-pointer transition-colors"
                                  disabled={actionLoading}
                                >
                                  HỦY BỎ
                                </button>
                                {item.effective_status === 'disabled' ? (
                                  <button
                                    onClick={() => handleUpdatePatchStatus(item.id, 'restore', reviewerNote)}
                                    disabled={!reviewerNote.trim() || actionLoading}
                                    className="px-3 py-1 bg-green-600 hover:bg-green-500 text-white rounded text-[10px] font-bold disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors flex items-center gap-1"
                                  >
                                    {actionLoading && <Loader2 className="animate-spin" size={10} />}
                                    KHÔI PHỤC BẢN VÁ
                                  </button>
                                ) : (
                                  <button
                                    onClick={() => handleUpdatePatchStatus(item.id, 'disable', reviewerNote)}
                                    disabled={!reviewerNote.trim() || actionLoading}
                                    className="px-3 py-1 bg-red-600 hover:bg-red-500 text-white rounded text-[10px] font-bold disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors flex items-center gap-1"
                                  >
                                    {actionLoading && <Loader2 className="animate-spin" size={10} />}
                                    XÁC NHẬN TẮT
                                  </button>
                                )}
                              </div>
                            </div>
                          ) : (
                            <div className="flex justify-end">
                              {item.effective_status === 'disabled' ? (
                                <button
                                  onClick={() => {
                                    setActioningPatchId(item.id);
                                    setReviewerNote('');
                                  }}
                                  className="px-3 py-1 border border-green-800/40 text-green-400 hover:bg-green-950/20 hover:border-green-600 rounded text-[10px] font-bold transition-all cursor-pointer"
                                >
                                  KHÔI PHỤC BẢN VÁ
                                </button>
                              ) : (
                                <button
                                  onClick={() => {
                                    setActioningPatchId(item.id);
                                    setReviewerNote('');
                                  }}
                                  className="px-3 py-1 border border-red-800/40 text-red-400 hover:bg-red-950/20 hover:border-red-600 rounded text-[10px] font-bold transition-all cursor-pointer"
                                >
                                  TẮT BẢN VÁ
                                </button>
                              )}
                            </div>
                          )}
                        </div>

                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>
          )}

          {/* TAB 4: Oracle Summaries */}
          {activeTab === 'oracle_summaries' && (
            <div className="space-y-3 font-mono">
              <div className="text-xs text-gray-500 px-1">
                Các câu hỏi/chủ đề bị độc giả phản hồi lỗi câu trả lời RAG, được gom nhóm và phân tích.
              </div>

              {oracleSummaries.length === 0 ? (
                <div className="bg-[#181818] border border-gray-800 rounded-lg p-8 text-center text-gray-500 text-xs italic">
                  Không tìm thấy phản hồi Oracle RAG tổng hợp nào.
                </div>
              ) : (
                <div className="grid gap-3">
                  {oracleSummaries.map((item) => (
                    <div
                      key={item.query_pattern}
                      className="bg-[#181818] border border-gray-800 rounded-lg p-5 space-y-4 hover:border-gray-700 transition-all text-xs"
                    >
                      {/* Query pattern header */}
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex flex-wrap items-center gap-3">
                          <span className="text-gray-100 font-bold text-base font-sans select-all">"{item.query_pattern}"</span>
                        </div>
                        <div className="text-[10px] text-gray-500 flex items-center gap-1.5">
                          <Clock size={10} />
                          <span>Cập nhật: {new Date(item.updated_at).toLocaleString('vi-VN')}</span>
                        </div>
                      </div>

                      {/* Issue classification counts */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2 bg-[#0f0f0f] border border-gray-900 rounded p-3 text-[10px] text-gray-400">
                        <div>
                          Tổng phản hồi: <span className="text-gray-200 font-bold">{item.total_feedback}</span>
                        </div>
                        <div>
                          Sơ sài: <span className="text-gray-200 font-bold">{item.shallow_count}</span>
                        </div>
                        <div>
                          Sai intent: <span className="text-gray-200 font-bold">{item.misclassification_count}</span>
                        </div>
                        <div>
                          Lan man: <span className="text-gray-200 font-bold">{item.irrelevant_count}</span>
                        </div>
                        <div>
                          Thiếu entity: <span className="text-gray-200 font-bold">{item.missing_entity_count}</span>
                        </div>
                        <div>
                          Stale cache: <span className="text-gray-200 font-bold">{item.stale_cache_count}</span>
                        </div>
                        <div>
                          Máy móc: <span className="text-gray-200 font-bold">{item.too_mechanical_count}</span>
                        </div>
                        <div>
                          Khác: <span className="text-gray-200 font-bold">{item.unknown_count}</span>
                        </div>
                      </div>

                      {/* Top comments */}
                      {item.top_comments && item.top_comments.length > 0 && (
                        <div className="space-y-2">
                          <div className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Ý kiến đóng góp:</div>
                          <div className="space-y-1.5 font-sans pl-2 border-l border-green-800/40">
                            {item.top_comments.map((cmt, idx) => (
                              <div key={idx} className="text-gray-300 text-xs">
                                "{cmt.comment}"
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 5: Oracle Patches */}
          {activeTab === 'oracle_patches' && (
            <div className="space-y-3 font-mono">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-1">
                <div className="text-xs text-gray-500">
                  Các bản vá (policy patches) tự học dành cho Chatbot Oracle RAG giúp tự động điều chỉnh retrieval/prompts.
                </div>

                {/* Status Filter */}
                <div className="flex items-center gap-1.5 bg-[#121212] border border-gray-800 rounded p-1 text-[10px] text-gray-400 self-start sm:self-auto">
                  <span className="pl-1 uppercase tracking-wider font-bold">Lọc:</span>
                  <button
                    onClick={() => setPatchFilter('all')}
                    className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                      patchFilter === 'all'
                        ? 'bg-green-600 text-white font-bold'
                        : 'hover:text-gray-200'
                    }`}
                  >
                    Tất cả
                  </button>
                  <button
                    onClick={() => setPatchFilter('active')}
                    className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                      patchFilter === 'active'
                        ? 'bg-green-600 text-white font-bold'
                        : 'hover:text-gray-200'
                    }`}
                  >
                    Hoạt động
                  </button>
                  <button
                    onClick={() => setPatchFilter('disabled')}
                    className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                      patchFilter === 'disabled'
                        ? 'bg-green-600 text-white font-bold'
                        : 'hover:text-gray-200'
                    }`}
                  >
                    Đã tắt
                  </button>
                </div>
              </div>

              {(() => {
                const filteredPatches = oraclePatches.filter(item => {
                  if (patchFilter === 'active') return item.effective_status === 'active';
                  if (patchFilter === 'disabled') return item.effective_status === 'disabled';
                  return true;
                });

                if (filteredPatches.length === 0) {
                  return (
                    <div className="bg-[#181818] border border-gray-800 rounded-lg p-8 text-center text-gray-500 text-xs italic">
                      Không tìm thấy bản vá Oracle nào phù hợp bộ lọc.
                    </div>
                  );
                }

                return (
                  <div className="grid gap-3">
                    {filteredPatches.map((item) => (
                      <div
                        key={item.id}
                        className="bg-[#181818] border border-gray-800 rounded-lg p-5 space-y-4 hover:border-gray-700 transition-all text-xs"
                      >
                        {/* Patch title row */}
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div className="flex flex-wrap items-center gap-3">
                            <span className="px-2 py-0.5 bg-blue-950/30 text-blue-400 border border-blue-900/30 rounded text-[10px] uppercase font-bold tracking-wider">
                              {item.patch_type}
                            </span>
                            <span className="text-gray-100 font-bold text-sm font-sans">
                              "{item.query_pattern}"
                            </span>
                            <span className="text-gray-600">/</span>
                            <span className="text-gray-400">Issue: {item.issue_type}</span>
                          </div>

                          <div className="flex flex-wrap items-center gap-2">
                            <span>Status:</span> {getPolicyBadge(item.effective_status)}
                            <span className="text-gray-600">|</span>
                            <span>Confidence:</span>
                            <span className="px-2 py-0.5 border rounded-full text-[9px] uppercase font-bold tracking-wider text-purple-400 bg-purple-950/20 border-purple-800/40">
                              {(item.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>

                        {/* Policy Rules */}
                        {item.policy && Object.keys(item.policy).length > 0 && (
                          <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3.5 space-y-2 text-xs leading-relaxed font-sans text-gray-300">
                            <div className="text-[10px] font-mono text-green-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
                              <CheckCircle2 size={12} />
                              Chính sách bản vá:
                            </div>
                            <pre className="text-[10px] font-mono text-gray-400 bg-black/30 p-2 rounded max-h-36 overflow-auto">
                              {JSON.stringify(item.policy, null, 2)}
                            </pre>
                          </div>
                        )}

                        {/* Patch metadata footer */}
                        <div className="flex flex-wrap items-center justify-between gap-3 text-[10px] text-gray-500 pt-2 border-t border-gray-900/60">
                          <div>
                            Lý do tạo: <span className="text-gray-300 font-sans italic">{item.reason || "N/A"}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span>Target: <span className="text-gray-400">{item.target_entity || item.target_intent || "N/A"}</span></span>
                            <span>|</span>
                            <span>{new Date(item.created_at).toLocaleString('vi-VN')}</span>
                          </div>
                        </div>

                        {/* Inline Admin Emergency Override Controls */}
                        <div className="pt-3 border-t border-gray-900/60 flex flex-col gap-2">
                          {actioningPatchId === item.id ? (
                            <div className="p-3 bg-[#121212] border border-gray-900 rounded space-y-2.5 animate-in fade-in duration-200">
                              <div className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">
                                Ghi chú người duyệt / Lý do kiểm toán (Reviewer Note):
                              </div>
                              <input
                                type="text"
                                value={reviewerNote}
                                onChange={(e) => setReviewerNote(e.target.value)}
                                placeholder="Nhập lý do ngắn (bắt buộc)..."
                                className="w-full bg-[#0c0c0c] border border-gray-800 rounded px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-green-500 font-sans"
                                disabled={actionLoading}
                              />
                              <div className="flex justify-end gap-2">
                                <button
                                  onClick={() => {
                                    setActioningPatchId(null);
                                    setReviewerNote('');
                                  }}
                                  className="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-[10px] font-bold cursor-pointer transition-colors"
                                  disabled={actionLoading}
                                >
                                  HỦY BỎ
                                </button>
                                {item.effective_status === 'disabled' ? (
                                  <button
                                    onClick={() => handleUpdatePatchStatus(item.id, 'restore', reviewerNote)}
                                    disabled={!reviewerNote.trim() || actionLoading}
                                    className="px-3 py-1 bg-green-600 hover:bg-green-500 text-white rounded text-[10px] font-bold disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors flex items-center gap-1"
                                  >
                                    {actionLoading && <Loader2 className="animate-spin" size={10} />}
                                    KHÔI PHỤC BẢN VÁ
                                  </button>
                                ) : (
                                  <button
                                    onClick={() => handleUpdatePatchStatus(item.id, 'disable', reviewerNote)}
                                    disabled={!reviewerNote.trim() || actionLoading}
                                    className="px-3 py-1 bg-red-600 hover:bg-red-500 text-white rounded text-[10px] font-bold disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors flex items-center gap-1"
                                  >
                                    {actionLoading && <Loader2 className="animate-spin" size={10} />}
                                    XÁC NHẬN TẮT
                                  </button>
                                )}
                              </div>
                            </div>
                          ) : (
                            <div className="flex justify-end">
                              {item.effective_status === 'disabled' ? (
                                <button
                                  onClick={() => {
                                    setActioningPatchId(item.id);
                                    setReviewerNote('');
                                  }}
                                  className="px-3 py-1 border border-green-800/40 text-green-400 hover:bg-green-950/20 hover:border-green-600 rounded text-[10px] font-bold transition-all cursor-pointer"
                                >
                                  KHÔI PHỤC BẢN VÁ
                                </button>
                              ) : (
                                <button
                                  onClick={() => {
                                    setActioningPatchId(item.id);
                                    setReviewerNote('');
                                  }}
                                  className="px-3 py-1 border border-red-800/40 text-red-400 hover:bg-red-950/20 hover:border-red-600 rounded text-[10px] font-bold transition-all cursor-pointer"
                                >
                                  TẮT BẢN VÁ
                                </button>
                              )}
                            </div>
                          )}
                        </div>

                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>
          )}

        </div>
      )}
    </div>
  );
}
