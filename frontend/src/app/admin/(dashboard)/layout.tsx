import AdminNav from '@/app/admin/AdminNav';

// Shared layout for all authenticated admin pages (wraps with sidebar nav)
export default function AdminAuthLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex flex-col md:flex-row min-h-screen bg-[#111]">
            <AdminNav />
            <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-6 w-full">
                {children}
            </main>
        </div>
    );
}
