import { useState, useEffect, useCallback } from 'react';
import { Plus, Edit2, Trash2, ArrowUpDown, Package } from 'lucide-react';
import toast from 'react-hot-toast';
import { productsApi } from '../utils/api';
import { useApp } from '../context/AppContext';
import SearchBar from '../components/ui/SearchBar';
import { StockBadge } from '../components/ui/Badge';
import ProductModal from '../components/products/ProductModal';
import StockMovementModal from '../components/stock/StockMovementModal';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';

const fmt = (n) => Number(n).toLocaleString('tr-TR', { minimumFractionDigits: 2 });

export default function Products() {
  const { categories } = useApp();
  const [products, setProducts]     = useState([]);
  const [loading, setLoading]       = useState(true);
  const [search, setSearch]         = useState('');
  const [catFilter, setCatFilter]   = useState('');
  const [sort, setSort]             = useState({ col: 'name', dir: 'asc' });

  const [productModal, setProductModal]   = useState({ open: false, product: null });
  const [movementModal, setMovementModal] = useState({ open: false, product: null });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await productsApi.getAll({
        search: search || undefined,
        category: catFilter || undefined,
        sort: sort.col, order: sort.dir,
      });
      setProducts(res.data);
    } catch (e) {
      toast.error(e);
    } finally {
      setLoading(false);
    }
  }, [search, catFilter, sort]);

  useEffect(() => { load(); }, [load]);

  function toggleSort(col) {
    setSort(s => ({ col, dir: s.col === col && s.dir === 'asc' ? 'desc' : 'asc' }));
  }

  async function handleSave(data) {
    try {
      if (productModal.product) {
        await productsApi.update(productModal.product.id, data);
        toast.success('Ürün güncellendi');
      } else {
        await productsApi.create(data);
        toast.success('Ürün eklendi');
      }
      setProductModal({ open: false, product: null });
      load();
    } catch (e) {
      toast.error(e);
    }
  }

  async function handleDelete(p) {
    if (!confirm(`"${p.name}" ürününü pasif yapmak istiyor musunuz?`)) return;
    try {
      await productsApi.remove(p.id);
      toast.success('Ürün pasif yapıldı');
      load();
    } catch (e) { toast.error(e); }
  }

  async function handleMovementSave(data) {
    const { movementsApi } = await import('../utils/api');
    try {
      await movementsApi.create({ ...data, product_id: movementModal.product.id });
      toast.success('Stok hareketi kaydedildi');
      setMovementModal({ open: false, product: null });
      load();
    } catch (e) { toast.error(e); }
  }

  function SortTh({ col, label }) {
    const active = sort.col === col;
    return (
      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide cursor-pointer select-none hover:text-slate-800"
          onClick={() => toggleSort(col)}>
        <span className="flex items-center gap-1">
          {label}
          <ArrowUpDown size={12} className={active ? 'text-indigo-500' : 'opacity-30'} />
        </span>
      </th>
    );
  }

  return (
    <div className="space-y-4 max-w-7xl mx-auto">

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <SearchBar
          value={search}
          onChange={setSearch}
          placeholder="Ürün adı, SKU veya barkod..."
        />
        <select className="input sm:w-48 shrink-0" value={catFilter} onChange={e => setCatFilter(e.target.value)}>
          <option value="">Tüm kategoriler</option>
          {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <button
          className="btn-primary shrink-0"
          onClick={() => setProductModal({ open: true, product: null })}
        >
          <Plus size={16} /> Yeni Ürün
        </button>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                <SortTh col="sku"        label="SKU" />
                <SortTh col="name"       label="Ürün Adı" />
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Kategori</th>
                <SortTh col="quantity"   label="Stok" />
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Durum</th>
                <SortTh col="buy_price"  label="Alış" />
                <SortTh col="sell_price" label="Satış" />
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">İşlem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {loading && (
                <tr><td colSpan={8}><Spinner /></td></tr>
              )}
              {!loading && products.length === 0 && (
                <tr><td colSpan={8}><EmptyState message="Ürün bulunamadı" icon={Package} /></td></tr>
              )}
              {!loading && products.map(p => (
                <tr key={p.id} className="table-row-hover">
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{p.sku}</td>
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-slate-800">{p.name}</p>
                      {p.barcode && <p className="text-xs text-slate-400">{p.barcode}</p>}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {p.category_name
                      ? <span className="badge" style={{ background: p.category_color + '22', color: p.category_color }}>{p.category_name}</span>
                      : <span className="text-slate-400">-</span>}
                  </td>
                  <td className="px-4 py-3 font-semibold">
                    {p.quantity} <span className="text-xs font-normal text-slate-400">{p.unit}</span>
                  </td>
                  <td className="px-4 py-3">
                    <StockBadge quantity={p.quantity} minThreshold={p.min_threshold} />
                  </td>
                  <td className="px-4 py-3 text-slate-600">₺ {fmt(p.buy_price)}</td>
                  <td className="px-4 py-3 text-slate-800 font-medium">₺ {fmt(p.sell_price)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        className="btn-ghost p-1.5 text-indigo-500"
                        title="Stok Hareketi"
                        onClick={() => setMovementModal({ open: true, product: p })}
                      >
                        <ArrowUpDown size={15} />
                      </button>
                      <button
                        className="btn-ghost p-1.5"
                        title="Düzenle"
                        onClick={() => setProductModal({ open: true, product: p })}
                      >
                        <Edit2 size={15} />
                      </button>
                      <button
                        className="btn-ghost p-1.5 text-red-400 hover:text-red-600"
                        title="Pasif Yap"
                        onClick={() => handleDelete(p)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {!loading && (
          <div className="px-4 py-3 border-t border-slate-100 text-xs text-slate-400">
            {products.length} ürün listelendi
          </div>
        )}
      </div>

      <ProductModal
        open={productModal.open}
        onClose={() => setProductModal({ open: false, product: null })}
        onSave={handleSave}
        product={productModal.product}
      />

      <StockMovementModal
        open={movementModal.open}
        onClose={() => setMovementModal({ open: false, product: null })}
        onSave={handleMovementSave}
        product={movementModal.product}
      />
    </div>
  );
}
