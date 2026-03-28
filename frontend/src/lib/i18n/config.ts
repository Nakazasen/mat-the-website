export const SUPPORTED_LOCALES = ["vi", "en", "zh-CN", "ja"] as const;

export type Locale = (typeof SUPPORTED_LOCALES)[number];

export const DEFAULT_LOCALE: Locale = "vi";
export const LOCALE_COOKIE = "mt_locale";

export const LOCALE_LABELS: Record<Locale, string> = {
    vi: "VI",
    en: "EN",
    "zh-CN": "中文",
    ja: "日本語",
};

export const LOCALE_LANG: Record<Locale, string> = {
    vi: "vi-VN",
    en: "en-US",
    "zh-CN": "zh-CN",
    ja: "ja-JP",
};

export function isSupportedLocale(value: string | null | undefined): value is Locale {
    return Boolean(value && SUPPORTED_LOCALES.includes(value as Locale));
}

export function normalizeLocale(value: string | null | undefined): Locale {
    if (!value) return DEFAULT_LOCALE;
    if (isSupportedLocale(value)) return value;

    const lowered = value.toLowerCase();
    if (lowered.startsWith("vi")) return "vi";
    if (lowered.startsWith("en")) return "en";
    if (lowered.startsWith("zh")) return "zh-CN";
    if (lowered.startsWith("ja")) return "ja";
    return DEFAULT_LOCALE;
}

export function getLocaleFromPath(pathname: string): Locale | null {
    const [, segment] = pathname.split("/");
    return isSupportedLocale(segment) ? segment : null;
}

export function stripLocaleFromPath(pathname: string): string {
    const locale = getLocaleFromPath(pathname);
    if (!locale) return pathname || "/";
    const stripped = pathname.slice(locale.length + 1);
    return stripped || "/";
}

export function withLocalePath(locale: Locale, href: string): string {
    if (!href.startsWith("/")) return href;
    const normalized = stripLocaleFromPath(href);
    return normalized === "/" ? `/${locale}` : `/${locale}${normalized}`;
}

export function replaceLocaleInPath(pathname: string, locale: Locale): string {
    return withLocalePath(locale, pathname || "/");
}
