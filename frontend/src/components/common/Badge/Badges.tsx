import type { ComplaintStatus, Priority, RiskLevel } from '@/types/complaint.types';

// ─── Status Badge ─────────────────────────────────────────────────────────────

interface StatusBadgeProps {
  status: ComplaintStatus | string;
  className?: string;
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  let badgeStyle = 'bg-gray-100 text-gray-800 border-gray-200';

  switch (status) {
    case 'NEW':
    case 'Draft':
      badgeStyle = 'bg-indigo-100 text-indigo-800 border-indigo-200';
      break;
    case 'UNDER_REVIEW':
    case 'Under Review':
      badgeStyle = 'bg-amber-100 text-amber-800 border-amber-200';
      break;
    case 'IN_PROGRESS':
      badgeStyle = 'bg-sky-100 text-sky-800 border-sky-200';
      break;
    case 'WAITING_CUSTOMER':
      badgeStyle = 'bg-purple-100 text-purple-800 border-purple-200';
      break;
    case 'RESOLVED':
      badgeStyle = 'bg-emerald-100 text-emerald-800 border-emerald-200';
      break;
    case 'CLOSED':
    case 'Closed':
      badgeStyle = 'bg-slate-100 text-slate-700 border-slate-200';
      break;
    case 'REJECTED':
      badgeStyle = 'bg-red-100 text-red-800 border-red-200';
      break;
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeStyle} ${className}`}
    >
      {status}
    </span>
  );
}

// ─── Risk Badge ───────────────────────────────────────────────────────────────

interface RiskBadgeProps {
  riskLevel: RiskLevel | string | null;
  className?: string;
}

export function RiskBadge({ riskLevel, className = '' }: RiskBadgeProps) {
  let badgeStyle = 'bg-gray-100 text-gray-700 border-gray-200';

  switch (riskLevel) {
    case 'High':
      badgeStyle = 'bg-red-100 text-red-800 border-red-300 font-bold';
      break;
    case 'Medium':
      badgeStyle = 'bg-amber-100 text-amber-800 border-amber-300 font-semibold';
      break;
    case 'Low':
      badgeStyle = 'bg-emerald-100 text-emerald-800 border-emerald-300';
      break;
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border ${badgeStyle} ${className}`}
    >
      {riskLevel ? `${riskLevel} Risk` : 'Unassessed'}
    </span>
  );
}

// ─── Priority Badge ───────────────────────────────────────────────────────────

interface PriorityBadgeProps {
  priority: Priority | string | null | undefined;
  className?: string;
}

export function PriorityBadge({ priority, className = '' }: PriorityBadgeProps) {
  if (!priority) return <span className="text-gray-400">—</span>;

  let badgeStyle = 'bg-blue-100 text-blue-800 border-blue-200';

  switch (priority) {
    case 'Critical':
      badgeStyle = 'bg-rose-100 text-rose-800 border-rose-300 font-bold shadow-2xs';
      break;
    case 'High':
      badgeStyle = 'bg-red-100 text-red-700 border-red-200 font-semibold';
      break;
    case 'Medium':
      badgeStyle = 'bg-amber-100 text-amber-700 border-amber-200';
      break;
    case 'Low':
      badgeStyle = 'bg-blue-100 text-blue-700 border-blue-200';
      break;
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs border ${badgeStyle} ${className}`}
    >
      {priority}
    </span>
  );
}
