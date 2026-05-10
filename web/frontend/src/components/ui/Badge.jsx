export function StockBadge({ quantity, minThreshold }) {
  if (quantity <= 0) return <span className="badge bg-red-100 text-red-700">Tukendi</span>;
  if (quantity <= minThreshold) return <span className="badge bg-amber-100 text-amber-700">Kritik</span>;
  return <span className="badge bg-emerald-100 text-emerald-700">Yeterli</span>;
}

export function MovementBadge({ type }) {
  const map = { in: { label: 'Giris', cls: 'bg-emerald-100 text-emerald-700' }, out: { label: 'Cikis', cls: 'bg-red-100 text-red-700' }, return: { label: 'Iade', cls: 'bg-amber-100 text-amber-700' }, adjustment: { label: 'Sayim', cls: 'bg-sky-100 text-sky-700' }, transfer: { label: 'Transfer', cls: 'bg-purple-100 text-purple-700' } };
  const { label, cls } = map[type] || { label: type, cls: 'bg-slate-100 text-slate-700' };
  return <span className={`badge ${cls}`}>{label}</span>;
}
