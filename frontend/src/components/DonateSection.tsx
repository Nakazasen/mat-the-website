"use client";

import { useState } from "react";
import { Coffee, Heart, X, QrCode } from "lucide-react";

interface DonateSectionProps {
    chapterNumber: number;
}

export default function DonateSection({ chapterNumber }: DonateSectionProps) {
    const [showQR, setShowQR] = useState(false);

    // QR image URL - sẽ được thay bằng link R2 thật khi anh upload
    const qrImageUrl = process.env.NEXT_PUBLIC_DONATE_QR_URL || "";

    return (
        <>
            {/* Donate trigger button */}
            <div className="flex justify-center py-6">
                <button
                    onClick={() => setShowQR(true)}
                    className="group relative flex items-center gap-3 px-6 py-3 
                        bg-gradient-to-r from-amber-900/20 via-amber-800/10 to-amber-900/20
                        border border-amber-700/30 rounded-xl
                        hover:border-amber-500/50 hover:from-amber-900/30 hover:via-amber-800/20 hover:to-amber-900/30
                        transition-all duration-300"
                >
                    <Coffee size={18} className="text-amber-400 group-hover:rotate-12 transition-transform" />
                    <span className="font-mono text-xs text-amber-300/80 tracking-wider">
                        Tiếp tế đạn dược và cafe cho tác giả ☕
                    </span>
                    <Heart size={14} className="text-red-400/60 group-hover:text-red-400 group-hover:scale-125 transition-all" />
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
