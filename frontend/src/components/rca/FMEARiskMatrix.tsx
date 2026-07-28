import React from 'react';
import type { FMEAAssessmentRead } from '@/types/rca.types';

interface FMEARiskMatrixProps {
  items: FMEAAssessmentRead[];
}

export const FMEARiskMatrix: React.FC<FMEARiskMatrixProps> = ({ items }) => {
  if (!items || items.length === 0) {
    return <div className="text-xs text-gray-500 italic p-4">No FMEA risk items recorded.</div>;
  }

  const getRiskBadge = (rpn: number, riskClass: string) => {
    if (riskClass === 'High' || rpn >= 200) {
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200 shadow-sm">
          🚨 High ({rpn})
        </span>
      );
    }
    if (riskClass === 'Medium' || rpn >= 100) {
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
          ⚠️ Med ({rpn})
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
        ✅ Low ({rpn})
      </span>
    );
  };

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg shadow-sm">
      <table className="w-full text-xs text-left border-collapse">
        <thead className="bg-gray-50 text-gray-700 uppercase text-[10px] font-bold tracking-wider border-b border-gray-200">
          <tr>
            <th className="py-2.5 px-3">Failure Mode</th>
            <th className="py-2.5 px-3">Effect of Failure</th>
            <th className="py-2.5 px-2 text-center" title="Severity (1-10)">
              S
            </th>
            <th className="py-2.5 px-2 text-center" title="Occurrence (1-10)">
              O
            </th>
            <th className="py-2.5 px-2 text-center" title="Detection (1-10)">
              D
            </th>
            <th className="py-2.5 px-3 text-center">RPN Score</th>
            <th className="py-2.5 px-3">Recommended Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {items.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50/80 transition-colors">
              <td className="py-2.5 px-3 font-semibold text-gray-900">{item.failure_mode}</td>
              <td className="py-2.5 px-3 text-gray-600 max-w-xs">{item.effect_of_failure}</td>
              <td className="py-2.5 px-2 text-center font-mono font-bold text-gray-700">
                {item.severity}
              </td>
              <td className="py-2.5 px-2 text-center font-mono font-bold text-gray-700">
                {item.occurrence}
              </td>
              <td className="py-2.5 px-2 text-center font-mono font-bold text-gray-700">
                {item.detection}
              </td>
              <td className="py-2.5 px-3 text-center font-semibold">
                {getRiskBadge(item.rpn, item.risk_class)}
              </td>
              <td className="py-2.5 px-3 text-gray-600 italic">
                {item.recommended_action || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
