import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
  LineChart, Line
} from 'recharts';
import { productsApi, movementsApi } from '../utils/api';
import Spinner from '../components/ui/Spinner';
import toast from 'react-hot-toast';

const fmt = (n) => Number(n ?? 0).toLocaleString('tr-TR', { minimumFractionDigits: 2 });

export default function Reports() {
  const [products,  setProducts]  = useState([]);
  const [movements, setMovements] = useState([]);
  const [loading,   setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([
      productsApi.getAll({ active: '1' }),
      movementsApi.getAll({ limit: 500 }),
    ]).then(([pr, mr]) => {
      setProducts(pr.data);
      setMovements(mr.data);
    }).catch(e => toast.error(e))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;

  // Stok değer bar chart (Top 10 ürün, alış değerine göre)
  const topProducts = [...products]
    .sort((a, b) => b.quantity * b.buy_price - a.quantity * a.buy_price)
    .slice(0, 10)
    .map(p => ({
      name: p.name.length > 14 ? p.name.slice(0, 14) + '…' : p.name,
      alisValue:  parseFloat((p.quantity * p.buy_price).toFixed(2)),
      satisValue: parseFloat((p.quantity * p.sell_price).toFixed(2)),
    }));

  // Kritik stok listesi
  const criticals = products.filter(p => p.quantity <= p.min_threshold)
    .sort((a, b) => a.quantity - b.quantity);

  // Hareket tipi dağılımı
  const typeDist = movements.reduce((acc, m) => {
    acc[m.type] = (acc[m.type] || 0) + 1;
    return acc;
  }, {});
  const typeData = Object.entries(typeDist).map(([k, v]) => ({
    name: { in:'Giriş', out:'Çıkış', return:'İade', adjustment:'Sayım', transfer:'Transfer' }[k] ?? k,
    value: v,
  }));
  const PIE_COLORS = ['#10b981','#ef4444','#f59e0b','#0ea5e9','#8b5cf6'];

  // Günlük kâr (son 14 gün)
  const dailyProfit = Object.entries(
    movements
      .filter(m => m.type === 'out')
      .reduce((acc, m) => {
        const day = m.created_at.slice(0, 10);
        acc[day] = (acc[day] || 0) + (m.total_amount ?? 0);
        return acc;
      }, {})
  ).sort(([a], [b]) => a.localeCompare(b)).slice(-14)
   .map(([date, total]) => ({ date: date.slice(5), total: parseFloat(total.toFixed(2)) }));

  // Özet
  const totalCost = products.reduce((s, p) => s + p.quantity * p.buy_price, 0);
  const totalSell = products.reduce((s, p) => s + p.quantity * p.sell_price, 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">

      {/* Özet */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Toplam Ürün',          value: products.length, color: 'text-indigo-600' },
          { label: 'Kritik Stok',          value: criticals.length, color: 'text-red-600' },
          { label: 'Stok Maliyet Değeri',  value: `₺ ${fmt(totalCost)}`, color: 'text-sky-600' },
          { label: 'Stok Satış Değeri',    value: `₺ ${fmt(totalSell)}`, color: 'text-emerald-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card p-4 text-center">
            <p className="text-xs text-slate-500 mb-1">{label}</p>
            <p className={`text-lg font-bold ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 10 stok değeri */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">En Değerli 10 Ürün (Stok × Fiyat)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={topProducts} layout="vertical" margin={{ left: 0, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
              <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={v => `₺${(v/1000).toFixed(0)}k`} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip formatter={v => [`₺ ${fmt(v)}`]} />
              <Bar dataKey="alisValue"  name="Alış"  fill="#6366f1" radius={[0,4,4,0]} barSize={10} />
              <Bar dataKey="satisValue" name="Satış" fill="#10b981" radius={[0,4,4,0]} barSize={10} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Hareket tipi dağılımı */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Hareket Tipi Dağılımı</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={typeData} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" outerRadius={80} paddingAngle={4}>
                {typeData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip />
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Günlük satış grafiği */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-slate-800 mb-4">Son 14 Gün Satış Tutarı</h3>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={dailyProfit}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `₺${v}`} axisLine={false} tickLine={false} />
            <Tooltip formatter={v => [`₺ ${fmt(v)}`]} />
            <Line type="monotone" dataKey="total" name="Satış" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Kritik stok tablosu */}
      <div className="card overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100">
          <h3 className="text-sm font-semibold text-slate-800">Kritik Stok Listesi</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                {['SKU','Ürün','Mevcut','Minimum','Eksik','Durum'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {criticals.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-sm text-slate-400">
                    Tüm ürünler yeterli stok seviyesinde ✓
                  </td>
                </tr>
              )}
              {criticals.map(p => {
                const eksik = Math.max(0, p.min_threshold - p.quantity);
                return (
                  <tr key={p.id} className="table-row-hover">
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{p.sku}</td>
                    <td className="px-4 py-3 font-medium text-slate-800">{p.name}</td>
                    <td className={`px-4 py-3 font-bold ${p.quantity <= 0 ? 'text-red-600' : 'text-amber-600'}`}>
                      {p.quantity} {p.unit}
                    </td>
                    <td className="px-4 py-3 text-slate-500">{p.min_threshold} {p.unit}</td>
                    <td className="px-4 py-3 text-red-500 font-medium">{eksik} {p.unit}</td>
                    <td className="px-4 py-3">
                      {p.quantity <= 0
                        ? <span className="badge bg-red-100 text-red-700">Tükendi</span>
                        : <span className="badge bg-amber-100 text-amber-700">Kritik</span>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
