import Link from "next/link";
import { NovelSettings } from "@/lib/api";

interface FooterProps {
    novel?: NovelSettings;
}

export default function Footer({ novel }: FooterProps) {
    const novelInfo = novel || {
        author: "Hàn Nhược Tuyết",
        status: "Đang cập nhật",
        genres: ["Mạt Thế", "Zombie"],
    };

    return (
        <footer className="bg-ash-950 border-t border-ash-800 mt-20">
            {/* Hazard divider */}
            <div className="hazard-divider mx-8 mb-0" />

            <div className="max-w-7xl mx-auto px-6 py-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                    {/* Brand */}
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <span className="text-2xl text-toxic-green-DEFAULT">☣</span>
                            <div>
                                <div className="font-biohazard text-lg text-toxic-green-DEFAULT tracking-widest">
                                    MẠT THẾ
                                </div>
                                <div className="font-mono text-[9px] text-ash-500 tracking-[0.3em]">
                                    SINH HOÁ NGUY CƠ
                                </div>
                            </div>
                        </div>
                        <p className="text-ash-400 text-sm leading-relaxed font-reading">
                            Trong bóng tối của ngày tận thế, ý chí con người là ánh sáng
                            cuối cùng. Theo chân {novelInfo.author} trong cuộc chiến sinh tử.
                        </p>
                    </div>

                    {/* Links */}
                    <div>
                        <h3 className="font-biohazard text-sm tracking-widest text-ash-300 mb-4 uppercase">
                            Điều Hướng
                        </h3>
                        <ul className="space-y-2">
                            {[
                                { href: "/", label: "Trang Chủ" },
                                { href: "/chapters", label: "Mục Lục" },
                                { href: "/chapters/1", label: "Chương Đầu" },
                                { href: "/chapters/813", label: "Chương Mới Nhất" },
                            ].map(({ href, label }) => (
                                <li key={href}>
                                    <Link
                                        href={href}
                                        className="text-ash-400 hover:text-toxic-green-DEFAULT text-sm transition-colors flex items-center gap-2 group"
                                    >
                                        <span className="text-toxic-green-DEFAULT/30 group-hover:text-toxic-green-DEFAULT transition-colors">
                                            ›
                                        </span>
                                        {label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Stats */}
                    <div>
                        <h3 className="font-biohazard text-sm tracking-widest text-ash-300 mb-4 uppercase">
                            Thông Tin Truyện
                        </h3>
                        <div className="space-y-3">
                            {[
                                { label: "Tác giả", value: novelInfo.author },
                                { label: "Tình trạng", value: novelInfo.status },
                                { label: "Thể loại", value: novelInfo.genres.join(" · ") },
                                { label: "Số chương", value: "813+ / ~5000" },
                            ].map(({ label, value }) => (
                                <div key={label} className="flex justify-between text-sm gap-4">
                                    <span className="text-ash-500">{label}</span>
                                    <span className="text-ash-300 text-right">{value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="mt-10 pt-6 border-t border-ash-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-ash-600 text-xs font-mono">
                        © 2026 MẠT THẾ ☣ · TẤT CẢ QUYỀN ĐƯỢC BẢO LƯU (v2.2)
                    </p>
                    <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-toxic-green-DEFAULT animate-pulse" />
                        <span className="text-xs font-mono text-ash-500">ONLINE</span>
                    </div>
                </div>
            </div>
        </footer>
    );
}
