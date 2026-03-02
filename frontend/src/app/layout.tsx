import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { ThemeProvider } from "@/context/ThemeContext";
import PWAInstallPrompt from "@/components/PWAInstallPrompt";
import { Analytics } from "@vercel/analytics/react";

export const metadata: Metadata = {
    title: {
        default: "Mạt Thế - Sinh Hoá Nguy Cơ ☣️",
        template: "%s | Mạt Thế - Sinh Hoá Nguy Cơ",
    },
    description:
        "Đọc truyện Mạt Thế - Sinh Hoá Nguy Cơ full 813+ chương. Thế giới tàn lụi, zombie, dị biến sinh học. Tác giả: Hàn Nhược Tuyết.",
    keywords: [
        "mạt thế sinh hoá nguy cơ",
        "đọc truyện zombie",
        "truyện tiên hiệp",
        "hàn phong",
        "truyện mạt thế",
        "đọc truyện online",
    ],
    openGraph: {
        title: "Mạt Thế - Sinh Hoá Nguy Cơ ☣️",
        description: "Đọc truyện mạt thế zombie dị biến sinh học online miễn phí",
        type: "website",
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="vi" suppressHydrationWarning>
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link
                    rel="preconnect"
                    href="https://fonts.gstatic.com"
                    crossOrigin="anonymous"
                />
                <link rel="manifest" href="/manifest.json" />
                <meta name="theme-color" content="#161616" />
                <meta name="apple-mobile-web-app-capable" content="yes" />
                <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
                <script
                    dangerouslySetInnerHTML={{
                        __html: `
                        if ('serviceWorker' in navigator) {
                            window.addEventListener('load', function() {
                                navigator.serviceWorker.register('/sw.js').then(
                                    function(registration) { console.log('SW success'); },
                                    function(err) { console.log('SW fail', err); }
                                );
                            });
                        }
                        `,
                    }}
                />
            </head>
            <body className="bg-ash-dark min-h-screen antialiased" suppressHydrationWarning>
                <ThemeProvider>
                    {children}
                </ThemeProvider>
                <Analytics />
            </body>
        </html>
    );
}
