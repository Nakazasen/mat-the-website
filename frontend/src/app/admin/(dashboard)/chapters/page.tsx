'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getFreshAdminAccessToken } from '@/lib/admin-session';
import {
    AlertTriangle,
    ArrowRight,
    CheckCircle2,
    CheckSquare,
    CheckSquare2,
    ChevronLeft,
    ChevronRight,
    Languages,
    Loader2,
    Pencil,
    PlusCircle,
    RefreshCw,
    Search,
    Trash2,
    Hash,
    Wand2,
} from 'lucide-react';

import { createAdminClient } from '@/lib/supabase-admin';
import {
    getAdminChapterTranslationStatuses,
    improveAdminChaptersBatch,
    improveAdminChapterTranslation,
    translateAdminChapter,
    translateAdminChaptersBatch,
    type AdminChapterTranslateResult,
    type TranslationFailure,
} from '@/lib/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mat-the-website.onrender.com';
const SAFE_BATCH_LIMIT = 2;
const FULL_BATCH_MAX_RETRIES = 3;
const FULL_BATCH_RETRY_DELAY_MS = 2500;
const FULL_BATCH_CHECKPOINT_KEY = 'admin-chapters-full-batch-checkpoint-v1';
const QUALITY_BATCH_CHECKPOINT_KEY = 'admin-chapters-quality-batch-checkpoint-v1';

interface Chapter {
    id: number;
    chapter_number: number;
    title: string;
    word_count?: number;
}

interface ChapterTranslationStatus {
    chapter_number: number;
    published_locales: string[];
    refined_locales: string[];
    failed_locales: string[];
    in_progress_locales: string[];
    published_count: number;
    refined_count: number;
    can_improve: boolean;
    failed_count: number;
    in_progress_count: number;
    attempt_count: number;
    last_error?: string | null;
    last_error_locale?: string | null;
    status_label: string;
    quality_status_label: string;
}

type ActionNotice = {
    tone: 'success' | 'error';
    message: string;
};

type FullBatchCheckpoint = {
    active: boolean;
    total: number;
    blockSize: number;
    nextStart: number;
    translated: number;
    skipped: number;
    failed: number;
    failureDetails: Array<{ chapter_number: number; detail?: string }>;
    updatedAt: string;
};

function formatTranslationFailures(failures: TranslationFailure[] | undefined): string {
    if (!Array.isArray(failures) || failures.length === 0) {
        return 'Không nhận được chi tiết lỗi từ backend.';
    }
    return failures
        .map((item) => `${item.locale || 'unknown'}: ${(item.detail || '').trim() || 'Không rõ nguyên nhân lỗi.'}`)
        .join(' | ');
}

function buildSingleTranslateNotice(chapterNumber: number, result: AdminChapterTranslateResult): ActionNotice {
    const translatedLocales = Array.isArray(result.translated_locales) ? result.translated_locales : [];
    const failedLocales = Array.isArray(result.failed_translations) ? result.failed_translations : [];
    if (failedLocales.length === 0) {
        return {
            tone: 'success',
            message: `Đã dịch chương ${chapterNumber}: ${translatedLocales.join(', ') || 'không có locale nào cần xử lý'}.`,
        };
    }
    if (translatedLocales.length === 0) {
        return {
            tone: 'error',
            message: `Chương ${chapterNumber} chưa dịch được locale nào. ${formatTranslationFailures(failedLocales)}`,
        };
    }
    return {
        tone: 'error',
        message: `Chương ${chapterNumber} dịch được ${translatedLocales.join(', ')}, nhưng còn lỗi: ${formatTranslationFailures(failedLocales)}`,
    };
}

function formatBatchNetworkError(message: string | undefined, completed: number, total: number): string {
    const normalized = (message || '').trim();
    if (!normalized) {
        return `Mất kết nối tới backend khi chạy block tiếp theo. Tiến độ đã giữ tới chương ${completed}/${total}. Bấm chạy lại để tiếp tục phần còn thiếu.`;
    }
    if (normalized.toLowerCase() === 'failed to fetch') {
        return `Mất kết nối tới backend khi chạy block tiếp theo. Tiến độ đã giữ tới chương ${completed}/${total}. Bấm chạy lại để tiếp tục phần còn thiếu.`;
    }
    return normalized;
}

function isTransientBackendFetchError(message: string | undefined): boolean {
    const normalized = (message || '').trim().toLowerCase();
    if (!normalized) return false;
    return (
        normalized === 'failed to fetch'
        || normalized.includes('networkerror')
        || normalized.includes('load failed')
        || normalized.includes('backend')
        || normalized.includes('gateway')
        || normalized.includes('fetch')
    );
}

function sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function readFullBatchCheckpoint(storageKey: string = FULL_BATCH_CHECKPOINT_KEY): FullBatchCheckpoint | null {
    if (typeof window === 'undefined') return null;
    try {
        const raw = window.localStorage.getItem(storageKey);
        if (!raw) return null;
        const parsed = JSON.parse(raw) as Partial<FullBatchCheckpoint>;
        if (
            !parsed
            || typeof parsed.total !== 'number'
            || typeof parsed.blockSize !== 'number'
            || typeof parsed.nextStart !== 'number'
        ) {
            return null;
        }
        return {
            active: parsed.active !== false,
            total: Math.max(0, parsed.total || 0),
            blockSize: Math.max(1, parsed.blockSize || 1),
            nextStart: Math.max(1, parsed.nextStart || 1),
            translated: Math.max(0, parsed.translated || 0),
            skipped: Math.max(0, parsed.skipped || 0),
            failed: Math.max(0, parsed.failed || 0),
            failureDetails: Array.isArray(parsed.failureDetails) ? parsed.failureDetails : [],
            updatedAt: typeof parsed.updatedAt === 'string' ? parsed.updatedAt : '',
        };
    } catch {
        return null;
    }
}

function writeFullBatchCheckpoint(payload: FullBatchCheckpoint, storageKey: string = FULL_BATCH_CHECKPOINT_KEY): void {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(storageKey, JSON.stringify(payload));
}

function clearFullBatchCheckpointStorage(storageKey: string = FULL_BATCH_CHECKPOINT_KEY): void {
    if (typeof window === 'undefined') return;
    window.localStorage.removeItem(storageKey);
}

