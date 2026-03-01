'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { BookOpen, Settings, LogOut, BarChart3, Home, LibraryBig, Users } from 'lucide-react';
import { createAdminClient } from '@/lib/supabase-admin';

const navItems = [
    { href: '/admin', label: 'Dashboard', icon: BarChart3, exact: true },
    { href: '/admin/homepage', label: 'Trang Chủ', icon: Home },
    { href: '/admin/chapters', label: 'Chương Truyện', icon: BookOpen },
    { href: '/admin/novel', label: 'Thông Tin Truyện', icon: Settings },
    { href: '/admin/wiki', label: 'Wiki / Bách Khoa', icon: LibraryBig },
    { href: '/admin/personnel', label: 'Nhân Sự', icon: Users },
];

export default function AdminNav() {
    const pathname = usePathname();
    const router = useRouter();

    const handleLogout = async () => {
        const supabase = createAdminClient();
        if (!supabase) {
            // This component does not have setError or setLoading.
            // The provided snippet seems to be for a login page.
            // For logout, if supabase client cannot be created, we can't log out.
            // We'll proceed with the existing logic, assuming createAdminClient
            // handles its own errors or returns null if misconfigured.
            console.error('Lỗi cấu hình: Không thể tạo Supabase client.');
            router.push('/admin/login'); // Still redirect to login as we can't confirm logout
            router.refresh();
            return;
        }
        await supabase.auth.signOut();
        router.push('/admin/login');
        router.refresh();
    };

    return (
        <aside className="w-56 shrink-0 flex flex-col bg-[#0d0d0d] border-r border-gray-800 min-h-screen">
            {/* Logo */}
            <div className="px-5 py-5 border-b border-gray-800">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">☣</span>
                    <div>
                        <div className="font-mono text-xs text-green-400 tracking-widest">ADMIN</div>
                        <div className="font-mono text-[9px] text-gray-600 tracking-wider">MẠT THẾ CP</div>
                    </div>
                </div>
            </div>

            {/* Nav */}
            <nav className="flex-1 p-3 space-y-1">
                {navItems.map(({ href, label, icon: Icon, exact }) => {
                    const isActive = exact ? pathname === href : pathname.startsWith(href);
                    return (
                        <Link
                            key={href}
                            href={href}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded text-sm font-mono transition-all ${isActive
                                ? 'bg-green-900/30 text-green-400 border border-green-800/40'
                                : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/50'
                                }`}
                        >
                            <Icon size={14} />
                            {label}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer nav */}
            <div className="p-3 border-t border-gray-800 space-y-1">
                <Link
                    href="/"
                    target="_blank"
                    className="flex items-center gap-3 px-3 py-2 rounded text-xs font-mono text-gray-600 hover:text-gray-300 transition-colors"
                >
                    <Home size={12} />
                    Xem Web
                </Link>
                <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded text-xs font-mono text-gray-600 hover:text-red-400 transition-colors"
                >
                    <LogOut size={12} />
                    Đăng Xuất
                </button>
            </div>
        </aside>
    );
}
