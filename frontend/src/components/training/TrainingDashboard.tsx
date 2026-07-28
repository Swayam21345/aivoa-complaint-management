import React from 'react';
import type { TrainingDashboardRead } from '@/types/training.types';
import { DepartmentComplianceChart } from './DepartmentComplianceChart';

interface TrainingDashboardProps {
  metrics: TrainingDashboardRead;
}

export const TrainingDashboard: React.FC<TrainingDashboardProps> = ({ metrics }) => {
  return (
    <div className="space-y-6">
      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-gray-500">Active Courses</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{metrics.active_courses}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-600">Completion Rate</p>
          <p className="text-2xl font-black text-emerald-700 mt-1">{metrics.completion_rate_percentage}%</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-amber-600">Avg Quiz Score</p>
          <p className="text-2xl font-black text-amber-700 mt-1">{metrics.average_quiz_score}%</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-red-600">Overdue Assignments</p>
          <p className="text-2xl font-black text-red-700 mt-1">{metrics.overdue_assignments}</p>
        </div>
      </div>

      {/* Compliance Chart & Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <DepartmentComplianceChart data={metrics.department_compliance} />

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3">
          <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider border-b pb-2">
            📌 Assignment Status Distribution
          </h3>
          <div className="space-y-2 pt-1 text-xs">
            {Object.entries(metrics.status_distribution).map(([st, cnt]) => (
              <div key={st} className="flex justify-between items-center py-1 border-b border-gray-100">
                <span className="font-medium text-gray-600">{st}</span>
                <span className="font-bold font-mono text-slate-900">{cnt}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
