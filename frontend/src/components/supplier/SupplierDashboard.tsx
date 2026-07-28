import React from 'react';
import type { SupplierDashboardRead } from '@/types/supplier.types';

interface SupplierDashboardProps {
  metrics: SupplierDashboardRead;
}

export const SupplierDashboard: React.FC<SupplierDashboardProps> = ({ metrics }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-gray-500">Total Suppliers</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{metrics.total_suppliers}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-600">Approved Suppliers</p>
          <p className="text-2xl font-black text-emerald-700 mt-1">{metrics.approved_suppliers}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-amber-600">Avg Overall Score</p>
          <p className="text-2xl font-black text-amber-700 mt-1">{metrics.avg_overall_score}%</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-red-600">Upcoming Audits</p>
          <p className="text-2xl font-black text-red-700 mt-1">{metrics.upcoming_audits_count}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3">
          <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider border-b pb-2">
            🛡️ Supplier Risk Level Distribution
          </h3>
          <div className="space-y-2 pt-1 text-xs">
            {Object.entries(metrics.risk_distribution).map(([rk, cnt]) => (
              <div key={rk} className="flex justify-between items-center py-1 border-b border-gray-100">
                <span className="font-medium text-gray-600">{rk} Risk</span>
                <span className="font-bold font-mono text-slate-900">{cnt}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3">
          <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider border-b pb-2">
            🏭 Supplier Category Breakdown
          </h3>
          <div className="space-y-2 pt-1 text-xs">
            {Object.entries(metrics.by_type).map(([tp, cnt]) => (
              <div key={tp} className="flex justify-between items-center py-1 border-b border-gray-100">
                <span className="font-medium text-gray-600">{tp}</span>
                <span className="font-bold font-mono text-slate-900">{cnt}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
