"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
    BookOpen,
    HelpCircle,
    Home,
    List,
    LogIn,
    LogOut,
    Map as MapIcon,
    Menu,
    Trophy,
    User,
    X,
    Zap,
} from "lucide-react";
import type { User as SupabaseUser } from "@supabase/supabase-js";

import { useLocale } from "@/context/LocaleContext";
import { useNovel } from "@/context/NovelContext";
import { createAdminClient } from "@/lib/supabase-admin";

import LanguageSwitcher from "./LanguageSwitcher";
import ReaderSettingsPanel from "./ReaderSettingsPanel";

export default function Header() {
    const { novel } = useNovel();
    const { dictionary, localizePath } = useLocale();
    const [scrolled, setScrolled] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);
    const [user, setUser] = useState<SupabaseUser | null>(null);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 40);
        window.addEventListener("scroll", handleScroll, { passive: true });

        const supabase = createAdminClient();
        if (!supabase) {
            return () => window.removeEventListener("scroll", handleScroll);
        }

        supabase.auth.getSession().then(({ data: { session } }) => {
            setUser(session?.user ?? null);
        });

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null);
        });

        return () => {
            window.removeEventListener("scroll", handleScroll);
            subscription.unsubscribe();
        };
    }, []);

    const handleLogin = async () => {
        const supabase = createAdminClient();
        if (!supabase) return;
        await supabase.auth.signInWithOAuth({
            provider: "google",
            options: {
                redirectTo: `${window.location.origin}/auth/callback`,
            },
        });
    };

    const handleLogout = async () => {
        const supabase = createAdminClient();
        if (!supabase) return;
        await supabase.auth.signOut();
        window.location.reload();
    };

    const navLinks = [
        { href: "/", label: dictionary.common.home, icon: Home },
        { href: "/chapters", label: dictionary.common.chapters, icon: List },
        { href: "/wiki", label: dictionary.common.wiki, icon: BookOpen },
        { href: "/leaderboard", label: dictionary.common.leaderboard, icon: Trophy },
        { href: "/map", label: dictionary.common.map, icon: MapIcon },
        { href: "/headquarters", label: dictionary.common.headquarters, icon: Zap },
        { href: "/huong-dan", label: dictionary.common.guide, icon: HelpCircle },
        { href: "/chapters/1", label: dictionary.common.readNow, icon: BookOpen, highlight: true },
    ];

    return (
        <>
            <header
                className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
                    scrolled
                        ? "bg-ash-950/95 backdrop-blur-md border-b border-toxic-green-DEFAULT/20 shadow-lg shadow-black/50"
                        : "bg-transparent"
                }`}
            >
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="flex items-center justify-between h-16 md:h-18">
                        <Link href={localizePath("/")} className="flex items-center gap-3 group">
                            <div className="relative">
                                <span className="text-3xl animate-flicker">☣</span>
                                <span className="absolute -inset-1 rounded-full bg-toxic-green-DEFAULT/10 blur-sm group-hover:bg-toxic-green-DEFAULT/20 transition-all" />
                            </div>
                            <div className="hidden sm:block">
                                <div className="font-biohazard text-xl leading-none text-toxic-green-DEFAULT tracking-widest">
                                    {dictionary.footer.heading}
                                </div>
                                <div className="font-mono text-[9px] text-ash-400 tracking-[0.3em] uppercase">
                                    {dictionary.header.archive}
                                </div>
                            </div>
                        </Link>

                        <nav className="hidden md:flex items-center gap-1">
                            {navLinks.map(({ href, label, icon: Icon, highlight }) =>
                                highlight ? (
                                    <Link
                                        key={href}
                                        href={localizePath(href)}
                                        className="btn-blood ml-2 flex items-center gap-2 text-sm"
                                    >
                                        <Icon size={14} />
                                        <span>{label}</span>
                                    </Link>
                                ) : (
                                    <Link
                                        key={href}
                                        href={localizePath(href)}
                                        className="flex items-center gap-2 px-3 py-2 text-sm font-biohazard tracking-widest text-ash-200 hover:text-toxic-green-DEFAULT transition-colors relative group"
                                    >
                                        <Icon size={13} />
                                        {label}
                                        <span className="absolute bottom-0 left-0 w-0 h-px bg-toxic-green-DEFAULT group-hover:w-full transition-all duration-300" />
                                    </Link>
                                ),
                            )}

                            <div className="ml-3 flex items-center gap-3 border-l border-ash-800 pl-3">
                                <LanguageSwitcher />
                                <ReaderSettingsPanel className="flex items-center" />
                                {user ? (
                                    <div className="group relative">
                                        <button className="flex items-center gap-2 text-ash-300 hover:text-white transition-colors">
                                            {user.user_metadata?.avatar_url ? (
                                                // eslint-disable-next-line @next/next/no-img-element
                                                <img src={user.user_metadata.avatar_url} alt="Avatar" className="w-8 h-8 rounded-full border border-ash-700" />
                                            ) : (
                                                <div className="w-8 h-8 rounded-full bg-ash-800 flex items-center justify-center border border-ash-700">
                                                    <User size={14} />
                                                </div>
                                            )}
                                        </button>
                                        <div className="absolute right-0 top-full mt-2 w-48 bg-ash-900 border border-ash-800 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                                            <div className="p-3 border-b border-ash-800">
                                                <div className="text-sm text-white font-medium truncate">{user.user_metadata?.full_name || user.email}</div>
                                                <div className="text-xs text-ash-400 truncate">{user.email}</div>
                                            </div>
                                            <Link
                                                href={localizePath("/profile")}
                                                className="w-full flex items-center gap-2 p-3 text-sm text-ash-300 hover:text-toxic-green-DEFAULT hover:bg-ash-800/50 transition-colors tracking-wider font-mono"
                                            >
                                                <User size={14} />
                                                {dictionary.common.profile}
                                            </Link>
                                            <button onClick={handleLogout} className="w-full flex items-center gap-2 p-3 text-sm text-red-400 hover:bg-ash-800/50 transition-colors rounded-b-lg tracking-wider font-mono">
                                                <LogOut size={14} />
                                                {dictionary.common.logout}
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <button onClick={handleLogin} className="flex items-center gap-2 px-3 py-1.5 text-xs font-mono text-toxic-green-DEFAULT border border-toxic-green-DEFAULT/30 hover:bg-toxic-green-DEFAULT/10 tracking-widest rounded transition-all">
                                        <LogIn size={14} />
                                        {dictionary.common.login}
                                    </button>
                                )}
                            </div>
                        </nav>

                        <div className="flex items-center gap-2 md:hidden">
                            <ReaderSettingsPanel className="flex items-center" />
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

                {menuOpen && (
                    <div className="md:hidden bg-ash-950/98 backdrop-blur-md border-b border-toxic-green-DEFAULT/20">
                        <div className="px-4 pt-4">
                            <LanguageSwitcher mobile />
                        </div>
                        <nav className="px-4 py-4 flex flex-col gap-2">
                            {navLinks.map(({ href, label, icon: Icon, highlight }) => (
                                <Link
                                    key={href}
                                    href={localizePath(href)}
                                    onClick={() => setMenuOpen(false)}
                                    className={`flex items-center gap-3 px-4 py-3 font-biohazard tracking-widest text-base transition-colors ${
                                        highlight
                                            ? "text-white bg-blood-red-DEFAULT border border-blood-red-bright/40 rounded"
                                            : "text-ash-300 hover:text-toxic-green-DEFAULT border border-ash-800 rounded hover:border-toxic-green-DEFAULT/30"
                                    }`}
                                >
                                    <Icon size={16} />
                                    {label}
                                </Link>
                            ))}
                        </nav>

                        <div className="px-4 py-4 border-t border-ash-800/50">
                            {user ? (
                                <div className="flex flex-col gap-3">
                                    <div className="flex items-center gap-3 bg-ash-900/50 p-3 rounded-lg border border-ash-800">
                                        {user.user_metadata?.avatar_url ? (
                                            // eslint-disable-next-line @next/next/no-img-element
                                            <img src={user.user_metadata.avatar_url} alt="Avatar" className="w-10 h-10 rounded-full border border-ash-700" />
                                        ) : (
                                            <div className="w-10 h-10 rounded-full bg-ash-800 flex items-center justify-center border border-ash-700">
                                                <User size={18} />
                                            </div>
                                        )}
                                        <div className="flex-1 min-w-0">
                                            <div className="text-sm text-white font-medium truncate">{user.user_metadata?.full_name || user.email}</div>
                                            <div className="text-xs text-ash-400 truncate">{user.email}</div>
                                        </div>
                                    </div>
                                    <Link href={localizePath("/profile")} onClick={() => setMenuOpen(false)} className="w-full flex items-center justify-center gap-2 py-3 text-sm font-mono text-toxic-green-DEFAULT bg-toxic-green-DEFAULT/5 hover:bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/30 tracking-widest rounded transition-all">
                                        <User size={16} />
                                        {dictionary.common.profile}
                                    </Link>
                                    <button onClick={handleLogout} className="w-full flex items-center justify-center gap-2 py-3 text-sm font-mono text-red-400 bg-red-950/20 hover:bg-red-950/40 border border-red-900/30 tracking-widest rounded transition-all">
                                        <LogOut size={16} />
                                        {dictionary.common.logout}
                                    </button>
                                </div>
                            ) : (
                                <button onClick={handleLogin} className="w-full flex items-center justify-center gap-2 py-3 text-sm font-mono text-toxic-green-DEFAULT bg-toxic-green-DEFAULT/5 hover:bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/30 tracking-widest rounded transition-all">
                                    <LogIn size={16} />
                                    {dictionary.common.login}
                                </button>
                            )}
                        </div>

                        <div className="flex items-center gap-2 px-8 pb-4 text-xs font-mono text-ash-600">
                            <Zap size={10} className="text-toxic-green-DEFAULT" />
                            <span>{dictionary.common.online} · {novel?.max_chapter || "?"} {dictionary.common.chapters}</span>
                        </div>
                    </div>
                )}
            </header>

            <div className="h-16" />
        </>
    );
}
