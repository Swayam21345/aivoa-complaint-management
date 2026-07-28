import type { AIAnalysis, InputType } from './complaint.types';

// ─── Upload ───────────────────────────────────────────────────────────────────

export interface UploadResponse {
  status: 'success' | 'error';
  input_type: InputType;
  /** UUID of the persisted UploadRecord row */
  upload_id: string;
  /** Original filename — null for text / email inputs */
  original_filename: string | null;
  /** File size in bytes — null for text / email inputs */
  file_size_bytes: number | null;
  /** Plain text extracted from the document */
  extracted_text: string;
  /** Character count of extracted_text */
  char_count: number;
  /** AI-extracted complaint fields — null until Phase 3 */
  ai_analysis: AIAnalysis | null;
  /** Total wall-clock time for ingestion in ms */
  processing_time_ms: number | null;
}

// ─── Create complaint ─────────────────────────────────────────────────────────

export interface CreateComplaintRequest {
  product_name: string;
  batch_number: string;
  customer_name: string;
  category: string;
  risk_level: string;
  complaint_text: string;
  reviewer_notes?: string;
  submitted_by?: string;
  ai_analysis?: AIAnalysis | null;
}

export interface CreateComplaintResponse {
  complaint_id: string;
  id: string;
  status: string;
  created_at: string;
}

// ─── Update complaint ─────────────────────────────────────────────────────────

export interface UpdateComplaintRequest {
  status?: string;
  reviewer_notes?: string;
  change_reason?: string;
  changed_by?: string;
}

export interface UpdateComplaintResponse {
  id: string;
  complaint_id: string;
  status: string;
  updated_at: string;
}

// ─── Generic API error ────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  status_code?: number;
}
