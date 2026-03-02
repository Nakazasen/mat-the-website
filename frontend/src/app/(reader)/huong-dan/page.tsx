"use client";

import { useEffect, useState } from "react";
import { BookOpen, HelpCircle, Map, Heart, MessageSquare, Search } from "lucide-react";
import { getPublicGuide } from "@/lib/api";

export default function HuongDanPage() {
    const [guide, setGuide] = useState<{ title: string; content: string } | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getPublicGuide("reader-guide")
            .then(setGuide)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const hasCustomContent = guide?.content && guide.content.trim().length > 10;

    return (
        <div className="min-h-screen bg-[var(--reader-bg)] text-[var(--reader-text)]">
            {/* Hero */}
            <div className="relative py-16 sm:py-20 overflow-hidden">
                <div className="absolute inset-0 bg-grid-overlay opacity-30" />
                <div className="absolute inset-0 bg-radial-toxic" />
                <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
                    <div className="inline-flex items-center gap-2 bg-toxic-green-DEFAULT/10 px-4 py-1.5 rounded-full border border-toxic-green-DEFAULT/20 mb-6">
                        <HelpCircle size={14} className="text-toxic-green-DEFAULT" />
                        <span className="font-mono text-[10px] text-toxic-green-DEFAULT tracking-[0.3em]">CẨM NANG SINH TỒN</span>
                    </div>
                    <h1 className="font-biohazard text-4xl sm:text-5xl tracking-wider text-[var(--reader-text)] mb-4">
                        {guide?.title || "HƯỚNG DẪN SỬ DỤNG"}
                    </h1>
                    <p className="text-[var(--reader-muted,#737373)] font-mono text-xs tracking-wider max-w-xl mx-auto">
                        Tất cả những gì bạn cần biết để khám phá thế giới Mạt Thế một cách trọn vẹn nhất
                    </p>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-4xl mx-auto px-4 pb-20">
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-6 h-6 border-2 border-toxic-green-DEFAULT border-t-transparent rounded-full animate-spin" />
                            <span className="text-[var(--reader-muted,#737373)] text-xs font-mono">ĐANG TẢI...</span>
                        </div>
                    </div>
                ) : hasCustomContent ? (
                    <div
                        className="prose prose-invert prose-emerald max-w-none 
                            prose-headings:font-biohazard prose-headings:tracking-wider prose-headings:text-toxic-green-DEFAULT
                            prose-p:text-[var(--reader-text)] prose-p:leading-relaxed
                            prose-a:text-toxic-green-DEFAULT prose-a:no-underline hover:prose-a:underline
                            prose-strong:text-[var(--reader-text)]
                            prose-img:rounded-lg prose-img:border prose-img:border-ash-800/30"
                        dangerouslySetInnerHTML={{ __html: guide!.content }}
                    />
                ) : (
                    /* Default guide content when admin hasn't written anything yet */
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {[
                            {
                                icon: BookOpen,
                                title: "ĐỌC TRUYỆN",
                                items: [
                                    "Vào MỤC LỤC để xem danh sách tất cả các chương",
                                    "Click vào bất kỳ chương nào để bắt đầu đọc",
                                    "Dùng nút ← → hoặc phím mũi tên để chuyển chương",
                                    "Click biểu tượng ⚙️ để đổi Font, Cỡ chữ, Nền đọc",
                                    "Web tự nhớ chương bạn đọc dở, lần sau vào sẽ thấy nút Tiếp tục",
                                ],
                            },
                            {
                                icon: Search,
                                title: "BÁCH KHOA TOÀN THƯ",
                                items: [
                                    "Truy cập trang BÁCH KHOA từ menu trên",
                                    "Tra cứu thông tin về Nhân vật, Zombie, Thế lực...",
                                    "Dùng thanh TÌM KIẾM để tìm nhanh",
                                    "Click vào mục bất kỳ để xem chi tiết đầy đủ",
                                ],
                            },
                            {
                                icon: Heart,
                                title: "THẢ TIM ❤️",
                                items: [
                                    "Cuối mỗi chương có nút ❤️ THẢ TIM",
                                    "Click để ủng hộ tác giả (không cần đăng nhập)",
                                    "Mỗi chương chỉ thả tim 1 lần",
                                ],
                            },
                            {
                                icon: MessageSquare,
                                title: "BÌNH LUẬN",
                                items: [
                                    "Kéo xuống cuối mỗi chương để xem và viết bình luận",
                                    "Nhập tên hoặc để trống (sẽ hiện 'Ẩn danh')",
                                    "Viết cảm nghĩ và nhấn ĐĂNG BÌNH LUẬN",
                                ],
                            },
                            {
                                icon: Map,
                                title: "BẢN ĐỒ CHIẾN SỰ",
                                items: [
                                    "Vào BẢN ĐỒ từ menu để xem bản đồ tương tác",
                                    "Phóng to / Thu nhỏ bằng chuột hoặc nút +/−",
                                    "Click vào các điểm ghim để xem chi tiết vùng đất",
                                ],
                            },
                            {
                                icon: HelpCircle,
                                title: "MẸO HAY",
                                items: [
                                    "Cài ứng dụng PWA để đọc offline (nhấn 'Cài đặt' trên trình duyệt)",
                                    "Dùng phím ← → trên bàn phím để chuyển chương nhanh",
                                    "Bật Chế độ Tối để đọc ban đêm không mỏi mắt",
                                ],
                            },
                        ].map((section) => (
                            <div
                                key={section.title}
                                className="card-biohazard rounded-lg p-6 group"
                            >
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="w-10 h-10 rounded bg-toxic-green-DEFAULT/10 flex items-center justify-center border border-toxic-green-DEFAULT/20">
                                        <section.icon size={18} className="text-toxic-green-DEFAULT" />
                                    </div>
                                    <h3 className="font-biohazard text-lg tracking-wider text-[var(--reader-text)]">
                                        {section.title}
                                    </h3>
                                </div>
                                <ul className="space-y-2.5">
                                    {section.items.map((item, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-[var(--reader-muted,#a0a0a0)]">
                                            <span className="text-toxic-green-DEFAULT/60 mt-1 text-xs">▸</span>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
