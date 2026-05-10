import { useState, useEffect } from 'react';
import Modal from '../ui/Modal';

const TYPES = [
  { value: 'in',         label: '📥 Stok Girişi (Satın Alma)' },
  { value: 'out',        label: '📤 Stok Çıkışı (Satış / Fire)' },
  { value: 'return',     label: '↩️ İade' },
  { value: 'adjustment', label: '⚖️ Stok Sayımı (Düzeltme)' },
];

const EMPTY = { type: 'in', quantity: '', unit_price: '', document_no: '', notes: '' };

export default function StockMovementModal({ open, onClose, onSave, product }) {
  const [form, setForm] = useState(EMPTY);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && product) {
      setForm({ ...EMPTY, unit_price: product.buy_price || '' });
    }
  }, [open, product]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  useEffect(() => {
    if (form.type === 'in')  set('unit_price', product?.buy_price  ?? '');
    if (form.type === 'out') set('unit_price', product?.sell_price ?? '');
  }, [form.type]);  // eslint-disable-line

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      await onSave({ ...form, quantity: Number(form.quantity), unit_price: Number(form.unit_price) || null });
    } finally {
      setLoading(false);
    }
  }

  const total = form.quantity && form.unit_price
    ? (Number(form.quantity) * Number(form.unit_price)).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    : null;

  return (
    <Modal open={open} onClose={onClose} title="Stok Hareketi Ekle">
      {product && (
        <div className="mb-5 p-3 bg-slate-50 rounded-lg text-sm">
          <p className="font-medium text-slate-800">{product.name}</p>
          <p className="text-slate-500">
            SKU: {product.sku} · Mevcut Stok: <strong>{product.quantity} {product.unit}</strong>
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label">Hareket Tipi *</label>
          <select className="input" value={form.type} onChange={e => set('type', e.target.value)}>
            {TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">
              {form.type === 'adjustment' ? 'Yeni Stok Miktarı *' : 'Miktar *'}
            </label>
            <input
              type="number" min="0.001" step="0.001" className="input"
              value={form.quantity} onChange={e => set('quantity', e.target.value)}
              required placeholder="0"
            />
          </div>
          <div>
            <label className="label">Birim Fiyat (₺)</label>
            <input
              type="number" min="0" step="0.01" className="input"
              value={form.unit_price} onChange={e => set('unit_price', e.target.value)}
              placeholder="0.00"
            />
          </div>
        </div>

        {total && (
          <div className="text-right text-sm font-medium text-indigo-600 -mt-2">
            Toplam: ₺ {total}
          </div>
        )}

        <div>
          <label className="label">Belge / Fatura No</label>
          <input className="input" value={form.document_no} onChange={e => set('document_no', e.target.value)} placeholder="FAT-2024-001" />
        </div>

        <div>
          <label className="label">Not</label>
          <textarea className="input resize-none" rows={2} value={form.notes}
            onChange={e => set('notes', e.target.value)} placeholder="Opsiyonel açıklama..." />
        </div>

        <div className="flex gap-3 pt-1">
          <button type="button" className="btn-secondary flex-1" onClick={onClose}>İptal</button>
          <button type="submit" className="btn-primary flex-1" disabled={loading}>
            {loading ? 'Kaydediliyor...' : 'Kaydet'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
