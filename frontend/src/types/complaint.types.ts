// ─── Domain enums ────────────────────────────────────────────────────────────

export type RiskLevel = 'High' | 'Medium' | 'Low';

export type Priority = 'Critical' | 'High' | 'Medium' | 'Low';

export type ComplaintStatus =
  | 'Draft'
  | 'NEW'
  | 'TRIAGED'
  | 'ASSIGNED'
  | 'UNDER_INVESTIGATION'
  | 'ROOT_CAUSE_IDENTIFIED'
  | 'CAPA_IN_PROGRESS'
  | 'QA_REVIEW'
  | 'QA_APPROVED'
  | 'CLOSED'
  | 'REJECTED'
  | 'ON_HOLD'
  | 'CANCELLED'
  | 'UNDER_REVIEW'
  | 'IN_PROGRESS'
  | 'WAITING_CUSTOMER'
  | 'RESOLVED'
  | 'Under Review'
  | 'Closed';

export type SLAStatus = 'ON_TRACK' | 'AT_RISK' | 'BREACHED';

export type ComplaintCategory =
  | 'Product Quality Defect'
  | 'Packaging Defect'
  | 'Labeling Error'
  | 'Delivery Damage'
  | 'Adverse Event'
  | 'Foreign Material'
  | 'Documentation Error'
  | 'Other';

export type InputType = 'pdf' | 'image' | 'email' | 'text';

// ─── SLA & Escalation ─────────────────────────────────────────────────────────

export interface SLATrackingRead {
  created_at?: string;
  due_date?: string;
  sla_status: SLAStatus;
  remaining_hours: number;
  age_hours: number;
  time_under_review_hours: number;
  sla_target_hours: number;
  hours_until_due: number;
  is_overdue: boolean;
  near_sla: boolean;
  is_escalated: boolean;
  escalation_reason?: string | null;
  escalated_at?: string | null;
}

// ─── Audit Event ──────────────────────────────────────────────────────────────

export interface AuditEventRead {
  id: string;
  complaint_id?: string | null;
  actor_email: string;
  action_type: string;
  description: string;
  event_metadata?: Record<string, any> | null;
  created_at: string;
}

// ─── Investigator Dashboard ───────────────────────────────────────────────────

export interface InvestigatorDashboardData {
  assigned_to_me: number;
  pending_reviews: number;
  overdue_cases: number;
  completed_this_month: number;
  average_resolution_time?: number;
}

// ─── AI Analysis ─────────────────────────────────────────────────────────────

export interface ComplaintSummaryData {
  short_summary: string;
  detailed_summary: string;
}

export interface ComplaintCompletenessData {
  completeness_score: number;
  missing_fields: string[];
  recommendations: string[];
}

export interface RootCauseData {
  probable_root_causes: string[];
  confidence: number;
}

export interface CAPAData {
  corrective_actions: string[];
  preventive_actions: string[];
}

export interface SimilarComplaintItem {
  complaint_id: string;
  similarity_score: number;
  summary: string;
}

export interface DuplicateDetectionData {
  duplicate_found: boolean;
  similar_complaints: SimilarComplaintItem[];
  confidence: number;
}

export interface RiskExplanationData {
  risk_level: string;
  explanation: string;
}

export interface AIAnalysis {
  complaint_summary: string | null;
  product_name: string | null;
  batch_number: string | null;
  customer_name: string | null;
  category: ComplaintCategory | null;
  risk_level: RiskLevel | null;
  root_cause_recommendation: string | null;
  capa_recommendation: string | null;
  processing_time_ms?: number | null;
  model_used?: string | null;

  summary?: ComplaintSummaryData | null;
  completeness?: ComplaintCompletenessData | null;
  root_cause?: RootCauseData | null;
  capa?: CAPAData | null;
  duplicates?: DuplicateDetectionData | null;
  risk_explanation?: RiskExplanationData | null;
}

export interface ComplaintHistoryRead {
  id: string;
  complaint_id: string;
  old_status: string | null;
  new_status: string;
  changed_by: string | null;
  change_reason: string | null;
  created_at: string;
}

// ─── Electronic Signature (21 CFR Part 11) ────────────────────────────────────

export interface ElectronicSignatureRead {
  id: string;
  complaint_id: string;
  user_id: string;
  user_name?: string | null;
  action: string;
  status_before: string;
  status_after: string;
  reason: string;
  signature_timestamp: string;
  ip_address?: string | null;
  user_agent?: string | null;
  signature_hash: string;
  created_at: string;
}

export interface ElectronicSignatureCreate {
  password: string;
  reason: string;
  target_status: string;
  action?: string;
}

export interface ElectronicSignatureResponse {
  signed: boolean;
  signed_by: string;
  timestamp: string;
  signature_id: string;
  hash: string;
}

export interface ReviewerNoteRead {
  id: string;
  complaint_id: string;
  author: string;
  content: string;
  created_at: string;
  updated_at: string;
}

// ─── Complaint list item (summary) ───────────────────────────────────────────

export interface ComplaintListItem {
  id: string;
  complaint_id: string;
  date_received: string;        // ISO date string YYYY-MM-DD
  product_name: string | null;
  customer_name?: string | null;
  category: ComplaintCategory | null;
  risk_level: RiskLevel | null;
  priority?: Priority | null;
  status: ComplaintStatus;
  assigned_to?: string | null;
  assigned_by?: string | null;
  assigned_at?: string | null;
  is_escalated?: boolean;
  escalated_at?: string | null;
  escalation_reason?: string | null;
  sla_tracking?: SLATrackingRead | null;
  created_at: string;           // ISO datetime string
  updated_at?: string;
}

// ─── Full complaint detail ────────────────────────────────────────────────────

export interface ComplaintDetail extends ComplaintListItem {
  batch_number: string | null;
  customer_name: string | null;
  complaint_text: string | null;
  reviewer_notes: string | null;
  submitted_by: string | null;
  due_date?: string | null;
  updated_at: string;
  ai_analysis: AIAnalysis | null;
  history?: ComplaintHistoryRead[];
  notes?: ReviewerNoteRead[];
  audit_events?: AuditEventRead[];
  signatures?: ElectronicSignatureRead[];
}

// ─── Complaint form (draft state used in the UI) ──────────────────────────────

export interface ComplaintFormDraft {
  product_name: string;
  batch_number: string;
  customer_name: string;
  category: ComplaintCategory | '';
  risk_level: RiskLevel | '';
  complaint_text: string;
  reviewer_notes: string;
  submitted_by: string;
  date_received: string;        // ISO date YYYY-MM-DD
}

// ─── Paginated list response ──────────────────────────────────────────────────

export interface PaginatedComplaints {
  total: number;
  page: number;
  page_size: number;
  items: ComplaintListItem[];
}
