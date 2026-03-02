"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
import { getNovelSettings, type NovelSettings } from "@/lib/api";

interface NovelContextType {
    novel: NovelSettings | null;
    loading: boolean;
    refreshNovel: () => void;
}

const NovelContext = createContext<NovelContextType | undefined>(undefined);

export function NovelProvider({ children }: { children: React.ReactNode }) {
    const [novel, setNovel] = useState<NovelSettings | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchNovel = async () => {
        try {
            setLoading(true);
            const data = await getNovelSettings();
            setNovel(data);
        } catch (error) {
            console.error("Failed to fetch novel settings:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNovel();
    }, []);

    return (
        <NovelContext.Provider value={{ novel, loading, refreshNovel: fetchNovel }}>
            {children}
        </NovelContext.Provider>
    );
}

export function useNovel() {
    const context = useContext(NovelContext);
    if (context === undefined) {
        throw new Error("useNovel must be used within a NovelProvider");
    }
    return context;
}
