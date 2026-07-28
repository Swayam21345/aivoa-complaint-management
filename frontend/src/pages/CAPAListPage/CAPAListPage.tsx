import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import PageContainer from '@/components/layout/PageContainer/PageContainer';
import { CAPAStatusBadge } from '@/components/capa/CAPAStatusBadge';
import { fetchCAPADashboard, fetchCAPAList } from '@/services/capaService';
import type { CAPADashboardRead, CAPARead } from '@/types/capa.types';
import { formatDate } from '@/utils/formatDate';
import { useAppSelector } from '@/store/hooks';

export default function CAPAListPage() {
  const { user } = useAppSelector((state) => state.auth);
  const [capas, setCapas] = useState<CAPARead[]>([]);
  const [dashboard, setDashboard] = useState<CAPADashboardRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const role = user?.role;

  useEffect(() => {
    loadData();
  }, [page, statusFilter, priorityFilter]);

  async function loadData() {
    setLoading(true);
    try {
      const [listRes, dashRes] = await Promise.all([
        fetchCAPAList({
          page,
          page_size: 10,
          status: statusFilter || undefined,
          priority: priorityFilter || undefined,
          search: search.trim() || undefined,
        }),
        fetchCAPADashboard().catch(() => null),
      ]);
      setCapas(listRes.items);
      setTotal(listRes.total);
      setTotalPages(listRes.total_pages);
      setDashboard(dashRes);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    setPage(1);
    loadData();
  }

  return (
    <PageContainer
      title="🛡️ Enterprise CAPA Management"
      subtitle="TrackWise / Veeva Vault Compliant Corrective & Preventive Action Tracking"
    >
      {/* ── KPI Summary Cards ────────────────────────────────────────────────── */}
      {dashboard && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="card p-4 border border-blue-200 bg-blue-50/40">
            <span className="text-[10px] font-bold text-blue-700 uppercase tracking-wider">
              Open CAPAs
            </span>
            <p className="text-2xl font-extrabold text-blue-900 mt-1">{dashboard.open_capas}</p>
          </div>
          <div className="card p-4 border border-red-200 bg-red-50/40">
            <span className="text-[10px] font-bold text-red-700 uppercase tracking-wider">
              Overdue CAPAs
            </span>
            <p className="text-2xl font-extrabold text-red-900 mt-1">{dashboard.overdue_capas}</p>
          </div>
          <div className="card p-4 border border-purple-200 bg-purple-50/40">
            <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider">
              Pending Effectiveness
            </span>
            <p className="text-2xl font-extrabold text-purple-900 mt-1">
              {dashboard.pending_effectiveness}
            </p>
          </div>
          <div className="card p-4 border border-emerald-200 bg-emerald-50/40">
            <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider">
              Closed This Month
            </span>
            <p className="text-2xl font-extrabold text-emerald-900 mt-1">
              {dashboard.closed_this_month}
            </p>
          </div>
          <div className="card p-4 border border-gray-200 bg-gray-50/50">
            <span className="text-[10px] font-bold text-gray-600 uppercase tracking-wider">
              Avg Closure Time
            </span>
            <p className="text-2xl font-extrabold text-gray-900 mt-1">
              {dashboard.average_closure_days} <span className="text-xs font-normal">days</span>
            </p>
          </div>
        </div>
      )}

      {/* ── Search & Filters Bar ────────────────────────────────────────────── */}
      <div className="card p-4 mb-6 bg-white shadow-xs border border-gray-200">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          <div className="flex-1">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search CAPA number, title, description, or owner..."
              className="w-full border border-gray-300 rounded px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="border border-gray-300 rounded px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">OPEN</option>
            <option value="UNDER_IMPLEMENTATION">UNDER IMPLEMENTATION</option>
            <option value="PENDING_EFFECTIVENESS">PENDING EFFECTIVENESS</option>
            <option value="EFFECTIVE">EFFECTIVE</option>
            <option value="INEFFECTIVE">INEFFECTIVE</option>
            <option value="CLOSED">CLOSED</option>
          </select>
          <select
            value={priorityFilter}
            onChange={(e) => {
              setPriorityFilter(e.target.value);
              setPage(1);
            }}
            className="border border-gray-300 rounded px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <button
            type="submit"
            className="bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs px-4 py-2 rounded transition-colors"
          >
            Search
          </button>
        </form>
      </div>

      {/* ── CAPA Data Table ──────────────────────────────────────────────────── */}
      <div className="card p-5 bg-white shadow-xs border border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">
            CAPA Records ({total})
          </h3>
          {role && ['ADMIN', 'QA_MANAGER', 'INVESTIGATOR'].includes(role) && (
            <Link
              to="/complaints"
              className="bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold px-3 py-1.5 rounded no-underline"
            >
              + Create CAPA from Complaint
            </Link>
          )}
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-gray-400">Loading CAPA records...</div>
        ) : capas.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left" aria-label="CAPA records table">
              <thead>
                <tr className="bg-gray-50 border-b text-gray-500 font-bold uppercase tracking-wider">
                  <th className="p-3">CAPA Number</th>
                  <th className="p-3">Title</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Priority</th>
                  <th className="p-3">Owner</th>
                  <th className="p-3">Created</th>
                  <th className="p-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {capas.map((capa) => (
                  <tr key={capa.id} className="hover:bg-gray-50 transition-colors">
                    <td className="p-3 font-mono font-bold text-blue-700">
                      <Link to={`/capa/${capa.id}`} className="no-underline hover:underline">
                        {capa.capa_number}
                      </Link>
                    </td>
                    <td className="p-3 font-medium text-gray-900 max-w-xs truncate">
                      {capa.title}
                    </td>
                    <td className="p-3">
                      <CAPAStatusBadge status={capa.status} />
                    </td>
                    <td className="p-3">
                      <span
                        className={`font-bold text-[11px] px-2 py-0.5 rounded ${
                          capa.priority === 'Critical'
                            ? 'bg-red-100 text-red-800'
                            : capa.priority === 'High'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {capa.priority}
                      </span>
                    </td>
                    <td className="p-3 text-gray-700">{capa.owner || 'Unassigned'}</td>
                    <td className="p-3 text-gray-500 font-mono text-[11px]">
                      {formatDate(capa.created_at)}
                    </td>
                    <td className="p-3">
                      <Link
                        to={`/capa/${capa.id}`}
                        className="btn-secondary text-[11px] py-1 px-2.5 no-underline"
                      >
                        View CAPA →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-12 text-center">
            <div className="text-3xl mb-2">🛡️</div>
            <p className="text-sm font-bold text-gray-700">No CAPA Records Found</p>
            <p className="text-xs text-gray-400">
              CAPAs can be created when a complaint reaches Root Cause Identified.
            </p>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-between items-center pt-4 border-t mt-4 text-xs">
            <span className="text-gray-500">
              Page {page} of {totalPages} ({total} items)
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </PageContainer>
  );
}
