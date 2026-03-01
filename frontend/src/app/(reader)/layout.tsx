import Header from "@/components/Header";
import Footer from "@/components/Footer";
import PWAInstallPrompt from "@/components/PWAInstallPrompt";
import { getNovelSettings } from "@/lib/api";

export default async function ReaderLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    let novel;
    try {
        novel = await getNovelSettings();
    } catch {
        // Fallback or leave as undefined
    }

    return (
        <>
            <Header />
            <main>{children}</main>
            <Footer novel={novel} />
            <PWAInstallPrompt />
        </>
    );
}
