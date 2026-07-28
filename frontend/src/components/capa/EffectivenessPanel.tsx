import { useState } from 'react';
import type { FormEvent } from 'react';
import type { CAPARead } from '@/types/capa.types';
import { submitCAPAEffectiveness } from '@/services/capaService';

interface Props {
  capa: CAPARead;
  onUpdate: () => void;
  canReview: boolean;
}

export function EffectivenessPanel({ capa, onUpdate, canReview }: Props) {
  const [password, setPassword] = useState('');
  const [effectivenessCheck, setEffectivenessCheck] = useState(capa.effectiveness_check || '');
  const [isEffective, setIsEffective] = useState(true);
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isReviewed = capa.status === 'EFFECTIVE' || capa.status === 'INEFFECTIVE';

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!password || !effectivenessCheck || !reason) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await submitCAPAEffectiveness(capa.id, {
        password,
        effectiveness_check: effectivenessCheck.trim(),
        is_effective: isEffective,
        reason: reason.trim(),
      });
      setPassword('');
      setReason('');
      onUpdate();
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: { detail?: string } } };
      setError(
        apiErr?.response?.data?.detail || 'Effectiveness review failed. Verify password.',
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="card p-5 border border-purple-200 bg-purple-50/30">
      <div className="flex items-center justify-between mb-3 border-b border-purple-200 pb-2">
        <h3 className="text-xs font-bold text-purple-900 uppercase tracking-wider">
          🔬 21 CFR Part 11 Effectiveness Review
        </h3>
        {isReviewed && (
          <span
            className={`text-xs font-extrabold px-3 py-1 rounded ${
              capa.status === 'EFFECTIVE'
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {capa.status === 'EFFECTIVE' ? '✅ EFFECTIVE' : '❌ INEFFECTIVE'}
          </span>
        )}
      </div>

      {isReviewed ? (
        <div className="space-y-3 text-xs">
          <div>
            <p className="font-bold text-gray-700">Evaluation Findings & Verification:</p>
            <p className="bg-white p-3 rounded border border-purple-100 text-gray-800 mt-1 whitespace-pre-wrap">
              {capa.effectiveness_check}
            </p>
          </div>
          <div className="flex justify-between text-gray-500 text-[11px] border-t pt-2">
            <span>Reviewed by: <strong>{capa.reviewer || 'QA Reviewer'}</strong></span>
            <span>Due Date: {capa.effectiveness_due_date ? new Date(capa.effectiveness_due_date).toLocaleDateString() : 'N/A'}</span>
          </div>
        </div>
      ) : canReview ? (
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <p className="text-purple-800 text-[11px]">
            Perform 21 CFR Part 11 signed evaluation to verify whether corrective actions successfully prevented complaint reoccurrences.
          </p>

          <div>
            <label htmlFor="eff-check" className="block font-semibold text-gray-700 mb-1">
              Effectiveness Check Verification Findings *
            </label>
            <textarea
              id="eff-check"
              value={effectivenessCheck}
              onChange={(e) => setEffectivenessCheck(e.target.value)}
              required
              rows={3}
              className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-purple-500 outline-none"
              placeholder="Describe line audit findings, batch yield sampling, or zero-defect monitoring data..."
            />
          </div>

          <div>
            <label className="block font-semibold text-gray-700 mb-1">Effectiveness Determination *</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer font-bold text-emerald-700">
                <input
                  type="radio"
                  name="effective-radio"
                  checked={isEffective === true}
                  onChange={() => setIsEffective(true)}
                />
                ✅ EFFECTIVE (Actions Verified)
              </label>
              <label className="flex items-center gap-2 cursor-pointer font-bold text-red-700">
                <input
                  type="radio"
                  name="effective-radio"
                  checked={isEffective === false}
                  onChange={() => setIsEffective(false)}
                />
                ❌ INEFFECTIVE (Reopen CAPA)
              </label>
            </div>
          </div>

          <div>
            <label htmlFor="eff-reason" className="block font-semibold text-gray-700 mb-1">
              21 CFR Part 11 Regulatory Rationale *
            </label>
            <textarea
              id="eff-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              required
              rows={2}
              className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-purple-500 outline-none"
              placeholder="Provide legally binding justification for effectiveness determination..."
            />
          </div>

          <div>
            <label htmlFor="eff-pass" className="block font-semibold text-gray-700 mb-1">
              Password Re-Authentication *
            </label>
            <input
              id="eff-pass"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border border-gray-300 rounded p-2 text-xs focus:ring-2 focus:ring-purple-500 outline-none"
              placeholder="Enter current password"
            />
          </div>

          {error && <p className="text-red-600 font-medium text-[11px]">{error}</p>}

          <button
            type="submit"
            disabled={isSubmitting || !password || !effectivenessCheck || !reason}
            className="w-full bg-purple-700 hover:bg-purple-800 disabled:bg-gray-300 text-white font-bold py-2 rounded transition-colors"
          >
            {isSubmitting ? 'Signing...' : '🔏 Submit Signed Effectiveness Review'}
          </button>
        </form>
      ) : (
        <p className="text-xs text-gray-500 italic">
          Effectiveness check pending QA Manager / Admin review.
        </p>
      )}
    </div>
  );
}
