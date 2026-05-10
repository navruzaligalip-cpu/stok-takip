import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Package, ArrowLeftRight,
  Tag, BarChart2, X
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

const NAV = [
  { to: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/products',   icon: Package,          label: 'Ürünler' },
  { to: '/movements',  icon: ArrowLeftRight,   label: 'Stok Hareketleri' },
  { to: '/categories', icon: Tag,              label: 'Kategoriler' },
  { to: '/reports',    icon: BarChart2,        label: 'Raporlar' },
];

function NavItem({ to, icon: Icon, label, onClick }) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
         ${isActive
           ? 'bg-indigo-50 text-indigo-600'
           : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`
      }
    >
      <Icon size={18} className="shrink-0" />
      <span>{label}</span>
    </NavLink>
  );
}

export default function Sidebar() {
  const { sidebarOpen, setSidebarOpen } = useApp();

  return (
    <>
      {/* Overlay (mobile) */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-slate-100 flex flex-col
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:relative md:translate-x-0 md:flex
        `}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
              <Package size={16} className="text-white" />
            </div>
            <span className="font-semibold text-slate-900">StokTakip</span>
          </div>
          <button
            className="md:hidden p-1 rounded-lg hover:bg-slate-100"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={18} className="text-slate-500" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV.map(item => (
            <NavItem
              key={item.to}
              {...item}
              onClick={() => setSidebarOpen(false)}
            />
          ))}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-slate-100">
          <p className="text-xs text-slate-400">v1.0.0 · Stok Takip</p>
        </div>
      </aside>
    </>
  );
}
