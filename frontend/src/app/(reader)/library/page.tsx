'use client';

import React, { useState, useEffect } from 'react';
import {
  Search,
  Loader2,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Database,
  BookOpen,
  ChevronDown,
  ChevronUp,
  MessageSquareWarning,
  CheckCircle2
} from 'lucide-react';
import WikiSettingsWrapper from '@/components/WikiSettingsWrapper';

interface EvidenceItem {
  chapter_number: number;
  chapter_title: string;
  chunk_index: number;
  content_hash: string;
  preview: string;
}

interface ProvisionalItem {
  id: string;
  name: string;
  type: string;
  summary: string;
  evidence: EvidenceItem[];
  confidence: number;
  quality_class: 'high_confidence' | 'medium_confidence' | string;
  status: string;
  source: string;
  feedback_score: number;
  chapter_numbers: number[];
  first_chapter: number | null;
  last_chapter: number | null;
  created_at: string;
}

const TYPE_LABELS: Record<string, string> = {
  entity: "Thực thể / Nhân vật",
  item: "Vật phẩm / Tinh thể",
  ability: "Dị năng / Kỹ năng",
  location: "Địa điểm / Căn cứ",
  faction: "Thế lực / Băng nhóm",
  event: "Sự kiện",
  relationship: "Quan hệ",
  chapter_summary: "Tóm tắt chương"
};

const QUALITY_LABELS: Record<string, string> = {
  high_confidence: "Tin cậy cao",
  medium_confidence: "Tin cậy trung bình"
};

const QUALITY_BADGE_CLASSES: Record<string, string> = {
  high_confidence: "text-green-600 dark:text-toxic-green-DEFAULT bg-green-50 dark:bg-toxic-green-DEFAULT/5 border-green-200 dark:border-toxic-green-DEFAULT/20",
  medium_confidence: "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800/40"
};

const FEEDBACK_TYPE_LABELS: Record<string, string> = {
  wrong_info: "Sai thông tin",
  wrong_type: "Sai phân loại",
  wrong_evidence: "Sai bằng chứng",
  duplicate: "Trùng mục",
  spoiler: "Sai mức spoiler / chương",
  missing_info: "Thiếu thông tin",
  other: "Ý kiến khác"
};

