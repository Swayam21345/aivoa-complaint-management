import React from 'react';
import type { InternalAuditDashboardRead } from '@/types/internalAudit.types';

interface AuditDashboardProps {
  metrics: InternalAuditDashboardRead;
}

export const AuditDashboard: React.FC<AuditDashboardProps> = ({ metrics }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-gray-500">Total Audits</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{metrics.total_audits}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-blue-600">Planned Audits</p>
          <p className="text-2xl font-black text-blue-700 mt-1">{metrics.planned_audits}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-600">Closed Audits</p>
          <p className="text-2xl font-black text-emerald-700 mt-1">{metrics.closed_audits}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-purple-600">Inspection Readiness</p>
          <p className="text-2xl font-black text-purple-700 mt-1">{metrics.avg_inspection_readiness_score}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3">
          <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider border-b pb-2">
            🏢 Audits by Department
          </h3>
          <div className="space-y-2 pt-1 text-xs">
            {Object.entries(metrics.by_department).map(([dept, cnt]) => (
              <div key={dept} className="flex justify-between items-center py-1 border-b border-gray-100">
                <span className="font-medium text-gray-600">{dept}</span>
                <span className="font-bold font-mono text-slate-900">{cnt}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3">
          <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider border-b pb-2">
            🚨 Findings by Severity Category
          </h3>
          <div className="space-y-2 pt-1 text-xs">
            {Object.entries(metrics.by_category).map(([cat, cnt]) => (
              <div key={cat} className="flex justify-between items-center py-1 border-b border-gray-100">
                <span className="font-medium text-gray-600">{cat}</span>
                <span className="font-bold font-mono text-slate-900">{cnt}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
