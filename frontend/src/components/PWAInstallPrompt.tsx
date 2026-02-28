'use client';

import { useEffect, useState } from 'react';
import { Download, X } from 'lucide-react';

export default function PWAInstallPrompt() {
    const [installPrompt, setInstallPrompt] = useState<any>(null);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const handler = (e: any) => {
            // Ngăn trình duyệt hiện prompt mặc định ngay lập tức
            e.preventDefault();
            // Lưu lại event để dùng sau
            setInstallPrompt(e);

            // Chỉ hiện sau 5 giây để không gây phiền phức ngay khi vào web
            const timer = setTimeout(() => {
                // Kiểm tra xem đã ở chế độ standalone chưa
                const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
                if (!isStandalone) {
                    setIsVisible(true);
                }
            }, 5000);

            return () => clearTimeout(timer);
        };

        window.addEventListener('beforeinstallprompt', handler);

        return () => window.removeEventListener('beforeinstallprompt', handler);
    }, []);

    const handleInstallClick = async () => {
        if (!installPrompt) return;

        // Hiện prompt của trình duyệt
        installPrompt.prompt();

        // Chờ người dùng phản hồi
        const { outcome } = await installPrompt.userChoice;
        if (outcome === 'accepted') {
            console.log('User accepted the PWA install');
            setIsVisible(false);
        }
        setInstallPrompt(null);
    };

    if (!isVisible) return null;

    return (
        <div className="fixed bottom-4 left-4 right-4 z-[100] md:left-auto md:right-6 md:w-80">
            <div className="relative overflow-hidden rounded-xl border border-toxic-green-DEFAULT/30 bg-[#1a1a1a] p-4 shadow-2xl shadow-black/50 ring-1 ring-white/10 animate-in fade-in slide-in-from-bottom-5 duration-500">
                {/* Nền gradient nhẹ */}
                <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-toxic-green-DEFAULT/5 blur-2xl" />

                <button
                    onClick={() => setIsVisible(false)}
                    className="absolute right-2 top-2 p-1 text-gray-500 hover:text-white transition-colors"
                >
                    <X size={16} />
                </button>

                <div className="flex items-start gap-4">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-toxic-green-DEFAULT/10 border border-toxic-green-DEFAULT/20">
                        <Download className="text-toxic-green-DEFAULT" size={24} />
                    </div>

                    <div className="flex-1 pr-4">
                        <h3 className="font-biohazard text-sm tracking-widest text-toxic-green-DEFAULT">
                            CÀI ĐẶT APP ☣️
                        </h3>
                        <p className="mt-1 text-xs leading-relaxed text-gray-400">
                            Cài đặt ứng dụng để nghe audio mượt hơn trên màn hình khóa.
                        </p>

                        <button
                            onClick={handleInstallClick}
                            className="mt-3 flex w-full items-center justify-center rounded-lg bg-toxic-green-DEFAULT px-3 py-2 text-xs font-bold text-black hover:bg-toxic-green-light transition-colors"
                        >
                            CÀI ĐẶT NGAY
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
