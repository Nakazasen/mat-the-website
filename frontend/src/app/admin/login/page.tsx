'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { Lock, LogIn, AlertTriangle, ArrowLeft, Mail, CheckCircle2 } from 'lucide-react';

export default function AdminLoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [forgotMode, setForgotMode] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const supabase = createAdminClient();
        if (!supabase) {
            setError('Lỗi cấu hình: Thiếu NEXT_PUBLIC_SUPABASE_URL trên Vercel.');
            setLoading(false);
            return;
        }
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

    const handleForgotPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email) {
            setError('Vui lòng nhập email.');
            return;
        }
        setLoading(true);
        setError(null);
        setSuccess(null);

        const supabase = createAdminClient();
        if (!supabase) {
            setError('Lỗi cấu hình.');
            setLoading(false);
            return;
        }

        const { error: resetError } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/admin/login`,
        });

        if (resetError) {
            setError('Không thể gửi email khôi phục. Kiểm tra lại email.');
        } else {
            setSuccess('Đã gửi email khôi phục mật khẩu! Kiểm tra hộp thư (và cả Spam) nhé.');
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4">
            <div className="w-full max-w-sm">
                {/* Logo */}
                <div className="text-center mb-8">
                    <span className="text-6xl">☣</span>
                    <h1 className="mt-3 font-mono text-lg text-green-400 tracking-widest">
                        {forgotMode ? 'KHÔI PHỤC MẬT KHẨU' : 'ADMIN ACCESS'}
                    </h1>
                    <p className="text-gray-600 text-xs font-mono mt-1">
                        MẠT THẾ · SINH HOÁ NGUY CƠ
                    </p>
                </div>

                {forgotMode ? (
                    /* Forgot Password Form */
                    <form
                        onSubmit={handleForgotPassword}
                        className="bg-[#111] border border-gray-800 rounded-lg p-6 space-y-4 shadow-2xl"
                    >
                        {error && (
                            <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-3 text-sm">
                                <AlertTriangle size={14} className="shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}
                        {success && (
                            <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-3 text-sm">
                                <CheckCircle2 size={14} className="shrink-0" />
                                <span>{success}</span>
                            </div>
                        )}

                        <p className="text-xs font-mono text-gray-500 leading-relaxed">
                            Nhập email đã đăng ký. Hệ thống sẽ gửi link khôi phục mật khẩu đến hộp thư của bạn.
                        </p>

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

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex items-center justify-center gap-2 py-2.5 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 font-mono text-sm tracking-widest rounded transition-all"
                        >
                            {loading ? (
                                <span className="animate-pulse">ĐANG GỬI...</span>
                            ) : (
                                <>
                                    <Mail size={14} />
                                    GỬI EMAIL KHÔI PHỤC
                                </>
                            )}
                        </button>

                        <button
                            type="button"
                            onClick={() => { setForgotMode(false); setError(null); setSuccess(null); }}
                            className="w-full flex items-center justify-center gap-2 py-2 text-gray-500 hover:text-gray-300 font-mono text-xs tracking-widest transition-colors"
                        >
                            <ArrowLeft size={12} />
                            QUAY LẠI ĐĂNG NHẬP
                        </button>
                    </form>
                ) : (
                    /* Login Form */
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

                        <div className="flex justify-end">
                            <button
                                type="button"
                                onClick={() => { setForgotMode(true); setError(null); }}
                                className="text-[10px] font-mono text-gray-600 hover:text-green-400 transition-colors tracking-wider"
                            >
                                Quên mật khẩu?
                            </button>
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
                )}

                <p className="text-center text-xs font-mono text-gray-700 mt-4 flex items-center justify-center gap-1">
                    <Lock size={10} />
                    KHU VỰC CẤM ĐỊA · CHỈ ADMIN
                </p>
            </div>
        </div>
    );
}
