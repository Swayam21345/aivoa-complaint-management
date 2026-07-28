import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { analyzeComplaint } from '@/services/uploadService';
import type { UploadResponse } from '@/types/api.types';
import type { InputType } from '@/types/complaint.types';

// ─── Validation constants ─────────────────────────────────────────────────────

export const MAX_PDF_SIZE_BYTES = 20 * 1024 * 1024;   // 20 MB
export const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB

export const ALLOWED_MIME: Record<string, string[]> = {
  pdf: ['application/pdf'],
  image: ['image/jpeg', 'image/png', 'image/tiff'],
};

// ─── Thunks ───────────────────────────────────────────────────────────────────

export const uploadDocument = createAsyncThunk<
  UploadResponse,
  { inputType: InputType; file?: File; text?: string },
  { rejectValue: string }
>(
  'upload/analyzeDocument',
  async ({ inputType, file, text }, { dispatch, rejectWithValue }) => {
    try {
      return await analyzeComplaint(
        inputType,
        file,
        text,
        (percent) => dispatch(setUploadProgress(percent)),
      );
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  },
);

// ─── State ────────────────────────────────────────────────────────────────────

/** Serialisable file metadata — File objects themselves cannot go in Redux */
export interface FileMetadata {
  name: string;
  size: number;
  type: string;
}

interface UploadState {
  /** Overall request lifecycle */
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  /** Active tab selection */
  inputType: InputType | null;
  /** File selected for upload (pdf / image) */
  selectedFile: FileMetadata | null;
  /** Paste text content (email / text) */
  pastedText: string;
  /** Axios upload progress 0–100 */
  uploadProgress: number;
  /** Full API response after successful ingestion */
  result: UploadResponse | null;
  /** Extracted plain text from the last successful upload */
  extractedText: string | null;
  /** UUID of the persisted UploadRecord */
  uploadId: string | null;
  /** Character count of the extracted text */
  charCount: number | null;
  /** User-facing error message */
  error: string | null;
  /** Client-side validation error (before API call) */
  validationError: string | null;
}

const initialState: UploadState = {
  status: 'idle',
  inputType: 'pdf',
  selectedFile: null,
  pastedText: '',
  uploadProgress: 0,
  result: null,
  extractedText: null,
  uploadId: null,
  charCount: null,
  error: null,
  validationError: null,
};

// ─── Slice ────────────────────────────────────────────────────────────────────

const uploadSlice = createSlice({
  name: 'upload',
  initialState,
  reducers: {
    setInputType(state, action: PayloadAction<InputType>) {
      state.inputType = action.payload;
      state.selectedFile = null;
      state.pastedText = '';
      state.error = null;
      state.validationError = null;
      state.result = null;
      state.extractedText = null;
      state.uploadId = null;
      state.charCount = null;
      state.uploadProgress = 0;
      state.status = 'idle';
    },
    setSelectedFile(state, action: PayloadAction<FileMetadata | null>) {
      state.selectedFile = action.payload;
      state.error = null;
      state.validationError = null;
    },
    setPastedText(state, action: PayloadAction<string>) {
      state.pastedText = action.payload;
      state.error = null;
      state.validationError = null;
    },
    setUploadProgress(state, action: PayloadAction<number>) {
      state.uploadProgress = action.payload;
    },
    setValidationError(state, action: PayloadAction<string | null>) {
      state.validationError = action.payload;
    },
    resetUpload(_state) {
      return { ...initialState };
    },
    clearUploadError(state) {
      state.error = null;
      state.validationError = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(uploadDocument.pending, (state) => {
        state.status = 'loading';
        state.error = null;
        state.validationError = null;
        state.uploadProgress = 0;
        state.extractedText = null;
        state.uploadId = null;
        state.charCount = null;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.result = action.payload;
        state.extractedText = action.payload.extracted_text;
        state.uploadId = action.payload.upload_id;
        state.charCount = action.payload.char_count;
        state.uploadProgress = 100;
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload ?? 'Upload failed. Please try again.';
        state.uploadProgress = 0;
      });
  },
});

export const {
  setInputType,
  setSelectedFile,
  setPastedText,
  setUploadProgress,
  setValidationError,
  resetUpload,
  clearUploadError,
} = uploadSlice.actions;

export default uploadSlice.reducer;
