import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Package, ArrowLeftRight, BarChart2, Tag } from 'lucide-react';

const NAV = [
  { to: '/dashboard',  icon: LayoutDashboard, label: 'Anasayfa' },
  { to: '/products',   icon: Package,          label: 'Ürünler' },
  { to: '/movements',  icon: ArrowLeftRight,   label: 'Hareketler' },
  { to: '/categories', icon: Tag,              label: 'Kategori' },
  { to: '/reports',    icon: BarChart2,        label: 'Raporlar' },
];

export default function MobileBottomBar() {
  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-20 bg-white border-t border-slate-100 pb-safe">
      <div className="flex">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center gap-0.5 py-2.5 text-[10px] font-medium transition-colors
               ${isActive ? 'text-indigo-600' : 'text-slate-400'}`
            }
          >
            <Icon size={20} />
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
