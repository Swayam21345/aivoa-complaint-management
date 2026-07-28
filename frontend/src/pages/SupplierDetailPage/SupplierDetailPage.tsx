import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ElectronicSignatureModal from '@/components/complaint/ElectronicSignatureModal/ElectronicSignatureModal';
import { SupplierAuditTimeline } from '@/components/supplier/SupplierAuditTimeline';
import { SupplierRiskBadge } from '@/components/supplier/SupplierRiskBadge';
import { SupplierScorecard } from '@/components/supplier/SupplierScorecard';
import {
  addSupplierNonconformance,
  addSupplierScorecard,
  fetchSupplierDetail,
  scheduleSupplierAudit,
} from '@/services/supplierService';

import type { SupplierRead } from '@/types/supplier.types';

export const SupplierDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [supplier, setSupplier] = useState<SupplierRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [isApproveOpen, setIsApproveOpen] = useState(false);

  // Sub-entity creation modals
  const [isAuditOpen, setIsAuditOpen] = useState(false);
  const [isScorecardOpen, setIsScorecardOpen] = useState(false);
  const [isNcrOpen, setIsNcrOpen] = useState(false);

  // Form states
  const [auditor, setAuditor] = useState('');
  const [scPeriod, setScPeriod] = useState('2026-Q1');
  const [qScore, setQScore] = useState(95);
  const [dScore, setDScore] = useState(90);
  const [cScore, setCScore] = useState(100);

  const [ncrTitle, setNcrTitle] = useState('');
  const [ncrDesc, setNcrDesc] = useState('');

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await fetchSupplierDetail(id);
      setSupplier(data);
    } catch (err) {
      console.error('Failed to load supplier detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    await scheduleSupplierAudit(id, 'QUALIFICATION', new Date().toISOString(), auditor);
    setIsAuditOpen(false);
    await loadData();
  };

  const handleScorecard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    await addSupplierScorecard(id, scPeriod, qScore, dScore, cScore);
    setIsScorecardOpen(false);
    await loadData();
  };

  const handleNcr = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    await addSupplierNonconformance(id, ncrTitle, ncrDesc, 'MAJOR');
    setIsNcrOpen(false);
    await loadData();
  };

  if (loading) return <div className="p-8 text-center text-xs text-gray-500">Loading supplier detail...</div>;
  if (!supplier) return <div className="p-8 text-center text-xs text-red-500">Supplier not found.</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-gray-900">{supplier.supplier_number}</h1>
            <SupplierRiskBadge level={supplier.risk_level} />
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
              supplier.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
            }`}>
              {supplier.status}
            </span>
          </div>
          <p className="text-sm font-bold text-gray-800 mt-1">{supplier.supplier_name}</p>
        </div>

        <div className="flex items-center gap-2">
          {supplier.status !== 'APPROVED' && (
            <button onClick={() => setIsApproveOpen(true)} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700">
              ✍️ Approve Qualification
            </button>
          )}

          <button onClick={() => setIsAuditOpen(true)} className="px-3 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold">
            📅 Schedule Audit
          </button>
          <button onClick={() => setIsScorecardOpen(true)} className="px-3 py-2 bg-slate-100 text-slate-800 rounded-lg text-xs font-semibold border border-slate-300">
            📊 Add Scorecard
          </button>
          <button onClick={() => setIsNcrOpen(true)} className="px-3 py-2 bg-red-100 text-red-800 rounded-lg text-xs font-bold border border-red-200">
            ⚠️ Log Nonconformance
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <SupplierScorecard scorecards={supplier.scorecards} />
          <SupplierAuditTimeline audits={supplier.audits} />
        </div>

        <div className="space-y-6 text-xs">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-2">
            <h4 className="font-bold text-gray-800 uppercase tracking-wider text-[11px] border-b pb-2">
              ℹ️ Vendor Details
            </h4>
            <p><strong className="text-gray-500">Type:</strong> {supplier.supplier_type}</p>
            <p><strong className="text-gray-500">Category:</strong> {supplier.category}</p>
            <p><strong className="text-gray-500">Email:</strong> {supplier.email || 'N/A'}</p>
            <p><strong className="text-gray-500">Phone:</strong> {supplier.phone || 'N/A'}</p>
            <p><strong className="text-gray-500">Address:</strong> {supplier.address || 'N/A'}, {supplier.city}, {supplier.country}</p>
          </div>
        </div>
      </div>

      {/* Modals */}
      {isAuditOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleAudit} className="bg-white rounded-xl p-6 max-w-md w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">📅 Schedule Quality Audit</h3>
            <div>
              <label className="block font-semibold mb-1">Auditor Name *</label>
              <input type="text" required value={auditor} onChange={(e) => setAuditor(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsAuditOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-slate-900 text-white font-bold rounded">Schedule</button>
            </div>
          </form>
        </div>
      )}

      {isScorecardOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleScorecard} className="bg-white rounded-xl p-6 max-w-md w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">📊 Add Quarterly Scorecard</h3>
            <div>
              <label className="block font-semibold mb-1">Period *</label>
              <input type="text" required value={scPeriod} onChange={(e) => setScPeriod(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block font-semibold mb-1">Quality %</label>
                <input type="number" value={qScore} onChange={(e) => setQScore(Number(e.target.value))} className="w-full rounded border p-2 text-xs" />
              </div>
              <div>
                <label className="block font-semibold mb-1">Delivery %</label>
                <input type="number" value={dScore} onChange={(e) => setDScore(Number(e.target.value))} className="w-full rounded border p-2 text-xs" />
              </div>
              <div>
                <label className="block font-semibold mb-1">Compliance %</label>
                <input type="number" value={cScore} onChange={(e) => setCScore(Number(e.target.value))} className="w-full rounded border p-2 text-xs" />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsScorecardOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-slate-900 text-white font-bold rounded">Save Scorecard</button>
            </div>
          </form>
        </div>
      )}

      {isNcrOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleNcr} className="bg-white rounded-xl p-6 max-w-md w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">⚠️ Log Nonconformance Report (NCR)</h3>
            <div>
              <label className="block font-semibold mb-1">Title *</label>
              <input type="text" required value={ncrTitle} onChange={(e) => setNcrTitle(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div>
              <label className="block font-semibold mb-1">Description *</label>
              <textarea required rows={2} value={ncrDesc} onChange={(e) => setNcrDesc(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsNcrOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-red-800 text-white font-bold rounded">Log NCR</button>
            </div>
          </form>
        </div>
      )}

      <ElectronicSignatureModal
        isOpen={isApproveOpen}
        onClose={() => setIsApproveOpen(false)}
        onSuccess={() => {
          setIsApproveOpen(false);
          loadData();
        }}
        complaintId={supplier.id}
        complaintNumber={supplier.supplier_number}
        currentStatus={supplier.status}
        targetStatus="APPROVED"
      />
    </div>
  );
};

export default SupplierDetailPage;
