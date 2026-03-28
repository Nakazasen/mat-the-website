"use client";

import { createAdminClient } from "@/lib/supabase-admin";
import type { Locale } from "@/lib/i18n/config";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
const READER_API_BASE = `${API_BASE_URL}/api/reader`;

export type ReaderLookupSource = "cache" | "rule_based" | "ai" | "placeholder";

export interface ReaderExternalLink {
    label: string;
    url: string;
}

export interface ReaderLookupRequest {
    locale: Locale;
    term: string;
    context_sentence?: string;
    chapter_id?: number;
}

export interface ReaderLookupResponse {
    term: string;
    normalized_term: string;
    locale: Locale;
    reading?: string | null;
    meaning_vi?: string | null;
    pos?: string | null;
    notes?: string | null;
    source: ReaderLookupSource;
    external_links: ReaderExternalLink[];
}

export interface ReaderSentenceInsightRequest {
    locale: Locale;
    sentence_text: string;
    chapter_id?: number;
}

export interface ReaderSentenceInsightResponse {
    sentence_text: string;
    locale: Locale;
    meaning_vi?: string | null;
    notes?: string | null;
    source: ReaderLookupSource;
}

export type ReaderGrammarHintCategory =
    | "grammar"
    | "structure"
    | "idiom"
    | "phrasal_verb"
    | "collocation"
    | "conjugation"
    | "aspect"
    | "tone";

export interface ReaderGrammarHint {
    title: string;
    explanation_vi: string;
    example_fragment?: string | null;
    category: ReaderGrammarHintCategory;
}

export interface ReaderGrammarHintsRequest {
    locale: Locale;
    sentence_text: string;
    chapter_id?: number;
}

export interface ReaderGrammarHintsResponse {
    sentence_text: string;
    locale: Locale;
    hints: ReaderGrammarHint[];
    source: ReaderLookupSource;
}

export interface ReaderSaveVocabRequest {
    locale: Locale;
    term: string;
    normalized_term?: string;
    reading?: string;
    meaning_vi?: string;
    pos?: string;
    notes?: string;
    context_sentence?: string;
    chapter_id?: number;
    source?: string;
}

export interface ReaderSavedVocabItem {
    id: string;
    user_id: string;
    locale: Locale;
    term: string;
    normalized_term: string;
    reading?: string | null;
    meaning_vi?: string | null;
    pos?: string | null;
    notes?: string | null;
    context_sentence?: string | null;
    chapter_id?: number | null;
    source: string;
    created_at: string;
    updated_at: string;
    review_count?: number;
    next_review_at?: string | null;
    interval_days?: number;
    ease?: number;
    due_for_review?: boolean;
}

export interface ReaderSavedVocabListResponse {
    items: ReaderSavedVocabItem[];
    total: number;
    page: number;
    limit: number;
}

export interface ReaderSaveSentenceRequest {
    locale: Locale;
    sentence_text: string;
    meaning_vi?: string;
    note?: string;
    chapter_id?: number;
}

export interface ReaderSavedSentenceItem {
    id: string;
    user_id: string;
    locale: Locale;
    sentence_text: string;
    meaning_vi?: string | null;
    note?: string | null;
    chapter_id?: number | null;
    created_at: string;
}

export interface ReaderSavedSentenceListResponse {
    items: ReaderSavedSentenceItem[];
    total: number;
    page: number;
    limit: number;
}

export interface ReaderReviewRequest {
    saved_vocab_id: string;
    grade: number;
}

export interface ReaderReviewResponse {
    saved_vocab_id: string;
    ease: number;
    interval_days: number;
    next_review_at?: string | null;
    review_count: number;
}

export interface ReaderSentenceTtsRequest {
    locale: Locale;
    sentence_text: string;
    speed?: number;
    chapter_id?: number;
    voice?: string;
}

export interface ReaderSentenceTtsResponse {
    status: string;
    detail: string;
    audio_url?: string | null;
    provider?: string | null;
    cached?: boolean;
}

