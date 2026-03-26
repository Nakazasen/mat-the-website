"use client";

import { Languages } from "lucide-react";

import { useLocale } from "@/context/LocaleContext";
import { LOCALE_LABELS, SUPPORTED_LOCALES, type Locale } from "@/lib/i18n/config";

export default function LanguageSwitcher({ mobile = false }: { mobile?: boolean }) {
    const { locale, setLocale, dictionary } = useLocale();

    return (
        <div
            className={`flex items-center gap-1 rounded-full border border-ash-800/80 bg-ash-950/70 ${
                mobile ? "px-2 py-2" : "px-2 py-1.5"
            }`}
            aria-label={dictionary.common.language}
        >
            <Languages size={mobile ? 16 : 14} className="text-toxic-green-DEFAULT" />
            {SUPPORTED_LOCALES.map((item) => (
                <button
                    key={item}
                    type="button"
                    onClick={() => setLocale(item as Locale)}
                    className={`rounded-full px-2 py-1 text-[10px] font-mono tracking-widest transition-all ${
                        item === locale
                            ? "border border-toxic-green-bright/60 bg-toxic-green-DEFAULT/20 text-toxic-green-bright"
                            : "text-ash-400 hover:text-toxic-green-DEFAULT"
                    }`}
                >
                    {LOCALE_LABELS[item]}
                </button>
            ))}
        </div>
    );
}
