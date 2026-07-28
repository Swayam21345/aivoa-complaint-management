/**
 * Format an ISO date string (YYYY-MM-DD) to a human-readable form.
 * e.g. "2026-07-27" → "Jul 27, 2026"
 */
export function formatDate(isoDate: string | null | undefined): string {
  if (!isoDate) return '—';
  const date = new Date(isoDate + 'T00:00:00'); // avoid UTC offset shift
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format an ISO datetime string to a human-readable local datetime.
 * e.g. "2026-07-27T10:42:00Z" → "Jul 27, 2026, 10:42 AM"
 */
export function formatDateTime(isoDateTime: string | null | undefined): string {
  if (!isoDateTime) return '—';
  const date = new Date(isoDateTime);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

/**
 * Returns today's date as an ISO string (YYYY-MM-DD).
 */
export function todayISO(): string {
  return new Date().toISOString().split('T')[0];
}
