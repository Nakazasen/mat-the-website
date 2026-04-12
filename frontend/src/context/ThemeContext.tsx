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
    isAIEnabled: boolean;
    setIsAIEnabled: (enabled: boolean) => void;
    isLearningEnabled: boolean;
    setIsLearningEnabled: (enabled: boolean) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>('sepia');
    const [fontSize, setFontSizeState] = useState(18);
    const [fontFamily, setFontFamilyState] = useState<FontFamily>('sans');
    const [isAIEnabled, setIsAIEnabledState] = useState(true);
    const [isLearningEnabled, setIsLearningEnabledState] = useState(true);
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

        const savedAI = localStorage.getItem('reader-ai-enabled');
        if (savedAI !== null) {
            setIsAIEnabledState(savedAI === 'true');
        }

        const savedLearning = localStorage.getItem('reader-learning-enabled');
        if (savedLearning !== null) {
            setIsLearningEnabledState(savedLearning === 'true');
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
        localStorage.setItem('reader-ai-enabled', isAIEnabled.toString());
        localStorage.setItem('reader-learning-enabled', isLearningEnabled.toString());
    }, [theme, fontSize, fontFamily, isAIEnabled, isLearningEnabled, mounted]);

    const setTheme = (t: Theme) => setThemeState(t);
    const setFontSize = (s: number) => setFontSizeState(s);
    const setFontFamily = (f: FontFamily) => setFontFamilyState(f);
    const setIsAIEnabled = (enabled: boolean) => setIsAIEnabledState(enabled);
    const setIsLearningEnabled = (enabled: boolean) => setIsLearningEnabledState(enabled);

    return (
        <ThemeContext.Provider value={{
            theme, setTheme,
            fontSize, setFontSize,
            fontFamily, setFontFamily,
            isAIEnabled, setIsAIEnabled,
            isLearningEnabled, setIsLearningEnabled
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
