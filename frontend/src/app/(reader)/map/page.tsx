'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'leaflet/dist/leaflet.css';
import { Shield, Skull, Flag, MapPin, Landmark, Loader2, AlertTriangle, ArrowLeft, Maximize2, ExternalLink } from 'lucide-react';
import Link from 'next/link';
import { getMapLocations, type MapLocation } from '@/lib/api';

// Dynamic imports for Leaflet
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });
const ImageOverlay = dynamic(() => import('react-leaflet').then(mod => mod.ImageOverlay), { ssr: false });

// Fix for default marker icons
if (typeof window !== 'undefined') {
    const L = require('leaflet');
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    });
}

const TYPE_CONFIG = {
    safe_zone: { icon: Shield, color: 'text-toxic-green-DEFAULT', label: 'VÙNG AN TOÀN', bg: 'bg-green-500/10', border: 'border-green-500/30' },
    danger_zone: { icon: Skull, color: 'text-blood-glow', label: 'Ổ DỊCH (NGUY HIỂM)', bg: 'bg-red-500/10', border: 'border-red-500/30' },
    neutral: { icon: Flag, color: 'text-blue-400', label: 'KHU TRUNG LẬP', bg: 'bg-blue-500/10', border: 'border-blue-500/30' },
    outpost: { icon: MapPin, color: 'text-yellow-500', label: 'TRẠM TIỀN TIÊU', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
    ruins: { icon: Landmark, color: 'text-gray-400', label: 'TÀN TÍCH', bg: 'bg-gray-500/10', border: 'border-gray-500/30' },
    system_map: { icon: MapPin, color: 'text-emerald-400', label: 'BẢN ĐỒ HỆ THỐNG', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30' },
};

export default function ReaderMapPage() {
    const [locations, setLocations] = useState<MapLocation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchMap = async () => {
            try {
                const data = await getMapLocations();
                setLocations(data);
            } catch (err) {
                setError("Tín hiệu vệ tinh bị gián đoạn. Không thể tải bản đồ.");
            } finally {
                setLoading(false);
            }
        };
        fetchMap();
    }, []);

    // Find custom background map
    const systemMapLocation = locations.find(l => l.type === 'system_map' && l.image_url);
    const MAP_BOUNDS: [number, number][] = [[8, 100], [24, 110]]; // Fixed bounds covering Vietnam area

    if (loading) {
        return (
            <div className="fixed inset-0 bg-[#070707] flex flex-col items-center justify-center gap-4 z-[100]">
                <Loader2 className="animate-spin text-toxic-green-DEFAULT" size={40} />
                <div className="font-mono text-xs text-ash-500 tracking-[0.5em] uppercase animate-pulse">
                    Đang thiết lập kết nối vệ tinh...
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-ash-950 flex flex-col pt-16 z-40">
            {/* Header / HUD Overlay */}
            <div className="absolute top-20 left-6 z-[1000] pointer-events-none">
                <div className="bg-ash-900/80 backdrop-blur-md border border-toxic-green-DEFAULT/20 p-4 hazard-corner pointer-events-auto max-w-xs shadow-2xl">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="relative flex">
                            <div className="w-3 h-3 rounded-full bg-toxic-green-DEFAULT animate-pulse" />
                            <div className="absolute inset-0 w-3 h-3 rounded-full bg-toxic-green-DEFAULT animate-ping opacity-50" />
                        </div>
                        <h1 className="font-biohazard text-xl text-worn-white tracking-widest uppercase">BẢN ĐỒ CHIẾN SỰ</h1>
                    </div>
                    <p className="text-[10px] font-mono text-ash-400 leading-relaxed uppercase tracking-tighter">
                        Cập nhật thời gian thực từ vệ tinh Recon-9. Click vào các điểm đánh dấu để xem chi tiết tình hình khu vực.
                    </p>
                    <div className="mt-4 flex flex-wrap gap-2">
                        {Object.entries(TYPE_CONFIG).filter(([key]) => key !== 'system_map').map(([key, config]) => (
                            <div key={key} className="flex items-center gap-1.5 bg-black/40 px-2 py-1 rounded border border-ash-800 text-[8px] font-mono text-ash-500">
                                <config.icon size={8} className={config.color} />
                                {config.label}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Map Container */}
            <div className="flex-1 w-full h-full relative">
                <MapContainer
                    center={[16, 106] as any}
                    zoom={6}
                    className="h-full w-full grayscale-[0.2] contrast-[1.2] invert-0"
                    zoomControl={false}
                >
                    <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; CARTO'
                        opacity={systemMapLocation ? 0.3 : 1}
                    />

                    {systemMapLocation && (
                        <ImageOverlay
                            url={systemMapLocation.image_url!}
                            bounds={MAP_BOUNDS as any}
                            zIndex={10}
                        />
                    )}

                    {locations.filter(l => l.type !== 'system_map').map(loc => {
                        const config = TYPE_CONFIG[loc.type as keyof typeof TYPE_CONFIG] || TYPE_CONFIG.neutral;
                        return (
                            <Marker key={loc.id} position={[loc.lat, loc.lng] as any}>
                                <Popup className="map-popup">
                                    <div className="w-64 bg-ash-900 overflow-hidden rounded-lg border border-ash-800 shadow-2xl">
                                        {loc.image_url && (
                                            <div className="aspect-video w-full overflow-hidden">
                                                <img src={loc.image_url} alt={loc.name} className="w-full h-full object-cover" />
                                            </div>
                                        )}
                                        <div className="p-4 bg-ash-900">
                                            <div className={`text-[8px] font-mono mb-1 inline-block px-1.5 py-0.5 rounded border ${config.bg} ${config.color} ${config.border}`}>
                                                {config.label}
                                            </div>
                                            <h3 className="text-sm font-bold text-white mb-2 uppercase tracking-wide">{loc.name}</h3>
                                            <div
                                                className="text-[10px] text-ash-400 leading-relaxed italic mb-0 rich-text-content"
                                                dangerouslySetInnerHTML={{ __html: loc.description || "Chưa có dữ liệu chi tiết về khu vực này." }}
                                            />
                                        </div>
                                    </div>
                                </Popup>
                            </Marker>
                        );
                    })}
                </MapContainer>

                {/* Aesthetic Vignette */}
                <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_150px_rgba(0,0,0,0.8)] z-[999]" />
            </div>

            {/* Controls HUD */}
            <div className="absolute bottom-6 left-6 z-[1000] flex gap-3">
                <Link href="/" className="bg-ash-900/80 hover:bg-ash-800 backdrop-blur-md border border-ash-700 p-3 rounded flex items-center gap-2 group transition-all">
                    <ArrowLeft size={16} className="text-ash-400 group-hover:text-toxic-green-DEFAULT" />
                    <span className="text-[10px] font-mono text-ash-300 uppercase tracking-widest">Rời khỏi bản đồ</span>
                </Link>
            </div>

            <style jsx global>{`
                .leaflet-tile {
                    outline: 1px solid transparent;
                    -webkit-backface-visibility: hidden;
                }
                .leaflet-container {
                    background: #070707 !important;
                }
                .leaflet-popup-content-wrapper {
                    background: transparent !important;
                    padding: 0 !important;
                    box-shadow: none !important;
                }
                .leaflet-popup-content {
                    margin: 0 !important;
                    width: auto !important;
                }
                .leaflet-popup-tip {
                    background: #1a1a1a !important;
                }
                .map-popup .leaflet-popup-close-button {
                    color: white !important;
                    top: 10px !important;
                    right: 10px !important;
                    z-index: 10;
                }
            `}</style>
        </div>
    );
}
