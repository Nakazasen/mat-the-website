'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Search,
  Loader2,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Database,
  ShieldAlert,
  BookOpen,
  Bookmark,
  TrendingUp,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

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
  quality_class: 'high_confidence' | 'medium_confidence' | 'weak_evidence' | 'discard_candidate' | string;
  status: string;
  source: string;
  feedback_score: number;
  needs_review: boolean;
  chapter_numbers: number[];
  first_chapter: number | null;
  last_chapter: number | null;
  created_at: string;
}

interface LibraryStats {
  total: number;
  high_confidence: number;
  medium_confidence: number;
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
  medium_confidence: "Tin cậy trung bình",
  weak_evidence: "Bằng chứng yếu",
  discard_candidate: "Bị loại bỏ"
};

const QUALITY_BADGE_CLASSES: Record<string, string> = {
  high_confidence: "text-green-400 bg-green-950/20 border-green-800/40",
  medium_confidence: "text-blue-400 bg-blue-950/20 border-blue-800/40",
  weak_evidence: "text-yellow-400 bg-yellow-950/20 border-yellow-800/40",
  discard_candidate: "text-red-400 bg-red-950/20 border-red-800/40"
};

export default function AdminProvisionalLibraryPage() {
  const router = useRouter();

  // State variables
  const [items, setItems] = useState<ProvisionalItem[]>([]);
  const [stats, setStats] = useState<LibraryStats>({ total: 0, high_confidence: 0, medium_confidence: 0 });
  const [loading, setLoading] = useState(false);
  const [loadingStats, setLoadingStats] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUnauthorized, setIsUnauthorized] = useState(false);

  // Filter state
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [type, setType] = useState('all');
  const [qualityClass, setQualityClass] = useState('all');

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [totalCount, setTotalCount] = useState(0);

  // Expanded evidence state
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [search]);

  // Load stats and library items
  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    loadLibraryItems();
  }, [debouncedSearch, type, qualityClass, page]);

  const loadStats = async () => {
    setLoadingStats(true);
    try {
      const res = await fetch('/api/oracle/provisional-library?stats=true');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error("Error loading library stats:", err);
    } finally {
      setLoadingStats(false);
    }
  };

  const loadLibraryItems = async () => {
    setLoading(true);
    setError(null);
    setIsUnauthorized(false);

    try {
      const queryParams = new URLSearchParams({
        search: debouncedSearch,
        type,
        quality_class: qualityClass,
        page: page.toString(),
        page_size: pageSize.toString()
      });

      const res = await fetch(`/api/oracle/provisional-library?${queryParams}`);

      if (res.ok) {
        const data = await res.json();
        setItems(data.items || []);
        setTotalCount(data.total || 0);
      } else {
        if (res.status === 401) {
          setIsUnauthorized(true);
          setError("Bạn cần đăng nhập admin để xem dữ liệu này.");
        } else {
          const err = await res.json().catch(() => ({}));
          setError(err.error || "Không thể tải danh sách thư viện tự động.");
        }
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

  const totalPages = Math.ceil(totalCount / pageSize) || 1;

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
            <Database className="text-green-500" size={24} />
            THƯ VIỆN TỰ ĐỘNG (PROVISIONAL)
          </h1>
          <p className="text-gray-500 text-sm font-mono mt-1">
            Dữ liệu trích xuất tự động bằng thuật toán/heuristic từ truyện. Chưa được biên duyệt làm Wiki chính thức.
          </p>
        </div>
      </div>

      {/* Warning banner */}
      <div className="flex items-start gap-3 text-yellow-400 bg-yellow-950/20 border border-yellow-800/40 rounded-lg p-4 text-xs font-mono leading-relaxed">
        <AlertCircle className="shrink-0 mt-0.5" size={16} />
        <div>
          <span className="font-bold uppercase">Cảnh báo bản nháp (Provisional):</span> Đây là thư viện tự động thu thập từ các chương truyện. 
          Dữ liệu có thể chứa nhiễu, lỗi phân loại hoặc tóm tắt chưa chuẩn xác. Tuyệt đối không tự ý áp dụng trực tiếp 
          vào Wiki chính thống mà không qua chỉnh sửa và xác nhận canon từ admin. Giao diện này chỉ hỗ trợ tra cứu tham khảo.
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wider">Tổng số thực thể hợp lệ</div>
            <div className="text-2xl font-bold text-gray-100 mt-1">
              {loadingStats ? <Loader2 className="animate-spin text-green-500 inline" size={20} /> : stats.total}
            </div>
          </div>
          <Database className="text-green-500/40" size={32} />
        </div>

        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wider">Độ tin cậy cao (High)</div>
            <div className="text-2xl font-bold text-green-400 mt-1">
              {loadingStats ? <Loader2 className="animate-spin text-green-500 inline" size={20} /> : stats.high_confidence}
            </div>
          </div>
          <Bookmark className="text-green-500/40" size={32} />
        </div>

        <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 flex items-center justify-between font-mono">
          <div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wider">Độ tin cậy vừa (Medium)</div>
            <div className="text-2xl font-bold text-blue-400 mt-1">
              {loadingStats ? <Loader2 className="animate-spin text-green-500 inline" size={20} /> : stats.medium_confidence}
            </div>
          </div>
          <TrendingUp className="text-blue-500/40" size={32} />
        </div>
      </div>

      {/* Filter and Search Panel */}
      <div className="bg-[#181818] border border-gray-800 rounded-lg p-4 space-y-4 font-mono">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search box */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-2.5 text-gray-500" size={16} />
            <input
              type="text"
              placeholder="Tìm kiếm tên, tóm tắt..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#0a0a0a] border border-gray-800 rounded pl-10 pr-4 py-2 text-sm text-gray-200 outline-none focus:border-green-800 transition-all font-sans"
            />
          </div>

          {/* Type dropdown */}
          <div className="w-full md:w-56 flex items-center gap-2">
            <span className="text-xs text-gray-500 shrink-0">Loại:</span>
            <select
              value={type}
              onChange={(e) => { setType(e.target.value); setPage(1); }}
              className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-xs text-gray-300 outline-none focus:border-green-800 transition-all cursor-pointer font-sans"
            >
              <option value="all">Tất cả phân loại</option>
              {Object.entries(TYPE_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>

          {/* Quality dropdown */}
          <div className="w-full md:w-56 flex items-center gap-2">
            <span className="text-xs text-gray-500 shrink-0">Độ tin cậy:</span>
            <select
              value={qualityClass}
              onChange={(e) => { setQualityClass(e.target.value); setPage(1); }}
              className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-xs text-gray-300 outline-none focus:border-green-800 transition-all cursor-pointer font-sans"
            >
              <option value="all">Tất cả mức độ</option>
              <option value="high_confidence">Tin cậy cao (High)</option>
              <option value="medium_confidence">Tin cậy vừa (Medium)</option>
            </select>
          </div>
        </div>
      </div>

      {/* List content */}
      {error && (
        <div className="flex items-center gap-2 text-red-400 bg-red-950/20 border border-red-900/50 rounded-lg p-4 text-xs font-mono">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-24">
          <Loader2 className="animate-spin text-green-500" size={36} />
        </div>
      ) : items.length === 0 ? (
        <div className="bg-[#181818] border border-gray-800 rounded-lg p-12 text-center text-gray-500 text-xs italic font-mono">
          Không tìm thấy thực thể/bản ghi nào khớp với điều kiện lọc.
        </div>
      ) : (
        <div className="space-y-4">
          {/* Item count bar */}
          <div className="text-xs font-mono text-gray-500 px-1">
            Hiển thị thực thể <span className="text-green-500 font-bold">{(page - 1) * pageSize + 1}</span> - <span className="text-green-500 font-bold">{Math.min(page * pageSize, totalCount)}</span> trên tổng số <span className="text-green-500 font-bold">{totalCount}</span> kết quả.
          </div>

          {/* Grid list of items */}
          <div className="grid gap-4">
            {items.map((item) => {
              const typeLabel = TYPE_LABELS[item.type] || item.type;
              const qBadgeClass = QUALITY_BADGE_CLASSES[item.quality_class] || "text-gray-400 bg-gray-900 border-gray-800";
              const qLabel = QUALITY_LABELS[item.quality_class] || item.quality_class;
              const isExpanded = expandedItems[item.id] || false;

              return (
                <div
                  key={item.id}
                  className="bg-[#181818] border border-gray-800 rounded-lg p-5 hover:border-gray-700 transition-all font-mono space-y-4"
                >
                  {/* Meta row */}
                  <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="text-gray-100 font-bold text-base font-sans">{item.name}</span>
                      <span className="text-gray-600">/</span>
                      <span className="text-gray-400 text-xs">{typeLabel}</span>
                      <span className="text-gray-600">|</span>
                      <span className={`px-2 py-0.5 border rounded-full text-[9px] uppercase font-bold tracking-wider ${qBadgeClass}`}>
                        {qLabel}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-[11px] text-gray-500">
                      <span>Độ tin cậy: <span className="text-green-400 font-bold">{item.confidence}</span></span>
                      <span>|</span>
                      <span>Chương xuất hiện: <span className="text-gray-300 font-bold">
                        {item.first_chapter === item.last_chapter
                          ? `Chương ${item.first_chapter}`
                          : `Chương ${item.first_chapter || '?'} - ${item.last_chapter || '?'}`
                        }
                      </span></span>
                    </div>
                  </div>

                  {/* Summary/Description */}
                  {item.summary && (
                    <div className="bg-[#0f0f0f] border border-gray-900 rounded p-3 text-xs leading-relaxed font-sans text-gray-300">
                      {item.summary}
                    </div>
                  )}

                  {/* Bottom citation details */}
                  <div className="flex items-center justify-between pt-2 border-t border-gray-800/60 text-xs">
                    <div className="text-gray-500 flex flex-wrap items-center gap-2">
                      <BookOpen size={12} className="text-green-600" />
                      <span>Bằng chứng trích xuất từ các chương:</span>
                      <div className="flex flex-wrap gap-1">
                        {item.chapter_numbers?.slice(0, 8).map((ch) => (
                          <span key={ch} className="px-1.5 py-0.2 bg-gray-900 text-gray-400 rounded text-[10px]">
                            {ch}
                          </span>
                        ))}
                        {item.chapter_numbers?.length > 8 && (
                          <span className="text-gray-600 text-[10px] self-end">
                            +{item.chapter_numbers.length - 8} chương khác
                          </span>
                        )}
                      </div>
                    </div>

                    <button
                      onClick={() => toggleExpand(item.id)}
                      className="flex items-center gap-1.5 px-3 py-1 bg-gray-800 hover:bg-gray-700 text-[10px] text-gray-300 font-bold rounded tracking-wider transition-colors cursor-pointer"
                    >
                      {isExpanded ? (
                        <>
                          ẨN EVIDENCE <ChevronUp size={12} />
                        </>
                      ) : (
                        <>
                          XEM EVIDENCE ({item.evidence?.length || 0}) <ChevronDown size={12} />
                        </>
                      )}
                    </button>
                  </div>

                  {/* Expanded evidence block */}
                  {isExpanded && item.evidence && (
                    <div className="mt-4 pt-4 border-t border-gray-800 space-y-3 animate-in fade-in duration-200">
                      <div className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-2">
                        Bằng chứng (Citation Evidence)
                      </div>

                      <div className="space-y-2.5">
                        {item.evidence.map((ev, idx) => (
                          <div key={idx} className="bg-[#0c0c0c] border border-gray-900/60 rounded p-3 space-y-2 text-xs font-sans">
                            {/* Evidence header */}
                            <div className="flex flex-wrap items-center justify-between text-[10px] font-mono text-gray-500">
                              <div className="flex items-center gap-2">
                                <span className="text-green-500 font-bold"># {idx + 1}</span>
                                <span>|</span>
                                <span className="text-gray-300 font-sans font-semibold">Chương {ev.chapter_number}: {ev.chapter_title}</span>
                              </div>
                              <span className="text-[9px] text-gray-600 select-all font-mono">hash: {ev.content_hash?.slice(0, 12)}...</span>
                            </div>

                            {/* Quote snippet */}
                            <div className="text-gray-400 italic pl-3 border-l-2 border-green-800/40 py-0.5 leading-relaxed">
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

          {/* Pagination bar */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between bg-[#181818] border border-gray-800 px-4 py-3 rounded-lg text-xs font-mono mt-6">
              <button
                onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                disabled={page === 1}
                className="flex items-center gap-1 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed text-gray-300 font-bold rounded transition-colors cursor-pointer"
              >
                <ChevronLeft size={14} /> TRƯỚC
              </button>

              <div className="text-gray-400">
                Trang <span className="text-green-400 font-bold">{page}</span> / <span className="text-gray-400 font-bold">{totalPages}</span>
              </div>

              <button
                onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                disabled={page === totalPages}
                className="flex items-center gap-1 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed text-gray-300 font-bold rounded transition-colors cursor-pointer"
              >
                SAU <ChevronRight size={14} />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
