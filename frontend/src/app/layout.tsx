import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/react";

import "./globals.css";

import FirstVisitOnboarding from "@/components/FirstVisitOnboarding";
import { LocaleProvider } from "@/context/LocaleContext";
import { NovelProvider } from "@/context/NovelContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { getNovelSettings } from "@/lib/api";
import { LOCALE_LANG, SUPPORTED_LOCALES, withLocalePath } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/dictionaries";
import { getCurrentCanonicalPath, getCurrentLocale, getUnlocalizedPath } from "@/lib/i18n/server";

const SITE_URL = "https://matthesinhhoa.vercel.app";

export async function generateMetadata(): Promise<Metadata> {
    const locale = await getCurrentLocale();
    const dictionary = getDictionary(locale);
    const currentPath = await getCurrentCanonicalPath();
    const unlocalizedPath = await getUnlocalizedPath();

    try {
        const novel = await getNovelSettings(locale);
        return {
            metadataBase: new URL(SITE_URL),
            title: {
                default: novel.title,
                template: `%s | ${novel.title}`,
            },
            description: novel.description,
            keywords: novel.genres.concat(["mat the", "zombie", dictionary.common.chapters]),
            alternates: {
                canonical: currentPath,
                languages: Object.fromEntries(
                    SUPPORTED_LOCALES.map((item) => [LOCALE_LANG[item], withLocalePath(item, unlocalizedPath)]),
                ),
            },
            openGraph: {
                title: novel.title,
                description: novel.description,
                url: currentPath,
                type: "website",
                siteName: novel.title,
                locale: LOCALE_LANG[locale],
            },
        };
    } catch {
        return {
            metadataBase: new URL(SITE_URL),
            title: {
                default: "Mat The",
                template: "%s | Mat The",
            },
            description: "Biochemical apocalypse novel.",
            alternates: {
                canonical: currentPath,
                languages: Object.fromEntries(
                    SUPPORTED_LOCALES.map((item) => [LOCALE_LANG[item], withLocalePath(item, unlocalizedPath)]),
                ),
            },
        };
    }
}

export default async function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const locale = await getCurrentLocale();

    return (
        <html lang={locale} suppressHydrationWarning>
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                <link rel="manifest" href="/manifest.json" />
                <meta name="theme-color" content="#161616" />
                <meta name="apple-mobile-web-app-capable" content="yes" />
                <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
                {SUPPORTED_LOCALES.map((item) => (
                    <link key={item} rel="alternate" hrefLang={LOCALE_LANG[item]} href={`${SITE_URL}/${item}`} />
                ))}
                <script
                    dangerouslySetInnerHTML={{
                        __html: `
                        if ('serviceWorker' in navigator) {
                            window.addEventListener('load', function() {
                                navigator.serviceWorker.register('/sw.js').catch(function(err) {
                                    console.log('SW fail', err);
                                });
                            });
                        }
                        `,
                    }}
                />
            </head>
            <body className="bg-ash-dark min-h-screen antialiased" suppressHydrationWarning>
                <ThemeProvider>
                    <LocaleProvider locale={locale}>
                        <NovelProvider>
                            <FirstVisitOnboarding />
                            {children}
                        </NovelProvider>
                    </LocaleProvider>
                </ThemeProvider>
                <Analytics />
            </body>
        </html>
    );
}
