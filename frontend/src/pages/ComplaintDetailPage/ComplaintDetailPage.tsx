import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useParams, Link } from 'react-router-dom';

import AICopilotPanel from '@/components/complaint/AICopilotPanel/AICopilotPanel';
import Timeline from '@/components/complaint/Timeline/Timeline';
import ElectronicSignatureModal from '@/components/complaint/ElectronicSignatureModal/ElectronicSignatureModal';
import { CAPACreateModal } from '@/components/capa/CAPACreateModal';
import { CAPAStatusBadge } from '@/components/capa/CAPAStatusBadge';
import { WorkflowStepper } from '@/components/complaint/WorkflowStepper/WorkflowStepper';
import PageContainer from '@/components/layout/PageContainer/PageContainer';
import { StatusBadge, RiskBadge, PriorityBadge } from '@/components/common/Badge/Badges';
import { PageSkeleton } from '@/components/common/Skeleton/Skeleton';

import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchComplaintDetail,
  patchComplaintStatus,
  clearDetail,
  clearComplaintError,
} from '@/store/slices/complaintSlice';
import { addToast } from '@/store/slices/toastSlice';
import { assignComplaint, exportComplaintPDF, getComplaintTimeline } from '@/services/complaintService';
import { fetchCAPAList } from '@/services/capaService';
import { fetchRCAList, createRCA } from '@/services/rcaService';
import type { CAPARead } from '@/types/capa.types';
import type { RCARead, RCACreatePayload } from '@/types/rca.types';
import { formatDate, formatDateTime } from '@/utils/formatDate';
import type { ComplaintStatus, ElectronicSignatureResponse } from '@/types/complaint.types';


// ─── Tabs ─────────────────────────────────────────────────────────────────────

type DetailTab = 'overview' | 'timeline' | 'copilot' | 'notes' | 'rca' | 'capa' | 'history' | 'activity' | 'signatures';


// ─── Helper Components ────────────────────────────────────────────────────────

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="grid grid-cols-3 gap-2 py-2.5 border-b border-gray-100 last:border-0">
      <dt className="text-xs font-semibold text-gray-500 uppercase tracking-wide self-start pt-0.5">
        {label}
      </dt>
      <dd className="col-span-2 text-sm text-gray-900 break-words font-medium">
        {value ?? <span className="text-gray-400">—</span>}
      </dd>
    </div>
  );
}

