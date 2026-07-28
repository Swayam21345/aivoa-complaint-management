import { useEffect, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import AICopilotPanel from '@/components/complaint/AICopilotPanel/AICopilotPanel';
import PageContainer from '@/components/layout/PageContainer/PageContainer';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  updateDraftField,
  resetComplaintForm,
  submitComplaint,
  clearComplaintError,
} from '@/store/slices/complaintSlice';
import type { ComplaintFormDraft, ComplaintCategory, RiskLevel } from '@/types/complaint.types';

// ─── Constants ────────────────────────────────────────────────────────────────

const CATEGORIES: ComplaintCategory[] = [
  'Product Quality Defect',
  'Packaging Defect',
  'Labeling Error',
  'Delivery Damage',
  'Adverse Event',
  'Foreign Material',
  'Documentation Error',
  'Other',
];

const RISK_LEVELS: RiskLevel[] = ['High', 'Medium', 'Low'];

const RISK_COLORS: Record<RiskLevel, string> = {
  High:   'bg-red-100 text-red-700 border-red-300',
  Medium: 'bg-amber-100 text-amber-700 border-amber-300',
  Low:    'bg-green-100 text-green-700 border-green-300',
};

// ─── Sub-components ───────────────────────────────────────────────────────────

interface FieldProps {
  label: string;
  required?: boolean;
  error?: string;
  children: ReactNode;
  htmlFor?: string;
}

function Field({ label, required, error, children, htmlFor }: FieldProps) {
  return (
    <div>
      <label htmlFor={htmlFor} className="form-label">
        {label}
        {required && <span className="ml-0.5 text-red-500" aria-hidden="true">*</span>}
      </label>
      {children}
      {error && <p className="form-error" role="alert">{error}</p>}
    </div>
  );
}

// ─── Validation ───────────────────────────────────────────────────────────────

interface FormErrors {
  product_name?: string;
  customer_name?: string;
  category?: string;
  risk_level?: string;
  complaint_text?: string;
}

