import apiClient from './apiClient';
import type {
  DocumentApprovalPayload,
  DocumentCreatePayload,
  DocumentDashboardRead,
  DocumentListResponse,
  DocumentRead,
  DocumentUpdatePayload,
  DocumentUploadResponse,
  DocumentVerifyResponse,
} from '@/types/document.types';


export async function fetchDocumentList(params?: {
  page?: number;
  page_size?: number;
  category?: string;
  status?: string;
  entity_type?: string;
  entity_id?: string;
  search?: string;
}): Promise<DocumentListResponse> {
  const { data } = await apiClient.get<DocumentListResponse>('/api/documents', { params });
  return data;
}

export async function fetchDocumentDetail(id: string): Promise<DocumentRead> {
  const { data } = await apiClient.get<DocumentRead>(`/api/documents/${id}`);
  return data;
}

export async function uploadDocument(
  payload: DocumentCreatePayload,
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', payload.file);
  formData.append('title', payload.title);
  if (payload.description) formData.append('description', payload.description);
  formData.append('category', payload.category);
  formData.append('entity_type', payload.entity_type);
  formData.append('entity_id', payload.entity_id);

  const { data } = await apiClient.post<DocumentUploadResponse>('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function uploadNewVersion(
  documentId: string,
  file: File,
  changeSummary?: string,
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (changeSummary) formData.append('change_summary', changeSummary);

  const { data } = await apiClient.post<DocumentUploadResponse>(
    `/api/documents/${documentId}/versions`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return data;
}

export async function updateDocument(
  id: string,
  payload: DocumentUpdatePayload,
): Promise<DocumentRead> {
  const { data } = await apiClient.patch<DocumentRead>(`/api/documents/${id}`, payload);
  return data;
}

export async function approveDocument(
  id: string,
  payload: DocumentApprovalPayload,
): Promise<DocumentRead> {
  const { data } = await apiClient.post<DocumentRead>(`/api/documents/${id}/approve`, payload);
  return data;
}

export async function archiveDocument(id: string): Promise<DocumentRead> {
  const { data } = await apiClient.post<DocumentRead>(`/api/documents/${id}/archive`);
  return data;
}

export async function restoreDocument(id: string): Promise<DocumentRead> {
  const { data } = await apiClient.post<DocumentRead>(`/api/documents/${id}/restore`);
  return data;
}

export async function verifyDocumentHash(
  id: string,
  versionId?: string,
): Promise<DocumentVerifyResponse> {
  const { data } = await apiClient.get<DocumentVerifyResponse>(`/api/documents/${id}/verify`, {
    params: { version_id: versionId },
  });
  return data;
}

export async function fetchDocumentDashboard(): Promise<DocumentDashboardRead> {
  const { data } = await apiClient.get<DocumentDashboardRead>('/api/documents/dashboard');
  return data;
}

export async function deleteDocument(id: string): Promise<void> {
  await apiClient.delete(`/api/documents/${id}`);
}

export function getDocumentDownloadUrl(id: string, versionId?: string): string {
  const query = versionId ? `?version_id=${versionId}` : '';
  return `/api/documents/${id}/download${query}`;
}
