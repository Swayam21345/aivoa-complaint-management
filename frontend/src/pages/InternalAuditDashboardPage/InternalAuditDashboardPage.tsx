import React, { useEffect, useState } from 'react';
import { AuditDashboard } from '@/components/internalAudit/AuditDashboard';
import { fetchInspectionReadinessPackages, fetchInternalAuditDashboard } from '@/services/internalAuditService';
import type { InspectionReadinessRead, InternalAuditDashboardRead } from '@/types/internalAudit.types';

export const InternalAuditDashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<InternalAuditDashboardRead | null>(null);
  const [packages, setPackages] = useState<InspectionReadinessRead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchInternalAuditDashboard(), fetchInspectionReadinessPackages()])
      .then(([m, p]) => {
        setMetrics(m);
        setPackages(p);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center text-xs text-gray-500">Loading Internal Audit Analytics...</div>;
  if (!metrics) return <div className="p-8 text-center text-xs text-red-500">Failed to load analytics.</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-black text-gray-900">📊 Internal Audit & Inspection Readiness Dashboard</h1>
        <p className="text-xs text-gray-500 mt-1">Real-time GxP Quality System Compliance & Regulatory Audit Packages</p>
      </div>

      <AuditDashboard metrics={metrics} />

      <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3 text-xs">
        <h3 className="font-bold text-gray-800 uppercase tracking-wider text-xs border-b pb-2 flex justify-between items-center">
          <span>📦 Regulatory Inspection Readiness Packages</span>
          <span className="text-gray-400 font-normal text-[11px]">{packages.length} Dossiers</span>
        </h3>

        {packages.length === 0 ? (
          <p className="text-gray-400 italic text-center py-4">No inspection packages compiled.</p>
        ) : (
          <div className="space-y-2">
            {packages.map((pkg) => (
              <div key={pkg.id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex justify-between items-center">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-900">{pkg.package_number}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-purple-100 text-purple-900 border border-purple-200">
                      {pkg.agency}
                    </span>
                    <span className="font-bold text-gray-800">{pkg.title}</span>
                  </div>
                  <p className="text-gray-500 text-[11px] mt-0.5">{pkg.description}</p>
                </div>

                <div className="text-right">
                  <p className="text-xs font-bold text-purple-700 font-mono">{pkg.readiness_score}% Score</p>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                    {pkg.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default InternalAuditDashboardPage;
