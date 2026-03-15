'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'leaflet/dist/leaflet.css';
import { MapPin, Shield, Skull, Flag, Landmark, Trash2, Save, Plus, Loader2, AlertTriangle, CheckCircle2, Image as ImageIcon, Map as MapIcon } from 'lucide-react';
import { createAdminClient } from '@/lib/supabase-admin';
import { getMapLocations, createMapLocation, updateMapLocation, deleteMapLocation, uploadImageR2, type MapLocation, type AdminMapLocationIn } from '@/lib/api';

// Dynamically import Leaflet components to avoid SSR issues
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });
const ImageOverlay = dynamic(() => import('react-leaflet').then(mod => mod.ImageOverlay), { ssr: false });

// Fix for default marker icons in Leaflet + Next.js
if (typeof window !== 'undefined') {
    const L = require('leaflet');
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    });
}

const LOCATION_TYPES = [
    { value: 'safe_zone', label: 'Vùng An Toàn', icon: Shield, color: 'text-green-500' },
    { value: 'danger_zone', label: 'Ổ Dịch (Nguy Hiểm)', icon: Skull, color: 'text-red-500' },
    { value: 'neutral', label: 'Trung Lập', icon: Flag, color: 'text-blue-500' },
    { value: 'outpost', label: 'Trạm Tiền Tiêu', icon: MapPin, color: 'text-yellow-500' },
    { value: 'ruins', label: 'Tàn Tích', icon: Landmark, color: 'text-gray-500' },
    { value: 'system_map', label: 'Bản Đồ Hệ Thống', icon: MapIcon, color: 'text-emerald-400' },
];

// Function to create custom DivIcon based on location type
const createCustomIcon = (type: string) => {
    if (typeof window === 'undefined') return null;
    const L = require('leaflet');
    
    let bgClass = 'bg-blue-500';
    let ringClass = 'ring-blue-500/50';

    if (type === 'safe_zone') { bgClass = 'bg-green-500'; ringClass = 'ring-green-500/50'; }
    else if (type === 'danger_zone') { bgClass = 'bg-red-500'; ringClass = 'ring-red-500/50'; }
    else if (type === 'outpost') { bgClass = 'bg-yellow-500'; ringClass = 'ring-yellow-500/50'; }
    else if (type === 'ruins') { bgClass = 'bg-gray-500'; ringClass = 'ring-gray-500/50'; }
    else if (type === 'system_map') { bgClass = 'bg-emerald-400'; ringClass = 'ring-emerald-400/50'; }

    const html = `
        <div class="relative flex items-center justify-center w-8 h-8">
            <div class="absolute inset-0 rounded-full ${bgClass} opacity-20 animate-ping"></div>
            <div class="relative w-4 h-4 rounded-full ${bgClass} ring-4 ${ringClass} shadow-lg border-2 border-[#0d0d0d]"></div>
        </div>
    `;

    return L.divIcon({
        html,
        className: 'custom-leaflet-icon',
        iconSize: [32, 32],
        iconAnchor: [16, 16], 
        popupAnchor: [0, -16]
    });
};

