import React from 'react';

interface SupplierRiskBadgeProps {
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
}

export const SupplierRiskBadge: React.FC<SupplierRiskBadgeProps> = ({ level }) => {
  switch (level) {
    case 'CRITICAL':
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-900 border border-red-300">
          🔥 CRITICAL RISK
        </span>
      );
    case 'HIGH':
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-orange-900 border border-orange-300">
          ⚠️ HIGH RISK
        </span>
      );
    case 'MEDIUM':
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
          ⚡ MEDIUM RISK
        </span>
      );
    default:
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
          🛡️ LOW RISK
        </span>
      );
  }
};
