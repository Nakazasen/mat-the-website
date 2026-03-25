'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { BookOpen, Settings, LogOut, BarChart3, Home, LibraryBig, Users, Map as MapIcon, FileText, Menu, X, MessageSquare } from 'lucide-react';
import { createAdminClient } from '@/lib/supabase-admin';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const navItems = [
    { href: '/admin', label: 'Dashboard', icon: BarChart3, exact: true },
    { href: '/admin/homepage', label: 'Trang Chủ', icon: Home },
    { href: '/admin/chapters', label: 'Chương Truyện', icon: BookOpen },
    { href: '/admin/novel', label: 'Thông Tin Truyện', icon: Settings },
    { href: '/admin/comments', label: 'Bình Luận', icon: MessageSquare },
    { href: '/admin/wiki', label: 'Wiki / Bách Khoa', icon: LibraryBig },
    { href: '/admin/personnel', label: 'Nhân Sự', icon: Users, superadminOnly: true },
    { href: '/admin/map', label: 'Bản Đồ', icon: MapIcon },
    { href: '/admin/guide', label: 'Hướng Dẫn & SOP', icon: FileText },
];

export default function AdminNav() {
    const pathname = usePathname();
    const router = useRouter();
    const [userRole, setUserRole] = useState<string>('editor');
    const [isMobileOpen, setIsMobileOpen] = useState(false);

    // Close mobile nav on route change
    useEffect(() => {
        setIsMobileOpen(false);
    }, [pathname]);

    useEffect(() => {
        const fetchRole = async () => {
            const supabase = createAdminClient();
            if (!supabase) return;
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;

            try {
                const res = await fetch(`${API_BASE_URL}/api/admin/users`, {
                    headers: { 'Authorization': `Bearer ${session.access_token}` }
                });
                if (res.ok) {
                    // If user can list users, they are superadmin
                    setUserRole('superadmin');
                }
            } catch {
                // Not superadmin, keep default
            }
        };
        fetchRole();
    }, []);

    const handleLogout = async () => {
        const supabase = createAdminClient();
        if (!supabase) {
            console.error('Lỗi cấu hình: Không thể tạo Supabase client.');
            router.push('/admin/login');
            router.refresh();
            return;
        }
        await supabase.auth.signOut();
        router.push('/admin/login');
        router.refresh();
    };

    const visibleItems = navItems.filter(item =>
        !item.superadminOnly || userRole === 'superadmin'
    );

    return (
        <>
            {/* Mobile Header */}
            <div className="md:hidden flex items-center justify-between bg-[#0d0d0d] border-b border-gray-800 p-4 sticky top-0 z-40">
                <div className="flex items-center gap-2">
                    <span className="text-xl">☣</span>
                    <div>
                        <div className="font-mono text-xs text-green-400 tracking-widest">ADMIN</div>
                        <div className="font-mono text-[9px] text-gray-600 tracking-wider">MẠT THẾ CP</div>
                    </div>
                </div>
                <button
                    onClick={() => setIsMobileOpen(!isMobileOpen)}
                    className="text-gray-300 p-2 focus:outline-none"
                    aria-label="Toggle menu"
                >
                    {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Mobile Backdrop */}
            {isMobileOpen && (
                <div
                    className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-sm"
                    onClick={() => setIsMobileOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={`fixed md:sticky top-0 left-0 z-50 md:z-10 h-screen md:h-auto overflow-y-auto w-64 md:w-56 shrink-0 flex flex-col bg-[#0d0d0d] border-r border-gray-800 min-h-screen transition-transform duration-300 ease-in-out ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
                {/* Logo */}
                <div className="hidden md:block px-5 py-5 border-b border-gray-800">
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
                    {visibleItems.map(({ href, label, icon: Icon, exact }) => {
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
                <div className="p-3 border-t border-gray-800 space-y-1 mt-auto">
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
        </>
    );
}
