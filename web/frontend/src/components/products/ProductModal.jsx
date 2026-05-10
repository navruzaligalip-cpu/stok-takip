import { useState, useEffect } from 'react';
import Modal from '../ui/Modal';
import { useApp } from '../../context/AppContext';

const UNITS    = ['adet', 'kg', 'litre', 'metre', 'paket', 'kutu', 'ton', 'gram'];
const VAT_OPTS = [0, 1, 8, 18, 20];

const EMPTY = {
  sku: '', name: '', barcode: '', category_id: '', supplier_id: '',
  unit: 'adet', buy_price: '', sell_price: '', vat_rate: 18,
  quantity: '', min_threshold: 5, max_threshold: '', location: '', description: '',
};

export default function ProductModal({ open, onClose, onSave, product }) {
  const { categories } = useApp();
  const [form, setForm]   = useState(EMPTY);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setForm(product
      ? { ...EMPTY, ...product, quantity: product.quantity ?? '' }
      : EMPTY
    );
  }, [product, open]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));
  const num = (v) => v === '' ? '' : Number(v);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      await onSave({
        ...form,
        buy_price: num(form.buy_price),
        sell_price: num(form.sell_price),
        quantity: num(form.quantity),
        min_threshold: num(form.min_threshold),
        max_threshold: form.max_threshold === '' ? null : num(form.max_threshold),
        vat_rate: num(form.vat_rate),
      });
    } finally {
      setLoading(false);
    }
  }

  const Field = ({ label, children }) => (
    <div>
      <label className="label">{label}</label>
      {children}
    </div>
  );

  return (
    <Modal open={open} onClose={onClose} title={product ? 'Ürün Düzenle' : 'Yeni Ürün Ekle'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Temel bilgiler */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="SKU / Ürün Kodu *">
            <input className="input" value={form.sku} onChange={e => set('sku', e.target.value)} required placeholder="ELK-001" />
          </Field>
          <Field label="Ürün Adı *">
            <input className="input" value={form.name} onChange={e => set('name', e.target.value)} required placeholder="Ürün adı" />
          </Field>
          <Field label="Barkod">
            <input className="input" value={form.barcode} onChange={e => set('barcode', e.target.value)} placeholder="1234567890123" />
          </Field>
          <Field label="Kategori">
            <select className="input" value={form.category_id} onChange={e => set('category_id', e.target.value)}>
              <option value="">Kategori seçin</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </Field>
        </div>

        {/* Birim ve KDV */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <Field label="Birim">
            <select className="input" value={form.unit} onChange={e => set('unit', e.target.value)}>
              {UNITS.map(u => <option key={u}>{u}</option>)}
            </select>
          </Field>
          <Field label="KDV Oranı (%)">
            <select className="input" value={form.vat_rate} onChange={e => set('vat_rate', e.target.value)}>
              {VAT_OPTS.map(v => <option key={v} value={v}>%{v}</option>)}
            </select>
          </Field>
          <Field label="Raf Konumu">
            <input className="input" value={form.location} onChange={e => set('location', e.target.value)} placeholder="A-01-02" />
          </Field>
        </div>

        {/* Fiyatlar */}
        <div className="grid grid-cols-2 gap-4">
          <Field label="Alış Fiyatı (₺) *">
            <input type="number" min="0" step="0.01" className="input" value={form.buy_price}
              onChange={e => set('buy_price', e.target.value)} required placeholder="0.00" />
          </Field>
          <Field label="Satış Fiyatı (₺) *">
            <input type="number" min="0" step="0.01" className="input" value={form.sell_price}
              onChange={e => set('sell_price', e.target.value)} required placeholder="0.00" />
          </Field>
        </div>

        {/* Stok */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <Field label={product ? 'Mevcut Stok (salt okunur)' : 'Başlangıç Stoğu'}>
            <input type="number" min="0" step="0.01" className="input" value={form.quantity}
              onChange={e => set('quantity', e.target.value)}
              disabled={!!product} placeholder="0" />
          </Field>
          <Field label="Min. Stok Eşiği">
            <input type="number" min="0" step="0.01" className="input" value={form.min_threshold}
              onChange={e => set('min_threshold', e.target.value)} />
          </Field>
          <Field label="Maks. Stok (opsiyonel)">
            <input type="number" min="0" step="0.01" className="input" value={form.max_threshold}
              onChange={e => set('max_threshold', e.target.value)} placeholder="Sınırsız" />
          </Field>
        </div>

        {/* Açıklama */}
        <Field label="Açıklama">
          <textarea className="input resize-none" rows={2} value={form.description}
            onChange={e => set('description', e.target.value)} placeholder="Opsiyonel açıklama..." />
        </Field>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button type="button" className="btn-secondary flex-1" onClick={onClose}>İptal</button>
          <button type="submit" className="btn-primary flex-1" disabled={loading}>
            {loading ? 'Kaydediliyor...' : product ? 'Güncelle' : 'Ekle'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
