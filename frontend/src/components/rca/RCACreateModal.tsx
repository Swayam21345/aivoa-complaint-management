import React, { useState } from 'react';
import { createRCA } from '@/services/rcaService';
import type { RCACreatePayload } from '@/types/rca.types';

interface RCACreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  complaintId: string;
  onSuccess: () => void;
}

export const RCACreateModal: React.FC<RCACreateModalProps> = ({
  isOpen,
  onClose,
  complaintId,
  onSuccess,
}) => {
  const [primaryCause, setPrimaryCause] = useState('');
  const [category, setCategory] = useState('Equipment Failure');
  const [methodology, setMethodology] = useState<'FIVE_WHYS' | 'FISHBONE' | 'HYBRID'>('HYBRID');

  // FMEA line item
  const [failureMode, setFailureMode] = useState('');
  const [effect, setEffect] = useState('');
  const [severity, setSeverity] = useState(5);
  const [occurrence, setOccurrence] = useState(4);
  const [detection, setDetection] = useState(3);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const calculatedRPN = severity * occurrence * detection;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!primaryCause.trim()) {
      setError('Primary root cause is required.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const payload: RCACreatePayload = {
        complaint_id: complaintId,
        primary_root_cause: primaryCause,
        root_cause_category: category,
        methodology,
        fmea_items: failureMode
          ? [
              {
                failure_mode: failureMode,
                effect_of_failure: effect || 'Process breakdown',
                severity,
                occurrence,
                detection,
              },
            ]
          : [],
      };

      await createRCA(payload);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create RCA investigation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-xl w-full border border-gray-100 overflow-hidden my-8">
        <div className="bg-slate-900 text-white p-4 flex items-center justify-between border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold flex items-center gap-2">
              🔬 Initiate Root Cause Analysis (RCA)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              TrackWise / Veeva QMS Compliant Failure Investigation
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-lg font-bold px-2 py-1 rounded"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          {error && (
            <div className="p-3 rounded-lg bg-red-50 text-red-700 border border-red-200 font-medium">
              ⚠️ {error}
            </div>
          )}

          <div>
            <label className="block font-semibold text-gray-700 mb-1">
              Primary Root Cause Finding <span className="text-red-500">*</span>
            </label>
            <textarea
              required
              rows={3}
              value={primaryCause}
              onChange={(e) => setPrimaryCause(e.target.value)}
              placeholder="e.g. Degradation of thermal printer head roller causing illegible expiration date print..."
              className="w-full rounded-lg border-gray-300 border p-2.5 text-xs focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Root Cause Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full rounded-lg border-gray-300 border p-2 text-xs"
              >
                <option value="Equipment Failure">⚙️ Equipment Failure</option>
                <option value="Human Error">👨‍🔧 Human Error</option>
                <option value="Raw Material Defect">📦 Raw Material Defect</option>
                <option value="SOP Non-compliance">📋 SOP Non-compliance</option>
                <option value="Environmental">🌱 Environmental</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">Methodology</label>
              <select
                value={methodology}
                onChange={(e) => setMethodology(e.target.value as any)}
                className="w-full rounded-lg border-gray-300 border p-2 text-xs"
              >
                <option value="HYBRID">🔀 Hybrid (5 Whys + Fishbone)</option>
                <option value="FIVE_WHYS">❓ 5 Whys</option>
                <option value="FISHBONE">🐟 6M Fishbone</option>
              </select>
            </div>
          </div>

          <hr className="border-gray-200" />

          {/* FMEA Quick Add */}
          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 space-y-3">
            <h4 className="font-bold text-slate-800 flex items-center justify-between text-xs">
              <span>📊 Initial FMEA Line Item</span>
              <span className="text-[10px] text-slate-500">Calculated RPN: {calculatedRPN}</span>
            </h4>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Failure Mode</label>
              <input
                type="text"
                value={failureMode}
                onChange={(e) => setFailureMode(e.target.value)}
                placeholder="e.g. Faint expiry print"
                className="w-full rounded border-gray-300 border p-2 text-xs bg-white"
              />
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Effect of Failure</label>
              <input
                type="text"
                value={effect}
                onChange={(e) => setEffect(e.target.value)}
                placeholder="e.g. Patient safety issue"
                className="w-full rounded border-gray-300 border p-2 text-xs bg-white"
              />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-[10px] font-semibold text-slate-600">
                  Severity (1-10)
                </label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={severity}
                  onChange={(e) => setSeverity(Number(e.target.value))}
                  className="w-full rounded border-gray-300 border p-1.5 text-xs text-center bg-white"
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-slate-600">
                  Occurrence (1-10)
                </label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={occurrence}
                  onChange={(e) => setOccurrence(Number(e.target.value))}
                  className="w-full rounded border-gray-300 border p-1.5 text-xs text-center bg-white"
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-slate-600">
                  Detection (1-10)
                </label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={detection}
                  onChange={(e) => setDetection(Number(e.target.value))}
                  className="w-full rounded border-gray-300 border p-1.5 text-xs text-center bg-white"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-lg text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 transition-colors shadow-md disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create RCA Investigation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
