'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { Lock, LogIn, AlertTriangle } from 'lucide-react';

export default function AdminLoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const supabase = createAdminClient();
        const { error: authError } = await supabase.auth.signInWithPassword({
            email,
            password,
        });

        if (authError) {
            setError('Email hoặc mật khẩu không đúng. Thử lại đi!');
            setLoading(false);
            return;
        }

        router.push('/admin');
        router.refresh();
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4">
            <div className="w-full max-w-sm">
                {/* Logo */}
                <div className="text-center mb-8">
                    <span className="text-6xl">☣</span>
                    <h1 className="mt-3 font-mono text-lg text-green-400 tracking-widest">
                        ADMIN ACCESS
                    </h1>
                    <p className="text-gray-600 text-xs font-mono mt-1">
                        MẠT THẾ · SINH HOÁ NGUY CƠ
                    </p>
                </div>

                {/* Form */}
                <form
                    onSubmit={handleLogin}
                    className="bg-[#111] border border-gray-800 rounded-lg p-6 space-y-4 shadow-2xl"
                >
                    {error && (
                        <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-3 text-sm">
                            <AlertTriangle size={14} className="shrink-0" />
                            <span>{error}</span>
                        </div>
                    )}

                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">
                            EMAIL
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            autoComplete="email"
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                            placeholder="admin@example.com"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-mono text-gray-500 mb-1 tracking-widest">
                            MẬT KHẨU
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            autoComplete="current-password"
                            className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-green-500 transition-colors"
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full flex items-center justify-center gap-2 py-2.5 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 font-mono text-sm tracking-widest rounded transition-all"
                    >
                        {loading ? (
                            <span className="animate-pulse">ĐANG XÁC THỰC...</span>
                        ) : (
                            <>
                                <LogIn size={14} />
                                ĐĂNG NHẬP
                            </>
                        )}
                    </button>
                </form>

                <p className="text-center text-xs font-mono text-gray-700 mt-4 flex items-center justify-center gap-1">
                    <Lock size={10} />
                    KHU VỰC CẤM ĐỊA · CHỈ ADMIN
                </p>
            </div>
        </div>
    );
}
