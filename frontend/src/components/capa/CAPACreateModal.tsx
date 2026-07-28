import { useState } from 'react';
import type { FormEvent } from 'react';
import { createCAPA } from '@/services/capaService';
import type { CAPAPriority, CAPARead, CAPARiskLevel } from '@/types/capa.types';

interface Props {
  complaintId: string;
  complaintNumber?: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (capa: CAPARead) => void;
}

export function CAPACreateModal({
  complaintId,
  complaintNumber,
  isOpen,
  onClose,
  onSuccess,
}: Props) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [rootCause, setRootCause] = useState('');
  const [correctiveAction, setCorrectiveAction] = useState('');
  const [preventiveAction, setPreventiveAction] = useState('');
  const [owner, setOwner] = useState('');
  const [priority, setPriority] = useState<CAPAPriority>('High');
  const [riskLevel, setRiskLevel] = useState<CAPARiskLevel>('High');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const capa = await createCAPA({
        complaint_id: complaintId,
        title: title.trim(),
        description: description.trim(),
        root_cause: rootCause.trim() || undefined,
        corrective_action: correctiveAction.trim() || undefined,
        preventive_action: preventiveAction.trim() || undefined,
        owner: owner.trim() || undefined,
        priority,
        risk_level: riskLevel,
      });
      onSuccess(capa);
      onClose();
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: { detail?: string } } };
      setError(apiErr?.response?.data?.detail || 'Failed to create CAPA record.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-700 to-indigo-900 px-6 py-4 flex justify-between items-center text-white">
          <div>
            <h2 className="font-bold text-base">🛡️ Create CAPA Plan</h2>
            {complaintNumber && (
              <p className="text-blue-200 text-xs mt-0.5">Linked to Complaint {complaintNumber}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:text-gray-300 text-xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto text-xs">
          <div>
            <label htmlFor="capa-title" className="block font-semibold text-gray-700 mb-1">
              CAPA Title *
            </label>
            <input
              id="capa-title"
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="e.g. Line 3 Temperature Sensor Recalibration & Sealed Lot Audit"
            />
          </div>

          <div>
            <label htmlFor="capa-desc" className="block font-semibold text-gray-700 mb-1">
              Problem / Deviation Description *
            </label>
            <textarea
              id="capa-desc"
              required
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Detailed explanation of quality defect or non-conformance..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="capa-rc" className="block font-semibold text-gray-700 mb-1">
                Root Cause Analysis
              </label>
              <textarea
                id="capa-rc"
                rows={2}
                value={rootCause}
                onChange={(e) => setRootCause(e.target.value)}
                className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Identified root cause findings..."
              />
            </div>
            <div>
              <label htmlFor="capa-owner" className="block font-semibold text-gray-700 mb-1">
                Implementation Owner
              </label>
              <input
                id="capa-owner"
                type="text"
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g. Dr. Jane Smith"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="capa-ca" className="block font-semibold text-gray-700 mb-1">
                Immediate Corrective Action
              </label>
              <textarea
                id="capa-ca"
                rows={2}
                value={correctiveAction}
                onChange={(e) => setCorrectiveAction(e.target.value)}
                className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Immediate containment actions taken..."
              />
            </div>
            <div>
              <label htmlFor="capa-pa" className="block font-semibold text-gray-700 mb-1">
                Long-Term Preventive Action
              </label>
              <textarea
                id="capa-pa"
                rows={2}
                value={preventiveAction}
                onChange={(e) => setPreventiveAction(e.target.value)}
                className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Preventive engineering or SOP controls..."
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="capa-prio" className="block font-semibold text-gray-700 mb-1">
                Priority
              </label>
              <select
                id="capa-prio"
                value={priority}
                onChange={(e) => setPriority(e.target.value as CAPAPriority)}
                className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            <div>
              <label htmlFor="capa-risk" className="block font-semibold text-gray-700 mb-1">
                Risk Level
              </label>
              <select
                id="capa-risk"
                value={riskLevel}
                onChange={(e) => setRiskLevel(e.target.value as CAPARiskLevel)}
                className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
              >
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>

          {error && <p className="text-red-600 font-semibold text-xs">{error}</p>}

          <div className="flex gap-3 pt-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 hover:bg-gray-50 py-2 rounded font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !title.trim() || !description.trim()}
              className="flex-1 bg-blue-700 hover:bg-blue-800 disabled:bg-gray-300 text-white font-bold py-2 rounded transition-colors"
            >
              {isSubmitting ? 'Creating...' : 'Create CAPA Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
