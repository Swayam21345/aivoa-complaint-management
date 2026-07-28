import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PageContainer from '@/components/layout/PageContainer/PageContainer';
import { StatusBadge, RiskBadge, PriorityBadge } from '@/components/common/Badge/Badges';
import { TableSkeleton } from '@/components/common/Skeleton/Skeleton';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchComplaints,
  setFilter,
  setPage,
  resetFilters,
} from '@/store/slices/complaintsListSlice';
import { formatDate } from '@/utils/formatDate';
import type { RiskLevel, ComplaintStatus, ComplaintCategory, Priority } from '@/types/complaint.types';

// ─── Options ──────────────────────────────────────────────────────────────────

const STATUS_OPTIONS: ComplaintStatus[] = [
  'NEW',
  'UNDER_REVIEW',
  'IN_PROGRESS',
  'WAITING_CUSTOMER',
  'RESOLVED',
  'CLOSED',
  'REJECTED',
  'Draft',
];
const PRIORITY_OPTIONS: Priority[] = ['Critical', 'High', 'Medium', 'Low'];
const RISK_OPTIONS: RiskLevel[] = ['High', 'Medium', 'Low'];
const CATEGORY_OPTIONS: ComplaintCategory[] = [
  'Product Quality Defect',
  'Packaging Defect',
  'Labeling Error',
  'Delivery Damage',
  'Adverse Event',
  'Foreign Material',
  'Documentation Error',
  'Other',
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function FilterSelect({
  id,
  label,
  value,
  options,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex flex-col gap-1 min-w-[140px]">
      <label htmlFor={id} className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
        {label}
      </label>
      <select
        id={id}
        className="form-input text-xs py-1.5 px-2 rounded-md border-gray-300"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label={`Filter by ${label}`}
      >
        <option value="">All {label}s</option>
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}

// ─── Page Component ───────────────────────────────────────────────────────────

export default function ComplaintsListPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const { items, total, page, page_size, filters, status, error } =
    useAppSelector((s) => s.complaintsList);
  const { role } = useAppSelector((s) => s.auth);

  const [searchInput, setSearchInput] = useState(filters.search || '');

  const isLoading = status === 'loading';
  const totalPages = Math.max(1, Math.ceil(total / page_size));
  const canCreate = role && ['ADMIN', 'QA_MANAGER', 'INVESTIGATOR'].includes(role);

  // ── Fetch on mount and when filters / page change ────────────────────────
  useEffect(() => {
    dispatch(
      fetchComplaints({
        status: filters.status || undefined,
        risk_level: filters.risk_level || undefined,
        priority: filters.priority || undefined,
        category: filters.category || undefined,
        search: filters.search || undefined,
        sort: filters.sort,
        sort_by: filters.sort_by,
        sort_order: filters.sort_order,
        page,
        page_size,
      }),
    );
  }, [dispatch, filters, page, page_size]);

  // ── Handlers ────────────────────────────────────────────────────────────

  function handleFilterChange(key: keyof typeof filters, value: string) {
    dispatch(setFilter({ key, value }));
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    dispatch(setFilter({ key: 'search', value: searchInput }));
  }

  function handleSortToggle(columnKey: string) {
    if (filters.sort_by === columnKey) {
      const nextOrder = filters.sort_order === 'asc' ? 'desc' : 'asc';
      dispatch(setFilter({ key: 'sort_order', value: nextOrder }));
    } else {
      dispatch(setFilter({ key: 'sort_by', value: columnKey }));
      dispatch(setFilter({ key: 'sort_order', value: 'asc' }));
    }
  }

  function handleReset() {
    setSearchInput('');
    dispatch(resetFilters());
  }

  function handlePageChange(next: number) {
    if (next < 1 || next > totalPages) return;
    dispatch(setPage(next));
  }

  const hasActiveFilters =
    Boolean(filters.risk_level || filters.priority || filters.category || filters.status || filters.search);

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <PageContainer
      title="Complaint Records & Quality Management"
      subtitle="Search, filter, sort, and inspect all logged customer complaint files."
    >
      {/* ── Toolbar & Search ───────────────────────────────────────────── */}
      <div className="card p-4 mb-6 space-y-4">
        {/* Top row: Search input & CTA */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 flex-1 max-w-lg">
            <div className="relative flex-1">
              <input
                type="text"
                className="form-input text-xs py-2 pl-9 pr-3 w-full"
                placeholder="Search by Complaint ID, Customer, Product, Batch, or Text..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
              />
              <span className="absolute left-3 top-2.5 text-gray-400 text-xs">🔍</span>
            </div>
            <button type="submit" className="btn-primary text-xs py-2 px-4">
              Search
            </button>
          </form>

          {canCreate && (
            <Link to="/upload" className="btn-primary text-xs py-2 px-4 no-underline shrink-0 flex items-center justify-center gap-1.5">
              <span>✦</span>
              <span>New Complaint</span>
            </Link>
          )}
        </div>

        {/* Bottom row: Multi-filter selects */}
        <div className="flex flex-wrap items-end gap-3 pt-2 border-t border-gray-100">
          <FilterSelect
            id="filter-status"
            label="Status"
            value={filters.status}
            options={STATUS_OPTIONS}
            onChange={(v) => handleFilterChange('status', v)}
          />
          <FilterSelect
            id="filter-priority"
            label="Priority"
            value={filters.priority}
            options={PRIORITY_OPTIONS}
            onChange={(v) => handleFilterChange('priority', v)}
          />
          <FilterSelect
            id="filter-risk"
            label="Risk Level"
            value={filters.risk_level}
            options={RISK_OPTIONS}
            onChange={(v) => handleFilterChange('risk_level', v)}
          />
          <FilterSelect
            id="filter-category"
            label="Category"
            value={filters.category}
            options={CATEGORY_OPTIONS}
            onChange={(v) => handleFilterChange('category', v)}
          />

          {/* Reset button */}
          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleReset}
              className="btn-secondary text-xs py-1.5 px-3 text-red-600 hover:text-red-700 self-end"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* ── Error Notification ────────────────────────────────────────── */}
      {error && (
        <div role="alert" className="mb-4 rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* ── Complaints Table ──────────────────────────────────────────── */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-4">
            <TableSkeleton />
          </div>
        ) : items.length === 0 ? (
          <div className="py-20 text-center text-gray-400 text-sm">
            <p className="text-3xl mb-3">📋</p>
            <p className="font-semibold text-gray-700">No complaints match criteria</p>
            <p className="mt-1 text-xs text-gray-500">
              {hasActiveFilters
                ? 'Try clearing or modifying the active search or filter criteria.'
                : 'No complaints logged yet.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left" aria-label="Complaints list">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50/80 text-gray-600 font-semibold uppercase tracking-wider select-none">
                  <th
                    className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSortToggle('complaint_id')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Complaint ID</span>
                      {filters.sort_by === 'complaint_id' && (
                        <span>{filters.sort_order === 'asc' ? '▲' : '▼'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSortToggle('created_at')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Date</span>
                      {filters.sort_by === 'created_at' && (
                        <span>{filters.sort_order === 'asc' ? '▲' : '▼'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSortToggle('product_name')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Product</span>
                      {filters.sort_by === 'product_name' && (
                        <span>{filters.sort_order === 'asc' ? '▲' : '▼'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSortToggle('customer_name')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Customer</span>
                      {filters.sort_by === 'customer_name' && (
                        <span>{filters.sort_order === 'asc' ? '▲' : '▼'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSortToggle('category')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Category</span>
                      {filters.sort_by === 'category' && (
                        <span>{filters.sort_order === 'asc' ? '▲' : '▼'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSortToggle('priority')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Priority</span>
                      {filters.sort_by === 'priority' && (
                        <span>{filters.sort_order === 'asc' ? '▲' : '▼'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSortToggle('risk_level')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Risk</span>
                      {filters.sort_by === 'risk_level' && (
                        <span>{filters.sort_order === 'asc' ? '▲' : '▼'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => handleSortToggle('status')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Status</span>
                      {filters.sort_by === 'status' && (
                        <span>{filters.sort_order === 'asc' ? '▲' : '▼'}</span>
                      )}
                    </div>
                  </th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {items.map((c) => (
                  <tr
                    key={c.id}
                    className="hover:bg-blue-50/40 transition-colors cursor-pointer group"
                    onClick={() => navigate(`/complaints/${c.id}`)}
                    role="button"
                    tabIndex={0}
                    aria-label={`View complaint ${c.complaint_id}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        navigate(`/complaints/${c.id}`);
                      }
                    }}
                  >
                    <td className="px-4 py-3 font-mono font-medium text-primary-600 group-hover:underline whitespace-nowrap">
                      {c.complaint_id}
                    </td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                      {formatDate(c.date_received)}
                    </td>
                    <td className="px-4 py-3 text-gray-900 font-medium max-w-[160px] truncate">
                      {c.product_name ?? <span className="text-gray-400">—</span>}
                    </td>
                    <td className="px-4 py-3 text-gray-600 max-w-[140px] truncate">
                      {c.customer_name ?? <span className="text-gray-400">—</span>}
                    </td>
                    <td className="px-4 py-3 text-gray-600 max-w-[140px] truncate">
                      {c.category ?? <span className="text-gray-400">—</span>}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <PriorityBadge priority={c.priority} />
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <RiskBadge riskLevel={c.risk_level} />
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="text-primary-600 font-semibold group-hover:translate-x-0.5 transition-transform inline-block">
                        View →
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Pagination Footer ─────────────────────────────────────────── */}
      {!isLoading && total > 0 && (
        <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-gray-500">
          <span>
            Showing <strong className="text-gray-800">{(page - 1) * page_size + 1}</strong>–
            <strong className="text-gray-800">{Math.min(page * page_size, total)}</strong> of{' '}
            <strong className="text-gray-900">{total}</strong> complaints
          </span>

          <div className="flex items-center gap-1" role="navigation" aria-label="Pagination">
            <button
              type="button"
              className="btn-secondary px-2.5 py-1 text-xs disabled:opacity-40"
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              aria-label="Previous page"
            >
              ← Prev
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(
                (p) =>
                  p === 1 || p === totalPages || Math.abs(p - page) <= 2,
              )
              .reduce<(number | 'ellipsis')[]>((acc, p, idx, arr) => {
                if (idx > 0 && p - (arr[idx - 1] as number) > 1) {
                  acc.push('ellipsis');
                }
                acc.push(p);
                return acc;
              }, [])
              .map((p, idx) =>
                p === 'ellipsis' ? (
                  <span key={`ellipsis-${idx}`} className="px-2 text-gray-400">
                    …
                  </span>
                ) : (
                  <button
                    key={p}
                    type="button"
                    onClick={() => handlePageChange(p as number)}
                    aria-label={`Page ${p}`}
                    aria-current={page === p ? 'page' : undefined}
                    className={`
                      px-2.5 py-1 rounded text-xs font-medium transition-colors
                      ${page === p
                        ? 'bg-primary-600 text-white font-bold'
                        : 'btn-secondary'}
                    `}
                  >
                    {p}
                  </button>
                ),
              )}

            <button
              type="button"
              className="btn-secondary px-2.5 py-1 text-xs disabled:opacity-40"
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
              aria-label="Next page"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
