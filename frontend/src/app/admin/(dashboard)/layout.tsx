import AdminNav from '@/app/admin/AdminNav';

// Shared layout for all authenticated admin pages (wraps with sidebar nav)
export default function AdminAuthLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex min-h-screen">
            <AdminNav />
            <main className="flex-1 overflow-auto bg-[#111] p-6">
                {children}
            </main>
        </div>
    );
}
