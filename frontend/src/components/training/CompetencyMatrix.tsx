import React from 'react';
import { formatDate } from '@/utils/formatDate';
import type { CompetencyRead } from '@/types/training.types';

interface CompetencyMatrixProps {
  records: CompetencyRead[];
}

export const CompetencyMatrix: React.FC<CompetencyMatrixProps> = ({ records }) => {
  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'EXPERT':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">👑 EXPERT</span>;
      case 'ADVANCED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">⭐ ADVANCED</span>;
      case 'INTERMEDIATE':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">🔷 INTERMEDIATE</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">🌱 BEGINNER</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden text-xs">
      <div className="p-4 border-b border-gray-200 bg-gray-50/50 flex justify-between items-center">
        <h3 className="font-bold text-gray-800 uppercase tracking-wider text-xs flex items-center gap-2">
          🏅 Competency & Skill Matrix
        </h3>
        <span className="text-gray-500 font-medium text-[11px]">{records.length} Verified Records</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-gray-50 text-gray-700 uppercase text-[10px] font-bold border-b border-gray-200">
            <tr>
              <th className="py-3 px-4">Employee</th>
              <th className="py-3 px-4">Skill / Competency</th>
              <th className="py-3 px-4">Level</th>
              <th className="py-3 px-4">Verified By</th>
              <th className="py-3 px-4">Verification Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {records.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-6 text-center text-gray-400">No competency records found.</td>
              </tr>
            ) : (
              records.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50/80 transition-colors">
                  <td className="py-3 px-4 font-bold text-gray-900">{r.user_full_name || 'Employee'}</td>
                  <td className="py-3 px-4 font-semibold text-slate-800">{r.skill}</td>
                  <td className="py-3 px-4">{getLevelBadge(r.level)}</td>
                  <td className="py-3 px-4 text-gray-600">{r.verified_by}</td>
                  <td className="py-3 px-4 text-gray-500">{formatDate(r.verified_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
