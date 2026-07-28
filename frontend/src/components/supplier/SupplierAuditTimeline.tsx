import React from 'react';
import { formatDate } from '@/utils/formatDate';
import type { SupplierAuditRead } from '@/types/supplier.types';

interface SupplierAuditTimelineProps {
  audits: SupplierAuditRead[];
}

export const SupplierAuditTimeline: React.FC<SupplierAuditTimelineProps> = ({ audits }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3 text-xs">
      <h3 className="font-bold text-gray-800 uppercase tracking-wider text-xs border-b pb-2 flex justify-between items-center">
        <span>🔍 Quality Audit History</span>
        <span className="text-gray-400 font-normal text-[11px]">{audits.length} Audits Logged</span>
      </h3>

      {audits.length === 0 ? (
        <p className="text-gray-400 italic text-center py-4">No audits scheduled or logged.</p>
      ) : (
        <div className="space-y-2">
          {audits.map((a) => (
            <div key={a.id} className="p-3 bg-white border border-gray-200 rounded-lg flex justify-between items-center">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-slate-900">{a.audit_number}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">
                    {a.audit_type}
                  </span>
                </div>
                <p className="text-gray-500 text-[11px] mt-0.5">
                  Auditor: <strong className="text-gray-700">{a.auditor}</strong> | Scheduled: {formatDate(a.scheduled_date)}
                </p>
              </div>

              <span className={`px-2.5 py-1 rounded text-[10px] font-bold ${
                a.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {a.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