const MapEvents = ({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) => {
    const { useMapEvents } = require('react-leaflet');
    useMapEvents({
        click(e: { latlng: { lat: number, lng: number } }) {
            onMapClick(e.latlng.lat, e.latlng.lng);
        },
    });
    return null;
};

export default function AdminMapPage() {
    const [locations, setLocations] = useState<MapLocation[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [token, setToken] = useState<string | null>(null);

    const [selectedLocation, setSelectedLocation] = useState<MapLocation | null>(null);
    const [formData, setFormData] = useState<AdminMapLocationIn>({
        name: '',
        type: 'neutral',
        description: '',
        lat: 10.762622, 
        lng: 106.660172,
        image_url: ''
    });

    useEffect(() => {
        const init = async () => {
            const supabase = createAdminClient();
            if (!supabase) return;
            const { data: { session } } = await supabase.auth.getSession();
            if (session) setToken(session.access_token);
            else setToken(process.env.NEXT_PUBLIC_ADMIN_TOKEN || "mat-the-admin-2026");

            try {
                const data = await getMapLocations();
                setLocations(data);
            } catch (err) {
                setError("Lỗi tải dữ liệu bản đồ.");
            } finally {
                setLoading(false);
            }
        };
        init();
    }, []);

    const systemMapLocation = locations.find(l => (l.type as any) === 'system_map' && l.image_url);
    const MAP_BOUNDS: [number, number][] = [[0, 90], [27, 138]]; // 16:9 aspect ratio bounds covering SEA

    const handleMapClick = (lat: number, lng: number) => {
        setFormData(prev => ({ ...prev, lat, lng }));
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;
        setSaving(true);
        setError(null);
        setSuccess(null);

        try {
            if (selectedLocation) {
                const updated = await updateMapLocation(selectedLocation.id, formData, token);
                setLocations(prev => prev.map(l => l.id === updated.id ? updated : l));
                setSuccess("Đã cập nhật điểm đánh dấu!");
            } else {
                const created = await createMapLocation(formData, token);
                setLocations(prev => [created, ...prev]);
                setSuccess("Đã thêm điểm mới lên bản đồ!");
                setFormData({ name: '', type: 'neutral', description: '', lat: 10.762622, lng: 106.660172, image_url: '' });
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!token || !confirm("Xoá điểm này khỏi bản đồ?")) return;
        try {
            await deleteMapLocation(id, token);
            setLocations(prev => prev.filter(l => l.id !== id));
            if (selectedLocation?.id === id) {
                setSelectedLocation(null);
                setFormData({ name: '', type: 'neutral', description: '', lat: 10.762622, lng: 106.660172, image_url: '' });
            }
            setSuccess("Đã xoá điểm đánh dấu.");
        } catch (err) {
            setError("Lỗi khi xoá.");
        }
    };

    const handleImageFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || !token) return;
        setSaving(true);
        try {
            const url = await uploadImageR2(file, token);
            setFormData(prev => ({ ...prev, image_url: url }));
            setSuccess("Đã tải ảnh lên thành công!");
        } catch (err: any) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500 font-mono">Đang khởi tạo bản đồ...</div>;

    return (
        <div className="max-w-7xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-mono text-gray-100 flex items-center gap-3">
                    <MapIcon className="text-green-500" />
                    BẢN ĐỒ CHIẾN SỰ
                </h1>
                <p className="text-gray-500 text-sm font-mono mt-1">Cắm gờ các vùng an toàn và ổ xác sống trên toàn cầu.</p>
            </div>

            {success && <div className="bg-green-950/20 border border-green-800 text-green-400 p-4 rounded mb-6 text-sm flex items-center gap-2"><CheckCircle2 size={16} />{success}</div>}
            {error && <div className="bg-red-950/20 border border-red-800 text-red-400 p-4 rounded mb-6 text-sm flex items-center gap-2"><AlertTriangle size={16} />{error}</div>}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                    <div className="h-[600px] rounded-lg border border-gray-800 overflow-hidden relative group">
                        <MapContainer 
                            center={[16, 106] as any} 
                            zoom={6} 
                            className="h-full w-full bg-[#0d0d0d]"
                        >
                            <TileLayer
                                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                                attribution='&copy; OpenStreetMap &copy; CARTO'
                                opacity={systemMapLocation ? 0.3 : 1}
                            />
                            
                            {systemMapLocation && (
                                <ImageOverlay
                                    url={systemMapLocation.image_url!}
                                    bounds={MAP_BOUNDS as any}
                                    zIndex={10}
                                />
                            )}

                            <MapEvents onMapClick={handleMapClick} />
                            
                            <Marker
                                position={[formData.lat, formData.lng] as any}
                                icon={createCustomIcon(formData.type)}
                                zIndexOffset={1000}
                            >
                                <Popup>Điểm đang chọn</Popup>
                            </Marker>

                            {locations.map(loc => (
                                <Marker
                                    key={loc.id}
                                    position={[loc.lat, loc.lng] as any}
                                    icon={createCustomIcon(loc.type)}
                                    eventHandlers={{
                                        click: () => {
                                            setSelectedLocation(loc);
                                            setFormData({
                                                name: loc.name,
                                                type: loc.type,
                                                description: loc.description || '',
                                                lat: loc.lat,
                                                lng: loc.lng,
                                                image_url: loc.image_url || ''
                                            });
                                        }
                                    }}
                                >
                                    <Popup>
                                        <div className="text-dark p-1">
                                            <div className="font-bold border-b mb-1">{loc.name}</div>
                                            <div className="text-[10px] uppercase font-mono">{LOCATION_TYPES.find(t => t.value === loc.type)?.label || loc.type}</div>
                                            {loc.description && <div className="text-xs mt-1 text-gray-600 line-clamp-2 max-w-[150px]">{loc.description}</div>}
                                        </div>
                                    </Popup>
                                </Marker>
                            ))}
                        </MapContainer>

                        <style jsx global>{`
                            .leaflet-tile {
                                outline: 1px solid transparent;
                                -webkit-backface-visibility: hidden;
                            }
                            .leaflet-container {
                                background: #0d0d0d !important;
                            }
                            .custom-leaflet-icon {
                                background: transparent !important;
                                border: none !important;
                            }
                        `}</style>
                        
                        <div className="absolute bottom-4 left-4 z-[1000] bg-black/80 p-2 border border-gray-700 rounded text-[10px] font-mono text-gray-400">
                            COORD: {formData.lat.toFixed(6)}, {formData.lng.toFixed(6)}
                            <div className="text-green-500 mt-1">TIP: Click lên bản đồ để lấy tọa độ mới</div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <form onSubmit={handleSave} className="bg-[#181818] border border-gray-800 rounded-lg p-6 hazard-corner">
                        <div className="flex items-center justify-between mb-6 border-b border-gray-800 pb-3">
                            <h2 className="text-sm font-mono text-gray-200 uppercase tracking-widest flex items-center gap-2">
                                {selectedLocation ? <Save size={16} /> : <Plus size={16} />}
                                {selectedLocation ? "Cập Nhật Điểm" : "Thêm Điểm Mới"}
                            </h2>
                            {selectedLocation && (
                                <button
                                    type="button"
                                    onClick={() => { setSelectedLocation(null); setFormData({ name: '', type: 'neutral', description: '', lat: 10.762622, lng: 106.660172, image_url: '' }); }}
                                    className="text-[10px] text-gray-500 hover:text-white uppercase font-mono"
                                >
                                    Hủy
                                </button>
                            )}
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">Tên Địa Điểm</label>
                                <input
                                    type="text" required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-100 text-sm focus:border-green-500 outline-none"
                                    placeholder="VD: Căn Cứ Hi Vọng"
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">Loại Hình</label>
                                <div className="grid grid-cols-1 gap-2">
                                    {LOCATION_TYPES.map(t => (
                                        <button
                                            key={t.value}
                                            type="button"
                                            onClick={() => setFormData({ ...formData, type: t.value as any })}
                                            className={`flex items-center gap-3 p-3 rounded border text-xs font-mono transition-all ${formData.type === t.value
                                                ? 'bg-gray-800 border-green-500 text-white'
                                                : 'bg-[#0a0a0a] border-gray-800 text-gray-500 hover:border-gray-700'
                                                }`}
                                        >
                                            <t.icon className={t.color} size={14} />
                                            {t.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">Mô Tả Khu Vực</label>
                                <textarea
                                    rows={3}
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-100 text-sm focus:border-green-500 outline-none resize-none"
                                    placeholder="Nơi trú ẩn an toàn nhất..."
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">Ảnh Minh Họa / Bản Đồ</label>
                                {formData.image_url && (
                                    <div className="relative aspect-video rounded border border-gray-800 overflow-hidden mb-2">
                                        <img src={formData.image_url} alt="Preview" className="w-full h-full object-cover" />
                                        <button
                                            type="button" onClick={() => setFormData({ ...formData, image_url: '' })}
                                            className="absolute top-1 right-1 bg-black/60 p-1 rounded text-red-500 hover:text-red-400"
                                        >
                                            <Trash2 size={12} />
                                        </button>
                                    </div>
                                )}
                                <div className="relative group">
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleImageFileChange}
                                        className="hidden"
                                        id="map-image-upload"
                                    />
                                    <label
                                        htmlFor="map-image-upload"
                                        className="flex flex-col items-center justify-center py-4 border-2 border-dashed border-gray-800 rounded group-hover:border-green-500/50 cursor-pointer transition-all"
                                    >
                                        <ImageIcon size={20} className="text-gray-600 group-hover:text-green-500" />
                                        <span className="text-[10px] text-gray-500 mt-2 uppercase tracking-tighter">Click để tải ảnh lên R2</span>
                                    </label>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={saving}
                                className="w-full py-4 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 text-white font-mono text-sm tracking-[0.2em] font-bold rounded transition-all uppercase flex items-center justify-center gap-2"
                            >
                                {saving ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />}
                                {saving ? "ĐANG XỬ LÝ..." : (selectedLocation ? "CẬP NHẬT" : "LƯU ĐIỂM")}
                            </button>
                        </div>
                    </form>

                    {selectedLocation && (
                        <button
                            type="button"
                            onClick={() => handleDelete(selectedLocation.id)}
                            className="w-full py-3 border border-red-900/30 text-red-900 hover:text-red-500 hover:bg-red-500/5 transition-all text-[10px] font-mono uppercase tracking-[0.2em]"
                        >
                            Xóa địa điểm này
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