export interface ReaderLearningStatsResponse {
    saved_vocab_count: number;
    saved_sentence_count: number;
    review_due_count: number;
}

async function getReaderAccessToken(): Promise<string | null> {
    const supabase = createAdminClient();
    if (!supabase) return null;
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
}

async function readResponseJson<T>(response: Response): Promise<T> {
    const text = await response.text();
    return (text ? JSON.parse(text) : {}) as T;
}

async function readerRequest<T>(path: string, init: RequestInit = {}, requireAuth = false): Promise<T> {
    const headers = new Headers(init.headers || {});
    headers.set("Content-Type", "application/json");

    if (requireAuth) {
        const token = await getReaderAccessToken();
        if (!token) {
            throw new Error("Bạn cần đăng nhập để dùng tính năng học tập.");
        }
        headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`${READER_API_BASE}${path}`, {
        ...init,
        headers,
        cache: "no-store",
    });
    const payload = await readResponseJson<T & { detail?: string }>(response);
    if (!response.ok) {
        throw new Error(payload.detail || "Yêu cầu học tập thất bại.");
    }
    return payload;
}

export function lookupReaderTerm(data: ReaderLookupRequest): Promise<ReaderLookupResponse> {
    return readerRequest<ReaderLookupResponse>("/lookup", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export function getReaderSentenceInsight(data: ReaderSentenceInsightRequest): Promise<ReaderSentenceInsightResponse> {
    return readerRequest<ReaderSentenceInsightResponse>("/sentence-insight", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export function getReaderGrammarHints(data: ReaderGrammarHintsRequest): Promise<ReaderGrammarHintsResponse> {
    return readerRequest<ReaderGrammarHintsResponse>("/grammar-hints", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export function saveReaderVocab(data: ReaderSaveVocabRequest): Promise<ReaderSavedVocabItem> {
    return readerRequest<ReaderSavedVocabItem>(
        "/save-vocab",
        {
            method: "POST",
            body: JSON.stringify(data),
        },
        true,
    );
}

export function getSavedReaderVocab(params: {
    locale?: Locale;
    page?: number;
    limit?: number;
} = {}): Promise<ReaderSavedVocabListResponse> {
    const search = new URLSearchParams();
    if (params.locale) search.set("locale", params.locale);
    if (params.page) search.set("page", String(params.page));
    if (params.limit) search.set("limit", String(params.limit));
    return readerRequest<ReaderSavedVocabListResponse>(
        `/saved-vocab${search.toString() ? `?${search.toString()}` : ""}`,
        undefined,
        true,
    );
}

export function saveReaderSentence(data: ReaderSaveSentenceRequest): Promise<ReaderSavedSentenceItem> {
    return readerRequest<ReaderSavedSentenceItem>(
        "/save-sentence",
        {
            method: "POST",
            body: JSON.stringify(data),
        },
        true,
    );
}

export function getSavedReaderSentences(params: {
    locale?: Locale;
    page?: number;
    limit?: number;
} = {}): Promise<ReaderSavedSentenceListResponse> {
    const search = new URLSearchParams();
    if (params.locale) search.set("locale", params.locale);
    if (params.page) search.set("page", String(params.page));
    if (params.limit) search.set("limit", String(params.limit));
    return readerRequest<ReaderSavedSentenceListResponse>(
        `/saved-sentences${search.toString() ? `?${search.toString()}` : ""}`,
        undefined,
        true,
    );
}

export function reviewSavedReaderVocab(data: ReaderReviewRequest): Promise<ReaderReviewResponse> {
    return readerRequest<ReaderReviewResponse>(
        "/review-vocab",
        {
            method: "POST",
            body: JSON.stringify(data),
        },
        true,
    );
}

export function requestReaderSentenceTts(data: ReaderSentenceTtsRequest): Promise<ReaderSentenceTtsResponse> {
    return readerRequest<ReaderSentenceTtsResponse>("/sentence-tts", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export function getReaderLearningStats(): Promise<ReaderLearningStatsResponse> {
    return readerRequest<ReaderLearningStatsResponse>("/learning-stats", undefined, true);
}
