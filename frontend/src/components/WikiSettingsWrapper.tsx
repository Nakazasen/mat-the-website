"use client";

import React, { ReactNode } from "react";
import { useTheme } from "@/context/ThemeContext";
import ReaderSettingsPanel from "@/components/ReaderSettingsPanel";

export default function WikiSettingsWrapper({ children }: { children: ReactNode }) {
    const { theme, fontFamily, fontSize } = useTheme();

    return (
        <div id="wiki-reader-container" 
             className={`min-h-screen transition-colors duration-300 ${fontFamily === 'serif' ? 'font-serif' : 'font-sans'}`}
             style={{ 
                backgroundColor: 'var(--reader-bg)', 
                color: 'var(--reader-text)',
                fontSize: `${fontSize}px`
             }}>
            {children}
            
            {/* Custom styles for Wiki content to respect font size and theme */}
            <style jsx global>{`
                /* Force body and html to respect the reader theme background */
                html[data-theme='light'], html[data-theme='light'] body {
                    background-color: #ffffff !important;
                }
                html[data-theme='sepia'], html[data-theme='sepia'] body {
                    background-color: #f4ecd8 !important;
                }
                html[data-theme='dark'], html[data-theme='dark'] body {
                    background-color: #0d0d0d !important;
                }

                /* Ensure the reader container itself is fixed to the variable */
                #wiki-reader-container {
                    background-color: var(--reader-bg) !important;
                    color: var(--reader-text) !important;
                }

                /* Ensure Header is also theme-aware or transparent */
                header {
                    background-color: var(--reader-bg) !important;
                    border-bottom-color: var(--reader-border) !important;
                }
                
                .rich-text-content p, .rich-text-content li {
                    font-size: ${fontSize}px !important;
                }
                .rich-text-content h1, .rich-text-content h2, .rich-text-content h3 {
                    color: var(--reader-text) !important;
                }
            `}</style>
        </div>
    );
}
