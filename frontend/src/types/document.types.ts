export interface DocumentVersionRead {
  id: string;
  document_id: string;
  version: number;
  original_filename: string;
  stored_filename: string;
  mime_type: string;
  size: number;
  sha256_hash: string;
  storage_path: string;
  uploaded_by: string;
  uploaded_at: string;
  change_summary?: string;
}

export interface DocumentRead {
  id: string;
  document_number: string;
  title: string;
  description?: string;
  category: string;
  entity_type: string;
  entity_id: string;
  current_version: number;
  status: 'DRAFT' | 'UNDER_REVIEW' | 'APPROVED' | 'ARCHIVED';
  approved_by?: string;
  approved_at?: string;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
  versions: DocumentVersionRead[];
}

export interface DocumentCreatePayload {
  file: File;
  title: string;
  description?: string;
  category: string;
  entity_type: string;
  entity_id: string;
}

export interface DocumentUpdatePayload {
  title?: string;
  description?: string;
  category?: string;
  status?: string;
}

export interface DocumentApprovalPayload {
  password: string;
  reason: string;
}

export interface DocumentListResponse {
  items: DocumentRead[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DocumentDashboardRead {
  total_documents: number;
  approved_documents: number;
  draft_documents: number;
  archived_documents: number;
  by_category: Record<string, number>;
  by_entity_type: Record<string, number>;
}

export interface DocumentUploadResponse {
  document: DocumentRead;
  latest_version: DocumentVersionRead;
}

export interface DocumentVerifyResponse {
  document_id: string;
  version_id: string;
  original_filename: string;
  stored_hash: string;
  calculated_hash: string;
  is_valid: boolean;
  verification_message: string;
}
