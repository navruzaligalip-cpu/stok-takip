import { useLocation } from 'react-router-dom';
import { Menu, Bell } from 'lucide-react';
import { useApp } from '../../context/AppContext';

const TITLES = { '/dashboard': 'Dashboard', '/products': 'Urun Yonetimi', '/movements': 'Stok Hareketleri', '/categories': 'Kategoriler', '/reports': 'Raporlar' };

export default function Header() {
  const { setSidebarOpen } = useApp();
  const { pathname } = useLocation();
  return (
    <header className="h-16 bg-white border-b border-slate-100 flex items-center px-4 md:px-6 shrink-0">
      <button className="md:hidden p-2 rounded-lg hover:bg-slate-100 mr-3" onClick={() => setSidebarOpen(true)}><Menu size={20} className="text-slate-600" /></button>
      <h1 className="text-lg font-semibold text-slate-900 flex-1">{TITLES[pathname] ?? 'Stok Takip'}</h1>
      <div className="flex items-center gap-2">
        <button className="p-2 rounded-lg hover:bg-slate-100 relative"><Bell size={18} className="text-slate-500" /><span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" /></button>
        <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center"><span className="text-xs font-semibold text-indigo-600">A</span></div>
      </div>
    </header>
  );
}
