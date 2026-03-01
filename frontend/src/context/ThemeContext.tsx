'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'dark' | 'light' | 'sepia';
type FontFamily = 'sans' | 'serif';

interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
    fontSize: number;
    setFontSize: (size: number) => void;
    fontFamily: FontFamily;
    setFontFamily: (font: FontFamily) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>('dark');
    const [fontSize, setFontSizeState] = useState(18);
    const [fontFamily, setFontFamilyState] = useState<FontFamily>('sans');
    const [mounted, setMounted] = useState(false);

    // Initialize state from localStorage on mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('reader-theme') as Theme;
        if (savedTheme && ['dark', 'light', 'sepia'].includes(savedTheme)) {
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

        setMounted(true);
    }, []);

    // Update document attribute and localStorage when settings change
    useEffect(() => {
        if (!mounted) return;

        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('reader-theme', theme);
        localStorage.setItem('reader-font-size', fontSize.toString());
        localStorage.setItem('reader-font-family', fontFamily);

        // Manage 'dark' class for Tailwind
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme, fontSize, fontFamily, mounted]);

    const setTheme = (newTheme: Theme) => setThemeState(newTheme);
    const setFontSize = (size: number) => setFontSizeState(size);
    const setFontFamily = (font: FontFamily) => setFontFamilyState(font);

    return (
        <ThemeContext.Provider value={{
            theme, setTheme,
            fontSize, setFontSize,
            fontFamily, setFontFamily
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
