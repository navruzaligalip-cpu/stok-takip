import { PackageOpen } from 'lucide-react';
export default function EmptyState({ message = 'Kayit bulunamadi', icon: Icon = PackageOpen }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <Icon size={40} className="mb-3 opacity-40" />
      <p className="text-sm font-medium">{message}</p>
    </div>
  );
}
