import React from 'react';
import { getDocumentDownloadUrl } from '@/services/documentService';
import { formatDate } from '@/utils/formatDate';
import type { DocumentVersionRead } from '@/types/document.types';

interface VersionTimelineProps {
  documentId: string;
  versions: DocumentVersionRead[];
}

export const VersionTimeline: React.FC<VersionTimelineProps> = ({ documentId, versions }) => {
  if (!versions || versions.length === 0) {
    return <div className="text-xs text-gray-400 italic p-4">No versions recorded.</div>;
  }

  return (
    <div className="space-y-3">
      {versions.map((ver) => (
        <div
          key={ver.id}
          className="p-3.5 bg-white border border-gray-200 rounded-lg shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-3 hover:border-primary-300 transition-colors"
        >
          <div className="flex items-start gap-3">
            <span className="w-8 h-8 rounded-full bg-slate-900 text-cyan-400 font-mono font-bold text-xs flex items-center justify-center border border-slate-800 flex-shrink-0">
              v{ver.version}
            </span>
            <div className="text-xs space-y-0.5">
              <p className="font-bold text-gray-900 flex items-center gap-2">
                <span>{ver.original_filename}</span>
                <span className="text-[10px] text-gray-400 font-normal">
                  ({(ver.size / 1024).toFixed(1)} KB)
                </span>
              </p>
              <p className="text-gray-500 text-[11px]">
                Uploaded by <strong className="text-gray-700">{ver.uploaded_by}</strong> on{' '}
                {formatDate(ver.uploaded_at)}
              </p>
              {ver.change_summary && (
                <p className="text-slate-600 bg-slate-50 px-2 py-1 rounded text-[11px] font-medium border border-slate-100 mt-1">
                  Summary: {ver.change_summary}
                </p>
              )}
            </div>
          </div>

          <a
            href={getDocumentDownloadUrl(documentId, ver.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded font-semibold text-[11px] border border-slate-300 transition-colors flex items-center gap-1 self-end md:self-auto"
          >
            📥 Download v{ver.version}
          </a>
        </div>
      ))}
    </div>
  );
};
