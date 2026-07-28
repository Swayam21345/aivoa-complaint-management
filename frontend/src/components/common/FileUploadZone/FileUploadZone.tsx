import { useRef, useState, useCallback } from 'react';
import type { DragEvent, ChangeEvent } from 'react';

interface FileUploadZoneProps {
  accept: string;                         // e.g. ".pdf" | ".jpg,.jpeg,.png,.tiff"
  maxSizeBytes: number;
  onFileSelected: (file: File) => void;
  onValidationError: (msg: string) => void;
  disabled?: boolean;
  /** Short label shown inside the drop zone, e.g. "PDF up to 20 MB" */
  hint: string;
}

/**
 * Drag-and-drop file upload zone.
 * Validates file type and size client-side before calling onFileSelected.
 * Accessible: keyboard-operable via Enter/Space, ARIA roles set correctly.
 */
export default function FileUploadZone({
  accept,
  maxSizeBytes,
  onFileSelected,
  onValidationError,
  disabled = false,
  hint,
}: FileUploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Convert accept string ".pdf,.jpg" → array of extensions / mime types
  const acceptedTypes = accept.split(',').map((s) => s.trim().toLowerCase());

  const validate = useCallback(
    (file: File): string | null => {
      // Extension / MIME check
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      const mimeOk = acceptedTypes.some(
        (t) => t === ext || file.type.startsWith(t.replace('*', '')),
      );
      if (!mimeOk) {
        return `File type "${ext}" is not supported. Accepted: ${accept}`;
      }
      // Size check
      if (file.size > maxSizeBytes) {
        const limitMb = Math.round(maxSizeBytes / (1024 * 1024));
        return `File is too large. Maximum allowed size is ${limitMb} MB.`;
      }
      return null;
    },
    [accept, acceptedTypes, maxSizeBytes],
  );

  const handleFile = useCallback(
    (file: File) => {
      const error = validate(file);
      if (error) {
        onValidationError(error);
      } else {
        onFileSelected(file);
      }
    },
    [validate, onFileSelected, onValidationError],
  );

  // ── Drag handlers ──────────────────────────────────────────────────────────
  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };
  const onDragLeave = () => setIsDragging(false);
  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  // ── Input change ───────────────────────────────────────────────────────────
  const onInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    // Reset input so the same file can be re-selected after an error
    e.target.value = '';
  };

  const openPicker = () => {
    if (!disabled) inputRef.current?.click();
  };

  const borderClass = isDragging
    ? 'border-primary-600 bg-primary-50'
    : 'border-gray-300 bg-white hover:border-primary-400 hover:bg-gray-50';

  const cursorClass = disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer';

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="File upload drop zone. Press Enter or Space to browse files."
      aria-disabled={disabled}
      className={`
        flex flex-col items-center justify-center gap-3
        rounded-lg border-2 border-dashed p-10 text-center
        transition-colors select-none
        ${borderClass} ${cursorClass}
      `}
      onClick={openPicker}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openPicker();
        }
      }}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {/* Upload icon */}
      <svg
        className="w-10 h-10 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.5}
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
        />
      </svg>

      <div>
        <p className="text-sm font-medium text-gray-700">
          Drag and drop your file here, or{' '}
          <span className="text-primary-600 underline">browse</span>
        </p>
        <p className="mt-1 text-xs text-gray-400">{hint}</p>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="sr-only"
        aria-hidden="true"
        tabIndex={-1}
        onChange={onInputChange}
        disabled={disabled}
      />
    </div>
  );
}
