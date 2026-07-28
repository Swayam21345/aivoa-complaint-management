import apiClient from './apiClient';
import type {
  SupplierAuditRead,
  SupplierCorrectiveActionRead,
  SupplierCreate,
  SupplierDashboardRead,
  SupplierNonconformanceRead,
  SupplierRead,
  SupplierReportRead,
  SupplierScorecardRead,
  SupplierUpdate,
} from '@/types/supplier.types';

export async function fetchSupplierList(params?: {
  status?: string;
  risk_level?: string;
  supplier_type?: string;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<{ items: SupplierRead[]; total: number; page: number; page_size: number }> {
  const { data } = await apiClient.get('/api/suppliers', { params });
  return data;
}

export async function fetchSupplierDetail(id: string): Promise<SupplierRead> {
  const { data } = await apiClient.get<SupplierRead>(`/api/suppliers/${id}`);
  return data;
}

export async function createSupplier(payload: SupplierCreate): Promise<SupplierRead> {
  const { data } = await apiClient.post<SupplierRead>('/api/suppliers', payload);
  return data;
}

export async function updateSupplier(id: string, payload: SupplierUpdate): Promise<SupplierRead> {
  const { data } = await apiClient.patch<SupplierRead>(`/api/suppliers/${id}`, payload);
  return data;
}

export async function deleteSupplier(id: string): Promise<void> {
  await apiClient.delete(`/api/suppliers/${id}`);
}

export async function approveSupplier(
  id: string,
  password: string,
  reason: string,
): Promise<SupplierRead> {
  const { data } = await apiClient.post<SupplierRead>(`/api/suppliers/${id}/approve`, {
    password,
    reason,
  });
  return data;
}

export async function scheduleSupplierAudit(
  id: string,
  auditType: string,
  scheduledDate: string,
  auditor: string,
): Promise<SupplierAuditRead> {

  const { data } = await apiClient.post<SupplierAuditRead>(`/api/suppliers/${id}/audit`, {
    audit_type: auditType,
    scheduled_date: scheduledDate,
    auditor,
  });
  return data;
}

export async function addSupplierScorecard(
  id: string,
  period: string,
  qualityScore: number,
  deliveryScore: number,
  complianceScore: number,
): Promise<SupplierScorecardRead> {
  const { data } = await apiClient.post<SupplierScorecardRead>(`/api/suppliers/${id}/scorecard`, {
    period,
    quality_score: qualityScore,
    delivery_score: deliveryScore,
    compliance_score: complianceScore,
  });
  return data;
}

export async function addSupplierNonconformance(
  id: string,
  title: string,
  description: string,
  severity: string = 'MEDIUM',
  complaintId?: string,
): Promise<SupplierNonconformanceRead> {
  const { data } = await apiClient.post<SupplierNonconformanceRead>(
    `/api/suppliers/${id}/nonconformance`,
    {
      title,
      description,
      severity,
      complaint_id: complaintId,
    },
  );
  return data;
}

export async function addSupplierCorrectiveAction(
  id: string,
  actionPlan: string,
  owner: string,
  dueDays: number = 30,
  capaId?: string,
): Promise<SupplierCorrectiveActionRead> {
  const { data } = await apiClient.post<SupplierCorrectiveActionRead>(
    `/api/suppliers/${id}/corrective-action`,
    {
      action_plan: actionPlan,
      owner,
      due_days: dueDays,
      capa_id: capaId,
    },
  );
  return data;
}

export async function fetchSupplierDashboard(): Promise<SupplierDashboardRead> {
  const { data } = await apiClient.get<SupplierDashboardRead>('/api/suppliers/dashboard');
  return data;
}

export async function fetchSupplierReport(): Promise<SupplierReportRead> {
  const { data } = await apiClient.get<SupplierReportRead>('/api/suppliers/report');
  return data;
}