function validate(draft: ComplaintFormDraft): FormErrors {
  const errors: FormErrors = {};
  if (!draft.product_name.trim())   errors.product_name   = 'Product name is required.';
  if (!draft.customer_name.trim())  errors.customer_name  = 'Customer name is required.';
  if (!draft.category)              errors.category       = 'Please select a category.';
  if (!draft.risk_level)            errors.risk_level     = 'Please select a risk level.';
  if (!draft.complaint_text.trim()) errors.complaint_text = 'Complaint details are required.';
  return errors;
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function ComplaintFormPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const { draft, aiAnalysis, submitStatus, submittedComplaintId, submittedId, error } =
    useAppSelector((s) => s.complaint);
  const uploadExtractedText = useAppSelector((s) => s.upload.extractedText);

  const isSubmitting = submitStatus === 'loading';

  // Pre-fill complaint_text from upload extraction if draft is empty
  useEffect(() => {
    if (uploadExtractedText && !draft.complaint_text) {
      dispatch(updateDraftField({ field: 'complaint_text', value: uploadExtractedText }));
    }
  }, [uploadExtractedText, draft.complaint_text, dispatch]);

  // Navigate to detail page after successful submission
  useEffect(() => {
    if (submitStatus === 'succeeded' && submittedId) {
      navigate(`/complaints/${submittedId}`);
    }
  }, [submitStatus, submittedId, navigate]);

  // ── Field change handler ─────────────────────────────────────────────────

  function handleChange<K extends keyof ComplaintFormDraft>(
    field: K,
    value: ComplaintFormDraft[K],
  ) {
    dispatch(updateDraftField({ field, value }));
    if (error) dispatch(clearComplaintError());
  }

  // ── Validate + submit ────────────────────────────────────────────────────

  const [formErrors, setFormErrors] = useState<FormErrors>({});

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const errors = validate(draft);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    setFormErrors({});
    dispatch(
      submitComplaint({
        product_name:   draft.product_name,
        batch_number:   draft.batch_number,
        customer_name:  draft.customer_name,
        category:       draft.category,
        risk_level:     draft.risk_level,
        complaint_text: draft.complaint_text,
        reviewer_notes: draft.reviewer_notes || undefined,
        submitted_by:   draft.submitted_by   || undefined,
        ai_analysis:    aiAnalysis,
      }),
    );
  }

  function handleReset() {
    dispatch(resetComplaintForm());
    setFormErrors({});
  }

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <PageContainer
      title="New Complaint"
      subtitle="Complete all required fields and submit the complaint record."
    >
      <div className="max-w-6xl mx-auto">

        {/* Back link */}
        <div className="mb-4">
          <Link to="/" className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1">
            ← New upload
          </Link>
        </div>

        {/* Complaint ID banner (after successful submit, shown briefly) */}
        {submitStatus === 'succeeded' && submittedComplaintId && (
          <div className="mb-4 rounded-md bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800 flex items-center gap-2">
            <span>✓</span>
            <span>
              Complaint <strong>{submittedComplaintId}</strong> submitted successfully. Redirecting…
            </span>
          </div>
        )}

        {/* API error */}
        {error && (
          <div role="alert" className="mb-4 rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Grid Container: Form + AI Copilot Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          {/* Form column (2/3) */}
          <form onSubmit={handleSubmit} noValidate aria-label="Complaint submission form" className="lg:col-span-2 space-y-4">
          <div className="card p-6 space-y-5">

            {/* Row 1 — Date + Status */}
            <div className="grid grid-cols-2 gap-4">
              <Field label="Date Received" htmlFor="date_received">
                <input
                  id="date_received"
                  type="date"
                  className="form-input"
                  value={draft.date_received}
                  onChange={(e) => handleChange('date_received', e.target.value)}
                  disabled={isSubmitting}
                />
              </Field>
              <Field label="Status">
                <input
                  type="text"
                  className="form-input bg-gray-50"
                  value="Draft"
                  readOnly
                  aria-readonly="true"
                />
              </Field>
            </div>

            {/* Row 2 — Customer + Submitted by */}
            <div className="grid grid-cols-2 gap-4">
              <Field
                label="Customer Name"
                htmlFor="customer_name"
                required
                error={formErrors.customer_name}
              >
                <input
                  id="customer_name"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Pharma Distributor GmbH"
                  value={draft.customer_name}
                  onChange={(e) => handleChange('customer_name', e.target.value)}
                  disabled={isSubmitting}
                  aria-required="true"
                  aria-invalid={!!formErrors.customer_name}
                />
              </Field>
              <Field label="Submitted By" htmlFor="submitted_by">
                <input
                  id="submitted_by"
                  type="text"
                  className="form-input"
                  placeholder="Your name or team"
                  value={draft.submitted_by}
                  onChange={(e) => handleChange('submitted_by', e.target.value)}
                  disabled={isSubmitting}
                />
              </Field>
            </div>

            {/* Row 3 — Product + Batch */}
            <div className="grid grid-cols-2 gap-4">
              <Field
                label="Product Name"
                htmlFor="product_name"
                required
                error={formErrors.product_name}
              >
                <input
                  id="product_name"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Amoxicillin 500mg"
                  value={draft.product_name}
                  onChange={(e) => handleChange('product_name', e.target.value)}
                  disabled={isSubmitting}
                  aria-required="true"
                  aria-invalid={!!formErrors.product_name}
                />
              </Field>
              <Field label="Batch Number" htmlFor="batch_number">
                <input
                  id="batch_number"
                  type="text"
                  className="form-input"
                  placeholder="e.g. AMX-2026-1104"
                  value={draft.batch_number}
                  onChange={(e) => handleChange('batch_number', e.target.value)}
                  disabled={isSubmitting}
                />
              </Field>
            </div>

            {/* Row 4 — Category + Risk */}
            <div className="grid grid-cols-2 gap-4">
              <Field
                label="Complaint Category"
                htmlFor="category"
                required
                error={formErrors.category}
              >
                <select
                  id="category"
                  className="form-input"
                  value={draft.category}
                  onChange={(e) =>
                    handleChange('category', e.target.value as ComplaintCategory | '')
                  }
                  disabled={isSubmitting}
                  aria-required="true"
                  aria-invalid={!!formErrors.category}
                >
                  <option value="">Select category…</option>
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </Field>

              <Field
                label="Risk Level"
                htmlFor="risk_level"
                required
                error={formErrors.risk_level}
              >
                <div className="flex gap-2 pt-1" role="group" aria-label="Risk level">
                  {RISK_LEVELS.map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => handleChange('risk_level', r)}
                      disabled={isSubmitting}
                      aria-pressed={draft.risk_level === r}
                      className={`
                        flex-1 rounded-md border px-2 py-1.5 text-xs font-semibold
                        transition-colors
                        ${draft.risk_level === r
                          ? RISK_COLORS[r]
                          : 'border-gray-200 bg-white text-gray-500 hover:bg-gray-50'}
                      `}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </Field>
            </div>

            {/* Complaint details textarea */}
            <Field
              label="Complaint Details"
              htmlFor="complaint_text"
              required
              error={formErrors.complaint_text}
            >
              <textarea
                id="complaint_text"
                className="form-input resize-none h-36"
                placeholder="Describe the complaint in full…"
                value={draft.complaint_text}
                onChange={(e) => handleChange('complaint_text', e.target.value)}
                disabled={isSubmitting}
                aria-required="true"
                aria-invalid={!!formErrors.complaint_text}
              />
            </Field>

            {/* Reviewer notes */}
            <Field label="Reviewer Notes" htmlFor="reviewer_notes">
              <textarea
                id="reviewer_notes"
                className="form-input resize-none h-24"
                placeholder="Optional internal notes…"
                value={draft.reviewer_notes}
                onChange={(e) => handleChange('reviewer_notes', e.target.value)}
                disabled={isSubmitting}
              />
            </Field>

          </div>

          {/* Actions */}
          <div className="mt-4 flex items-center gap-3 justify-end">
            <button
              type="button"
              className="btn-secondary"
              onClick={handleReset}
              disabled={isSubmitting}
            >
              Clear Form
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
              aria-busy={isSubmitting}
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                  Submitting…
                </span>
              ) : (
                'Submit Complaint'
              )}
            </button>
          </div>
        </form>

        {/* AI Copilot Panel column (1/3) */}
        <div className="lg:col-span-1">
          <AICopilotPanel aiAnalysis={aiAnalysis} />
        </div>
      </div>

      </div>
    </PageContainer>
  );
}

