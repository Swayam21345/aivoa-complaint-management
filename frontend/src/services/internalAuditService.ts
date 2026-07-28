import apiClient from './apiClient';
import type {
  AuditChecklistRead,
  AuditFindingRead,
  InspectionReadinessCreate,
  InspectionReadinessRead,
  InternalAuditCreate,
  InternalAuditDashboardRead,
  InternalAuditRead,
  InternalAuditUpdate,
} from '@/types/internalAudit.types';

export async function fetchInternalAuditList(params?: {
  status?: string;
  department?: string;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<{ items: InternalAuditRead[]; total: number; page: number; page_size: number }> {
  const { data } = await apiClient.get('/api/internal-audits', { params });
  return data;
}

export async function fetchInternalAuditDetail(id: string): Promise<InternalAuditRead> {
  const { data } = await apiClient.get<InternalAuditRead>(`/api/internal-audits/${id}`);
  return data;
}

export async function createInternalAudit(payload: InternalAuditCreate): Promise<InternalAuditRead> {
  const { data } = await apiClient.post<InternalAuditRead>('/api/internal-audits', payload);
  return data;
}

export async function updateInternalAudit(id: string, payload: InternalAuditUpdate): Promise<InternalAuditRead> {
  const { data } = await apiClient.patch<InternalAuditRead>(`/api/internal-audits/${id}`, payload);
  return data;
}

export async function addAuditChecklistItem(
  id: string,
  section: string,
  requirement: string,
  question: string,
  complianceStatus: string = 'COMPLIANT',
  comments?: string,
): Promise<AuditChecklistRead> {
  const { data } = await apiClient.post<AuditChecklistRead>(`/api/internal-audits/${id}/checklist`, {
    section,
    requirement,
    question,
    compliance_status: complianceStatus,
    comments,
  });
  return data;
}

export async function addAuditFinding(
  id: string,
  category: string,
  description: string,
  clauseReference?: string,
  capaId?: string,
): Promise<AuditFindingRead> {
  const { data } = await apiClient.post<AuditFindingRead>(`/api/internal-audits/${id}/finding`, {
    category,
    description,
    clause_reference: clauseReference,
    capa_id: capaId,
  });
  return data;
}

export async function approveAndCloseAudit(
  id: string,
  password: string,
  reason: string,
  conclusion?: string,
): Promise<InternalAuditRead> {
  const { data } = await apiClient.post<InternalAuditRead>(`/api/internal-audits/${id}/approve`, {
    password,
    reason,
    conclusion,
  });
  return data;
}

export async function fetchInspectionReadinessPackages(): Promise<InspectionReadinessRead[]> {
  const { data } = await apiClient.get<InspectionReadinessRead[]>('/api/internal-audits/readiness-packages');
  return data;
}

export async function createInspectionReadinessPackage(
  payload: InspectionReadinessCreate,
): Promise<InspectionReadinessRead> {
  const { data } = await apiClient.post<InspectionReadinessRead>('/api/internal-audits/readiness-packages', payload);
  return data;
}

export async function fetchInternalAuditDashboard(): Promise<InternalAuditDashboardRead> {
  const { data } = await apiClient.get<InternalAuditDashboardRead>('/api/internal-audits/dashboard');
  return data;
}
