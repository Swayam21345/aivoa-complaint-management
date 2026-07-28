export type CAPAStatus =
  | 'OPEN'
  | 'UNDER_IMPLEMENTATION'
  | 'PENDING_EFFECTIVENESS'
  | 'EFFECTIVE'
  | 'INEFFECTIVE'
  | 'CLOSED'
  | 'CANCELLED';

export type CAPAPriority = 'Critical' | 'High' | 'Medium' | 'Low';
export type CAPARiskLevel = 'High' | 'Medium' | 'Low';

export interface CAPARead {
  id: string;
  complaint_id: string;
  complaint_number?: string;
  capa_number: string;
  title: string;
  description: string;
  root_cause?: string;
  corrective_action?: string;
  preventive_action?: string;
  owner?: string;
  reviewer?: string;
  effectiveness_check?: string;
  effectiveness_due_date?: string;
  target_completion_date?: string;
  completed_date?: string;
  priority: CAPAPriority;
  risk_level: CAPARiskLevel;
  status: CAPAStatus;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
}

export interface CAPACreatePayload {
  complaint_id: string;
  title: string;
  description: string;
  root_cause?: string;
  corrective_action?: string;
  preventive_action?: string;
  owner?: string;
  reviewer?: string;
  target_completion_date?: string;
  effectiveness_due_date?: string;
  priority?: CAPAPriority;
  risk_level?: CAPARiskLevel;
}

export interface CAPAUpdatePayload {
  title?: string;
  description?: string;
  root_cause?: string;
  corrective_action?: string;
  preventive_action?: string;
  owner?: string;
  reviewer?: string;
  effectiveness_check?: string;
  target_completion_date?: string;
  effectiveness_due_date?: string;
  priority?: CAPAPriority;
  risk_level?: CAPARiskLevel;
  status?: CAPAStatus;
}

export interface CAPAEffectivenessPayload {
  password: string;
  effectiveness_check: string;
  is_effective: boolean;
  reason: string;
}

export interface CAPAClosePayload {
  password: string;
  reason: string;
}

export interface CAPAListResponse {
  items: CAPARead[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CAPATrendItem {
  month: string;
  created: number;
  closed: number;
}

export interface CAPADashboardRead {
  open_capas: number;
  overdue_capas: number;
  pending_effectiveness: number;
  closed_this_month: number;
  average_closure_days: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_risk_level: Record<string, number>;
  monthly_trends: CAPATrendItem[];
}