export default function AdminChaptersPage() {
    const router = useRouter();
    const [chapters, setChapters] = useState<Chapter[]>([]);
    const [loading, setLoading] = useState(true);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [translatingId, setTranslatingId] = useState<number | null>(null);
    const [improvingId, setImprovingId] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [token, setToken] = useState<string | null>(null);

    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalChapters, setTotalChapters] = useState(0);
    const limit = 100;

    const [searchQuery, setSearchQuery] = useState('');
    const [jumpNumber, setJumpNumber] = useState('');
    const [batchStart, setBatchStart] = useState('1');
    const [batchEnd, setBatchEnd] = useState('');
    const [batchOnlyMissing, setBatchOnlyMissing] = useState(true);
    const [batchRunning, setBatchRunning] = useState(false);
    const [batchResult, setBatchResult] = useState<string | null>(null);
    const [batchFailureDetails, setBatchFailureDetails] = useState<Array<{ chapter_number: number; detail?: string }>>([]);
    const [batchBlockSize, setBatchBlockSize] = useState('2');
    const [fullBatchRunning, setFullBatchRunning] = useState(false);
    const [fullBatchProgress, setFullBatchProgress] = useState<{ completed: number; total: number; translated: number; skipped: number; failed: number } | null>(null);
    const [fullBatchCheckpoint, setFullBatchCheckpoint] = useState<FullBatchCheckpoint | null>(null);
    const [qualityBatchRunning, setQualityBatchRunning] = useState(false);
    const [qualityBatchProgress, setQualityBatchProgress] = useState<{ completed: number; total: number; translated: number; skipped: number; failed: number } | null>(null);
    const [qualityBatchCheckpoint, setQualityBatchCheckpoint] = useState<FullBatchCheckpoint | null>(null);
    const [qualityBatchResult, setQualityBatchResult] = useState<string | null>(null);
    const [qualityBatchFailureDetails, setQualityBatchFailureDetails] = useState<Array<{ chapter_number: number; detail?: string }>>([]);
    const [forceQualityRefine, setForceQualityRefine] = useState(false);
    const [translationStatusMap, setTranslationStatusMap] = useState<Record<number, ChapterTranslationStatus>>({});
    const [actionNotice, setActionNotice] = useState<ActionNotice | null>(null);
    const [failureLogNotice, setFailureLogNotice] = useState<string | null>(null);

    useEffect(() => {
        if (!error || error !== 'Failed to fetch') return;

        if (fullBatchProgress) {
            const nextMessage = formatBatchNetworkError(error, fullBatchProgress.completed, fullBatchProgress.total);
            if (nextMessage !== error) {
                setError(nextMessage);
            }
            return;
        }

        const startChapter = Math.max(1, parseInt(batchStart || '1', 10) || 1);
        const endChapter = Math.max(startChapter, parseInt(batchEnd || `${totalChapters || startChapter}`, 10) || startChapter);
        const nextMessage = formatBatchNetworkError(error, startChapter - 1, endChapter);
        if (nextMessage !== error) {
            setError(nextMessage);
        }
    }, [error, fullBatchProgress, batchStart, batchEnd, totalChapters]);

    useEffect(() => {
        const supabase = createAdminClient();
        if (!supabase) {
            setError('Lỗi cấu hình: thiếu biến môi trường NEXT_PUBLIC_SUPABASE_URL.');
            setLoading(false);
            return;
        }
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session) {
                router.push('/admin/login');
                return;
            }
            setToken(session.access_token);
        });
    }, [router]);

    const resolveAdminToken = useCallback(async () => {
        const freshToken = await getFreshAdminAccessToken();
        setToken(freshToken);
        return freshToken;
    }, []);

    const handleClearFailureLogs = useCallback(() => {
        setBatchFailureDetails([]);
        setQualityBatchFailureDetails([]);
        setFailureLogNotice('Da xoa log loi.');
        window.setTimeout(() => setFailureLogNotice(null), 2000);
    }, []);

    const fetchChapters = useCallback(async (page: number) => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE_URL}/api/chapters?page=${page}&limit=${limit}&sort=desc`, { cache: 'no-store' });
            if (!res.ok) throw new Error('Không thể tải danh sách chương');
            const data = await res.json();
            setChapters(data.chapters || []);
            setTotalPages(data.total_pages || 1);
            setTotalChapters(data.total || 0);
            setCurrentPage(page);
            setBatchEnd((current) => current || String(data.total || data.total_pages || ''));
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchChapters(1);
    }, [fetchChapters]);

    useEffect(() => {
        const checkpoint = readFullBatchCheckpoint();
        if (!checkpoint || !checkpoint.active) return;

        setFullBatchCheckpoint(checkpoint);
        setBatchBlockSize(String(checkpoint.blockSize));
        setFullBatchProgress({
            completed: Math.max(0, checkpoint.nextStart - 1),
            total: checkpoint.total,
            translated: checkpoint.translated,
            skipped: checkpoint.skipped,
            failed: checkpoint.failed,
        });
        setBatchFailureDetails(checkpoint.failureDetails || []);
        setBatchResult(
            `Đã khôi phục checkpoint tới chương ${Math.max(0, checkpoint.nextStart - 1)}/${checkpoint.total}. Bấm tiếp tục để chạy phần còn thiếu.`
        );
    }, []);

    useEffect(() => {
        const checkpoint = readFullBatchCheckpoint(QUALITY_BATCH_CHECKPOINT_KEY);
        if (!checkpoint || !checkpoint.active) return;

        setQualityBatchCheckpoint(checkpoint);
        setBatchBlockSize(String(checkpoint.blockSize));
        setQualityBatchProgress({
            completed: Math.max(0, checkpoint.nextStart - 1),
            total: checkpoint.total,
            translated: checkpoint.translated,
            skipped: checkpoint.skipped,
            failed: checkpoint.failed,
        });
        setQualityBatchFailureDetails(checkpoint.failureDetails || []);
        setQualityBatchResult(
            `Đã khôi phục checkpoint nâng chất lượng tới chương ${Math.max(0, checkpoint.nextStart - 1)}/${checkpoint.total}. Bấm tiếp tục để chạy phần còn thiếu.`
        );
    }, []);

    const refreshTranslationStatuses = useCallback(async (targetChapters?: number[]) => {
        if (!token) return;
        const chapterNumbers = (targetChapters && targetChapters.length > 0)
            ? targetChapters
            : chapters.map((chapter) => chapter.chapter_number);
        if (chapterNumbers.length === 0) return;
        try {
            const freshToken = await resolveAdminToken();
            const result = await getAdminChapterTranslationStatuses(chapterNumbers, freshToken);
            setTranslationStatusMap((prev) => {
                const nextMap = { ...prev };
                for (const item of result.statuses || []) {
                    nextMap[item.chapter_number] = item;
                }
                return nextMap;
            });
        } catch {
            // Keep the page usable even if status summary fails.
        }
    }, [chapters, resolveAdminToken, token]);

    useEffect(() => {
        refreshTranslationStatuses();
    }, [refreshTranslationStatuses]);

    const filteredChapters = useMemo(() => {
        if (!searchQuery.trim()) return chapters;
        const query = searchQuery.toLowerCase().trim();
        return chapters.filter((chapter) =>
            chapter.title.toLowerCase().includes(query) || chapter.chapter_number.toString().includes(query),
        );
    }, [chapters, searchQuery]);

    const handleJump = (event?: React.FormEvent) => {
        event?.preventDefault();
        if (!jumpNumber) return;
        const value = parseInt(jumpNumber, 10);
        if (Number.isNaN(value) || value < 1) {
            alert('Vui lòng nhập số chương hợp lệ.');
            return;
        }
        router.push(`/admin/chapters/${value}/edit`);
    };

    const handleDelete = async (chapterNumber: number) => {
        if (!token) return;
        if (!confirm(`Xóa chương ${chapterNumber}? Hành động này không thể hoàn tác.`)) return;

        setDeletingId(chapterNumber);
        try {
            const freshToken = await resolveAdminToken();
            const res = await fetch(`${API_BASE_URL}/api/admin/chapters/${chapterNumber}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${freshToken}` },
            });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Lỗi khi xóa chương');
            }
            await fetchChapters(currentPage);
        } catch (err: any) {
            alert(`Lỗi: ${err.message}`);
        } finally {
            setDeletingId(null);
        }
    };

    const handleTranslate = async (chapterNumber: number) => {
        if (!token) return;
        setTranslatingId(chapterNumber);
        setActionNotice(null);
        try {
            const freshToken = await resolveAdminToken();
            const result = await translateAdminChapter(chapterNumber, freshToken);
            setActionNotice(buildSingleTranslateNotice(chapterNumber, result));
            await refreshTranslationStatuses([chapterNumber]);
        } catch (err: any) {
            setActionNotice({
                tone: 'error',
                message: `Lỗi dịch chương ${chapterNumber}: ${err?.message || 'Không nhận được thông báo lỗi từ backend.'}`,
            });
            await refreshTranslationStatuses([chapterNumber]);
        } finally {
            setTranslatingId(null);
        }
    };

    const handleImproveQuality = async (chapterNumber: number) => {
        if (!token) return;
        setImprovingId(chapterNumber);
        setActionNotice(null);
        try {
            const freshToken = await resolveAdminToken();
            const result = await improveAdminChapterTranslation(chapterNumber, freshToken, forceQualityRefine);
            const translatedLocales = Array.isArray(result.translated_locales) ? result.translated_locales : [];
            const skippedLocales = Array.isArray(result.skipped_locales) ? result.skipped_locales : [];
            const failedLocales = Array.isArray(result.failed_translations) ? result.failed_translations : [];

            if (translatedLocales.length === 0 && failedLocales.length === 0 && skippedLocales.length > 0) {
                setActionNotice({
                    tone: 'success',
                    message: `Chương ${chapterNumber} đã được nâng chất lượng trước đó: ${skippedLocales.join(', ')}. Bật ép chạy lại nếu muốn refine lại.`,
                });
            } else if (failedLocales.length === 0) {
                setActionNotice({
                    tone: 'success',
                    message: `Đã cải thiện chất lượng chương ${chapterNumber}: ${translatedLocales.join(', ') || 'không có locale nào được cập nhật'}.`,
                });
            } else {
                setActionNotice({
                    tone: translatedLocales.length > 0 ? 'success' : 'error',
                    message: translatedLocales.length > 0
                        ? `Chương ${chapterNumber} đã cải thiện ${translatedLocales.join(', ')}, nhưng vẫn còn lỗi: ${formatTranslationFailures(failedLocales)}`
                        : `Không thể cải thiện chất lượng chương ${chapterNumber}. ${formatTranslationFailures(failedLocales)}`,
                });
            }
            await refreshTranslationStatuses([chapterNumber]);
        } catch (err: any) {
            setActionNotice({
                tone: 'error',
                message: `Lỗi cải thiện chất lượng chương ${chapterNumber}: ${err?.message || 'Không nhận được thông báo lỗi từ backend.'}`,
            });
            await refreshTranslationStatuses([chapterNumber]);
        } finally {
            setImprovingId(null);
        }
    };

    const handleClearQualityBatchCheckpoint = () => {
        setQualityBatchCheckpoint(null);
        setQualityBatchProgress(null);
        setQualityBatchFailureDetails([]);
        setQualityBatchResult(null);
        clearFullBatchCheckpointStorage(QUALITY_BATCH_CHECKPOINT_KEY);
    };

    const handleImproveAllTranslatedDrafts = async () => {
        if (!token) return;

        const checkpoint = qualityBatchCheckpoint?.active ? qualityBatchCheckpoint : null;
        const total = Math.max(totalChapters, checkpoint?.total || 0);
        const blockSize = Math.min(
            SAFE_BATCH_LIMIT,
            Math.max(1, checkpoint?.blockSize || parseInt(batchBlockSize || '2', 10) || 2),
        );
        if (total === 0) {
            setError('Không có chương nào để nâng chất lượng.');
            return;
        }

        const initialStart = Math.min(Math.max(1, checkpoint?.nextStart || 1), Math.max(total, 1));

        setQualityBatchRunning(true);
        setBatchRunning(false);
        setError(null);
        setActionNotice(null);
        setQualityBatchResult(
            checkpoint
                ? `Tiếp tục nâng chất lượng từ checkpoint chương ${Math.max(0, initialStart - 1)}/${total}...`
                : 'Bắt đầu nâng chất lượng toàn bộ bản dịch phủ...',
        );

        let translated = checkpoint?.translated || 0;
        let skipped = checkpoint?.skipped || 0;
        let failed = checkpoint?.failed || 0;
        let completed = Math.max(0, initialStart - 1);
        const aggregatedFailures: Array<{ chapter_number: number; detail?: string }> = checkpoint?.failureDetails
            ? [...checkpoint.failureDetails]
            : [];

        setQualityBatchFailureDetails([...aggregatedFailures]);
        setQualityBatchProgress({ completed, total, translated, skipped, failed });

        const persistCheckpoint = (nextStart: number, isActive: boolean) => {
            const payload: FullBatchCheckpoint = {
                active: isActive,
                total,
                blockSize,
                nextStart,
                translated,
                skipped,
                failed,
                failureDetails: aggregatedFailures.slice(-200),
                updatedAt: new Date().toISOString(),
            };
            if (isActive) {
                writeFullBatchCheckpoint(payload, QUALITY_BATCH_CHECKPOINT_KEY);
                setQualityBatchCheckpoint(payload);
            } else {
                clearFullBatchCheckpointStorage(QUALITY_BATCH_CHECKPOINT_KEY);
                setQualityBatchCheckpoint(null);
            }
        };

        persistCheckpoint(initialStart, initialStart <= total);

        try {
            for (let start = initialStart; start <= total; start += blockSize) {
                const end = Math.min(start + blockSize - 1, total);
                let result: Awaited<ReturnType<typeof improveAdminChaptersBatch>> | null = null;
                let lastBlockError: any = null;

                for (let attempt = 1; attempt <= FULL_BATCH_MAX_RETRIES; attempt += 1) {
                    try {
                        const freshToken = await resolveAdminToken();
                        result = await improveAdminChaptersBatch(
                            {
                                start_chapter: start,
                                end_chapter: end,
                                only_unrefined: !forceQualityRefine,
                                force: forceQualityRefine,
                            },
                            freshToken,
                        );
                        break;
                    } catch (err: any) {
                        lastBlockError = err;
                        if (!isTransientBackendFetchError(err?.message) || attempt === FULL_BATCH_MAX_RETRIES) {
                            throw err;
                        }
                        setQualityBatchResult(`Mất kết nối tạm thời ở block ${start}-${end}. Đang thử lại lần ${attempt + 1}/${FULL_BATCH_MAX_RETRIES}...`);
                        await sleep(FULL_BATCH_RETRY_DELAY_MS * attempt);
                    }
                }

                if (!result) {
                    throw lastBlockError || new Error('Failed to improve current block');
                }

                translated += result.translated_count;
                skipped += result.skipped_count;
                failed += result.failed_count;
                completed = end;
                aggregatedFailures.push(...(result.failed_chapters || []));

                setQualityBatchProgress({ completed, total, translated, skipped, failed });
                setQualityBatchResult(
                    `Đã nâng chất lượng tới chương ${end}/${total}. Đã refine: ${translated}, bỏ qua: ${skipped}, lỗi: ${failed}.`
                );
                setQualityBatchFailureDetails([...aggregatedFailures]);
                persistCheckpoint(Math.min(end + 1, total), end < total);
                if (start + blockSize <= total) {
                    await sleep(600);
                }
            }
        } catch (err: any) {
            setError(err?.message || 'Không thể nâng chất lượng hàng loạt.');
        } finally {
            setQualityBatchRunning(false);
            await refreshTranslationStatuses();
        }
    };

    const handleBatchTranslate = async () => {
        if (!token) return;

        const startChapter = Math.max(1, parseInt(batchStart || '1', 10) || 1);
        const endChapter = Math.max(startChapter, parseInt(batchEnd || `${totalChapters || startChapter}`, 10) || startChapter);
        const selectedCount = endChapter - startChapter + 1;
        if (selectedCount > SAFE_BATCH_LIMIT) {
            setError(`Batch thủ công hiện chỉ nên chạy tối đa ${SAFE_BATCH_LIMIT} chương mỗi lượt. Hãy chia nhỏ khoảng chương.`);
            return;
        }

        setBatchRunning(true);
        setBatchResult(null);
        setBatchFailureDetails([]);
        setError(null);
        setActionNotice(null);

        try {
            const freshToken = await resolveAdminToken();
            const result = await translateAdminChaptersBatch(
                {
                    start_chapter: startChapter,
                    end_chapter: endChapter,
                    only_missing: batchOnlyMissing,
                },
                freshToken,
            );
            setBatchResult(
                `Đã xử lý ${startChapter}-${endChapter}. Dịch mới: ${result.translated_count}, bỏ qua: ${result.skipped_count}, lỗi: ${result.failed_count}.`
            );
            setBatchFailureDetails(result.failed_chapters || []);
            await refreshTranslationStatuses();
        } catch (err: any) {
            setError(err?.message || 'Không thể batch dịch chương.');
        } finally {
            setBatchRunning(false);
        }
    };

    const handleClearFullBatchCheckpoint = () => {
        setFullBatchCheckpoint(null);
        setFullBatchProgress(null);
        setBatchFailureDetails([]);
        setBatchResult(null);
        clearFullBatchCheckpointStorage();
    };

    const handleTranslateAllMissing = async () => {
        if (!token) return;

        const checkpoint = fullBatchCheckpoint?.active ? fullBatchCheckpoint : null;
        const total = Math.max(totalChapters, checkpoint?.total || 0);
        const blockSize = Math.min(
            SAFE_BATCH_LIMIT,
            Math.max(1, checkpoint?.blockSize || parseInt(batchBlockSize || '2', 10) || 2),
        );
        if (total === 0) {
            setError('Không có chương nào để dịch.');
            return;
        }

        const initialStart = Math.min(Math.max(1, checkpoint?.nextStart || 1), Math.max(total, 1));

        setFullBatchRunning(true);
        setBatchRunning(false);
        setError(null);
        setActionNotice(null);
        setBatchResult(
            checkpoint
                ? `Tiếp tục từ checkpoint chương ${Math.max(0, initialStart - 1)}/${total}...`
                : 'Bắt đầu chạy toàn bộ chương còn thiếu...',
        );

        let translated = checkpoint?.translated || 0;
        let skipped = checkpoint?.skipped || 0;
        let failed = checkpoint?.failed || 0;
        let completed = Math.max(0, initialStart - 1);
        const aggregatedFailures: Array<{ chapter_number: number; detail?: string }> = checkpoint?.failureDetails
            ? [...checkpoint.failureDetails]
            : [];

        setBatchFailureDetails([...aggregatedFailures]);
        setFullBatchProgress({ completed, total, translated, skipped, failed });

        const persistCheckpoint = (nextStart: number, isActive: boolean) => {
            const payload: FullBatchCheckpoint = {
                active: isActive,
                total,
                blockSize,
                nextStart,
                translated,
                skipped,
                failed,
                failureDetails: aggregatedFailures.slice(-200),
                updatedAt: new Date().toISOString(),
            };
            if (isActive) {
                writeFullBatchCheckpoint(payload);
                setFullBatchCheckpoint(payload);
            } else {
                clearFullBatchCheckpointStorage();
                setFullBatchCheckpoint(null);
            }
        };

        persistCheckpoint(initialStart, initialStart <= total);

        try {
            for (let start = initialStart; start <= total; start += blockSize) {
                const end = Math.min(start + blockSize - 1, total);
                let result: Awaited<ReturnType<typeof translateAdminChaptersBatch>> | null = null;
                let lastBlockError: any = null;

                for (let attempt = 1; attempt <= FULL_BATCH_MAX_RETRIES; attempt += 1) {
                    try {
                        const freshToken = await resolveAdminToken();
                        result = await translateAdminChaptersBatch(
                            {
                                start_chapter: start,
                                end_chapter: end,
                                only_missing: true,
                            },
                            freshToken,
                        );
                        break;
                    } catch (err: any) {
                        lastBlockError = err;
                        if (!isTransientBackendFetchError(err?.message) || attempt === FULL_BATCH_MAX_RETRIES) {
                            throw err;
                        }
                        setBatchResult(`Mất kết nối tạm thời ở block ${start}-${end}. Đang thử lại lần ${attempt + 1}/${FULL_BATCH_MAX_RETRIES}...`);
                        await sleep(FULL_BATCH_RETRY_DELAY_MS * attempt);
                    }
                }

                if (!result) {
                    throw lastBlockError || new Error('Failed to translate current block');
                }

                translated += result.translated_count;
                skipped += result.skipped_count;
                failed += result.failed_count;
                completed = end;
                aggregatedFailures.push(...(result.failed_chapters || []));

                setFullBatchProgress({
                    completed,
                    total,
                    translated,
                    skipped,
                    failed,
                });
                setBatchResult(
                    `Đã chạy tới chương ${end}/${total}. Dịch mới: ${translated}, bỏ qua: ${skipped}, lỗi: ${failed}.`
                );
                setBatchFailureDetails([...aggregatedFailures]);
                persistCheckpoint(Math.min(end + 1, total), end < total);
                if (start + blockSize <= total) {
                    await sleep(600);
                }
            }
        } catch (err: any) {
            setError(err?.message || 'Không thể dịch toàn bộ chương còn thiếu.');
        } finally {
            setFullBatchRunning(false);
            await refreshTranslationStatuses();
        }
    };

    return (
        <div className="pb-10">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-xl font-mono text-gray-100 tracking-wider uppercase font-bold">Quản lý chương</h1>
                    <p className="text-xs font-mono text-gray-600 mt-1">
                        Hiển thị {chapters.length} / {totalChapters} chương, trang {currentPage}/{totalPages}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => fetchChapters(currentPage)}
                        className="flex items-center gap-1.5 px-3 py-2 border border-gray-700 text-gray-400 hover:text-gray-200 rounded font-mono text-xs transition-all active:scale-95"
                    >
                        <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                        Làm mới
                    </button>
                    <Link
                        href="/admin/chapters/new"
                        className="flex items-center gap-1.5 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded font-mono text-xs font-bold transition-all shadow-lg shadow-green-900/20 active:scale-95"
                    >
                        <PlusCircle size={14} />
                        Đăng chương mới
                    </Link>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-toxic-green-DEFAULT transition-colors" size={16} />
                    <input
                        type="text"
                        placeholder="Tìm theo tiêu đề hoặc số chương..."
                        value={searchQuery}
                        onChange={(event) => setSearchQuery(event.target.value)}
                        className="w-full bg-[#0d0d0d] border border-gray-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-toxic-green-DEFAULT/50 focus:ring-1 focus:ring-toxic-green-DEFAULT/20 transition-all font-mono"
                    />
                    {searchQuery && (
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono text-gray-600">
                            {filteredChapters.length} kết quả
                        </span>
                    )}
                </div>

                <form onSubmit={handleJump} className="relative group flex gap-2">
                    <div className="relative flex-1">
                        <Hash className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-400 transition-colors" size={16} />
                        <input
                            type="number"
                            placeholder="Nhảy đến chương số..."
                            value={jumpNumber}
                            onChange={(event) => setJumpNumber(event.target.value)}
                            className="w-full bg-[#0d0d0d] border border-gray-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all font-mono"
                        />
                    </div>
                    <button
                        type="submit"
                        className="px-4 bg-gray-800 hover:bg-gray-700 text-blue-400 border border-gray-700 hover:border-blue-500/50 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-2 whitespace-nowrap active:scale-95"
                    >
                        NHẢY <ArrowRight size={14} />
                    </button>
                </form>
            </div>

            <div className="mb-6 rounded-lg border border-gray-800 bg-[#0d0d0d] p-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
                    <div>
                        <p className="font-mono text-xs tracking-widest text-purple-300 uppercase">Batch Translate</p>
                        <p className="mt-1 text-xs text-gray-500">
                            Chạy hàng loạt theo khoảng chương. Để ổn định, batch thủ công hiện chỉ nên chạy tối đa 2 chương mỗi lượt.
                        </p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 w-full lg:w-auto">
                        <input
                            type="number"
                            min={1}
                            value={batchStart}
                            onChange={(event) => setBatchStart(event.target.value)}
                            className="bg-black border border-gray-800 rounded px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
                            placeholder="Từ chương"
                        />
                        <input
                            type="number"
                            min={1}
                            value={batchEnd}
                            onChange={(event) => setBatchEnd(event.target.value)}
                            className="bg-black border border-gray-800 rounded px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
                            placeholder="Đến chương"
                        />
                        <label className="flex items-center gap-2 rounded border border-gray-800 px-3 py-2 text-xs font-mono text-gray-300">
                            <input
                                type="checkbox"
                                checked={batchOnlyMissing}
                                onChange={(event) => setBatchOnlyMissing(event.target.checked)}
                                className="accent-purple-500"
                            />
                            Chỉ dịch chương còn thiếu
                        </label>
                        <button
                            type="button"
                            onClick={handleBatchTranslate}
                            disabled={!token || batchRunning || fullBatchRunning}
                            className="inline-flex items-center justify-center gap-2 rounded border border-purple-700/60 px-4 py-2 text-xs font-mono text-purple-300 hover:bg-purple-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {batchRunning ? <Loader2 size={14} className="animate-spin" /> : <CheckSquare size={14} />}
                            {batchRunning ? 'ĐANG CHẠY BATCH...' : 'DỊCH THEO KHOẢNG'}
                        </button>
                    </div>
                </div>
                <div className="mt-4 flex flex-col gap-3 border-t border-gray-800 pt-4 lg:flex-row lg:items-end lg:justify-between">
                    <div>
                        <p className="font-mono text-xs tracking-widest text-cyan-300 uppercase">Translate All Missing</p>
                        <p className="mt-1 text-xs text-gray-500">
                            Tự động chạy từ chương 1 đến chương {totalChapters}, chia block nhỏ để hạn chế timeout và dễ theo dõi tiến độ.
                        </p>
                        {fullBatchCheckpoint?.active && (
                            <p className="mt-2 text-xs text-cyan-200/90">
                                Có checkpoint tới chương {Math.max(0, fullBatchCheckpoint.nextStart - 1)}/{fullBatchCheckpoint.total}.
                                Tải lại trang vẫn có thể tiếp tục từ đây.
                            </p>
                        )}
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-[140px_auto_auto] gap-3 w-full lg:w-auto">
                        <input
                            type="number"
                            min={1}
                            value={batchBlockSize}
                            onChange={(event) => setBatchBlockSize(event.target.value)}
                            className="bg-black border border-gray-800 rounded px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
                            placeholder="Kích thước block"
                        />
                        <button
                            type="button"
                            onClick={handleTranslateAllMissing}
                            disabled={!token || fullBatchRunning || batchRunning}
                            className="inline-flex items-center justify-center gap-2 rounded border border-cyan-700/60 px-4 py-2 text-xs font-mono text-cyan-300 hover:bg-cyan-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {fullBatchRunning ? <Loader2 size={14} className="animate-spin" /> : <CheckSquare2 size={14} />}
                            {fullBatchRunning ? 'ĐANG DỊCH TOÀN BỘ...' : 'DỊCH TOÀN BỘ CHƯƠNG CHƯA DỊCH'}
                        </button>
                    </div>
                </div>
                <div className="mt-4 flex flex-col gap-3 border-t border-gray-800 pt-4 lg:flex-row lg:items-end lg:justify-between">
                    <div>
                        <p className="font-mono text-xs tracking-widest text-emerald-300 uppercase">Improve Existing Drafts</p>
                        <p className="mt-1 text-xs text-gray-500">
                            Tự động nâng chất lượng các chương đã có bản dịch published nhưng chưa refine. Mặc định sẽ bỏ qua những locale đã nâng chất lượng rồi.
                        </p>
                    </div>
                    <div className="grid grid-cols-1 gap-3 w-full lg:w-auto">
                        <label className="flex items-center gap-2 rounded border border-gray-800 px-3 py-2 text-xs font-mono text-gray-300">
                            <input
                                type="checkbox"
                                checked={forceQualityRefine}
                                onChange={(event) => setForceQualityRefine(event.target.checked)}
                                className="accent-emerald-500"
                            />
                            Ép chạy lại cả chương đã refine
                        </label>
                        <div className="grid grid-cols-1 sm:grid-cols-[auto_auto] gap-3 w-full lg:w-auto">
                            <button
                                type="button"
                                onClick={handleImproveAllTranslatedDrafts}
                                disabled={!token || qualityBatchRunning || fullBatchRunning || batchRunning}
                                className="inline-flex items-center justify-center gap-2 rounded border border-emerald-700/60 px-4 py-2 text-xs font-mono text-emerald-300 hover:bg-emerald-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                {qualityBatchRunning ? <Loader2 size={14} className="animate-spin" /> : <Wand2 size={14} />}
                                {qualityBatchRunning ? 'ĐANG NÂNG CHẤT LƯỢNG...' : 'NÂNG CHẤT LƯỢNG CÁC CHƯƠNG ĐÃ DỊCH'}
                            </button>
                            {qualityBatchCheckpoint?.active && !qualityBatchRunning && (
                                <button
                                    type="button"
                                    onClick={handleClearQualityBatchCheckpoint}
                                    className="inline-flex items-center justify-center rounded border border-gray-700 px-3 py-2 text-xs font-mono text-gray-300 hover:bg-gray-800/80"
                                >
                                    XÓA CHECKPOINT QUALITY
                                </button>
                            )}
                        </div>
                    </div>
                </div>
                {batchResult && (
                    <div className="mt-3 rounded border border-green-900/50 bg-green-950/30 px-3 py-2 text-sm text-green-300">
                        {batchResult}
                    </div>
                )}
                {qualityBatchResult && (
                    <div className="mt-3 rounded border border-emerald-900/50 bg-emerald-950/20 px-3 py-2 text-sm text-emerald-300">
                        {qualityBatchResult}
                    </div>
                )}
                {fullBatchCheckpoint?.active && !fullBatchRunning && (
                    <div className="mt-3 flex flex-col gap-2 rounded border border-cyan-900/40 bg-cyan-950/10 px-3 py-3 text-sm text-cyan-100 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <div className="font-mono text-xs uppercase tracking-widest text-cyan-300">Checkpoint khả dụng</div>
                            <div className="mt-1 text-xs text-cyan-100/80">
                                Hệ thống đang giữ tiến độ tới chương {Math.max(0, fullBatchCheckpoint.nextStart - 1)}/{fullBatchCheckpoint.total}.
                                Bấm nút dịch lại để tiếp tục, hoặc xóa checkpoint để bắt đầu từ đầu.
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={handleClearFullBatchCheckpoint}
                            className="inline-flex items-center justify-center rounded border border-gray-700 px-3 py-2 text-xs font-mono text-gray-300 hover:bg-gray-800/80"
                        >
                            XÓA CHECKPOINT
                        </button>
                    </div>
                )}
                {qualityBatchCheckpoint?.active && !qualityBatchRunning && (
                    <div className="mt-3 flex flex-col gap-2 rounded border border-emerald-900/40 bg-emerald-950/10 px-3 py-3 text-sm text-emerald-100 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <div className="font-mono text-xs uppercase tracking-widest text-emerald-300">Checkpoint quality khả dụng</div>
                            <div className="mt-1 text-xs text-emerald-100/80">
                                Hệ thống đang ghi nhớ tiến độ nâng chất lượng tới chương {Math.max(0, qualityBatchCheckpoint.nextStart - 1)}/{qualityBatchCheckpoint.total}.
                                Bấm nút nâng chất lượng lại để tiếp tục, hoặc xóa checkpoint để bắt đầu từ đầu.
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={handleClearQualityBatchCheckpoint}
                            className="inline-flex items-center justify-center rounded border border-gray-700 px-3 py-2 text-xs font-mono text-gray-300 hover:bg-gray-800/80"
                        >
                            XÓA CHECKPOINT QUALITY
                        </button>
                    </div>
                )}
                {fullBatchProgress && (
                    <div className="mt-3 rounded border border-cyan-900/50 bg-cyan-950/20 px-3 py-3 text-sm text-cyan-200">
                        <div className="font-mono text-xs uppercase tracking-widest text-cyan-300">
                            Đã xong {fullBatchProgress.completed} / {fullBatchProgress.total} chương
                        </div>
                        <div className="mt-1">
                            Dịch mới: {fullBatchProgress.translated} | Bỏ qua: {fullBatchProgress.skipped} | Lỗi: {fullBatchProgress.failed}
                        </div>
                    </div>
                )}
                {qualityBatchProgress && (
                    <div className="mt-3 rounded border border-emerald-900/50 bg-emerald-950/20 px-3 py-3 text-sm text-emerald-200">
                        <div className="font-mono text-xs uppercase tracking-widest text-emerald-300">
                            Đã nâng chất lượng {qualityBatchProgress.completed} / {qualityBatchProgress.total} chương
                        </div>
                        <div className="mt-1">
                            Refine mới: {qualityBatchProgress.translated} | Bỏ qua: {qualityBatchProgress.skipped} | Lỗi: {qualityBatchProgress.failed}
                        </div>
                    </div>
                )}
                {batchFailureDetails.length > 0 && (
                    <div className="mt-3 rounded border border-red-900/50 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                        <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-xs uppercase tracking-widest text-red-300">
                            <span>Chi tiết lỗi</span>
                            <button
                                type="button"
                                onClick={handleClearFailureLogs}
                                className="inline-flex items-center justify-center rounded border border-red-900/60 px-2.5 py-1 text-[11px] font-mono text-red-100 hover:bg-red-900/40"
                            >
                                XOA LOG LOI
                            </button>
                        </div>
                        <div className="mt-2 space-y-2">
                            {batchFailureDetails.slice(0, 12).map((item) => (
                                <div key={`${item.chapter_number}-${item.detail || 'error'}`} className="rounded border border-red-900/40 bg-black/20 px-3 py-2">
                                    <div className="font-medium">Chương {item.chapter_number}</div>
                                    <div className="mt-1 text-xs text-red-300/90 whitespace-pre-wrap break-words">
                                        {item.detail || 'Không rõ nguyên nhân lỗi.'}
                                    </div>
                                </div>
                            ))}
                            {batchFailureDetails.length > 12 && (
                                <div className="text-xs text-red-300/80">
                                    Còn {batchFailureDetails.length - 12} lỗi khác chưa hiển thị.
                                </div>
                            )}
                        </div>
                    </div>
                )}
                {qualityBatchFailureDetails.length > 0 && (
                    <div className="mt-3 rounded border border-red-900/50 bg-red-950/20 px-3 py-3 text-sm text-red-200">
                        <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-xs uppercase tracking-widest text-red-300">
                            <span>Chi tiết lỗi nâng chất lượng</span>
                            <button
                                type="button"
                                onClick={handleClearFailureLogs}
                                className="inline-flex items-center justify-center rounded border border-red-900/60 px-2.5 py-1 text-[11px] font-mono text-red-100 hover:bg-red-900/40"
                            >
                                XOA LOG LOI
                            </button>
                        </div>
                        <div className="mt-2 space-y-2">
                            {qualityBatchFailureDetails.slice(0, 12).map((item) => (
                                <div key={`${item.chapter_number}-${item.detail || 'quality-error'}`} className="rounded border border-red-900/40 bg-black/20 px-3 py-2">
                                    <div className="font-medium">Chương {item.chapter_number}</div>
                                    <div className="mt-1 text-xs text-red-300/90 whitespace-pre-wrap break-words">
                                        {item.detail || 'Không rõ nguyên nhân lỗi.'}
                                    </div>
                                </div>
                            ))}
                            {qualityBatchFailureDetails.length > 12 && (
                                <div className="text-xs text-red-300/80">
                                    Còn {qualityBatchFailureDetails.length - 12} lỗi khác chưa hiển thị
                                </div>
                            )}
                        </div>
                    </div>
                )}
                {failureLogNotice && (
                    <div className="mt-3 rounded border border-emerald-900/40 bg-emerald-950/20 px-3 py-2 text-xs text-emerald-200">
                        {failureLogNotice}
                    </div>
                )}
            </div>

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-3 text-sm mb-4">
                    <AlertTriangle size={14} />
                    <span>{error}</span>
                </div>
            )}

            {actionNotice && (
                <div
                    className={`flex items-start gap-2 rounded p-3 text-sm mb-4 ${
                        actionNotice.tone === 'success'
                            ? 'border border-green-900/50 bg-green-950/30 text-green-300'
                            : 'border border-red-900/50 bg-red-950/30 text-red-200'
                    }`}
                >
                    {actionNotice.tone === 'success'
                        ? <CheckCircle2 size={14} className="mt-0.5 shrink-0" />
                        : <AlertTriangle size={14} className="mt-0.5 shrink-0" />}
                    <span className="whitespace-pre-wrap break-words">{actionNotice.message}</span>
                </div>
            )}

            {loading ? (
                <div className="space-y-2">
                    {Array.from({ length: 15 }).map((_, index) => (
                        <div key={index} className="h-12 bg-[#0d0d0d] rounded animate-pulse border border-gray-800" />
                    ))}
                </div>
            ) : (
                <>
                    <div className="bg-[#0d0d0d] border border-gray-800 rounded-lg overflow-hidden mb-6">
                        <table className="w-full text-sm">
                            <thead className="hidden md:table-header-group">
                                <tr className="border-b border-gray-800 bg-[#111111]">
                                    <th className="px-4 py-3 text-left font-mono text-xs text-gray-600 tracking-widest">#</th>
                                    <th className="px-4 py-3 text-left font-mono text-xs text-gray-600 tracking-widest">TIÊU ĐỀ</th>
                                    <th className="px-4 py-3 text-right font-mono text-xs text-gray-600 tracking-widest hidden md:table-cell">TỪ</th>
                                    <th className="px-4 py-3 text-right font-mono text-xs text-gray-600 tracking-widest">HÀNH ĐỘNG</th>
                                </tr>
                            </thead>
                            <tbody className="flex flex-col md:table-row-group">
                                {filteredChapters.length > 0 ? (
                                    filteredChapters.map((chapter) => (
                                        <tr key={chapter.id} className="flex flex-col md:table-row border-b border-gray-800/50 hover:bg-gray-800/20 transition-colors p-4 md:p-0">
                                            <td className="md:table-cell py-1 md:px-4 md:py-3 font-mono text-xs text-green-400 whitespace-nowrap font-bold">
                                                <span className="md:hidden text-gray-600 mr-2">CHƯƠNG</span>
                                                {String(chapter.chapter_number).padStart(3, '0')}
                                            </td>
                                            <td className="md:table-cell py-2 md:px-4 md:py-3 text-gray-200">
                                                <div className="max-w-xs md:max-w-md truncate font-medium">{chapter.title}</div>
                                                {translationStatusMap[chapter.chapter_number] && (
                                                    <div className="mt-2 space-y-1">
                                                        <div className="text-[11px] font-mono text-cyan-300">
                                                            {translationStatusMap[chapter.chapter_number].status_label}
                                                        </div>
                                                        <div className="text-[11px] text-gray-500">
                                                            Hoàn thành {translationStatusMap[chapter.chapter_number].published_count}/3
                                                            {translationStatusMap[chapter.chapter_number].in_progress_count > 0 && ` | Đang dịch: ${translationStatusMap[chapter.chapter_number].in_progress_locales.join(', ')}`}
                                                            {translationStatusMap[chapter.chapter_number].failed_count > 0 && ` | Lỗi: ${translationStatusMap[chapter.chapter_number].failed_locales.join(', ')}`}
                                                        </div>
                                                        <div className="text-[11px] text-cyan-300/80">
                                                            {translationStatusMap[chapter.chapter_number].quality_status_label}
                                                        </div>
                                                        {translationStatusMap[chapter.chapter_number].attempt_count > 0 && (
                                                            <div className="text-[11px] text-amber-300/90">
                                                                Đã thử {translationStatusMap[chapter.chapter_number].attempt_count} lần
                                                              </div>
                                                        )}
                                                        {translationStatusMap[chapter.chapter_number].last_error && (
                                                            <div className="text-[11px] text-red-300/90 line-clamp-2">
                                                                Lỗi gần nhất{translationStatusMap[chapter.chapter_number].last_error_locale ? ` (${translationStatusMap[chapter.chapter_number].last_error_locale})` : ''}: {translationStatusMap[chapter.chapter_number].last_error}
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-4 py-3 text-right font-mono text-xs text-gray-600 hidden md:table-cell">
                                                {chapter.word_count?.toLocaleString() || '—'}
                                            </td>
                                            <td className="md:table-cell py-3 md:px-4 md:py-3 text-right">
                                                <div className="flex items-center justify-start md:justify-end gap-2 flex-wrap">
                                                    <button
                                                        onClick={() => handleTranslate(chapter.chapter_number)}
                                                        disabled={!token || translatingId === chapter.chapter_number || improvingId === chapter.chapter_number}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 border border-purple-700/60 hover:border-purple-500 text-purple-300 hover:text-purple-200 disabled:opacity-50 rounded text-xs font-mono transition-all hover:bg-purple-500/10"
                                                    >
                                                        <Languages size={10} />
                                                        {translatingId === chapter.chapter_number ? 'ĐANG DỊCH...' : 'DỊCH 3 NGÔN NGỮ'}
                                                    </button>
                                                    <button
                                                        onClick={() => handleImproveQuality(chapter.chapter_number)}
                                                        disabled={
                                                            !token
                                                            || improvingId === chapter.chapter_number
                                                            || translatingId === chapter.chapter_number
                                                            || (translationStatusMap[chapter.chapter_number]?.published_count || 0) === 0
                                                            || (!forceQualityRefine && !translationStatusMap[chapter.chapter_number]?.can_improve)
                                                        }
                                                        className="flex items-center gap-1.5 px-3 py-1.5 border border-cyan-700/60 hover:border-cyan-500 text-cyan-300 hover:text-cyan-200 disabled:opacity-50 rounded text-xs font-mono transition-all hover:bg-cyan-500/10"
                                                        title={
                                                            (translationStatusMap[chapter.chapter_number]?.published_count || 0) === 0
                                                                ? 'Cần có ít nhất một bản dịch đã xuất bản để cải thiện chất lượng'
                                                                : (!forceQualityRefine && !translationStatusMap[chapter.chapter_number]?.can_improve)
                                                                    ? 'Chương này đã được nâng chất lượng rồi. Bật ép chạy lại nếu muốn refine lại.'
                                                                    : 'Cải thiện lại chất lượng bản dịch hiện có'
                                                        }
                                                    >
                                                        <Wand2 size={10} />
                                                        {improvingId === chapter.chapter_number ? 'ĐANG REFINE...' : 'NÂNG CHẤT LƯỢNG'}
                                                    </button>
                                                    <div className="flex gap-2 w-full sm:w-auto">
                                                        <Link
                                                            href={`/admin/chapters/${chapter.chapter_number}/edit`}
                                                            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 border border-gray-700 hover:border-blue-500 text-gray-400 hover:text-blue-400 rounded text-xs font-mono transition-all hover:bg-blue-500/10"
                                                        >
                                                            <Pencil size={10} />
                                                            Sửa
                                                        </Link>
                                                        <button
                                                            onClick={() => handleDelete(chapter.chapter_number)}
                                                            disabled={deletingId === chapter.chapter_number}
                                                            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-1.5 border border-gray-700 hover:border-red-600 text-gray-500 hover:text-red-400 disabled:opacity-50 rounded text-xs font-mono transition-all hover:bg-red-500/10"
                                                        >
                                                            <Trash2 size={10} />
                                                            {deletingId === chapter.chapter_number ? '...' : 'Xóa'}
                                                        </button>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr className="flex flex-col md:table-row">
                                        <td colSpan={4} className="px-4 py-10 text-center text-gray-600 font-mono text-xs">
                                            {searchQuery ? `Không tìm thấy chương nào khớp với "${searchQuery}"` : 'Không có dữ liệu chương'}
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>

                    {!searchQuery && totalPages > 1 && (
                        <div className="flex items-center justify-center gap-4 mt-8">
                            <button
                                onClick={() => fetchChapters(currentPage - 1)}
                                disabled={currentPage === 1 || loading}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-700 text-gray-400 hover:text-gray-100 disabled:opacity-30 disabled:hover:text-gray-400 rounded-md font-mono text-xs transition-all active:scale-95"
                            >
                                <ChevronLeft size={16} />
                                TRƯỚC
                            </button>

                            <div className="flex items-center gap-2">
                                {Array.from({ length: Math.min(5, totalPages) }).map((_, index) => {
                                    let pageNum = index + 1;
                                    if (totalPages > 5) {
                                        if (currentPage > 3) pageNum = currentPage - 3 + index;
                                        if (pageNum > totalPages) pageNum = totalPages - 4 + index;
                                        if (pageNum < 1) pageNum = index + 1;
                                    }
                                    if (pageNum > totalPages) return null;
                                    return (
                                        <button
                                            key={pageNum}
                                            onClick={() => fetchChapters(pageNum)}
                                            className={`w-8 h-8 flex items-center justify-center rounded font-mono text-xs transition-colors ${currentPage === pageNum ? 'bg-green-600 text-white' : 'text-gray-500 hover:bg-gray-800 hover:text-gray-200'}`}
                                        >
                                            {pageNum}
                                        </button>
                                    );
                                })}
                            </div>

                            <button
                                onClick={() => fetchChapters(currentPage + 1)}
                                disabled={currentPage === totalPages || loading}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-700 text-gray-400 hover:text-gray-100 disabled:opacity-30 disabled:hover:text-gray-400 rounded-md font-mono text-xs transition-all active:scale-95"
                            >
                                TIẾP
                                <ChevronRight size={16} />
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
