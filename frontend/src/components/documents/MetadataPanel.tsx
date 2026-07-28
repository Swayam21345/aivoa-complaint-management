import React from 'react';
import { formatDate } from '@/utils/formatDate';
import type { DocumentRead } from '@/types/document.types';

interface MetadataPanelProps {
  document: DocumentRead;
}

export const MetadataPanel: React.FC<MetadataPanelProps> = ({ document }) => {
  const latest = document.versions?.[0];

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3 text-xs">
      <h4 className="font-bold text-gray-800 uppercase tracking-wider text-[11px] border-b pb-2">
        📄 Controlled Document Metadata
      </h4>
      <div className="space-y-2 text-gray-600">
        <div className="flex justify-between">
          <span className="font-medium text-gray-500">Document Number:</span>
          <span className="font-bold font-mono text-gray-900">{document.document_number}</span>
        </div>
        <div className="flex justify-between">
          <span className="font-medium text-gray-500">Category:</span>
          <span className="font-semibold text-primary-700">{document.category}</span>
        </div>
        <div className="flex justify-between">
          <span className="font-medium text-gray-500">Entity Type:</span>
          <span className="font-semibold text-slate-800">{document.entity_type}</span>
        </div>
        <div className="flex justify-between">
          <span className="font-medium text-gray-500">Current Version:</span>
          <span className="font-bold font-mono text-slate-900">v{document.current_version}</span>
        </div>
        <div className="flex justify-between">
          <span className="font-medium text-gray-500">Approval Status:</span>
          <span
            className={`font-bold px-2 py-0.5 rounded text-[10px] ${
              document.status === 'APPROVED'
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-amber-100 text-amber-800'
            }`}
          >
            {document.status}
          </span>
        </div>
        {latest && (
          <>
            <div className="flex justify-between">
              <span className="font-medium text-gray-500">Original Filename:</span>
              <span className="font-mono text-gray-800 truncate max-w-[150px]">
                {latest.original_filename}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-gray-500">File Size:</span>
              <span className="font-mono font-semibold text-gray-800">
                {formatBytes(latest.size)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-gray-500">MIME Type:</span>
              <span className="font-mono text-gray-700">{latest.mime_type}</span>
            </div>
            <div className="pt-2 border-t border-gray-100">
              <p className="font-medium text-gray-500 mb-1 text-[10px]">SHA-256 Checksum:</p>
              <p className="font-mono text-[9px] bg-slate-50 p-2 rounded border border-slate-200 break-all text-slate-700">
                {latest.sha256_hash}
              </p>
            </div>
          </>
        )}
        <div className="pt-2 border-t border-gray-100 flex justify-between text-[11px]">
          <span className="text-gray-500">Uploaded By:</span>
          <span className="font-medium text-gray-800">{document.created_by}</span>
        </div>
        <div className="flex justify-between text-[11px]">
          <span className="text-gray-500">Created Date:</span>
          <span className="font-medium text-gray-800">{formatDate(document.created_at)}</span>
        </div>
      </div>
    </div>
  );
};
