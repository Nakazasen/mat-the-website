"use client";

import { Globe2, Languages, Sparkles, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";

import { useLocale } from "@/context/LocaleContext";
import { LOCALE_LABELS, SUPPORTED_LOCALES, type Locale } from "@/lib/i18n/config";

const STORAGE_KEY = "site-first-visit-onboarding-v1";

const localeSubLabels: Record<Locale, string> = {
    vi: "Tiếng Việt",
    en: "English",
    "zh-CN": "简体中文",
    ja: "日本語",
};

const onboardingCopy: Record<
    Locale,
    {
        title: string;
        subtitle: string;
        chooseLanguage: string;
        stepsTitle: string;
        stepLabel: string;
        steps: string[];
        continueLabel: string;
        skipLabel: string;
    }
> = {
    vi: {
        title: "Chọn ngôn ngữ và làm quen nhanh",
        subtitle: "Lần đầu vào web, anh có thể chọn ngôn ngữ đọc và xem nhanh cách dùng các tính năng chính.",
        chooseLanguage: "Ngôn ngữ hiển thị",
        stepsTitle: "Dùng web như sau",
        stepLabel: "Bước",
        steps: [
            "Dùng nút đổi ngôn ngữ để chuyển giữa Việt, Anh, Trung và Nhật.",
            "Trong trang đọc, bôi đen hoặc click đúp vào từ ngắn để tra nhanh ngay trong trang.",
            "Bật audio nếu muốn nghe truyện, và dùng panel Learning để lưu từ hoặc câu.",
        ],
        continueLabel: "Đã hiểu, bắt đầu đọc",
        skipLabel: "Để sau",
    },
    en: {
        title: "Pick your language and get oriented",
        subtitle: "On your first visit, choose the reading language and review the core features in a few seconds.",
        chooseLanguage: "Display language",
        stepsTitle: "How to use the site",
        stepLabel: "Step",
        steps: [
            "Use the language switcher to move between Vietnamese, English, Chinese, and Japanese.",
            "Inside the reader, highlight text or double-click a short word for an in-page lookup.",
            "Use audio for listening practice, and use the Learning panel to save words or sentences.",
        ],
        continueLabel: "Got it, start reading",
        skipLabel: "Maybe later",
    },
    "zh-CN": {
        title: "先选择语言，再快速了解网站",
        subtitle: "第一次进入网站时，你可以先选择阅读语言，再快速看看主要功能怎么用。",
        chooseLanguage: "显示语言",
        stepsTitle: "网站使用方式",
        stepLabel: "步骤",
        steps: [
            "使用语言切换按钮，在越南语、英语、中文和日语之间切换。",
            "在阅读页面中，选中文本或双击较短的词，就能直接在页面内快速查词。",
            "如果想边听边读，可以开启音频，并使用 Learning 面板保存单词或句子。",
        ],
        continueLabel: "知道了，开始阅读",
        skipLabel: "稍后再说",
    },
    ja: {
        title: "言語を選んで、使い方をすぐ確認",
        subtitle: "初回アクセス時に、表示言語を選び、主要機能の使い方をすばやく確認できます。",
        chooseLanguage: "表示言語",
        stepsTitle: "使い方ガイド",
        stepLabel: "手順",
        steps: [
            "言語切替ボタンで、ベトナム語・英語・中国語・日本語を切り替えられます。",
            "読書ページでは、語句を選択するか短い単語をダブルクリックすると、その場ですぐ調べられます。",
            "音声を再生して聞きながら読み進めたり、Learning パネルで単語や文を保存したりできます。",
        ],
        continueLabel: "理解しました。読み始める",
        skipLabel: "あとで",
    },
};

export default function FirstVisitOnboarding() {
    const pathname = usePathname();
    const { locale, setLocale } = useLocale();
    const [open, setOpen] = useState(false);

    useEffect(() => {
        if (!pathname || pathname.startsWith("/admin")) return;
        try {
            const seen = window.localStorage.getItem(STORAGE_KEY);
            if (!seen) {
                setOpen(true);
            }
        } catch {
            setOpen(true);
        }
    }, [pathname]);

    const copy = useMemo(() => onboardingCopy[locale] ?? onboardingCopy.vi, [locale]);

    const close = () => {
        setOpen(false);
        try {
            window.localStorage.setItem(STORAGE_KEY, "seen");
        } catch {
            // Ignore storage failures.
        }
    };

    if (!open || !pathname || pathname.startsWith("/admin")) {
        return null;
    }

    return (
        <div className="fixed inset-0 z-[90] flex items-end justify-center bg-black/70 backdrop-blur-sm sm:items-center sm:p-4">
            <div className="flex max-h-[92dvh] w-full max-w-2xl flex-col overflow-hidden rounded-t-[28px] border border-b-0 border-toxic-green-DEFAULT/20 bg-ash-950/95 shadow-[0_25px_80px_rgba(0,0,0,0.55)] sm:max-h-[calc(100dvh-2rem)] sm:rounded-3xl sm:border-b">
                <div className="mx-auto mt-3 h-1.5 w-14 rounded-full bg-ash-700/80 sm:hidden" />

                <div className="flex items-start justify-between border-b border-ash-800/80 px-5 py-5 sm:px-7">
                    <div className="min-w-0">
                        <div className="flex items-center gap-2 text-toxic-green-DEFAULT">
                            <Globe2 size={16} />
                            <span className="text-[11px] font-mono uppercase tracking-[0.28em]">Welcome</span>
                        </div>
                        <h2 className="mt-3 text-xl font-semibold text-white sm:text-2xl">{copy.title}</h2>
                        <p className="mt-2 max-w-xl text-sm leading-6 text-ash-300">{copy.subtitle}</p>
                    </div>
                    <button
                        type="button"
                        onClick={close}
                        className="rounded-full border border-ash-800/80 p-2 text-ash-400 hover:border-toxic-green-DEFAULT/40 hover:text-toxic-green-DEFAULT"
                        aria-label="Close onboarding"
                    >
                        <X size={16} />
                    </button>
                </div>

                <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
                    <div className="grid gap-0 md:grid-cols-[0.95fr_1.05fr]">
                        <div className="border-b border-ash-800/70 p-5 md:border-b-0 md:border-r md:p-7">
                            <div className="flex items-center gap-2 text-toxic-green-DEFAULT">
                                <Languages size={15} />
                                <span className="text-[11px] font-mono uppercase tracking-[0.24em]">{copy.chooseLanguage}</span>
                            </div>
                            <div className="mt-4 grid grid-cols-2 gap-3">
                                {SUPPORTED_LOCALES.map((item) => (
                                    <button
                                        key={item}
                                        type="button"
                                        onClick={() => setLocale(item)}
                                        className={`rounded-2xl border px-4 py-3 text-left transition-all ${
                                            item === locale
                                                ? "border-toxic-green-bright/50 bg-toxic-green-DEFAULT/10 text-toxic-green-bright"
                                                : "border-ash-800/80 bg-ash-900/50 text-ash-300 hover:border-toxic-green-DEFAULT/30 hover:text-white"
                                        }`}
                                    >
                                        <div className="text-sm font-semibold">{LOCALE_LABELS[item]}</div>
                                        <div className="mt-1 text-xs text-ash-500">{localeSubLabels[item]}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="p-5 md:p-7">
                            <div className="flex items-center gap-2 text-toxic-green-DEFAULT">
                                <Sparkles size={15} />
                                <span className="text-[11px] font-mono uppercase tracking-[0.24em]">{copy.stepsTitle}</span>
                            </div>
                            <div className="mt-4 space-y-3">
                                {copy.steps.map((step, index) => (
                                    <div key={step} className="rounded-2xl border border-ash-800/70 bg-ash-900/45 px-4 py-3">
                                        <div className="text-[10px] font-mono uppercase tracking-[0.24em] text-ash-500">
                                            {copy.stepLabel} {index + 1}
                                        </div>
                                        <div className="mt-2 text-sm leading-6 text-ash-200">{step}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="sticky bottom-0 border-t border-ash-800/80 bg-ash-950/98 px-5 py-4 sm:px-7">
                    <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                        <button
                            type="button"
                            onClick={close}
                            className="w-full rounded-full bg-toxic-green-DEFAULT px-5 py-3 text-sm font-medium text-black transition hover:bg-toxic-green-bright sm:w-auto"
                        >
                            {copy.continueLabel}
                        </button>
                        <button
                            type="button"
                            onClick={close}
                            className="w-full rounded-full border border-ash-700 px-5 py-3 text-sm text-ash-300 transition hover:border-toxic-green-DEFAULT/40 hover:text-white sm:w-auto"
                        >
                            {copy.skipLabel}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
