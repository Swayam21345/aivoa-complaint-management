import React from 'react';

interface DepartmentComplianceChartProps {
  data: Record<string, number>;
}

export const DepartmentComplianceChart: React.FC<DepartmentComplianceChartProps> = ({ data }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3">
      <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider border-b pb-2">
        📊 Department GxP Compliance Rates
      </h3>
      <div className="space-y-3 pt-1">
        {Object.entries(data).map(([dept, pct]) => (
          <div key={dept} className="space-y-1">
            <div className="flex justify-between text-xs font-semibold text-gray-700">
              <span>{dept}</span>
              <span className="font-mono text-emerald-700 font-bold">{pct}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden border border-slate-200">
              <div
                className="bg-emerald-600 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
