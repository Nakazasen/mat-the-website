"use client";

import React from "react";
import { createContext, useContext, useMemo } from "react";
import { usePathname, useRouter } from "next/navigation";

import { getDictionary, type Dictionary } from "@/lib/i18n/dictionaries";
import {
    LOCALE_COOKIE,
    type Locale,
    replaceLocaleInPath,
} from "@/lib/i18n/config";

interface LocaleContextValue {
    locale: Locale;
    dictionary: Dictionary;
    setLocale: (nextLocale: Locale) => void;
    localizePath: (href: string) => string;
}

const LocaleContext = createContext<LocaleContextValue | undefined>(undefined);

export function LocaleProvider({
    locale,
    children,
}: {
    locale: Locale;
    children: React.ReactNode;
}) {
    const router = useRouter();
    const pathname = usePathname();

    const value = useMemo<LocaleContextValue>(() => {
        const dictionary = getDictionary(locale);

        return {
            locale,
            dictionary,
            setLocale: (nextLocale: Locale) => {
                document.cookie = `${LOCALE_COOKIE}=${nextLocale}; path=/; max-age=31536000; samesite=lax`;
                router.push(replaceLocaleInPath(pathname || "/", nextLocale));
            },
            localizePath: (href: string) => {
                if (!href.startsWith("/")) return href;
                return replaceLocaleInPath(href, locale);
            },
        };
    }, [locale, pathname, router]);

    return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
    const context = useContext(LocaleContext);
    if (!context) {
        throw new Error("useLocale must be used within LocaleProvider");
    }
    return context;
}
