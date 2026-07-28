import React from 'react';
import { Link } from 'react-router-dom';
import type { SupplierRead } from '@/types/supplier.types';
import { SupplierRiskBadge } from './SupplierRiskBadge';

interface SupplierCardProps {
  supplier: SupplierRead;
}

export const SupplierCard: React.FC<SupplierCardProps> = ({ supplier }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow space-y-3 flex flex-col justify-between text-xs">
      <div>
        <div className="flex justify-between items-start gap-2 mb-2">
          <span className="font-mono font-bold text-xs text-primary-700 bg-primary-50 px-2 py-0.5 rounded border border-primary-200">
            {supplier.supplier_number}
          </span>
          <SupplierRiskBadge level={supplier.risk_level} />
        </div>

        <h3 className="font-bold text-gray-900 text-sm line-clamp-1">{supplier.supplier_name}</h3>
        <p className="text-gray-500 text-[11px] mt-0.5">Type: <span className="font-semibold text-gray-700">{supplier.supplier_type}</span></p>
      </div>

      <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
          supplier.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
        }`}>
          {supplier.status}
        </span>

        <Link
          to={`/suppliers/${supplier.id}`}
          className="px-3 py-1.5 bg-slate-900 text-white font-semibold rounded-lg hover:bg-slate-800 transition-colors text-xs"
        >
          View Supplier →
        </Link>
      </div>
    </div>
  );
};
