"use client";
import Link from "next/link";
import { useState, useEffect } from "react";
import { BookOpen, List, Home, Menu, X, Zap } from "lucide-react";
import ThemeSwitcher from "./ThemeSwitcher";

export default function Header() {
    const [scrolled, setScrolled] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 40);
        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const navLinks = [
        { href: "/", label: "TRANG CHỦ", icon: Home },
        { href: "/chapters", label: "MỤC LỤC", icon: List },
        { href: "/wiki", label: "BÁCH KHOA", icon: BookOpen },
        { href: "/chapters/1", label: "ĐỌC NGAY", icon: BookOpen, highlight: true },
    ];

    return (
        <>
            <header
                className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled
                    ? "bg-ash-950/95 backdrop-blur-md border-b border-toxic-green-DEFAULT/20 shadow-lg shadow-black/50"
                    : "bg-transparent"
                    }`}
            >
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="flex items-center justify-between h-16 md:h-18">
                        {/* Logo */}
                        <Link href="/" className="flex items-center gap-3 group">
                            <div className="relative">
                                <span className="text-3xl animate-flicker">☣</span>
                                <span className="absolute -inset-1 rounded-full bg-toxic-green-DEFAULT/10 blur-sm group-hover:bg-toxic-green-DEFAULT/20 transition-all" />
                            </div>
                            <div className="hidden sm:block">
                                <div className="font-biohazard text-xl leading-none text-toxic-green-DEFAULT tracking-widest">
                                    MẠT THẾ
                                </div>
                                <div className="font-mono text-[9px] text-ash-400 tracking-[0.3em] uppercase">
                                    SINH HOÁ NGUY CƠ
                                </div>
                            </div>
                        </Link>

                        {/* Desktop Nav */}
                        <nav className="hidden md:flex items-center gap-1">
                            {navLinks.map(({ href, label, icon: Icon, highlight }) =>
                                highlight ? (
                                    <Link
                                        key={href}
                                        href={href}
                                        className="btn-blood ml-4 flex items-center gap-2 text-sm"
                                    >
                                        <Icon size={14} />
                                        <span>{label}</span>
                                    </Link>
                                ) : (
                                    <Link
                                        key={href}
                                        href={href}
                                        className="flex items-center gap-2 px-4 py-2 text-sm font-biohazard tracking-widest text-ash-300 hover:text-toxic-green-DEFAULT transition-colors relative group"
                                    >
                                        <Icon size={13} />
                                        {label}
                                        <span className="absolute bottom-0 left-0 w-0 h-px bg-toxic-green-DEFAULT group-hover:w-full transition-all duration-300" />
                                    </Link>
                                )
                            )}
                            <div className="ml-4 border-l border-ash-800 pl-4">
                                <ThemeSwitcher />
                            </div>
                        </nav>

                        {/* Mobile action & menu button */}
                        <div className="flex items-center gap-2 md:hidden">
                            <ThemeSwitcher />
                            <button
                                className="text-ash-300 hover:text-toxic-green-DEFAULT transition-colors p-2"
                                onClick={() => setMenuOpen(!menuOpen)}
                                aria-label="Toggle menu"
                            >
                                {menuOpen ? <X size={22} /> : <Menu size={22} />}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Mobile menu */}
                {menuOpen && (
                    <div className="md:hidden bg-ash-950/98 backdrop-blur-md border-b border-toxic-green-DEFAULT/20">
                        <nav className="px-4 py-4 flex flex-col gap-2">
                            {navLinks.map(({ href, label, icon: Icon, highlight }) => (
                                <Link
                                    key={href}
                                    href={href}
                                    onClick={() => setMenuOpen(false)}
                                    className={`flex items-center gap-3 px-4 py-3 font-biohazard tracking-widest text-base transition-colors ${highlight
                                        ? "text-white bg-blood-red-DEFAULT border border-blood-red-bright/40 rounded"
                                        : "text-ash-300 hover:text-toxic-green-DEFAULT border border-ash-800 rounded hover:border-toxic-green-DEFAULT/30"
                                        }`}
                                >
                                    <Icon size={16} />
                                    {label}
                                </Link>
                            ))}
                        </nav>
                        {/* Status bar */}
                        <div className="flex items-center gap-2 px-8 pb-4 text-xs font-mono text-ash-600">
                            <Zap size={10} className="text-toxic-green-DEFAULT" />
                            <span>ĐANG ONLINE · 813+ CHƯƠNG</span>
                        </div>
                    </div>
                )}
            </header>

            {/* Spacer */}
            <div className="h-16" />
        </>
    );
}
