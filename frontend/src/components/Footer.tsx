"use client";

import Link from "next/link";
import { useState, useEffect, useMemo } from "react";

import { useLocale } from "@/context/LocaleContext";
import { useNovel } from "@/context/NovelContext";
import { createAdminClient } from "@/lib/supabase-admin";

export default function Footer() {
    const { novel } = useNovel();
    const { dictionary, localizePath, locale } = useLocale();

    const [onlineCount, setOnlineCount] = useState(12);
    const [realtimeConnected, setRealtimeConnected] = useState(false);
    const [seed, setSeed] = useState(0);

    // Simulated traffic generator
    useEffect(() => {
        const nowHour = new Date().getHours();
        const baseByTime = 9 + Math.round(5 * Math.sin((nowHour - 14) * Math.PI / 12));
        
        let currentBase = baseByTime;
        setOnlineCount(currentBase);

        const interval = setInterval(() => {
            const change = Math.floor(Math.random() * 3) - 1;
            currentBase = Math.max(6, Math.min(25, currentBase + change));
            setSeed(s => s + 1);
            if (!realtimeConnected) {
                setOnlineCount(currentBase);
            }
        }, 7000);

        return () => clearInterval(interval);
    }, [realtimeConnected]);

    // Supabase Realtime Connection
    useEffect(() => {
        const supabase = createAdminClient();
        if (!supabase) return;

        const channelId = `online_presence_${Math.random().toString(36).substring(2, 10)}`;
        const channel = supabase.channel('online_presence', {
            config: {
                presence: {
                    key: channelId,
                }
            }
        });

        let active = true;

        channel
            .on('presence', { event: 'sync' }, () => {
                if (!active) return;
                const state = channel.presenceState();
                const actualCount = Object.keys(state).length;
                const baseByTime = 9 + Math.round(5 * Math.sin((new Date().getHours() - 14) * Math.PI / 12));
                const total = Math.max(actualCount, baseByTime + (actualCount > 1 ? actualCount - 1 : 0));
                setOnlineCount(total);
            })
            .subscribe(async (status) => {
                if (!active) return;
                if (status === 'SUBSCRIBED') {
                    setRealtimeConnected(true);
                    await channel.track({
                        online_at: new Date().toISOString(),
                    });
                } else {
                    setRealtimeConnected(false);
                }
            });

        return () => {
            active = false;
            channel.unsubscribe();
        };
    }, []);

    // Survivor distribution mapping labels
    const sectionLabels: Record<string, any> = {
        vi: {
            uplinkActive: "UPLINK HỆ THỐNG: HOẠT ĐỘNG",
            uplinkOffline: "UPLINK HỆ THỐNG: NGOẠI TUYẾN",
            locationHome: "Trang chủ",
            locationReader: "Đọc truyện",
            locationHQ: "Sở chỉ huy",
            locationWiki: "Bách khoa",
            distributionTitle: "PHÂN BỔ SỐNG SÓT",
            signalStatus: "Tín hiệu: Ổn định",
            totalOnline: "Tổng số liên kết"
        },
        en: {
            uplinkActive: "SYSTEM UPLINK: ACTIVE",
            uplinkOffline: "SYSTEM UPLINK: OFFLINE",
            locationHome: "Home Page",
            locationReader: "Reading Chapter",
            locationHQ: "Headquarters",
            locationWiki: "Lore Wiki",
            distributionTitle: "SURVIVOR DISTRIBUTION",
            signalStatus: "Signal: Stable",
            totalOnline: "Total Uplinks"
        },
        "zh-CN": {
            uplinkActive: "系统上行: 已激活",
            uplinkOffline: "系统上行: 已离线",
            locationHome: "主页",
            locationReader: "阅读章节",
            locationHQ: "司令部",
            locationWiki: "百科",
            distributionTitle: "幸存者分布",
            signalStatus: "信号: 稳定",
            totalOnline: "总连接数"
        },
        ja: {
            uplinkActive: "システム同期: アクティブ",
            uplinkOffline: "システム同期: オフライン",
            locationHome: "ホーム",
            locationReader: "読書中",
            locationHQ: "司令部",
            locationWiki: "百科事典",
            distributionTitle: "生存者の分布",
            signalStatus: "信号強度: 良好",
            totalOnline: "総接続数"
        }
    };

    const currentLabels = sectionLabels[locale] || sectionLabels.vi;

    const distributedLocations = useMemo(() => {
        const count = onlineCount;
        if (count <= 0) return [];
        
        let rRatio = 0.5 + 0.05 * Math.sin(seed * 0.7);
        let hRatio = 0.2 + 0.05 * Math.cos(seed * 0.9);
        let hqRatio = 0.15 + 0.03 * Math.sin(seed * 1.2);
        let wRatio = 1.0 - (rRatio + hRatio + hqRatio);
        if (wRatio < 0.05) wRatio = 0.05;
        
        const sumRatios = rRatio + hRatio + hqRatio + wRatio;
        rRatio /= sumRatios;
        hRatio /= sumRatios;
        hqRatio /= sumRatios;
        wRatio /= sumRatios;
        
        let rCount = Math.round(count * rRatio);
        let hCount = Math.round(count * hRatio);
        let hqCount = Math.round(count * hqRatio);
        let wCount = count - (rCount + hCount + hqCount);
        
        if (wCount < 0) {
            rCount += wCount;
            wCount = 0;
        }
        
        return [
            { name: currentLabels.locationReader, count: Math.max(1, rCount) },
            { name: currentLabels.locationHome, count: Math.max(1, hCount) },
            { name: currentLabels.locationHQ, count: Math.max(0, hqCount) },
            { name: currentLabels.locationWiki, count: Math.max(0, wCount) }
        ];
    }, [onlineCount, seed, locale, currentLabels]);

    const novelInfo = novel || {
        author: "Han Phong",
        status: "Updating",
        genres: ["Apocalypse", "Zombie"],
        max_chapter: 0,
        total_chapters: 0,
    };

    return (
        <footer className="bg-ash-950 border-t border-ash-800 mt-20">
            <div className="hazard-divider mx-8 mb-0" />

            <div className="max-w-7xl mx-auto px-6 py-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <span className="text-2xl text-toxic-green-DEFAULT">☣</span>
                            <div>
                                <div className="font-biohazard text-lg text-toxic-green-DEFAULT tracking-widest">
                                    {dictionary.footer.heading}
                                </div>
                                <div className="font-mono text-[9px] text-ash-500 tracking-[0.3em] uppercase">
                                    {dictionary.header.archive}
                                </div>
                            </div>
                        </div>
                        <p className="text-ash-400 text-sm leading-relaxed font-reading">
                            {dictionary.footer.blurb}
                        </p>
                    </div>

                    <div>
                        <h3 className="font-biohazard text-sm tracking-widest text-ash-300 mb-4 uppercase">
                            {dictionary.footer.links}
                        </h3>
                        <ul className="space-y-2">
                            {[
                                { href: "/", label: dictionary.common.home },
                                { href: "/chapters", label: dictionary.common.chapters },
                                { href: "/chapters/1", label: dictionary.footer.firstChapter },
                                { href: `/chapters/${novelInfo.max_chapter || 1}`, label: dictionary.footer.latest },
                            ].map(({ href, label }) => (
                                <li key={href}>
                                    <Link
                                        href={localizePath(href)}
                                        className="text-ash-400 hover:text-toxic-green-DEFAULT text-sm transition-colors flex items-center gap-2 group"
                                    >
                                        <span className="text-toxic-green-DEFAULT/30 group-hover:text-toxic-green-DEFAULT transition-colors">
                                            •
                                        </span>
                                        {label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-biohazard text-sm tracking-widest text-ash-300 mb-4 uppercase">
                            {dictionary.footer.stats}
                        </h3>
                        <div className="space-y-3">
                            {[
                                { label: dictionary.footer.author, value: novelInfo.author },
                                { label: dictionary.footer.status, value: novelInfo.status },
                                { label: dictionary.footer.genres, value: novelInfo.genres.join(" · ") },
                                { label: dictionary.footer.chapters, value: `${novelInfo.max_chapter || "?"}` },
                            ].map(({ label, value }) => (
                                <div key={label} className="flex justify-between text-sm gap-4">
                                    <span className="text-ash-500">{label}</span>
                                    <span className="text-ash-300 text-right">{value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="mt-10 pt-6 border-t border-ash-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-ash-600 text-xs font-mono">
                        © 2026 MAT THE · {dictionary.footer.allRightsReserved}
                    </p>
                    <div className="relative group flex items-center gap-2 cursor-pointer bg-ash-900/60 hover:bg-ash-900 border border-ash-800 hover:border-toxic-green-DEFAULT/50 px-3 py-1.5 rounded-md transition-all duration-300 shadow-sm shadow-black/20">
                        <span className="relative flex h-2 w-2">
                            {realtimeConnected && (
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-toxic-green-DEFAULT opacity-75"></span>
                            )}
                            <span className={`relative inline-flex rounded-full h-2 w-2 ${realtimeConnected ? 'bg-toxic-green-DEFAULT' : 'bg-amber-500 animate-pulse'}`}></span>
                        </span>
                        
                        <span className="text-xs font-mono text-ash-400 select-none">
                            {dictionary.common.online}: <span className="text-toxic-green-DEFAULT font-bold ml-1">{onlineCount}</span>
                        </span>

                        {/* Sci-fi HUD Hover Popover */}
                        <div className="absolute bottom-full right-0 mb-3 w-64 bg-ash-950/95 border border-toxic-green-DEFAULT/30 rounded p-4 shadow-xl opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity duration-300 z-50 backdrop-blur-md">
                            {/* Sci-fi HUD Header */}
                            <div className="flex justify-between items-center border-b border-ash-800 pb-2 mb-2 font-mono text-[10px] tracking-wider">
                                <span className={realtimeConnected ? "text-toxic-green-DEFAULT" : "text-amber-500"}>
                                    {realtimeConnected ? currentLabels.uplinkActive : currentLabels.uplinkOffline}
                                </span>
                                <span className="text-ash-500">{currentLabels.signalStatus}</span>
                            </div>
                            
                            {/* Survivor distribution list */}
                            <div className="space-y-2 font-mono text-xs">
                                <div className="text-[10px] text-ash-500 uppercase tracking-widest font-bold mb-1">
                                    {currentLabels.distributionTitle}
                                </div>
                                <div className="space-y-1.5">
                                    {distributedLocations.map((loc, idx) => (
                                        <div key={idx} className="flex justify-between items-center text-ash-400">
                                            <span className="flex items-center gap-2">
                                                <span className="w-1.5 h-1.5 rounded-full bg-toxic-green-DEFAULT/40" />
                                                {loc.name}
                                            </span>
                                            <span className="text-toxic-green-DEFAULT font-bold">{loc.count}</span>
                                        </div>
                                    ))}
                                </div>
                                
                                <div className="border-t border-ash-800/60 pt-2 mt-2 flex justify-between text-[10px] text-ash-500 uppercase">
                                    <span>{currentLabels.totalOnline}</span>
                                    <span className="text-ash-300 font-bold">{onlineCount}</span>
                                </div>
                            </div>
                            
                            {/* Cyberpunk corner details */}
                            <div className="absolute top-0 right-0 w-2 h-[1px] bg-toxic-green-DEFAULT/60" />
                            <div className="absolute top-0 right-0 w-[1px] h-2 bg-toxic-green-DEFAULT/60" />
                            <div className="absolute bottom-0 left-0 w-2 h-[1px] bg-toxic-green-DEFAULT/60" />
                            <div className="absolute bottom-0 left-0 w-[1px] h-2 bg-toxic-green-DEFAULT/60" />
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    );
}
