'use client';

import React, { useState } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { Sun, Moon, Coffee, Settings2 } from 'lucide-react';

export default function ThemeSwitcher() {
    const { theme, setTheme } = useTheme();
    const [isOpen, setIsOpen] = useState(false);

    const themes = [
        { id: 'dark', label: 'TỐI', icon: Moon, color: '#0d0d0d' },
        { id: 'light', label: 'SÁNG', icon: Sun, color: '#ffffff' },
        { id: 'sepia', label: 'VÀNG', icon: Coffee, color: '#f4ecd8' },
    ] as const;

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-2 text-ash-300 hover:text-toxic-green-DEFAULT transition-colors font-biohazard tracking-widest text-sm border border-ash-800 rounded hover:border-toxic-green-DEFAULT/30"
                title="Đổi giao diện"
            >
                <Settings2 size={16} className={isOpen ? 'animate-spin-slow' : ''} />
                <span className="hidden sm:inline">GIAO DIỆN</span>
            </button>

            {isOpen && (
                <>
                    <div
                        className="fixed inset-0 z-10"
                        onClick={() => setIsOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-40 bg-ash-950/95 backdrop-blur-md border border-toxic-green-DEFAULT/20 shadow-2xl z-20 py-2 rounded-lg animate-fade-in-up">
                        <div className="px-3 py-1 mb-2 border-b border-ash-800">
                            <span className="text-[10px] font-mono text-ash-500 uppercase tracking-tighter">CHẾ ĐỘ ĐỌC</span>
                        </div>
                        {themes.map((t) => (
                            <button
                                key={t.id}
                                onClick={() => {
                                    setTheme(t.id);
                                    setIsOpen(false);
                                }}
                                className={`w-full flex items-center justify-between px-4 py-2 text-xs font-biohazard tracking-widest transition-all ${theme === t.id
                                        ? 'text-toxic-green-DEFAULT bg-toxic-green-DEFAULT/10'
                                        : 'text-ash-400 hover:text-worn-white hover:bg-ash-800'
                                    }`}
                            >
                                <div className="flex items-center gap-3">
                                    <t.icon size={14} />
                                    <span>{t.label}</span>
                                </div>
                                {theme === t.id && <div className="w-1.5 h-1.5 rounded-full bg-toxic-green-DEFAULT animate-pulse" />}
                            </button>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
