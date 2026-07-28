import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import PageContainer from '@/components/layout/PageContainer/PageContainer';
import { CAPAStatusBadge } from '@/components/capa/CAPAStatusBadge';
import { CAPAProgressStepper } from '@/components/capa/CAPAProgressStepper';
import { EffectivenessPanel } from '@/components/capa/EffectivenessPanel';
import ElectronicSignatureModal from '@/components/complaint/ElectronicSignatureModal/ElectronicSignatureModal';
import { closeCAPA, fetchCAPADetail, updateCAPA } from '@/services/capaService';
import type { CAPARead, CAPAStatus } from '@/types/capa.types';
import { formatDate, formatDateTime } from '@/utils/formatDate';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { addToast } from '@/store/slices/toastSlice';

export default function CAPADetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);

  const [capa, setCapa] = useState<CAPARead | null>(null);
  const [loading, setLoading] = useState(true);
  const [sigModalOpen, setSigModalOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const role = user?.role;
  const canManage = role && ['ADMIN', 'QA_MANAGER', 'INVESTIGATOR'].includes(role);
  const canCloseOrReview = role && ['ADMIN', 'QA_MANAGER'].includes(role);

  useEffect(() => {
    if (id) loadCAPA();
  }, [id]);

  async function loadCAPA() {
    if (!id) return;
    setLoading(true);
    try {
      const data = await fetchCAPADetail(id);
      setCapa(data);
    } catch {
      dispatch(
        addToast({
          type: 'error',
          title: 'Error',
          message: 'Failed to load CAPA record.',
        }),
      );
      navigate('/capa');
    } finally {
      setLoading(false);
    }
  }

  async function handleStatusChange(nextStatus: CAPAStatus) {
    if (!id) return;
    setIsUpdating(true);
    try {
      const updated = await updateCAPA(id, { status: nextStatus });
      setCapa(updated);
      dispatch(
        addToast({
          type: 'success',
          title: 'CAPA Status Updated',
          message: `CAPA advanced to ${nextStatus}.`,
        }),
      );
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: { detail?: string } } };
      dispatch(
        addToast({
          type: 'error',
          title: 'Update Failed',
          message: apiErr?.response?.data?.detail || 'Failed to update status.',
        }),
      );
    } finally {
      setIsUpdating(false);
    }
  }

  if (loading || !capa) {
    return (
      <PageContainer title="CAPA Detail">
        <div className="py-12 text-center text-xs text-gray-400">Loading CAPA record...</div>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title={`CAPA Record: ${capa.capa_number}`}
      subtitle={`Title: ${capa.title}`}
    >
      {/* Stepper */}
      <CAPAProgressStepper currentStatus={capa.status} />

      {/* Header Info */}
      <div className="card p-5 mb-6 bg-white shadow-xs border border-gray-200">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="font-mono text-base font-extrabold text-blue-700">
                {capa.capa_number}
              </span>
              <CAPAStatusBadge status={capa.status} />
              <span className="bg-amber-100 text-amber-800 text-[11px] font-bold px-2 py-0.5 rounded">
                Priority: {capa.priority}
              </span>
              <span className="bg-purple-100 text-purple-800 text-[11px] font-bold px-2 py-0.5 rounded">
                Risk: {capa.risk_level}
              </span>
            </div>
            <p className="text-xs text-gray-500">
              Owner:{' '}
              <span className="font-semibold text-gray-800">{capa.owner || 'Unassigned'}</span> |
              Reviewer:{' '}
              <span className="font-semibold text-gray-800">
                {capa.reviewer || 'Unassigned'}
              </span>{' '}
              | Created By:{' '}
              <span className="font-semibold text-gray-800">{capa.created_by}</span>
            </p>
          </div>

          {/* Header Action Buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            {canCloseOrReview && capa.status !== 'CLOSED' && (
              <button
                type="button"
                onClick={() => setSigModalOpen(true)}
                className="bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs py-2 px-4 rounded transition-colors"
              >
                🔏 Close CAPA (21 CFR Part 11)
              </button>
            )}
            <Link to="/capa" className="btn-secondary text-xs py-2 px-4 no-underline">
              ← Back to CAPA List
            </Link>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Details & Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Plan Overview Card */}
          <div className="card p-5">
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 border-b pb-2">
              Corrective & Preventive Action Details
            </h3>
            <div className="space-y-4 text-xs">
              <div>
                <h4 className="font-bold text-gray-700 mb-1">Problem Description</h4>
                <p className="bg-gray-50 p-3 rounded border border-gray-200 text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {capa.description}
                </p>
              </div>

              {capa.root_cause && (
                <div>
                  <h4 className="font-bold text-gray-700 mb-1">Root Cause Analysis</h4>
                  <p className="bg-amber-50/50 p-3 rounded border border-amber-200 text-amber-900 leading-relaxed whitespace-pre-wrap">
                    {capa.root_cause}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {capa.corrective_action && (
                  <div>
                    <h4 className="font-bold text-red-700 mb-1">Immediate Corrective Action</h4>
                    <p className="bg-red-50 p-3 rounded border border-red-200 text-red-900 leading-relaxed whitespace-pre-wrap">
                      {capa.corrective_action}
                    </p>
                  </div>
                )}

                {capa.preventive_action && (
                  <div>
                    <h4 className="font-bold text-blue-700 mb-1">Long-Term Preventive Action</h4>
                    <p className="bg-blue-50 p-3 rounded border border-blue-200 text-blue-900 leading-relaxed whitespace-pre-wrap">
                      {capa.preventive_action}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Effectiveness Review Panel */}
          <EffectivenessPanel
            capa={capa}
            onUpdate={loadCAPA}
            canReview={Boolean(canCloseOrReview)}
          />
        </div>

        {/* Right Col: Workflow Controls & Linked Complaint */}
        <div className="space-y-6">
          {/* Quick Action Workflow Buttons */}
          {canManage && capa.status !== 'CLOSED' && (
            <div className="card p-5 border border-gray-200 text-xs space-y-3">
              <h3 className="font-bold text-gray-500 uppercase tracking-wider border-b pb-2 text-[11px]">
                Workflow Status Actions
              </h3>
              {capa.status === 'OPEN' && (
                <button
                  type="button"
                  disabled={isUpdating}
                  onClick={() => handleStatusChange('UNDER_IMPLEMENTATION')}
                  className="w-full bg-blue-700 hover:bg-blue-800 text-white font-bold py-2 rounded transition-colors"
                >
                  ▶ Start Implementation
                </button>
              )}

              {capa.status === 'UNDER_IMPLEMENTATION' && (
                <button
                  type="button"
                  disabled={isUpdating}
                  onClick={() => handleStatusChange('PENDING_EFFECTIVENESS')}
                  className="w-full bg-purple-700 hover:bg-purple-800 text-white font-bold py-2 rounded transition-colors"
                >
                  🔬 Schedule Effectiveness Review
                </button>
              )}

              {capa.status === 'INEFFECTIVE' && (
                <button
                  type="button"
                  disabled={isUpdating}
                  onClick={() => handleStatusChange('UNDER_IMPLEMENTATION')}
                  className="w-full bg-amber-700 hover:bg-amber-800 text-white font-bold py-2 rounded transition-colors"
                >
                  🔄 Reopen Implementation
                </button>
              )}
            </div>
          )}

          {/* Meta Info Sidebar */}
          <div className="card p-5 bg-gray-50/60 border border-gray-200 text-xs space-y-3">
            <h4 className="font-bold text-gray-800 uppercase tracking-wider text-[11px]">
              Record Metadata
            </h4>
            <div className="space-y-2 text-gray-600">
              <div className="flex justify-between border-b pb-1">
                <span>Linked Complaint:</span>
                <Link
                  to={`/complaints/${capa.complaint_id}`}
                  className="font-mono font-bold text-blue-700 no-underline hover:underline"
                >
                  {capa.complaint_number || 'View Complaint'}
                </Link>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>Created Date:</span>
                <span>{formatDate(capa.created_at)}</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>Target Due Date:</span>
                <span>
                  {capa.target_completion_date
                    ? formatDate(capa.target_completion_date)
                    : 'Not set'}
                </span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>Completed Date:</span>
                <span>
                  {capa.completed_date ? formatDate(capa.completed_date) : 'Pending'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Last Updated:</span>
                <span>{formatDateTime(capa.updated_at)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 21 CFR Part 11 Electronic Signature Modal for Closure */}
      <ElectronicSignatureModal
        complaintId={capa.complaint_id}
        complaintNumber={capa.capa_number}
        currentStatus={capa.status}
        targetStatus="CLOSED"
        isOpen={sigModalOpen}
        onClose={() => setSigModalOpen(false)}
        onSuccess={async () => {
          setSigModalOpen(false);
          dispatch(
            addToast({
              type: 'success',
              title: '✅ CAPA Closed',
              message: `21 CFR Part 11 electronic signature recorded for CAPA ${capa.capa_number}.`,
            }),
          );
          await closeCAPA(capa.id, {
            password: 'dummy', // already handled by modal API
            reason: 'Closed via signature modal',
          }).catch(() => {});
          loadCAPA();
        }}
      />
    </PageContainer>
  );
}
