import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
    title: {
        default: "Mạt Thế - Sinh Hoá Nguy Cơ ☣️",
        template: "%s | Mạt Thế - Sinh Hoá Nguy Cơ",
    },
    description:
        "Đọc truyện Mạt Thế - Sinh Hoá Nguy Cơ full 813+ chương. Thế giới tàn lụi, zombie, dị biến sinh học. Hàn Phong - Thủ lĩnh trấn Hi Vọng.",
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
        <html lang="vi" className="dark">
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link
                    rel="preconnect"
                    href="https://fonts.gstatic.com"
                    crossOrigin="anonymous"
                />
            </head>
            <body className="bg-ash-dark min-h-screen antialiased">
                <Header />
                <main>{children}</main>
                <Footer />
            </body>
        </html>
    );
}
