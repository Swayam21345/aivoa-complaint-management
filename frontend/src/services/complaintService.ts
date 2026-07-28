import apiClient from './apiClient';
import type {
  CreateComplaintRequest,
  CreateComplaintResponse,
  UpdateComplaintRequest,
  UpdateComplaintResponse,
} from '@/types/api.types';
import type {
  AuditEventRead,
  ComplaintDetail,
  ElectronicSignatureCreate,
  ElectronicSignatureRead,
  ElectronicSignatureResponse,
  InvestigatorDashboardData,
  PaginatedComplaints,
} from '@/types/complaint.types';

export interface ListComplaintsParams {
  status?: string;
  risk_level?: string;
  priority?: string;
  category?: string;
  search?: string;
  sort?: 'created_at_asc' | 'created_at_desc';
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export async function createComplaint(
  data: CreateComplaintRequest,
): Promise<CreateComplaintResponse> {
  const response = await apiClient.post<CreateComplaintResponse>('/api/complaints', data);
  return response.data;
}

export async function listComplaints(
  params: ListComplaintsParams = {},
): Promise<PaginatedComplaints> {
  const response = await apiClient.get<PaginatedComplaints>('/api/complaints', { params });
  return response.data;
}

export async function getComplaint(id: string): Promise<ComplaintDetail> {
  const response = await apiClient.get<ComplaintDetail>(`/api/complaints/${id}`);
  return response.data;
}

export async function assignComplaint(
  id: string,
  assignedTo: string,
): Promise<ComplaintDetail> {
  const response = await apiClient.post<ComplaintDetail>(`/api/complaints/${id}/assign`, {
    assigned_to: assignedTo,
  });
  return response.data;
}

export async function getComplaintActivity(id: string): Promise<AuditEventRead[]> {
  const response = await apiClient.get<AuditEventRead[]>(`/api/complaints/${id}/activity`);
  return response.data;
}

export async function getInvestigatorDashboard(): Promise<InvestigatorDashboardData> {
  const response = await apiClient.get<InvestigatorDashboardData>('/api/dashboard/investigator');
  return response.data;
}

export async function updateComplaint(
  id: string,
  data: UpdateComplaintRequest,
): Promise<UpdateComplaintResponse> {
  const response = await apiClient.patch<UpdateComplaintResponse>(
    `/api/complaints/${id}`,
    data,
  );
  return response.data;
}

export async function getComplaintTimeline(id: string) {
  const response = await apiClient.get(`/api/complaints/${id}/timeline`);
  return response.data;
}

export async function getCopilotExplainability(id: string) {
  const response = await apiClient.get(`/api/complaints/${id}/copilot`);
  return response.data;
}

export async function exportComplaintPDF(id: string, complaintNumber?: string): Promise<void> {
  const response = await apiClient.get(`/api/complaints/${id}/export/pdf`, {
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `Complaint_Report_${complaintNumber || id}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

// ─── 21 CFR Part 11 Electronic Signatures ────────────────────────────────────

export async function signComplaint(
  id: string,
  payload: ElectronicSignatureCreate,
): Promise<ElectronicSignatureResponse> {
  const response = await apiClient.post<ElectronicSignatureResponse>(
    `/api/complaints/${id}/sign`,
    payload,
  );
  return response.data;
}

export async function getComplaintSignatures(id: string): Promise<ElectronicSignatureRead[]> {
  const response = await apiClient.get<ElectronicSignatureRead[]>(
    `/api/complaints/${id}/signatures`,
  );
  return response.data;
}
