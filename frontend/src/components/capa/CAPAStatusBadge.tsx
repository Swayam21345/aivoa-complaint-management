import type { CAPAStatus } from '@/types/capa.types';

interface Props {
  status: CAPAStatus | string;
}

const BADGE_STYLES: Record<string, { bg: string; text: string; border: string; icon: string }> = {
  OPEN: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', icon: '🔵' },
  UNDER_IMPLEMENTATION: { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', icon: '⚙️' },
  PENDING_EFFECTIVENESS: { bg: 'bg-purple-50', text: 'text-purple-800', border: 'border-purple-200', icon: '🔬' },
  EFFECTIVE: { bg: 'bg-emerald-50', text: 'text-emerald-800', border: 'border-emerald-200', icon: '✅' },
  INEFFECTIVE: { bg: 'bg-red-50', text: 'text-red-800', border: 'border-red-200', icon: '❌' },
  CLOSED: { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300', icon: '🔒' },
  CANCELLED: { bg: 'bg-gray-50', text: 'text-gray-500', border: 'border-gray-200', icon: '🚫' },
};

export function CAPAStatusBadge({ status }: Props) {
  const style = BADGE_STYLES[status] || {
    bg: 'bg-gray-50',
    text: 'text-gray-700',
    border: 'border-gray-200',
    icon: '📌',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold border ${style.bg} ${style.text} ${style.border}`}
    >
      <span>{style.icon}</span>
      <span>{status.replace(/_/g, ' ')}</span>
    </span>
  );
}
