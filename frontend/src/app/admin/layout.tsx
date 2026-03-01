import type { Metadata } from 'next';
import '../globals.css';

export const metadata: Metadata = {
    title: 'Admin | Mạt Thế',
    description: 'Trang quản trị nội bộ - Cấm truy cập trái phép.',
    robots: 'noindex, nofollow',
};

// Admin layout is isolated — no Header, Footer, or PWA prompt
export default function AdminLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-[#0a0a0a] text-gray-200 antialiased">
            {children}
        </div>
    );
}
