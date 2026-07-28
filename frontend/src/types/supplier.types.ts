export interface SupplierContactRead {
  id: string;
  supplier_id: string;
  name: string;
  email: string;
  phone?: string;
  title?: string;
  is_primary: boolean;
}

export interface SupplierAuditRead {
  id: string;
  supplier_id: string;
  audit_number: string;
  audit_type: string;
  scheduled_date: string;
  completed_date?: string;
  auditor: string;
  status: 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  score?: number;
  findings_summary?: string;
}

export interface SupplierScorecardRead {
  id: string;
  supplier_id: string;
  period: string;
  quality_score: number;
  delivery_score: number;
  compliance_score: number;
  overall_score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  evaluated_by: string;
  evaluated_at: string;
}

export interface SupplierNonconformanceRead {
  id: string;
  supplier_id: string;
  complaint_id?: string;
  ncr_number: string;
  title: string;

  description: string;
  severity: 'MINOR' | 'MAJOR' | 'CRITICAL';
  status: 'OPEN' | 'INVESTIGATING' | 'CLOSED';
  created_at: string;
}

export interface SupplierCorrectiveActionRead {
  id: string;
  supplier_id: string;
  capa_id?: string;
  action_number: string;
  action_plan: string;
  owner: string;
  due_date: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'COMPLETED';
  completed_at?: string;
}

export interface SupplierRead {
  id: string;
  supplier_number: string;
  supplier_name: string;
  supplier_type: string;
  category: string;
  status: 'PENDING_QUALIFICATION' | 'APPROVED' | 'CONDITIONAL' | 'DISQUALIFIED';
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  zip_code?: string;
  phone?: string;
  email?: string;
  website?: string;
  approval_status: string;
  approved_by?: string;
  approved_at?: string;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
  contacts: SupplierContactRead[];
  audits: SupplierAuditRead[];
  scorecards: SupplierScorecardRead[];
  nonconformances: SupplierNonconformanceRead[];
  corrective_actions: SupplierCorrectiveActionRead[];
}

export interface SupplierCreate {
  supplier_name: string;
  supplier_type: string;
  category?: string;
  risk_level?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  zip_code?: string;
  phone?: string;
  email?: string;
  website?: string;
}

export interface SupplierUpdate {
  supplier_name?: string;
  supplier_type?: string;
  category?: string;
  status?: string;
  risk_level?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  zip_code?: string;
  phone?: string;
  email?: string;
  website?: string;
}

export interface SupplierDashboardRead {
  total_suppliers: number;
  approved_suppliers: number;
  pending_approvals: number;
  disqualified_suppliers: number;
  risk_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
  by_type: Record<string, number>;
  upcoming_audits_count: number;
  open_supplier_capas_count: number;
  avg_overall_score: number;
}

export interface SupplierReportRead {
  total_suppliers: number;
  approved_count: number;
  high_risk_count: number;
  open_ncr_count: number;
  suppliers: SupplierRead[];
}
