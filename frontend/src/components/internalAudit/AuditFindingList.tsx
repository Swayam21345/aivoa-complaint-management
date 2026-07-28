import React from 'react';
import type { AuditFindingRead } from '@/types/internalAudit.types';

interface AuditFindingListProps {
  findings: AuditFindingRead[];
}

export const AuditFindingList: React.FC<AuditFindingListProps> = ({ findings }) => {
  const getCategoryBadge = (cat: string) => {
    switch (cat) {
      case 'CRITICAL_NC':
        return <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-red-100 text-red-900 border border-red-300">🔥 CRITICAL NC</span>;
      case 'MAJOR_NC':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-orange-100 text-orange-900 border border-orange-300">⚠️ MAJOR NC</span>;
      case 'MINOR_NC':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300">⚡ MINOR NC</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700">🔍 OBSERVATION</span>;
    }
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3 text-xs">
      <h3 className="font-bold text-gray-800 uppercase tracking-wider text-xs border-b pb-2 flex justify-between items-center">
        <span>🚨 Audit Findings & Nonconformances</span>
        <span className="text-gray-400 font-normal text-[11px]">{findings.length} Logged</span>
      </h3>

      {findings.length === 0 ? (
        <p className="text-gray-400 italic text-center py-4">No audit findings logged.</p>
      ) : (
        <div className="space-y-3">
          {findings.map((f) => (
            <div key={f.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-mono font-bold text-slate-900">{f.finding_number}</span>
                {getCategoryBadge(f.category)}
              </div>

              <p className="text-slate-800 font-medium">{f.description}</p>
              {f.clause_reference && (
                <p className="text-slate-500 text-[11px]">Reference Standard: <span className="font-mono font-bold text-slate-700">{f.clause_reference}</span></p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
