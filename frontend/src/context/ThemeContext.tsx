'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'dark' | 'light' | 'sepia' | 'hazard';
type FontFamily = 'sans' | 'serif';

interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
    fontSize: number;
    setFontSize: (size: number) => void;
    fontFamily: FontFamily;
    setFontFamily: (font: FontFamily) => void;
    isAnimated: boolean;
    setIsAnimated: (isAnimated: boolean) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>('dark');
    const [fontSize, setFontSizeState] = useState(18);
    const [fontFamily, setFontFamilyState] = useState<FontFamily>('sans');
    const [isAnimated, setIsAnimatedState] = useState(true);
    const [mounted, setMounted] = useState(false);

    // Initialize state from localStorage on mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('reader-theme') as Theme;
        if (savedTheme && ['dark', 'light', 'sepia', 'hazard'].includes(savedTheme)) {
            setThemeState(savedTheme);
        }

        const savedFontSize = localStorage.getItem('reader-font-size');
        if (savedFontSize) {
            setFontSizeState(parseInt(savedFontSize, 10));
        }

        const savedFontFamily = localStorage.getItem('reader-font-family') as FontFamily;
        if (savedFontFamily && ['sans', 'serif'].includes(savedFontFamily)) {
            setFontFamilyState(savedFontFamily);
        }

        const savedIsAnimated = localStorage.getItem('reader-is-animated');
        if (savedIsAnimated !== null) {
            setIsAnimatedState(savedIsAnimated === 'true');
        }

        setMounted(true);
    }, []);

    // Update document attribute and localStorage when settings change
    useEffect(() => {
        if (!mounted) return;

        if (typeof document !== 'undefined') {
            document.documentElement.setAttribute('data-theme', theme);
            if (theme === 'dark') {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        }
        localStorage.setItem('reader-theme', theme);
        localStorage.setItem('reader-font-size', fontSize.toString());
        localStorage.setItem('reader-font-family', fontFamily);
        localStorage.setItem('reader-is-animated', isAnimated.toString());
    }, [theme, fontSize, fontFamily, isAnimated, mounted]);

    const setTheme = (newTheme: Theme) => setThemeState(newTheme);
    const setFontSize = (size: number) => setFontSizeState(size);
    const setFontFamily = (font: FontFamily) => setFontFamilyState(font);
    const setIsAnimated = (anim: boolean) => setIsAnimatedState(anim);

    return (
        <ThemeContext.Provider value={{
            theme, setTheme,
            fontSize, setFontSize,
            fontFamily, setFontFamily,
            isAnimated, setIsAnimated
        }}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
}
