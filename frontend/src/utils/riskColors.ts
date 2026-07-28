import type { RiskLevel } from '@/types/complaint.types';

/**
 * Returns the Tailwind CSS class name for a risk badge.
 * Falls back to a neutral style when risk is null/undefined.
 */
export function getRiskBadgeClass(risk: RiskLevel | null | undefined): string {
  switch (risk) {
    case 'High':
      return 'badge-high';
    case 'Medium':
      return 'badge-medium';
    case 'Low':
      return 'badge-low';
    default:
      return 'badge-draft';
  }
}

/**
 * Returns a hex color string for use outside Tailwind (e.g., inline styles).
 */
export function getRiskColor(risk: RiskLevel | null | undefined): string {
  switch (risk) {
    case 'High':
      return '#E02424';
    case 'Medium':
      return '#D97706';
    case 'Low':
      return '#057A55';
    default:
      return '#6B7280';
  }
}
