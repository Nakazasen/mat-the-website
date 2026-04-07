"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
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
    const { locale, dictionary, localizePath } = useLocale();
    const pathname = usePathname();
    const [scrolled, setScrolled] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);
    const [user, setUser] = useState<SupabaseUser | null>(null);
    const [lastReadChapter, setLastReadChapter] = useState<string | null>(null);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        const handleScroll = () => setScrolled(window.scrollY > 40);
        window.addEventListener("scroll", handleScroll, { passive: true });

        const supabase = createAdminClient();
        if (supabase) {
            supabase.auth.getSession().then(({ data: { session } }) => {
                setUser(session?.user ?? null);
            });

            const {
                data: { subscription },
            } = supabase.auth.onAuthStateChange((_event, session) => {
                setUser(session?.user ?? null);
            });

            // Cleanup function for internal listeners
            return () => {
                window.removeEventListener("scroll", handleScroll);
                subscription.unsubscribe();
            };
        }

        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    // Re-sync progress on navigation
    useEffect(() => {
        if (!mounted) return;
        
        const savedChapter = localStorage.getItem("lastReadChapter");
        console.log("Header sync - pathname:", pathname, "savedChapter:", savedChapter);
        setLastReadChapter(savedChapter);
    }, [pathname, mounted]);

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
        { id: "home", href: "/", label: dictionary.common.home, icon: Home },
        { id: "chapters", href: "/chapters", label: dictionary.common.chapters, icon: List },
        { id: "wiki", href: "/wiki", label: dictionary.common.wiki, icon: BookOpen },
        { id: "leaderboard", href: "/leaderboard", label: dictionary.common.leaderboard, icon: Trophy },
        { id: "map", href: "/map", label: dictionary.common.map, icon: MapIcon },
        { id: "hq", href: "/headquarters", label: dictionary.common.headquarters, icon: Zap },
        { id: "guide", href: "/huong-dan", label: dictionary.common.guide, icon: HelpCircle },
        // Only show dynamic button after mounting to prevent hydration mismatch
        ...(mounted 
            ? [lastReadChapter
                ? {
                      id: "header-continue-button",
                      href: `/chapters/${lastReadChapter}`,
                      label: dictionary.reader.continueReading,
                      icon: BookOpen,
                      highlight: true,
                      isContinue: true,
                  }
                : {
                      id: "header-read-now-button",
                      href: "/chapters/1",
                      label: dictionary.common.readNow,
                      icon: BookOpen,
                      highlight: true,
                  }]
            : [])
    ];

    const isEastAsianLocale = locale === "ja" || locale === "zh-CN";
    const brandClassName = isEastAsianLocale
        ? "font-biohazard text-[1.36rem] leading-none text-ash-100 tracking-[0.04em]"
        : "font-biohazard text-[1.45rem] leading-none text-ash-100 tracking-[0.08em]";
    const desktopNavClassName = isEastAsianLocale
        ? "group relative flex items-center gap-2 rounded-full px-3 py-2 text-[0.92rem] font-biohazard tracking-[0.03em] text-ash-300 transition-colors hover:bg-white/4 hover:text-white"
        : "group relative flex items-center gap-2 rounded-full px-3.5 py-2 text-sm font-biohazard tracking-[0.08em] text-ash-300 transition-colors hover:bg-white/4 hover:text-white";
    const mobileNavClassName = isEastAsianLocale
        ? "flex items-center gap-3 px-4 py-3 font-biohazard tracking-[0.04em] text-[1.02rem] transition-colors"
        : "flex items-center gap-3 px-4 py-3 font-biohazard tracking-widest text-base transition-colors";

    return (
        <>
            <header
                className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
                    scrolled
                        ? "bg-black/80 backdrop-blur-xl border-b border-white/8 shadow-[0_18px_50px_rgba(0,0,0,0.42)]"
                        : "bg-black/44 backdrop-blur-md border-b border-white/6"
                }`}
            >
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="flex items-center justify-between h-16 md:h-[74px]">
                        <Link href={localizePath("/")} className="flex items-center gap-3 group">
                            <div className="relative">
                                <span className="text-3xl animate-flicker">☣</span>
                                <span className="absolute -inset-1 rounded-full bg-toxic-green-DEFAULT/8 blur-sm group-hover:bg-toxic-green-DEFAULT/15 transition-all" />
                            </div>
                            <div className="hidden sm:block">
                                <div className={brandClassName}>
                                    {dictionary.footer.heading}
                                </div>
                                <div className="font-mono text-[9px] text-ash-500 tracking-[0.28em] uppercase">
                                    {dictionary.header.archive}
                                </div>
                            </div>
                        </Link>

                        <nav className="hidden md:flex items-center gap-1.5">
                            {navLinks.map(({ id, href, label, icon: Icon, highlight, isContinue }) =>
                                highlight ? (
                                    <Link
                                        key={id}
                                        href={localizePath(href)}
                                        className={`${
                                            isContinue
                                                ? "btn-toxic shadow-[0_14px_32px_rgba(57,255,20,0.18)]"
                                                : "btn-blood shadow-[0_14px_32px_rgba(139,0,0,0.18)]"
                                        } ml-2 flex items-center gap-2 px-5 py-2.5 text-sm transition-all`}
                                    >
                                        <Icon size={14} />
                                        <span>{label}</span>
                                    </Link>
                                ) : (
                                    <Link
                                        key={id}
                                        href={localizePath(href)}
                                        className={desktopNavClassName}
                                    >
                                        <Icon size={13} />
                                        {label}
                                        <span className="absolute bottom-[5px] left-3.5 right-3.5 h-px scale-x-0 bg-toxic-green-DEFAULT/70 transition-transform duration-300 group-hover:scale-x-100" />
                                    </Link>
                                ),
                            )}

                            <div className="ml-3 flex items-center gap-3 border-l border-white/8 pl-4">
                                <LanguageSwitcher />
                                <ReaderSettingsPanel className="flex items-center" />
                                {user ? (
                                    <div className="group relative">
                                        <button className="flex items-center gap-2 text-ash-300 hover:text-white transition-colors">
                                            {user.user_metadata?.avatar_url ? (
                                                // eslint-disable-next-line @next/next/no-img-element
                                                <img src={user.user_metadata.avatar_url} alt="Avatar" className="w-8 h-8 rounded-full border border-white/10" />
                                            ) : (
                                                <div className="w-8 h-8 rounded-full bg-black/40 flex items-center justify-center border border-white/10">
                                                    <User size={14} />
                                                </div>
                                            )}
                                        </button>
                                        <div className="absolute right-0 top-full mt-2 w-48 rounded-xl border border-white/10 bg-black/88 shadow-2xl backdrop-blur-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                                            <div className="p-3 border-b border-white/8">
                                                <div className="text-sm text-white font-medium truncate">{user.user_metadata?.full_name || user.email}</div>
                                                <div className="text-xs text-ash-400 truncate">{user.email}</div>
                                            </div>
                                            <Link
                                                href={localizePath("/profile")}
                                                className="w-full flex items-center gap-2 p-3 text-sm text-ash-300 hover:text-white hover:bg-white/4 transition-colors tracking-wider font-mono"
                                            >
                                                <User size={14} />
                                                {dictionary.common.profile}
                                            </Link>
                                            <button onClick={handleLogout} className="w-full flex items-center gap-2 rounded-b-xl p-3 text-sm text-red-400 hover:bg-white/4 transition-colors tracking-wider font-mono">
                                                <LogOut size={14} />
                                                {dictionary.common.logout}
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <button onClick={handleLogin} className="flex items-center gap-2 rounded-full border border-white/12 bg-black/36 px-3.5 py-2 text-xs font-mono tracking-[0.24em] text-ash-200 transition-all hover:border-white/18 hover:bg-white/5 hover:text-white">
                                        <LogIn size={14} />
                                        {dictionary.common.login}
                                    </button>
                                )}
                            </div>
                        </nav>

                        <div className="flex items-center gap-2 md:hidden">
                            <ReaderSettingsPanel className="flex items-center" />
                            <button
                                className="rounded-full border border-white/10 bg-black/36 p-2 text-ash-300 transition-colors hover:bg-white/5 hover:text-white"
                                onClick={() => setMenuOpen(!menuOpen)}
                                aria-label="Toggle menu"
                            >
                                {menuOpen ? <X size={22} /> : <Menu size={22} />}
                            </button>
                        </div>
                    </div>
                </div>

                {menuOpen && (
                    <div className="md:hidden border-b border-white/8 bg-black/78 px-3 pb-3 backdrop-blur-xl">
                        <div className="mt-2 overflow-hidden rounded-[24px] border border-white/10 bg-black/88 shadow-[0_24px_80px_rgba(0,0,0,0.42)]">
                        <div className="px-4 pt-4">
                            <LanguageSwitcher mobile />
                        </div>
                        <nav className="px-4 py-4 flex flex-col gap-2">
                            {navLinks.map(({ id, href, label, icon: Icon, highlight, isContinue }) => (
                                <Link
                                    key={id}
                                    href={localizePath(href)}
                                    onClick={() => setMenuOpen(false)}
                                    className={`${mobileNavClassName} ${
                                        highlight
                                            ? isContinue
                                                ? "rounded-2xl border border-toxic-green-DEFAULT/35 bg-toxic-green-DEFAULT/90 text-black shadow-[0_14px_34px_rgba(57,255,20,0.2)]"
                                                : "rounded-2xl border border-blood-red-bright/35 bg-blood-red-DEFAULT/92 text-white shadow-[0_14px_34px_rgba(139,0,0,0.2)]"
                                            : "rounded-2xl border border-white/8 bg-white/[0.03] text-ash-300 hover:border-white/12 hover:bg-white/5 hover:text-white"
                                    }`}
                                >
                                    <Icon size={16} />
                                    {label}
                                </Link>
                            ))}
                        </nav>

                        <div className="border-t border-white/8 px-4 py-4">
                            {user ? (
                                <div className="flex flex-col gap-3">
                                    <div className="flex items-center gap-3 rounded-xl border border-white/8 bg-black/36 p-3">
                                        {user.user_metadata?.avatar_url ? (
                                            // eslint-disable-next-line @next/next/no-img-element
                                            <img src={user.user_metadata.avatar_url} alt="Avatar" className="w-10 h-10 rounded-full border border-white/10" />
                                        ) : (
                                            <div className="w-10 h-10 rounded-full bg-black/40 flex items-center justify-center border border-white/10">
                                                <User size={18} />
                                            </div>
                                        )}
                                        <div className="flex-1 min-w-0">
                                            <div className="text-sm text-white font-medium truncate">{user.user_metadata?.full_name || user.email}</div>
                                            <div className="text-xs text-ash-400 truncate">{user.email}</div>
                                        </div>
                                    </div>
                                    <Link href={localizePath("/profile")} onClick={() => setMenuOpen(false)} className="w-full flex items-center justify-center gap-2 rounded-xl border border-white/12 bg-black/36 py-3 text-sm font-mono tracking-[0.24em] text-ash-200 transition-all hover:bg-white/5 hover:text-white">
                                        <User size={16} />
                                        {dictionary.common.profile}
                                    </Link>
                                    <button onClick={handleLogout} className="w-full flex items-center justify-center gap-2 rounded-xl border border-red-900/30 bg-red-950/20 py-3 text-sm font-mono tracking-[0.24em] text-red-400 transition-all hover:bg-red-950/40">
                                        <LogOut size={16} />
                                        {dictionary.common.logout}
                                    </button>
                                </div>
                            ) : (
                                <button onClick={handleLogin} className="w-full flex items-center justify-center gap-2 rounded-xl border border-white/12 bg-black/36 py-3 text-sm font-mono tracking-[0.24em] text-ash-200 transition-all hover:bg-white/5 hover:text-white">
                                    <LogIn size={16} />
                                    {dictionary.common.login}
                                </button>
                            )}
                        </div>

                        <div className="flex items-center gap-2 px-8 pb-4 text-[11px] font-mono uppercase tracking-[0.2em] text-ash-600">
                            <Zap size={10} className="text-toxic-green-DEFAULT" />
                            <span>{dictionary.common.online} · {novel?.max_chapter || "?"} {dictionary.common.chapters}</span>
                        </div>
                        </div>
                    </div>
                )}
            </header>

            <div className="h-16" />
        </>
    );
}
