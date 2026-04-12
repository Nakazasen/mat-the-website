import type { Config } from "tailwindcss";
import typography from "@tailwindcss/typography";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // === BIOHAZARD PALETTE ===
                "toxic-green": {
                    DEFAULT: "#39FF14",
                    dark: "#1a7a09",
                    glow: "#00ff41",
                    muted: "#2dcc0f",
                    dim: "#1a5c09",
                },
                "blood-red": {
                    DEFAULT: "#8B0000",
                    bright: "#cc0000",
                    deep: "#5c0000",
                    glow: "#ff2020",
                },
                ash: {
                    DEFAULT: "#1a1a1a",
                    light: "#2a2a2a",
                    dark: "#0d0d0d",
                    50: "#f5f5f5",
                    100: "#e5e5e5",
                    200: "#c5c5c5",
                    300: "#a0a0a0",
                    400: "#737373",
                    500: "#525252",
                    600: "#404040",
                    700: "#303030",
                    800: "#202020",
                    900: "#141414",
                    950: "#0a0a0a",
                },
                "worn-white": "#d4d0c8",
                "bone": "#e8e0d0",
                "haze": "#8a8878",
                // === READER THEMES ===
                "reader-bg": "var(--reader-bg)",
                "reader-text": "var(--reader-text)",
                "reader-accent": "var(--reader-accent)",
                "reader-muted": "var(--reader-muted)",
                "reader-border": "var(--reader-border)",
                "reader-card-bg": "var(--reader-card-bg)",
            },
            fontFamily: {
                biohazard: ["Bebas Neue", "Impact", "sans-serif"],
                reading: ["Noto Serif", "Georgia", "serif"],
                mono: ["Courier Prime", "Courier New", "monospace"],
                ui: ["Inter", "system-ui", "sans-serif"],
            },
            backgroundImage: {
                "hazard-stripes":
                    "repeating-linear-gradient(45deg, #39FF14 0px, #39FF14 2px, transparent 2px, transparent 20px)",
                "grid-overlay":
                    "linear-gradient(rgba(57,255,20,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(57,255,20,0.03) 1px, transparent 1px)",
                "radial-toxic":
                    "radial-gradient(ellipse at center, rgba(57,255,20,0.15) 0%, transparent 70%)",
                "radial-blood":
                    "radial-gradient(ellipse at center, rgba(139,0,0,0.25) 0%, transparent 70%)",
                "hero-overlay":
                    "linear-gradient(to bottom, rgba(10,10,10,0.3) 0%, rgba(10,10,10,0.6) 50%, rgba(10,10,10,0.95) 100%)",
            },
            boxShadow: {
                "toxic-glow": "0 0 20px rgba(57, 255, 20, 0.6), 0 0 60px rgba(57, 255, 20, 0.2)",
                "toxic-glow-sm": "0 0 8px rgba(57, 255, 20, 0.5)",
                "blood-glow": "0 0 20px rgba(139, 0, 0, 0.7), 0 0 60px rgba(139, 0, 0, 0.3)",
                "blood-glow-sm": "0 0 8px rgba(204, 0, 0, 0.5)",
                "inner-dark": "inset 0 0 80px rgba(0,0,0,0.8)",
            },
            animation: {
                "flicker": "flicker 3s infinite",
                "pulse-toxic": "pulse-toxic 2s ease-in-out infinite",
                "scanline": "scanline 8s linear infinite",
                "float": "float 6s ease-in-out infinite",
                "glitch": "glitch 4s infinite",
                "fade-in-up": "fade-in-up 0.6s ease-out forwards",
                "glow-text": "glow-text 2s ease-in-out infinite alternate",
                "scan": "scan 2s ease-in-out infinite",
                "spin-fast": "spin-fast 4s linear infinite",
                "glitch-text": "glitch-text 0.5s ease-in-out infinite",
            },
            keyframes: {
                flicker: {
                    "0%, 100%": { opacity: "1" },
                    "92%": { opacity: "1" },
                    "93%": { opacity: "0.3" },
                    "94%": { opacity: "1" },
                    "96%": { opacity: "0.5" },
                    "97%": { opacity: "1" },
                },
                "pulse-toxic": {
                    "0%, 100%": {
                        boxShadow: "0 0 5px rgba(57,255,20,0.3), 0 0 20px rgba(57,255,20,0.1)",
                    },
                    "50%": {
                        boxShadow: "0 0 20px rgba(57,255,20,0.8), 0 0 60px rgba(57,255,20,0.3)",
                    },
                },
                scanline: {
                    "0%": { transform: "translateY(-100%)" },
                    "100%": { transform: "translateY(100vh)" },
                },
                float: {
                    "0%, 100%": { transform: "translateY(0px)" },
                    "50%": { transform: "translateY(-12px)" },
                },
                glitch: {
                    "0%, 90%, 100%": { transform: "translate(0)" },
                    "91%": { transform: "translate(-2px, 1px)" },
                    "92%": { transform: "translate(2px, -1px)" },
                    "93%": { transform: "translate(0)" },
                },
                "fade-in-up": {
                    from: { opacity: "0", transform: "translateY(30px)" },
                    to: { opacity: "1", transform: "translateY(0)" },
                },
                "glow-text": {
                    from: { textShadow: "0 0 10px rgba(57,255,20,0.5)" },
                    to: { textShadow: "0 0 30px rgba(57,255,20,1), 0 0 60px rgba(57,255,20,0.5)" },
                },
                "scan": {
                    "0%": { top: "0%", opacity: "1" },
                    "50%": { top: "100%", opacity: "0.5" },
                    "100%": { top: "0%", opacity: "1" },
                },
                "spin-fast": {
                    "0%": { transform: "rotate(0deg)" },
                    "100%": { transform: "rotate(360deg)" },
                },
                "glitch-text": {
                    "0%, 100%": { transform: "translate(0)", opacity: "1" },
                    "20%": { transform: "translate(-2px, 2px)", opacity: "0.8" },
                    "40%": { transform: "translate(2px, -1px)", opacity: "1" },
                    "60%": { transform: "translate(-1px, -1px)", opacity: "0.9" },
                    "80%": { transform: "translate(1px, 1px)", opacity: "1" },
                },
            },
        },
    },
    plugins: [typography],
};

export default config;