export default function ComplaintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const dispatch = useAppDispatch();

  const { detail, detailStatus, error } = useAppSelector((state) => state.complaint);
  const { user, role } = useAppSelector((state) => state.auth);

  const [activeTab, setActiveTab] = useState<DetailTab>('overview');

  const [editedStatus, setEditedStatus] = useState<ComplaintStatus>('NEW');
  const [changeReason, setChangeReason] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const [assigneeName, setAssigneeName] = useState('');
  const [isAssigning, setIsAssigning] = useState(false);

  const [timelineEvents, setTimelineEvents] = useState<any[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // ── 21 CFR Part 11 Electronic Signature State ─────────────────────────────
  const [sigModalOpen, setSigModalOpen] = useState(false);
  const [sigTargetStatus, setSigTargetStatus] = useState('QA_APPROVED');

  const canSign = role && ['ADMIN', 'QA_MANAGER'].includes(role);


  const canManageStatus = role && ['ADMIN', 'QA_MANAGER', 'INVESTIGATOR'].includes(role);
  const canAssign = role && ['ADMIN', 'QA_MANAGER'].includes(role);


  // ── RCA & CAPA State ──────────────────────────────────────────────────────────────
  const [rcaList, setRcaList] = useState<RCARead[]>([]);
  const [capaList, setCapaList] = useState<CAPARead[]>([]);
  const [createCapaModalOpen, setCreateCapaModalOpen] = useState(false);

  // ── RCA Create Modal ──────────────────────────────────────────────────────────────
  const [rcaModalOpen, setRcaModalOpen] = useState(false);
  const [rcaForm, setRcaForm] = useState({ primary_root_cause: '', root_cause_category: 'Equipment Failure', methodology: 'HYBRID' });
  const [rcaSubmitting, setRcaSubmitting] = useState(false);

  async function handleCreateRCA(e: FormEvent) {
    e.preventDefault();
    if (!id || !rcaForm.primary_root_cause.trim()) return;
    setRcaSubmitting(true);
    try {
      const payload: RCACreatePayload = {
        complaint_id: id,
        primary_root_cause: rcaForm.primary_root_cause,
        root_cause_category: rcaForm.root_cause_category,
        methodology: rcaForm.methodology as 'FIVE_WHYS' | 'FISHBONE' | 'HYBRID',
      };
      const newRca = await createRCA(payload);
      setRcaList((prev) => [newRca, ...prev]);
      setRcaModalOpen(false);
      setRcaForm({ primary_root_cause: '', root_cause_category: 'Equipment Failure', methodology: 'HYBRID' });
      dispatch(addToast({ type: 'success', title: 'RCA Created', message: `RCA ${newRca.rca_number} created successfully.` }));
    } catch (err: any) {
      dispatch(addToast({ type: 'error', title: 'RCA Creation Failed', message: err?.response?.data?.detail || 'Failed to create RCA.' }));
    } finally {
      setRcaSubmitting(false);
    }
  }

  useEffect(() => {
    if (id) {
      dispatch(fetchComplaintDetail(id));
      setTimelineLoading(true);
      getComplaintTimeline(id)
        .then((res) => setTimelineEvents(res.events || []))
        .catch(() => {})
        .finally(() => setTimelineLoading(false));

      fetchCAPAList({ complaint_id: id })
        .then((res) => setCapaList(res.items || []))
        .catch(() => {});

      fetchRCAList({ complaint_id: id })
        .then((res) => setRcaList(res.items || []))
        .catch(() => {});
    }
    return () => {
      dispatch(clearDetail());
      dispatch(clearComplaintError());
    };
  }, [id, dispatch]);


  useEffect(() => {
    if (detail?.status) {
      setEditedStatus(detail.status as ComplaintStatus);
    }
    if (detail?.assigned_to) {
      setAssigneeName(detail.assigned_to);
    }
  }, [detail?.status, detail?.assigned_to]);

  async function handleStatusSave(e: FormEvent) {
    e.preventDefault();
    if (!id || !detail || !canManageStatus) return;
    setIsUpdating(true);
    try {
      await dispatch(
        patchComplaintStatus({
          id,
          data: {
            status: editedStatus,
            change_reason: changeReason.trim() || undefined,
            changed_by: user?.full_name || 'Quality Reviewer',
          },
        }),
      ).unwrap();
      dispatch(
        addToast({
          type: 'success',
          title: 'Status Updated',
          message: `Complaint ${detail.complaint_id} status updated to ${editedStatus}`,
        }),
      );
      setChangeReason('');
      getComplaintTimeline(id).then((res) => setTimelineEvents(res.events || []));
    } catch (err: any) {
      dispatch(
        addToast({
          type: 'error',
          title: 'Status Transition Rejected',
          message: err?.detail || err || 'Invalid status transition or permission denied',
        }),
      );
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleAssignInvestigator(e: FormEvent) {
    e.preventDefault();
    if (!id || !detail || !canAssign || !assigneeName.trim()) return;
    setIsAssigning(true);
    try {
      await assignComplaint(id, assigneeName.trim());
      dispatch(fetchComplaintDetail(id));
      dispatch(
        addToast({
          type: 'success',
          title: 'Investigator Assigned',
          message: `Assigned complaint ${detail.complaint_id} to ${assigneeName}`,
        }),
      );
    } catch (err: any) {
      dispatch(
        addToast({
          type: 'error',
          title: 'Assignment Failed',
          message: err?.response?.data?.detail || 'Failed to assign investigator',
        }),
      );
    } finally {
      setIsAssigning(false);
    }
  }

  async function handleExportPDF() {
    if (!id || !detail) return;
    setIsExporting(true);
    try {
      await exportComplaintPDF(id, detail.complaint_id);
      dispatch(
        addToast({
          type: 'success',
          title: 'PDF Export Downloaded',
          message: `Report for ${detail.complaint_id} downloaded successfully.`,
        }),
      );
    } catch (err) {
      dispatch(
        addToast({
          type: 'error',
          title: 'PDF Export Failed',
          message: 'Failed to generate complaint PDF report.',
        }),
      );
    } finally {
      setIsExporting(false);
    }
  }

  if (detailStatus === 'loading' || !detail) {
    return (
      <PageContainer title="Loading Complaint Record...">
        <PageSkeleton />
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer title="Error Loading Complaint">
        <div className="card p-8 text-center max-w-lg mx-auto my-8 border-red-200 bg-red-50/40">
          <p className="text-sm font-semibold text-red-800 mb-2">Complaint Record Not Found</p>
          <p className="text-xs text-red-600 mb-4">{error}</p>
          <Link to="/complaints" className="btn-primary text-xs py-2 px-4 inline-block no-underline">
            ← Return to Complaints List
          </Link>
        </div>
      </PageContainer>
    );
  }

  const ai = detail.ai_analysis;
  const rawAi = ai ? (ai as any).raw_llm_response || {} : {};
  const capaData = ai?.capa || rawAi.capa;
  const sla = detail.sla_tracking;

  return (
    <>
    <PageContainer
      title={`Complaint ${detail.complaint_id}`}
      subtitle={`Product: ${detail.product_name ?? 'N/A'} | Batch: ${detail.batch_number ?? 'N/A'}`}
    >

      {/* ── Escalation Banner ──────────────────────────────────────────────────── */}
      {(detail.is_escalated || sla?.is_escalated) && (
        <div className="card p-4 mb-6 bg-red-500 text-white shadow-md border border-red-600 flex items-center gap-3">
          <span className="text-2xl animate-pulse">⚠️</span>
          <div>
            <h4 className="font-bold text-sm uppercase tracking-wide">
              Automated QMS Escalation Flagged
            </h4>
            <p className="text-xs opacity-90 mt-0.5">
              {detail.escalation_reason || sla?.escalation_reason || 'Critical SLA threshold exceeded. High risk complaint requires immediate QA review.'}
            </p>
          </div>
        </div>
      )}

      {/* ── QMS Workflow Stepper ────────────────────────────────────────────────── */}
      <WorkflowStepper currentStatus={detail.status} />

      {/* ── Enterprise Header Bar ──────────────────────────────────────────────── */}
      <div className="card p-5 mb-6 bg-white shadow-xs border border-gray-200">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="font-mono text-base font-extrabold text-primary-700">
                {detail.complaint_id}
              </span>
              <StatusBadge status={detail.status} />
              <RiskBadge riskLevel={detail.risk_level} />
              <PriorityBadge priority={detail.priority} />

              {/* SLA Badge */}
              {sla?.is_overdue ? (
                <span className="bg-red-100 text-red-800 text-[11px] font-bold px-2.5 py-0.5 rounded border border-red-200">
                  🚨 OVERDUE ({sla.age_hours}h)
                </span>
              ) : sla?.near_sla ? (
                <span className="bg-amber-100 text-amber-800 text-[11px] font-bold px-2.5 py-0.5 rounded border border-amber-200">
                  ⚠️ NEAR SLA ({sla.hours_until_due}h left)
                </span>
              ) : (
                <span className="bg-green-100 text-green-800 text-[11px] font-medium px-2.5 py-0.5 rounded border border-green-200">
                  ⏱️ On Schedule ({sla?.hours_until_due ?? 0}h left)
                </span>
              )}
            </div>
            <p className="text-xs text-gray-500">
              Customer: <span className="font-semibold text-gray-800">{detail.customer_name ?? '—'}</span> | Category:{' '}
              <span className="font-semibold text-gray-800">{detail.category ?? 'Uncategorized'}</span> | Assigned To:{' '}
              <span className="font-semibold text-primary-700">{detail.assigned_to ?? 'Unassigned'}</span>
            </p>
          </div>

          {/* Action Bar */}
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleExportPDF}
              disabled={isExporting}
              className="btn-secondary text-xs py-2 px-4 flex items-center gap-2 shadow-xs hover:shadow"
            >
              <span>📄</span>
              <span>{isExporting ? 'Generating PDF...' : 'Export PDF Report'}</span>
            </button>
            <Link to="/complaints" className="btn-primary text-xs py-2 px-4 no-underline">
              ← Back to List
            </Link>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 border-b border-gray-200 mt-6 -mb-5 overflow-x-auto">
          {[
                      { id: 'overview', label: '📌 Overview' },
            { id: 'timeline', label: `⏱️ Audit Timeline (${timelineEvents.length})` },
            { id: 'copilot', label: '✦ AI Copilot' },
            { id: 'notes', label: `💬 Reviewer Notes (${detail.notes?.length ?? 0})` },
            { id: 'rca', label: '🔬 RCA & FMEA' },
            { id: 'capa', label: '🛡️ CAPA' },

            { id: 'history', label: `📜 Audit History (${detail.history?.length ?? 0})` },
            { id: 'activity', label: `🛡️ Activity Audit Feed (${detail.audit_events?.length ?? 0})` },
            { id: 'signatures', label: `🔏 E-Signatures (${detail.signatures?.length ?? 0})` },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id as DetailTab)}
              className={`px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition-colors border-b-2 -mb-px ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-700 bg-primary-50/50 rounded-t'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Tab Content Views ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Active Tab Content (2/3 width) */}
        <div className="lg:col-span-2 space-y-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <>
              <div className="card p-5">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 border-b pb-2">
                  Complaint Record Overview
                </h3>
                <dl>
                  <DetailRow label="Date Received" value={formatDate(detail.date_received)} />
                  <DetailRow label="Customer Name" value={detail.customer_name} />
                  <DetailRow label="Submitted By" value={detail.submitted_by} />
                  <DetailRow label="Assigned Investigator" value={detail.assigned_to ?? 'Unassigned'} />
                  <DetailRow label="Assigned By" value={detail.assigned_by} />
                  <DetailRow label="Product Name" value={detail.product_name} />
                  <DetailRow label="Batch / Lot Number" value={detail.batch_number} />
                  <DetailRow label="Defect Category" value={detail.category} />
                  <DetailRow label="Risk Assessment" value={<RiskBadge riskLevel={detail.risk_level} />} />
                  <DetailRow label="Priority" value={<PriorityBadge priority={detail.priority} />} />
                  <DetailRow label="Status" value={<StatusBadge status={detail.status} />} />
                  <DetailRow label="Created Date" value={formatDateTime(detail.created_at)} />
                  <DetailRow label="Last Updated" value={formatDateTime(detail.updated_at)} />
                </dl>
              </div>

              {detail.complaint_text && (
                <div className="card p-5">
                  <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
                    Reported Complaint Narrative
                  </h3>
                  <p className="text-xs text-gray-800 bg-gray-50 p-4 rounded border border-gray-200 leading-relaxed whitespace-pre-wrap">
                    {detail.complaint_text}
                  </p>
                </div>
              )}
            </>
          )}

          {/* TAB 2: TIMELINE */}
          {activeTab === 'timeline' && (
            <div className="card p-5">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 border-b pb-2">
                Chronological Complaint Audit Timeline
              </h3>
              <Timeline events={timelineEvents} loading={timelineLoading} />
            </div>
          )}

          {/* TAB 3: AI COPILOT */}
          {activeTab === 'copilot' && (
            <div>
              <AICopilotPanel aiAnalysis={ai} />
            </div>
          )}

          {/* TAB 4: REVIEWER NOTES */}
          {activeTab === 'notes' && (
            <div className="card p-5 space-y-4">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 border-b pb-2">
                Quality Reviewer Notes
              </h3>
              {detail.notes && detail.notes.length > 0 ? (
                <div className="space-y-3">
                  {detail.notes.map((n) => (
                    <div key={n.id} className="bg-gray-50 p-3.5 rounded border border-gray-200 text-xs">
                      <div className="flex justify-between text-gray-500 mb-1 font-mono text-[11px]">
                        <span className="font-bold text-gray-900">{n.author}</span>
                        <span>{formatDateTime(n.created_at)}</span>
                      </div>
                      <p className="text-gray-800 leading-relaxed">{n.content}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400 italic p-4 text-center">No reviewer notes logged yet.</p>
              )}
            </div>
          )}

          {/* TAB 5: RCA & FMEA */}
          {activeTab === 'rca' && (
            <div className="card p-5 space-y-4">
              <div className="flex items-center justify-between border-b pb-3">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  🔬 Root Cause Analysis (RCA) & FMEA Assessments ({rcaList.length})
                </h3>
                <button
                  type="button"
                  onClick={() => setRcaModalOpen(true)}
                  className="bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold px-3 py-1.5 rounded transition-colors"
                >
                  + Create RCA Assessment
                </button>
              </div>

              {rcaList.length > 0 ? (
                <div className="space-y-3">
                  {rcaList.map((r) => (
                    <div
                      key={r.id}
                      className="bg-purple-50/30 border border-purple-200 rounded-lg p-4 text-xs flex flex-col md:flex-row md:items-center justify-between gap-3"
                    >
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-mono font-bold text-purple-700 text-sm">
                            {r.rca_number}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              r.status === 'APPROVED'
                                ? 'bg-green-100 text-green-800'
                                : r.status === 'UNDER_REVIEW'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            {r.status}
                          </span>
                          <span className="bg-gray-100 text-gray-700 text-[10px] font-bold px-2 py-0.5 rounded">
                            Method: {r.methodology}
                          </span>
                        </div>
                        <h4 className="font-bold text-gray-900 text-xs mb-1">Primary Root Cause</h4>
                        <p className="text-gray-700 line-clamp-2 leading-relaxed">
                          {r.primary_root_cause || 'No root cause entered.'}
                        </p>
                        <p className="text-gray-400 text-[10px] mt-1">
                          Created By: <strong>{r.created_by || 'Unknown'}</strong> · Created:{' '}
                          {formatDate(r.created_at)}
                        </p>
                      </div>
                      <Link
                        to={`/rca/${r.id}`}
                        className="btn-primary text-xs py-1.5 px-3 whitespace-nowrap no-underline text-center"
                      >
                        View Full RCA →
                      </Link>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-6 text-center text-xs text-gray-500">
                  <p className="font-bold mb-1">No RCA Records Linked to this Complaint Yet</p>
                  <p className="text-gray-400 text-[11px] mb-3">
                    Perform a 5-Whys or Fishbone Root Cause Analysis to identify true underlying causes.
                  </p>
                  <button
                    type="button"
                    onClick={() => setRcaModalOpen(true)}
                    className="bg-blue-700 hover:bg-blue-800 text-white font-bold px-4 py-1.5 rounded transition-colors"
                  >
                    Create RCA Assessment
                  </button>
                </div>
              )}

              {/* AI Recommended Root Cause fallback */}
              {ai?.root_cause_recommendation && (
                <div className="border-t pt-4 mt-4 space-y-2">
                  <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                    🤖 AI Copilot Root Cause Recommendation
                  </h4>
                  <p className="text-xs text-gray-800 bg-purple-50 p-3 rounded border border-purple-200 leading-relaxed whitespace-pre-wrap">
                    {ai.root_cause_recommendation}
                  </p>
                </div>
              )}
              {/* RCA Create Modal */}
              {rcaModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                  <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6">
                    <div className="flex items-center justify-between mb-5">
                      <h3 className="text-base font-bold text-gray-900">🔬 Create RCA Investigation</h3>
                      <button type="button" onClick={() => setRcaModalOpen(false)} className="text-gray-400 hover:text-gray-600 text-xl font-bold">✕</button>
                    </div>
                    <form onSubmit={handleCreateRCA} className="space-y-4">
                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">Methodology</label>
                        <select
                          value={rcaForm.methodology}
                          onChange={(e) => setRcaForm((f) => ({ ...f, methodology: e.target.value }))}
                          className="w-full border border-gray-300 rounded-lg p-2 text-sm"
                        >
                          <option value="HYBRID">Hybrid (5-Whys + Fishbone)</option>
                          <option value="FIVE_WHYS">5-Whys</option>
                          <option value="FISHBONE">Fishbone (Ishikawa)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">Root Cause Category</label>
                        <select
                          value={rcaForm.root_cause_category}
                          onChange={(e) => setRcaForm((f) => ({ ...f, root_cause_category: e.target.value }))}
                          className="w-full border border-gray-300 rounded-lg p-2 text-sm"
                        >
                          <option>Equipment Failure</option>
                          <option>Human Error</option>
                          <option>Raw Material Defect</option>
                          <option>SOP Non-compliance</option>
                          <option>Environmental</option>
                          <option>Process Deviation</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">Primary Root Cause <span className="text-red-500">*</span></label>
                        <textarea
                          rows={4}
                          required
                          value={rcaForm.primary_root_cause}
                          onChange={(e) => setRcaForm((f) => ({ ...f, primary_root_cause: e.target.value }))}
                          placeholder="Describe the identified primary root cause..."
                          className="w-full border border-gray-300 rounded-lg p-2 text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        />
                      </div>
                      <div className="flex justify-end gap-3 pt-2">
                        <button type="button" onClick={() => setRcaModalOpen(false)} className="px-4 py-2 text-sm font-semibold text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
                          Cancel
                        </button>
                        <button type="submit" disabled={rcaSubmitting} className="px-4 py-2 text-sm font-bold text-white bg-blue-700 rounded-lg hover:bg-blue-800 disabled:opacity-60">
                          {rcaSubmitting ? 'Saving...' : 'Create RCA'}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: CAPA */}
          {activeTab === 'capa' && (
            <div className="card p-5 space-y-4">
              <div className="flex items-center justify-between border-b pb-3">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  🛡️ Corrective & Preventive Actions (CAPA) Plan ({capaList.length})
                </h3>
                {canManageStatus && (
                  <button
                    type="button"
                    onClick={() => setCreateCapaModalOpen(true)}
                    className="bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold px-3 py-1.5 rounded transition-colors"
                  >
                    + Create CAPA Record
                  </button>
                )}
              </div>

              {/* Live CAPA Records */}
              {capaList.length > 0 ? (
                <div className="space-y-3">
                  {capaList.map((c) => (
                    <div
                      key={c.id}
                      className="bg-blue-50/30 border border-blue-200 rounded-lg p-4 text-xs flex flex-col md:flex-row md:items-center justify-between gap-3"
                    >
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-mono font-bold text-blue-700 text-sm">
                            {c.capa_number}
                          </span>
                          <CAPAStatusBadge status={c.status} />
                          <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded">
                            Priority: {c.priority}
                          </span>
                        </div>
                        <h4 className="font-bold text-gray-900 text-xs mb-1">{c.title}</h4>
                        <p className="text-gray-600 line-clamp-2 leading-relaxed">{c.description}</p>
                        <p className="text-gray-400 text-[10px] mt-1">
                          Owner: <strong>{c.owner || 'Unassigned'}</strong> · Target Completion:{' '}
                          {c.target_completion_date ? formatDate(c.target_completion_date) : 'N/A'}
                        </p>
                      </div>
                      <Link
                        to={`/capa/${c.id}`}
                        className="btn-primary text-xs py-1.5 px-3 whitespace-nowrap no-underline text-center"
                      >
                        Manage CAPA →
                      </Link>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-6 text-center text-xs text-gray-500">
                  <p className="font-bold mb-1">No CAPAs Created for this Complaint Yet</p>
                  <p className="text-gray-400 text-[11px] mb-3">
                    CAPA plans can be initiated when root cause analysis is identified.
                  </p>
                  {canManageStatus && (
                    <button
                      type="button"
                      onClick={() => setCreateCapaModalOpen(true)}
                      className="bg-blue-700 hover:bg-blue-800 text-white font-bold px-4 py-1.5 rounded transition-colors"
                    >
                      Create First CAPA Plan
                    </button>
                  )}
                </div>
              )}

              {/* AI Recommended CAPA fallback */}
              {capaData && (
                <div className="border-t pt-4 mt-4 space-y-3">
                  <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                    🤖 AI Copilot Recommended CAPA Summary
                  </h4>
                  {capaData.corrective_actions?.length > 0 && (
                    <div>
                      <h5 className="font-bold text-red-700 uppercase tracking-wider text-[10px] mb-1">
                        Immediate Corrective Actions
                      </h5>
                      <ul className="space-y-1">
                        {capaData.corrective_actions.map((act: string, i: number) => (
                          <li key={i} className="bg-red-50 p-2 rounded border border-red-200 text-red-900 font-medium">
                            ✓ {act}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {capaData.preventive_actions?.length > 0 && (
                    <div>
                      <h5 className="font-bold text-blue-700 uppercase tracking-wider text-[10px] mb-1">
                        Long-term Preventive Actions
                      </h5>
                      <ul className="space-y-1">
                        {capaData.preventive_actions.map((act: string, i: number) => (
                          <li key={i} className="bg-blue-50 p-2 rounded border border-blue-200 text-blue-900 font-medium">
                            → {act}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}


          {/* TAB 6: HISTORY */}
          {activeTab === 'history' && (
            <div className="card p-5">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 border-b pb-2">
                Audit History & Status Transitions
              </h3>
              {detail.history && detail.history.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left" aria-label="Complaint Audit History">
                    <thead>
                      <tr className="bg-gray-50 border-b text-gray-500 font-semibold uppercase tracking-wider">
                        <th className="p-2.5">Old Status</th>
                        <th className="p-2.5">New Status</th>
                        <th className="p-2.5">Changed By</th>
                        <th className="p-2.5">Reason</th>
                        <th className="p-2.5">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {detail.history.map((h) => (
                        <tr key={h.id} className="hover:bg-gray-50">
                          <td className="p-2.5 text-gray-400">{h.old_status || '—'}</td>
                          <td className="p-2.5 font-bold text-primary-700">{h.new_status}</td>
                          <td className="p-2.5">{h.changed_by || 'System'}</td>
                          <td className="p-2.5 text-gray-700">{h.change_reason || 'Status update'}</td>
                          <td className="p-2.5 text-gray-500 font-mono text-[11px]">{formatDateTime(h.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-gray-400 italic p-4 text-center">No history transitions recorded.</p>
              )}
            </div>
          )}

          {/* TAB 7: IMMUTABLE AUDIT FEED */}
          {activeTab === 'activity' && (
            <div className="card p-5">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 border-b pb-2">
                21 CFR Part 11 Compliance Immutable Activity Feed
              </h3>
              {detail.audit_events && detail.audit_events.length > 0 ? (
                <div className="space-y-3">
                  {detail.audit_events.map((evt) => (
                    <div key={evt.id} className="bg-gray-50 p-3.5 rounded border border-gray-200 text-xs">
                      <div className="flex justify-between items-center text-gray-500 mb-1 font-mono text-[11px]">
                        <span className="font-bold text-gray-900 bg-gray-200 px-2 py-0.5 rounded">
                          {evt.action_type}
                        </span>
                        <span>{formatDateTime(evt.created_at)}</span>
                      </div>
                      <p className="text-gray-800 font-medium">{evt.description}</p>
                      <p className="text-[11px] text-gray-500 mt-1">Actor: {evt.actor_email}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400 italic p-4 text-center">No audit events recorded.</p>
              )}
            </div>
          )}

          {/* TAB 8: ELECTRONIC SIGNATURES (21 CFR Part 11) */}
          {activeTab === 'signatures' && (
            <div className="card p-5">
              <div className="flex items-center justify-between mb-4 border-b pb-3">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  🔏 21 CFR Part 11 Electronic Signatures
                </h3>
                {canSign && (
                  <button
                    type="button"
                    onClick={() => {
                      const st = detail.status === 'QA_REVIEW' ? 'QA_APPROVED' : 'CLOSED';
                      setSigTargetStatus(st);
                      setSigModalOpen(true);
                    }}
                    disabled={!['QA_REVIEW', 'QA_APPROVED'].includes(detail.status)}
                    className="bg-blue-700 hover:bg-blue-800 disabled:bg-gray-300 disabled:cursor-not-allowed text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors"
                  >
                    + Apply Electronic Signature
                  </button>
                )}
              </div>

              {detail.signatures && detail.signatures.length > 0 ? (
                <div className="space-y-3">
                  {detail.signatures.map((sig) => (
                    <div
                      key={sig.id}
                      className="bg-blue-50/40 border border-blue-200 rounded-lg p-4 text-xs"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <span className="font-bold text-blue-900 text-sm">{sig.action}</span>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="bg-gray-200 text-gray-700 px-2 py-0.5 rounded font-mono text-[10px]">
                              {sig.status_before}
                            </span>
                            <span className="text-gray-400">→</span>
                            <span className="bg-blue-700 text-white px-2 py-0.5 rounded font-mono text-[10px]">
                              {sig.status_after}
                            </span>
                          </div>
                        </div>
                        <span className="text-gray-400 font-mono text-[10px] whitespace-nowrap ml-3">
                          {formatDateTime(sig.signature_timestamp)}
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2 leading-relaxed">
                        <strong>Reason:</strong> {sig.reason}
                      </p>
                      <p className="text-gray-500 mb-2">
                        <strong>Signed by:</strong> {sig.user_name || 'Unknown'}
                      </p>
                      <div className="bg-white border border-blue-100 rounded p-2">
                        <p className="text-[10px] font-bold text-gray-500 uppercase mb-1">
                          SHA-256 Integrity Hash
                        </p>
                        <p className="font-mono text-[10px] text-gray-600 break-all">
                          {sig.signature_hash}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-10 text-center">
                  <div className="text-4xl mb-3">🔏</div>
                  <p className="text-sm font-semibold text-gray-700 mb-1">
                    No Electronic Signatures Recorded
                  </p>
                  <p className="text-xs text-gray-400">
                    21 CFR Part 11 signatures are required for QA Approval and Complaint Closure.
                  </p>
                  {canSign && ['QA_REVIEW', 'QA_APPROVED'].includes(detail.status) && (
                    <button
                      type="button"
                      onClick={() => {
                        const st = detail.status === 'QA_REVIEW' ? 'QA_APPROVED' : 'CLOSED';
                        setSigTargetStatus(st);
                        setSigModalOpen(true);
                      }}
                      className="mt-4 bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold px-5 py-2 rounded-lg transition-colors"
                    >
                      Apply First Signature
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Sidebar (1/3 width) */}
        <div className="space-y-6">
          {/* Assignment Panel */}
          {canAssign && (
            <form onSubmit={handleAssignInvestigator} className="card p-5 shadow-xs border border-gray-200" aria-label="Assign investigator">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 border-b pb-2">
                Investigator Assignment
              </h3>
              <div className="mb-3">
                <label htmlFor="assignee" className="form-label text-xs">
                  Assign To (Investigator)
                </label>
                <input
                  id="assignee"
                  type="text"
                  className="form-input text-xs"
                  placeholder="e.g. Dr. Jane Smith"
                  value={assigneeName}
                  onChange={(e) => setAssigneeName(e.target.value)}
                />
              </div>
              <button
                type="submit"
                disabled={isAssigning}
                className="btn-secondary w-full text-xs py-2 px-4"
              >
                {isAssigning ? 'Assigning...' : 'Assign Investigator'}
              </button>
            </form>
          )}

          {/* Status Update Form */}
          {canManageStatus ? (
            <form onSubmit={handleStatusSave} className="card p-5 shadow-xs border border-gray-200" aria-label="Update record status">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 border-b pb-2">
                Update QMS Workflow Status
              </h3>

              <div className="mb-4">
                <label htmlFor="edit-status" className="form-label text-xs">
                  Workflow Status
                </label>
                <select
                  id="edit-status"
                  className="form-input text-xs font-medium"
                  value={editedStatus}
                  onChange={(e) => setEditedStatus(e.target.value as ComplaintStatus)}
                >
                  <option value="NEW">1. NEW (Intake)</option>
                  <option value="TRIAGED">2. TRIAGED (QA Review)</option>
                  <option value="ASSIGNED">3. ASSIGNED (Investigator)</option>
                  <option value="UNDER_INVESTIGATION">4. UNDER_INVESTIGATION</option>
                  <option value="ROOT_CAUSE_IDENTIFIED">5. ROOT_CAUSE_IDENTIFIED</option>
                  <option value="CAPA_IN_PROGRESS">6. CAPA_IN_PROGRESS</option>
                  <option value="QA_REVIEW">7. QA_REVIEW</option>
                  <option value="QA_APPROVED">8. QA_APPROVED</option>
                  <option value="CLOSED">9. CLOSED</option>
                  <option value="ON_HOLD">⏸️ ON_HOLD</option>
                  <option value="REJECTED">⛔ REJECTED</option>
                  <option value="CANCELLED">🚫 CANCELLED</option>
                </select>
              </div>

              <div className="mb-4">
                <label htmlFor="change-reason" className="form-label text-xs">
                  Audit Change Reason
                </label>
                <textarea
                  id="change-reason"
                  className="form-input text-xs h-20"
                  placeholder="Reason for status change..."
                  value={changeReason}
                  onChange={(e) => setChangeReason(e.target.value)}
                />
              </div>

              <button
                type="submit"
                disabled={isUpdating}
                className="btn-primary w-full text-xs py-2 px-4 shadow-sm"
              >
                {isUpdating ? 'Saving...' : 'Save Workflow Update'}
              </button>
            </form>
          ) : (
            <div className="card p-5 bg-amber-50/60 border border-amber-200 text-xs">
              <h3 className="font-bold text-amber-900 uppercase tracking-wider text-[11px] mb-1">
                🔒 Workflow Status Locked
              </h3>
              <p className="text-amber-800 leading-relaxed">
                Your role ({role}) has read-only access to this complaint record. Only QA Managers, Investigators, and Administrators can update status transitions.
              </p>
            </div>
          )}

          {/* Quick Info Sidebar */}
          <div className="card p-5 bg-gray-50/50 space-y-3 border border-gray-200 text-xs">
            <h4 className="font-bold text-gray-800 uppercase tracking-wider text-[11px]">
              SLA & Quality Control Metrics
            </h4>
            <div className="space-y-2 text-gray-600">
              <div className="flex justify-between border-b pb-1">
                <span>Status:</span>
                <span className="font-bold text-primary-700">{sla?.sla_status ?? 'ON_TRACK'}</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>Total Age:</span>
                <span className="font-semibold text-gray-900">{sla?.age_hours ?? 0} hrs</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>Time Under Review:</span>
                <span className="font-semibold text-gray-900">{sla?.time_under_review_hours ?? 0} hrs</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>SLA Target Limit:</span>
                <span className="font-semibold text-gray-900">{sla?.sla_target_hours ?? 168} hrs</span>
              </div>
              <div className="flex justify-between">
                <span>AI Model:</span>
                <span className="font-mono">{ai?.model_used || 'gemma2-9b-it'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>

    {/* ── 21 CFR Part 11 Electronic Signature Modal ──────────────────────── */}
    {detail && (
      <ElectronicSignatureModal
        complaintId={detail.id}
        complaintNumber={detail.complaint_id}
        currentStatus={detail.status}
        targetStatus={sigTargetStatus}
        isOpen={sigModalOpen}
        onClose={() => setSigModalOpen(false)}
        onSuccess={(response: ElectronicSignatureResponse) => {
          dispatch(
            addToast({
              type: 'success',
              title: '✅ Electronic Signature Recorded',
              message: `21 CFR Part 11 signature applied by ${response.signed_by}. Complaint advanced to ${sigTargetStatus}.`,
            }),
          );
          setSigModalOpen(false);
          if (id) dispatch(fetchComplaintDetail(id));
        }}
      />
    )}

    {/* ── CAPA Creation Modal ───────────────────────────────────────────── */}
    {detail && (
      <CAPACreateModal
        complaintId={detail.id}
        complaintNumber={detail.complaint_id}
        isOpen={createCapaModalOpen}
        onClose={() => setCreateCapaModalOpen(false)}
        onSuccess={(newCapa) => {
          setCapaList((prev) => [newCapa, ...prev]);
          dispatch(
            addToast({
              type: 'success',
              title: 'CAPA Record Created',
              message: `CAPA ${newCapa.capa_number} created successfully.`,
            }),
          );
        }}
      />
    )}
    </>
  );
}




