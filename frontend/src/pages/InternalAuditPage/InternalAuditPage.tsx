import React, { useEffect, useState } from 'react';
import { InternalAuditCard } from '@/components/internalAudit/InternalAuditCard';
import { createInternalAudit, fetchInternalAuditList } from '@/services/internalAuditService';
import type { InternalAuditRead } from '@/types/internalAudit.types';

export const InternalAuditPage: React.FC = () => {
  const [audits, setAudits] = useState<InternalAuditRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [title, setTitle] = useState('');
  const [auditType] = useState('INTERNAL_SOP');
  const [scope, setScope] = useState('');

  const [leadAuditor, setLeadAuditor] = useState('');
  const [department, setDepartment] = useState('QUALITY_ASSURANCE');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchInternalAuditList({ search: search || undefined });
      setAudits(res.items);
    } catch (err) {
      console.error('Failed to load internal audits:', err);
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
      const now = new Date();
      const end = new Date();
      end.setDate(now.getDate() + 5);

      await createInternalAudit({
        title,
        audit_type: auditType,
        scope,
        lead_auditor: leadAuditor,
        department,
        scheduled_start_date: now.toISOString(),
        scheduled_end_date: end.toISOString(),
      });
      setIsModalOpen(false);
      setTitle('');
      setScope('');
      setLeadAuditor('');
      await loadData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create internal audit.');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
            📋 Enterprise Internal Audit Management
          </h1>
          <p className="text-xs text-gray-500 mt-1">ISO 13485:2016 Cl. 8.2.2 & 21 CFR 820.22 Audit System</p>
        </div>

        <button onClick={() => setIsModalOpen(true)} className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold hover:bg-slate-800">
          ➕ Plan New Internal Audit
        </button>
      </div>

      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 Search audits by number, title, or auditor..."
          className="w-full md:w-96 rounded-lg border-gray-300 border p-2 text-xs"
        />
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-gray-500">Loading audit schedule...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {audits.map((a) => (
            <InternalAuditCard key={a.id} audit={a} />
          ))}
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleCreate} className="bg-white rounded-xl p-6 max-w-md w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">➕ Plan New Internal Audit</h3>

            <div>
              <label className="block font-semibold mb-1">Audit Title *</label>
              <input type="text" required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Annual QMS Compliance Audit" className="w-full rounded border p-2 text-xs" />
            </div>

            <div>
              <label className="block font-semibold mb-1">Audit Scope *</label>
              <textarea required rows={2} value={scope} onChange={(e) => setScope(e.target.value)} placeholder="Define audit boundaries & standards" className="w-full rounded border p-2 text-xs" />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block font-semibold mb-1">Lead Auditor *</label>
                <input type="text" required value={leadAuditor} onChange={(e) => setLeadAuditor(e.target.value)} placeholder="Dr. Aris Thorne" className="w-full rounded border p-2 text-xs" />
              </div>

              <div>
                <label className="block font-semibold mb-1">Department</label>
                <select value={department} onChange={(e) => setDepartment(e.target.value)} className="w-full rounded border p-2 text-xs">
                  <option value="QUALITY_ASSURANCE">QUALITY ASSURANCE</option>
                  <option value="MANUFACTURING">MANUFACTURING</option>

                  <option value="REGULATORY_AFFAIRS">REGULATORY AFFAIRS</option>
                  <option value="R_AND_D">R & D</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-slate-900 text-white font-bold rounded">Plan Audit</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default InternalAuditPage;
