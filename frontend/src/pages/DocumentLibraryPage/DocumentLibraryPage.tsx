import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchDocumentDashboard, fetchDocumentList, getDocumentDownloadUrl } from '@/services/documentService';
import type { DocumentDashboardRead, DocumentRead } from '@/types/document.types';

export const DocumentLibraryPage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentRead[]>([]);
  const [dashboard, setDashboard] = useState<DocumentDashboardRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [entityTypeFilter, setEntityTypeFilter] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [listRes, dashRes] = await Promise.all([
        fetchDocumentList({
          search: search || undefined,
          category: categoryFilter || undefined,
          status: statusFilter || undefined,
          entity_type: entityTypeFilter || undefined,
        }),
        fetchDocumentDashboard(),
      ]);
      setDocuments(listRes.items);
      setDashboard(dashRes);
    } catch (err) {
      console.error('Failed to load document library:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search, categoryFilter, statusFilter, entityTypeFilter]);

  const getStatusBadge = (st: string) => {
    switch (st) {
      case 'APPROVED':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
            ✅ Approved
          </span>
        );
      case 'ARCHIVED':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-600 border border-gray-200">
            📦 Archived
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
            📝 Draft
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 flex items-center gap-2">
            📁 Controlled Document & Evidence Library
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            21 CFR Part 11 Compliant Evidence Repository with SHA-256 Checksums
          </p>
        </div>
      </div>

      {/* Metrics Row */}
      {dashboard && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
              Total Documents
            </p>
            <p className="text-2xl font-black text-slate-900 mt-1">{dashboard.total_documents}</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-600">
              Approved Records
            </p>
            <p className="text-2xl font-black text-emerald-700 mt-1">
              {dashboard.approved_documents}
            </p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-amber-600">
              Draft / Under Review
            </p>
            <p className="text-2xl font-black text-amber-700 mt-1">{dashboard.draft_documents}</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
              Archived Documents
            </p>
            <p className="text-2xl font-black text-gray-700 mt-1">{dashboard.archived_documents}</p>
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 Search documents by number, title, or description..."
          className="w-full md:w-96 rounded-lg border-gray-300 border p-2 text-xs focus:ring-primary-500"
        />

        <div className="flex flex-wrap gap-2 w-full md:w-auto">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="rounded-lg border-gray-300 border p-2 text-xs bg-white"
          >
            <option value="">All Categories</option>
            <option value="Complaint Evidence">Complaint Evidence</option>
            <option value="Customer Images">Customer Images</option>
            <option value="Lab Report">Lab Report</option>
            <option value="Root Cause Evidence">Root Cause Evidence</option>
            <option value="CAPA Evidence">CAPA Evidence</option>
            <option value="Supplier Evidence">Supplier Evidence</option>
            <option value="Certificate">Certificate</option>
          </select>

          <select
            value={entityTypeFilter}
            onChange={(e) => setEntityTypeFilter(e.target.value)}
            className="rounded-lg border-gray-300 border p-2 text-xs bg-white"
          >
            <option value="">All Entities</option>
            <option value="COMPLAINT">Complaints</option>
            <option value="RCA">RCA Records</option>
            <option value="CAPA">CAPA Records</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border-gray-300 border p-2 text-xs bg-white"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="APPROVED">Approved</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-xs text-gray-500">Loading document library...</div>
        ) : documents.length === 0 ? (
          <div className="p-8 text-center text-xs text-gray-500">No documents found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead className="bg-gray-50 text-gray-700 uppercase text-[10px] font-bold tracking-wider border-b border-gray-200">
                <tr>
                  <th className="py-3 px-4">Document #</th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Entity</th>
                  <th className="py-3 px-4">Version</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="text-primary-600 hover:text-primary-800 underline"
                      >
                        {doc.document_number}
                      </Link>
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-800">{doc.title}</td>
                    <td className="py-3 px-4 font-medium text-gray-600">{doc.category}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                        {doc.entity_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-gray-700">
                      v{doc.current_version}
                    </td>
                    <td className="py-3 px-4">{getStatusBadge(doc.status)}</td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <a
                        href={getDocumentDownloadUrl(doc.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-2.5 py-1 bg-slate-100 text-slate-800 rounded text-[11px] font-semibold hover:bg-slate-200 transition-colors border border-slate-300"
                      >
                        ⬇️ Download
                      </a>
                      <Link
                        to={`/documents/${doc.id}`}
                        className="px-2.5 py-1 bg-slate-900 text-white rounded text-[11px] font-semibold hover:bg-slate-800 transition-colors"
                      >
                        View Record →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentLibraryPage;
