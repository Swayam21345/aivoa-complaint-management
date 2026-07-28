import React from 'react';
import type { AuditChecklistRead } from '@/types/internalAudit.types';

interface AuditChecklistProps {
  checklists: AuditChecklistRead[];
}

export const AuditChecklist: React.FC<AuditChecklistProps> = ({ checklists }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3 text-xs">
      <h3 className="font-bold text-gray-800 uppercase tracking-wider text-xs border-b pb-2 flex justify-between items-center">
        <span>📋 Audit Verification Checklist</span>
        <span className="text-gray-400 font-normal text-[11px]">{checklists.length} Criteria</span>
      </h3>

      {checklists.length === 0 ? (
        <p className="text-gray-400 italic text-center py-4">No checklist criteria logged.</p>
      ) : (
        <div className="space-y-2">
          {checklists.map((c) => (
            <div key={c.id} className="p-3 bg-white border border-gray-200 rounded-lg flex justify-between items-start">
              <div className="space-y-1">
                <span className="font-bold text-slate-900">{c.section}: {c.requirement}</span>
                <p className="text-gray-600 text-[11px]">{c.question}</p>
                {c.comments && <p className="text-gray-500 italic text-[10px]">Note: {c.comments}</p>}
              </div>

              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                c.compliance_status === 'COMPLIANT' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
              }`}>
                {c.compliance_status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
