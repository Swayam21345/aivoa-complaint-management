import React from 'react';
import { getDocumentDownloadUrl } from '@/services/documentService';
import type { DocumentRead } from '@/types/document.types';

interface DocumentPreviewProps {
  document: DocumentRead;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({ document }) => {
  const latest = document.versions?.[0];
  if (!latest) {
    return <div className="p-8 text-center text-xs text-gray-400">No file preview available.</div>;
  }

  const downloadUrl = getDocumentDownloadUrl(document.id, latest.id);
  const mime = latest.mime_type.toLowerCase();
  const ext = latest.original_filename.includes('.') ? latest.original_filename.split('.').pop()?.toLowerCase() || '' : '';


  const isImage = mime.startsWith('image/') || ['png', 'jpg', 'jpeg', 'gif'].includes(ext);
  const isPDF = mime.includes('pdf') || ext === 'pdf';
  const isVideo = mime.startsWith('video/') || ext === 'mp4';

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden p-4 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
        <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
          🖼️ Document Evidence Preview ({latest.original_filename})
        </span>
        <a
          href={downloadUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-bold transition-colors"
        >
          ⬇️ Open Original
        </a>
      </div>

      <div className="flex items-center justify-center min-h-[300px] bg-slate-950 rounded-lg border border-slate-800 p-4">
        {isImage ? (
          <img
            src={downloadUrl}
            alt={latest.original_filename}
            className="max-h-[500px] max-w-full object-contain rounded shadow-lg"
          />
        ) : isPDF ? (
          <iframe
            src={downloadUrl}
            title={latest.original_filename}
            className="w-full h-[500px] rounded border border-slate-800"
          />
        ) : isVideo ? (
          <video controls className="max-h-[500px] max-w-full rounded shadow-lg">
            <source src={downloadUrl} type={latest.mime_type} />
            Your browser does not support the video tag.
          </video>
        ) : (
          <div className="text-center p-8 space-y-3">
            <div className="text-5xl">📄</div>
            <p className="text-xs font-semibold text-slate-300">{latest.original_filename}</p>
            <p className="text-[11px] text-slate-400">
              Direct preview not supported for {latest.mime_type}. Use download button to view file.
            </p>
            <a
              href={downloadUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded text-xs font-bold border border-slate-700 transition-colors"
            >
              📥 Download File ({ (latest.size / (1024 * 1024)).toFixed(2) } MB)
            </a>
          </div>
        )}
      </div>
    </div>
  );
};
