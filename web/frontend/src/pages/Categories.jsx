import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { categoriesApi } from '../utils/api';
import { useApp } from '../context/AppContext';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import Spinner from '../components/ui/Spinner';

const COLORS = [
  '#6366f1','#0ea5e9','#10b981','#f59e0b',
  '#ef4444','#8b5cf6','#ec4899','#14b8a6',
];

function CategoryModal({ open, onClose, onSave, category }) {
  const [name, setName]   = useState('');
  const [color, setColor] = useState(COLORS[0]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setName(category?.name ?? '');
    setColor(category?.color ?? COLORS[0]);
  }, [category, open]);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try { await onSave({ name, color }); }
    finally { setLoading(false); }
  }

  return (
    <Modal open={open} onClose={onClose} title={category ? 'Kategori Düzenle' : 'Yeni Kategori'} size="sm">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label">Kategori Adı *</label>
          <input className="input" value={name} onChange={e => setName(e.target.value)} required placeholder="Elektronik" />
        </div>
        <div>
          <label className="label">Renk</label>
          <div className="flex gap-2 flex-wrap">
            {COLORS.map(c => (
              <button
                key={c} type="button"
                className={`w-8 h-8 rounded-lg transition-all ${color === c ? 'ring-2 ring-offset-2 ring-slate-400 scale-110' : ''}`}
                style={{ background: c }}
                onClick={() => setColor(c)}
              />
            ))}
          </div>
        </div>
        <div className="flex gap-3 pt-1">
          <button type="button" className="btn-secondary flex-1" onClick={onClose}>İptal</button>
          <button type="submit" className="btn-primary flex-1" disabled={loading}>
            {loading ? 'Kaydediliyor...' : category ? 'Güncelle' : 'Ekle'}
          </button>
        </div>
      </form>
    </Modal>
  );
}

export default function Categories() {
  const { loadCategories } = useApp();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading]       = useState(true);
  const [modal, setModal]           = useState({ open: false, category: null });

  async function load() {
    setLoading(true);
    try {
      const res = await categoriesApi.getAll();
      setCategories(res.data);
    } catch (e) { toast.error(e); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function handleSave(data) {
    try {
      if (modal.category) {
        await categoriesApi.update(modal.category.id, data);
        toast.success('Kategori güncellendi');
      } else {
        await categoriesApi.create(data);
        toast.success('Kategori eklendi');
      }
      setModal({ open: false, category: null });
      load();
      loadCategories();
    } catch (e) { toast.error(e); }
  }

  async function handleDelete(c) {
    if (!confirm(`"${c.name}" kategorisini silmek istiyor musunuz?`)) return;
    try {
      await categoriesApi.remove(c.id);
      toast.success('Kategori silindi');
      load();
      loadCategories();
    } catch (e) { toast.error(e); }
  }

  return (
    <div className="space-y-4 max-w-2xl mx-auto">
      <div className="flex justify-end">
        <button className="btn-primary" onClick={() => setModal({ open: true, category: null })}>
          <Plus size={16} /> Yeni Kategori
        </button>
      </div>

      {loading && <Spinner />}

      {!loading && categories.length === 0 && <EmptyState message="Henüz kategori eklenmemiş" />}

      <div className="space-y-2">
        {categories.map(c => (
          <div key={c.id} className="card p-4 flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl shrink-0 flex items-center justify-center"
                 style={{ background: c.color + '22' }}>
              <div className="w-4 h-4 rounded-full" style={{ background: c.color }} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-slate-800">{c.name}</p>
              <p className="text-xs text-slate-400">{c.product_count} ürün</p>
            </div>
            <div className="flex gap-1">
              <button className="btn-ghost p-2" onClick={() => setModal({ open: true, category: c })}>
                <Edit2 size={15} />
              </button>
              <button className="btn-ghost p-2 text-red-400 hover:text-red-600"
                      onClick={() => handleDelete(c)}>
                <Trash2 size={15} />
              </button>
            </div>
          </div>
        ))}
      </div>

      <CategoryModal
        open={modal.open}
        onClose={() => setModal({ open: false, category: null })}
        onSave={handleSave}
        category={modal.category}
      />
    </div>
  );
}
