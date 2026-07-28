import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ElectronicSignatureModal from '@/components/complaint/ElectronicSignatureModal/ElectronicSignatureModal';
import { AuditChecklist } from '@/components/internalAudit/AuditChecklist';
import { AuditFindingList } from '@/components/internalAudit/AuditFindingList';
import {
  addAuditChecklistItem,
  addAuditFinding,
  fetchInternalAuditDetail,
} from '@/services/internalAuditService';
import type { InternalAuditRead } from '@/types/internalAudit.types';

export const InternalAuditDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [audit, setAudit] = useState<InternalAuditRead | null>(null);
  const [loading, setLoading] = useState(true);

  const [isApproveOpen, setIsApproveOpen] = useState(false);
  const [isChkOpen, setIsChkOpen] = useState(false);
  const [isFindingOpen, setIsFindingOpen] = useState(false);

  // Forms
  const [section, setSection] = useState('Cl. 8.2');
  const [requirement, setRequirement] = useState('Quality Records Retention');
  const [question, setQuestion] = useState('Are audit records retained for min 5 years?');

  const [findingCat, setFindingCat] = useState('MAJOR_NC');
  const [findingDesc, setFindingDesc] = useState('');
  const [clauseRef, setClauseRef] = useState('ISO 13485:2016 Cl. 8.2.2');

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await fetchInternalAuditDetail(id);
      setAudit(data);
    } catch (err) {
      console.error('Failed to load audit detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleChecklist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    await addAuditChecklistItem(id, section, requirement, question, 'COMPLIANT');
    setIsChkOpen(false);
    await loadData();
  };

  const handleFinding = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    await addAuditFinding(id, findingCat, findingDesc, clauseRef);
    setIsFindingOpen(false);
    await loadData();
  };

  if (loading) return <div className="p-8 text-center text-xs text-gray-500">Loading audit detail...</div>;
  if (!audit) return <div className="p-8 text-center text-xs text-red-500">Internal Audit record not found.</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-gray-900">{audit.audit_number}</h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
              audit.status === 'CLOSED' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
            }`}>
              {audit.status}
            </span>
          </div>
          <p className="text-sm font-bold text-gray-800 mt-1">{audit.title}</p>
        </div>

        <div className="flex items-center gap-2">
          {audit.status !== 'CLOSED' && (
            <button onClick={() => setIsApproveOpen(true)} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700">
              ✍️ Signoff & Close Audit
            </button>
          )}

          <button onClick={() => setIsChkOpen(true)} className="px-3 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold">
            📋 Add Checklist Item
          </button>
          <button onClick={() => setIsFindingOpen(true)} className="px-3 py-2 bg-red-100 text-red-800 rounded-lg text-xs font-bold border border-red-200">
            🚨 Log Finding
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <AuditFindingList findings={audit.findings} />
          <AuditChecklist checklists={audit.checklists} />
        </div>

        <div className="space-y-6 text-xs">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-2">
            <h4 className="font-bold text-gray-800 uppercase tracking-wider text-[11px] border-b pb-2">
              ℹ️ Audit Overview
            </h4>
            <p><strong className="text-gray-500">Lead Auditor:</strong> {audit.lead_auditor}</p>
            <p><strong className="text-gray-500">Department:</strong> {audit.department}</p>
            <p><strong className="text-gray-500">Type:</strong> {audit.audit_type}</p>
            <p><strong className="text-gray-500">Scope:</strong> {audit.scope}</p>
          </div>
        </div>
      </div>

      {/* Modals */}
      {isChkOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleChecklist} className="bg-white rounded-xl p-6 max-w-md w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">📋 Add Verification Criteria</h3>
            <div>
              <label className="block font-semibold mb-1">Section *</label>
              <input type="text" required value={section} onChange={(e) => setSection(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div>
              <label className="block font-semibold mb-1">Requirement *</label>
              <input type="text" required value={requirement} onChange={(e) => setRequirement(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div>
              <label className="block font-semibold mb-1">Audit Question *</label>
              <textarea required rows={2} value={question} onChange={(e) => setQuestion(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsChkOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-slate-900 text-white font-bold rounded">Add Criteria</button>
            </div>
          </form>
        </div>
      )}

      {isFindingOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleFinding} className="bg-white rounded-xl p-6 max-w-md w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">🚨 Log Nonconformance / Finding</h3>
            <div>
              <label className="block font-semibold mb-1">Category *</label>
              <select value={findingCat} onChange={(e) => setFindingCat(e.target.value)} className="w-full rounded border p-2 text-xs">
                <option value="CRITICAL_NC">CRITICAL NC</option>
                <option value="MAJOR_NC">MAJOR NC</option>
                <option value="MINOR_NC">MINOR NC</option>
                <option value="OBSERVATION">OBSERVATION</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold mb-1">Finding Description *</label>
              <textarea required rows={3} value={findingDesc} onChange={(e) => setFindingDesc(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div>
              <label className="block font-semibold mb-1">Standard Clause Reference</label>
              <input type="text" value={clauseRef} onChange={(e) => setClauseRef(e.target.value)} className="w-full rounded border p-2 text-xs" />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsFindingOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-red-800 text-white font-bold rounded">Log Finding</button>
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
        complaintId={audit.id}
        complaintNumber={audit.audit_number}
        currentStatus={audit.status}
        targetStatus="CLOSED"
      />
    </div>
  );
};

export default InternalAuditDetailPage;
