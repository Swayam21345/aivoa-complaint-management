import React, { useEffect, useState } from 'react';
import { SupplierCard } from '@/components/supplier/SupplierCard';
import { createSupplier, fetchSupplierList } from '@/services/supplierService';
import type { SupplierRead } from '@/types/supplier.types';

export const SupplierPage: React.FC = () => {
  const [suppliers, setSuppliers] = useState<SupplierRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [supplierName, setSupplierName] = useState('');
  const [supplierType, setSupplierType] = useState('RAW_MATERIAL');
  const [riskLevel, setRiskLevel] = useState('MEDIUM');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchSupplierList({ search: search || undefined });
      setSuppliers(res.items);
    } catch (err) {
      console.error('Failed to load suppliers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createSupplier({
        supplier_name: supplierName,
        supplier_type: supplierType,
        risk_level: riskLevel,
      });
      setIsModalOpen(false);
      setSupplierName('');
      await loadData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create supplier.');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
            🏭 Enterprise Supplier Quality Management (SQM)
          </h1>
          <p className="text-xs text-gray-500 mt-1">ISO 13485 & 21 CFR Part 820 Vendor Qualification Workspace</p>
        </div>

        <button onClick={() => setIsModalOpen(true)} className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold hover:bg-slate-800">
          ➕ Register New Supplier
        </button>
      </div>

      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 Search suppliers by number, name, or email..."
          className="w-full md:w-96 rounded-lg border-gray-300 border p-2 text-xs"
        />
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-gray-500">Loading supplier records...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {suppliers.map((s) => (
            <SupplierCard key={s.id} supplier={s} />
          ))}
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleCreate} className="bg-white rounded-xl p-6 max-w-md w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">➕ Register New Supplier</h3>

            <div>
              <label className="block font-semibold mb-1">Supplier Name *</label>
              <input type="text" required value={supplierName} onChange={(e) => setSupplierName(e.target.value)} placeholder="e.g. PharmaChem Global Synthetics" className="w-full rounded border p-2 text-xs" />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block font-semibold mb-1">Supplier Type</label>
                <select value={supplierType} onChange={(e) => setSupplierType(e.target.value)} className="w-full rounded border p-2 text-xs">
                  <option value="RAW_MATERIAL">RAW MATERIAL</option>
                  <option value="COMPONENT">COMPONENT</option>
                  <option value="CONTRACT_MANUFACTURER">CONTRACT MANUFACTURER</option>
                  <option value="PACKAGING">PACKAGING</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1">Risk Level</label>
                <select value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)} className="w-full rounded border p-2 text-xs">
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-slate-900 text-white font-bold rounded">Register Supplier</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default SupplierPage;
