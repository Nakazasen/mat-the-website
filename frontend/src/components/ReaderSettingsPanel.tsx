"use client";

import { useTheme } from "@/context/ThemeContext";
import { Moon, Sun, Coffee, Settings } from "lucide-react";
import { useState } from "react";

interface ReaderSettingsPanelProps {
    showReadingProgress?: boolean;
    readingProgress?: number;
    className?: string;
}

export default function ReaderSettingsPanel({
    showReadingProgress = false,
    readingProgress = 0,
    className = ""
}: ReaderSettingsPanelProps) {
    const { theme, setTheme, fontSize, setFontSize, fontFamily, setFontFamily } = useTheme();
    const [showSettings, setShowSettings] = useState(false);
    
    // Debug log to confirm component is rendering with expected data
    // console.log("ReaderSettingsPanel theme:", theme, "fontSize:", fontSize);

    return (
        <div className={`relative ${className}`}>
            <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-ash-500 hover:text-toxic-green-DEFAULT transition-colors"
                title="Cài đặt đọc"
            >
                <Settings size={15} />
            </button>

            {showSettings && (
                <div className="absolute top-full right-0 mt-2 z-50 min-w-[300px] sm:min-w-[450px] border border-reader-border bg-reader-bg px-4 py-4 rounded-xl shadow-2xl backdrop-blur-md">
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-col gap-4">
                            {/* Theme */}
                            <div className="flex items-center gap-3">
                                <span className="text-reader-muted text-[10px] font-mono tracking-widest uppercase w-16">NỀN</span>
                                <div className="flex bg-reader-accent/5 p-1 rounded border border-reader-border">
                                    {[
                                        { id: 'dark', icon: Moon, label: 'TỐI' },
                                        { id: 'light', icon: Sun, label: 'SÁNG' },
                                        { id: 'sepia', icon: Coffee, label: 'VÀNG' }
                                    ].map((t) => (
                                        <button
                                            key={t.id}
                                            onClick={() => setTheme(t.id as any)}
                                            className={`flex items-center gap-2 px-3 py-1.5 text-[10px] font-mono tracking-widest rounded transition-all ${theme === t.id
                                                ? "bg-reader-accent text-black shadow-[0_0_10px_rgba(var(--reader-accent-rgb),0.3)]"
                                                : "text-reader-muted hover:text-reader-text"
                                                }`}
                                        >
                                            <t.icon size={12} />
                                            <span className="hidden xs:inline">{t.label}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Font Family */}
                            <div className="flex items-center gap-3">
                                <span className="text-reader-muted text-[10px] font-mono tracking-widest uppercase w-16">FONT</span>
                                <div className="flex bg-reader-accent/5 p-1 rounded border border-reader-border">
                                    <button
                                        onClick={() => setFontFamily('sans')}
                                        className={`px-4 py-1.5 text-[10px] font-mono tracking-widest rounded transition-all ${fontFamily === 'sans' ? "bg-reader-accent text-black" : "text-reader-muted hover:text-reader-text"}`}
                                    >
                                        SANS-SERIF
                                    </button>
                                    <button
                                        onClick={() => setFontFamily('serif')}
                                        className={`px-4 py-1.5 text-[10px] font-serif tracking-widest rounded transition-all ${fontFamily === 'serif' ? "bg-reader-accent text-black" : "text-reader-muted hover:text-reader-text"}`}
                                    >
                                        SERIF
                                    </button>
                                </div>
                            </div>

                            {/* Font size */}
                            <div className="flex items-center gap-3">
                                <span className="text-reader-muted text-[10px] font-mono tracking-widest uppercase w-16">CỠ CHỮ</span>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => setFontSize(Math.max(12, fontSize - 1))}
                                        className="w-8 h-8 flex items-center justify-center border border-reader-border text-reader-text hover:border-reader-accent hover:text-reader-accent transition-colors rounded text-sm font-mono"
                                    >
                                        -
                                    </button>
                                    <span className="text-reader-accent font-mono text-sm w-8 text-center bg-reader-accent/10 py-1 rounded">
                                        {fontSize}
                                    </span>
                                    <button
                                        onClick={() => setFontSize(Math.min(32, fontSize + 1))}
                                        className="w-8 h-8 flex items-center justify-center border border-reader-border text-reader-text hover:border-reader-accent hover:text-reader-accent transition-colors rounded text-sm font-mono"
                                    >
                                        +
                                    </button>
                                </div>
                            </div>
                        </div>

                        {showReadingProgress && (
                            <div className="text-reader-muted text-[10px] font-mono text-center sm:text-right border-t border-reader-border pt-2">
                                {Math.round(readingProgress)}% đã đọc
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
