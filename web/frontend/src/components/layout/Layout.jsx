import { Outlet } from 'react-router-dom';
import { useEffect } from 'react';
import Sidebar from './Sidebar';
import Header  from './Header';
import MobileBottomBar from './MobileBottomBar';
import { useApp } from '../../context/AppContext';

export default function Layout() {
  const { loadCategories } = useApp();
  useEffect(() => { loadCategories(); }, [loadCategories]);

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Desktop sidebar */}
      <Sidebar />

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto px-4 py-6 md:px-6 pb-24 md:pb-6 page-enter">
          <Outlet />
        </main>
      </div>

      {/* Mobile bottom navigation */}
      <MobileBottomBar />
    </div>
  );
}
