'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'dark' | 'light' | 'sepia';

interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
    fontSize: number;
    setFontSize: (size: number) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>('dark');
    const [fontSize, setFontSizeState] = useState(18);
    const [mounted, setMounted] = useState(false);

    // Initialize theme from localStorage on mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('reader-theme') as Theme;
        if (savedTheme && ['dark', 'light', 'sepia'].includes(savedTheme)) {
            setThemeState(savedTheme);
        }

        const savedFontSize = localStorage.getItem('reader-font-size');
        if (savedFontSize) {
            setFontSizeState(parseInt(savedFontSize, 10));
        }

        setMounted(true);
    }, []);

    // Update document attribute and localStorage when theme changes
    useEffect(() => {
        if (!mounted) return;

        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('reader-theme', theme);
        localStorage.setItem('reader-font-size', fontSize.toString());

        // Also manage the 'dark' class for Tailwind components that might rely on it
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme, mounted]);

    const setTheme = (newTheme: Theme) => {
        setThemeState(newTheme);
    };

    const setFontSize = (size: number) => {
        setFontSizeState(size);
    };

    return (
        <ThemeContext.Provider value={{ theme, setTheme, fontSize, setFontSize }}>
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
