import React, { useEffect, useState } from 'react';
import { SupplierDashboard } from '@/components/supplier/SupplierDashboard';
import { fetchSupplierDashboard } from '@/services/supplierService';
import type { SupplierDashboardRead } from '@/types/supplier.types';

export const SupplierDashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<SupplierDashboardRead | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSupplierDashboard()
      .then(setMetrics)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center text-xs text-gray-500">Loading SQM Dashboard...</div>;
  if (!metrics) return <div className="p-8 text-center text-xs text-red-500">Failed to load dashboard.</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-black text-gray-900">📊 Supplier Quality Performance Analytics</h1>
        <p className="text-xs text-gray-500 mt-1">Real-time GxP Vendor Risk Metrics & Scorecard Tracking</p>
      </div>

      <SupplierDashboard metrics={metrics} />
    </div>
  );
};

export default SupplierDashboardPage;
