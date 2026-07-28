import React, { useState } from 'react';
import { verifyDocumentHash } from '@/services/documentService';
import type { DocumentVerifyResponse } from '@/types/document.types';

interface HashVerificationBadgeProps {
  documentId: string;
  versionId?: string;
  storedHash: string;
}

export const HashVerificationBadge: React.FC<HashVerificationBadgeProps> = ({
  documentId,
  versionId,
  storedHash,
}) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DocumentVerifyResponse | null>(null);

  const handleVerify = async () => {
    setLoading(true);
    try {
      const res = await verifyDocumentHash(documentId, versionId);
      setResult(res);
    } catch (err) {
      console.error('Hash verification failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="inline-flex items-center gap-2">
      {!result ? (
        <button
          type="button"
          onClick={handleVerify}
          disabled={loading}
          className="px-2.5 py-1 rounded bg-slate-100 text-slate-700 hover:bg-slate-200 text-[10px] font-mono font-bold border border-slate-300 transition-colors flex items-center gap-1.5"
          title={`SHA-256: ${storedHash}`}
        >
          <span>🔒 Hash: {storedHash.slice(0, 10)}...</span>
          <span className="text-[9px] text-cyan-600 font-sans">{loading ? '⏳ Verifying...' : '⚡ Verify Hash'}</span>
        </button>
      ) : result.is_valid ? (
        <span className="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold border border-emerald-300 flex items-center gap-1">
          ✅ Hash Validated (SHA-256)
        </span>
      ) : (
        <span className="px-2.5 py-1 rounded bg-red-100 text-red-800 text-[10px] font-bold border border-red-300 flex items-center gap-1">
          🚨 Hash Mismatch / File Tampered
        </span>
      )}
    </div>
  );
};
