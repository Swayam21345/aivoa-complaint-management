import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

import PageContainer from '@/components/layout/PageContainer/PageContainer';
import FileUploadZone from '@/components/common/FileUploadZone/FileUploadZone';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  setInputType,
  setSelectedFile,
  setPastedText,
  setValidationError,
  resetUpload,
  clearUploadError,
  uploadDocument,
  MAX_PDF_SIZE_BYTES,
  MAX_IMAGE_SIZE_BYTES,
} from '@/store/slices/uploadSlice';
import { populateDraftFromAI } from '@/store/slices/complaintSlice';
import type { InputType } from '@/types/complaint.types';

// ─── Tab configuration ────────────────────────────────────────────────────────

interface Tab {
  id: InputType;
  label: string;
  icon: string;
  description: string;
}

const TABS: Tab[] = [
  { id: 'pdf',   label: 'PDF',   icon: '📄', description: 'Upload a complaint PDF document' },
  { id: 'image', label: 'Image', icon: '🖼️', description: 'Upload a scanned image or photo' },
  { id: 'email', label: 'Email', icon: '✉️', description: 'Paste an email body' },
  { id: 'text',  label: 'Text',  icon: '✏️', description: 'Paste plain complaint text' },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function UploadPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const {
    status,
    inputType,
    selectedFile,
    pastedText,
    uploadProgress,
    extractedText,
    result,
    error,
    validationError,
  } = useAppSelector((s) => s.upload);

  const isLoading = status === 'loading';
  const hasFile = inputType && ['pdf', 'image'].includes(inputType) && selectedFile !== null;
  const hasText = inputType && ['email', 'text'].includes(inputType) && pastedText.trim().length > 0;
  const canSubmit = !isLoading && (hasFile || hasText);

  // Navigate to complaint form once extraction succeeds and AI result is available
  useEffect(() => {
    if (status === 'succeeded') {
      if (result?.ai_analysis) {
        dispatch(populateDraftFromAI(result.ai_analysis));
      }
      navigate('/complaint/new');
    }
  }, [status, result, navigate, dispatch]);

  // Reset upload state when arriving at this page fresh
  useEffect(() => {
    dispatch(resetUpload());
  }, [dispatch]);

  // ── Handlers ──────────────────────────────────────────────────────────────

  function handleTabChange(tab: InputType) {
    dispatch(setInputType(tab));
  }

  function handleFileSelected(file: File) {
    dispatch(setSelectedFile({ name: file.name, size: file.size, type: file.type }));
    dispatch(clearUploadError());
    // Store the actual File object on a ref so the thunk can access it
    fileRef.current = file;
  }

  function handleValidationError(msg: string) {
    dispatch(setValidationError(msg));
    dispatch(setSelectedFile(null));
    fileRef.current = null;
  }

  // We cannot store a File object in Redux, so keep it in a component ref
  const fileRef = useRef<File | null>(null);

  function handleTextChange(value: string) {
    dispatch(setPastedText(value));
  }

  async function handleSubmit() {
    if (!inputType) return;
    dispatch(clearUploadError());

    if (['pdf', 'image'].includes(inputType)) {
      if (!fileRef.current) {
        dispatch(setValidationError('Please select a file before analysing.'));
        return;
      }
      dispatch(
        uploadDocument({ inputType, file: fileRef.current }),
      );
    } else {
      if (!pastedText.trim()) {
        dispatch(setValidationError('Please paste some text before analysing.'));
        return;
      }
      dispatch(uploadDocument({ inputType, text: pastedText }));
    }
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <PageContainer
      title="New Customer Complaint"
      subtitle="Upload a complaint document or paste complaint text to begin AI analysis."
    >
      <div className="max-w-2xl mx-auto">

        {/* ── Tab Selector ─────────────────────────────────────────────── */}
        <div
          className="grid grid-cols-4 gap-2 mb-6"
          role="tablist"
          aria-label="Complaint input type"
        >
          {TABS.map((tab) => {
            const isActive = inputType === tab.id;
            return (
              <button
                key={tab.id}
                role="tab"
                aria-selected={isActive}
                aria-controls={`panel-${tab.id}`}
                id={`tab-${tab.id}`}
                onClick={() => handleTabChange(tab.id)}
                disabled={isLoading}
                className={`
                  flex flex-col items-center gap-1.5 rounded-lg border-2 py-3 px-2
                  text-xs font-medium transition-colors
                  disabled:opacity-50 disabled:cursor-not-allowed
                  ${
                    isActive
                      ? 'border-primary-600 bg-primary-50 text-primary-700'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                <span className="text-xl leading-none" aria-hidden="true">
                  {tab.icon}
                </span>
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* ── Input Panel ──────────────────────────────────────────────── */}
        <div className="card p-6 mb-4">

          {/* PDF tab */}
          {inputType === 'pdf' && (
            <div
              id="panel-pdf"
              role="tabpanel"
              aria-labelledby="tab-pdf"
            >
              <FileUploadZone
                accept=".pdf"
                maxSizeBytes={MAX_PDF_SIZE_BYTES}
                hint="PDF up to 20 MB"
                onFileSelected={handleFileSelected}
                onValidationError={handleValidationError}
                disabled={isLoading}
              />
            </div>
          )}

          {/* Image tab */}
          {inputType === 'image' && (
            <div
              id="panel-image"
              role="tabpanel"
              aria-labelledby="tab-image"
            >
              <FileUploadZone
                accept=".jpg,.jpeg,.png,.tiff"
                maxSizeBytes={MAX_IMAGE_SIZE_BYTES}
                hint="JPEG, PNG, or TIFF up to 10 MB"
                onFileSelected={handleFileSelected}
                onValidationError={handleValidationError}
                disabled={isLoading}
              />
            </div>
          )}

          {/* Email tab */}
          {inputType === 'email' && (
            <div
              id="panel-email"
              role="tabpanel"
              aria-labelledby="tab-email"
            >
              <label htmlFor="email-input" className="form-label">
                Email Body
              </label>
              <textarea
                id="email-input"
                ref={textareaRef}
                className="form-input resize-none h-48 font-mono text-xs"
                placeholder="Paste the full email body here, including any relevant headers…"
                value={pastedText}
                onChange={(e) => handleTextChange(e.target.value)}
                disabled={isLoading}
                aria-describedby="email-hint"
              />
              <p id="email-hint" className="mt-1 text-xs text-gray-400">
                Email headers (From:, Subject:, etc.) will be stripped automatically.
              </p>
            </div>
          )}

          {/* Text tab */}
          {inputType === 'text' && (
            <div
              id="panel-text"
              role="tabpanel"
              aria-labelledby="tab-text"
            >
              <label htmlFor="text-input" className="form-label">
                Complaint Text
              </label>
              <textarea
                id="text-input"
                ref={textareaRef}
                className="form-input resize-none h-48"
                placeholder="Paste or type the complaint text here…"
                value={pastedText}
                onChange={(e) => handleTextChange(e.target.value)}
                disabled={isLoading}
              />
            </div>
          )}

          {/* ── Selected file indicator ──────────────────────────────── */}
          {selectedFile && (
            <div className="mt-3 flex items-center gap-2 rounded-md bg-green-50 border border-green-200 px-3 py-2">
              <svg className="w-4 h-4 text-green-600 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="text-xs text-green-800 font-medium truncate flex-1">
                {selectedFile.name}
              </span>
              <span className="text-xs text-green-600 shrink-0">
                {formatBytes(selectedFile.size)}
              </span>
              <button
                type="button"
                aria-label="Remove selected file"
                className="ml-1 text-green-500 hover:text-green-700"
                onClick={() => {
                  dispatch(setSelectedFile(null));
                  fileRef.current = null;
                }}
                disabled={isLoading}
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* ── Validation / API error ──────────────────────────────────── */}
        {(validationError || error) && (
          <div
            role="alert"
            className="mb-4 flex items-start gap-2 rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700"
          >
            <svg className="w-4 h-4 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm-.75-4.75a.75.75 0 001.5 0v-4.5a.75.75 0 00-1.5 0v4.5zm.75-7.5a.75.75 0 100 1.5.75.75 0 000-1.5z" clipRule="evenodd" />
            </svg>
            <span>{validationError ?? error}</span>
          </div>
        )}

        {/* ── Upload progress bar ─────────────────────────────────────── */}
        {isLoading && (
          <div className="mb-4" aria-live="polite" aria-label={`Upload progress: ${uploadProgress}%`}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-500 font-medium">
                {uploadProgress < 100 ? 'Uploading…' : 'Extracting text…'}
              </span>
              <span className="text-xs text-gray-500">{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
                role="progressbar"
                aria-valuenow={uploadProgress}
                aria-valuemin={0}
                aria-valuemax={100}
              />
            </div>
            {uploadProgress === 100 && (
              <p className="mt-2 text-xs text-gray-500 flex items-center gap-1.5">
                <span className="inline-block w-3 h-3 rounded-full border-2 border-primary-200 border-t-primary-600 animate-spin" />
                Extracting text from document…
              </p>
            )}
          </div>
        )}

        {/* ── Submit button ───────────────────────────────────────────── */}
        <button
          type="button"
          className="btn-primary w-full py-3 text-sm"
          onClick={handleSubmit}
          disabled={!canSubmit}
          aria-busy={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
              Analysing…
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <span aria-hidden="true">✦</span>
              Analyse with AI
            </span>
          )}
        </button>

        {/* ── Extracted text preview (Phase 2A result) ────────────────── */}
        {extractedText && status === 'succeeded' && (
          <div className="mt-6 card p-5" aria-live="polite">
            <h2 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Text extracted successfully
              <span className="ml-auto text-xs font-normal text-gray-400">
                {extractedText.length.toLocaleString()} characters
              </span>
            </h2>
            <pre className="whitespace-pre-wrap text-xs text-gray-600 bg-gray-50 rounded-md p-3 max-h-48 overflow-y-auto leading-relaxed">
              {extractedText.slice(0, 1200)}
              {extractedText.length > 1200 && (
                <span className="text-gray-400">
                  {'\n\n'}… {(extractedText.length - 1200).toLocaleString()} more characters
                </span>
              )}
            </pre>
          </div>
        )}

      </div>
    </PageContainer>
  );
}
