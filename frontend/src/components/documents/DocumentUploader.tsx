import React, { useState } from 'react';
import { uploadDocument } from '@/services/documentService';
import type { DocumentCreatePayload } from '@/types/document.types';

interface DocumentUploaderProps {
  entityType: 'COMPLAINT' | 'RCA' | 'CAPA';
  entityId: string;
  onSuccess: () => void;
  defaultCategory?: string;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  entityType,
  entityId,
  onSuccess,
  defaultCategory = 'Complaint Evidence',
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState(defaultCategory);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const handleFileChange = (selectedFile: File | null) => {
    if (!selectedFile) return;
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('File size exceeds maximum 50 MB limit.');
      return;
    }
    setFile(selectedFile);
    if (!title) {
      setTitle(selectedFile.name.replace(/\.[^/.]+$/, ''));
    }

    setError('');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    if (!title.trim()) {
      setError('Document title is required.');
      return;
    }

    setIsUploading(true);
    setError('');

    try {
      const payload: DocumentCreatePayload = {
        file,
        title,
        description,
        category,
        entity_type: entityType,
        entity_id: entityId,
      };

      await uploadDocument(payload);
      setFile(null);
      setTitle('');
      setDescription('');
      onSuccess();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to upload document.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-4 text-xs">
      <h4 className="font-bold text-gray-900 uppercase tracking-wider text-xs flex items-center gap-2 border-b pb-2">
        📤 Upload Controlled Evidence File
      </h4>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 text-red-700 border border-red-200 font-medium">
          ⚠️ {error}
        </div>
      )}

      {/* Drag & Drop Box */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-6 text-center transition-colors ${
          dragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50/50 hover:bg-gray-50'
        }`}
      >
        <input
          type="file"
          id="doc-file-input"
          onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
          className="hidden"
        />
        <label htmlFor="doc-file-input" className="cursor-pointer block">
          <div className="text-3xl mb-2">📁</div>
          {file ? (
            <p className="font-bold text-primary-700 text-xs">
              Selected: {file.name} ({ (file.size / (1024 * 1024)).toFixed(2) } MB)
            </p>
          ) : (
            <div>
              <p className="font-semibold text-gray-700 text-xs">
                Drag & Drop evidence file here or <span className="text-primary-600 underline">Browse</span>
              </p>
              <p className="text-[10px] text-gray-400 mt-1">
                Supported: PDF, PNG, JPG, DOCX, XLSX, CSV, ZIP, MP4 (Max 50 MB)
              </p>
            </div>
          )}
        </label>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block font-semibold text-gray-700 mb-1">
            Document Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Spectroscopy Seal Analysis Report"
            className="w-full rounded-lg border-gray-300 border p-2 text-xs"
          />
        </div>

        <div>
          <label className="block font-semibold text-gray-700 mb-1">Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full rounded-lg border-gray-300 border p-2 text-xs bg-white"
          >
            <option value="Complaint Evidence">Complaint Evidence</option>
            <option value="Customer Images">Customer Images</option>
            <option value="Lab Report">Lab Report</option>
            <option value="Root Cause Evidence">Root Cause Evidence</option>
            <option value="CAPA Evidence">CAPA Evidence</option>
            <option value="Supplier Evidence">Supplier Evidence</option>
            <option value="Training Document">Training Document</option>
            <option value="Calibration Report">Calibration Report</option>
            <option value="Certificate">Certificate</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block font-semibold text-gray-700 mb-1">Description / Notes</label>
        <textarea
          rows={2}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional notes regarding this evidence upload..."
          className="w-full rounded-lg border-gray-300 border p-2 text-xs"
        />
      </div>

      <div className="flex justify-end pt-1">
        <button
          type="submit"
          disabled={isUploading || !file}
          className="px-5 py-2 rounded-lg text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 transition-colors shadow-md disabled:opacity-50 flex items-center gap-2"
        >
          {isUploading ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Uploading & Computing Hash...
            </>
          ) : (
            '🔒 Upload Evidence & SHA-256 Checksum'
          )}
        </button>
      </div>
    </form>
  );
};
