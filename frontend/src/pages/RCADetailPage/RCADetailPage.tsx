import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import ElectronicSignatureModal from '@/components/complaint/ElectronicSignatureModal/ElectronicSignatureModal';

import { FishboneDiagram } from '@/components/rca/FishboneDiagram';
import { FiveWhysForm } from '@/components/rca/FiveWhysForm';
import { FMEARiskMatrix } from '@/components/rca/FMEARiskMatrix';
import { fetchRCADetail } from '@/services/rcaService';

import type { RCARead } from '@/types/rca.types';

export const RCADetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [rca, setRca] = useState<RCARead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isApproveOpen, setIsApproveOpen] = useState(false);

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await fetchRCADetail(id);
      setRca(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load RCA investigation record.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);



  if (loading) {
    return <div className="p-8 text-center text-xs text-gray-500">Loading RCA Record...</div>;
  }

  if (error || !rca) {
    return (
      <div className="p-8 text-center text-xs text-red-600 bg-red-50 rounded-xl border border-red-200">
        ⚠️ {error || 'RCA investigation record not found.'}
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-gray-900">{rca.rca_number}</h1>
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold ${
                rca.status === 'APPROVED'
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : 'bg-amber-100 text-amber-800 border border-amber-300'
              }`}
            >
              {rca.status === 'APPROVED' ? '✅ APPROVED' : '📝 DRAFT / UNDER REVIEW'}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Linked Complaint:{' '}
            <Link
              to={`/complaints/${rca.complaint_id}`}
              className="text-primary-600 font-semibold underline"
            >
              {rca.complaint_number || rca.complaint_id}
            </Link>
          </p>
        </div>

        {rca.status !== 'APPROVED' && (
          <button
            onClick={() => setIsApproveOpen(true)}
            className="px-5 py-2.5 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700 transition-colors shadow-md flex items-center gap-2"
          >
            ✍️ Approve RCA (21 CFR Part 11 Signature)
          </button>
        )}
      </div>

      {/* Primary Root Cause Banner */}
      <div className="bg-slate-900 text-white p-6 rounded-xl border border-slate-800 shadow-xl space-y-2">
        <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">
          Primary Root Cause Finding
        </span>
        <p className="text-base font-semibold leading-relaxed">{rca.primary_root_cause}</p>
        <div className="flex gap-4 text-xs text-slate-400 pt-2 border-t border-slate-800">
          <span>Category: <strong className="text-slate-200">{rca.root_cause_category}</strong></span>
          <span>Methodology: <strong className="text-slate-200">{rca.methodology}</strong></span>
          <span>Created By: <strong className="text-slate-200">{rca.created_by}</strong></span>
        </div>
      </div>

      {/* 5 Whys Section */}
      {rca.five_whys && rca.five_whys.length > 0 && (
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center gap-2">
            ❓ 5 Whys Iterative Analysis
          </h3>
          <FiveWhysForm items={rca.five_whys} />
        </div>
      )}

      {/* 6M Fishbone Section */}
      {rca.fishbone && (
        <FishboneDiagram categories={rca.fishbone} primaryCause={rca.primary_root_cause} />
      )}

      {/* FMEA Risk Assessment Matrix */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center gap-2">
          📊 FMEA Failure Mode & Risk Priority Matrix
        </h3>
        <FMEARiskMatrix items={rca.fmea_items} />
      </div>

      {/* Approval E-Signature Modal */}
      <ElectronicSignatureModal
        isOpen={isApproveOpen}
        onClose={() => setIsApproveOpen(false)}
        onSuccess={() => {
          setIsApproveOpen(false);
          loadData();
        }}
        complaintId={rca.complaint_id}
        complaintNumber={rca.complaint_number || rca.complaint_id}
        currentStatus={rca.status}
        targetStatus="APPROVED"
      />

    </div>
  );
};

export default RCADetailPage;

