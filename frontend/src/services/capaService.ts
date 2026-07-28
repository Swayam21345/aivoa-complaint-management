import apiClient from './apiClient';

import type {
  CAPAClosePayload,
  CAPACreatePayload,
  CAPADashboardRead,
  CAPAEffectivenessPayload,
  CAPAListResponse,
  CAPARead,
  CAPAUpdatePayload,
} from '@/types/capa.types';

export async function fetchCAPAList(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  priority?: string;
  risk_level?: string;
  complaint_id?: string;
  owner?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}): Promise<CAPAListResponse> {
  const { data } = await apiClient.get<CAPAListResponse>('/api/capa', { params });
  return data;
}

export async function fetchCAPADetail(id: string): Promise<CAPARead> {
  const { data } = await apiClient.get<CAPARead>(`/api/capa/${id}`);
  return data;
}

export async function createCAPA(payload: CAPACreatePayload): Promise<CAPARead> {
  const { data } = await apiClient.post<CAPARead>('/api/capa', payload);
  return data;
}

export async function updateCAPA(id: string, payload: CAPAUpdatePayload): Promise<CAPARead> {
  const { data } = await apiClient.patch<CAPARead>(`/api/capa/${id}`, payload);
  return data;
}

export async function deleteCAPA(id: string): Promise<void> {
  await apiClient.delete(`/api/capa/${id}`);
}

export async function submitCAPAEffectiveness(
  id: string,
  payload: CAPAEffectivenessPayload,
): Promise<CAPARead> {
  const { data } = await apiClient.post<CAPARead>(`/api/capa/${id}/effectiveness`, payload);
  return data;
}

export async function closeCAPA(id: string, payload: CAPAClosePayload): Promise<CAPARead> {
  const { data } = await apiClient.post<CAPARead>(`/api/capa/${id}/close`, payload);
  return data;
}

export async function fetchCAPADashboard(): Promise<CAPADashboardRead> {
  const { data } = await apiClient.get<CAPADashboardRead>('/api/capa/dashboard');
  return data;
}
