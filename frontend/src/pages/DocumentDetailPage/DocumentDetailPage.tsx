import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ElectronicSignatureModal from '@/components/complaint/ElectronicSignatureModal/ElectronicSignatureModal';
import { DocumentPreview } from '@/components/documents/DocumentPreview';
import { HashVerificationBadge } from '@/components/documents/HashVerificationBadge';
import { MetadataPanel } from '@/components/documents/MetadataPanel';
import { VersionTimeline } from '@/components/documents/VersionTimeline';
import {
  archiveDocument,
  fetchDocumentDetail,
  restoreDocument,
  uploadNewVersion,
} from '@/services/documentService';
import type { DocumentRead } from '@/types/document.types';

export const DocumentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [doc, setDoc] = useState<DocumentRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isApproveOpen, setIsApproveOpen] = useState(false);

  // New version upload state
  const [newFile, setNewFile] = useState<File | null>(null);
  const [changeSummary, setChangeSummary] = useState('');
  const [uploadingVersion, setUploadingVersion] = useState(false);

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await fetchDocumentDetail(id);
      setDoc(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load document record.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleUploadVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !newFile) return;

    setUploadingVersion(true);
    try {
      await uploadNewVersion(id, newFile, changeSummary);
      setNewFile(null);
      setChangeSummary('');
      await loadData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to upload new version.');
    } finally {
      setUploadingVersion(false);
    }
  };

  const handleArchive = async () => {
    if (!id) return;
    await archiveDocument(id);
    await loadData();
  };

  const handleRestore = async () => {
    if (!id) return;
    await restoreDocument(id);
    await loadData();
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-gray-500">Loading Document Record...</div>;
  }

  if (error || !doc) {
    return (
      <div className="p-8 text-center text-xs text-red-600 bg-red-50 rounded-xl border border-red-200">
        ⚠️ {error || 'Document record not found.'}
      </div>
    );
  }

  const latest = doc.versions?.[0];

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-gray-900">{doc.document_number}</h1>
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold ${
                doc.status === 'APPROVED'
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : doc.status === 'ARCHIVED'
                  ? 'bg-gray-100 text-gray-600 border border-gray-300'
                  : 'bg-amber-100 text-amber-800 border border-amber-300'
              }`}
            >
              {doc.status === 'APPROVED'
                ? '✅ APPROVED'
                : doc.status === 'ARCHIVED'
                ? '📦 ARCHIVED'
                : '📝 DRAFT'}
            </span>
          </div>
          <p className="text-xs font-semibold text-gray-700 mt-1">{doc.title}</p>
        </div>

        <div className="flex items-center gap-2">
          {latest && (
            <HashVerificationBadge
              documentId={doc.id}
              versionId={latest.id}
              storedHash={latest.sha256_hash}
            />
          )}

          {doc.status !== 'APPROVED' && doc.status !== 'ARCHIVED' && (
            <button
              onClick={() => setIsApproveOpen(true)}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700 transition-colors shadow-md"
            >
              ✍️ Approve Document
            </button>
          )}

          {doc.status !== 'ARCHIVED' ? (
            <button
              onClick={handleArchive}
              className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-xs font-semibold hover:bg-gray-200 transition-colors border border-gray-300"
            >
              📦 Archive
            </button>
          ) : (
            <button
              onClick={handleRestore}
              className="px-3 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition-colors"
            >
              ↩️ Restore
            </button>
          )}
        </div>
      </div>

      {/* Main Grid: Left Preview & Versions (2/3), Right Metadata (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Document Preview */}
          <DocumentPreview document={doc} />

          {/* Upload New Version Form */}
          <form
            onSubmit={handleUploadVersion}
            className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3 text-xs"
          >
            <h4 className="font-bold text-gray-900 uppercase tracking-wider text-[11px] border-b pb-2 flex items-center justify-between">
              <span>🔄 Upload New Version (v{doc.current_version + 1})</span>
              <span className="text-gray-400 font-normal text-[10px]">Never Overwrites</span>
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block font-medium text-gray-700 mb-1">Select File</label>
                <input
                  type="file"
                  required
                  onChange={(e) => setNewFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-gray-500 file:mr-2 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-slate-900 file:text-white hover:file:bg-slate-800"
                />
              </div>

              <div>
                <label className="block font-medium text-gray-700 mb-1">Change Summary</label>
                <input
                  type="text"
                  value={changeSummary}
                  onChange={(e) => setChangeSummary(e.target.value)}
                  placeholder="e.g. Updated signature block"
                  className="w-full rounded-lg border-gray-300 border p-2 text-xs"
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                type="submit"
                disabled={uploadingVersion || !newFile}
                className="px-4 py-2 bg-slate-900 text-white rounded-lg font-bold text-xs hover:bg-slate-800 transition-colors shadow-md disabled:opacity-50"
              >
                {uploadingVersion ? 'Uploading Version...' : '⬆️ Upload Version'}
              </button>
            </div>
          </form>

          {/* Version Timeline History */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider border-b pb-2">
              📜 Version Audit History
            </h3>
            <VersionTimeline documentId={doc.id} versions={doc.versions} />
          </div>
        </div>

        {/* Right Sidebar: Metadata */}
        <div>
          <MetadataPanel document={doc} />
        </div>
      </div>

      {/* Approval E-Signature Modal */}
      <ElectronicSignatureModal
        isOpen={isApproveOpen}
        onClose={() => setIsApproveOpen(false)}
        onSuccess={() => {
          setIsApproveOpen(false);
          loadData();
        }}
        complaintId={doc.entity_id}
        complaintNumber={doc.document_number}
        currentStatus={doc.status}
        targetStatus="APPROVED"
      />
    </div>
  );
};

export default DocumentDetailPage;