export default function PublicProvisionalLibraryPage() {
  const [items, setItems] = useState<ProvisionalItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [type, setType] = useState('all');
  const [qualityClass, setQualityClass] = useState('all');

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);

  // Expandable evidence state
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});

  // Feedback States
  const [activeFeedbackId, setActiveFeedbackId] = useState<string | null>(null);
  const [feedbackType, setFeedbackType] = useState('wrong_info');
  const [userComment, setUserComment] = useState('');
  const [suggestedCorrection, setSuggestedCorrection] = useState('');
  const [website, setWebsite] = useState(''); // Honeypot
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [submittedFeedbackIds, setSubmittedFeedbackIds] = useState<Record<string, boolean>>({});

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [search]);

  // Load public items
  useEffect(() => {
    loadLibraryItems();
  }, [debouncedSearch, type, qualityClass, page]);

  const loadLibraryItems = async () => {
    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams({
        search: debouncedSearch,
        type,
        quality_class: qualityClass,
        page: page.toString(),
        page_size: pageSize.toString()
      });

      const res = await fetch(`/api/public/provisional-library?${queryParams}`);

      if (res.ok) {
        const data = await res.json();
        setItems(data.items || []);
        setTotalCount(data.total || 0);
      } else {
        const err = await res.json().catch(() => ({}));
        setError(err.error || "Không thể tải danh sách thư viện tự động.");
      }
    } catch (err) {
      setError("Lỗi kết nối server khi tải thư viện tự động.");
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedItems(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleOpenFeedback = (item: ProvisionalItem) => {
    setActiveFeedbackId(item.id);
    setFeedbackType('wrong_info');
    setUserComment('');
    setSuggestedCorrection('');
    setWebsite(''); // Reset honeypot
    setFeedbackError(null);
  };

  const handleCancelFeedback = () => {
    setActiveFeedbackId(null);
    setWebsite(''); // Reset honeypot
    setFeedbackError(null);
  };

  const handleSubmitFeedback = async (item: ProvisionalItem) => {
    setFeedbackError(null);

    const trimmedComment = userComment.trim();
    if (!trimmedComment) {
      setFeedbackError("Ý kiến đóng góp không được trống.");
      return;
    }
    if (trimmedComment.length < 3) {
      setFeedbackError("Ý kiến đóng góp quá ngắn (tối thiểu 3 ký tự).");
      return;
    }

    setFeedbackSubmitting(true);

    try {
      const payload = {
        provisional_id: item.id,
        record_name: item.name,
        feedback_type: feedbackType,
        user_comment: trimmedComment,
        suggested_correction: suggestedCorrection.trim(),
        page_url: window.location.href,
        website: website.trim() // Honeypot field
      };

      const res = await fetch('/api/public/provisional-library/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setSubmittedFeedbackIds(prev => ({ ...prev, [item.id]: true }));
        setActiveFeedbackId(null);
      } else {
        const err = await res.json().catch(() => ({}));
        setFeedbackError(err.error || "Gửi ý kiến thất bại. Vui lòng thử lại.");
      }
    } catch (err) {
      setFeedbackError("Lỗi kết nối khi gửi ý kiến đóng góp.");
    } finally {
      setFeedbackSubmitting(false);
    }
  };

  const totalPages = Math.ceil(totalCount / pageSize) || 1;

  return (
    <WikiSettingsWrapper>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-10 space-y-8">
        {/* Header section */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 mb-4 px-4 py-1.5 border border-reader-accent/40 bg-reader-accent/5 rounded-full">
            <Database size={14} className="text-reader-accent" />
            <span className="text-xs font-mono text-reader-accent tracking-widest uppercase">AUTO-GENERATED ARCHIVE</span>
          </div>
          <h1 className="font-biohazard text-4xl text-reader-text tracking-wide mb-2 uppercase">
            THƯ VIỆN TỰ ĐỘNG
          </h1>
          <p className="text-reader-muted text-sm font-reading max-w-xl mx-auto leading-relaxed">
            Dữ liệu được trích xuất tự động từ nội dung các chương truyện, chưa phải bách khoa canon chính thức từ tác giả.
          </p>
        </div>

        {/* Warning banner */}
        <div className="flex items-start gap-3 text-amber-800 dark:text-amber-500 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/30 rounded-xl p-4 text-xs font-mono leading-relaxed max-w-4xl mx-auto">
          <AlertTriangle className="shrink-0 mt-0.5" size={16} />
          <div>
            <span className="font-bold uppercase">Lưu ý quan trọng:</span> Đây là dữ liệu nháp (provisional) được thu thập tự động bằng thuật toán.
            Các tóm tắt và phân loại có thể có sai lệch hoặc chứa chi tiết nhiễu. Độc giả vui lòng đối chiếu và kiểm chứng thêm khi tham khảo.
          </div>
        </div>

        {/* Content layout with sidebar */}
        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar Filters */}
          <aside className="w-full md:w-64 flex-shrink-0 space-y-6">
            <div className="bg-reader-card-bg border border-reader-border rounded-xl p-5 backdrop-blur-sm shadow-xl space-y-5">
              {/* Search Box */}
              <div className="space-y-2">
                <label className="text-xs font-mono text-reader-muted uppercase tracking-wider">Tìm kiếm</label>
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 text-reader-muted" size={16} />
                  <input
                    type="text"
                    placeholder="Nhập tên, mô tả..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full bg-reader-bg border border-reader-border rounded pl-10 pr-3 py-2 text-xs text-reader-text outline-none focus:border-reader-accent transition-all font-sans"
                  />
                </div>
              </div>

              {/* Type Filter */}
              <div className="space-y-2">
                <label className="text-xs font-mono text-reader-muted uppercase tracking-wider">Phân loại</label>
                <select
                  value={type}
                  onChange={(e) => { setType(e.target.value); setPage(1); }}
                  className="w-full bg-reader-bg border border-reader-border rounded px-3 py-2 text-xs text-reader-text outline-none focus:border-reader-accent transition-all cursor-pointer font-sans"
                >
                  <option value="all" className="bg-reader-bg text-reader-text">Tất cả phân loại</option>
                  {Object.entries(TYPE_LABELS).map(([k, v]) => (
                    <option key={k} value={k} className="bg-reader-bg text-reader-text">{v}</option>
                  ))}
                </select>
              </div>

              {/* Quality Filter */}
              <div className="space-y-2">
                <label className="text-xs font-mono text-reader-muted uppercase tracking-wider">Độ tin cậy</label>
                <select
                  value={qualityClass}
                  onChange={(e) => { setQualityClass(e.target.value); setPage(1); }}
                  className="w-full bg-reader-bg border border-reader-border rounded px-3 py-2 text-xs text-reader-text outline-none focus:border-reader-accent transition-all cursor-pointer font-sans"
                >
                  <option value="all" className="bg-reader-bg text-reader-text">Tất cả mức độ</option>
                  <option value="high_confidence" className="bg-reader-bg text-reader-text">Tin cậy cao (High)</option>
                  <option value="medium_confidence" className="bg-reader-bg text-reader-text">Tin cậy trung bình (Medium)</option>
                </select>
              </div>
            </div>

            {/* Error reporting CTA */}
            <div className="bg-reader-card-bg border border-reader-border rounded-xl p-5 backdrop-blur-sm shadow-xl flex flex-col items-center text-center space-y-3 font-mono text-xs">
              <MessageSquareWarning className="text-reader-accent" size={24} />
              <div className="text-reader-text font-bold uppercase tracking-wider">Phát hiện sai sót?</div>
              <p className="text-reader-muted leading-relaxed font-sans">
                Nếu phát hiện lỗi chi tiết hoặc phân loại sai lệch, hãy gửi báo lỗi trực tiếp qua Oracle chatbot ở khung đọc truyện.
              </p>
            </div>
          </aside>

          {/* List of items */}
          <div className="flex-1 space-y-4">
            {error && (
              <div className="flex items-center gap-2 text-red-500 dark:text-red-400 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/30 rounded-xl p-4 text-xs font-mono">
                <AlertTriangle size={16} />
                <span>{error}</span>
              </div>
            )}

            {loading ? (
              <div className="flex justify-center items-center py-32">
                <Loader2 className="animate-spin text-reader-accent" size={36} />
              </div>
            ) : items.length === 0 ? (
              <div className="bg-reader-card-bg border border-reader-border rounded-xl p-16 text-center text-reader-muted text-xs italic font-mono">
                Không tìm thấy mục tự động nào phù hợp với bộ lọc hiện tại.
              </div>
            ) : (
              <div className="space-y-4">
                {/* Stats & pagination meta */}
                <div className="text-xs font-mono text-reader-muted px-1">
                  Hiển thị kết quả <span className="text-reader-accent font-bold">{(page - 1) * pageSize + 1}</span> - <span className="text-reader-accent font-bold">{Math.min(page * pageSize, totalCount)}</span> trên tổng số <span className="text-reader-accent font-bold">{totalCount}</span> mục.
                </div>

                {/* Items Card List */}
                <div className="grid gap-4">
                  {items.map((item) => {
                    const typeLabel = TYPE_LABELS[item.type] || item.type;
                    const qBadgeClass = QUALITY_BADGE_CLASSES[item.quality_class] || "text-reader-muted bg-reader-bg border-reader-border";
                    const qLabel = QUALITY_LABELS[item.quality_class] || item.quality_class;
                    const isExpanded = expandedItems[item.id] || false;
                    const isFeedbackOpen = activeFeedbackId === item.id;
                    const isSubmitted = submittedFeedbackIds[item.id] || false;

                    return (
                      <div
                        key={item.id}
                        className="bg-reader-card-bg border border-reader-border rounded-xl p-5 hover:border-reader-accent/60 hover:shadow-[0_0_15px_rgba(57,255,20,0.02)] transition-all font-mono space-y-4"
                      >
                        {/* Title & Metadata Row */}
                        <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
                          <div className="flex flex-wrap items-center gap-3">
                            <span className="text-reader-text font-bold text-base font-sans">{item.name}</span>
                            <span className="text-reader-border">/</span>
                            <span className="text-reader-text/85 text-xs">{typeLabel}</span>
                            <span className="text-reader-border">|</span>
                            <span className={`px-2 py-0.5 border rounded-full text-[9px] uppercase font-bold tracking-wider ${qBadgeClass}`}>
                              {qLabel}
                            </span>
                          </div>

                          <div className="flex items-center gap-4 text-[11px] text-reader-muted">
                            <span>Độ tin cậy: <span className="text-reader-accent font-bold">{item.confidence}</span></span>
                            <span>|</span>
                            <span>Chương xuất hiện: <span className="text-reader-text font-bold">
                              {item.first_chapter === item.last_chapter
                                ? `Chương ${item.first_chapter}`
                                : `Chương ${item.first_chapter || '?'} - ${item.last_chapter || '?'}`
                              }
                            </span></span>
                          </div>
                        </div>

                        {/* Summary Text */}
                        {item.summary && (
                          <div className="bg-reader-bg/60 border border-reader-border rounded-lg p-3.5 text-xs leading-relaxed font-sans text-reader-text">
                            {item.summary}
                          </div>
                        )}

                        {/* Success Message Banner */}
                        {isSubmitted && (
                          <div className="bg-green-500/10 border border-green-500/20 text-green-600 dark:text-green-400 p-3.5 rounded-lg text-xs flex items-center gap-2 font-sans">
                            <CheckCircle2 size={16} className="shrink-0" />
                            <span>Cảm ơn bạn đã gửi đóng góp ý kiến! Ý kiến của bạn đã được ghi nhận để kiểm chứng.</span>
                          </div>
                        )}

                        {/* Inline Feedback Form */}
                        {isFeedbackOpen && (
                          <div className="bg-reader-bg/50 border border-reader-border/80 rounded-lg p-4 space-y-3.5 animate-in fade-in duration-200 font-sans">
                            <div className="space-y-1">
                              <div className="text-xs font-mono font-bold text-reader-accent uppercase tracking-wider">
                                Báo lỗi / Góp ý mục: {item.name}
                              </div>
                              <div className="text-[11px] text-reader-muted font-sans leading-relaxed">
                                Vui lòng mô tả lỗi cụ thể, tránh spam hoặc gửi nhiều lần cùng nội dung.
                              </div>
                            </div>

                            {feedbackError && (
                              <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-2.5 rounded text-xs flex items-center gap-2">
                                <AlertTriangle size={14} className="shrink-0" />
                                <span>{feedbackError}</span>
                              </div>
                            )}

                            <div className="space-y-3">
                              {/* Feedback Type Dropdown */}
                              <div className="space-y-1">
                                <label htmlFor={`feedback-type-${item.id}`} className="text-[10px] font-mono text-reader-muted uppercase tracking-wider">Loại lỗi / Góp ý</label>
                                <select
                                  id={`feedback-type-${item.id}`}
                                  value={feedbackType}
                                  onChange={(e) => setFeedbackType(e.target.value)}
                                  className="w-full bg-reader-bg border border-reader-border rounded px-3 py-1.5 text-xs text-reader-text outline-none focus:border-reader-accent transition-all cursor-pointer font-sans"
                                >
                                  {Object.entries(FEEDBACK_TYPE_LABELS).map(([k, v]) => (
                                    <option key={k} value={k} className="bg-reader-bg text-reader-text">{v}</option>
                                  ))}
                                </select>
                              </div>

                              {/* Honeypot field (hidden from users) */}
                              <div className="hidden" aria-hidden="true">
                                <label htmlFor={`website-${item.id}`}>Website</label>
                                <input
                                  id={`website-${item.id}`}
                                  type="text"
                                  name="website"
                                  value={website}
                                  onChange={(e) => setWebsite(e.target.value)}
                                  tabIndex={-1}
                                  autoComplete="off"
                                />
                              </div>

                              {/* User Comment Textarea */}
                              <div className="space-y-1">
                                <label htmlFor={`user-comment-${item.id}`} className="text-[10px] font-mono text-reader-muted uppercase tracking-wider">Ý kiến người đọc (Bắt buộc)</label>
                                <textarea
                                  id={`user-comment-${item.id}`}
                                  placeholder="Nhập ý kiến đóng góp của bạn (tối thiểu 3 ký tự, tối đa 2000)..."
                                  value={userComment}
                                  onChange={(e) => setUserComment(e.target.value)}
                                  rows={3}
                                  maxLength={2000}
                                  className="w-full bg-reader-bg border border-reader-border rounded p-2.5 text-xs text-reader-text outline-none focus:border-reader-accent transition-all resize-none font-sans"
                                />
                              </div>

                              {/* Suggested Correction Textarea */}
                              <div className="space-y-1">
                                <label htmlFor={`suggested-correction-${item.id}`} className="text-[10px] font-mono text-reader-muted uppercase tracking-wider">Đề xuất sửa đổi (Tùy chọn)</label>
                                <textarea
                                  id={`suggested-correction-${item.id}`}
                                  placeholder="Đề xuất thông tin sửa đổi chính xác nếu có (tối đa 4000)..."
                                  value={suggestedCorrection}
                                  onChange={(e) => setSuggestedCorrection(e.target.value)}
                                  rows={2}
                                  maxLength={4000}
                                  className="w-full bg-reader-bg border border-reader-border rounded p-2.5 text-xs text-reader-text outline-none focus:border-reader-accent transition-all resize-none font-sans"
                                />
                              </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex items-center justify-end gap-2 pt-1">
                              <button
                                onClick={handleCancelFeedback}
                                disabled={feedbackSubmitting}
                                className="px-3 py-1.5 bg-reader-bg/40 hover:bg-reader-bg/80 border border-reader-border text-xs text-reader-text rounded transition-all cursor-pointer disabled:opacity-40"
                              >
                                HỦY
                              </button>
                              <button
                                onClick={() => handleSubmitFeedback(item)}
                                disabled={feedbackSubmitting}
                                className="px-4 py-1.5 bg-reader-accent hover:bg-reader-accent/90 border border-reader-accent text-xs text-black font-bold rounded transition-all cursor-pointer disabled:opacity-40 flex items-center gap-1.5"
                              >
                                {feedbackSubmitting && <Loader2 size={12} className="animate-spin" />}
                                GỬI BÁO LỖI
                              </button>
                            </div>
                          </div>
                        )}

                        {/* Evidence citation footer */}
                        <div className="flex items-center justify-between pt-2 border-t border-reader-border/40 text-xs">
                          <div className="text-reader-muted flex flex-wrap items-center gap-2">
                            <BookOpen size={12} className="text-reader-accent" />
                            <span>Xuất hiện ở các chương:</span>
                            <div className="flex flex-wrap gap-1">
                              {item.chapter_numbers?.slice(0, 8).map((ch) => (
                                <span key={ch} className="px-1.5 py-0.2 bg-reader-bg/40 text-reader-text/80 rounded text-[10px]">
                                  {ch}
                                </span>
                              ))}
                              {item.chapter_numbers?.length > 8 && (
                                <span className="text-reader-muted text-[10px] self-end">
                                  +{item.chapter_numbers.length - 8} chương khác
                                </span>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            {!isSubmitted && !isFeedbackOpen && (
                              <button
                                onClick={() => handleOpenFeedback(item)}
                                className="flex items-center gap-1.5 px-3 py-1 bg-red-950/20 hover:bg-red-950/40 border border-red-900/30 text-[10px] text-red-600 dark:text-red-400 font-bold rounded tracking-wider transition-colors cursor-pointer"
                              >
                                BÁO LỖI MỤC NÀY
                              </button>
                            )}

                            <button
                              onClick={() => toggleExpand(item.id)}
                              className="flex items-center gap-1.5 px-3 py-1 bg-reader-bg/40 hover:bg-reader-bg/80 border border-reader-border text-[10px] text-reader-text font-bold rounded tracking-wider transition-colors cursor-pointer"
                            >
                              {isExpanded ? (
                                <>
                                  ẨN TRÍCH ĐOẠN <ChevronUp size={12} />
                                </>
                              ) : (
                                <>
                                  XEM TRÍCH ĐOẠN ({item.evidence?.length || 0}) <ChevronDown size={12} />
                                </>
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Collapsible evidence details */}
                        {isExpanded && item.evidence && (
                          <div className="mt-4 pt-4 border-t border-reader-border/40 space-y-3 animate-in fade-in duration-200">
                            <div className="text-[10px] text-reader-muted uppercase tracking-widest font-bold mb-2">
                              Trích đoạn minh chứng (Citation Evidence)
                            </div>

                            <div className="space-y-2.5">
                              {item.evidence.map((ev, idx) => (
                                <div key={idx} className="bg-reader-bg/50 border border-reader-border/50 rounded-lg p-3 space-y-2 text-xs font-sans">
                                  <div className="flex flex-wrap items-center justify-between text-[10px] font-mono text-reader-muted">
                                    <div className="flex items-center gap-2">
                                      <span className="text-reader-accent font-bold"># {idx + 1}</span>
                                      <span>|</span>
                                      <span className="text-reader-text font-sans font-semibold">Chương {ev.chapter_number}: {ev.chapter_title}</span>
                                    </div>
                                  </div>
                                  <div className="text-reader-text/90 italic pl-3 border-l-2 border-reader-accent/30 py-0.5 leading-relaxed">
                                    "{ev.preview}"
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Pagination control */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between bg-reader-card-bg border border-reader-border px-4 py-3 rounded-xl text-xs font-mono mt-6">
                    <button
                      onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                      disabled={page === 1}
                      className="flex items-center gap-1 px-3 py-1.5 bg-reader-bg/40 hover:bg-reader-bg/80 border border-reader-border disabled:opacity-40 disabled:cursor-not-allowed text-reader-text font-bold rounded transition-colors cursor-pointer"
                    >
                      <ChevronLeft size={14} /> TRƯỚC
                    </button>

                    <div className="text-reader-text">
                      Trang <span className="text-reader-accent font-bold">{page}</span> / <span className="text-reader-text font-bold">{totalPages}</span>
                    </div>

                    <button
                      onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                      disabled={page === totalPages}
                      className="flex items-center gap-1 px-3 py-1.5 bg-reader-bg/40 hover:bg-reader-bg/80 border border-reader-border disabled:opacity-40 disabled:cursor-not-allowed text-reader-text font-bold rounded transition-colors cursor-pointer"
                    >
                      SAU <ChevronRight size={14} />
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </WikiSettingsWrapper>
  );
}
