import { useState, useEffect, useCallback } from 'react';
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import { movementsApi, productsApi } from '../utils/api';
import { MovementBadge } from '../components/ui/Badge';
import StockMovementModal from '../components/stock/StockMovementModal';
import SearchBar from '../components/ui/SearchBar';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';

const fmt = (n) => n != null
  ? Number(n).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
  : '-';

const TYPE_MAP = {
  in: 'Giriş', out: 'Çıkış', return: 'İade', adjustment: 'Sayım', transfer: 'Transfer'
};

export default function StockMovements() {
  const [movements, setMovements] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [typeFilter, setTypeFilter] = useState('');
  const [dateFrom, setDateFrom]   = useState('');
  const [dateTo, setDateTo]       = useState('');

  const [modal, setModal]         = useState({ open: false, product: null });
  const [products, setProducts]   = useState([]);
  const [productSel, setProductSel] = useState('');

  useEffect(() => {
    productsApi.getAll({ active: '1' }).then(r => setProducts(r.data)).catch(() => {});
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await movementsApi.getAll({
        type: typeFilter || undefined,
        from: dateFrom  || undefined,
        to:   dateTo    || undefined,
        product_id: productSel || undefined,
        limit: 200,
      });
      setMovements(res.data);
    } catch (e) {
      toast.error(e);
    } finally {
      setLoading(false);
    }
  }, [typeFilter, dateFrom, dateTo, productSel]);

  useEffect(() => { load(); }, [load]);

  async function handleSave(data) {
    try {
      await movementsApi.create({ ...data, product_id: modal.product.id });
      toast.success('Hareket kaydedildi');
      setModal({ open: false, product: null });
      load();
    } catch (e) { toast.error(e); }
  }

  const totals = movements.reduce((acc, m) => {
    if (m.type === 'in')  acc.totalIn  += m.total_amount ?? 0;
    if (m.type === 'out') acc.totalOut += m.total_amount ?? 0;
    return acc;
  }, { totalIn: 0, totalOut: 0 });

  return (
    <div className="space-y-4 max-w-7xl mx-auto">

      {/* Filters */}
      <div className="card p-4 flex flex-col sm:flex-row gap-3 flex-wrap">
        <select className="input sm:w-44 shrink-0" value={productSel} onChange={e => setProductSel(e.target.value)}>
          <option value="">Tüm ürünler</option>
          {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <select className="input sm:w-40 shrink-0" value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">Tüm tipler</option>
          {Object.entries(TYPE_MAP).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <input type="date" className="input sm:w-40 shrink-0" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
        <input type="date" className="input sm:w-40 shrink-0" value={dateTo}   onChange={e => setDateTo(e.target.value)} />
        <div className="flex-1" />
        <button
          className="btn-primary shrink-0"
          onClick={() => {
            if (!productSel) { toast.error('Önce ürün seçin'); return; }
            const p = products.find(x => x.id === productSel) || products[0];
            setModal({ open: true, product: p });
          }}
        >
          <Plus size={16} /> Hareket Ekle
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card p-4 text-center">
          <p className="text-xs text-slate-500 mb-1">Toplam Kayıt</p>
          <p className="text-xl font-bold text-slate-800">{movements.length}</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-xs text-slate-500 mb-1">Toplam Giriş</p>
          <p className="text-xl font-bold text-emerald-600">₺ {fmt(totals.totalIn)}</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-xs text-slate-500 mb-1">Toplam Çıkış</p>
          <p className="text-xl font-bold text-red-500">₺ {fmt(totals.totalOut)}</p>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                {['Tarih', 'Ürün', 'Tip', 'Miktar', 'Birim Fiyat', 'Toplam', 'Belge No', 'Not', 'Yapan'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {loading && <tr><td colSpan={9}><Spinner /></td></tr>}
              {!loading && movements.length === 0 && (
                <tr><td colSpan={9}><EmptyState message="Hareket kaydı bulunamadı" /></td></tr>
              )}
              {!loading && movements.map(m => (
                <tr key={m.id} className="table-row-hover">
                  <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">
                    {new Date(m.created_at).toLocaleDateString('tr-TR', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })}
                  </td>
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-800">{m.product_name}</p>
                    <p className="text-xs text-slate-400">{m.sku}</p>
                  </td>
                  <td className="px-4 py-3"><MovementBadge type={m.type} /></td>
                  <td className="px-4 py-3 font-semibold">{m.quantity} <span className="text-xs font-normal text-slate-400">{m.unit}</span></td>
                  <td className="px-4 py-3 text-slate-600">{m.unit_price != null ? `₺ ${fmt(m.unit_price)}` : '-'}</td>
                  <td className="px-4 py-3 font-medium text-slate-800">{m.total_amount != null ? `₺ ${fmt(m.total_amount)}` : '-'}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">{m.document_no ?? '-'}</td>
                  <td className="px-4 py-3 text-xs text-slate-500 max-w-[120px] truncate">{m.notes ?? '-'}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">{m.user_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!loading && (
          <div className="px-4 py-3 border-t border-slate-100 text-xs text-slate-400">
            {movements.length} hareket listelendi
          </div>
        )}
      </div>

      <StockMovementModal
        open={modal.open}
        onClose={() => setModal({ open: false, product: null })}
        onSave={handleSave}
        product={modal.product}
      />
    </div>
  );
}
