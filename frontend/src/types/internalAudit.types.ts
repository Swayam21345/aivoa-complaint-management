export interface AuditChecklistRead {
  id: string;
  audit_id: string;
  section: string;
  requirement: string;
  question: string;
  compliance_status: 'COMPLIANT' | 'NON_COMPLIANT' | 'OBSERVATION' | 'NOT_APPLICABLE';
  comments?: string;
  evidence_summary?: string;
}

export interface AuditFindingRead {
  id: string;
  audit_id: string;
  finding_number: string;
  category: 'CRITICAL_NC' | 'MAJOR_NC' | 'MINOR_NC' | 'OBSERVATION' | 'RECOMMENDATION';
  description: string;
  clause_reference?: string;
  capa_id?: string;
  status: 'OPEN' | 'CAPA_ASSIGNED' | 'RESOLVED' | 'CLOSED';
  created_at: string;
}

export interface InternalAuditRead {
  id: string;
  audit_number: string;
  title: string;
  audit_type: string;
  scope: string;
  lead_auditor: string;
  audit_team?: string;
  department: string;
  scheduled_start_date: string;
  scheduled_end_date: string;
  actual_start_date?: string;
  actual_end_date?: string;
  status: 'PLANNED' | 'IN_PROGRESS' | 'REPORT_PENDING' | 'CLOSED' | 'CANCELLED';
  conclusion?: string;
  approved_by?: string;
  approved_at?: string;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
  checklists: AuditChecklistRead[];
  findings: AuditFindingRead[];
}

export interface InternalAuditCreate {
  title: string;
  audit_type: string;
  scope: string;
  lead_auditor: string;
  audit_team?: string;
  department?: string;
  scheduled_start_date: string;
  scheduled_end_date: string;
}

export interface InternalAuditUpdate {
  title?: string;
  audit_type?: string;
  scope?: string;
  lead_auditor?: string;
  audit_team?: string;
  department?: string;
  scheduled_start_date?: string;
  scheduled_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  status?: string;
  conclusion?: string;
}

export interface InspectionReadinessRead {
  id: string;
  package_number: string;
  agency: string;
  title: string;
  description: string;
  readiness_score: number;
  status: string;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
}

export interface InspectionReadinessCreate {
  agency: string;
  title: string;
  description: string;
  readiness_score?: number;
}

export interface InternalAuditDashboardRead {
  total_audits: number;
  planned_audits: number;
  in_progress_audits: number;
  closed_audits: number;
  total_findings: number;
  critical_findings_count: number;
  open_findings_count: number;
  avg_inspection_readiness_score: number;
  by_department: Record<string, number>;
  by_category: Record<string, number>;
}
