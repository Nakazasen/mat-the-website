'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createAdminClient } from '@/lib/supabase-admin';
import { Users, UserPlus, Shield, User, Mail, Trash2, Loader2, CheckCircle2, AlertTriangle, Key, Pencil, X, Save } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface Profile {
    id: string;
    email: string;
    role: 'superadmin' | 'editor';
    display_name: string;
    created_at: string;
}

export default function AdminPersonnelPage() {
    const router = useRouter();
    const [users, setUsers] = useState<Profile[]>([]);
    const [loading, setLoading] = useState(true);
    const [inviting, setInviting] = useState(false);
    const [token, setToken] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Edit state
    const [editingUser, setEditingUser] = useState<Profile | null>(null);
    const [editForm, setEditForm] = useState({ display_name: '', email: '', role: 'editor' as string, password: '' });
    const [saving, setSaving] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        display_name: '',
        role: 'editor' as 'superadmin' | 'editor'
    });

    useEffect(() => {
        const loadUsers = async () => {
            const supabase = createAdminClient();
            if (!supabase) return;

            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push('/admin/login');
                return;
            }
            setToken(session.access_token);

            try {
                const res = await fetch(`${API_BASE_URL}/api/admin/users`, {
                    headers: { 'Authorization': `Bearer ${session.access_token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setUsers(data);
                } else {
                    const err = await res.json();
                    setError(err.detail || "Không có quyền truy cập danh sách nhân sự.");
                }
            } catch (err) {
                setError("Lỗi kết nối server.");
            } finally {
                setLoading(false);
            }
        };

        loadUsers();
    }, [router]);

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;
        setInviting(true);
        setError(null);
        setSuccess(null);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/invite`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Lỗi khi tạo tài khoản');

            setSuccess("Đã tạo tài khoản nhân sự thành công!");
            setFormData({ email: '', password: '', display_name: '', role: 'editor' });

            // Refresh list
            const refreshRes = await fetch(`${API_BASE_URL}/api/admin/users`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (refreshRes.ok) setUsers(await refreshRes.json());

        } catch (err: any) {
            setError(err.message);
        } finally {
            setInviting(false);
        }
    };

    const handleDelete = async (userId: string, email: string) => {
        if (!token) return;
        if (!confirm(`Bạn có chắc muốn xoá nhân sự: ${email}?\nHành động này không thể hoàn tác.`)) return;

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                setUsers(users.filter(u => u.id !== userId));
                setSuccess(`Đã xoá tài khoản ${email}`);
            } else {
                const data = await res.json();
                setError(data.detail || "Lỗi khi xoá tài khoản");
            }
        } catch (err) {
            setError("Lỗi kết nối server.");
        }
    };

    const startEdit = (user: Profile) => {
        setEditingUser(user);
        setEditForm({
            display_name: user.display_name || '',
            email: user.email,
            role: user.role,
            password: ''
        });
        setError(null);
        setSuccess(null);
    };

    const handleSaveEdit = async () => {
        if (!token || !editingUser) return;
        setSaving(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/users/${editingUser.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    display_name: editForm.display_name,
                    email: editForm.email,
                    role: editForm.role,
                    ...(editForm.password ? { password: editForm.password } : {})
                })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Lỗi khi cập nhật');

            setSuccess(`Đã cập nhật thông tin ${editForm.display_name || editForm.email}`);
            setEditingUser(null);

            // Refresh list
            const refreshRes = await fetch(`${API_BASE_URL}/api/admin/users`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (refreshRes.ok) setUsers(await refreshRes.json());
        } catch (err: any) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 gap-3">
                <Loader2 className="animate-spin text-green-500" size={32} />
                <p className="font-mono text-xs text-gray-500 tracking-widest uppercase">Đang tải danh sách nhân sự...</p>
            </div>
        );
    }

    const superadmins = users.filter(u => u.role === 'superadmin');
    const editors = users.filter(u => u.role === 'editor');

    const renderUserTable = (userList: Profile[]) => (
        <div className="bg-[#181818] border border-gray-800 rounded-lg overflow-x-auto">
            <table className="w-full text-left text-sm font-mono whitespace-nowrap">
                <thead className="bg-[#0d0d0d] border-b border-gray-800 text-gray-500 uppercase text-[10px] tracking-[0.2em]">
                    <tr>
                        <th className="px-4 py-4 sm:px-6 w-1/2 min-w-[200px]">Nhân sự</th>
                        <th className="px-4 py-4 sm:px-6 w-1/4">Vai trò</th>
                        <th className="px-4 py-4 sm:px-6 w-1/4 text-right">Thao tác</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                    {userList.map((user) => (
                        <tr key={user.id} className="hover:bg-gray-800/20 transition-colors group">
                            <td className="px-4 py-4 sm:px-6">
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded bg-green-900/20 border border-green-800/30 flex items-center justify-center text-green-500 font-bold shrink-0">
                                        {user.display_name?.[0] || user.email[0].toUpperCase()}
                                    </div>
                                    <div className="overflow-hidden">
                                        <div className="text-gray-200 font-bold truncate">{user.display_name || 'Chưa đặt tên'}</div>
                                        <div className="text-gray-500 text-[10px] truncate">{user.email}</div>
                                    </div>
                                </div>
                            </td>
                            <td className="px-4 py-4 sm:px-6">
                                <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] tracking-widest uppercase font-bold border ${user.role === 'superadmin'
                                    ? 'bg-red-500/10 border-red-500/20 text-red-500'
                                    : 'bg-green-500/10 border-green-500/20 text-green-500'
                                    }`}>
                                    <Shield size={10} />
                                    {user.role}
                                </span>
                            </td>
                            <td className="px-4 py-4 sm:px-6 text-right">
                                <div className="flex items-center justify-end gap-1">
                                    <button
                                        onClick={() => startEdit(user)}
                                        className="text-gray-600 hover:text-green-500 transition-colors p-2"
                                        title="Chỉnh sửa"
                                    >
                                        <Pencil size={15} />
                                    </button>
                                    {user.role !== 'superadmin' && (
                                        <button
                                            onClick={() => handleDelete(user.id, user.email)}
                                            className="text-gray-600 hover:text-red-500 transition-colors p-2"
                                            title="Xoá tài khoản"
                                        >
                                            <Trash2 size={15} />
                                        </button>
                                    )}
                                </div>
                            </td>
                        </tr>
                    ))}
                    {userList.length === 0 && (
                        <tr>
                            <td colSpan={3} className="px-6 py-8 text-center text-gray-500 text-xs italic">
                                Không có dữ liệu.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );

    return (
        <div className="max-w-6xl">
            <div className="mb-8">
                <h1 className="text-2xl font-mono text-gray-100 tracking-tight flex items-center gap-3">
                    <Users className="text-green-500" size={24} />
                    QUẢN LÝ NHÂN SỰ
                </h1>
                <p className="text-gray-500 text-sm font-mono mt-1">Cấp quyền Editor hoặc Quản trị viên cho đội ngũ nội dung.</p>
            </div>

            {success && (
                <div className="flex items-center gap-2 text-green-400 bg-green-950/30 border border-green-800/50 rounded p-4 text-sm mb-6 animate-in fade-in slide-in-from-top-2">
                    <CheckCircle2 size={16} />
                    <span>{success}</span>
                </div>
            )}

            {error && (
                <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded p-4 text-sm mb-6">
                    <AlertTriangle size={16} />
                    <span>{error}</span>
                </div>
            )}

            {/* EDIT MODAL */}
            {editingUser && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
                    <div className="bg-[#181818] border border-gray-700 rounded-lg p-6 w-full max-w-md mx-4 shadow-2xl">
                        <div className="flex items-center justify-between mb-6 border-b border-gray-800 pb-3">
                            <h2 className="text-sm font-mono text-gray-200 uppercase tracking-widest flex items-center gap-2">
                                <Pencil className="text-green-500" size={16} />
                                Chỉnh Sửa Nhân Sự
                            </h2>
                            <button onClick={() => setEditingUser(null)} className="text-gray-500 hover:text-gray-300 transition-colors">
                                <X size={18} />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <User size={10} /> Tên Hiển Thị
                                </label>
                                <input
                                    type="text"
                                    value={editForm.display_name}
                                    onChange={(e) => setEditForm({ ...editForm, display_name: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <Mail size={10} /> Email
                                </label>
                                <input
                                    type="email"
                                    value={editForm.email}
                                    onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <Shield size={10} /> Vai Trò
                                </label>
                                <select
                                    value={editForm.role}
                                    onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all appearance-none"
                                >
                                    <option value="editor">Editor (Đăng/Sửa truyện)</option>
                                    <option value="superadmin">SuperAdmin (Toàn quyền)</option>
                                </select>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <Key size={10} /> Đặt Lại Mật Khẩu
                                </label>
                                <input
                                    type="password"
                                    value={editForm.password}
                                    onChange={(e) => setEditForm({ ...editForm, password: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                    placeholder="Để trống nếu không đổi"
                                />
                                <p className="text-[9px] font-mono text-gray-700 italic">Để trống = giữ nguyên mật khẩu cũ. Tối thiểu 6 ký tự.</p>
                            </div>
                        </div>

                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => setEditingUser(null)}
                                className="flex-1 py-2.5 border border-gray-700 text-gray-400 hover:text-gray-200 hover:border-gray-600 rounded font-mono text-xs tracking-widest transition-all"
                            >
                                HỦY
                            </button>
                            <button
                                onClick={handleSaveEdit}
                                disabled={saving}
                                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded font-mono text-xs tracking-widest transition-all"
                            >
                                {saving ? <Loader2 className="animate-spin" size={14} /> : <Save size={14} />}
                                {saving ? "ĐANG LƯU..." : "LƯU THAY ĐỔI"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* LIST SECTION */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 border-b border-gray-800 pb-2">
                            <Shield className="text-red-500" size={16} />
                            <h2 className="text-sm font-mono text-gray-200 uppercase tracking-widest">Danh Sách SuperAdmin</h2>
                        </div>
                        {renderUserTable(superadmins)}
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center gap-2 border-b border-gray-800 pb-2">
                            <Pencil className="text-green-500" size={16} />
                            <h2 className="text-sm font-mono text-gray-200 uppercase tracking-widest">Danh Sách Editor</h2>
                        </div>
                        {renderUserTable(editors)}
                    </div>
                </div>

                {/* INVITE SECTION */}
                <div className="space-y-6">
                    <div className="bg-[#181818] border border-gray-800 rounded-lg p-6 hazard-corner">
                        <div className="flex items-center gap-2 mb-6 border-b border-gray-800 pb-3">
                            <UserPlus className="text-green-500" size={18} />
                            <h2 className="text-sm font-mono text-gray-200 uppercase tracking-widest">Tuyển dụng Mới</h2>
                        </div>

                        <form onSubmit={handleInvite} className="space-y-4">
                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <Mail size={10} /> Email Đăng Nhập
                                </label>
                                <input
                                    type="email"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                    placeholder="nhanvien@example.com"
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <Key size={10} /> Mật khẩu ban đầu
                                </label>
                                <input
                                    type="password"
                                    required
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                    placeholder="••••••••"
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <User size={10} /> Tên Hiển Thị
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.display_name}
                                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all"
                                    placeholder="VD: Hà Phong (Editor)"
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <Shield size={10} /> Vai Trò Hệ Thống
                                </label>
                                <select
                                    value={formData.role}
                                    onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                                    className="w-full bg-[#0a0a0a] border border-gray-800 rounded px-3 py-2 text-gray-200 text-sm focus:border-green-500 outline-none transition-all appearance-none"
                                >
                                    <option value="editor">Editor (Đăng/Sửa truyện)</option>
                                    <option value="superadmin">SuperAdmin (Toàn quyền)</option>
                                </select>
                            </div>

                            <button
                                type="submit"
                                disabled={inviting}
                                className="w-full mt-4 flex items-center justify-center gap-2 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-mono text-xs tracking-widest rounded transition-all uppercase font-bold"
                            >
                                {inviting ? <Loader2 className="animate-spin" size={14} /> : <UserPlus size={14} />}
                                {inviting ? "Đang tạo hồ sơ..." : "Tạo Tài Khoản"}
                            </button>
                        </form>
                    </div>

                    <div className="p-4 rounded border border-gray-800/50 bg-[#0d0d0d] flex gap-3 items-start">
                        <AlertTriangle className="text-gray-600 shrink-0 mt-0.5" size={14} />
                        <p className="text-[10px] font-mono text-gray-600 leading-relaxed italic">
                            Chế độ SuperAdmin cho phép bạn mời người khác. <br />
                            Hãy cẩn thận khi cấp quyền Quản trị viên tối cao.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
