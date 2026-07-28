import React from 'react';
import type { SupplierScorecardRead } from '@/types/supplier.types';

interface SupplierScorecardProps {
  scorecards: SupplierScorecardRead[];
}

export const SupplierScorecard: React.FC<SupplierScorecardProps> = ({ scorecards }) => {
  const getGradeBadge = (grade: string) => {
    switch (grade) {
      case 'A':
        return <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold border border-emerald-300">Grade A (Excellent)</span>;
      case 'B':
        return <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold border border-blue-300">Grade B (Good)</span>;
      case 'C':
        return <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold border border-amber-300">Grade C (Satisfactory)</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-red-100 text-red-800 font-bold border border-red-300">Grade {grade} (Unsatisfactory)</span>;
    }
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-4 text-xs">
      <h3 className="font-bold text-gray-800 uppercase tracking-wider text-xs border-b pb-2 flex items-center justify-between">
        <span>📈 Quarterly Performance Scorecards</span>
        <span className="text-gray-400 font-normal text-[11px]">{scorecards.length} Evaluated Periods</span>
      </h3>

      {scorecards.length === 0 ? (
        <p className="text-gray-400 italic text-center py-4">No scorecards recorded yet.</p>
      ) : (
        <div className="space-y-3">
          {scorecards.map((sc) => (
            <div key={sc.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-bold font-mono text-slate-900 text-sm">{sc.period}</span>
                {getGradeBadge(sc.grade)}
              </div>

              <div className="grid grid-cols-4 gap-2 pt-1 text-[11px] text-center">
                <div className="bg-white p-2 rounded border border-slate-200">
                  <p className="text-gray-500 font-medium">Quality (40%)</p>
                  <p className="font-bold font-mono text-emerald-700 mt-0.5">{sc.quality_score}%</p>
                </div>

                <div className="bg-white p-2 rounded border border-slate-200">
                  <p className="text-gray-500 font-medium">Delivery (30%)</p>
                  <p className="font-bold font-mono text-blue-700 mt-0.5">{sc.delivery_score}%</p>
                </div>

                <div className="bg-white p-2 rounded border border-slate-200">
                  <p className="text-gray-500 font-medium">Compliance (30%)</p>
                  <p className="font-bold font-mono text-purple-700 mt-0.5">{sc.compliance_score}%</p>
                </div>

                <div className="bg-slate-900 text-cyan-400 p-2 rounded font-bold">
                  <p className="text-slate-400 font-medium">Overall Score</p>
                  <p className="text-sm mt-0.5">{sc.overall_score}%</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
