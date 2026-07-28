/**
 * ElectronicSignatureModal.tsx
 * 21 CFR Part 11 Electronic Signature Component
 *
 * Renders a secure signature dialog that:
 *  1. Re-authenticates the user's password
 *  2. Collects a mandatory reason / rationale
 *  3. Displays the target workflow status transition
 *  4. Posts to POST /api/complaints/{id}/sign
 *  5. Shows the resulting cryptographic SHA-256 hash
 */

import { useState, useRef, useEffect } from 'react';
import type { FormEvent } from 'react';
import { signComplaint } from '@/services/complaintService';
import type { ElectronicSignatureResponse } from '@/types/complaint.types';

interface Props {
  complaintId: string;
  complaintNumber: string;
  currentStatus: string;
  targetStatus: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (response: ElectronicSignatureResponse) => void;
}

const STATUS_LABELS: Record<string, string> = {
  QA_APPROVED: '✅ QA Approved',
  CLOSED: '🔒 Closed',
};

export default function ElectronicSignatureModal({
  complaintId,
  complaintNumber,
  currentStatus,
  targetStatus,
  isOpen,
  onClose,
  onSuccess,
}: Props) {
  const [password, setPassword] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<ElectronicSignatureResponse | null>(null);

  const passwordRef = useRef<HTMLInputElement>(null);

  // Auto-focus password field when modal opens
  useEffect(() => {
    if (isOpen) {
      setPassword('');
      setReason('');
      setError(null);
      setSuccess(null);
      setTimeout(() => passwordRef.current?.focus(), 80);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!password || !reason.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await signComplaint(complaintId, {
        password,
        reason: reason.trim(),
        target_status: targetStatus,
      });
      setSuccess(response);
      onSuccess(response);
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: { detail?: string } } };
      setError(
        apiErr?.response?.data?.detail ||
          'Electronic signature failed. Please verify your password and try again.',
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleClose() {
    if (!isSubmitting) {
      onClose();
    }
  }

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="esig-modal-title"
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        {/* ── Header ─────────────────────────────────────────────────── */}
        <div className="bg-gradient-to-r from-blue-700 to-blue-900 px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h2
                id="esig-modal-title"
                className="text-white font-bold text-base tracking-wide"
              >
                🔏 21 CFR Part 11 Electronic Signature
              </h2>
              <p className="text-blue-200 text-xs mt-0.5">
                Complaint {complaintNumber} · Legally Binding Authorization
              </p>
            </div>
            {!success && (
              <button
                type="button"
                onClick={handleClose}
                disabled={isSubmitting}
                className="text-blue-200 hover:text-white text-xl leading-none disabled:opacity-50"
                aria-label="Close modal"
              >
                ×
              </button>
            )}
          </div>
        </div>

        {/* ── Success State ───────────────────────────────────────────── */}
        {success ? (
          <div className="p-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-5 text-center">
              <div className="text-4xl mb-3">✅</div>
              <h3 className="font-bold text-green-900 text-sm mb-1">
                Electronic Signature Successfully Recorded
              </h3>
              <p className="text-green-700 text-xs mb-4">
                Signed by <strong>{success.signed_by}</strong> at{' '}
                {new Date(success.timestamp).toLocaleString()}
              </p>
              <div className="bg-white border border-green-200 rounded p-3 text-left mb-4">
                <p className="text-[10px] font-bold text-gray-500 uppercase mb-1">
                  SHA-256 Cryptographic Hash
                </p>
                <p className="font-mono text-[10px] text-gray-700 break-all">{success.hash}</p>
              </div>
              <p className="text-[11px] text-gray-500">
                Signature ID: <span className="font-mono">{success.signature_id}</span>
              </p>
            </div>
            <button
              type="button"
              onClick={handleClose}
              className="mt-4 w-full bg-blue-700 hover:bg-blue-800 text-white font-semibold text-sm py-2.5 px-4 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        ) : (
          /* ── Signature Form ─────────────────────────────────────────── */
          <form onSubmit={handleSubmit} className="p-6 space-y-5">
            {/* Transition Preview */}
            <div className="flex items-center justify-center gap-3 bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm">
              <span className="font-mono font-bold text-gray-700">{currentStatus}</span>
              <span className="text-gray-400">→</span>
              <span className="font-mono font-bold text-blue-700">
                {STATUS_LABELS[targetStatus] || targetStatus}
              </span>
            </div>

            {/* Compliance Notice */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
              <p className="text-amber-900 text-[11px] leading-relaxed">
                <strong>⚠️ Legal Notice:</strong> This action constitutes a legally binding
                electronic signature pursuant to 21 CFR Part 11. You are certifying that the
                information provided is accurate and that you are authorized to approve this
                workflow action. An immutable audit record will be created.
              </p>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="esig-password" className="block text-xs font-semibold text-gray-700 mb-1.5">
                Password Re-Authentication <span className="text-red-600">*</span>
              </label>
              <input
                id="esig-password"
                ref={passwordRef}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your current password to authenticate"
              />
            </div>

            {/* Reason Field */}
            <div>
              <label htmlFor="esig-reason" className="block text-xs font-semibold text-gray-700 mb-1.5">
                Rationale / Reason for Signature <span className="text-red-600">*</span>
              </label>
              <textarea
                id="esig-reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                required
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                placeholder="Provide a detailed rationale for this approval decision (required for regulatory compliance)..."
              />
              <p className="text-[10px] text-gray-400 mt-1">
                Minimum 10 characters required. This reason is recorded immutably.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3">
                <p className="text-red-800 text-xs font-medium">⛔ {error}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 pt-1">
              <button
                type="button"
                onClick={handleClose}
                disabled={isSubmitting}
                className="flex-1 border border-gray-300 text-gray-700 hover:bg-gray-50 font-semibold text-sm py-2.5 px-4 rounded-lg transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !password || reason.trim().length < 10}
                className="flex-1 bg-blue-700 hover:bg-blue-800 disabled:bg-gray-300 text-white font-semibold text-sm py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Signing…
                  </>
                ) : (
                  <>🔏 Apply Electronic Signature</>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
