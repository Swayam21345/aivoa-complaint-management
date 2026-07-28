import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts';

import PageContainer from '@/components/layout/PageContainer/PageContainer';
import { StatusBadge, RiskBadge, PriorityBadge } from '@/components/common/Badge/Badges';
import { PageSkeleton } from '@/components/common/Skeleton/Skeleton';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { getDashboardData } from '@/store/slices/dashboardSlice';
import { fetchComplaints } from '@/store/slices/complaintsListSlice';
import { getInvestigatorDashboard } from '@/services/complaintService';
import { formatDate } from '@/utils/formatDate';
import type { InvestigatorDashboardData } from '@/types/complaint.types';

// ─── Recharts Colors ──────────────────────────────────────────────────────────

const RISK_COLORS: Record<string, string> = {
  High: '#E02424',
  Medium: '#D97706',
  Low: '#057A55',
  Unassessed: '#9CA3AF',
};

const STATUS_COLORS: Record<string, string> = {
  NEW: '#4F46E5',
  Draft: '#6366F1',
  UNDER_REVIEW: '#F59E0B',
  'Under Review': '#F59E0B',
  IN_PROGRESS: '#0EA5E9',
  WAITING_CUSTOMER: '#8B5CF6',
  RESOLVED: '#10B981',
  CLOSED: '#64748B',
  Closed: '#64748B',
  REJECTED: '#EF4444',
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const { kpis, trends, loading, error } = useAppSelector((state) => state.dashboard);
  const { items: recentComplaints, status: listStatus } = useAppSelector(
    (state) => state.complaintsList,
  );
  const { user, role } = useAppSelector((state) => state.auth);

  const [investigatorData, setInvestigatorData] = useState<InvestigatorDashboardData | null>(null);

  useEffect(() => {
    dispatch(getDashboardData());
    dispatch(
      fetchComplaints({
        page: 1,
        page_size: 5,
        sort_by: 'created_at',
        sort_order: 'desc',
      }),
    );

    if (role === 'INVESTIGATOR' || role === 'QA_MANAGER' || role === 'ADMIN') {
      getInvestigatorDashboard()
        .then((data) => setInvestigatorData(data))
        .catch(() => {});
    }
  }, [dispatch, role]);

  const isEmpty = (kpis?.total_complaints ?? 0) === 0;

  return (
    <PageContainer
      title="Executive Quality Management Dashboard"
      subtitle="Real-time surveillance of pharmaceutical product quality complaints, risk metrics, and resolution trends."
    >
      {/* ── Top Bar Action Bar ─────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2.5">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
            ● Live QMS Analytics
          </span>
          <span className="text-xs text-gray-500 font-mono">
            Updated: {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/upload"
            className="btn-primary flex items-center gap-2 text-xs py-2 px-4 no-underline shadow-sm hover:shadow"
          >
            <span>✦</span>
            <span>AI Upload & Ingest</span>
          </Link>
          <Link
            to="/complaints"
            className="btn-secondary flex items-center gap-2 text-xs py-2 px-4 no-underline"
          >
            <span>📋 View All Complaints</span>
          </Link>
        </div>
      </div>

      {/* ── Investigator Personalized Dashboard Panel ──────────────────── */}
      {investigatorData && (
        <div className="card p-5 mb-8 bg-gradient-to-r from-primary-900 via-primary-800 to-indigo-900 text-white shadow-md">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-sm font-extrabold uppercase tracking-wider text-primary-200">
                🕵️ Investigator Dashboard ({user?.full_name || 'My Queue'})
              </h3>
              <p className="text-xs text-primary-300">
                Personalized task queue, active review cases, and monthly completion metrics.
              </p>
            </div>
            <span className="text-xs bg-primary-700/60 px-3 py-1 rounded-full border border-primary-500/40 text-white font-mono">
              Role: {role}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div className="bg-white/10 backdrop-blur p-3.5 rounded-lg border border-white/10">
              <span className="text-xs text-primary-200 uppercase tracking-wide font-semibold block mb-1">
                Assigned To Me
              </span>
              <span className="text-2xl font-black text-white">{investigatorData.assigned_to_me}</span>
            </div>
            <div className="bg-white/10 backdrop-blur p-3.5 rounded-lg border border-white/10">
              <span className="text-xs text-amber-200 uppercase tracking-wide font-semibold block mb-1">
                Pending Reviews
              </span>
              <span className="text-2xl font-black text-amber-300">{investigatorData.pending_reviews}</span>
            </div>
            <div className="bg-white/10 backdrop-blur p-3.5 rounded-lg border border-white/10">
              <span className="text-xs text-red-200 uppercase tracking-wide font-semibold block mb-1">
                Overdue Cases
              </span>
              <span className="text-2xl font-black text-red-300">{investigatorData.overdue_cases}</span>
            </div>
            <div className="bg-white/10 backdrop-blur p-3.5 rounded-lg border border-white/10">
              <span className="text-xs text-emerald-200 uppercase tracking-wide font-semibold block mb-1">
                Completed This Month
              </span>
              <span className="text-2xl font-black text-emerald-300">{investigatorData.completed_this_month}</span>
            </div>
            <div className="bg-white/10 backdrop-blur p-3.5 rounded-lg border border-white/10">
              <span className="text-xs text-sky-200 uppercase tracking-wide font-semibold block mb-1">
                Avg Resolution Time
              </span>
              <span className="text-2xl font-black text-sky-300">{investigatorData.average_resolution_time ?? 0}h</span>
            </div>
          </div>
        </div>
      )}

      {/* ── Loading State ──────────────────────────────────────────────── */}
      {loading && <PageSkeleton />}

      {/* ── Error State ────────────────────────────────────────────────── */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm flex items-center justify-between">
          <span>Failed to load dashboard metrics: {error}</span>
          <button
            onClick={() => dispatch(getDashboardData())}
            className="text-xs font-semibold text-red-800 underline hover:text-red-900"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* ── Empty State Banner ────────────────────────────────────────── */}
          {isEmpty && (
            <div className="card p-6 mb-8 bg-blue-50/50 border border-blue-200 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="text-sm font-semibold text-blue-900">Welcome to AICCMS QMS Dashboard</h3>
                <p className="text-xs text-blue-700 mt-1">
                  No complaints logged yet. Upload a document or paste complaint text to run AI extraction.
                </p>
              </div>
              <Link to="/upload" className="btn-primary text-xs py-2 px-4 whitespace-nowrap no-underline">
                ✦ Start AI Document Ingestion
              </Link>
            </div>
          )}

          {/* ── KPI Grid (10 Required KPI Cards) ──────────────────────────── */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 mb-8">
            {/* 1. Total Complaints */}
            <div className="card p-4 border-l-4 border-l-primary-600 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-gray-500 text-xs font-medium mb-1">
                <span>Total Complaints</span>
                <span className="text-base" role="img" aria-label="Total">📦</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{kpis?.total_complaints ?? 0}</div>
              <div className="text-[11px] text-gray-400 mt-1">All logged records</div>
            </div>

            {/* 2. New */}
            <div className="card p-4 border-l-4 border-l-indigo-500 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-gray-500 text-xs font-medium mb-1">
                <span>New</span>
                <span className="text-base" role="img" aria-label="New">🆕</span>
              </div>
              <div className="text-2xl font-bold text-indigo-600">{kpis?.new_count ?? 0}</div>
              <div className="text-[11px] text-gray-400 mt-1">Awaiting triage</div>
            </div>

            {/* 3. Under Review */}
            <div className="card p-4 border-l-4 border-l-amber-500 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-gray-500 text-xs font-medium mb-1">
                <span>Under Review</span>
                <span className="text-base" role="img" aria-label="Under Review">🔍</span>
              </div>
              <div className="text-2xl font-bold text-amber-600">{kpis?.under_review_count ?? 0}</div>
              <div className="text-[11px] text-gray-400 mt-1">Investigation active</div>
            </div>

            {/* 4. In Progress */}
            <div className="card p-4 border-l-4 border-l-sky-500 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-gray-500 text-xs font-medium mb-1">
                <span>In Progress</span>
                <span className="text-base" role="img" aria-label="In Progress">⚙️</span>
              </div>
              <div className="text-2xl font-bold text-sky-600">{kpis?.in_progress_count ?? 0}</div>
              <div className="text-[11px] text-gray-400 mt-1">CAPA underway</div>
            </div>

            {/* 5. Resolved */}
            <div className="card p-4 border-l-4 border-l-emerald-500 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-gray-500 text-xs font-medium mb-1">
                <span>Resolved</span>
                <span className="text-base" role="img" aria-label="Resolved">✅</span>
              </div>
              <div className="text-2xl font-bold text-emerald-600">{kpis?.resolved_count ?? 0}</div>
              <div className="text-[11px] text-gray-400 mt-1">Pending closure</div>
            </div>

            {/* 6. Closed */}
            <div className="card p-4 border-l-4 border-l-slate-400 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-gray-500 text-xs font-medium mb-1">
                <span>Closed</span>
                <span className="text-base" role="img" aria-label="Closed">🔒</span>
              </div>
              <div className="text-2xl font-bold text-slate-700">{kpis?.closed_count ?? 0}</div>
              <div className="text-[11px] text-gray-400 mt-1">Archived</div>
            </div>

            {/* 7. High Risk */}
            <div className="card p-4 border-l-4 border-l-red-600 bg-red-50/40 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-red-700 text-xs font-semibold mb-1">
                <span>High Risk</span>
                <span className="text-base" role="img" aria-label="High Risk">🚨</span>
              </div>
              <div className="text-2xl font-bold text-red-600">{kpis?.high_risk_count ?? 0}</div>
              <div className="text-[11px] text-red-500 mt-1">Quality alert</div>
            </div>

            {/* 8. Critical Priority */}
            <div className="card p-4 border-l-4 border-l-rose-600 bg-rose-50/40 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-rose-700 text-xs font-semibold mb-1">
                <span>Critical Priority</span>
                <span className="text-base" role="img" aria-label="Critical Priority">⚡</span>
              </div>
              <div className="text-2xl font-bold text-rose-600">{kpis?.critical_priority_count ?? 0}</div>
              <div className="text-[11px] text-rose-500 mt-1">Urgent response</div>
            </div>

            {/* 9. Created Today */}
            <div className="card p-4 border-l-4 border-l-blue-500 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-gray-500 text-xs font-medium mb-1">
                <span>Created Today</span>
                <span className="text-base" role="img" aria-label="Created Today">📅</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">{kpis?.created_today_count ?? 0}</div>
              <div className="text-[11px] text-gray-400 mt-1">Today's volume</div>
            </div>

            {/* 10. Created This Month */}
            <div className="card p-4 border-l-4 border-l-teal-500 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between text-gray-500 text-xs font-medium mb-1">
                <span>Created This Month</span>
                <span className="text-base" role="img" aria-label="Created This Month">🗓️</span>
              </div>
              <div className="text-2xl font-bold text-teal-600">{kpis?.created_this_month_count ?? 0}</div>
              <div className="text-[11px] text-gray-400 mt-1">Monthly total</div>
            </div>
          </div>

          {/* ── Recharts Analytics Section ─────────────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Chart 1: Complaint Status Distribution */}
            <div className="card p-5">
              <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>Complaint Status Distribution</span>
                <span className="text-[10px] text-gray-400 font-normal">Active Workflow</span>
              </h3>
              <div className="h-64 w-full">
                {trends?.by_status && trends.by_status.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={trends.by_status} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
                      <XAxis dataKey="label" tick={{ fontSize: 10 }} interval={0} />
                      <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{ borderRadius: '8px', fontSize: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                      />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                      <Bar dataKey="count" name="Complaints" radius={[4, 4, 0, 0]}>
                        {trends.by_status.map((entry) => (
                          <Cell key={entry.label} fill={STATUS_COLORS[entry.label] || '#4F46E5'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-gray-400 italic">
                    No status distribution data available.
                  </div>
                )}
              </div>
            </div>

            {/* Chart 2: Risk Level Distribution */}
            <div className="card p-5">
              <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>Risk Level Classification</span>
                <span className="text-[10px] text-gray-400 font-normal">Severity Profile</span>
              </h3>
              <div className="h-64 w-full">
                {trends?.by_risk_level && trends.by_risk_level.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={trends.by_risk_level}
                        dataKey="count"
                        nameKey="label"
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        paddingAngle={3}
                        label={({ name, value }) => `${name}: ${value}`}
                      >
                        {trends.by_risk_level.map((entry) => (
                          <Cell key={entry.label} fill={RISK_COLORS[entry.label] || '#9CA3AF'} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ borderRadius: '8px', fontSize: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                      />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-gray-400 italic">
                    No risk level classification data available.
                  </div>
                )}
              </div>
            </div>

            {/* Chart 3: Complaint Category Distribution */}
            <div className="card p-5">
              <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>Complaint Category Breakdown</span>
                <span className="text-[10px] text-gray-400 font-normal">Defect Types</span>
              </h3>
              <div className="h-64 w-full">
                {trends?.by_category && trends.by_category.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      layout="vertical"
                      data={trends.by_category}
                      margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
                      <XAxis type="number" tick={{ fontSize: 10 }} allowDecimals={false} />
                      <YAxis dataKey="label" type="category" tick={{ fontSize: 10 }} width={120} />
                      <Tooltip
                        contentStyle={{ borderRadius: '8px', fontSize: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                      />
                      <Bar dataKey="count" name="Complaints" fill="#6366F1" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-gray-400 italic">
                    No category breakdown data available.
                  </div>
                )}
              </div>
            </div>

            {/* Chart 4: Monthly Complaint Trend */}
            <div className="card p-5">
              <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>Monthly Complaint Volume Trend</span>
                <span className="text-[10px] text-gray-400 font-normal">Historical Timeline</span>
              </h3>
              <div className="h-64 w-full">
                {trends?.monthly_trend && trends.monthly_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trends.monthly_trend} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                      <defs>
                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#1A56DB" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#1A56DB" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
                      <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{ borderRadius: '8px', fontSize: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                      />
                      <Area
                        type="monotone"
                        dataKey="count"
                        name="Monthly Complaints"
                        stroke="#1A56DB"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorCount)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-gray-400 italic">
                    No monthly trend data recorded yet.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ── Complaint Summary Table (Recent Complaints) ───────────────── */}
          <div className="card overflow-hidden mb-6">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
              <div>
                <h3 className="text-sm font-semibold text-gray-800">Recent Customer Complaints</h3>
                <p className="text-xs text-gray-500 mt-0.5">Most recent quality complaints logged in system</p>
              </div>
              <Link to="/complaints" className="text-xs font-semibold text-primary-600 hover:text-primary-800 no-underline">
                View All →
              </Link>
            </div>

            {listStatus === 'loading' ? (
              <div className="p-6 text-center text-xs text-gray-400">Loading recent complaints...</div>
            ) : recentComplaints.length === 0 ? (
              <div className="p-8 text-center text-xs text-gray-400">No recent complaints found.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left" aria-label="Recent complaints summary">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-gray-500 font-semibold uppercase tracking-wider">
                      <th className="px-4 py-3">Complaint ID</th>
                      <th className="px-4 py-3">Product</th>
                      <th className="px-4 py-3">Customer</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Priority</th>
                      <th className="px-4 py-3">Risk</th>
                      <th className="px-4 py-3">Created Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {recentComplaints.slice(0, 5).map((c) => (
                      <tr
                        key={c.id}
                        className="hover:bg-blue-50/40 transition-colors cursor-pointer"
                        onClick={() => navigate(`/complaints/${c.id}`)}
                      >
                        <td className="px-4 py-3 font-mono font-medium text-primary-600 whitespace-nowrap">
                          {c.complaint_id}
                        </td>
                        <td className="px-4 py-3 text-gray-900 font-medium max-w-[160px] truncate">
                          {c.product_name ?? <span className="text-gray-400">—</span>}
                        </td>
                        <td className="px-4 py-3 text-gray-600 max-w-[140px] truncate">
                          {c.customer_name ?? <span className="text-gray-400">—</span>}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <StatusBadge status={c.status} />
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <PriorityBadge priority={c.priority} />
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <RiskBadge riskLevel={c.risk_level} />
                        </td>
                        <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                          {formatDate(c.date_received)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </PageContainer>
  );
}
