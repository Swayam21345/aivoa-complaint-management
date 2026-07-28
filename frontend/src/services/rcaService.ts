import apiClient from './apiClient';
import type {
  FMEAAssessmentCreate,
  FMEAAssessmentRead,
  RCAApprovePayload,
  RCACreatePayload,
  RCADashboardRead,
  RCAListResponse,
  RCARead,
  RCAUpdatePayload,
} from '@/types/rca.types';

export async function fetchRCAList(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  category?: string;
  complaint_id?: string;
  search?: string;
}): Promise<RCAListResponse> {
  const { data } = await apiClient.get<RCAListResponse>('/api/rca', { params });
  return data;
}

export async function fetchRCADetail(id: string): Promise<RCARead> {
  const { data } = await apiClient.get<RCARead>(`/api/rca/${id}`);
  return data;
}

export async function createRCA(payload: RCACreatePayload): Promise<RCARead> {
  const { data } = await apiClient.post<RCARead>('/api/rca', payload);
  return data;
}

export async function updateRCA(id: string, payload: RCAUpdatePayload): Promise<RCARead> {
  const { data } = await apiClient.patch<RCARead>(`/api/rca/${id}`, payload);
  return data;
}

export async function deleteRCA(id: string): Promise<void> {
  await apiClient.delete(`/api/rca/${id}`);
}

export async function approveRCA(id: string, payload: RCAApprovePayload): Promise<RCARead> {
  const { data } = await apiClient.post<RCARead>(`/api/rca/${id}/approve`, payload);
  return data;
}

export async function addFMEAItem(
  rcaId: string,
  payload: FMEAAssessmentCreate,
): Promise<FMEAAssessmentRead> {
  const { data } = await apiClient.post<FMEAAssessmentRead>(`/api/rca/${rcaId}/fmea`, payload);
  return data;
}

export async function fetchRCADashboard(): Promise<RCADashboardRead> {
  const { data } = await apiClient.get<RCADashboardRead>('/api/rca/dashboard');
  return data;
}
