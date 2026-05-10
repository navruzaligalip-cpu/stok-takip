import { useState, useEffect } from 'react';
import {
  Package, AlertTriangle, TrendingUp, TrendingDown,
  DollarSign, ShoppingCart, ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import { dashboardApi } from '../utils/api';
import StatCard from '../components/ui/StatCard';
import { MovementBadge } from '../components/ui/Badge';
import Spinner from '../components/ui/Spinner';
import toast from 'react-hot-toast';

const fmt = (n) => n?.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) ?? '0,00';

export default function Dashboard() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi.get()
      .then(r => setData(r.data))
      .catch(() => toast.error('Dashboard yüklenemedi'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;
  if (!data)   return null;

  const { stats, recentMovements, criticalProducts, weeklyChart, categoryChart } = data;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Toplam Ürün"           value={stats.totalProducts}  icon={Package}       color="indigo" />
        <StatCard title="Kritik Stok"           value={stats.criticalCount}  icon={AlertTriangle} color="red"    sub={`${stats.outOfStock} ürün tükendi`} />
        <StatCard title="Stok Değeri (Alış)"   value={`₺ ${fmt(stats.totalStockCost)}`} icon={DollarSign} color="sky" />
        <StatCard title="Potansiyel Kâr"        value={`₺ ${fmt(stats.profit)}`}         icon={TrendingUp} color="green" />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Bugün Giriş"   value={`₺ ${fmt(stats.todayIn)}`}   icon={TrendingUp}   color="green" />
        <StatCard title="Bugün Çıkış"   value={`₺ ${fmt(stats.todayOut)}`}  icon={TrendingDown} color="red"   />
        <StatCard title="Bu Ay Giriş"   value={`₺ ${fmt(stats.monthIn)}`}   icon={ShoppingCart} color="indigo" />
        <StatCard title="Bu Ay Çıkış"   value={`₺ ${fmt(stats.monthOut)}`}  icon={TrendingDown} color="amber" />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly area chart */}
        <div className="card p-5 lg:col-span-2">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Son 7 Gün Hareket</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={weeklyChart} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="gIn"  x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#10b981" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gOut" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={v => `₺${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => [`₺ ${fmt(v)}`]} labelStyle={{ fontSize: 12 }} />
              <Area type="monotone" dataKey="income"  name="Giriş" stroke="#10b981" fill="url(#gIn)"  strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="expense" name="Çıkış" stroke="#ef4444" fill="url(#gOut)" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Category pie */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Kategori Dağılımı</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={categoryChart} dataKey="value" nameKey="category"
                   cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3}>
                {categoryChart.map((c, i) => (
                  <Cell key={i} fill={c.color || '#6366f1'} />
                ))}
              </Pie>
              <Tooltip formatter={v => [`₺ ${fmt(v)}`]} />
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tables row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Critical stock */}
        <div className="card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
              <AlertTriangle size={15} className="text-red-500" />
              Kritik Stok Uyarıları
            </h3>
            <Link to="/products" className="text-xs text-indigo-500 hover:underline flex items-center gap-1">
              Tümü <ArrowRight size={12} />
            </Link>
          </div>
          <div className="divide-y divide-slate-50">
            {criticalProducts.length === 0 && (
              <p className="text-center text-sm text-slate-400 py-8">Tüm ürünler yeterli seviyede ✓</p>
            )}
            {criticalProducts.map(p => (
              <div key={p.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-800">{p.name}</p>
                  <p className="text-xs text-slate-400">{p.category ?? 'Kategori yok'} · {p.sku}</p>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-bold ${p.quantity <= 0 ? 'text-red-600' : 'text-amber-600'}`}>
                    {p.quantity} {p.unit}
                  </p>
                  <p className="text-xs text-slate-400">Min: {p.min_threshold}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent movements */}
        <div className="card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <h3 className="text-sm font-semibold text-slate-800">Son Hareketler</h3>
            <Link to="/movements" className="text-xs text-indigo-500 hover:underline flex items-center gap-1">
              Tümü <ArrowRight size={12} />
            </Link>
          </div>
          <div className="divide-y divide-slate-50">
            {recentMovements.map(m => (
              <div key={m.id} className="flex items-center justify-between px-5 py-3">
                <div className="min-w-0 flex-1 mr-3">
                  <p className="text-sm font-medium text-slate-800 truncate">{m.product_name}</p>
                  <p className="text-xs text-slate-400">{m.notes ?? '-'}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <MovementBadge type={m.type} />
                  <span className="text-sm font-semibold text-slate-700">
                    {m.quantity} {m.unit}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
