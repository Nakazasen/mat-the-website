"use client";

import { useState } from "react";
import { Coffee, Heart, X, QrCode } from "lucide-react";
import { useTheme } from "@/context/ThemeContext";
import { useNovel } from "@/context/NovelContext";

interface DonateSectionProps {
    chapterNumber: number;
}

export default function DonateSection({ chapterNumber }: DonateSectionProps) {
    const { theme } = useTheme();
    const { novel } = useNovel();
    const [showQR, setShowQR] = useState(false);

    // QR image URL - ưu tiên lấy từ Database, nếu không có thì lấy từ môi trường
    const qrImageUrl = novel?.donate_qr_url || process.env.NEXT_PUBLIC_DONATE_QR_URL || "";

    return (
        <>
            {/* Donate trigger button */}
            <div className="flex justify-center py-6">
                <button
                    onClick={() => setShowQR(true)}
                    className={`group relative flex items-center gap-3 px-6 py-3 
                        border rounded-xl transition-all duration-300
                        ${theme === 'dark'
                            ? 'bg-gradient-to-r from-amber-900/20 via-amber-800/10 to-amber-900/20 border-amber-700/30 hover:border-amber-500/50 hover:from-amber-900/30 hover:via-amber-800/20 hover:to-amber-900/30'
                            : theme === 'sepia'
                                ? 'bg-amber-100/50 border-amber-200 hover:border-amber-400 hover:bg-amber-100'
                                : 'bg-amber-50 border-amber-200 hover:border-amber-400 hover:bg-amber-100'
                        }`}
                >
                    <Coffee size={18} className={`${theme === 'dark' ? 'text-amber-400' : 'text-amber-600'} group-hover:rotate-12 transition-transform`} />
                    <span className={`font-mono text-xs tracking-wider ${theme === 'dark' ? 'text-amber-300/80' : 'text-amber-900 font-bold'}`}>
                        Tiếp tế đan dược và cafe cho tác giả ☕
                    </span>
                    <Heart size={14} className={`${theme === 'dark' ? 'text-red-400/60 group-hover:text-red-400' : 'text-red-600 group-hover:text-red-500'} group-hover:scale-125 transition-all outline-none`} />
                </button>
            </div>

            {/* QR Modal */}
            {showQR && (
                <div
                    className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
                    onClick={() => setShowQR(false)}
                >
                    <div
                        className="relative bg-[#1a1a1a] border border-amber-800/40 rounded-2xl p-6 max-w-sm w-full shadow-2xl"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <button
                            onClick={() => setShowQR(false)}
                            className="absolute top-3 right-3 text-gray-500 hover:text-gray-300 transition-colors"
                        >
                            <X size={18} />
                        </button>

                        <div className="text-center">
                            {/* Header */}
                            <div className="flex items-center justify-center gap-2 mb-1">
                                <Coffee className="text-amber-400" size={20} />
                                <h3 className="font-biohazard text-lg text-amber-300 tracking-wider">
                                    ỦNG HỘ TÁC GIẢ
                                </h3>
                            </div>
                            <p className="text-xs font-mono text-gray-500 mb-4">
                                Mỗi ly cafe giúp tác giả thức thêm một đêm viết truyện ☣️
                            </p>

                            {/* QR Code */}
                            {qrImageUrl ? (
                                <div className="bg-white rounded-xl p-3 mx-auto w-fit mb-4">
                                    <img
                                        src={qrImageUrl}
                                        alt="Mã QR ủng hộ"
                                        className="w-48 h-48 object-contain"
                                    />
                                </div>
                            ) : (
                                <div className="bg-[#0d0d0d] border border-dashed border-gray-700 rounded-xl p-8 mx-auto mb-4 flex flex-col items-center gap-2">
                                    <QrCode size={48} className="text-gray-700" />
                                    <p className="text-[10px] font-mono text-gray-700">
                                        Mã QR sẽ sớm được cập nhật
                                    </p>
                                </div>
                            )}

                            <p className="text-xs font-mono text-amber-400/70 mb-2">
                                Quét mã bằng MoMo, ZaloPay hoặc App ngân hàng
                            </p>

                            <div className="mt-3 pt-3 border-t border-gray-800">
                                <p className="text-[10px] font-mono text-gray-600 italic">
                                    &ldquo;Trong thế giới mạt thế, sự ủng hộ của bạn là nguồn sống của tác giả&rdquo;
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
