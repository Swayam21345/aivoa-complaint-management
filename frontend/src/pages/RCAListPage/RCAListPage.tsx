import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchRCADashboard, fetchRCAList } from '@/services/rcaService';
import type { RCADashboardRead, RCARead } from '@/types/rca.types';

export const RCAListPage: React.FC = () => {

  const [rcas, setRcas] = useState<RCARead[]>([]);
  const [dashboard, setDashboard] = useState<RCADashboardRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [listRes, dashRes] = await Promise.all([
        fetchRCAList({
          search: search || undefined,
          status: statusFilter || undefined,
          category: categoryFilter || undefined,
        }),
        fetchRCADashboard(),
      ]);
      setRcas(listRes.items);
      setDashboard(dashRes);
    } catch (err) {
      console.error('Failed to load RCA records:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search, statusFilter, categoryFilter]);

  const getStatusBadge = (st: string) => {
    switch (st) {
      case 'APPROVED':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
            ✅ Approved
          </span>
        );
      case 'UNDER_REVIEW':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
            ⏳ Under Review
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-700 border border-gray-200">
            📝 Draft
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 flex items-center gap-2">
            🔬 Root Cause Analysis (RCA) & FMEA Module
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            TrackWise & Veeva QMS Compliant Failure Mode Investigation & Risk Prioritization
          </p>
        </div>
      </div>

      {/* Metrics Row */}
      {dashboard && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-gray-500">Total RCAs</p>
            <p className="text-2xl font-black text-slate-900 mt-1">{dashboard.total_rcas}</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-600">
              Approved RCAs
            </p>
            <p className="text-2xl font-black text-emerald-700 mt-1">{dashboard.approved_rcas}</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-amber-600">
              Pending Review
            </p>
            <p className="text-2xl font-black text-amber-700 mt-1">{dashboard.pending_rcas}</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-red-600">
              High Risk FMEAs (RPN ≥ 200)
            </p>
            <p className="text-2xl font-black text-red-700 mt-1">{dashboard.high_risk_fmea_count}</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-cyan-600">
              Average RPN Score
            </p>
            <p className="text-2xl font-black text-cyan-700 mt-1">{dashboard.average_rpn}</p>
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 Search by RCA #, primary cause, or category..."
          className="w-full md:w-96 rounded-lg border-gray-300 border p-2 text-xs focus:ring-primary-500"
        />

        <div className="flex gap-2 w-full md:w-auto">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border-gray-300 border p-2 text-xs bg-white"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="APPROVED">Approved</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="rounded-lg border-gray-300 border p-2 text-xs bg-white"
          >
            <option value="">All Categories</option>
            <option value="Equipment Failure">Equipment Failure</option>
            <option value="Human Error">Human Error</option>
            <option value="Raw Material Defect">Raw Material Defect</option>
            <option value="SOP Non-compliance">SOP Non-compliance</option>
            <option value="Environmental">Environmental</option>
          </select>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-xs text-gray-500">Loading RCA investigations...</div>
        ) : rcas.length === 0 ? (
          <div className="p-8 text-center text-xs text-gray-500">No RCA records found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead className="bg-gray-50 text-gray-700 uppercase text-[10px] font-bold tracking-wider border-b border-gray-200">
                <tr>
                  <th className="py-3 px-4">RCA Number</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Primary Root Cause</th>
                  <th className="py-3 px-4">Methodology</th>
                  <th className="py-3 px-4">FMEA Items</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {rcas.map((rca) => (
                  <tr key={rca.id} className="hover:bg-gray-50/80 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-900">
                      <Link
                        to={`/rca/${rca.id}`}
                        className="text-primary-600 hover:text-primary-800 underline"
                      >
                        {rca.rca_number}
                      </Link>
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-700">
                      {rca.root_cause_category}
                    </td>
                    <td className="py-3 px-4 text-gray-600 max-w-sm truncate">
                      {rca.primary_root_cause}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                        {rca.methodology}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-gray-700">
                      {rca.fmea_items?.length || 0}
                    </td>
                    <td className="py-3 px-4">{getStatusBadge(rca.status)}</td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/rca/${rca.id}`}
                        className="px-3 py-1 bg-slate-900 text-white rounded-md text-[11px] font-semibold hover:bg-slate-800 transition-colors"
                      >
                        View Record →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default RCAListPage;

